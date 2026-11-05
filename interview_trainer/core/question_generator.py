"""
question_generator.py – Generate interview question sets with model answers and citations.

Orchestrates: knowledge-base retrieval → prompt construction → Granite generation
→ structured output parsing.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from interview_trainer.config import RETRIEVAL_TOP_K
from interview_trainer.core.granite_client import GraniteClient, get_granite_client
from interview_trainer.core.knowledge_base import KnowledgeBase, RetrievalResult, get_knowledge_base

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Citation:
    """Source provenance for a retrieved knowledge-base chunk."""

    source_file: str
    question_id: str
    section_title: str
    similarity_score: float


@dataclass
class InterviewQuestion:
    """A single interview question with model answer and metadata."""

    question: str
    category: str            # "technical" | "behavioral" | "hr" | "resume_based"
    difficulty: str          # "beginner" | "intermediate" | "advanced"
    model_answer: str
    star_format: bool        # True when behavioral STAR answer
    citations: list[Citation] = field(default_factory=list)
    question_id: str = ""    # auto-assigned sequential ID


@dataclass
class QuestionSet:
    """A grouped set of interview questions."""

    role: str
    experience_level: str
    technical: list[InterviewQuestion] = field(default_factory=list)
    behavioral: list[InterviewQuestion] = field(default_factory=list)
    hr: list[InterviewQuestion] = field(default_factory=list)
    resume_based: list[InterviewQuestion] = field(default_factory=list)

    def all_questions(self) -> list[InterviewQuestion]:
        return self.technical + self.behavioral + self.hr + self.resume_based


# ---------------------------------------------------------------------------
# Question generator
# ---------------------------------------------------------------------------

class QuestionGenerator:
    """Generate tailored interview question sets using RAG + IBM Granite.

    Args:
        kb:     :class:`KnowledgeBase` instance (uses singleton if not provided).
        client: :class:`GraniteClient` instance (uses singleton if not provided).
    """

    def __init__(
        self,
        kb: Optional[KnowledgeBase] = None,
        client: Optional[GraniteClient] = None,
    ) -> None:
        self._kb = kb or get_knowledge_base()
        self._client = client or get_granite_client()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_question_set(
        self,
        role: str,
        role_key: str,
        experience_level: str,
        interview_type: str,
        resume_data: Optional[dict] = None,
        company_type: str = "Any",
        n_technical: int = 8,
        n_behavioral: int = 4,
        n_hr: int = 3,
        n_resume: int = 3,
    ) -> QuestionSet:
        """Generate a complete interview question set for the given profile.

        Args:
            role:             Human-readable role name (e.g. "Java Developer").
            role_key:         Knowledge-base role key (e.g. "java_developer").
            experience_level: One of Fresher / 0-2 yrs / 2-5 yrs / 5+ yrs.
            interview_type:   "Technical" | "Soft Skills" | "Mixed".
            resume_data:      Parsed resume dict (from resume_parser).
            company_type:     Target company type for contextual tailoring.
            n_technical:      Number of technical questions.
            n_behavioral:     Number of behavioral questions.
            n_hr:             Number of HR questions.
            n_resume:         Number of resume-based questions.

        Returns:
            A :class:`QuestionSet` with all sections populated.
        """
        qs = QuestionSet(role=role, experience_level=experience_level)

        difficulty_filter = _experience_to_difficulty(experience_level)

        # Technical questions
        if interview_type in ("Technical", "Mixed"):
            qs.technical = self._generate_section(
                category="technical",
                role_key=role_key,
                role=role,
                experience_level=experience_level,
                difficulty_hint=difficulty_filter,
                company_type=company_type,
                count=n_technical,
            )

        # Behavioral
        if interview_type in ("Soft Skills", "Mixed"):
            qs.behavioral = self._generate_section(
                category="behavioral",
                role_key=role_key,
                role=role,
                experience_level=experience_level,
                difficulty_hint="intermediate",
                company_type=company_type,
                count=n_behavioral,
            )
            qs.hr = self._generate_section(
                category="hr",
                role_key=role_key,
                role=role,
                experience_level=experience_level,
                difficulty_hint="beginner",
                company_type=company_type,
                count=n_hr,
            )
        elif interview_type == "Technical":
            # Still include a couple of HR basics
            qs.hr = self._generate_section(
                category="hr",
                role_key=role_key,
                role=role,
                experience_level=experience_level,
                difficulty_hint="beginner",
                company_type=company_type,
                count=2,
            )

        # Resume-based questions
        if resume_data and interview_type in ("Technical", "Mixed"):
            qs.resume_based = self._generate_resume_questions(
                role=role,
                role_key=role_key,
                resume_data=resume_data,
                count=n_resume,
            )

        # Assign sequential IDs
        _assign_ids(qs)
        return qs

    # ------------------------------------------------------------------
    # Private helpers – section generation
    # ------------------------------------------------------------------

    def _generate_section(
        self,
        category: str,
        role_key: str,
        role: str,
        experience_level: str,
        difficulty_hint: str,
        company_type: str,
        count: int,
    ) -> list[InterviewQuestion]:
        """Retrieve relevant chunks and ask Granite to generate a question list."""
        query = _build_retrieval_query(category, role, difficulty_hint)
        results = self._kb.retrieve(
            query=query,
            role=role_key,
            category=category if category in ("technical",) else None,
            top_k=RETRIEVAL_TOP_K,
        )

        if not results:
            logger.warning("No retrieval results for category=%s role=%s", category, role_key)
            context_text = ""
            citations: list[Citation] = []
        else:
            context_text, citations = _format_context(results)

        prompt = _build_generation_prompt(
            category=category,
            role=role,
            experience_level=experience_level,
            difficulty_hint=difficulty_hint,
            company_type=company_type,
            context=context_text,
            count=count,
        )

        raw = self._client.generate_structured(prompt, max_new_tokens=2048)
        questions = _parse_questions_json(raw, category, citations)

        # Fallback to context-only if Granite returned nothing useful
        if not questions and results:
            questions = _fallback_from_retrieval(results, category, count)

        return questions[:count]

    def _generate_resume_questions(
        self,
        role: str,
        role_key: str,
        resume_data: dict,
        count: int,
    ) -> list[InterviewQuestion]:
        """Generate resume-specific questions based on parsed resume data."""
        skills = resume_data.get("skills", [])[:8]
        projects = resume_data.get("projects", [])[:4]
        experience_lines = resume_data.get("experience", [])[:5]

        if not skills and not projects:
            return []

        prompt = _build_resume_questions_prompt(
            role=role,
            skills=skills,
            projects=projects,
            experience_lines=experience_lines,
            count=count,
        )

        raw = self._client.generate_structured(prompt, max_new_tokens=1024)
        questions = _parse_questions_json(raw, "resume_based", [])
        return questions[:count]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _build_retrieval_query(category: str, role: str, difficulty: str) -> str:
    if category == "technical":
        return f"{role} technical interview questions {difficulty} level"
    elif category == "behavioral":
        return f"behavioral STAR format interview questions {role}"
    elif category == "hr":
        return f"HR situational interview questions professional work"
    return f"{role} interview questions {category}"


def _build_generation_prompt(
    category: str,
    role: str,
    experience_level: str,
    difficulty_hint: str,
    company_type: str,
    context: str,
    count: int,
) -> str:
    category_desc = {
        "technical": f"technical {role} interview questions",
        "behavioral": "behavioral interview questions using the STAR method",
        "hr": "HR and situational interview questions",
    }.get(category, f"{category} interview questions")

    company_ctx = "" if company_type == "Any" else f" for a {company_type.lower()}"

    context_block = (
        f"\n\nKNOWLEDGE BASE CONTEXT:\n{context}\n\n"
        if context
        else "\n\n[No context retrieved from knowledge base.]\n\n"
    )

    star_instruction = (
        ' For behavioral questions, model answers MUST follow the STAR structure '
        '(Situation, Task, Action, Result).'
        if category == "behavioral" else ""
    )

    return f"""You are an expert interview coach specialising in {role} roles{company_ctx}.
{context_block}
Your task: Generate exactly {count} {category_desc} for a candidate with experience level: {experience_level}.
Difficulty level: {difficulty_hint}.{star_instruction}

RULES:
1. Use ONLY information from the knowledge base context above when available.
2. If context is not available for a question, still generate a reasonable question and answer but note the answer is general.
3. Vary difficulty across questions appropriate to {difficulty_hint} level.
4. Each model answer must be detailed (150-300 words), practical, and include code examples where relevant for technical questions.

Respond with a JSON array of {count} objects. Each object must have these exact keys:
- "question": the interview question text
- "model_answer": detailed model answer
- "difficulty": one of "beginner", "intermediate", "advanced"
- "is_star": true for STAR behavioral answers, false otherwise

Example format:
[
  {{
    "question": "...",
    "model_answer": "...",
    "difficulty": "intermediate",
    "is_star": false
  }}
]

Generate the JSON array now:"""


def _build_resume_questions_prompt(
    role: str,
    skills: list[str],
    projects: list[str],
    experience_lines: list[str],
    count: int,
) -> str:
    skills_str = ", ".join(skills) if skills else "various technologies"
    projects_str = "\n".join(f"- {p}" for p in projects) if projects else "- (no specific projects listed)"
    exp_str = "\n".join(f"- {e}" for e in experience_lines) if experience_lines else "- (experience not detailed)"

    return f"""You are an expert technical interviewer for {role} roles.
The candidate's resume shows:
SKILLS: {skills_str}
PROJECTS:
{projects_str}
EXPERIENCE:
{exp_str}

Generate exactly {count} specific interview questions based on THIS candidate's resume.
Questions should probe their specific experience — e.g., "You mention [project X], explain your design choices" or "How did you use [skill Y] in your work?"

Respond with a JSON array of {count} objects with keys:
- "question": specific question referencing their resume
- "model_answer": what an ideal answer would contain
- "difficulty": one of "beginner", "intermediate", "advanced"
- "is_star": false

JSON array:"""


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

def _parse_questions_json(
    raw: str,
    category: str,
    citations: list[Citation],
) -> list[InterviewQuestion]:
    """Parse the Granite JSON response into InterviewQuestion objects.

    Falls back gracefully if the output is malformed.
    """
    # Extract JSON array from the response
    raw = raw.strip()
    json_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not json_match:
        logger.warning("No JSON array found in Granite response: %s", raw[:200])
        return []

    try:
        items = json.loads(json_match.group())
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse error: %s. Raw snippet: %s", exc, raw[:200])
        return []

    questions: list[InterviewQuestion] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        q_text = str(item.get("question", "")).strip()
        if not q_text:
            continue
        questions.append(
            InterviewQuestion(
                question=q_text,
                category=category,
                difficulty=str(item.get("difficulty", "intermediate")).lower(),
                model_answer=str(item.get("model_answer", "")).strip(),
                star_format=bool(item.get("is_star", False)),
                citations=citations[:],
            )
        )
    return questions


def _fallback_from_retrieval(
    results: list[RetrievalResult],
    category: str,
    count: int,
) -> list[InterviewQuestion]:
    """Emergency fallback: use retrieved Q&A chunks directly when generation fails."""
    questions: list[InterviewQuestion] = []
    for r in results[:count]:
        chunk = r.chunk
        # Extract question and answer from chunk text
        q_match = re.search(r"\*\*Question:\*\*\s*(.+)", chunk.text)
        a_match = re.search(r"\*\*Answer:\*\*\s*(.+?)(?=---|\Z)", chunk.text, re.DOTALL)
        q_text = q_match.group(1).strip() if q_match else chunk.question_text
        a_text = a_match.group(1).strip() if a_match else chunk.text[:500]
        questions.append(
            InterviewQuestion(
                question=q_text,
                category=category,
                difficulty=chunk.difficulty,
                model_answer=a_text,
                star_format=False,
                citations=[
                    Citation(
                        source_file=chunk.source_file,
                        question_id=chunk.question_id,
                        section_title=chunk.question_text,
                        similarity_score=r.score,
                    )
                ],
            )
        )
    return questions


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _format_context(results: list[RetrievalResult]) -> tuple[str, list[Citation]]:
    """Format retrieved chunks into a context string and citation list."""
    citations: list[Citation] = []
    sections: list[str] = []
    for r in results:
        chunk = r.chunk
        sections.append(
            f"[Source: {chunk.source_file} | {chunk.question_id} | "
            f"Difficulty: {chunk.difficulty}]\n{chunk.text}"
        )
        citations.append(
            Citation(
                source_file=chunk.source_file,
                question_id=chunk.question_id,
                section_title=chunk.question_text,
                similarity_score=r.score,
            )
        )
    return "\n\n---\n\n".join(sections), citations


def _experience_to_difficulty(experience_level: str) -> str:
    mapping = {
        "Fresher": "beginner",
        "0-2 yrs": "beginner",
        "2-5 yrs": "intermediate",
        "5+ yrs": "advanced",
    }
    return mapping.get(experience_level, "intermediate")


def _assign_ids(qs: QuestionSet) -> None:
    counter = 1
    for q in qs.all_questions():
        q.question_id = f"Q{counter:02d}"
        counter += 1

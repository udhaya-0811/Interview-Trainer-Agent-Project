"""
resume_parser.py – Extract skills, education, and projects from uploaded resumes.

Supports PDF and DOCX formats; also accepts plain pasted text.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import IO

# PDF and DOCX parsing – imported lazily so missing deps give clear messages
try:
    import pdfplumber  # type: ignore
    _PDF_AVAILABLE = True
except ImportError:
    _PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument  # type: ignore
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from a PDF or DOCX file.

    Args:
        file_bytes: Raw bytes of the uploaded file.
        filename:   Original filename (used to detect extension).

    Returns:
        Extracted plain text.

    Raises:
        ValueError: If the file type is unsupported.
        RuntimeError: If the required parsing library is not installed.
    """
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_from_pdf(file_bytes)
    elif suffix in (".docx", ".doc"):
        return _extract_from_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type: '{suffix}'. Please upload a PDF or DOCX file."
        )


def parse_resume(text: str) -> dict[str, list[str]]:
    """Parse raw resume text into structured sections.

    Uses heuristic section detection (no LLM required at this stage).
    The result is refined further by the question generator via Granite.

    Args:
        text: Raw resume text.

    Returns:
        A dict with keys: ``skills``, ``education``, ``projects``,
        ``experience``, ``certifications``.
    """
    text = _normalise(text)
    sections = _split_sections(text)

    skills: list[str] = _extract_skills(sections.get("skills", ""))
    education: list[str] = _extract_education(sections.get("education", ""))
    projects: list[str] = _extract_projects(sections.get("projects", ""))
    experience: list[str] = _extract_experience(sections.get("experience", ""))
    certifications: list[str] = _extract_certifications(
        sections.get("certifications", "")
    )

    # Fallback: infer skills from full text if section not found
    if not skills:
        skills = _infer_skills_from_text(text)

    return {
        "skills": skills,
        "education": education,
        "projects": projects,
        "experience": experience,
        "certifications": certifications,
    }


# ---------------------------------------------------------------------------
# File-type extractors
# ---------------------------------------------------------------------------

def _extract_from_pdf(file_bytes: bytes) -> str:
    if not _PDF_AVAILABLE:
        raise RuntimeError(
            "pdfplumber is not installed. Run: pip install pdfplumber"
        )
    import io
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def _extract_from_docx(file_bytes: bytes) -> str:
    if not _DOCX_AVAILABLE:
        raise RuntimeError(
            "python-docx is not installed. Run: pip install python-docx"
        )
    import io
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

_SECTION_HEADERS: dict[str, list[str]] = {
    "skills": [
        "skills", "technical skills", "core competencies", "technologies",
        "tools", "programming languages", "tech stack",
    ],
    "education": ["education", "academic background", "qualifications", "degree"],
    "experience": [
        "experience", "work experience", "employment", "professional experience",
        "career", "internship",
    ],
    "projects": ["projects", "personal projects", "academic projects", "portfolio"],
    "certifications": [
        "certifications", "certificates", "courses", "achievements", "awards",
    ],
}


def _normalise(text: str) -> str:
    """Normalise whitespace and remove non-printable characters."""
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[^\x20-\x7e\n]", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _split_sections(text: str) -> dict[str, str]:
    """Detect and split resume into named sections."""
    # Build a regex that matches any known header
    all_headers: list[str] = []
    for headers in _SECTION_HEADERS.values():
        all_headers.extend(headers)

    # Pattern: line that is entirely a known header (case-insensitive)
    pattern = r"(?im)^[ \t]*(" + "|".join(re.escape(h) for h in all_headers) + r")[ \t]*:?[ \t]*$"
    splits = list(re.finditer(pattern, text))

    if not splits:
        # Return the entire text as "experience" fallback
        return {"experience": text}

    sections: dict[str, str] = {}
    for i, match in enumerate(splits):
        header_raw = match.group(1).lower().strip()
        section_name = _map_header(header_raw)
        start = match.end()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        sections[section_name] = text[start:end].strip()

    return sections


def _map_header(raw: str) -> str:
    for canonical, aliases in _SECTION_HEADERS.items():
        if raw in aliases:
            return canonical
    return raw


# ---------------------------------------------------------------------------
# Per-section extractors
# ---------------------------------------------------------------------------

_TECH_KEYWORDS: frozenset[str] = frozenset(
    [
        # Languages
        "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
        "rust", "kotlin", "swift", "ruby", "php", "scala", "r", "matlab",
        # Web
        "html", "css", "react", "vue", "angular", "nextjs", "svelte",
        "nodejs", "express", "django", "flask", "fastapi", "spring", "spring boot",
        # Data
        "sql", "nosql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "spark", "hadoop", "kafka", "airflow", "dbt", "tableau", "powerbi",
        # ML/AI
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
        "huggingface", "langchain", "llm", "rag", "machine learning",
        "deep learning", "nlp", "computer vision",
        # DevOps
        "docker", "kubernetes", "jenkins", "github actions", "gitlab ci",
        "terraform", "ansible", "aws", "gcp", "azure", "linux",
        # Other
        "git", "rest", "graphql", "microservices", "agile", "scrum",
        "junit", "pytest", "selenium", "jira", "confluence",
    ]
)


def _extract_skills(section_text: str) -> list[str]:
    """Extract skills from the skills section using keyword matching."""
    if not section_text:
        return []
    lower = section_text.lower()
    # Extract comma/pipe/bullet separated items
    raw_items = re.split(r"[,|•·\n]+", section_text)
    skills: list[str] = []
    for item in raw_items:
        item = item.strip(" :-")
        if 1 < len(item) <= 60 and not item.isdigit():
            skills.append(item)
    return [s for s in skills if s]


def _infer_skills_from_text(text: str) -> list[str]:
    """Fallback: extract tech keywords from unstructured resume text."""
    lower = text.lower()
    return [kw.title() for kw in sorted(_TECH_KEYWORDS) if kw in lower]


def _extract_education(section_text: str) -> list[str]:
    if not section_text:
        return []
    lines = [l.strip() for l in section_text.splitlines() if l.strip()]
    return [l for l in lines if len(l) > 5][:8]


def _extract_projects(section_text: str) -> list[str]:
    if not section_text:
        return []
    # Split on project names (lines that look like titles: mixed case, no trailing verb)
    raw_blocks = re.split(r"\n(?=[A-Z][a-z])", section_text)
    projects: list[str] = []
    for block in raw_blocks:
        title_line = block.splitlines()[0].strip() if block.strip() else ""
        if title_line and len(title_line) > 3:
            projects.append(title_line)
    return projects[:10]


def _extract_experience(section_text: str) -> list[str]:
    if not section_text:
        return []
    lines = [l.strip() for l in section_text.splitlines() if l.strip()]
    return lines[:15]


def _extract_certifications(section_text: str) -> list[str]:
    if not section_text:
        return []
    items = re.split(r"[•·\n]+", section_text)
    return [i.strip() for i in items if len(i.strip()) > 3][:10]

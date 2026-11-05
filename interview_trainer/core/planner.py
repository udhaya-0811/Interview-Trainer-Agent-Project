"""
planner.py – Generate a day-by-day / week-by-week preparation plan using Granite.

The plan is based on identified knowledge gaps from evaluation results and is
exported as Markdown for download.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from interview_trainer.core.evaluator import EvaluationResult
from interview_trainer.core.granite_client import GraniteClient, get_granite_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class PrepPlan:
    """A structured preparation plan."""

    role: str
    experience_level: str
    plan_markdown: str
    gaps_summary: list[str] = field(default_factory=list)
    duration_weeks: int = 2


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

class PrepPlanner:
    """Generate a personalised interview preparation plan using IBM Granite.

    Args:
        client: :class:`GraniteClient` instance (uses singleton if not provided).
    """

    def __init__(self, client: Optional[GraniteClient] = None) -> None:
        self._client = client or get_granite_client()

    def generate_plan(
        self,
        role: str,
        experience_level: str,
        evaluation_results: list[EvaluationResult],
        skills: Optional[list[str]] = None,
        duration_weeks: int = 2,
    ) -> PrepPlan:
        """Generate a preparation plan based on evaluation gaps.

        Args:
            role:                Target job role.
            experience_level:    Candidate's experience level.
            evaluation_results:  List of evaluation results from mock interview.
            skills:              Known skills from resume (optional).
            duration_weeks:      Plan duration in weeks (1, 2, or 4).

        Returns:
            A :class:`PrepPlan` with a Markdown-formatted plan.
        """
        gaps = _extract_gaps(evaluation_results)
        weak_areas = _identify_weak_areas(evaluation_results)

        prompt = _build_planner_prompt(
            role=role,
            experience_level=experience_level,
            gaps=gaps,
            weak_areas=weak_areas,
            skills=skills or [],
            duration_weeks=duration_weeks,
        )

        plan_text = self._client.generate(prompt, max_new_tokens=1500, temperature=0.4)

        # Ensure it is valid Markdown
        if not plan_text.strip().startswith("#"):
            plan_text = f"# {role} Interview Preparation Plan\n\n" + plan_text

        return PrepPlan(
            role=role,
            experience_level=experience_level,
            plan_markdown=plan_text,
            gaps_summary=gaps[:10],
            duration_weeks=duration_weeks,
        )

    def generate_quick_plan(
        self,
        role: str,
        experience_level: str,
        interview_type: str,
        duration_weeks: int = 1,
    ) -> PrepPlan:
        """Generate a generic prep plan without evaluation results.

        Useful when a user wants a plan before doing mock interviews.
        """
        prompt = _build_quick_plan_prompt(
            role=role,
            experience_level=experience_level,
            interview_type=interview_type,
            duration_weeks=duration_weeks,
        )

        plan_text = self._client.generate(prompt, max_new_tokens=1500, temperature=0.4)

        if not plan_text.strip().startswith("#"):
            plan_text = f"# {role} Interview Preparation Plan\n\n" + plan_text

        return PrepPlan(
            role=role,
            experience_level=experience_level,
            plan_markdown=plan_text,
            duration_weeks=duration_weeks,
        )


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _build_planner_prompt(
    role: str,
    experience_level: str,
    gaps: list[str],
    weak_areas: list[str],
    skills: list[str],
    duration_weeks: int,
) -> str:
    gaps_str = "\n".join(f"- {g}" for g in gaps) if gaps else "- General preparation needed"
    weak_str = "\n".join(f"- {w}" for w in weak_areas) if weak_areas else "- No specific weak areas identified"
    skills_str = ", ".join(skills[:8]) if skills else "not specified"
    time_unit = "day" if duration_weeks == 1 else "week"
    sections = duration_weeks * (7 if duration_weeks == 1 else 1)

    return f"""You are an expert career coach creating a personalised interview preparation plan.

CANDIDATE PROFILE:
- Target Role: {role}
- Experience Level: {experience_level}
- Known Skills: {skills_str}

IDENTIFIED GAPS (from mock interview evaluations):
{gaps_str}

WEAK AREAS BY DIMENSION:
{weak_str}

TASK: Create a detailed {duration_weeks}-week interview preparation plan for this candidate.
The plan should address their specific gaps and weaknesses.

FORMAT REQUIREMENTS (use Markdown):
1. Start with a summary section: candidate profile, key gaps to address, overall strategy.
2. Create a {time_unit}-by-{time_unit} schedule for {duration_weeks} {'week' if duration_weeks > 1 else 'week'} ({sections} {time_unit}s).
3. For each {time_unit} include:
   - Focus topic (addressing a specific gap)
   - 2-3 specific study resources or practice tasks
   - One practice question to solve
   - Expected outcome
4. End with a "Day Before Interview" checklist.
5. Include a resources section with free online resources (documentation, courses, practice sites).

Generate the complete Markdown plan now:"""


def _build_quick_plan_prompt(
    role: str,
    experience_level: str,
    interview_type: str,
    duration_weeks: int,
) -> str:
    time_unit = "day" if duration_weeks == 1 else "week"
    sections = 7 if duration_weeks == 1 else duration_weeks

    return f"""You are an expert career coach. Create a {duration_weeks}-week interview preparation plan.

CANDIDATE PROFILE:
- Target Role: {role}
- Experience Level: {experience_level}
- Interview Type: {interview_type}

FORMAT (Markdown):
1. Executive summary (what to focus on)
2. {sections} {time_unit}s of structured preparation:
   - Each {time_unit}: topic, tasks, practice question, resource
3. Interview day checklist
4. Key resources

Generate the complete Markdown plan:"""


# ---------------------------------------------------------------------------
# Gap extraction helpers
# ---------------------------------------------------------------------------

def _extract_gaps(results: list[EvaluationResult]) -> list[str]:
    """Collect all unique gaps from evaluation results."""
    seen: set[str] = set()
    gaps: list[str] = []
    for result in results:
        for gap in result.gaps:
            if gap and gap not in seen:
                seen.add(gap)
                gaps.append(gap)
    return gaps


def _identify_weak_areas(results: list[EvaluationResult]) -> list[str]:
    """Identify dimensions with consistently low scores."""
    if not results:
        return []

    # Aggregate scores per dimension
    dim_totals: dict[str, list[int]] = {}
    for result in results:
        for ds in result.dimension_scores:
            dim_totals.setdefault(ds.dimension, []).append(ds.score)

    weak_areas: list[str] = []
    for dim, scores in dim_totals.items():
        avg = sum(scores) / len(scores)
        if avg < 6:
            weak_areas.append(f"{dim.title()} (avg score: {avg:.1f}/10)")

    return sorted(weak_areas)

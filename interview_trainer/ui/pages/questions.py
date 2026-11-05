"""
questions.py – Question bank page for Interview Trainer Agent.

Generates and displays the full question set with model answers and citations.
"""
from __future__ import annotations

import streamlit as st

from interview_trainer.core.granite_client import GraniteCredentialsError, GraniteAPIError
from interview_trainer.core.knowledge_base import get_knowledge_base
from interview_trainer.core.question_generator import QuestionGenerator, QuestionSet, InterviewQuestion
from interview_trainer.ui.helpers import (
    require_profile,
    show_error,
    show_spinner_text,
    render_citation_box,
    difficulty_badge,
    category_badge,
)


def render_questions() -> None:
    """Render the Question Bank page."""
    if not require_profile():
        return

    st.title("📚 Question Bank")
    profile = st.session_state.user_profile

    st.markdown(
        f"**Role:** {profile['role']} | "
        f"**Level:** {profile['experience_level']} | "
        f"**Type:** {profile['interview_type']}"
    )
    st.markdown("---")

    col_gen, col_opts = st.columns([1, 2])
    with col_gen:
        if st.button("🔄 Generate Questions", type="primary", use_container_width=True):
            _generate_questions(profile)

    with col_opts:
        if st.session_state.get("question_set"):
            qs: QuestionSet = st.session_state.question_set
            total = len(qs.all_questions())
            st.info(
                f"✅ {total} questions generated: "
                f"{len(qs.technical)} technical, {len(qs.behavioral)} behavioral, "
                f"{len(qs.hr)} HR, {len(qs.resume_based)} resume-based"
            )
            if st.button("▶ Start Mock Interview", use_container_width=True):
                st.session_state.page = "mock_interview"
                st.rerun()

    # Display questions
    if st.session_state.get("question_set"):
        _display_question_set(st.session_state.question_set)


# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

def _generate_questions(profile: dict) -> None:
    """Invoke the question generator and store result in session state."""
    with st.spinner("🤖 Generating personalised questions with IBM Granite…"):
        try:
            kb = get_knowledge_base()
            generator = QuestionGenerator(kb=kb)

            qs = generator.generate_question_set(
                role=profile["role"],
                role_key=profile["role_key"],
                experience_level=profile["experience_level"],
                interview_type=profile["interview_type"],
                resume_data=st.session_state.get("resume_data"),
                company_type=profile.get("company_type", "Any"),
            )
            st.session_state.question_set = qs
            st.rerun()

        except GraniteCredentialsError as exc:
            show_error(
                f"**IBM watsonx.ai credentials not configured.**\n\n{exc}\n\n"
                "Please create a `.env` file based on `.env.example` and restart the app."
            )
        except GraniteAPIError as exc:
            show_error(f"**Granite API error:** {exc}")
        except Exception as exc:
            show_error(f"**Unexpected error:** {exc}")


# ---------------------------------------------------------------------------
# Question display
# ---------------------------------------------------------------------------

def _display_question_set(qs: QuestionSet) -> None:
    """Display the question set grouped by category."""
    sections = [
        ("⚙️ Technical Questions", qs.technical),
        ("🧠 Behavioral Questions (STAR)", qs.behavioral),
        ("🤝 HR & Situational", qs.hr),
        ("📋 Resume-Based Questions", qs.resume_based),
    ]

    # Filter control
    show_answers = st.toggle("Show Model Answers", value=True)
    show_citations = st.toggle("Show Citations", value=True)

    for section_title, questions in sections:
        if not questions:
            continue
        st.subheader(section_title)
        for q in questions:
            _render_question_card(q, show_answers, show_citations)
        st.markdown("---")


def _render_question_card(
    q: InterviewQuestion,
    show_answer: bool,
    show_citations: bool,
) -> None:
    """Render a single question card with optional answer and citations."""
    with st.expander(
        f"{q.question_id} {difficulty_badge(q.difficulty)} {category_badge(q.category)} — {q.question[:100]}",
        expanded=False,
    ):
        st.markdown(f"**Question:** {q.question}")

        if show_answer and q.model_answer:
            st.markdown("---")
            if q.star_format:
                st.markdown("**📌 Model Answer (STAR Format):**")
                _render_star_answer(q.model_answer)
            else:
                st.markdown("**📌 Model Answer:**")
                st.markdown(q.model_answer)

        if show_citations and q.citations:
            st.markdown("")
            for citation in q.citations:
                render_citation_box(citation)


def _render_star_answer(answer: str) -> None:
    """Attempt to visually structure a STAR-format answer."""
    import re
    star_parts = {
        "Situation": None,
        "Task": None,
        "Action": None,
        "Result": None,
    }
    for part in star_parts:
        match = re.search(rf"\*\*{part}[:\*]*\*?\*?\s*(.+?)(?=\*\*(?:Situation|Task|Action|Result)|$)", answer, re.DOTALL | re.IGNORECASE)
        if match:
            star_parts[part] = match.group(1).strip()

    if any(star_parts.values()):
        for part, content in star_parts.items():
            if content:
                st.markdown(f"**{part}:** {content}")
    else:
        st.markdown(answer)

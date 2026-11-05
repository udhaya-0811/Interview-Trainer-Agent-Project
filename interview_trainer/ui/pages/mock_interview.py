"""
mock_interview.py – Mock interview mode page for Interview Trainer Agent.

Presents one question at a time, collects user answer, evaluates it via Granite,
and shows scored rubric feedback.
"""
from __future__ import annotations

import streamlit as st

from interview_trainer.core.evaluator import AnswerEvaluator, EvaluationResult
from interview_trainer.core.granite_client import GraniteCredentialsError, GraniteAPIError
from interview_trainer.core.question_generator import InterviewQuestion, QuestionSet
from interview_trainer.core.session_store import get_session_store
from interview_trainer.ui.helpers import (
    require_profile,
    require_question_set,
    show_error,
    show_success,
    difficulty_badge,
    category_badge,
    render_score_gauge,
    render_citation_box,
)


def render_mock_interview() -> None:
    """Render the mock interview mode page."""
    if not require_profile():
        return
    if not require_question_set():
        return

    st.title("🎤 Mock Interview")
    profile = st.session_state.user_profile
    qs: QuestionSet = st.session_state.question_set
    all_questions = qs.all_questions()

    if not all_questions:
        st.warning("No questions available. Please generate questions first.")
        return

    # Initialise mock interview state
    _init_mock_state(all_questions)
    mock = st.session_state.mock_state

    _render_progress_bar(mock, all_questions)
    st.markdown("---")

    current_idx = mock["current_idx"]

    if current_idx >= len(all_questions):
        _render_session_summary(mock, profile, qs)
        return

    current_q = all_questions[current_idx]
    _render_question(current_q, current_idx, len(all_questions))

    # Show evaluation if already answered
    if current_idx in mock["evaluations"]:
        _render_evaluation(mock["evaluations"][current_idx])
        _render_navigation(mock, all_questions)
    else:
        _render_answer_form(current_q, current_idx, mock)


# ---------------------------------------------------------------------------
# State initialisation
# ---------------------------------------------------------------------------

def _init_mock_state(all_questions: list[InterviewQuestion]) -> None:
    if "mock_state" not in st.session_state:
        st.session_state.mock_state = {
            "current_idx": 0,
            "evaluations": {},    # idx -> EvaluationResult
            "scores": [],         # list of overall scores
            "session_saved": False,
        }


# ---------------------------------------------------------------------------
# Question rendering
# ---------------------------------------------------------------------------

def _render_progress_bar(mock: dict, all_questions: list[InterviewQuestion]) -> None:
    answered = len(mock["evaluations"])
    total = len(all_questions)
    progress = answered / total if total > 0 else 0
    st.progress(progress, text=f"Progress: {answered}/{total} questions answered")


def _render_question(q: InterviewQuestion, idx: int, total: int) -> None:
    st.markdown(
        f"### Question {idx + 1} of {total} "
        f"{difficulty_badge(q.difficulty)} {category_badge(q.category)}"
    )
    st.markdown(f"**{q.question}**")

    # Hint for behavioral
    if q.star_format or q.category == "behavioral":
        st.info(
            "💡 **Tip:** Use the STAR method — "
            "**S**ituation → **T**ask → **A**ction → **R**esult"
        )


# ---------------------------------------------------------------------------
# Answer form
# ---------------------------------------------------------------------------

def _render_answer_form(
    q: InterviewQuestion, idx: int, mock: dict
) -> None:
    with st.form(key=f"answer_form_{idx}"):
        user_answer = st.text_area(
            "Your Answer",
            height=200,
            placeholder="Type your answer here… take your time.",
            key=f"answer_text_{idx}",
        )
        submitted = st.form_submit_button(
            "📤 Submit Answer", type="primary", use_container_width=True
        )

    if submitted:
        if not user_answer.strip():
            st.warning("Please write an answer before submitting.")
            return
        _evaluate_answer(q, idx, user_answer, mock)
        st.rerun()


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def _evaluate_answer(
    q: InterviewQuestion, idx: int, user_answer: str, mock: dict
) -> None:
    with st.spinner("🤖 IBM Granite is evaluating your answer…"):
        try:
            evaluator = AnswerEvaluator()
            result = evaluator.evaluate(
                question=q.question,
                model_answer=q.model_answer,
                user_answer=user_answer,
                category=q.category,
            )
            mock["evaluations"][idx] = result
            mock["scores"].append(result.overall_score)
        except GraniteCredentialsError as exc:
            show_error(f"Credentials error: {exc}")
        except GraniteAPIError as exc:
            show_error(f"API error: {exc}")
        except Exception as exc:
            show_error(f"Evaluation error: {exc}")


def _render_evaluation(result: EvaluationResult) -> None:
    """Display evaluation results for the answered question."""
    st.markdown("---")
    st.markdown("### 📊 Evaluation")

    # Overall score
    col_score, col_valid = st.columns([1, 3])
    with col_score:
        render_score_gauge(result.overall_score)

    with col_valid:
        if not result.is_valid:
            st.warning("⚠️ Evaluation parsing was incomplete. Scores are approximate.")

    # Dimension scores
    st.markdown("#### Rubric Breakdown")
    cols = st.columns(5)
    for i, ds in enumerate(result.dimension_scores):
        with cols[i]:
            color = _score_color(ds.score)
            st.markdown(
                f"""<div style="text-align:center; padding:8px; background:{color}20; 
                border:1px solid {color}; border-radius:8px;">
                <div style="font-size:1.6rem;font-weight:700;color:{color}">{ds.score}/10</div>
                <div style="font-size:0.75rem;font-weight:600">{ds.dimension.upper()}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    # Dimension feedback
    with st.expander("📋 Detailed Dimension Feedback"):
        for ds in result.dimension_scores:
            st.markdown(f"**{ds.dimension.title()}:** {ds.feedback}")

    # Strengths & Gaps
    col_s, col_g = st.columns(2)
    with col_s:
        st.markdown("#### ✅ Strengths")
        for s in result.strengths:
            st.markdown(f"• {s}")

    with col_g:
        st.markdown("#### 🔧 Areas to Improve")
        for g in result.gaps:
            st.markdown(f"• {g}")

    # Improved answer
    if result.improved_answer:
        with st.expander("✨ Improved Answer (by IBM Granite)"):
            st.markdown(result.improved_answer)


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

def _render_navigation(mock: dict, all_questions: list[InterviewQuestion]) -> None:
    st.markdown("---")
    col_prev, col_skip, col_next = st.columns([1, 1, 1])

    current_idx = mock["current_idx"]
    total = len(all_questions)

    with col_prev:
        if current_idx > 0:
            if st.button("⬅ Previous", use_container_width=True):
                mock["current_idx"] -= 1
                st.rerun()

    with col_skip:
        if current_idx < total - 1:
            if st.button("⏭ Skip", use_container_width=True):
                mock["current_idx"] += 1
                st.rerun()

    with col_next:
        if current_idx < total - 1:
            if st.button("Next ➡", type="primary", use_container_width=True):
                mock["current_idx"] += 1
                st.rerun()
        else:
            if st.button("🏁 Finish Interview", type="primary", use_container_width=True):
                mock["current_idx"] = total
                st.rerun()


# ---------------------------------------------------------------------------
# Session summary
# ---------------------------------------------------------------------------

def _render_session_summary(
    mock: dict, profile: dict, qs: QuestionSet
) -> None:
    """Display end-of-session summary and save to history."""
    st.markdown("## 🏁 Interview Complete!")

    scores = mock.get("scores", [])
    if scores:
        avg = sum(scores) / len(scores)
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall Score", f"{avg:.1f}/10")
        col2.metric("Questions Answered", len(scores))
        col3.metric("Questions Skipped", len(qs.all_questions()) - len(scores))

        # Per-question summary
        st.markdown("### Question-by-Question Summary")
        all_questions = qs.all_questions()
        for idx, result in mock["evaluations"].items():
            q = all_questions[idx]
            color = _score_color(result.overall_score)
            st.markdown(
                f"**{q.question_id}** {category_badge(q.category)} — "
                f"Score: <span style='color:{color};font-weight:700'>"
                f"{result.overall_score}/10</span> — {q.question[:80]}",
                unsafe_allow_html=True,
            )

        # Save session
        if not mock.get("session_saved"):
            _save_session(mock, profile, qs, avg)
            mock["session_saved"] = True
            show_success("Session saved to history!")

        # Actions
        st.markdown("---")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("📊 View Progress", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
        with col_b:
            if st.button("📝 Generate Prep Plan", use_container_width=True):
                st.session_state.page = "prep_plan"
                st.rerun()
        with col_c:
            if st.button("🔄 New Interview", use_container_width=True):
                st.session_state.pop("mock_state", None)
                st.session_state.pop("question_set", None)
                st.session_state.page = "setup"
                st.rerun()
    else:
        st.info("No answers were submitted in this session.")
        if st.button("🔄 Try Again"):
            st.session_state.pop("mock_state", None)
            st.rerun()


# ---------------------------------------------------------------------------
# Session persistence
# ---------------------------------------------------------------------------

def _save_session(
    mock: dict, profile: dict, qs: QuestionSet, avg_score: float
) -> None:
    """Save the completed session to SQLite."""
    try:
        store = get_session_store()
        session_id = store.save_session(
            user_name=profile.get("user_name", ""),
            role=profile["role"],
            experience_level=profile["experience_level"],
            interview_type=profile["interview_type"],
            company_type=profile.get("company_type", "Any"),
            overall_score=round(avg_score, 2),
            questions_attempted=len(mock["evaluations"]),
        )

        # Save individual question scores
        all_questions = qs.all_questions()
        for idx, result in mock["evaluations"].items():
            q = all_questions[idx]
            dim_scores = {ds.dimension: ds.score for ds in result.dimension_scores}
            store.save_question_score(
                session_id=session_id,
                question_id=q.question_id,
                question_text=q.question,
                category=q.category,
                user_answer=result.user_answer,
                overall_score=result.overall_score,
                dimension_scores=dim_scores,
                strengths=result.strengths,
                gaps=result.gaps,
            )

        st.session_state.last_session_id = session_id
        # Store evaluations for prep plan
        st.session_state.last_evaluations = list(mock["evaluations"].values())

    except Exception as exc:
        show_error(f"Could not save session: {exc}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _score_color(score: float) -> str:
    if score >= 8:
        return "#16a34a"   # green
    elif score >= 6:
        return "#ca8a04"   # amber
    elif score >= 4:
        return "#dc7219"   # orange
    return "#dc2626"       # red

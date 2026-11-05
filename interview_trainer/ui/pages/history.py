"""
history.py – Session history and progress chart page.

Shows past sessions stored in SQLite and renders a progress chart.
"""
from __future__ import annotations

import json

import streamlit as st

from interview_trainer.core.session_store import get_session_store, Session
from interview_trainer.ui.helpers import require_profile


def render_history() -> None:
    """Render the session history and progress page."""
    if not require_profile():
        return

    st.title("📊 Progress & History")
    profile = st.session_state.user_profile
    user_name = profile.get("user_name", "")

    store = get_session_store()
    sessions = store.get_sessions(user_name=user_name or None, limit=50)

    if not sessions:
        st.info(
            "No sessions recorded yet. Complete a mock interview to see your progress here."
        )
        if st.button("▶ Start Mock Interview"):
            st.session_state.page = "mock_interview"
            st.rerun()
        return

    # Summary metrics
    _render_summary_metrics(sessions)
    st.markdown("---")

    # Progress chart
    _render_progress_chart(store, user_name)
    st.markdown("---")

    # Dimension radar
    _render_dimension_chart(store, user_name)
    st.markdown("---")

    # Sessions table
    _render_sessions_table(sessions, store)


# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------

def _render_summary_metrics(sessions: list[Session]) -> None:
    scores = [s.overall_score for s in sessions if s.overall_score > 0]
    total_q = sum(s.questions_attempted for s in sessions)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sessions", len(sessions))
    col2.metric("Avg Score", f"{sum(scores)/len(scores):.1f}/10" if scores else "—")
    col3.metric("Best Session", f"{max(scores):.1f}/10" if scores else "—")
    col4.metric("Questions Answered", total_q)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------

def _render_progress_chart(store, user_name: str) -> None:
    st.subheader("📈 Score Progress Over Time")
    progress_data = store.get_progress_data(user_name=user_name or None, limit=20)

    if not progress_data:
        st.info("Not enough data for chart.")
        return

    dates = [d["date"] for d in progress_data]
    scores = [d["score"] for d in progress_data]

    # Use Streamlit's built-in line chart
    import pandas as pd
    df = pd.DataFrame({"Session Score": scores}, index=dates)
    st.line_chart(df, color="#3b82d4")


def _render_dimension_chart(store, user_name: str) -> None:
    st.subheader("🕸 Skill Dimension Averages")
    dim_avgs = store.get_dimension_averages(user_name=user_name or None)

    if not dim_avgs:
        st.info("Complete at least one evaluated session to see dimension scores.")
        return

    import pandas as pd
    df = pd.DataFrame(
        {"Average Score": list(dim_avgs.values())},
        index=[k.title() for k in dim_avgs.keys()],
    )
    st.bar_chart(df, color="#7c5cd8")


# ---------------------------------------------------------------------------
# Sessions table
# ---------------------------------------------------------------------------

def _render_sessions_table(sessions: list[Session], store) -> None:
    st.subheader("📋 Session History")

    for s in sessions:
        score_color = (
            "#16a34a" if s.overall_score >= 7
            else "#ca8a04" if s.overall_score >= 5
            else "#dc2626"
        )
        with st.expander(
            f"{'📅'} {s.created_at[:16].replace('T', ' ')} | "
            f"{s.role} | {s.experience_level} | "
            f"Score: {s.overall_score:.1f}/10",
            expanded=False,
        ):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**Role:** {s.role}")
            col1.markdown(f"**Level:** {s.experience_level}")
            col2.markdown(f"**Type:** {s.interview_type}")
            col2.markdown(f"**Company:** {s.company_type}")
            col3.metric("Score", f"{s.overall_score:.1f}/10")
            col3.metric("Questions", s.questions_attempted)

            # Show question-level breakdown
            if s.session_id:
                q_scores = store.get_question_scores(s.session_id)
                if q_scores:
                    st.markdown("**Question Scores:**")
                    score_cols = st.columns(min(len(q_scores), 5))
                    for i, qs in enumerate(q_scores):
                        col = score_cols[i % len(score_cols)]
                        with col:
                            col.markdown(
                                f"<small><b>{qs.question_id}</b><br>"
                                f"<span style='color:{_score_color(qs.overall_score)}'>"
                                f"{qs.overall_score:.1f}</span></small>",
                                unsafe_allow_html=True,
                            )

            # Delete button
            if st.button(
                f"🗑 Delete Session", key=f"del_{s.session_id}", type="secondary"
            ):
                store.delete_session(s.session_id)
                st.rerun()


def _score_color(score: float) -> str:
    if score >= 8:
        return "#16a34a"
    elif score >= 6:
        return "#ca8a04"
    return "#dc2626"

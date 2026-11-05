"""
prep_plan.py – Preparation plan generation and export page.

Uses Granite to create a day/week-by-week study plan and offers Markdown download.
"""
from __future__ import annotations

import streamlit as st

from interview_trainer.core.granite_client import GraniteCredentialsError, GraniteAPIError
from interview_trainer.core.planner import PrepPlanner
from interview_trainer.ui.helpers import require_profile, show_error, show_success


def render_prep_plan() -> None:
    """Render the preparation plan page."""
    if not require_profile():
        return

    st.title("📝 Preparation Plan")
    profile = st.session_state.user_profile

    st.markdown(
        "Generate a personalised study plan based on your profile and mock interview results. "
        "Download it as Markdown for offline use."
    )
    st.markdown("---")

    # Options
    col1, col2, col3 = st.columns(3)
    with col1:
        duration_weeks = st.selectbox(
            "Plan Duration",
            options=[1, 2, 4],
            format_func=lambda x: f"{x} Week{'s' if x > 1 else ''}",
            index=1,
        )

    with col2:
        use_eval_results = st.checkbox(
            "Use Mock Interview Results",
            value=bool(st.session_state.get("last_evaluations")),
            help="Tailor the plan to your identified gaps",
        )

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.button(
            "🤖 Generate Plan", type="primary", use_container_width=True
        )

    if generate_btn:
        _generate_plan(profile, duration_weeks, use_eval_results)

    # Display plan
    if st.session_state.get("prep_plan"):
        _display_plan(st.session_state.prep_plan)


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _generate_plan(profile: dict, duration_weeks: int, use_evals: bool) -> None:
    with st.spinner("🤖 IBM Granite is crafting your preparation plan…"):
        try:
            planner = PrepPlanner()
            evals = st.session_state.get("last_evaluations", []) if use_evals else []

            if evals:
                plan = planner.generate_plan(
                    role=profile["role"],
                    experience_level=profile["experience_level"],
                    evaluation_results=evals,
                    skills=st.session_state.get("resume_data", {}).get("skills", []),
                    duration_weeks=duration_weeks,
                )
            else:
                plan = planner.generate_quick_plan(
                    role=profile["role"],
                    experience_level=profile["experience_level"],
                    interview_type=profile.get("interview_type", "Mixed"),
                    duration_weeks=duration_weeks,
                )

            st.session_state.prep_plan = plan
            show_success("Plan generated! Scroll down to view and download.")
            st.rerun()

        except GraniteCredentialsError as exc:
            show_error(f"Credentials error: {exc}")
        except GraniteAPIError as exc:
            show_error(f"API error: {exc}")
        except Exception as exc:
            show_error(f"Unexpected error: {exc}")


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def _display_plan(plan) -> None:
    st.markdown("---")

    # Metadata
    col1, col2, col3 = st.columns(3)
    col1.metric("Role", plan.role)
    col2.metric("Experience", plan.experience_level)
    col3.metric("Duration", f"{plan.duration_weeks} week{'s' if plan.duration_weeks > 1 else ''}")

    if plan.gaps_summary:
        with st.expander("🔍 Identified Gaps Addressed"):
            for gap in plan.gaps_summary:
                st.markdown(f"• {gap}")

    st.markdown("---")
    st.markdown("### 📋 Your Preparation Plan")

    # Render Markdown
    st.markdown(plan.plan_markdown)

    # Download button
    st.markdown("---")
    filename = f"prep_plan_{plan.role.lower().replace(' ', '_')}.md"
    st.download_button(
        label="⬇️ Download Plan as Markdown",
        data=plan.plan_markdown.encode("utf-8"),
        file_name=filename,
        mime="text/markdown",
        type="primary",
        use_container_width=True,
    )

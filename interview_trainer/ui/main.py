"""
main.py – Streamlit application entry point for Interview Trainer Agent.

Wires together all UI screens via a sidebar navigation.
"""
from __future__ import annotations

import streamlit as st

from interview_trainer.ui import pages


def main() -> None:
    """Configure and launch the Streamlit application."""
    st.set_page_config(
        page_title="Interview Trainer Agent",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _inject_custom_css()
    _render_sidebar()
    _render_active_page()


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------

def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🎯 Interview Trainer")
        st.markdown("*Powered by IBM Granite on watsonx.ai*")
        st.markdown("---")

        nav_options = {
            "🏠 Setup Profile": "setup",
            "📚 Question Bank": "questions",
            "🎤 Mock Interview": "mock_interview",
            "📊 Progress & History": "history",
            "📝 Prep Plan": "prep_plan",
        }

        if "page" not in st.session_state:
            st.session_state.page = "setup"

        for label, page_key in nav_options.items():
            is_active = st.session_state.page == page_key
            btn_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=btn_type):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("---")
        # Show session context if set up
        if st.session_state.get("profile_complete"):
            profile = st.session_state.get("user_profile", {})
            st.markdown(f"**Role:** {profile.get('role', '—')}")
            st.markdown(f"**Level:** {profile.get('experience_level', '—')}")
            if profile.get("user_name"):
                st.markdown(f"**Name:** {profile['user_name']}")

        st.markdown("---")
        st.caption("IBM Granite | watsonx.ai | RAG-powered")


# ---------------------------------------------------------------------------
# Active page dispatcher
# ---------------------------------------------------------------------------

def _render_active_page() -> None:
    page = st.session_state.get("page", "setup")
    dispatch = {
        "setup":        pages.render_setup,
        "questions":    pages.render_questions,
        "mock_interview": pages.render_mock_interview,
        "history":      pages.render_history,
        "prep_plan":    pages.render_prep_plan,
    }
    render_fn = dispatch.get(page, pages.render_setup)
    render_fn()


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def _inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .stButton > button { border-radius: 6px; }
        .metric-card {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }
        .score-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .citation-box {
            background: #eff6ff;
            border-left: 3px solid #3b82d4;
            padding: 0.4rem 0.8rem;
            border-radius: 0 4px 4px 0;
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

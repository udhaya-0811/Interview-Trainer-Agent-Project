"""
helpers.py – Shared UI utility functions for Streamlit pages.
"""
from __future__ import annotations

import streamlit as st


# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------

def require_profile() -> bool:
    """Show a warning and return False if the user has not set up a profile."""
    if not st.session_state.get("profile_complete"):
        st.warning("⚠️ Please complete your profile setup first.")
        if st.button("Go to Setup →"):
            st.session_state.page = "setup"
            st.rerun()
        return False
    return True


def require_question_set() -> bool:
    """Show a warning and return False if no question set has been generated."""
    if not st.session_state.get("question_set"):
        st.warning("⚠️ No question set found. Please generate questions first.")
        if st.button("Go to Question Bank →"):
            st.session_state.page = "questions"
            st.rerun()
        return False
    return True


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def show_error(message: str) -> None:
    """Display a styled error message."""
    st.error(f"🚨 {message}")


def show_warning(message: str) -> None:
    """Display a styled warning message."""
    st.warning(f"⚠️ {message}")


def show_success(message: str) -> None:
    """Display a styled success message."""
    st.success(f"✅ {message}")


def show_spinner_text(text: str) -> st.spinner:  # type: ignore[return]
    """Return a spinner context manager with the given text."""
    return st.spinner(text)


# ---------------------------------------------------------------------------
# Badges and display components
# ---------------------------------------------------------------------------

def difficulty_badge(difficulty: str) -> str:
    """Return an HTML badge for a difficulty level."""
    colours = {
        "beginner": ("#dcfce7", "#16a34a"),
        "intermediate": ("#fef3c7", "#d97706"),
        "advanced": ("#fee2e2", "#dc2626"),
    }
    bg, fg = colours.get(difficulty.lower(), ("#f3f4f6", "#6b7280"))
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:10px;font-size:0.75rem;font-weight:600;">'
        f'{difficulty.title()}</span>'
    )


def category_badge(category: str) -> str:
    """Return an HTML badge for a question category."""
    colours = {
        "technical":    ("#dbeafe", "#1d4ed8"),
        "behavioral":   ("#f3e8ff", "#7c3aed"),
        "hr":           ("#fce7f3", "#be185d"),
        "resume_based": ("#ecfdf5", "#065f46"),
        "soft_skills":  ("#fffbeb", "#92400e"),
    }
    bg, fg = colours.get(category.lower(), ("#f3f4f6", "#6b7280"))
    label = category.replace("_", " ").title()
    return (
        f'<span style="background:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:10px;font-size:0.75rem;font-weight:600;">'
        f'{label}</span>'
    )


def render_citation_box(citation) -> None:
    """Render a citation source box."""
    st.markdown(
        f"""<div class="citation-box">
        📚 Source: <b>{citation.source_file}</b> · {citation.question_id} · 
        Similarity: {citation.similarity_score:.2f}
        </div>""",
        unsafe_allow_html=True,
    )


def render_score_gauge(score: float) -> None:
    """Render a simple score display."""
    color = "#16a34a" if score >= 7 else "#d97706" if score >= 5 else "#dc2626"
    st.markdown(
        f"""<div style="text-align:center;padding:12px;background:{color}15;
        border:2px solid {color};border-radius:12px;">
        <div style="font-size:2rem;font-weight:800;color:{color}">{score:.1f}</div>
        <div style="font-size:0.8rem;color:#57606a">Overall Score / 10</div>
        </div>""",
        unsafe_allow_html=True,
    )

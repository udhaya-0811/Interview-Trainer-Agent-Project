"""
setup.py – Profile setup page for Interview Trainer Agent.

Collects: name, role, experience, interview type, company type, and optional resume.
Triggers resume parsing and shows extracted skills for confirmation.
"""
from __future__ import annotations

import streamlit as st

from interview_trainer.config import (
    COMPANY_TYPES,
    EXPERIENCE_LEVELS,
    INTERVIEW_TYPES,
    SUPPORTED_ROLES,
)
from interview_trainer.core.resume_parser import extract_text_from_file, parse_resume
from interview_trainer.ui.helpers import show_error, show_success, show_warning


def render_setup() -> None:
    """Render the profile setup page."""
    st.title("🎯 Interview Trainer Agent")
    st.markdown(
        "Your AI-powered interview coach using **IBM Granite** on watsonx.ai. "
        "Set up your profile to get personalised questions and coaching."
    )
    st.markdown("---")

    col1, col2 = st.columns([3, 2])

    with col1:
        _render_profile_form()

    with col2:
        _render_resume_upload()


# ---------------------------------------------------------------------------
# Profile form
# ---------------------------------------------------------------------------

def _render_profile_form() -> None:
    st.subheader("👤 Your Profile")

    user_name = st.text_input(
        "Your Name (optional)",
        value=st.session_state.get("form_name", ""),
        placeholder="e.g. Priya Sharma",
        help="Used for personalisation",
    )

    role = st.selectbox(
        "Target Job Role *",
        options=list(SUPPORTED_ROLES.keys()),
        index=0,
        help="Select the role you're preparing for",
    )

    experience_level = st.selectbox(
        "Experience Level *",
        options=EXPERIENCE_LEVELS,
        index=0,
    )

    interview_type = st.selectbox(
        "Interview Type *",
        options=INTERVIEW_TYPES,
        index=2,
        help="Technical: coding & system design | Soft Skills: behavioral & HR | Mixed: all",
    )

    company_type = st.selectbox(
        "Target Company Type (optional)",
        options=COMPANY_TYPES,
        index=0,
    )

    st.markdown("---")

    if st.button("✅ Save Profile & Continue", type="primary", use_container_width=True):
        _save_profile(
            user_name=user_name,
            role=role,
            experience_level=experience_level,
            interview_type=interview_type,
            company_type=company_type,
        )


# ---------------------------------------------------------------------------
# Resume upload
# ---------------------------------------------------------------------------

def _render_resume_upload() -> None:
    st.subheader("📄 Resume (Optional)")
    st.markdown("Upload your resume to get personalised questions based on your experience.")

    tab_upload, tab_paste = st.tabs(["📎 Upload File", "📝 Paste Text"])

    with tab_upload:
        uploaded = st.file_uploader(
            "Upload PDF or DOCX",
            type=["pdf", "docx", "doc"],
            help="Max 10 MB",
        )
        if uploaded is not None:
            _process_uploaded_file(uploaded)

    with tab_paste:
        pasted = st.text_area(
            "Paste your resume text here",
            height=200,
            placeholder="Paste resume content...",
        )
        if st.button("Parse Pasted Text", use_container_width=True):
            if pasted.strip():
                _process_resume_text(pasted)
            else:
                show_warning("Please paste some resume text first.")

    # Show parsed skills
    if st.session_state.get("resume_parsed"):
        _show_parsed_resume()


# ---------------------------------------------------------------------------
# Processing helpers
# ---------------------------------------------------------------------------

def _process_uploaded_file(uploaded_file) -> None:
    """Extract text from uploaded file and parse resume."""
    try:
        file_bytes = uploaded_file.read()
        if len(file_bytes) == 0:
            show_error("The uploaded file is empty.")
            return
        text = extract_text_from_file(file_bytes, uploaded_file.name)
        if not text.strip():
            show_error("Could not extract text from the file. Please try pasting the text instead.")
            return
        _process_resume_text(text)
    except ValueError as exc:
        show_error(str(exc))
    except RuntimeError as exc:
        show_error(f"Parsing library error: {exc}")
    except Exception as exc:
        show_error(f"Unexpected error processing file: {exc}")


def _process_resume_text(text: str) -> None:
    """Parse resume text and store results in session state."""
    with st.spinner("Parsing resume…"):
        try:
            parsed = parse_resume(text)
            st.session_state.resume_text = text
            st.session_state.resume_data = parsed
            st.session_state.resume_parsed = True
            show_success("Resume parsed successfully!")
        except Exception as exc:
            show_error(f"Resume parsing failed: {exc}")


def _show_parsed_resume() -> None:
    """Display parsed resume data with edit capability."""
    st.markdown("---")
    st.markdown("#### 🔍 Extracted Skills")
    st.caption("Review and confirm the skills extracted from your resume.")

    parsed: dict = st.session_state.get("resume_data", {})

    skills = parsed.get("skills", [])
    if skills:
        # Allow user to deselect irrelevant skills
        confirmed_skills = st.multiselect(
            "Confirmed Skills",
            options=skills,
            default=skills,
            help="Deselect any skills that are incorrect",
        )
        st.session_state.resume_data["skills"] = confirmed_skills
    else:
        st.info("No specific skills detected. Questions will be role-based.")

    if parsed.get("projects"):
        with st.expander("📂 Projects Detected"):
            for proj in parsed["projects"]:
                st.markdown(f"• {proj}")

    if parsed.get("education"):
        with st.expander("🎓 Education"):
            for edu in parsed["education"][:3]:
                st.markdown(f"• {edu}")


# ---------------------------------------------------------------------------
# Save profile
# ---------------------------------------------------------------------------

def _save_profile(
    user_name: str,
    role: str,
    experience_level: str,
    interview_type: str,
    company_type: str,
) -> None:
    """Validate and save profile to session state."""
    st.session_state.user_profile = {
        "user_name": user_name.strip(),
        "role": role,
        "role_key": SUPPORTED_ROLES[role],
        "experience_level": experience_level,
        "interview_type": interview_type,
        "company_type": company_type,
    }
    st.session_state.profile_complete = True
    # Reset question set when profile changes
    st.session_state.pop("question_set", None)
    st.session_state.pop("mock_state", None)

    show_success(
        f"Profile saved! You're preparing for **{role}** ({experience_level}). "
        "Head to **Question Bank** to generate your questions."
    )
    st.session_state.form_name = user_name

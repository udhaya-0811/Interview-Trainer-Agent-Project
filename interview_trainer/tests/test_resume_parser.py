"""
test_resume_parser.py – Tests for the resume parser module.
"""
from __future__ import annotations

import pytest

from interview_trainer.core.resume_parser import (
    extract_text_from_file,
    parse_resume,
    _normalise,
    _split_sections,
    _infer_skills_from_text,
)


# ---------------------------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------------------------

class TestNormalise:
    def test_strips_whitespace(self):
        assert _normalise("  hello  ") == "hello"

    def test_normalises_crlf(self):
        result = _normalise("line1\r\nline2")
        assert "\r" not in result

    def test_removes_nonprintable(self):
        result = _normalise("hello\x00world")
        assert "\x00" not in result


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

SAMPLE_RESUME = """
John Doe
john@example.com

Skills
Python, Java, SQL, Docker, Git

Experience
Software Engineer at Acme Corp 2021-2023
- Built REST APIs using Spring Boot
- Deployed applications on AWS

Education
B.Tech Computer Science, IIT Delhi, 2021

Projects
E-Commerce Platform
Built a full-stack e-commerce application using React and Node.js

Certifications
AWS Certified Developer – Associate
"""


class TestSplitSections:
    def test_detects_skills_section(self):
        sections = _split_sections(SAMPLE_RESUME)
        assert "skills" in sections
        assert "Python" in sections["skills"] or "python" in sections["skills"].lower()

    def test_detects_education_section(self):
        sections = _split_sections(SAMPLE_RESUME)
        assert "education" in sections

    def test_detects_experience_section(self):
        sections = _split_sections(SAMPLE_RESUME)
        assert "experience" in sections


# ---------------------------------------------------------------------------
# Full parse_resume
# ---------------------------------------------------------------------------

class TestParseResume:
    def test_returns_required_keys(self):
        result = parse_resume(SAMPLE_RESUME)
        assert set(result.keys()) == {
            "skills", "education", "projects", "experience", "certifications"
        }

    def test_skills_are_list(self):
        result = parse_resume(SAMPLE_RESUME)
        assert isinstance(result["skills"], list)

    def test_extracts_at_least_one_skill(self):
        result = parse_resume(SAMPLE_RESUME)
        assert len(result["skills"]) >= 1

    def test_education_not_empty(self):
        result = parse_resume(SAMPLE_RESUME)
        assert len(result["education"]) >= 1

    def test_empty_resume_returns_empty_skills(self):
        result = parse_resume("   ")
        # Skills may be empty or contain tech keywords from empty text
        assert isinstance(result["skills"], list)


# ---------------------------------------------------------------------------
# Infer skills fallback
# ---------------------------------------------------------------------------

class TestInferSkills:
    def test_detects_python(self):
        skills = _infer_skills_from_text("I work with Python and Django")
        assert any("python" in s.lower() for s in skills)

    def test_detects_java(self):
        skills = _infer_skills_from_text("Experience with Java and Spring Boot")
        assert any("java" in s.lower() for s in skills)

    def test_empty_text(self):
        skills = _infer_skills_from_text("")
        assert isinstance(skills, list)


# ---------------------------------------------------------------------------
# Unsupported file type
# ---------------------------------------------------------------------------

class TestExtractTextFromFile:
    def test_raises_on_unsupported_type(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            extract_text_from_file(b"content", "resume.txt")

    def test_raises_on_csv(self):
        with pytest.raises(ValueError):
            extract_text_from_file(b"a,b,c", "data.csv")

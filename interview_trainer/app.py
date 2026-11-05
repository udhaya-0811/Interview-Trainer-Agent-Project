"""
Interview Trainer Agent – Streamlit entry point.

Run with:
    streamlit run app.py
"""
# Thin entry point; actual page logic lives in ui/ modules imported below.
from interview_trainer.ui import main  # noqa: F401 – imported for side-effects

if __name__ == "__main__":
    main()

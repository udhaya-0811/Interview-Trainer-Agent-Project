"""
Root-level Streamlit entry point for Interview Trainer Agent.

Run from the project root:
    streamlit run app.py
"""
import sys
from pathlib import Path

# Ensure the interview_trainer package is importable
sys.path.insert(0, str(Path(__file__).parent))

from interview_trainer.ui.main import main  # noqa: E402

if __name__ == "__main__" or True:
    main()

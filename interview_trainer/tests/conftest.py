"""
Pytest configuration for Interview Trainer Agent tests.

Ensures the interview_trainer package is importable from tests/.
"""
import sys
from pathlib import Path

# Add the interview_trainer directory to sys.path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

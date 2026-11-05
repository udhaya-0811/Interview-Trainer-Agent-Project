"""interview_trainer.ui.pages package init."""
from interview_trainer.ui.pages.setup import render_setup
from interview_trainer.ui.pages.questions import render_questions
from interview_trainer.ui.pages.mock_interview import render_mock_interview
from interview_trainer.ui.pages.history import render_history
from interview_trainer.ui.pages.prep_plan import render_prep_plan

__all__ = [
    "render_setup",
    "render_questions",
    "render_mock_interview",
    "render_history",
    "render_prep_plan",
]

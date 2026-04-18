"""Database models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.question import Question
from app.models.user_answer import UserAnswer
from app.models.stats import Stats
from app.models.sub_category import SubCategory
from app.models.difficulty import DifficultyLevel

__all__ = ["db", "Question", "UserAnswer", "Stats", "SubCategory", "DifficultyLevel"]

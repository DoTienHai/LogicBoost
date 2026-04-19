"""Database models package."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.question import Question
from app.models.user_answer import UserAnswer
from app.models.stats import Stats
from app.models.sub_category import SubCategory
from app.models.difficulty import DifficultyLevel
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission

__all__ = [
    "db",
    "Question",
    "UserAnswer",
    "Stats",
    "SubCategory",
    "DifficultyLevel",
    "User",
    "Role",
    "Permission",
]

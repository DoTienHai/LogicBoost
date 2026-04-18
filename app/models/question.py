"""Question model for LogicBoost."""
from datetime import datetime
from app.models import db


class Question(db.Model):
    """Question model storing quiz content."""

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    # English content (required)
    title = db.Column(db.String(255), nullable=False)
    question = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)

    # Vietnamese content (optional, fallback to English if null)
    title_vi = db.Column(db.String(255))
    question_vi = db.Column(db.Text)
    explanation_vi = db.Column(db.Text)

    # Images (shared across languages)
    question_image = db.Column(db.String(255))
    explanation_image = db.Column(db.String(255))

    # Answer options (null if used as free_text)
    option_a = db.Column(db.String(255))
    option_b = db.Column(db.String(255))
    option_c = db.Column(db.String(255))
    option_d = db.Column(db.String(255))

    # Correct answer
    answer = db.Column(db.String(255), nullable=False)

    # Metadata
    mode = db.Column(db.String(50), nullable=False)  # daily_challenge, mini_game, real_world
    sub_category = db.Column(db.String(50))  # finance, career, business
    difficulty = db.Column(db.Integer, default=1)  # 1-3
    time_limit = db.Column(db.Integer)  # seconds for mini_game

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Question {self.id}: {self.title}>"

    def to_dict(self, lang: str = "en") -> dict:
        """Convert question to dictionary with language support."""
        if lang == "vi":
            return {
                "id": self.id,
                "title": self.title_vi or self.title,
                "question": self.question_vi or self.question,
                "explanation": self.explanation_vi or self.explanation,
                "option_a": self.option_a,
                "option_b": self.option_b,
                "option_c": self.option_c,
                "option_d": self.option_d,
                "answer": self.answer,
                "question_image": self.question_image,
                "explanation_image": self.explanation_image,
                "mode": self.mode,
                "difficulty": self.difficulty,
            }
        return {
            "id": self.id,
            "title": self.title,
            "question": self.question,
            "explanation": self.explanation,
            "option_a": self.option_a,
            "option_b": self.option_b,
            "option_c": self.option_c,
            "option_d": self.option_d,
            "answer": self.answer,
            "question_image": self.question_image,
            "explanation_image": self.explanation_image,
            "mode": self.mode,
            "difficulty": self.difficulty,
        }

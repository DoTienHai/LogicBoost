"""User answer model for LogicBoost."""
from datetime import datetime
from app.models import db


class UserAnswer(db.Model):
    """UserAnswer model storing user quiz responses."""

    __tablename__ = "user_answers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, free_text
    mode = db.Column(db.String(50), nullable=False)  # daily_challenge, mini_game, real_world
    chosen = db.Column(db.String(255), nullable=False)  # 'a','b','c','d' or text
    is_correct = db.Column(db.Boolean, nullable=False)
    time_taken = db.Column(db.Integer)  # seconds
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Note: User model already defines the backref for this relationship
    question = db.relationship("Question", backref=db.backref("user_answers", lazy=True))

    def __repr__(self) -> str:
        return f"<UserAnswer Q{self.question_id}: {self.chosen} ({'✓' if self.is_correct else '✗'})>"

    def to_dict(self) -> dict:
        """Convert user answer to dictionary."""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "question_type": self.question_type,
            "chosen": self.chosen,
            "is_correct": self.is_correct,
            "time_taken": self.time_taken,
            "answered_at": self.answered_at.isoformat(),
        }

"""Stats model for LogicBoost."""
from datetime import datetime
from app.models import db


class Stats(db.Model):
    """Stats model tracking overall performance per mode per user."""

    __tablename__ = "stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mode = db.Column(db.String(50), nullable=False)  # daily_challenge, mini_game, real_world
    correct = db.Column(db.Integer, default=0)
    incorrect = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'mode', name='unique_user_mode'),
    )

    # Note: User model already defines the backref for this relationship,
    # so we don't define it again here to avoid conflicts

    def __repr__(self) -> str:
        return f"<Stats {self.mode}: {self.correct}✓ {self.incorrect}✗>"

    def to_dict(self) -> dict:
        """Convert stats to dictionary."""
        total = self.correct + self.incorrect
        accuracy = (self.correct / total * 100) if total > 0 else 0
        
        return {
            "mode": self.mode,
            "correct": self.correct,
            "incorrect": self.incorrect,
            "total": total,
            "accuracy": round(accuracy, 2),
            "updated_at": self.updated_at.isoformat(),
        }

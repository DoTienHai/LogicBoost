"""SubCategory model for LogicBoost."""
from app.models import db


class SubCategory(db.Model):
    """Sub-category model for organizing real-world questions."""

    __tablename__ = "sub_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # finance, career, business
    display_name = db.Column(db.String(100), nullable=False)  # 💰 Finance, 📈 Career, 🏢 Business
    description = db.Column(db.String(255))  # Optional description

    # Relationship
    questions = db.relationship("Question", backref="sub_category_obj", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SubCategory {self.name}>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
        }

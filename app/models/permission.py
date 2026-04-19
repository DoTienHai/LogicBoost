"""Permission model for RBAC system."""
from datetime import datetime
from app.models import db


class Permission(db.Model):
    """Permission model for fine-grained access control."""

    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # content, user_management, system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"

    def to_dict(self) -> dict:
        """Convert permission to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
        }

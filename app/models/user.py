"""User model with authentication."""
from datetime import datetime
from app.models import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Define junction tables
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    """User model with password hashing and role-based access control."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    roles = db.relationship("Role", secondary=user_roles, backref=db.backref("users", lazy="dynamic"))
    answers = db.relationship("UserAnswer", backref="user", lazy=True, cascade="all, delete-orphan")
    stats = db.relationship("Stats", backref="user", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a specific permission through their assigned roles.
        
        Args:
            permission_name: Name of the permission to check
            
        Returns:
            True if user has the permission, False otherwise
        """
        from app.models.permission import Permission

        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "roles": [{"id": r.id, "name": r.name, "display_name": r.display_name} for r in self.roles],
        }

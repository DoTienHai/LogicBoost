"""Authentication and authorization service."""
from app.models import db, User, Role, Permission
from typing import Tuple, Optional


class AuthService:
    """Service for user authentication and authorization."""

    @staticmethod
    def register_user(
        username: str, email: str, password: str, first_name: str = "", last_name: str = ""
    ) -> Tuple[User, Optional[str]]:
        """
        Register a new user with default 'user' role.

        Args:
            username: Unique username
            email: User's email address
            password: Plain text password to hash
            first_name: User's first name (optional)
            last_name: User's last name (optional)

        Returns:
            Tuple of (User object or None, error message or None)
        """
        # Validate inputs
        if not username or len(username) < 3:
            return None, "Username must be at least 3 characters long"

        if not email or "@" not in email:
            return None, "Valid email address is required"

        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters long"

        # Check username uniqueness
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"

        # Check email uniqueness
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"

        try:
            # Create new user
            user = User(
                username=username, email=email, first_name=first_name, last_name=last_name
            )
            user.set_password(password)

            # Assign default 'user' role
            user_role = Role.query.filter_by(name="user").first()
            if user_role:
                user.roles.append(user_role)

            db.session.add(user)
            db.session.commit()

            return user, None
        except Exception as e:
            db.session.rollback()
            return None, f"Registration failed: {str(e)}"

    @staticmethod
    def login_user(username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Authenticate user with username and password.

        Args:
            username: User's username
            password: User's plain text password

        Returns:
            Tuple of (User object if valid, error message or None)
        """
        if not username or not password:
            return None, "Username and password are required"

        user = User.query.filter_by(username=username).first()

        if not user:
            return None, "Invalid username or password"

        if not user.is_active:
            return None, "Account is disabled"

        if not user.verify_password(password):
            return None, "Invalid username or password"

        return user, None

    @staticmethod
    def change_password(
        user_id: int, old_password: str, new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Change user's password.

        Args:
            user_id: User ID
            old_password: Current password (plain text)
            new_password: New password (plain text)

        Returns:
            Tuple of (success: bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        if not user.verify_password(old_password):
            return False, "Current password is incorrect"

        if not new_password or len(new_password) < 6:
            return False, "New password must be at least 6 characters long"

        if old_password == new_password:
            return False, "New password must be different from current password"

        try:
            user.set_password(new_password)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Password change failed: {str(e)}"

    @staticmethod
    def assign_role(user_id: int, role_id: int) -> Tuple[bool, Optional[str]]:
        """
        Assign a role to a user.

        Args:
            user_id: User ID
            role_id: Role ID

        Returns:
            Tuple of (success: bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        role = Role.query.get(role_id)
        if not role:
            return False, "Role not found"

        if role in user.roles:
            return False, f"User already has role '{role.name}'"

        try:
            user.roles.append(role)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to assign role: {str(e)}"

    @staticmethod
    def revoke_role(user_id: int, role_id: int) -> Tuple[bool, Optional[str]]:
        """
        Remove a role from a user.

        Args:
            user_id: User ID
            role_id: Role ID

        Returns:
            Tuple of (success: bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        role = Role.query.get(role_id)
        if not role:
            return False, "Role not found"

        if role not in user.roles:
            return False, f"User does not have role '{role.name}'"

        try:
            user.roles.remove(role)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Failed to revoke role: {str(e)}"

    @staticmethod
    def update_user(user_id: int, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Update user profile information.

        Args:
            user_id: User ID
            **kwargs: Fields to update (first_name, last_name, email, etc.)

        Returns:
            Tuple of (success: bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        allowed_fields = {"first_name", "last_name", "email"}
        for key, value in kwargs.items():
            if key not in allowed_fields:
                continue

            if key == "email" and value != user.email:
                # Check email uniqueness if changing email
                if User.query.filter_by(email=value).first():
                    return False, "Email already registered"

            setattr(user, key, value)

        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Update failed: {str(e)}"

    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a user and their associated data.

        Args:
            user_id: User ID

        Returns:
            Tuple of (success: bool, error message or None)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"

        try:
            db.session.delete(user)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Delete failed: {str(e)}"

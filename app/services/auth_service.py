"""Authentication and authorization service."""
from app.models import db, User, Role, Permission
from app.constants.error_codes import AuthError
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
            return None, AuthError.USERNAME_TOO_SHORT["message"]

        if not email or "@" not in email:
            return None, AuthError.INVALID_EMAIL["message"]

        if not password or len(password) < 6:
            return None, AuthError.PASSWORD_TOO_SHORT["message"]

        # Check username uniqueness
        if User.query.filter_by(username=username).first():
            return None, AuthError.USERNAME_EXISTS["message"]

        # Check email uniqueness
        if User.query.filter_by(email=email).first():
            return None, AuthError.EMAIL_EXISTS["message"]

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
            return None, AuthError.REGISTRATION_FAILED["message"]

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
            return None, AuthError.MISSING_CREDENTIALS["message"]

        user = User.query.filter_by(username=username).first()

        if not user:
            return None, AuthError.INVALID_CREDENTIALS["message"]

        if not user.is_active:
            return None, AuthError.ACCOUNT_DISABLED["message"]

        if not user.verify_password(password):
            return None, AuthError.INVALID_CREDENTIALS["message"]

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
            return False, AuthError.USER_NOT_FOUND["message"]

        if not user.verify_password(old_password):
            return False, AuthError.WRONG_OLD_PASSWORD["message"]

        if not new_password or len(new_password) < 6:
            return False, AuthError.PASSWORD_TOO_SHORT["message"]

        if old_password == new_password:
            return False, AuthError.SAME_PASSWORD["message"]

        try:
            user.set_password(new_password)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, AuthError.PASSWORD_CHANGE_FAILED["message"]

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
            return False, AuthError.USER_NOT_FOUND["message"]

        role = Role.query.get(role_id)
        if not role:
            return False, AuthError.ROLE_NOT_FOUND["message"]

        if role in user.roles:
            return False, AuthError.ROLE_ALREADY_ASSIGNED["message"]

        try:
            user.roles.append(role)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, AuthError.ROLE_ASSIGNMENT_FAILED["message"]

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
            return False, AuthError.USER_NOT_FOUND["message"]

        role = Role.query.get(role_id)
        if not role:
            return False, AuthError.ROLE_NOT_FOUND["message"]

        if role not in user.roles:
            return False, AuthError.ROLE_NOT_ASSIGNED["message"]

        try:
            user.roles.remove(role)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, AuthError.ROLE_REVOKE_FAILED["message"]

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
            return False, AuthError.USER_NOT_FOUND["message"]

        allowed_fields = {"first_name", "last_name", "email"}
        for key, value in kwargs.items():
            if key not in allowed_fields:
                continue

            if key == "email" and value != user.email:
                # Check email uniqueness if changing email
                if User.query.filter_by(email=value).first():
                    return False, AuthError.EMAIL_EXISTS["message"]

            setattr(user, key, value)

        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, AuthError.USER_UPDATE_FAILED["message"]

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
            return False, AuthError.USER_NOT_FOUND["message"]

        try:
            db.session.delete(user)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, AuthError.USER_DELETE_FAILED["message"]

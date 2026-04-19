"""Tests for authentication service."""
import pytest
from app.models import User, Role, Permission, db
from app.services.auth_service import AuthService


class TestAuthServiceRegistration:
    """Tests for user registration."""

    def test_register_user_success(self, app, client):
        """Test successful user registration."""
        with app.app_context():
            user, error = AuthService.register_user(
                "testuser", "test@example.com", "password123", "John", "Doe"
            )

            assert error is None
            assert user is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.first_name == "John"
            assert user.last_name == "Doe"
            assert user.verify_password("password123")

            # Check default role is assigned
            assert len(user.roles) == 1
            assert user.roles[0].name == "user"

    def test_register_user_duplicate_username(self, app):
        """Test registration fails with duplicate username."""
        with app.app_context():
            # Create first user
            AuthService.register_user("testuser", "test1@example.com", "password123")

            # Try to create user with same username
            user, error = AuthService.register_user(
                "testuser", "test2@example.com", "password123"
            )

            assert error is not None
            assert "Username already exists" in error
            assert user is None

    def test_register_user_duplicate_email(self, app):
        """Test registration fails with duplicate email."""
        with app.app_context():
            # Create first user
            AuthService.register_user("user1", "test@example.com", "password123")

            # Try to create user with same email
            user, error = AuthService.register_user(
                "user2", "test@example.com", "password123"
            )

            assert error is not None
            assert "Email already registered" in error
            assert user is None

    def test_register_user_invalid_username(self, app):
        """Test registration fails with invalid username."""
        with app.app_context():
            # Username too short
            user, error = AuthService.register_user("ab", "test@example.com", "password123")
            assert error is not None
            assert "at least 3 characters" in error
            assert user is None

    def test_register_user_invalid_email(self, app):
        """Test registration fails with invalid email."""
        with app.app_context():
            user, error = AuthService.register_user("testuser", "invalid-email", "password123")
            assert error is not None
            assert "Valid email" in error
            assert user is None

    def test_register_user_weak_password(self, app):
        """Test registration fails with weak password."""
        with app.app_context():
            user, error = AuthService.register_user("testuser", "test@example.com", "short")
            assert error is not None
            assert "at least 6 characters" in error
            assert user is None


class TestAuthServiceLogin:
    """Tests for user login."""

    def test_login_user_success(self, app):
        """Test successful login."""
        with app.app_context():
            # Create user first
            AuthService.register_user("testuser", "test@example.com", "password123")

            # Login
            user, error = AuthService.login_user("testuser", "password123")

            assert error is None
            assert user is not None
            assert user.username == "testuser"

    def test_login_user_wrong_password(self, app):
        """Test login fails with wrong password."""
        with app.app_context():
            # Create user first
            AuthService.register_user("testuser", "test@example.com", "password123")

            # Try to login with wrong password
            user, error = AuthService.login_user("testuser", "wrongpassword")

            assert error is not None
            assert "Invalid username or password" in error
            assert user is None

    def test_login_user_not_found(self, app):
        """Test login fails when user doesn't exist."""
        with app.app_context():
            user, error = AuthService.login_user("nonexistent", "password123")

            assert error is not None
            assert "Invalid username or password" in error
            assert user is None

    def test_login_inactive_user(self, app):
        """Test login fails for inactive user."""
        with app.app_context():
            # Create user
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            # Deactivate user
            user.is_active = False
            db.session.commit()

            # Try to login
            logged_in_user, error = AuthService.login_user("testuser", "password123")

            assert error is not None
            assert "Account is disabled" in error
            assert logged_in_user is None

    def test_login_missing_credentials(self, app):
        """Test login fails with missing credentials."""
        with app.app_context():
            user, error = AuthService.login_user("", "")
            assert error is not None
            assert "required" in error
            assert user is None


class TestAuthServicePassword:
    """Tests for password management."""

    def test_change_password_success(self, app):
        """Test successful password change."""
        with app.app_context():
            # Create user
            user, _ = AuthService.register_user("testuser", "test@example.com", "oldpassword")

            # Change password
            success, error = AuthService.change_password(
                user.id, "oldpassword", "newpassword"
            )

            assert success
            assert error is None

            # Verify new password works
            user, _ = AuthService.login_user("testuser", "newpassword")
            assert user is not None

            # Verify old password doesn't work
            user, _ = AuthService.login_user("testuser", "oldpassword")
            assert user is None

    def test_change_password_wrong_old_password(self, app):
        """Test password change fails with wrong old password."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            success, error = AuthService.change_password(user.id, "wrongpassword", "newpassword")

            assert not success
            assert "Current password is incorrect" in error

    def test_change_password_weak_new_password(self, app):
        """Test password change fails with weak new password."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            success, error = AuthService.change_password(user.id, "password123", "short")

            assert not success
            assert "at least 6 characters" in error

    def test_change_password_same_as_old(self, app):
        """Test password change fails when new password is same as old."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            success, error = AuthService.change_password(user.id, "password123", "password123")

            assert not success
            assert "must be different" in error


class TestAuthServiceRoles:
    """Tests for role assignment."""

    def test_assign_role_success(self, app):
        """Test successful role assignment."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")
            admin_role = Role.query.filter_by(name="admin").first()

            success, error = AuthService.assign_role(user.id, admin_role.id)

            assert success
            assert error is None
            assert admin_role in user.roles

    def test_assign_role_duplicate(self, app):
        """Test assigning role fails when user already has it."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")
            user_role = Role.query.filter_by(name="user").first()

            # Try to assign the default role again
            success, error = AuthService.assign_role(user.id, user_role.id)

            assert not success
            assert "already has role" in error

    def test_revoke_role_success(self, app):
        """Test successful role revocation."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")
            user_role = Role.query.filter_by(name="user").first()

            # Revoke the default role
            success, error = AuthService.revoke_role(user.id, user_role.id)

            assert success
            assert error is None
            assert user_role not in user.roles

    def test_revoke_role_not_assigned(self, app):
        """Test revoking role fails when user doesn't have it."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")
            admin_role = Role.query.filter_by(name="admin").first()

            # Try to revoke a role user doesn't have
            success, error = AuthService.revoke_role(user.id, admin_role.id)

            assert not success
            assert "does not have role" in error


class TestUserPermissions:
    """Tests for permission checking."""

    def test_user_has_permission_via_role(self, app):
        """Test user has permission through their role."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            # Default 'user' role should have view_questions permission
            assert user.has_permission("view_questions")
            assert not user.has_permission("create_questions")

    def test_admin_has_all_permissions(self, app):
        """Test admin has all permissions."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")
            admin_role = Role.query.filter_by(name="admin").first()

            AuthService.assign_role(user.id, admin_role.id)

            # Admin should have all permissions
            assert user.has_permission("view_questions")
            assert user.has_permission("create_questions")
            assert user.has_permission("edit_questions")
            assert user.has_permission("delete_questions")
            assert user.has_permission("import_excel")
            assert user.has_permission("view_users")
            assert user.has_permission("assign_roles")

    def test_user_has_role(self, app):
        """Test checking if user has a specific role."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            assert user.has_role("user")
            assert not user.has_role("admin")


class TestUserUpdate:
    """Tests for user profile updates."""

    def test_update_user_success(self, app):
        """Test successful user update."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")

            success, error = AuthService.update_user(
                user.id, first_name="Jane", last_name="Smith", email="newemail@example.com"
            )

            assert success
            assert error is None

            # Verify update
            db.session.refresh(user)
            assert user.first_name == "Jane"
            assert user.last_name == "Smith"
            assert user.email == "newemail@example.com"

    def test_update_user_duplicate_email(self, app):
        """Test update fails with duplicate email."""
        with app.app_context():
            user1, _ = AuthService.register_user("user1", "test1@example.com", "password123")
            user2, _ = AuthService.register_user("user2", "test2@example.com", "password123")

            success, error = AuthService.update_user(user2.id, email="test1@example.com")

            assert not success
            assert "Email already registered" in error


class TestUserDeletion:
    """Tests for user deletion."""

    def test_delete_user_success(self, app):
        """Test successful user deletion."""
        with app.app_context():
            user, _ = AuthService.register_user("testuser", "test@example.com", "password123")
            user_id = user.id

            success, error = AuthService.delete_user(user_id)

            assert success
            assert error is None

            # Verify user is deleted
            deleted_user = User.query.get(user_id)
            assert deleted_user is None

    def test_delete_nonexistent_user(self, app):
        """Test deletion fails for nonexistent user."""
        with app.app_context():
            success, error = AuthService.delete_user(9999)

            assert not success
            assert "User not found" in error

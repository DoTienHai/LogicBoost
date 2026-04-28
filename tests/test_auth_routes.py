"""Tests for authentication routes."""
import pytest
from flask import url_for
from app.models import User, db


class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_register_page_get(self, client):
        """Test register page loads with GET."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data or b"Create Account" in response.data

    def test_register_user_success_post(self, client, app):
        """Test successful user registration via POST returns JSON with 201."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
                "first_name": "John",
                "last_name": "Doe",
            },
        )

        # Should return JSON with 201 Created
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "message" in data
        assert "redirect" in data
        assert "/auth/login" in data["redirect"]

        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username="newuser").first()
            assert user is not None
            assert user.email == "new@example.com"
            assert user.first_name == "John"
            assert user.last_name == "Doe"

    def test_register_duplicate_username_post(self, client, app):
        """Test registration fails with duplicate username returns JSON 409."""
        # Create existing user
        with app.app_context():
            user = User(username="existing", email="existing@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Try to register with duplicate username
        response = client.post(
            "/auth/register",
            data={
                "username": "existing",
                "email": "new@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "code" in data
        assert data["code"] == "USERNAME_EXISTS"
        assert "already exists" in data["error"].lower()

    def test_register_duplicate_email_post(self, client, app):
        """Test registration fails with duplicate email returns JSON 409."""
        # Create existing user
        with app.app_context():
            user = User(username="existing", email="existing@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Try to register with duplicate email
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "existing@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 409
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "code" in data
        assert data["code"] == "EMAIL_EXISTS"
        assert "already registered" in data["error"].lower()

    def test_register_short_password_post(self, client):
        """Test registration fails with short password returns JSON 400."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "short",  # Less than 6 characters
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "code" in data
        assert data["code"] == "PASSWORD_TOO_SHORT"
        assert "at least 6" in data["error"].lower()

    def test_register_invalid_email_post(self, client):
        """Test registration fails with invalid email returns JSON 400."""
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "invalid-email",  # Missing @
                "password": "password123",
            },
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "code" in data
        assert data["code"] == "INVALID_EMAIL"
        assert "email" in data["error"].lower()

    def test_register_already_logged_in_post(self, client, app):
        """Test registration fails when already logged in returns JSON 403."""
        # Create and login a user
        with app.app_context():
            user = User(username="existing", email="existing@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login
        client.post(
            "/auth/login",
            data={"username": "existing", "password": "password123"},
        )

        # Try to register while logged in
        response = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
        assert "code" in data
        assert data["code"] == "ALREADY_LOGGED_IN"

    def test_login_page_get(self, client):
        """Test login page loads."""
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_login_success(self, client, app):
        """Test successful login."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        # Should be logged in and redirected to home
        assert b"logout" in response.data.lower() or b"Logout" in response.data

    def test_login_wrong_password(self, client, app):
        """Test login fails with wrong password."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "wrongpassword"},
            follow_redirects=True,
        )

        assert b"Invalid" in response.data or b"invalid" in response.data.lower()

    def test_logout(self, client, app):
        """Test logout."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login first
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        # Logout
        response = client.get("/auth/logout", follow_redirects=True)

        assert response.status_code == 200
        # Should see login link after logout
        assert b"login" in response.data.lower() or b"Log in" in response.data

    def test_profile_requires_login(self, client):
        """Test profile page requires login."""
        response = client.get("/auth/profile")
        # Should redirect to login
        assert response.status_code == 302 or response.status_code == 401

    def test_profile_page_get(self, client, app):
        """Test viewing profile page."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com", first_name="John")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        response = client.get("/auth/profile")
        assert response.status_code == 200
        assert b"John" in response.data or b"profile" in response.data.lower()

    def test_profile_update(self, client, app):
        """Test updating profile."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        # Update profile
        response = client.post(
            "/auth/profile",
            data={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        with app.app_context():
            user = User.query.filter_by(username="testuser").first()
            assert user.first_name == "Jane"
            assert user.last_name == "Smith"
            assert user.email == "jane@example.com"

    def test_change_password_page(self, client, app):
        """Test change password page loads."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        response = client.get("/auth/change-password")
        assert response.status_code == 200

    def test_change_password_success(self, client, app):
        """Test successful password change."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        # Change password
        response = client.post(
            "/auth/change-password",
            data={
                "old_password": "password123",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200

        # Verify new password works
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "newpassword123"},
        )
        assert response.status_code == 302 or b"logout" in response.data.lower()

    def test_change_password_mismatch(self, client, app):
        """Test password change fails when passwords don't match."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        response = client.post(
            "/auth/change-password",
            data={
                "old_password": "password123",
                "new_password": "newpassword123",
                "confirm_password": "differentpassword",
            },
            follow_redirects=True,
        )

        assert b"do not match" in response.data or b"not match" in response.data.lower()


class TestAdminRoutes:
    """Tests for admin user management routes."""

    def test_list_users_requires_permission(self, client, app):
        """Test list users requires view_users permission."""
        with app.app_context():
            # Create regular user (only has view_questions)
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

        # Login as regular user
        client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password123"},
        )

        # Try to access users list
        response = client.get("/admin/users")
        # Should be forbidden
        assert response.status_code == 403

    def test_list_users_with_permission(self, client, app):
        """Test listing users with proper permission."""
        with app.app_context():
            # Login as admin
            admin = User.query.filter_by(username="admin").first()
            user_login = User(username="testuser", email="test@example.com")
            user_login.set_password("password123")
            db.session.add(user_login)
            db.session.commit()

        # Login as admin
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"},
        )

        response = client.get("/admin/users")
        # Admin should have access
        assert response.status_code == 200 or response.status_code == 302

    def test_view_user_detail(self, client, app):
        """Test viewing user detail."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Login as admin
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"},
        )

        response = client.get(f"/admin/users/{user_id}")
        assert response.status_code == 200
        assert b"testuser" in response.data or b"test@example.com" in response.data

    def test_edit_user(self, client, app):
        """Test editing user."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Login as admin
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"},
        )

        response = client.post(
            f"/admin/users/{user_id}/edit",
            data={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@example.com",
                "is_active": "on",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        with app.app_context():
            user = User.query.get(user_id)
            assert user.first_name == "Jane"
            assert user.email == "jane@example.com"

    def test_assign_role(self, client, app):
        """Test assigning role to user."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

            # Get admin role
            from app.models import Role

            admin_role = Role.query.filter_by(name="admin").first()

        # Login as admin
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"},
        )

        response = client.post(
            f"/admin/users/{user_id}/assign-role",
            data={"role_id": admin_role.id},
            follow_redirects=True,
        )

        assert response.status_code == 200
        with app.app_context():
            user = User.query.get(user_id)
            assert user.has_role("admin")

    def test_remove_role(self, client, app):
        """Test removing role from user."""
        with app.app_context():
            from app.models import Role

            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            admin_role = Role.query.filter_by(name="admin").first()
            user.roles.append(admin_role)
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Login as admin
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"},
        )

        with app.app_context():
            admin_role = Role.query.filter_by(name="admin").first()

        response = client.post(
            f"/admin/users/{user_id}/remove-role/{admin_role.id}",
            follow_redirects=True,
        )

        assert response.status_code == 200
        with app.app_context():
            user = User.query.get(user_id)
            assert not user.has_role("admin")

    def test_delete_user_not_only_admin(self, client, app):
        """Test deleting user when not the only admin."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        # Login as admin
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"},
        )

        response = client.post(
            f"/admin/users/{user_id}/delete",
            follow_redirects=True,
        )

        assert response.status_code == 200
        with app.app_context():
            assert User.query.get(user_id) is None

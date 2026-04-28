"""Tests for admin user management routes."""
import pytest
from app.models import User, Role, db


def create_admin_and_login(client, app):
    """Helper: create an admin user, assign admin role, and log in."""
    with app.app_context():
        # Ensure admin role exists
        role = Role.query.filter_by(name="admin").first()
        if not role:
            role = Role(name="admin", display_name="Administrator")
            db.session.add(role)
            db.session.commit()

        user = User.query.filter_by(username="admin_test").first()
        if not user:
            user = User(username="admin_test", email="admin_test@example.com")
            user.set_password("admin123")
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()

    client.post(
        "/auth/login",
        data={"username": "admin_test", "password": "admin123"},
        follow_redirects=True,
    )


class TestAdminListUsers:
    """Tests for listing users."""

    def test_admin_list_users_get(self, client, app):
        """Test listing all users page (GET)."""
        create_admin_and_login(client, app)
        response = client.get("/admin/users")
        assert response.status_code == 200
        assert b"User Management" in response.data or b"user" in response.data.lower()

    def test_admin_list_users_contains_admin_user(self, client, app):
        """Test that admin user appears in users list."""
        create_admin_and_login(client, app)
        response = client.get("/admin/users")
        assert response.status_code == 200
        assert b"admin_test" in response.data


class TestAdminViewUser:
    """Tests for viewing user details."""

    def test_admin_view_user_get(self, client, app):
        """Test viewing user details page (GET)."""
        create_admin_and_login(client, app)
        
        # Get admin user ID
        with app.app_context():
            admin = User.query.filter_by(username="admin_test").first()
            user_id = admin.id
        
        response = client.get(f"/admin/users/{user_id}")
        assert response.status_code == 200
        assert b"admin_test" in response.data

    def test_admin_view_nonexistent_user(self, client, app):
        """Test viewing non-existent user returns 404."""
        create_admin_and_login(client, app)
        response = client.get("/admin/users/9999")
        assert response.status_code == 404


class TestAdminCreateUser:
    """Tests for creating users."""

    def test_admin_create_user_get(self, client, app):
        """Test create user form page (GET)."""
        create_admin_and_login(client, app)
        response = client.get("/admin/users/create")
        assert response.status_code == 200
        assert b"Create" in response.data or b"create" in response.data.lower()

    def test_admin_create_user_post_valid(self, client, app):
        """Test creating a user with valid data (POST)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "New",
            "last_name": "User",
        }
        
        response = client.post("/admin/users/create", data=form_data, follow_redirects=False)
        
        # Should redirect to users list
        assert response.status_code == 302
        assert "/admin/users" in response.location
        
        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username="newuser").first()
            assert user is not None
            assert user.email == "newuser@example.com"
            assert user.first_name == "New"
            assert user.last_name == "User"

    def test_admin_create_user_post_missing_username(self, client, app):
        """Test creating user with missing username (validation)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        
        response = client.post("/admin/users/create", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Username" in response.data or b"required" in response.data

    def test_admin_create_user_post_missing_email(self, client, app):
        """Test creating user with missing email (validation)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "username": "newuser",
            "password": "password123",
            "confirm_password": "password123",
        }
        
        response = client.post("/admin/users/create", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Email" in response.data or b"required" in response.data

    def test_admin_create_user_post_missing_password(self, client, app):
        """Test creating user with missing password (validation)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "confirm_password": "password123",
        }
        
        response = client.post("/admin/users/create", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Password" in response.data or b"required" in response.data

    def test_admin_create_user_post_password_mismatch(self, client, app):
        """Test creating user with mismatched passwords (validation)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password456",
        }
        
        response = client.post("/admin/users/create", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"do not match" in response.data or b"mismatch" in response.data.lower()

    def test_admin_create_user_post_password_too_short(self, client, app):
        """Test creating user with short password (validation)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "pass",
            "confirm_password": "pass",
        }
        
        response = client.post("/admin/users/create", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"at least 6 characters" in response.data or b"too short" in response.data.lower()

    def test_admin_create_user_post_duplicate_username(self, client, app):
        """Test creating user with duplicate username (validation)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "username": "admin_test",  # Already exists
            "email": "different@example.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        
        response = client.post("/admin/users/create", data=form_data)
        
        # Should return error status
        assert response.status_code >= 400
        assert b"exists" in response.data or b"already" in response.data.lower()


class TestAdminEditUser:
    """Tests for editing users."""

    def test_admin_edit_user_get(self, client, app):
        """Test edit user form page (GET)."""
        create_admin_and_login(client, app)
        
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        response = client.get(f"/admin/users/{user_id}/edit")
        assert response.status_code == 200
        assert b"testuser" in response.data

    def test_admin_edit_user_post_valid(self, client, app):
        """Test editing a user with valid data (POST)."""
        create_admin_and_login(client, app)
        
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@example.com",
            "is_active": "on",
        }
        
        response = client.post(f"/admin/users/{user_id}/edit", data=form_data, follow_redirects=False)
        
        # Should redirect to user detail page
        assert response.status_code == 302
        
        # Verify user was updated
        with app.app_context():
            updated_user = db.session.get(User, user_id)
            assert updated_user.first_name == "Updated"
            assert updated_user.last_name == "User"
            assert updated_user.email == "updated@example.com"

    def test_admin_edit_user_post_missing_email(self, client, app):
        """Test editing user with missing email (validation)."""
        create_admin_and_login(client, app)
        
        # Create a test user
        with app.app_context():
            user = User(username="testuser", email="testuser@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "",  # Missing email
        }
        
        response = client.post(f"/admin/users/{user_id}/edit", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Email" in response.data or b"required" in response.data

    def test_admin_edit_user_post_duplicate_email(self, client, app):
        """Test editing user with duplicate email (validation)."""
        create_admin_and_login(client, app)
        
        # Create two test users
        with app.app_context():
            user1 = User(username="user1", email="user1@example.com")
            user1.set_password("password123")
            user2 = User(username="user2", email="user2@example.com")
            user2.set_password("password123")
            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()
            user1_id = user1.id
        
        # Try to change user2 email to user1's email
        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "email": "user1@example.com",  # user1's email
        }
        
        response = client.post(f"/admin/users/{user1_id}/edit", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Email" in response.data or b"already" in response.data.lower()


class TestAdminDeleteUser:
    """Tests for deleting users."""

    def test_admin_delete_user(self, client, app):
        """Test deleting a user."""
        create_admin_and_login(client, app)
        
        # Create a test user
        with app.app_context():
            user = User(username="userdelete", email="userdelete@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        
        # Verify user exists
        with app.app_context():
            assert db.session.get(User, user_id) is not None
        
        # Delete the user
        response = client.post(f"/admin/users/{user_id}/delete", follow_redirects=False)
        
        # Should redirect to users list
        assert response.status_code == 302
        
        # Verify user was deleted
        with app.app_context():
            assert db.session.get(User, user_id) is None

    def test_admin_delete_only_admin_user(self, client, app):
        """Test that the last admin user cannot be deleted."""
        create_admin_and_login(client, app)
        
        # Get the admin user
        with app.app_context():
            admin_user = User.query.filter_by(username="admin_test").first()
            user_id = admin_user.id
        
        # Try to delete the admin user
        response = client.post(f"/admin/users/{user_id}/delete", follow_redirects=False)
        
        # Should redirect (with error)
        assert response.status_code == 302
        
        # Verify user was NOT deleted
        with app.app_context():
            assert db.session.get(User, user_id) is not None

    def test_admin_delete_nonexistent_user(self, client, app):
        """Test deleting non-existent user returns 404."""
        create_admin_and_login(client, app)
        response = client.post("/admin/users/9999/delete", follow_redirects=False)
        
        # Should return 404
        assert response.status_code == 404


class TestAdminAssignRole:
    """Tests for assigning roles to users."""

    def test_admin_assign_role_to_user(self, client, app):
        """Test assigning a role to a user."""
        create_admin_and_login(client, app)
        
        # Create a test user and get content_creator role
        with app.app_context():
            user = User(username="assigntest", email="assigntest@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Ensure content_creator role exists
            role = Role.query.filter_by(name="content_creator").first()
            if not role:
                role = Role(name="content_creator", display_name="Content Creator")
                db.session.add(role)
                db.session.commit()
            role_id = role.id
        
        # Assign role
        form_data = {"role_id": role_id}
        response = client.post(f"/admin/users/{user_id}/assign-role", data=form_data, follow_redirects=False)
        
        # Should redirect to user detail page
        assert response.status_code == 302
        
        # Verify role was assigned
        with app.app_context():
            updated_user = db.session.get(User, user_id)
            assert len(updated_user.roles) > 0
            assert any(r.name == "content_creator" for r in updated_user.roles)


class TestAdminRemoveRole:
    """Tests for removing roles from users."""

    def test_admin_remove_role_from_user(self, client, app):
        """Test removing a role from a user."""
        create_admin_and_login(client, app)
        
        # Create a test user with a role
        with app.app_context():
            # Ensure content_creator role exists
            role = Role.query.filter_by(name="content_creator").first()
            if not role:
                role = Role(name="content_creator", display_name="Content Creator")
                db.session.add(role)
                db.session.commit()
            
            user = User(username="removetest", email="removetest@example.com")
            user.set_password("password123")
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            role_id = role.id
        
        # Remove the role
        response = client.post(f"/admin/users/{user_id}/remove-role/{role_id}", follow_redirects=False)
        
        # Should redirect to user detail page
        assert response.status_code == 302
        
        # Verify role was removed
        with app.app_context():
            updated_user = db.session.get(User, user_id)
            assert not any(r.name == "content_creator" for r in updated_user.roles)

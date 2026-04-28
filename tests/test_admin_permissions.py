"""Tests for FE/BE permission enforcement on admin routes.

Verifies that regular users (without admin permissions) cannot access
admin URLs and that the navbar admin link is hidden from them.
"""
from app.models import User, Role, db


def create_regular_user_and_login(client, app):
    """Helper: create a regular user (with 'user' role only) and log in."""
    with app.app_context():
        # Ensure 'user' role exists
        role = Role.query.filter_by(name="user").first()
        if not role:
            role = Role(name="user", display_name="User")
            db.session.add(role)
            db.session.commit()

        user = User.query.filter_by(username="regular_test").first()
        if not user:
            user = User(username="regular_test", email="regular_test@example.com")
            user.set_password("regular123")
            user.roles.append(role)
            db.session.add(user)
            db.session.commit()

    client.post(
        "/auth/login",
        data={"username": "regular_test", "password": "regular123"},
        follow_redirects=True,
    )


class TestRegularUserBlockedFromAdminRoutes:
    """Regular users (no admin permissions) should get 403 on admin URLs."""

    def test_regular_user_blocked_from_admin_dashboard(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.get("/admin/")
        assert response.status_code == 403

    def test_regular_user_blocked_from_add_question(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.get("/admin/question/new")
        assert response.status_code == 403

    def test_regular_user_blocked_from_import_excel(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.get("/admin/import")
        assert response.status_code == 403

    def test_regular_user_blocked_from_users_list(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.get("/admin/users")
        assert response.status_code == 403

    def test_regular_user_blocked_from_create_user(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.get("/admin/users/create")
        assert response.status_code == 403

    def test_regular_user_blocked_from_delete_user(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.post("/admin/users/1/delete")
        assert response.status_code == 403


class TestAnonymousUserRedirectedToLogin:
    """Unauthenticated users should be redirected to login."""

    def test_anonymous_redirected_from_admin_dashboard(self, client):
        response = client.get("/admin/", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.location

    def test_anonymous_redirected_from_users_list(self, client):
        response = client.get("/admin/users", follow_redirects=False)
        assert response.status_code == 302
        assert "/auth/login" in response.location


class TestNavbarHidesAdminLink:
    """The 'Admin' link in the navbar should not appear for regular users."""

    def test_admin_link_hidden_for_regular_user(self, client, app):
        create_regular_user_and_login(client, app)
        response = client.get("/")
        assert response.status_code == 200
        # Admin link uses the dashboard endpoint
        assert b'href="/admin/"' not in response.data
        assert "⚙️ Admin".encode("utf-8") not in response.data

    def test_admin_link_hidden_for_anonymous_user(self, client):
        # Anonymous users get redirected to login from /; follow the redirect
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert b'href="/admin/"' not in response.data


class TestAdminUserHasFullAccess:
    """Sanity check: admin user can access admin pages."""

    def test_admin_user_can_access_dashboard(self, client, app):
        # Reuse helper from test_admin_users
        from test_admin_users import create_admin_and_login

        create_admin_and_login(client, app)
        response = client.get("/admin/")
        assert response.status_code == 200

    def test_admin_user_can_access_users_list(self, client, app):
        from test_admin_users import create_admin_and_login

        create_admin_and_login(client, app)
        response = client.get("/admin/users")
        assert response.status_code == 200

    def test_admin_navbar_shows_admin_link(self, client, app):
        from test_admin_users import create_admin_and_login

        create_admin_and_login(client, app)
        response = client.get("/")
        assert response.status_code == 200
        assert b'href="/admin/"' in response.data

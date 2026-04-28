"""Tests for admin question management routes."""
import pytest
from app.models import Question, db
from app.models.user import User
from app.models.role import Role


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


class TestAdminQuestionsDashboard:
    """Tests for admin questions dashboard."""

    def test_admin_dashboard(self, client, app):
        """Test admin dashboard loads."""
        create_admin_and_login(client, app)
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"Admin Dashboard" in response.data


class TestAdminAddQuestion:
    """Tests for adding questions."""

    def test_admin_add_question_get(self, client, app):
        """Test add question form page (GET)."""
        create_admin_and_login(client, app)
        response = client.get("/admin/question/new")
        assert response.status_code == 200
        assert b"Question" in response.data or b"question" in response.data.lower()

    def test_admin_add_question_post_valid(self, client, app):
        """Test adding a question with valid data (POST)."""
        create_admin_and_login(client, app)
        
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "daily_challenge",
            "difficulty": "1",
            "option_a": "4",
            "option_b": "5",
        }
        
        response = client.post("/admin/question/new", data=form_data, follow_redirects=False)
        
        # Should redirect to admin dashboard
        assert response.status_code == 302
        assert "/admin/" in response.location
        
        # Verify question was saved to database
        with app.app_context():
            question = Question.query.filter_by(title="Test Question").first()
            assert question is not None
            assert question.question == "What is 2+2?"
            assert question.answer == "a"
            assert question.mode == "daily_challenge"

    def test_admin_add_question_post_missing_title(self, client, app):
        """Test adding question with missing title (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "daily_challenge",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Title" in response.data or b"required" in response.data

    def test_admin_add_question_post_missing_question(self, client, app):
        """Test adding question with missing question body (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "daily_challenge",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Question" in response.data or b"required" in response.data

    def test_admin_add_question_post_missing_explanation(self, client, app):
        """Test adding question with missing explanation (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "answer": "a",
            "mode": "daily_challenge",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Explanation" in response.data or b"required" in response.data

    def test_admin_add_question_post_missing_answer(self, client, app):
        """Test adding question with missing answer (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "mode": "daily_challenge",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Answer" in response.data or b"required" in response.data

    def test_admin_add_question_post_missing_mode(self, client, app):
        """Test adding question with missing mode (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Mode" in response.data or b"required" in response.data

    def test_admin_add_question_post_invalid_mode(self, client, app):
        """Test adding question with invalid mode (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "invalid_mode",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Invalid mode" in response.data or b"mode" in response.data.lower()

    def test_admin_add_question_post_missing_difficulty(self, client, app):
        """Test adding question with missing difficulty (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "daily_challenge",
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Difficulty" in response.data or b"required" in response.data

    def test_admin_add_question_post_invalid_difficulty(self, client, app):
        """Test adding question with invalid difficulty (validation)."""
        create_admin_and_login(client, app)
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "daily_challenge",
            "difficulty": "6",  # Invalid: must be 1-5
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Difficulty" in response.data or b"1-5" in response.data


class TestAdminEditQuestion:
    """Tests for editing questions."""

    def test_admin_edit_question_get(self, client, app):
        """Test edit question form page (GET)."""
        create_admin_and_login(client, app)
        
        # Create a question in the database
        with app.app_context():
            question = Question(
                title="Original Question",
                question="What is 2+2?",
                explanation="The answer is 4",
                answer="a",
                mode="daily_challenge",
                difficulty=1,
                option_a="4",
                option_b="5",
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        # Test GET edit form
        response = client.get(f"/admin/question/{question_id}/edit")
        assert response.status_code == 200
        assert b"Original Question" in response.data

    def test_admin_edit_question_post_valid(self, client, app):
        """Test editing a question with valid data (POST)."""
        create_admin_and_login(client, app)
        
        # Create a question
        with app.app_context():
            question = Question(
                title="Original Question",
                question="What is 2+2?",
                explanation="The answer is 4",
                answer="a",
                mode="daily_challenge",
                difficulty=1,
                option_a="4",
                option_b="5",
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        # Update the question
        form_data = {
            "title": "Updated Question",
            "question": "What is 3+3?",
            "explanation": "The answer is 6",
            "answer": "b",
            "mode": "mini_game",
            "difficulty": "2",
            "option_a": "5",
            "option_b": "6",
        }
        
        response = client.post(f"/admin/question/{question_id}/edit", data=form_data, follow_redirects=False)
        
        # Should redirect to admin dashboard
        assert response.status_code == 302
        
        # Verify question was updated
        with app.app_context():
            updated_q = db.session.get(Question, question_id)
            assert updated_q.title == "Updated Question"
            assert updated_q.question == "What is 3+3?"
            assert updated_q.answer == "b"
            assert updated_q.mode == "mini_game"

    def test_admin_edit_question_post_invalid(self, client, app):
        """Test editing question with invalid data (validation)."""
        create_admin_and_login(client, app)
        
        # Create a question
        with app.app_context():
            question = Question(
                title="Original Question",
                question="What is 2+2?",
                explanation="The answer is 4",
                answer="a",
                mode="daily_challenge",
                difficulty=1,
                option_a="4",
                option_b="5",
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        # Try to update with missing required field
        form_data = {
            "question": "What is 3+3?",
            "explanation": "The answer is 6",
            "answer": "b",
            "mode": "mini_game",
        }
        
        response = client.post(f"/admin/question/{question_id}/edit", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Title" in response.data or b"required" in response.data

    def test_admin_edit_nonexistent_question(self, client, app):
        """Test editing a non-existent question."""
        create_admin_and_login(client, app)
        response = client.get("/admin/question/9999/edit")
        
        # Should return 404
        assert response.status_code == 404


class TestAdminDeleteQuestion:
    """Tests for deleting questions."""

    def test_admin_delete_question(self, client, app):
        """Test deleting a question."""
        create_admin_and_login(client, app)
        
        # Create a question
        with app.app_context():
            question = Question(
                title="Question to Delete",
                question="What is 2+2?",
                explanation="The answer is 4",
                answer="a",
                mode="daily_challenge",
                difficulty=1,
                option_a="4",
                option_b="5",
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        # Verify question exists
        with app.app_context():
            assert db.session.get(Question, question_id) is not None
        
        # Delete the question
        response = client.post(f"/admin/question/{question_id}/delete", follow_redirects=False)
        
        # Should redirect to admin dashboard
        assert response.status_code == 302
        
        # Verify question was deleted
        with app.app_context():
            assert db.session.get(Question, question_id) is None

    def test_admin_delete_nonexistent_question(self, client, app):
        """Test deleting a non-existent question."""
        create_admin_and_login(client, app)
        response = client.post("/admin/question/9999/delete", follow_redirects=False)
        
        # Should return 404
        assert response.status_code == 404


class TestAdminImportExcel:
    """Tests for Excel import functionality."""

    def test_admin_import_page_get(self, client, app):
        """Test import page loads."""
        create_admin_and_login(client, app)
        response = client.get("/admin/import")
        assert response.status_code == 200
        assert b"Import" in response.data or b"import" in response.data.lower()

    def test_admin_download_template(self, client, app):
        """Test downloading Excel template."""
        create_admin_and_login(client, app)
        response = client.get("/admin/import/template")
        # Should return file download or redirect depending on template existence
        assert response.status_code in [200, 302]

"""Integration tests for all routes."""
import pytest
from app.models import Question, db


class TestMainRoutes:
    """Tests for main routes."""

    def test_home_page(self, client):
        """Test home page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"LogicBoost" in response.data
        assert b"Daily Challenge" in response.data


class TestDailyChallengeRoutes:
    """Tests for daily challenge routes."""

    def test_daily_challenge_index(self, client):
        """Test daily challenge lobby."""
        response = client.get("/daily-challenge/")
        assert response.status_code == 200
        assert b"Daily Challenge" in response.data

    def test_daily_challenge_start(self, client):
        """Test starting daily challenge."""
        # Mock questions in the database
        from app.models import Question
        q = Question(
            title="Test Q",
            question="What is 1+1?",
            explanation="2",
            answer="2",
            mode="daily_challenge",
            difficulty=1,
        )
        db.session.add(q)
        db.session.commit()
        
        # Add 5 test questions
        for i in range(5):
            q = Question(
                title=f"Test Q{i}",
                question=f"Question {i}",
                explanation=f"Answer {i}",
                answer=f"{i}",
                mode="daily_challenge",
                difficulty=1,
            )
            db.session.add(q)
        db.session.commit()
        
        response = client.get("/daily-challenge/start", follow_redirects=False)
        # Should redirect to first question
        assert response.status_code == 302
        assert b"question" in response.data.lower()

    def test_daily_challenge_summary(self, client):
        """Test daily challenge summary with session data."""
        with client:
            # Simulate a completed daily challenge with 5 answers
            with client.session_transaction() as sess:
                sess["daily_challenge_answers"] = [
                    {"question_id": 1, "answer": "a", "is_correct": True, "correct_answer": "a"},
                    {"question_id": 2, "answer": "b", "is_correct": True, "correct_answer": "b"},
                    {"question_id": 3, "answer": "c", "is_correct": False, "correct_answer": "x"},
                    {"question_id": 4, "answer": "d", "is_correct": True, "correct_answer": "d"},
                    {"question_id": 5, "answer": "text", "is_correct": False, "correct_answer": "correct"},
                ]
            
            response = client.get("/daily-challenge/summary")
            assert response.status_code == 200
            assert b"Complete" in response.data or b"Accuracy" in response.data


class TestMiniGameRoutes:
    """Tests for mini game routes."""

    def test_mini_game_index(self, client):
        """Test mini game lobby."""
        response = client.get("/mini-game/")
        assert response.status_code == 200
        assert b"Mini Game" in response.data or b"mini" in response.data.lower()

    def test_mini_game_play(self, client):
        """Test mini game play page."""
        response = client.get("/mini-game/play")
        assert response.status_code == 200
        assert b"timer" in response.data.lower()

    def test_mini_game_result(self, client):
        """Test mini game result."""
        response = client.get("/mini-game/result")
        assert response.status_code == 200
        assert b"Result" in response.data


class TestRealWorldRoutes:
    """Tests for real-world routes."""

    def test_real_world_index(self, client):
        """Test real-world problems page."""
        response = client.get("/real-world/")
        assert response.status_code == 200
        assert b"Real-world" in response.data or b"real-world" in response.data.lower()

    def test_real_world_category_finance(self, client):
        """Test finance category."""
        response = client.get("/real-world/finance")
        assert response.status_code == 200

    def test_real_world_category_career(self, client):
        """Test career category."""
        response = client.get("/real-world/career")
        assert response.status_code == 200

    def test_real_world_category_business(self, client):
        """Test business category."""
        response = client.get("/real-world/business")
        assert response.status_code == 200


class TestAdminRoutes:
    """Tests for admin routes."""

    def test_admin_dashboard(self, client):
        """Test admin dashboard."""
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"Admin" in response.data

    def test_admin_add_question_get(self, client):
        """Test add question form page (GET)."""
        response = client.get("/admin/question/new")
        assert response.status_code == 200
        assert b"Question" in response.data or b"question" in response.data.lower()

    def test_admin_add_question_post_valid(self, client, app):
        """Test adding a question with valid data (POST)."""
        from app.models import Question
        
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

    def test_admin_add_question_post_missing_title(self, client):
        """Test adding question with missing title (validation)."""
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

    def test_admin_add_question_post_missing_mode(self, client):
        """Test adding question with missing mode (validation)."""
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

    def test_admin_add_question_post_invalid_mode(self, client):
        """Test adding question with invalid mode (validation)."""
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

    def test_admin_add_question_post_invalid_difficulty(self, client):
        """Test adding question with invalid difficulty (validation)."""
        form_data = {
            "title": "Test Question",
            "question": "What is 2+2?",
            "explanation": "The answer is 4",
            "answer": "a",
            "mode": "daily_challenge",
            "difficulty": "5",  # Invalid: must be 1-3
        }
        
        response = client.post("/admin/question/new", data=form_data)
        
        # Should return 400 with errors
        assert response.status_code == 400
        assert b"Difficulty" in response.data or b"1, 2, or 3" in response.data

    def test_admin_import_page(self, client):
        """Test import page."""
        response = client.get("/admin/import")
        assert response.status_code == 200
        assert b"Import" in response.data

    def test_admin_edit_question_get(self, client, app):
        """Test edit question form page (GET)."""
        from app.models import Question
        
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
        from app.models import Question, db
        
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
            updated_q = Question.query.get(question_id)
            assert updated_q.title == "Updated Question"
            assert updated_q.question == "What is 3+3?"
            assert updated_q.answer == "b"
            assert updated_q.mode == "mini_game"

    def test_admin_edit_question_post_invalid(self, client, app):
        """Test editing question with invalid data (validation)."""
        from app.models import Question, db
        
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

    def test_admin_delete_question(self, client, app):
        """Test deleting a question."""
        from app.models import Question, db
        
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
            assert Question.query.get(question_id) is not None
        
        # Delete the question
        response = client.post(f"/admin/question/{question_id}/delete", follow_redirects=False)
        
        # Should redirect to admin dashboard
        assert response.status_code == 302
        
        # Verify question was deleted
        with app.app_context():
            assert Question.query.get(question_id) is None

    def test_admin_delete_nonexistent_question(self, client):
        """Test deleting a non-existent question."""
        response = client.post("/admin/question/9999/delete", follow_redirects=False)
        
        # Should return 404
        assert response.status_code == 404


class TestPageNavigation:
    """Tests for page navigation and buttons."""

    def test_home_has_navigation_buttons(self, client):
        """Test home page has navigation buttons."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Daily Challenge" in response.data
        assert b"Mini Game" in response.data
        assert b"Real-world" in response.data

    def test_navbar_visible_on_all_pages(self, client):
        """Test navbar is visible on all pages."""
        pages = [
            "/",
            "/daily-challenge/",
            "/mini-game/",
            "/real-world/",
            "/admin/",
        ]
        for page in pages:
            response = client.get(page)
            assert response.status_code == 200
            assert b"LogicBoost" in response.data  # Navbar has LogicBoost brand

    def test_back_navigation_buttons(self, client):
        """Test back navigation buttons exist."""
        # Daily challenge has back button
        response = client.get("/daily-challenge/")
        assert response.status_code == 200
        assert b"href" in response.data  # Has links

        # Admin has back button
        response = client.get("/admin/")
        assert response.status_code == 200
        assert b"href" in response.data  # Has links


class TestPageContent:
    """Tests for page content."""

    def test_pages_contain_placeholder_text(self, client):
        """Test pages contain placeholder content."""
        pages = {
            "/daily-challenge/": b"Daily Challenge",
            "/mini-game/": b"mini",
            "/real-world/": b"real",
            "/admin/": b"Admin",
        }

        for page, expected_text in pages.items():
            response = client.get(page)
            assert response.status_code == 200
            assert expected_text.lower() in response.data.lower()

    def test_forms_have_buttons(self, client):
        """Test forms have submit buttons."""
        response = client.get("/admin/question/new")
        assert response.status_code == 200
        assert b"button" in response.data.lower()

    def test_home_feature_cards_exist(self, client):
        """Test home page has feature cards."""
        response = client.get("/")
        assert response.status_code == 200
        # Each feature should be linked
        assert b"Daily Challenge" in response.data
        assert b"Quick Mini Game" in response.data or b"Mini Game" in response.data.lower()
        assert b"Real-world" in response.data or b"real" in response.data.lower()

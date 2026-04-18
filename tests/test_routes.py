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

    def test_admin_add_question(self, client):
        """Test add question page."""
        response = client.get("/admin/question/new")
        assert response.status_code == 200
        assert b"Question" in response.data or b"question" in response.data.lower()

    def test_admin_import_page(self, client):
        """Test import page."""
        response = client.get("/admin/import")
        assert response.status_code == 200
        assert b"Import" in response.data


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

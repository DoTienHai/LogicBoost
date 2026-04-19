"""Tests for Mini Game Service."""
import pytest
from app.services import mini_game_service
from app.models import Question, UserAnswer, db
from app.models.user import User


def make_user(db_session_or_app, username="mini_test_user", email="mini@example.com"):
    """Helper: create and commit a User, return id."""
    user = User(username=username, email=email)
    user.set_password("password123")
    db_session_or_app.add(user)
    db_session_or_app.commit()
    return user.id


class TestMiniGameService:
    """Test suite for mini_game_service module."""
    
    def test_get_random_question_returns_question(self, app, sample_mini_game_questions):
        """Test that get_random_question returns a valid question."""
        with app.app_context():
            question = mini_game_service.get_random_question()
            
            assert question is not None
            assert question.mode == "mini_game"
    
    def test_get_random_question_excludes_answered(self, app, sample_mini_game_questions):
        """Test that get_random_question excludes answered questions."""
        with app.app_context():
            # Get all question IDs
            all_questions = Question.query.filter_by(mode="mini_game").all()
            all_ids = [q.id for q in all_questions]
            
            # Mark all but one as answered
            answered_ids = all_ids[:-1]
            
            question = mini_game_service.get_random_question(answered_ids)
            
            assert question is not None
            assert question.id == all_ids[-1]
    
    def test_get_random_question_resets_when_all_answered(self, app, sample_mini_game_questions):
        """Test that get_random_question resets when all questions are answered."""
        with app.app_context():
            # Get all question IDs
            all_questions = Question.query.filter_by(mode="mini_game").all()
            all_ids = [q.id for q in all_questions]
            
            # Mark all as answered
            question = mini_game_service.get_random_question(all_ids)
            
            # Should still return a question (reset)
            assert question is not None
            assert question.mode == "mini_game"
    
    def test_get_random_question_returns_none_when_no_questions(self, app, db_session):
        """Test that get_random_question returns None when no questions available."""
        with app.app_context():
            # Clear all mini_game questions
            Question.query.filter_by(mode="mini_game").delete()
            db_session.commit()
            
            question = mini_game_service.get_random_question()
            
            assert question is None
    
    def test_get_random_question_avoids_last_question(self, app, sample_mini_game_questions):
        """Test that get_random_question avoids returning the last question shown."""
        with app.app_context():
            # Get first question and remember it
            q1 = mini_game_service.get_random_question()
            q1_id = q1.id
            
            # Get all question IDs
            all_ids = [q.id for q in Question.query.filter_by(mode="mini_game").all()]
            
            # Skip if only 1 question total
            if len(all_ids) <= 1:
                pytest.skip("Need at least 2 questions for this test")
            
            # Call again with last_question_id set to q1
            # Try multiple times to account for randomness
            different_found = False
            for _ in range(10):
                q2 = mini_game_service.get_random_question(last_question_id=q1_id)
                if q2 and q2.id != q1_id:
                    different_found = True
                    break
            
            # Should get a different question (or None if only 1 available, but we skipped that)
            assert different_found or q2 is None
    
    def test_check_answer_correct_multiple_choice(self, app, sample_mini_game_questions):
        """Test check_answer with correct multiple choice answer."""
        with app.app_context():
            user_id = make_user(db.session)
            question = Question.query.filter(
                Question.mode == "mini_game",
                Question.option_a.isnot(None)
            ).first()
            
            result = mini_game_service.check_answer(
                question.id,
                question.answer,
                time_taken=10,
                user_id=user_id,
            )
            
            assert result["is_correct"] is True
            assert result["correct_answer"] == question.answer
            assert "explanation" not in result
            
            # Check that answer was recorded
            answer_record = UserAnswer.query.filter_by(
                question_id=question.id, user_id=user_id
            ).first()
            
            assert answer_record is not None
            assert answer_record.is_correct is True
            assert answer_record.question_type == "multiple_choice"
    
    def test_check_answer_incorrect_multiple_choice(self, app, sample_mini_game_questions):
        """Test check_answer with incorrect multiple choice answer."""
        with app.app_context():
            user_id = make_user(db.session, "user_wrong", "wrong@example.com")
            question = Question.query.filter(
                Question.mode == "mini_game",
                Question.option_a.isnot(None)
            ).first()
            
            # Find a wrong answer
            wrong_answer = "z" if question.answer != "z" else "y"
            
            result = mini_game_service.check_answer(
                question.id,
                wrong_answer,
                time_taken=15,
                user_id=user_id,
            )
            
            assert result["is_correct"] is False
            assert result["correct_answer"] == question.answer
            assert "explanation" in result
            
            # Check that answer was recorded
            answer_record = UserAnswer.query.filter_by(
                question_id=question.id, user_id=user_id
            ).first()
            
            assert answer_record is not None
            assert answer_record.is_correct is False
    
    def test_check_answer_correct_free_text(self, app, sample_mini_game_questions):
        """Test check_answer with correct free text answer."""
        with app.app_context():
            user_id = make_user(db.session, "user_free", "free@example.com")
            question = Question.query.filter(
                Question.mode == "mini_game",
                Question.option_a.is_(None)
            ).first()
            
            result = mini_game_service.check_answer(
                question.id,
                question.answer,
                time_taken=20,
                user_id=user_id,
            )
            
            assert result["is_correct"] is True
            assert result["correct_answer"] == question.answer
            
            # Check that answer was recorded
            answer_record = UserAnswer.query.filter_by(
                question_id=question.id, user_id=user_id
            ).first()
            
            assert answer_record is not None
            assert answer_record.question_type == "free_text"
    
    def test_check_answer_case_insensitive(self, app, sample_mini_game_questions):
        """Test that check_answer is case insensitive."""
        with app.app_context():
            question = Question.query.filter_by(mode="mini_game").first()
            
            # Test with different case
            answer_upper = question.answer.upper()
            
            result = mini_game_service.check_answer(
                question.id,
                answer_upper,
                time_taken=5,
            )
            
            assert result["is_correct"] is True
    
    def test_check_answer_free_text_normalization(self, app, db_session):
        """Test that free text answers are normalized (remove commas, spaces, periods)."""
        with app.app_context():
            # Create a free text question with numeric answer
            question = Question(
                title="Math Test",
                question="What is 10,000 + 5,000?",
                explanation="Add them together: 15,000",
                answer="15000",
                mode="mini_game",
                difficulty=1
            )
            db_session.add(question)
            db_session.commit()
            
            # Test variations of the answer with different formatting
            test_answers = [
                ("15000", True),           # Exact match
                ("15,000", True),          # With commas
                ("15 000", True),          # With spaces
                ("15.000", True),          # With periods (European notation)
                ("15 , 0 0 0", True),      # Multiple spaces and commas
                ("FIFTEEN THOUSAND", False),  # Text (should not match)
                ("15001", False),          # Wrong number
            ]
            
            for user_answer, should_be_correct in test_answers:
                result = mini_game_service.check_answer(
                    question.id,
                    user_answer,
                    time_taken=10,
                )
                
                assert result["is_correct"] is should_be_correct, \
                    f"Answer '{user_answer}' should be correct={should_be_correct}, but got {result['is_correct']}"
    
    def test_check_answer_nonexistent_question(self, app):
        """Test check_answer with nonexistent question ID."""
        with app.app_context():
            result = mini_game_service.check_answer(
                question_id=99999,
                user_answer="test",
                time_taken=10
            )
            
            assert "error" in result
    
    def test_format_question_data_english(self, app, sample_mini_game_questions):
        """Test format_question_data with English language."""
        with app.app_context():
            question = Question.query.filter_by(mode="mini_game").first()
            
            data = mini_game_service.format_question_data(question, lang="en")
            
            assert data is not None
            assert data["id"] == question.id
            assert data["title"] == question.title
            assert data["question"] == question.question
            assert data["time_limit"] == (question.time_limit or 60)
    
    def test_format_question_data_vietnamese(self, app, sample_mini_game_questions):
        """Test format_question_data with Vietnamese language."""
        with app.app_context():
            # Find question with Vietnamese translation
            question = Question.query.filter(
                Question.mode == "mini_game",
                Question.title_vi.isnot(None)
            ).first()
            
            if question:
                data = mini_game_service.format_question_data(question, lang="vi")
                
                assert data is not None
                assert data["title"] == question.title_vi
                assert data["question"] == question.question_vi
    
    def test_format_question_data_fallback_to_english(self, app, sample_mini_game_questions):
        """Test that format_question_data falls back to English when Vietnamese not available."""
        with app.app_context():
            # Find question without Vietnamese translation
            question = Question.query.filter(
                Question.mode == "mini_game",
                Question.title_vi.is_(None)
            ).first()
            
            if question:
                data = mini_game_service.format_question_data(question, lang="vi")
                
                assert data is not None
                assert data["title"] == question.title
                assert data["question"] == question.question
    
    def test_format_question_data_none_question(self, app):
        """Test format_question_data with None question."""
        with app.app_context():
            data = mini_game_service.format_question_data(None)
            
            assert data is None

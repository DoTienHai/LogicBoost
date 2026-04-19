"""Unit tests for database models."""
import pytest
from app.models import db, Question, UserAnswer, Stats
from app.models.user import User


def make_user(db_session, username="testuser", email="test@example.com"):
    """Helper: create and commit a minimal User."""
    user = User(username=username, email=email)
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()
    return user


class TestQuestion:
    """Tests for Question model."""

    def test_create_question(self, db_session):
        """Test creating a question."""
        question = Question(
            title="Sample Question",
            question="What is 2 + 2?",
            explanation="2 + 2 = 4",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            answer="b",
            mode="daily_challenge",
            difficulty=1,
        )
        db_session.add(question)
        db_session.commit()

        assert question.id is not None
        assert question.title == "Sample Question"
        assert question.answer == "b"

    def test_question_with_vietnamese(self, db_session):
        """Test creating question with Vietnamese translation."""
        question = Question(
            title="Math Question",
            question="What is 2 + 2?",
            explanation="The answer is 4",
            title_vi="Câu Hỏi Toán",
            question_vi="2 + 2 bằng mấy?",
            explanation_vi="Câu trả lời là 4",
            answer="4",
            mode="daily_challenge",
        )
        db_session.add(question)
        db_session.commit()

        assert question.title_vi == "Câu Hỏi Toán"
        assert question.question_vi == "2 + 2 bằng mấy?"

    def test_question_to_dict_english(self, db_session):
        """Test converting question to dict (English)."""
        question = Question(
            title="Sample",
            question="Test?",
            explanation="Test answer",
            option_a="A",
            option_b="B",
            answer="a",
            mode="daily_challenge",
        )
        db_session.add(question)
        db_session.commit()

        result = question.to_dict("en")
        assert result["title"] == "Sample"
        assert result["option_a"] == "A"

    def test_question_to_dict_vietnamese_fallback(self, db_session):
        """Test converting question to dict with Vietnamese fallback."""
        question = Question(
            title="Sample",
            question="Test?",
            explanation="Test answer",
            title_vi="Mẫu",
            answer="a",
            mode="daily_challenge",
        )
        db_session.add(question)
        db_session.commit()

        result = question.to_dict("vi")
        assert result["title"] == "Mẫu"  # Vietnamese version
        assert result["question"] == "Test?"  # Falls back to English

    def test_question_free_text_mode(self, db_session):
        """Test question without multiple choice options."""
        question = Question(
            title="Free Text Question",
            question="What is the capital of Vietnam?",
            explanation="Hanoi is the capital",
            answer="Hanoi",
            mode="mini_game",
            option_a=None,
            option_b=None,
            option_c=None,
            option_d=None,
        )
        db_session.add(question)
        db_session.commit()

        assert question.option_a is None
        assert question.answer == "Hanoi"


class TestUserAnswer:
    """Tests for UserAnswer model."""

    def test_create_user_answer(self, db_session):
        """Test creating a user answer."""
        user = make_user(db_session)
        # Create question first
        question = Question(
            title="Test Q",
            question="Q?",
            explanation="Ans",
            answer="b",
            mode="daily_challenge",
        )
        db_session.add(question)
        db_session.commit()

        # Create user answer
        answer = UserAnswer(
            user_id=user.id,
            question_id=question.id,
            question_type="multiple_choice",
            mode="daily_challenge",
            chosen="b",
            is_correct=True,
            time_taken=15,
        )
        db_session.add(answer)
        db_session.commit()

        assert answer.id is not None
        assert answer.is_correct is True
        assert answer.time_taken == 15

    def test_user_answer_relationship(self, db_session):
        """Test UserAnswer relationship with Question."""
        user = make_user(db_session, username="user2", email="user2@example.com")
        question = Question(
            title="Test",
            question="Q?",
            explanation="A",
            answer="a",
            mode="daily_challenge",
        )
        db_session.add(question)
        db_session.commit()

        answer = UserAnswer(
            user_id=user.id,
            question_id=question.id,
            question_type="free_text",
            mode="daily_challenge",
            chosen="my answer",
            is_correct=False,
        )
        db_session.add(answer)
        db_session.commit()

        # Verify relationship
        retrieved_question = db_session.get(Question, question.id)
        assert len(retrieved_question.user_answers) == 1
        assert retrieved_question.user_answers[0].chosen == "my answer"

    def test_user_answer_to_dict(self, db_session):
        """Test converting user answer to dict."""
        user = make_user(db_session, username="user3", email="user3@example.com")
        question = Question(
            title="Test",
            question="Q?",
            explanation="A",
            answer="a",
            mode="daily_challenge",
        )
        db_session.add(question)
        db_session.commit()

        answer = UserAnswer(
            user_id=user.id,
            question_id=question.id,
            question_type="multiple_choice",
            mode="daily_challenge",
            chosen="a",
            is_correct=True,
            time_taken=10,
        )
        db_session.add(answer)
        db_session.commit()

        result = answer.to_dict()
        assert result["is_correct"] is True
        assert result["time_taken"] == 10
        assert "answered_at" in result


class TestStats:
    """Tests for Stats model."""

    def test_create_stats(self, db_session):
        """Test creating stats entry."""
        user = make_user(db_session, username="statsuser1", email="stats1@example.com")
        stats = Stats(user_id=user.id, mode="daily_challenge", correct=10, incorrect=2)
        db_session.add(stats)
        db_session.commit()

        assert stats.id is not None
        assert stats.mode == "daily_challenge"
        assert stats.correct == 10

    def test_stats_to_dict(self, db_session):
        """Test converting stats to dict."""
        user = make_user(db_session, username="statsuser2", email="stats2@example.com")
        stats = Stats(user_id=user.id, mode="mini_game", correct=15, incorrect=5)
        db_session.add(stats)
        db_session.commit()

        result = stats.to_dict()
        assert result["mode"] == "mini_game"
        assert result["total"] == 20
        assert result["accuracy"] == 75.0

    def test_stats_accuracy_calculation(self, db_session):
        """Test accuracy calculation in stats."""
        user = make_user(db_session, username="statsuser3", email="stats3@example.com")
        # Perfect score
        stats1 = Stats(user_id=user.id, mode="daily_challenge", correct=10, incorrect=0)
        db_session.add(stats1)
        db_session.commit()
        assert stats1.to_dict()["accuracy"] == 100.0

        # Half correct
        stats2 = Stats(user_id=user.id, mode="real_world", correct=5, incorrect=5)
        db_session.add(stats2)
        db_session.commit()
        assert stats2.to_dict()["accuracy"] == 50.0

    def test_stats_empty_accuracy(self, db_session):
        """Test accuracy when no answers yet."""
        user = make_user(db_session, username="statsuser4", email="stats4@example.com")
        stats = Stats(user_id=user.id, mode="mini_game", correct=0, incorrect=0)
        db_session.add(stats)
        db_session.commit()

        assert stats.to_dict()["accuracy"] == 0

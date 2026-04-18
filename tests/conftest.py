"""Pytest fixtures for LogicBoost tests."""
import sys
from pathlib import Path

# Add parent directory to path so pytest can find app module
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app import create_app
from app.models import db


@pytest.fixture(scope="function")
def app():
    """Create application for testing."""
    app = create_app("testing")
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def runner(app):
    """CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture(scope="function")
def db_session(app):
    """Database session for testing."""
    with app.app_context():
        yield db.session


@pytest.fixture(scope="function")
def sample_mini_game_questions(app, db_session):
    """Create sample mini game questions for testing."""
    from app.models import Question
    
    with app.app_context():
        # Multiple choice question
        q1 = Question(
            title="Quick Math",
            question="What is 2 + 2?",
            option_a="3",
            option_b="4",
            option_c="5",
            option_d="6",
            answer="b",
            explanation="2 + 2 = 4",
            mode="mini_game",
            difficulty=1,
            time_limit=30
        )
        
        # Free text question
        q2 = Question(
            title="Capital City",
            question="What is the capital of France?",
            answer="Paris",
            explanation="Paris is the capital and largest city of France.",
            mode="mini_game",
            difficulty=1,
            time_limit=45
        )
        
        # Multiple choice with Vietnamese
        q3 = Question(
            title="Basic Calculation",
            title_vi="Tính toán cơ bản",
            question="What is 10 x 5?",
            question_vi="10 x 5 bằng bao nhiêu?",
            option_a="45",
            option_b="50",
            option_c="55",
            option_d="60",
            answer="b",
            explanation="10 multiplied by 5 equals 50",
            explanation_vi="10 nhân 5 bằng 50",
            mode="mini_game",
            difficulty=2,
            time_limit=40
        )
        
        db_session.add_all([q1, q2, q3])
        db_session.commit()
        
        return [q1, q2, q3]

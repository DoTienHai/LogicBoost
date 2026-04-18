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

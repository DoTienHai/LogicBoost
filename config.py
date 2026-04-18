"""Flask configuration settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Try to create instance directory on local development (for SQLite database file)
try:
    base_dir = Path(__file__).resolve().parent
    instance_dir = base_dir / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    # Render or read-only filesystem - skip directory creation
    pass


class Config:
    """Base configuration - shared across all environments."""

    FLASK_APP = os.getenv("FLASK_APP", "run.py")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Feature configuration
    MAX_QUESTIONS_PER_DAILY = 5  # Daily challenge questions count
    MINI_GAME_TIME_LIMIT = 60  # Seconds per mini game question


class DevelopmentConfig(Config):
    """Development configuration - localhost coding and testing."""
    
    DEBUG = True
    TESTING = False
    # SQLite database: logicboost.db in instance/ directory
    # Auto-created: first run of app creates the file + tables
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./instance/logicboost.db'


class TestingConfig(Config):
    """Testing configuration - unit tests with isolated database."""
    
    DEBUG = True
    TESTING = True
    # In-memory SQLite: exists only during test run
    # Auto-cleanup: database deleted when test finishes
    # Speed: fast execution (no disk I/O)
    # Isolation: no side effects between tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration - Render deployment."""
    
    DEBUG = False
    TESTING = False
    # SQLite database: same path as development
    # Works on Render with lazy initialization (@app.before_request)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./instance/logicboost.db'


def get_config(env: str = None) -> Config:
    """Get config object based on environment."""
    env = env or os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)

"""Flask configuration settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build absolute path to instance directory (works on Windows and Linux)
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"

# Try to create instance directory on local development
try:
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    # Render or read-only filesystem - skip directory creation
    pass

# Build absolute SQLite database URI
DB_PATH = INSTANCE_DIR / "logicboost.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.as_posix()}"


class Config:
    """Base configuration - shared across all environments."""

    FLASK_APP = os.getenv("FLASK_APP", "run.py")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI  # Use absolute path built above
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Feature configuration
    MAX_QUESTIONS_PER_DAILY = 5  # Daily challenge questions count
    MINI_GAME_TIME_LIMIT = 60  # Seconds per mini game question


class DevelopmentConfig(Config):
    """Development configuration - localhost coding and testing."""
    
    DEBUG = True
    TESTING = False
    # Inherit SQLite database from Config (absolute path)


class TestingConfig(Config):
    """Testing configuration - unit tests with isolated database."""
    
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for tests
    # In-memory SQLite: exists only during test run
    # Auto-cleanup: database deleted when test finishes
    # Speed: fast execution (no disk I/O)
    # Isolation: no side effects between tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration - Render deployment."""
    
    DEBUG = False
    TESTING = False
    # Inherit SQLite database from Config (absolute path)


def get_config(env: str = None) -> Config:
    """Get config object based on environment."""
    env = env or os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)

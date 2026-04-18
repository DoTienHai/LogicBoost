"""Flask configuration settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _get_database_uri():
    """Get the database URI with absolute path."""
    base_dir = Path(__file__).resolve().parent  # config.py is in root, so .parent is root
    instance_dir = base_dir / "instance"
    db_path = instance_dir / "logicboost.db"
    # Create instance directory if needed
    instance_dir.mkdir(parents=True, exist_ok=True)
    # Convert file URI to sqlite URI
    file_uri = db_path.as_uri()
    sqlite_uri = file_uri.replace("file://", "sqlite://")
    return sqlite_uri


def _get_database_url():
    """Get database URL from environment, with PostgreSQL compatibility fix."""
    db_url = os.getenv("DATABASE_URL", _get_database_uri())
    
    # Fix PostgreSQL URL format for SQLAlchemy 2.0
    # Render uses postgres:// but SQLAlchemy 2.0+ requires postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    return db_url


class Config:
    """Base configuration."""

    FLASK_APP = os.getenv("FLASK_APP", "run.py")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Feature configuration
    MAX_QUESTIONS_PER_DAILY = 5  # Daily challenge questions count
    MINI_GAME_TIME_LIMIT = 60  # Seconds per mini game question


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False


def get_config(env: str = None) -> Config:
    """Get config object based on environment."""
    env = env or os.getenv("FLASK_ENV", "development")
    
    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    
    return config_map.get(env, DevelopmentConfig)

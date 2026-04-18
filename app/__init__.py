"""Flask application factory."""
import os
from flask import Flask
from config import get_config
from app.models import db


def create_app(config_name: str = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Environment name (development, testing, production)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Create instance directory if it doesn't exist
    if not config_name or config_name == "development":
        instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "instance")
        os.makedirs(instance_path, exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.daily_challenge import daily_challenge_bp
    from app.routes.mini_game import mini_game_bp
    from app.routes.real_world import real_world_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(daily_challenge_bp)
    app.register_blueprint(mini_game_bp)
    app.register_blueprint(real_world_bp)
    app.register_blueprint(admin_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

"""Flask application factory."""
import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import get_config
from app.models import db

csrf = CSRFProtect()


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
    
    # Create instance directory if it doesn't exist (development only)
    # On Render, filesystem is read-only, skip this
    if config_name != "production":
        try:
            instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "instance")
            os.makedirs(instance_path, exist_ok=True)
        except (OSError, PermissionError):
            # Render or read-only filesystem - skip
            pass
    
    # Initialize database
    db.init_app(app)
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login_get"
    login_manager.login_message = ""  # Disable auto-message; auth routes handle flashing
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user from database by ID."""
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.daily_challenge import daily_challenge_bp
    from app.routes.mini_game import mini_game_bp
    from app.routes.real_world import real_world_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(daily_challenge_bp)
    app.register_blueprint(mini_game_bp)
    app.register_blueprint(real_world_bp)
    app.register_blueprint(admin_bp)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return {"error": "Access denied"}, 403
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    # Create tables and initialize database
    with app.app_context():
        db.create_all()
        init_auth_database()
    
    return app


def init_auth_database():
    """Initialize authentication database with default roles and admin user."""
    from app.models import User, Role, Permission
    
    # Create default roles if they don't exist
    if not Role.query.filter_by(name="admin").first():
        admin_role = Role(
            name="admin",
            display_name="Administrator",
            description="Full access to all features and user management",
        )
        db.session.add(admin_role)
    
    if not Role.query.filter_by(name="content_creator").first():
        content_creator_role = Role(
            name="content_creator",
            display_name="Content Creator",
            description="Can manage questions and import Excel",
        )
        db.session.add(content_creator_role)
    
    if not Role.query.filter_by(name="user").first():
        user_role = Role(
            name="user",
            display_name="User",
            description="Can only play games and view questions",
        )
        db.session.add(user_role)
    
    db.session.commit()
    
    # Create default permissions if they don't exist
    permissions_config = [
        # Content permissions
        ("view_questions", "View Questions", "content"),
        ("create_questions", "Create Questions", "content"),
        ("edit_questions", "Edit Questions", "content"),
        ("delete_questions", "Delete Questions", "content"),
        ("import_excel", "Import Excel", "content"),
        # User management permissions
        ("view_users", "View Users", "user_management"),
        ("create_users", "Create Users", "user_management"),
        ("edit_users", "Edit Users", "user_management"),
        ("delete_users", "Delete Users", "user_management"),
        ("assign_roles", "Assign Roles", "user_management"),
        # System permissions
        ("manage_roles", "Manage Roles", "system"),
        ("manage_permissions", "Manage Permissions", "system"),
    ]
    
    for perm_name, display_name, category in permissions_config:
        if not Permission.query.filter_by(name=perm_name).first():
            permission = Permission(
                name=perm_name, display_name=display_name, category=category
            )
            db.session.add(permission)
    
    db.session.commit()
    
    # Assign permissions to roles
    admin_role = Role.query.filter_by(name="admin").first()
    content_creator_role = Role.query.filter_by(name="content_creator").first()
    user_role = Role.query.filter_by(name="user").first()
    
    # Admin: all permissions
    if admin_role:
        all_permissions = Permission.query.all()
        for permission in all_permissions:
            if permission not in admin_role.permissions:
                admin_role.permissions.append(permission)
    
    # Content Creator: content + view_users permissions
    if content_creator_role:
        content_perms = Permission.query.filter(
            Permission.category.in_(["content"])
        ).all()
        view_users_perm = Permission.query.filter_by(name="view_users").first()
        
        for permission in content_perms:
            if permission not in content_creator_role.permissions:
                content_creator_role.permissions.append(permission)
        
        if view_users_perm and view_users_perm not in content_creator_role.permissions:
            content_creator_role.permissions.append(view_users_perm)
    
    # User: view_questions permission only
    if user_role:
        view_questions_perm = Permission.query.filter_by(name="view_questions").first()
        if view_questions_perm and view_questions_perm not in user_role.permissions:
            user_role.permissions.append(view_questions_perm)
    
    db.session.commit()
    
    # Create default admin user if it doesn't exist
    if not User.query.filter_by(username="admin").first():
        admin_user = User(
            username="admin",
            email="admin@logicboost.local",
            first_name="Admin",
            is_active=True,
        )
        admin_user.set_password("admin123")
        
        admin_role = Role.query.filter_by(name="admin").first()
        if admin_role:
            admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        db.session.commit()

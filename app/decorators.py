"""Custom decorators for route protection and authorization."""
import functools
from flask import abort
from flask_login import current_user, login_required


def require_permission(permission_name: str):
    """
    Decorator to require a specific permission for accessing a route.

    Usage:
        @require_permission('edit_questions')
        def edit_question():
            ...

    Args:
        permission_name: Name of the permission to check

    Returns:
        Decorated function
    """

    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission_name):
                abort(403)  # Forbidden
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_role(role_name: str):
    """
    Decorator to require a specific role for accessing a route.

    Usage:
        @require_role('admin')
        def admin_dashboard():
            ...

    Args:
        role_name: Name of the role to check

    Returns:
        Decorated function
    """

    def decorator(f):
        @functools.wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role_name):
                abort(403)  # Forbidden
            return f(*args, **kwargs)

        return decorated_function

    return decorator

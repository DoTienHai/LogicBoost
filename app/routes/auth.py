"""Authentication routes."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from app.services.auth_service import AuthService
from app.constants.error_codes import AuthError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET"])
def register():
    """Display registration form."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    return render_template("auth/register.html")


@auth_bp.route("/register", methods=["POST"])
def register_submit():
    """Handle user registration submission."""
    if current_user.is_authenticated:
        error = AuthError.ALREADY_LOGGED_IN
        return jsonify({"success": False, "error": error["message"], "code": error["code"]}), error["status"]
    
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    
    user, error = AuthService.register_user(
        username, email, password, first_name, last_name
    )
    
    if error:
        return jsonify({
            "success": False,
            "error": error["message"],
            "code": error["code"]
        }), error["status"]
    
    return jsonify({
        "success": True,
        "message": "Registration successful! Please log in.",
        "redirect": url_for("auth.login_get")
    }), 201


@auth_bp.route("/login", methods=["GET"])
def login_get():
    """Display login form."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    """Process login submission."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    
    user, error = AuthService.login_user(username, password)
    
    if error:
        flash(error["message"], "error")
        return redirect(url_for("auth.login_get"))
    
    login_user(user)
    flash("Login successful!", "success")
    
    next_page = request.args.get("next")
    if next_page and next_page.startswith("/"):
        return redirect(next_page)
    return redirect(url_for("main.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET"])
@login_required
def profile_get():
    """Display user profile."""
    return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/profile", methods=["POST"])
@login_required
def profile_post():
    """Update user profile."""
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    
    success, error = AuthService.update_user(
        current_user.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
    )
    
    if error:
        flash(error["message"], "error")
    else:
        flash("Profile updated successfully!", "success")
        # Refresh current_user
        db.session.refresh(current_user)
        return redirect(url_for("auth.profile_get"))
    
    return render_template("auth/profile.html", user=current_user)


@auth_bp.route("/change-password", methods=["GET"])
@login_required
def change_password_get():
    """Display change password form."""
    return render_template("auth/change_password.html")


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password_post():
    """Process password change."""
    old_password = request.form.get("old_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")
    
    if new_password != confirm_password:
        error = AuthError.PASSWORDS_MISMATCH
        flash(error["message"], "error")
        return redirect(url_for("auth.change_password_get"))
    
    success, error = AuthService.change_password(
        current_user.id, old_password, new_password
    )
    
    if error:
        flash(error["message"], "error")
    else:
        flash("Password changed successfully!", "success")
        return redirect(url_for("auth.profile_get"))
    
    return render_template("auth/change_password.html")

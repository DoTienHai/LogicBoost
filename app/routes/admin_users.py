"""Admin routes for user management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import User, Role, db
from app.decorators import require_permission
from app.services.auth_service import AuthService

admin_users_bp = Blueprint("admin_users", __name__, url_prefix="/admin")


@admin_users_bp.route("/users", methods=["GET"])
@login_required
@require_permission("view_users")
def list_users_get():
    """Display list of all users."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    users = User.query.paginate(page=page, per_page=per_page)
    return render_template("admin/users.html", users=users)


@admin_users_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
@require_permission("view_users")
def view_user_get(user_id):
    """Display user details."""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    return render_template("admin/user_detail.html", user=user, roles=roles)


@admin_users_bp.route("/users/create", methods=["GET"])
@login_required
@require_permission("create_users")
def create_user_get():
    """Display create user form."""
    available_roles = Role.query.all()
    return render_template("admin/user_form.html", user=None, available_roles=available_roles, form_data={})


@admin_users_bp.route("/users/create", methods=["POST"])
@login_required
@require_permission("create_users")
def create_user_post():
    """Process new user creation."""
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    roles_input = request.form.get("roles", "")
    
    # Validate
    errors = []
    if not username:
        errors.append("Username is required")
    if not email:
        errors.append("Email is required")
    if not password:
        errors.append("Password is required")
    
    if password != confirm_password:
        errors.append("Passwords do not match")
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters")
    
    if errors:
        available_roles = Role.query.all()
        return render_template(
            "admin/user_form.html",
            user=None,
            errors=errors,
            available_roles=available_roles,
            form_data=request.form.to_dict()
        ), 400
    
    # Create user
    new_user, error = AuthService.register_user(
        username, email, password, first_name, last_name
    )
    
    if error:
        available_roles = Role.query.all()
        return render_template(
            "admin/user_form.html",
            user=None,
            errors=[error["message"]],
            available_roles=available_roles,
            form_data=request.form.to_dict()
        ), error["status"]
    
    # Assign roles
    if roles_input:
        try:
            role_ids = [int(rid) for rid in roles_input.split(",") if rid]
            roles = Role.query.filter(Role.id.in_(role_ids)).all()
            new_user.roles = roles
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Error assigning roles: {str(e)}", "error")
            return redirect(url_for("admin_users.list_users_get"))
    
    flash("User created successfully!", "success")
    return redirect(url_for("admin_users.list_users_get"))


@admin_users_bp.route("/users/<int:user_id>/edit", methods=["GET"])
@login_required
@require_permission("edit_users")
def edit_user_get(user_id):
    """Display edit user form."""
    user = User.query.get_or_404(user_id)
    available_roles = Role.query.all()
    return render_template(
        "admin/user_form.html",
        user=user,
        available_roles=available_roles,
        form_data={}
    )


@admin_users_bp.route("/users/<int:user_id>/edit", methods=["POST"])
@login_required
@require_permission("edit_users")
def edit_user_post(user_id):
    """Process user edit submission."""
    user = User.query.get_or_404(user_id)
    
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    is_active = request.form.get("is_active") == "on"
    roles_input = request.form.get("roles", "")
    
    # Validate email
    errors = []
    if not email:
        errors.append("Email is required")
    else:
        existing_email = User.query.filter(User.email == email, User.id != user_id).first()
        if existing_email:
            errors.append("Email already in use")
    
    if errors:
        available_roles = Role.query.all()
        return render_template(
            "admin/user_form.html",
            user=user,
            available_roles=available_roles,
            errors=errors,
            form_data=request.form.to_dict()
        ), 400
    
    try:
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_active = is_active
        
        # Update roles
        if roles_input:
            role_ids = [int(rid) for rid in roles_input.split(",") if rid]
            new_roles = Role.query.filter(Role.id.in_(role_ids)).all()
            user.roles = new_roles
        
        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("admin_users.view_user_get", user_id=user_id))
    except Exception as e:
        db.session.rollback()
        available_roles = Role.query.all()
        return render_template(
            "admin/user_form.html",
            user=user,
            available_roles=available_roles,
            errors=[f"Database error: {str(e)}"],
            form_data=request.form.to_dict()
        ), 500


@admin_users_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@require_permission("delete_users")
def delete_user(user_id):
    """Delete user."""
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting the only admin
    admin_role = Role.query.filter_by(name="admin").first()
    admin_users = User.query.join(User.roles).filter(Role.id == admin_role.id).all()
    
    if len(admin_users) == 1 and user in admin_users:
        flash("Cannot delete the only admin user", "error")
        return redirect(url_for("admin_users.view_user_get", user_id=user_id))
    
    success, error = AuthService.delete_user(user_id)
    
    if error:
        flash(error["message"], "error")
        return redirect(url_for("admin_users.view_user_get", user_id=user_id))
    
    flash("User deleted successfully!", "success")
    return redirect(url_for("admin_users.list_users_get"))


@admin_users_bp.route("/users/<int:user_id>/assign-role", methods=["POST"])
@login_required
@require_permission("assign_roles")
def assign_role(user_id):
    """Assign role to user."""
    user = User.query.get_or_404(user_id)
    role_id = request.form.get("role_id", type=int)
    
    if not role_id:
        flash("Role not selected", "error")
        return redirect(url_for("admin_users.view_user_get", user_id=user_id))
    
    success, error = AuthService.assign_role(user_id, role_id)
    
    if error:
        flash(error["message"], "error")
    else:
        flash("Role assigned successfully!", "success")
    
    return redirect(url_for("admin_users.view_user_get", user_id=user_id))


@admin_users_bp.route("/users/<int:user_id>/remove-role/<int:role_id>", methods=["POST"])
@login_required
@require_permission("assign_roles")
def remove_role(user_id, role_id):
    """Remove role from user."""
    user = User.query.get_or_404(user_id)
    
    success, error = AuthService.revoke_role(user_id, role_id)
    
    if error:
        flash(error["message"], "error")
    else:
        flash("Role removed successfully!", "success")
    
    return redirect(url_for("admin_users.view_user_get", user_id=user_id))

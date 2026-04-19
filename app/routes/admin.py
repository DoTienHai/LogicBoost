"""Admin routes."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import login_required
from app.models import Question, SubCategory, DifficultyLevel, db, User, Role
from app.services.import_service import import_from_excel
from app.decorators import require_permission
from app.services.auth_service import AuthService
import os
from werkzeug.utils import secure_filename
import tempfile
from PIL import Image
import io

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Image upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../static/images/questions')
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg'}
MAX_IMAGE_SIZE = 200 * 1024  # 200 KB


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image_file(file):
    """Validate image file. Returns (is_valid, error_message)."""
    if not file or file.filename == '':
        return True, None
    
    if not allowed_file(file.filename):
        return False, "Image must be PNG, WebP, JPG, or JPEG"
    
    if len(file.read()) > MAX_IMAGE_SIZE:
        file.seek(0)
        return False, "Image must be smaller than 200 KB"
    
    file.seek(0)
    return True, None


def save_image(file, question_id, image_type):
    """
    Save uploaded image with naming convention {question_id}_{image_type}.ext
    image_type: 'q' (question) or 'e' (explanation)
    Returns: (filename, error_message) or (None, error_message)
    """
    if not file or file.filename == '':
        return None, None
    
    # Validate
    is_valid, error = validate_image_file(file)
    if not is_valid:
        return None, error
    
    # Create upload folder if doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    try:
        # Convert to PNG for consistency (even if uploaded as WebP/JPG)
        img = Image.open(file)
        
        # Convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Generate filename
        filename = f"{question_id}_{image_type}.png"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save as PNG
        img.save(filepath, 'PNG', optimize=True)
        
        return filename, None
    except Exception as e:
        return None, f"Error processing image: {str(e)}"


def validate_question_data(data):
    """Validate question form data. Returns (is_valid, error_message)."""
    errors = []
    
    # Required fields
    if not data.get("title"):
        errors.append("Title (EN) is required")
    if not data.get("question"):
        errors.append("Question (EN) is required")
    if not data.get("explanation"):
        errors.append("Explanation (EN) is required")
    if not data.get("answer"):
        errors.append("Answer is required")
    if not data.get("mode"):
        errors.append("Mode is required")
    if not data.get("difficulty"):
        errors.append("Difficulty is required")
    
    # Validate mode
    valid_modes = ["daily_challenge", "mini_game", "real_world"]
    if data.get("mode") not in valid_modes:
        errors.append(f"Invalid mode. Must be one of: {', '.join(valid_modes)}")
    
    # Validate difficulty
    try:
        difficulty = int(data.get("difficulty", 1))
        if difficulty not in DifficultyLevel.all_values():
            errors.append("Difficulty must be 1-5 (Very Easy to Very Hard)")
    except (ValueError, TypeError):
        errors.append("Difficulty must be a number")
    
    # Validate time_limit if provided
    if data.get("time_limit"):
        try:
            int(data.get("time_limit"))
        except (ValueError, TypeError):
            errors.append("Time limit must be a number (seconds)")
    
    # Validate sub_category for real_world mode
    if data.get("mode") == "real_world" and not data.get("sub_category"):
        errors.append("Sub-category is required for Real-world mode")
    
    # Validate sub_category exists if provided
    if data.get("sub_category"):
        sub_cat = SubCategory.query.filter_by(name=data.get("sub_category")).first()
        if not sub_cat:
            errors.append(f"Sub-category '{data.get('sub_category')}' does not exist. Valid values: finance, career, business")
    
    return len(errors) == 0, errors


@admin_bp.route("/")
@login_required
@require_permission("view_questions")
def index():
    """Admin dashboard - list all questions."""
    questions = Question.query.all()
    return render_template("admin/index.html", questions=questions)


@admin_bp.route("/question/new", methods=["GET", "POST"])
@login_required
@require_permission("create_questions")
def add_question():
    """Add new question form."""
    if request.method == "POST":
        # Validate input
        is_valid, errors = validate_question_data(request.form)
        if not is_valid:
            return render_template(
                "admin/question_form.html",
                errors=errors,
                form_data=request.form.to_dict()
            ), 400
        
        try:
            # Look up sub_category_id if provided
            sub_category_id = None
            if request.form.get("sub_category"):
                sub_cat = SubCategory.query.filter_by(name=request.form.get("sub_category")).first()
                if sub_cat:
                    sub_category_id = sub_cat.id
            
            # Create question object (without ID yet)
            question = Question(
                title=request.form.get("title"),
                title_vi=request.form.get("title_vi"),
                question=request.form.get("question"),
                question_vi=request.form.get("question_vi"),
                explanation=request.form.get("explanation"),
                explanation_vi=request.form.get("explanation_vi"),
                option_a=request.form.get("option_a") or None,
                option_b=request.form.get("option_b") or None,
                option_c=request.form.get("option_c") or None,
                option_d=request.form.get("option_d") or None,
                answer=request.form.get("answer"),
                mode=request.form.get("mode"),
                sub_category_id=sub_category_id,
                difficulty=int(request.form.get("difficulty", 1)),
                time_limit=request.form.get("time_limit") or None,
            )
            db.session.add(question)
            db.session.flush()  # Get the ID without committing
            
            # Handle image uploads
            if 'question_image' in request.files:
                filename, error = save_image(request.files['question_image'], question.id, 'q')
                if error:
                    db.session.rollback()
                    return render_template(
                        "admin/question_form.html",
                        errors=[error],
                        form_data=request.form.to_dict()
                    ), 400
                if filename:
                    question.question_image = filename
            
            if 'explanation_image' in request.files:
                filename, error = save_image(request.files['explanation_image'], question.id, 'e')
                if error:
                    db.session.rollback()
                    return render_template(
                        "admin/question_form.html",
                        errors=[error],
                        form_data=request.form.to_dict()
                    ), 400
                if filename:
                    question.explanation_image = filename
            
            db.session.commit()
            return redirect(url_for("admin.index"))
        except Exception as e:
            db.session.rollback()
            return render_template(
                "admin/question_form.html",
                errors=[f"Database error: {str(e)}"],
                form_data=request.form.to_dict()
            ), 500

    return render_template("admin/question_form.html", form_data={})


@admin_bp.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("edit_questions")
def edit_question(question_id):
    """Edit existing question."""
    question = Question.query.get_or_404(question_id)

    if request.method == "POST":
        # Validate input
        is_valid, errors = validate_question_data(request.form)
        if not is_valid:
            return render_template(
                "admin/question_form.html",
                question=question,
                errors=errors,
                form_data=request.form.to_dict()
            ), 400
        
        try:
            # Look up sub_category_id if provided
            sub_category_id = None
            if request.form.get("sub_category"):
                sub_cat = SubCategory.query.filter_by(name=request.form.get("sub_category")).first()
                if sub_cat:
                    sub_category_id = sub_cat.id
            
            question.title = request.form.get("title")
            question.title_vi = request.form.get("title_vi")
            question.question = request.form.get("question")
            question.question_vi = request.form.get("question_vi")
            question.explanation = request.form.get("explanation")
            question.explanation_vi = request.form.get("explanation_vi")
            question.option_a = request.form.get("option_a") or None
            question.option_b = request.form.get("option_b") or None
            question.option_c = request.form.get("option_c") or None
            question.option_d = request.form.get("option_d") or None
            question.answer = request.form.get("answer")
            question.mode = request.form.get("mode")
            question.sub_category_id = sub_category_id
            question.difficulty = int(request.form.get("difficulty", 1))
            question.time_limit = request.form.get("time_limit") or None
            
            # Handle image uploads (optional, can update without changing images)
            if 'question_image' in request.files and request.files['question_image'].filename:
                filename, error = save_image(request.files['question_image'], question.id, 'q')
                if error:
                    db.session.rollback()
                    return render_template(
                        "admin/question_form.html",
                        question=question,
                        errors=[error],
                        form_data=request.form.to_dict()
                    ), 400
                if filename:
                    question.question_image = filename
            
            if 'explanation_image' in request.files and request.files['explanation_image'].filename:
                filename, error = save_image(request.files['explanation_image'], question.id, 'e')
                if error:
                    db.session.rollback()
                    return render_template(
                        "admin/question_form.html",
                        question=question,
                        errors=[error],
                        form_data=request.form.to_dict()
                    ), 400
                if filename:
                    question.explanation_image = filename

            db.session.commit()
            return redirect(url_for("admin.index"))
        except Exception as e:
            db.session.rollback()
            return render_template(
                "admin/question_form.html",
                question=question,
                errors=[f"Database error: {str(e)}"],
                form_data=request.form.to_dict()
            ), 500

    return render_template("admin/question_form.html", question=question, form_data={})


@admin_bp.route("/question/<int:question_id>/delete", methods=["POST"])
@login_required
@require_permission("delete_questions")
def delete_question(question_id):
    """Delete question."""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("admin.index"))


@admin_bp.route("/import", methods=["GET", "POST"])
@login_required
@require_permission("import_excel")
def import_page():
    """Excel import page."""
    results = None
    
    if request.method == "POST":
        # Check if file was uploaded
        if "file" not in request.files:
            results = {"errors": ["No file selected"], "success": 0}
        else:
            file = request.files["file"]
            
            if file.filename == "":
                results = {"errors": ["No file selected"], "success": 0}
            elif not file.filename.endswith((".xlsx", ".xls")):
                results = {"errors": ["File must be .xlsx or .xls format"], "success": 0}
            else:
                try:
                    # Create temporary file in system temp directory
                    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                        filepath = tmp_file.name
                        file.save(filepath)
                    
                    # Import questions from file
                    results = import_from_excel(filepath)
                    
                    # Clean up temporary file
                    try:
                        if os.path.exists(filepath):
                            os.remove(filepath)
                    except Exception:
                        pass  # Ignore cleanup errors
                    
                except Exception as e:
                    results = {"errors": [f"Error processing file: {str(e)}"], "success": 0}
    
    return render_template("admin/import_excel.html", results=results)


@admin_bp.route("/import/template")
def download_template():
    """Download Excel template."""
    template_dir = os.path.join(os.path.dirname(__file__), "..", "static", "templates")
    template_file = "questions_template.xlsx"
    
    # Check if template file exists
    template_path = os.path.join(template_dir, template_file)
    if not os.path.exists(template_path):
        flash("Template file not found. Please contact admin.", "error")
        return redirect(url_for("admin.import_page"))
    
    return send_from_directory(template_dir, template_file, as_attachment=True)


# User Management Routes


# User Form Route (Create/Edit)
@admin_bp.route("/users/", defaults={"user_id": None}, methods=["GET", "POST"])
@admin_bp.route("/users/<int:user_id>/", methods=["GET", "POST"])
@login_required
def user_form(user_id=None):
    """Create or edit user."""
    user = None
    available_roles = Role.query.all()
    
    if user_id:
        # Edit existing user
        user = User.query.get_or_404(user_id)
        if request.method == "POST":
            # Handle edit
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip()
            is_active = request.form.get("is_active") == "on"
            roles_input = request.form.get("roles", "")
            
            # Validate email
            existing_email = User.query.filter(User.email == email, User.id != user_id).first()
            if existing_email:
                flash("Email already in use", "error")
                return redirect(url_for("admin.user_form", user_id=user_id))
            
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
            return redirect(url_for("admin.list_users"))
    else:
        # Create new user
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            roles_input = request.form.get("roles", "")
            
            # Validate
            if not all([username, email, password]):
                flash("Username, email, and password are required", "error")
                return redirect(url_for("admin.user_form"))
            
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return redirect(url_for("admin.user_form"))
            
            if len(password) < 6:
                flash("Password must be at least 6 characters", "error")
                return redirect(url_for("admin.user_form"))
            
            # Create user
            new_user, error = AuthService.register_user(
                username, email, password, first_name, last_name
            )
            
            if error:
                flash(error, "error")
                return redirect(url_for("admin.user_form"))
            
            # Assign roles
            if roles_input:
                role_ids = [int(rid) for rid in roles_input.split(",") if rid]
                roles = Role.query.filter(Role.id.in_(role_ids)).all()
                new_user.roles = roles
                db.session.commit()
            
            flash("User created successfully!", "success")
            return redirect(url_for("admin.list_users"))
    
    return render_template("admin/user_form.html", user=user, available_roles=available_roles)


@admin_bp.route("/users")
@login_required
@require_permission("view_users")
def list_users():
    """List all users."""
    page = request.args.get("page", 1, type=int)
    per_page = 20
    users = User.query.paginate(page=page, per_page=per_page)
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:user_id>")
@login_required
@require_permission("view_users")
def view_user(user_id):
    """View user details."""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    return render_template("admin/user_detail.html", user=user, roles=roles)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission("edit_users")
def edit_user(user_id):
    """Edit user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        is_active = request.form.get("is_active") == "on"
        
        success, error = AuthService.update_user(
            user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        
        if error:
            flash(error, "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))
        
        # Update is_active separately
        user.is_active = is_active
        db.session.commit()
        
        flash("User updated successfully!", "success")
        return redirect(url_for("admin.view_user", user_id=user_id))
    
    return render_template("admin/user_form.html", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
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
        return redirect(url_for("admin.view_user", user_id=user_id))
    
    success, error = AuthService.delete_user(user_id)
    
    if error:
        flash(error, "error")
        return redirect(url_for("admin.view_user", user_id=user_id))
    
    flash("User deleted successfully!", "success")
    return redirect(url_for("admin.list_users"))


@admin_bp.route("/users/<int:user_id>/assign-role", methods=["POST"])
@login_required
@require_permission("assign_roles")
def assign_role(user_id):
    """Assign role to user."""
    user = User.query.get_or_404(user_id)
    role_id = request.form.get("role_id", type=int)
    
    if not role_id:
        flash("Role not selected", "error")
        return redirect(url_for("admin.view_user", user_id=user_id))
    
    success, error = AuthService.assign_role(user_id, role_id)
    
    if error:
        flash(error, "error")
    else:
        flash("Role assigned successfully!", "success")
    
    return redirect(url_for("admin.view_user", user_id=user_id))


@admin_bp.route("/users/<int:user_id>/remove-role/<int:role_id>", methods=["POST"])
@login_required
@require_permission("assign_roles")
def remove_role(user_id, role_id):
    """Remove role from user."""
    user = User.query.get_or_404(user_id)
    
    success, error = AuthService.revoke_role(user_id, role_id)
    
    if error:
        flash(error, "error")
    else:
        flash("Role removed successfully!", "success")
    
    return redirect(url_for("admin.view_user", user_id=user_id))

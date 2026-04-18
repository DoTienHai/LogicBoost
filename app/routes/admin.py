"""Admin routes."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from app.models import Question, SubCategory, db
from app.services.import_service import import_from_excel
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
        if difficulty not in [1, 2, 3]:
            errors.append("Difficulty must be 1, 2, or 3")
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
def index():
    """Admin dashboard - list all questions."""
    questions = Question.query.all()
    return render_template("admin/index.html", questions=questions)


@admin_bp.route("/question/new", methods=["GET", "POST"])
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
def delete_question(question_id):
    """Delete question."""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("admin.index"))


@admin_bp.route("/import", methods=["GET", "POST"])
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

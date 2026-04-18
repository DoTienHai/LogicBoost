"""Admin routes."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from app.models import Question, db
from app.services.import_service import import_from_excel
import os
from werkzeug.utils import secure_filename
import tempfile

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
            # Create and save question
            question = Question(
                title=request.form.get("title"),
                title_vi=request.form.get("title_vi"),
                question=request.form.get("question"),
                question_vi=request.form.get("question_vi"),
                explanation=request.form.get("explanation"),
                explanation_vi=request.form.get("explanation_vi"),
                option_a=request.form.get("option_a"),
                option_b=request.form.get("option_b"),
                option_c=request.form.get("option_c"),
                option_d=request.form.get("option_d"),
                answer=request.form.get("answer"),
                mode=request.form.get("mode"),
                sub_category=request.form.get("sub_category"),
                difficulty=int(request.form.get("difficulty", 1)),
                time_limit=request.form.get("time_limit") or None,
            )
            db.session.add(question)
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
            question.title = request.form.get("title")
            question.title_vi = request.form.get("title_vi")
            question.question = request.form.get("question")
            question.question_vi = request.form.get("question_vi")
            question.explanation = request.form.get("explanation")
            question.explanation_vi = request.form.get("explanation_vi")
            question.option_a = request.form.get("option_a")
            question.option_b = request.form.get("option_b")
            question.option_c = request.form.get("option_c")
            question.option_d = request.form.get("option_d")
            question.answer = request.form.get("answer")
            question.mode = request.form.get("mode")
            question.sub_category = request.form.get("sub_category")
            question.difficulty = int(request.form.get("difficulty", 1))
            question.time_limit = request.form.get("time_limit") or None

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

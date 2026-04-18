"""Admin routes."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models import Question, db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/")
def index():
    """Admin dashboard - list all questions."""
    questions = Question.query.all()
    return render_template("admin/index.html", questions=questions)


@admin_bp.route("/question/new", methods=["GET", "POST"])
def add_question():
    """Add new question form."""
    if request.method == "POST":
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
            time_limit=request.form.get("time_limit"),
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for("admin.index"))

    return render_template("admin/question_form.html")


@admin_bp.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    """Edit existing question."""
    question = Question.query.get_or_404(question_id)

    if request.method == "POST":
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
        question.time_limit = request.form.get("time_limit")

        db.session.commit()
        return redirect(url_for("admin.index"))

    return render_template("admin/question_form.html", question=question)


@admin_bp.route("/question/<int:question_id>/delete", methods=["POST"])
def delete_question(question_id):
    """Delete question."""
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("admin.index"))


@admin_bp.route("/import")
def import_page():
    """Excel import page."""
    return render_template("admin/import_excel.html")


@admin_bp.route("/import/template")
def download_template():
    """Download Excel template."""
    return "Template file here"

"""Real-world Problems routes."""
from flask import Blueprint, render_template, request, jsonify
from app.models import Question, db

real_world_bp = Blueprint("real_world", __name__, url_prefix="/real-world")


@real_world_bp.route("/")
def index():
    """Real-world problems by category."""
    categories = ["finance", "career", "business"]
    return render_template("real_world/index.html", categories=categories)


@real_world_bp.route("/<category>")
def category(category):
    """Get problems by category."""
    questions = Question.query.filter_by(
        mode="real_world", sub_category=category
    ).all()
    return render_template(
        "real_world/index.html",
        questions=questions,
        selected_category=category,
    )


@real_world_bp.route("/scenario/<int:question_id>")
def scenario(question_id):
    """Display scenario question."""
    question = Question.query.get_or_404(question_id)
    return render_template("real_world/scenario.html", question=question)


@real_world_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    """Submit scenario answer."""
    data = request.get_json()
    question_id = data.get("question_id")
    answer = data.get("answer")

    question = Question.query.get_or_404(question_id)
    is_correct = question.answer.lower() == answer.lower()

    return jsonify({
        "is_correct": is_correct,
        "answer": question.answer,
        "explanation": question.explanation,
    })


@real_world_bp.route("/explanation/<int:question_id>")
def explanation(question_id):
    """Show step-by-step explanation."""
    question = Question.query.get_or_404(question_id)
    return render_template("real_world/explanation.html", question=question)

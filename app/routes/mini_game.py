"""Mini Game routes."""
from flask import Blueprint, render_template, request, jsonify
from app.models import Question, db

mini_game_bp = Blueprint("mini_game", __name__, url_prefix="/mini-game")


@mini_game_bp.route("/")
def index():
    """Mini game selection page."""
    return render_template("mini_game/index.html")


@mini_game_bp.route("/play")
def play():
    """Start mini game with timer."""
    questions = Question.query.filter_by(mode="mini_game").limit(10).all()
    return render_template(
        "mini_game/play.html",
        question_id=questions[0].id if questions else None,
    )


@mini_game_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    """Submit timed answer."""
    data = request.get_json()
    question_id = data.get("question_id")
    answer = data.get("answer")
    time_taken = data.get("time_taken")

    question = Question.query.get_or_404(question_id)
    is_correct = question.answer.lower() == answer.lower()

    return jsonify({
        "is_correct": is_correct,
        "answer": question.answer,
        "time_taken": time_taken,
    })


@mini_game_bp.route("/result")
def result():
    """Show mini game result."""
    return render_template("mini_game/result.html")

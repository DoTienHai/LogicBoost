"""Daily Challenge routes."""
from flask import Blueprint, render_template, request, jsonify
from app.models import Question, UserAnswer, Stats, db

daily_challenge_bp = Blueprint("daily_challenge", __name__, url_prefix="/daily-challenge")


@daily_challenge_bp.route("/")
def index():
    """Daily challenge lobby."""
    return render_template("daily_challenge/index.html")


@daily_challenge_bp.route("/start")
def start():
    """Start daily challenge session."""
    # Get 3-5 random questions with increasing difficulty
    questions = Question.query.filter_by(mode="daily_challenge").all()
    return render_template(
        "daily_challenge/question.html",
        question_id=questions[0].id if questions else None,
        question_number=1,
        total_questions=len(questions),
    )


@daily_challenge_bp.route("/question/<int:question_id>")
def question(question_id):
    """Display a specific question."""
    q = Question.query.get_or_404(question_id)
    return render_template("daily_challenge/question.html", question=q)


@daily_challenge_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    """Submit answer for a question."""
    data = request.get_json()
    question_id = data.get("question_id")
    answer = data.get("answer")
    question_type = data.get("question_type")

    question = Question.query.get_or_404(question_id)
    is_correct = question.answer.lower() == answer.lower()

    # Save answer
    user_answer = UserAnswer(
        question_id=question_id,
        question_type=question_type,
        chosen=answer,
        is_correct=is_correct,
    )
    db.session.add(user_answer)
    db.session.commit()

    return jsonify({"is_correct": is_correct, "answer": question.answer})


@daily_challenge_bp.route("/summary")
def summary():
    """Show daily challenge summary."""
    return render_template("daily_challenge/summary.html")

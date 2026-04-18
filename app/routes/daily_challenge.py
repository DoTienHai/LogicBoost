"""Daily Challenge routes."""
from flask import Blueprint, render_template, request, jsonify, current_app, session, redirect, url_for
from app.models import Question, UserAnswer, Stats, db

daily_challenge_bp = Blueprint("daily_challenge", __name__, url_prefix="/daily-challenge")


@daily_challenge_bp.route("/")
def index():
    """Daily challenge lobby."""
    return render_template("daily_challenge/index.html")


@daily_challenge_bp.route("/start")
def start():
    """Start daily challenge session - load exactly 5 questions."""
    # Get 5 questions for this session
    num_questions = current_app.config['MAX_QUESTIONS_PER_DAILY']
    questions = Question.query.filter_by(mode="daily_challenge").limit(num_questions).all()
    
    if not questions or len(questions) < num_questions:
        return render_template(
            "daily_challenge/index.html",
            error="Not enough questions available. Need at least 5 questions."
        )
    
    # Store question IDs in session
    session["daily_challenge_questions"] = [q.id for q in questions]
    session["daily_challenge_current_index"] = 0
    session["daily_challenge_answers"] = []
    session.modified = True
    
    return redirect(url_for("daily_challenge.show_question", question_num=1))


@daily_challenge_bp.route("/question/<int:question_num>")
def show_question(question_num):
    """Display a specific question by number (1-5)."""
    # Check if session is active
    if "daily_challenge_questions" not in session:
        return redirect(url_for("daily_challenge.index"))
    
    question_list = session.get("daily_challenge_questions", [])
    num_questions = current_app.config['MAX_QUESTIONS_PER_DAILY']
    
    # Validate question number
    if question_num < 1 or question_num > num_questions or question_num > len(question_list):
        return redirect(url_for("daily_challenge.index"))
    
    # Get the question
    question_id = question_list[question_num - 1]
    q = Question.query.get_or_404(question_id)
    
    return render_template(
        "daily_challenge/question.html",
        question=q,
        question_number=question_num,
        total_questions=num_questions,
    )


@daily_challenge_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    """Submit answer for a question and move to next or summary."""
    data = request.get_json()
    question_id = data.get("question_id")
    answer = data.get("answer")
    question_type = data.get("question_type")
    question_num = data.get("question_num", 1)

    # Check session
    if "daily_challenge_questions" not in session:
        return jsonify({"error": "Session expired"}), 400

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
    
    # Store answer in session
    answers = session.get("daily_challenge_answers", [])
    answers.append({
        "question_id": question_id,
        "answer": answer,
        "is_correct": is_correct,
        "correct_answer": question.answer,
    })
    session["daily_challenge_answers"] = answers
    session.modified = True
    
    num_questions = current_app.config['MAX_QUESTIONS_PER_DAILY']
    
    # Determine next action
    if question_num < num_questions:
        # Move to next question
        next_num = question_num + 1
        return jsonify({
            "is_correct": is_correct,
            "answer": question.answer,
            "next_url": url_for("daily_challenge.show_question", question_num=next_num),
        })
    else:
        # All questions answered - redirect to summary
        return jsonify({
            "is_correct": is_correct,
            "answer": question.answer,
            "completed": True,
            "next_url": url_for("daily_challenge.summary"),
        })


@daily_challenge_bp.route("/summary")
def summary():
    """Show daily challenge summary."""
    if "daily_challenge_answers" not in session:
        return redirect(url_for("daily_challenge.index"))
    
    answers = session.get("daily_challenge_answers", [])
    correct_count = sum(1 for a in answers if a.get("is_correct"))
    
    # Clear session after summary
    session.pop("daily_challenge_questions", None)
    session.pop("daily_challenge_answers", None)
    session.modified = True
    
    return render_template(
        "daily_challenge/summary.html",
        total_questions=len(answers),
        correct_answers=correct_count,
        answers=answers,
    )

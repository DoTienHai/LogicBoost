"""Mini Game routes."""
from flask import Blueprint, render_template, request, jsonify, session
from app.models import Question, UserAnswer, db
import random

mini_game_bp = Blueprint("mini_game", __name__, url_prefix="/mini-game")


@mini_game_bp.route("/")
def index():
    """Mini game lobby page."""
    return render_template("mini_game/index.html")


@mini_game_bp.route("/play")
def play():
    """Play mini game page - loads questions dynamically."""
    return render_template("mini_game/play.html")


@mini_game_bp.route("/start", methods=["POST"])
def start():
    """Start a new mini game session."""
    # Initialize game session
    session["mini_game_active"] = True
    session["mini_game_score"] = 0
    session["mini_game_answered"] = []
    
    return jsonify({"status": "started"})


@mini_game_bp.route("/question")
def question():
    """Get next question for mini game."""
    # Get all mini_game questions
    all_questions = Question.query.filter_by(mode="mini_game").all()
    
    if not all_questions:
        return jsonify({"error": "No questions available"}), 404
    
    # Get questions already answered in this session
    answered_ids = session.get("mini_game_answered", [])
    
    # Find unanswered questions
    available = [q for q in all_questions if q.id not in answered_ids]
    
    # If all answered or none available, start over
    if not available:
        available = all_questions
    
    # Pick random question
    question_obj = random.choice(available)
    
    return jsonify({
        "id": question_obj.id,
        "title": question_obj.title,
        "question": question_obj.question,
        "question_image": question_obj.question_image,
        "option_a": question_obj.option_a,
        "option_b": question_obj.option_b,
        "option_c": question_obj.option_c,
        "option_d": question_obj.option_d,
        "time_limit": question_obj.time_limit or 60,  # Default 60 seconds
    })


@mini_game_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    """
    Submit answer for mini game.
    Returns: 
    - is_correct: boolean
    - correct_answer: string
    - score: number of correct in a row (if correct)
    - game_over: boolean (if wrong)
    """
    if not session.get("mini_game_active"):
        return jsonify({"error": "No active game"}), 400
    
    data = request.get_json()
    question_id = data.get("question_id")
    user_answer = data.get("answer")
    time_taken = data.get("time_taken", 0)
    
    question = Question.query.get_or_404(question_id)
    
    # Check answer (handle both multiple choice and free text)
    is_correct = (question.answer.lower().strip() == 
                  user_answer.lower().strip())
    
    # Record answer in database
    user_answer_record = UserAnswer(
        question_id=question_id,
        question_type="multiple_choice" if question.option_a else "free_text",
        chosen=user_answer,
        is_correct=is_correct,
        time_taken=time_taken,
    )
    db.session.add(user_answer_record)
    db.session.commit()
    
    if is_correct:
        # Add to answered list and increment score
        answered = session.get("mini_game_answered", [])
        answered.append(question_id)
        session["mini_game_answered"] = answered
        session["mini_game_score"] = len(answered)
        session.modified = True
        
        return jsonify({
            "is_correct": True,
            "correct_answer": question.answer,
            "score": session["mini_game_score"],
            "game_over": False,
        })
    else:
        # Wrong answer = Game Over
        session["mini_game_active"] = False
        session.modified = True
        
        return jsonify({
            "is_correct": False,
            "correct_answer": question.answer,
            "explanation": question.explanation,
            "score": session["mini_game_score"],
            "game_over": True,
        })


@mini_game_bp.route("/result")
def result():
    """Show mini game result and final score."""
    score = session.get("mini_game_score", 0)
    return render_template("mini_game/result.html", score=score)


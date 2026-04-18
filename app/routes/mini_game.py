"""Mini Game routes."""
from flask import Blueprint, render_template, request, jsonify, session
from app.services import mini_game_service

mini_game_bp = Blueprint("mini_game", __name__, url_prefix="/mini-game")


@mini_game_bp.route("/")
def index():
    """Mini game lobby page."""
    return render_template("mini_game/index.html")


@mini_game_bp.route("/play")
def play():
    """Play mini game page - loads questions dynamically."""
    # Always initialize a fresh session when entering play page
    session["mini_game_active"] = True
    session["mini_game_score"] = 0
    session["mini_game_answered"] = []
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
    # Get questions already answered in this session
    answered_ids = session.get("mini_game_answered", [])
    
    # Get language preference (default English)
    lang = request.args.get("lang", "en")
    
    # Get random question
    question_obj = mini_game_service.get_random_question(answered_ids)
    
    if not question_obj:
        return jsonify({"error": "No questions available"}), 404
    
    # Format question data
    question_data = mini_game_service.format_question_data(question_obj, lang)
    
    return jsonify(question_data)


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
    
    # Check answer using service
    result = mini_game_service.check_answer(question_id, user_answer, time_taken)
    
    if "error" in result:
        return jsonify(result), 404
    
    is_correct = result["is_correct"]
    
    if is_correct:
        # Add to answered list and increment score
        answered = session.get("mini_game_answered", [])
        answered.append(question_id)
        session["mini_game_answered"] = answered
        session["mini_game_score"] = len(answered)
        session.modified = True
        
        return jsonify({
            "is_correct": True,
            "correct_answer": result["correct_answer"],
            "score": session["mini_game_score"],
            "game_over": False,
            "time_limit": result.get("time_limit", 60)
        })
    else:
        # Wrong answer = Game Over
        final_score = session.get("mini_game_score", 0)
        session["mini_game_active"] = False
        session.modified = True
        
        return jsonify({
            "is_correct": False,
            "correct_answer": result["correct_answer"],
            "explanation": result.get("explanation", ""),
            "score": final_score,
            "game_over": True,
        })


@mini_game_bp.route("/result")
def result():
    """Show mini game result and final score."""
    score = session.get("mini_game_score", 0)
    return render_template("mini_game/result.html", score=score)


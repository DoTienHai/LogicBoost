"""Service layer for Quick Mini Game functionality."""
from app.models import Question, UserAnswer, db
import random


def get_random_question(answered_ids=None, last_question_id=None):
    """
    Get a random mini_game question that hasn't been answered yet.
    
    Args:
        answered_ids: List of question IDs already answered in this session
        last_question_id: ID of the last question shown (to avoid immediate repeat)
        
    Returns:
        Question object or None if no questions available
    """
    answered_ids = answered_ids or []
    exclude_ids = set(answered_ids)
    
    # Also exclude the last question to avoid immediate repeats
    if last_question_id:
        exclude_ids.add(last_question_id)
    
    # Get all mini_game questions
    all_questions = Question.query.filter_by(mode="mini_game").all()
    
    if not all_questions:
        return None
    
    # Filter out answered questions and last shown question
    available = [q for q in all_questions if q.id not in exclude_ids]
    
    # If all questions answered or only last_question remains, use all except answered
    if not available:
        available = [q for q in all_questions if q.id not in answered_ids]
    
    # If still empty (only 1 question total), reset to all
    if not available:
        available = all_questions
    
    # Return random question from available pool
    return random.choice(available) if available else None


def check_answer(question_id, user_answer, time_taken=0):
    """
    Check if user's answer is correct and record it.
    
    Args:
        question_id: ID of the question
        user_answer: User's answer (string)
        time_taken: Time taken to answer in seconds
        
    Returns:
        dict with keys:
            - is_correct: boolean
            - correct_answer: string
            - explanation: string (if wrong)
    """
    question = Question.query.get(question_id)
    if not question:
        return {"error": "Question not found"}
    
    # Determine question type
    question_type = "multiple_choice" if question.option_a else "free_text"
    
    # Check if answer is correct (different normalization for each type)
    if question_type == "multiple_choice":
        # Multiple choice: case-insensitive simple comparison
        is_correct = user_answer.lower().strip() == question.answer.lower().strip()
    else:
        # Free text: normalize by removing punctuation and spaces
        def normalize(text):
            """Normalize text by removing commas, spaces, periods, and converting to lowercase."""
            return text.replace(',', '').replace(' ', '').replace('.', '').lower().strip()
        
        is_correct = normalize(user_answer) == normalize(question.answer)
    
    # Record answer in database
    user_answer_record = UserAnswer(
        question_id=question_id,
        question_type=question_type,
        chosen=user_answer,
        is_correct=is_correct,
        time_taken=time_taken,
    )
    db.session.add(user_answer_record)
    db.session.commit()
    
    result = {
        "is_correct": is_correct,
        "correct_answer": question.answer,
        "time_limit": question.time_limit or 60,
    }
    
    # Include explanation if wrong
    if not is_correct:
        result["explanation"] = question.explanation
    
    return result


def format_question_data(question, lang="en"):
    """
    Format question data for frontend display.
    
    Args:
        question: Question object
        lang: Language code ('en' or 'vi')
        
    Returns:
        dict with question data formatted for JSON response
    """
    if not question:
        return None
    
    # Select language
    if lang == "vi":
        title = question.title_vi or question.title
        question_text = question.question_vi or question.question
    else:
        title = question.title
        question_text = question.question
    
    return {
        "id": question.id,
        "title": title,
        "question": question_text,
        "question_image": question.question_image,
        "option_a": question.option_a,
        "option_b": question.option_b,
        "option_c": question.option_c,
        "option_d": question.option_d,
        "time_limit": question.time_limit or 60,  # Default 60 seconds
    }

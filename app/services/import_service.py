"""Excel import service for questions."""
import openpyxl
from app.models import Question, SubCategory, db


def import_from_excel(filepath):
    """
    Import questions from Excel file.
    
    Expected columns:
    - title (required), title_vi
    - question (required), question_vi
    - option_a, option_b, option_c, option_d
    - answer (required)
    - explanation (required), explanation_vi
    - mode (required), sub_category, difficulty, time_limit
    
    Args:
        filepath: Path to Excel file
        
    Returns:
        dict with keys:
            'success': Number of successfully imported questions
            'errors': List of error messages (row_num, reason)
    """
    results = {'success': 0, 'errors': []}
    
    wb = None
    try:
        wb = openpyxl.load_workbook(filepath)
        ws = wb.active
    except Exception as e:
        results['errors'].append(f"Failed to open file: {str(e)}")
        return results
    
    try:
        # Iterate through rows (skip header at row 1)
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                (title, title_vi,
                 question, question_vi,
                 option_a, option_b, option_c, option_d,
                 answer,
                 explanation, explanation_vi,
                 mode, sub_category, difficulty, time_limit) = row[:15]
                
                # ---- VALIDATION ----
                # Required fields
                if not title:
                    results['errors'].append(f"Row {row_idx}: Title (EN) is required")
                    continue
                if not question:
                    results['errors'].append(f"Row {row_idx}: Question (EN) is required")
                    continue
                if not answer:
                    results['errors'].append(f"Row {row_idx}: Answer is required")
                    continue
                if not explanation:
                    results['errors'].append(f"Row {row_idx}: Explanation (EN) is required")
                    continue
                if not mode:
                    results['errors'].append(f"Row {row_idx}: Mode is required")
                    continue
                
                # Validate mode
                valid_modes = ['daily_challenge', 'mini_game', 'real_world']
                if mode not in valid_modes:
                    results['errors'].append(
                        f"Row {row_idx}: Invalid mode '{mode}'. "
                        f"Must be one of: {', '.join(valid_modes)}"
                    )
                    continue
                
                # Validate difficulty
                try:
                    difficulty = int(difficulty) if difficulty else 1
                    if difficulty not in [1, 2, 3]:
                        results['errors'].append(
                            f"Row {row_idx}: Difficulty {difficulty} invalid. Must be 1, 2, or 3"
                        )
                        continue
                except (ValueError, TypeError):
                    results['errors'].append(
                        f"Row {row_idx}: Difficulty must be a number"
                    )
                    continue
                
                # Validate time_limit if provided
                if time_limit:
                    try:
                        time_limit = int(time_limit)
                    except (ValueError, TypeError):
                        results['errors'].append(
                            f"Row {row_idx}: Time limit must be a number (seconds)"
                        )
                        continue
                else:
                    time_limit = None
                
                # ---- SAVE TO DATABASE ----
                # Look up sub_category_id if provided
                sub_category_id = None
                if sub_category:
                    sub_cat = SubCategory.query.filter_by(name=str(sub_category).strip().lower()).first()
                    if sub_cat:
                        sub_category_id = sub_cat.id
                    elif str(mode).strip() == 'real_world':
                        # For real_world mode, sub_category is required
                        results['errors'].append(
                            f"Row {row_idx}: Sub-category '{sub_category}' not found. "
                            f"Valid values: finance, career, business"
                        )
                        continue
                
                question_obj = Question(
                    title=str(title).strip(),
                    title_vi=str(title_vi).strip() if title_vi else None,
                    question=str(question).strip(),
                    question_vi=str(question_vi).strip() if question_vi else None,
                    option_a=str(option_a).strip() if option_a else None,
                    option_b=str(option_b).strip() if option_b else None,
                    option_c=str(option_c).strip() if option_c else None,
                    option_d=str(option_d).strip() if option_d else None,
                    answer=str(answer).strip(),
                    explanation=str(explanation).strip(),
                    explanation_vi=str(explanation_vi).strip() if explanation_vi else None,
                    mode=str(mode).strip(),
                    sub_category_id=sub_category_id,
                    difficulty=difficulty,
                    time_limit=time_limit,
                )
                
                db.session.add(question_obj)
                results['success'] += 1
                
            except ValueError as e:
                results['errors'].append(f"Row {row_idx}: Data format error - {str(e)}")
            except Exception as e:
                results['errors'].append(f"Row {row_idx}: {str(e)}")
        
        # Commit all successful additions at once
        if results['success'] > 0:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                results['errors'].insert(0, f"Database commit error: {str(e)}")
                results['success'] = 0
    
    finally:
        # Always close workbook to release file handle
        if wb:
            wb.close()
    
    return results

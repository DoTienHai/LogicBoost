"""Generate Excel template for admin import."""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation


def generate_template():
    """Generate Excel template for question import."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Questions"
    
    columns = [
        "title", "title_vi",
        "question", "question_vi",
        "option_a", "option_b", "option_c", "option_d",
        "answer",
        "explanation", "explanation_vi",
        "mode", "sub_category", "difficulty", "time_limit"
    ]
    
    # Header styling
    header_fill = PatternFill(start_color="0277BD", end_color="0277BD", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin")
    )
    
    # Add headers
    for col_idx, col_name in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = col_name
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = border
    
    # Add a few example rows (empty but formatted)
    for row_idx in range(2, 5):
        for col_idx in range(1, len(columns) + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = border
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    
    # Set column widths
    column_widths = {
        "A": 20, "B": 18, "C": 30, "D": 28, "E": 12, "F": 12,
        "G": 12, "H": 12, "I": 12, "J": 35, "K": 32, "L": 16,
        "M": 14, "N": 12, "O": 12
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    # Add data validation for dropdowns
    mode_dv = DataValidation(type="list", formula1='"daily_challenge,mini_game,real_world"', allow_blank=False)
    mode_dv.error = 'Select: daily_challenge, mini_game, or real_world'
    ws.add_data_validation(mode_dv)
    mode_dv.add("L2:L1000")
    
    sub_cat_dv = DataValidation(type="list", formula1='"finance,career,business"', allow_blank=True)
    sub_cat_dv.error = 'Select: finance, career, or business'
    ws.add_data_validation(sub_cat_dv)
    sub_cat_dv.add("M2:M1000")
    
    difficulty_dv = DataValidation(type="list", formula1='"1,2,3"', allow_blank=True)
    difficulty_dv.error = 'Select: 1, 2, or 3'
    ws.add_data_validation(difficulty_dv)
    difficulty_dv.add("N2:N1000")
    
    # Freeze header row
    ws.freeze_panes = "A2"
    
    # Save file
    output_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "app", "static", "templates",
        "questions_template.xlsx"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Generated template: {output_path}")


if __name__ == "__main__":
    generate_template()

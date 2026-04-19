"""Main routes for LogicBoost home page."""
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint("main", __name__, url_prefix="/")


@main_bp.route("/")
@login_required
def index():
    """Home page with navigation to all features."""
    return render_template("index.html")

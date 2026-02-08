from flask import Blueprint, render_template
import random

motivation_bp = Blueprint("motivation", __name__, url_prefix="/motivation")

QUOTES = [
    "Discipline beats motivation.",
    "Small steps every day.",
    "Your body can do it. Convince your mind.",
    "Progress, not perfection.",
]

@motivation_bp.route("", methods=["GET"])
def page():
    return render_template(
        "motivation.html",
        active="motivation",
        quote=random.choice(QUOTES),
    )

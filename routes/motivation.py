from flask import Blueprint, render_template
import random

motivation_bp = Blueprint("motivation", __name__, url_prefix="/motivation")

QUOTES = [
    "Discipline beats motivation.",
    "Small steps every day.",
    "Your body can do it. Convince your mind.",
    "Progress, not perfection.",
    "No pain, no gain.",
    "The only bad workout is the one that didn't happen.",
    "Push yourself, because no one else is going to do it for you.",
]

@motivation_bp.route("", methods=["GET"])
def page():
    return render_template(
        "motivation.html",
        active="motivation",
        quote=random.choice(QUOTES),
    )

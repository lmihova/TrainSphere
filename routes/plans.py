from flask import Blueprint, render_template, request
import json
import sqlite3
from pathlib import Path

plans_bp = Blueprint("plans", __name__, url_prefix="/plans")
DB_PATH = Path(__file__).resolve().parents[1] / "trainsphere.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@plans_bp.route("", methods=["GET", "POST"])
def page():
    if request.method == "POST":
        workout_type = request.form.get("workout_type")
        frequency = request.form.get("frequency")
        goal_type = request.form.get("goal_type")
        goal_value = request.form.get("goal_value")
        checklist = request.form.getlist("checklist")
        checklist_json = json.dumps(checklist, ensure_ascii=False) if checklist else None

        if workout_type and frequency and goal_type and goal_value:
            with get_db() as conn:
                conn.execute(
                    """INSERT INTO custom_plan
                       (workout_type, frequency_per_week, goal_type, goal_value, checklist_json)
                       VALUES (?, ?, ?, ?, ?)""",
                    (workout_type, frequency, goal_type, goal_value, checklist_json),
                )
                conn.commit()

        return render_template("plans.html", active="plans")

    return render_template("plans.html", active="plans")

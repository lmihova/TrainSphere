from flask import Blueprint, render_template, request, redirect, url_for
import json
import sqlite3
from pathlib import Path

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
DB_PATH = Path(__file__).resolve().parents[1] / "trainsphere.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@profile_bp.route("", methods=["GET", "POST"])
def page():
    if request.method == "POST":
        # Two different forms POST here (personal info + goals).
        # We keep a single "current" profile row by updating the latest record.
        name = (request.form.get("name") or "").strip() or None
        age = (request.form.get("age") or "").strip() or None
        height_cm = (request.form.get("height_cm") or "").strip() or None
        weight_kg = (request.form.get("weight_kg") or "").strip() or None
        goal_text = (request.form.get("goal_text") or "").strip() or None
        goal_weight_kg = (request.form.get("goal_weight_kg") or "").strip() or None

        quick_notes = request.form.getlist("quick_notes")
        quick_notes_json = json.dumps(quick_notes, ensure_ascii=False) if quick_notes else None

        with get_db() as conn:
            existing = conn.execute(
                "SELECT * FROM profile ORDER BY id DESC LIMIT 1" #take the latest profile as the "current" one
            ).fetchone()

            if existing:
                existing_quick = existing["quick_notes_json"] if "quick_notes_json" in existing.keys() else None

                # Merge: use incoming values when present, otherwise keep existing.
                merged = {
                    "name": name or existing["name"],
                    "age": age if age is not None else existing["age"],
                    "height_cm": height_cm if height_cm is not None else existing["height_cm"],
                    "weight_kg": weight_kg if weight_kg is not None else existing["weight_kg"],
                    "goal_text": goal_text if goal_text is not None else existing["goal_text"],
                    "goal_weight_kg": goal_weight_kg if goal_weight_kg is not None else existing["goal_weight_kg"],
                    "quick_notes_json": quick_notes_json if quick_notes_json is not None else existing_quick,
                }

                if merged["name"]:
                    conn.execute(
                        #always have a single profile row - update the existing one instead of inserting new
                        """UPDATE profile 
                           SET name=?, age=?, height_cm=?, weight_kg=?, goal_text=?, goal_weight_kg=?, quick_notes_json=?
                           WHERE id=?""",
                        (
                            merged["name"],
                            merged["age"],
                            merged["height_cm"],
                            merged["weight_kg"],
                            merged["goal_text"],
                            merged["goal_weight_kg"],
                            merged["quick_notes_json"],
                            existing["id"],
                        ),
                    )
                    conn.commit()
            else:
                if name:
                    conn.execute(
                        """INSERT INTO profile
                           (name, age, height_cm, weight_kg, goal_text, goal_weight_kg, quick_notes_json)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (name, age, height_cm, weight_kg, goal_text, goal_weight_kg, quick_notes_json),
                    )
                    conn.commit()

        return redirect(url_for("profile.page"))

    with get_db() as conn:
        profile = conn.execute(
            "SELECT * FROM profile ORDER BY id DESC LIMIT 1"
        ).fetchone()

    return render_template("profile.html", active="profile", profile=profile)

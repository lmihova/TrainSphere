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
        # Read values (empty string -> None)
        name = (request.form.get("name") or "").strip() or None
        age = (request.form.get("age") or "").strip() or None
        height_cm = (request.form.get("height_cm") or "").strip() or None
        weight_kg = (request.form.get("weight_kg") or "").strip() or None
        goal_text = (request.form.get("goal_text") or "").strip() or None
        goal_weight_kg = (request.form.get("goal_weight_kg") or "").strip() or None

        # IMPORTANT: if user unchecks all -> clear in DB
        quick_notes = request.form.getlist("quick_notes")
        quick_notes_json = json.dumps(quick_notes, ensure_ascii=False) if quick_notes else None

        with get_db() as conn:
            existing = conn.execute(
                "SELECT * FROM profile ORDER BY id DESC LIMIT 1"
            ).fetchone()

            if existing:
                # Keep existing name if user left it blank (because name is NOT NULL)
                final_name = name if name is not None else existing["name"]

                conn.execute(
                    """UPDATE profile
                       SET name=?, age=?, height_cm=?, weight_kg=?, goal_text=?, goal_weight_kg=?, quick_notes_json=?
                       WHERE id=?""",
                    (
                        final_name,
                        age,              # allow None -> clears field
                        height_cm,         # allow None -> clears field
                        weight_kg,         # allow None -> clears field
                        goal_text,         # allow None -> clears field
                        goal_weight_kg,    # allow None -> clears field
                        quick_notes_json,  # allow None -> clears notes
                        existing["id"],
                    ),
                )
                conn.commit()
            else:
                # Create only if name exists (required)
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

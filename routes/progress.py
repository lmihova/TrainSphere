from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

progress_bp = Blueprint("progress", __name__, url_prefix="/progress")
DB_PATH = Path(__file__).resolve().parents[1] / "trainsphere.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _derive_category(workout_type: str) -> str:
    wt = (workout_type or "").strip().lower()
    if wt.startswith("strength"):
        return "Strength"
    if wt.startswith("cardio"):
        return "Cardio"
    if wt.startswith("hiit"):
        return "HIIT"
    if "yoga" in wt or "mobility" in wt:
        return "Mobility"
    return (workout_type or "General").split("(")[0].strip() or "General"


def _parse_date(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except Exception:
        return None


def _compute_period(period: str):
    today = date.today()
    p = (period or "week").strip().lower()

    if p == "month":
        f = today.replace(day=1)
        if f.month == 12:
            next_month = f.replace(year=f.year + 1, month=1) # set to next month first, handle December correctly
        else:
            next_month = f.replace(month=f.month + 1)
        t = next_month - timedelta(days=1)
    else:
        f = today - timedelta(days=6) # default to week (7-day period ending today)
        t = today

    return f.isoformat(), t.isoformat() #date object в string


WORKOUT_TEMPLATES = {
    "Strength (Upper)": [
        {"name": "Incline Bench Press (Dumbbell)", "sets": 3, "reps": 12, "weight_kg": 28},
        {"name": "Lat Pulldown", "sets": 3, "reps": 12, "weight_kg": 35},
        {"name": "Dumbbell Shoulder Press", "sets": 3, "reps": 10, "weight_kg": 14},
    ],
    "Strength (Lower)": [
        {"name": "Squats", "sets": 4, "reps": 8, "weight_kg": 40},
        {"name": "Deadlifts", "sets": 3, "reps": 6, "weight_kg": 50},
        {"name": "Leg Press", "sets": 3, "reps": 12, "weight_kg": 80},
    ],
    "Cardio": [
        {"name": "Treadmill", "sets": 1, "reps": 20, "weight_kg": 0},
        {"name": "Bike", "sets": 1, "reps": 15, "weight_kg": 0},
    ],
    "HIIT": [
        {"name": "Burpees", "sets": 4, "reps": 10, "weight_kg": 0},
        {"name": "Jump Squats", "sets": 4, "reps": 12, "weight_kg": 0},
        {"name": "Mountain Climbers", "sets": 4, "reps": 30, "weight_kg": 0},
    ],
    "Mobility / Yoga": [
        {"name": "Yoga flow", "sets": 1, "reps": 20, "weight_kg": 0},
        {"name": "Stretching", "sets": 1, "reps": 15, "weight_kg": 0},
    ],
}


@progress_bp.route("", methods=["GET", "POST"])
def page():
    def to_int(x, default=None):
        try:
            return int(x)
        except:
            return default

    def to_float(x, default=None):
        try:
            return float(x)
        except:
            return default

    
    edit_id_raw = request.args.get("edit")
    edit_id = None
    try:
        if edit_id_raw:
            edit_id = int(edit_id_raw)
    except:
        edit_id = None

    if request.method == "POST":
        # If hidden workout_id is present -> update, else insert
        workout_id_raw = request.form.get("workout_id")
        workout_id = None
        try:
            if workout_id_raw:
                workout_id = int(workout_id_raw)
        except:
            workout_id = None

        workout_type = request.form.get("workout_type") or "Strength (Upper)"
        category = (request.form.get("category") or "").strip() or _derive_category(workout_type)
        duration_minutes = request.form.get("duration_minutes") or None
        notes = (request.form.get("notes") or "").strip()
        workout_date = _parse_date(request.form.get("workout_date")) or date.today().isoformat()

        performance_rating = to_int(request.form.get("performance_rating"), None)
        feeling_rating = to_int(request.form.get("feeling_rating"), None)

        names = request.form.getlist("exercise_name[]")
        sets_list = request.form.getlist("sets[]")
        reps_list = request.form.getlist("reps[]")
        weights_list = request.form.getlist("weight_kg[]")

        with get_db() as conn:
            if workout_id:  # UPDATE
                conn.execute(
                    """UPDATE workouts
                       SET workout_date=?, workout_type=?, category=?, duration_minutes=?,
                           performance_rating=?, feeling_rating=?, notes=?
                       WHERE id=?""",
                    (
                        workout_date,
                        workout_type,
                        category,
                        duration_minutes,
                        performance_rating,
                        feeling_rating,
                        notes,
                        workout_id,
                    ),
                )

                
                #? е placeholder (parameter marker) в SQLite
                conn.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))

                for i, name in enumerate(names):
                    name = (name or "").strip()
                    if not name:
                        continue
                    s = to_int(sets_list[i] if i < len(sets_list) else None, None)
                    r = to_int(reps_list[i] if i < len(reps_list) else None, None)
                    w = to_float(weights_list[i] if i < len(weights_list) else None, None)
                    conn.execute(
                        """INSERT INTO workout_exercises (workout_id, exercise_name, sets, reps, weight_kg)
                           VALUES (?, ?, ?, ?, ?)""",
                        (workout_id, name, s, r, w),
                    )

            else:  
                cur = conn.execute(
                    """INSERT INTO workouts (workout_date, workout_type, category, duration_minutes, performance_rating, feeling_rating, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (workout_date, workout_type, category, duration_minutes, performance_rating, feeling_rating, notes),
                )
                new_id = cur.lastrowid

                for i, name in enumerate(names):
                    name = (name or "").strip()
                    if not name:
                        continue
                    s = to_int(sets_list[i] if i < len(sets_list) else None, None)
                    r = to_int(reps_list[i] if i < len(reps_list) else None, None)
                    w = to_float(weights_list[i] if i < len(weights_list) else None, None)
                    conn.execute(
                        """INSERT INTO workout_exercises (workout_id, exercise_name, sets, reps, weight_kg)
                           VALUES (?, ?, ?, ?, ?)""",
                        (new_id, name, s, r, w),
                    )

            conn.commit()

        return redirect(url_for("progress.page"))

    # --- GET: list + (optional) edit data ---
    period = request.args.get("period", "week")
    category_f = (request.args.get("category") or "").strip()
    date_from, date_to = _compute_period(period)
    order_by = "workout_date DESC, id DESC"

    with get_db() as conn:
        categories = [r[0] for r in conn.execute(
            "SELECT DISTINCT COALESCE(category, '') FROM workouts WHERE COALESCE(category,'') <> '' ORDER BY 1"
        ).fetchall()]
        if not categories:
            categories = ["Strength", "Cardio", "HIIT", "Mobility", "General"]
        else:
            for c in ["Strength", "Cardio", "HIIT", "Mobility", "General"]:
                if c not in categories:
                    categories.append(c)

        where = ["workout_date BETWEEN ? AND ?"]
        params = [date_from, date_to]
        if category_f:
            where.append("COALESCE(category,'') = ?")
            params.append(category_f)

        recent = conn.execute(
            f"""
            SELECT w.id, w.workout_date, w.workout_type, w.category,
                   w.duration_minutes, w.performance_rating, w.feeling_rating, w.notes
            FROM workouts w
            WHERE {' AND '.join(where)}
            ORDER BY {order_by}
            LIMIT 50
            """,
            params,
        ).fetchall()

        # load exercises for list
        recent_ex = {}
        if recent:
            ids = [r["id"] for r in recent]
            q_marks = ",".join(["?"] * len(ids))
            ex_rows = conn.execute(
                f"""
                SELECT workout_id, exercise_name, sets, reps, weight_kg
                FROM workout_exercises
                WHERE workout_id IN ({q_marks})
                ORDER BY workout_id DESC, id ASC
                """,
                ids,
            ).fetchall()
            for ex in ex_rows:
                recent_ex.setdefault(ex["workout_id"], []).append(ex)

        # optional edit payload
        edit_workout = None
        edit_exercises = []
        if edit_id:
            edit_workout = conn.execute(
                """SELECT id, workout_date, workout_type, category, duration_minutes,
                          performance_rating, feeling_rating, notes
                   FROM workouts WHERE id=?""",
                (edit_id,),
            ).fetchone()
            if edit_workout:
                edit_exercises = conn.execute(
                    """SELECT exercise_name, sets, reps, weight_kg
                       FROM workout_exercises
                       WHERE workout_id=?
                       ORDER BY id ASC""",
                    (edit_id,),
                ).fetchall()

    return render_template(
        "progress.html",
        active="progress",
        workout_templates=WORKOUT_TEMPLATES,
        categories=categories,
        filters={"period": period, "category": category_f},
        recent=recent,
        recent_ex=recent_ex,
        edit_workout=edit_workout,
        edit_exercises=edit_exercises,
    )


@progress_bp.route("/delete/<int:workout_id>", methods=["POST"])
def delete(workout_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM workout_exercises WHERE workout_id = ?", (workout_id,))
        conn.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))
        conn.commit()
    return redirect(url_for("progress.page"))

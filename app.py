from flask import Flask, render_template, Blueprint, request, redirect, url_for
import sqlite3
from pathlib import Path
from datetime import date

app = Flask(__name__)
app.url_map.strict_slashes = False

DB_PATH = Path(__file__).with_name("trainsphere.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as connecion:
        cur = connecion.cursor()

        # PROFILE
        cur.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            height_cm INTEGER,
            weight_kg REAL,
            goal_text TEXT,
            goal_weight_kg REAL,
            quick_notes_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

       #keep existing DBs working
        profile_cols = [r[1] for r in cur.execute("PRAGMA table_info(profile)").fetchall()]
        if "quick_notes_json" not in profile_cols:
            cur.execute("ALTER TABLE profile ADD COLUMN quick_notes_json TEXT")

        # PLANS
        cur.execute("""
        CREATE TABLE IF NOT EXISTS custom_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_type TEXT NOT NULL,
            frequency_per_week INTEGER NOT NULL,
            goal_type TEXT NOT NULL,
            goal_value INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # GOALS - Home page
        cur.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            target_value INTEGER NOT NULL,
            target_unit TEXT NOT NULL,
            target_date TEXT,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Progress page
        cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_date TEXT DEFAULT CURRENT_DATE,
            workout_type TEXT NOT NULL,
            category TEXT,
            duration_minutes INTEGER,
            performance_rating INTEGER,
            feeling_rating INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # keep existing DBs working
        cols = [r[1] for r in cur.execute("PRAGMA table_info(workouts)").fetchall()]
        if "category" not in cols:
            cur.execute("ALTER TABLE workouts ADD COLUMN category TEXT")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight_kg REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (workout_id) REFERENCES workouts(id)
        )
        """)

        connecion.commit()


init_db()

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        metric = (request.form.get("metric") or "steps").strip().lower()
        unit = (request.form.get("target_unit") or "steps/day").strip()
        tdate = (request.form.get("target_date") or "").strip()
        note = (request.form.get("note") or "").strip()

        try:
            target_value = int(request.form.get("target_value") or "0")
        except ValueError:
            target_value = 0

        if target_value > 0 and metric and unit:
            with get_db() as conn:
                conn.execute(
                    """INSERT INTO goals (metric, target_value, target_unit, target_date, note)
                       VALUES (?, ?, ?, ?, ?)""",
                    (metric, target_value, unit, tdate, note),
                )
                conn.commit()

        return redirect(url_for("main.index"))

    with get_db() as conn:
        steps_goal = conn.execute(
            "SELECT * FROM goals WHERE metric='steps' ORDER BY id DESC LIMIT 1"
        ).fetchone()

        recent_goals = conn.execute(
            "SELECT * FROM goals ORDER BY id DESC LIMIT 5"
        ).fetchall()

    return render_template(
        "index.html",
        active="home",
        now_date=date.today().strftime("%d/%m/%Y"),
        steps_goal=steps_goal,
        recent_goals=recent_goals,
    )


app.register_blueprint(main)

# Blueprints
from routes.profile import profile_bp
from routes.plans import plans_bp
from routes.progress import progress_bp
from routes.motivation import motivation_bp
from routes.report import report_bp

app.register_blueprint(profile_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(motivation_bp)
app.register_blueprint(report_bp)

if __name__ == "__main__":
    app.run(debug=True)

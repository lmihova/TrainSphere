from flask import Blueprint, render_template, request, send_file
import sqlite3
from pathlib import Path
import io
import csv
import json

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _register_fonts():
    
    try:
        pdfmetrics.getFont("TrainSphereFont")
        pdfmetrics.getFont("TrainSphereFont-Bold")
        return True
    except Exception:
        pass

    regular_candidates = [
        # Linux
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        # Windows
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
        # macOS
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Helvetica.ttf"),
    ]
    bold_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Helvetica Bold.ttf"),
    ]

    regular_path = next((p for p in regular_candidates if p.exists()), None)
    bold_path = next((p for p in bold_candidates if p.exists()), None)

    if not regular_path:
        return False

    try:
        pdfmetrics.registerFont(TTFont("TrainSphereFont", str(regular_path)))
        if bold_path:
            pdfmetrics.registerFont(TTFont("TrainSphereFont-Bold", str(bold_path)))
        else:
            pdfmetrics.registerFont(TTFont("TrainSphereFont-Bold", str(regular_path)))
        return True
    except Exception:
        return False


report_bp = Blueprint("report", __name__, url_prefix="/report")
DB_PATH = Path(__file__).resolve().parents[1] / "trainsphere.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_report(limit_workouts: int = 20):
    """Fetch data needed for exports.

    We keep Profile + Plan as the latest rows.
    For Progress we export multiple workouts 
    """
    with get_db() as conn:
        profile = conn.execute(
            "SELECT * FROM profile ORDER BY id DESC LIMIT 1"
        ).fetchone()

        plan = conn.execute(
            "SELECT * FROM custom_plan ORDER BY id DESC LIMIT 1"
        ).fetchone()

        workouts = conn.execute(
            """SELECT id, workout_date, workout_type, duration_minutes,
                      performance_rating, feeling_rating, notes
               FROM workouts
               ORDER BY id DESC
               LIMIT ?""",
            (limit_workouts,),
        ).fetchall()

        exercises_by_workout = {}
        for w in workouts:
            exercises_by_workout[w["id"]] = conn.execute(
                """SELECT exercise_name, sets, reps, weight_kg
                   FROM workout_exercises
                   WHERE workout_id=?
                   ORDER BY id""",
                (w["id"],),
            ).fetchall()

    # Parse checked checklist / quick notes (stored as JSON arrays)
    checklist = []
    if plan and "checklist_json" in plan.keys() and plan["checklist_json"]:
        try:
            checklist = json.loads(plan["checklist_json"]) or []
        except Exception:
            checklist = []
    quick_notes = []
    if profile and "quick_notes_json" in profile.keys() and profile["quick_notes_json"]:
        try:
            quick_notes = json.loads(profile["quick_notes_json"]) or []
        except Exception:
            quick_notes = []

    return profile, plan, workouts, exercises_by_workout, checklist, quick_notes


@report_bp.route("", methods=["GET"])
def page():
    return render_template("report.html", active="report")


@report_bp.route("/export", methods=["GET"])
def export():
    format = (request.args.get("format") or "none").lower()
    profile, plan, workouts, exercises_by_workout, checklist, quick_notes = fetch_report()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["TrainSphere Report"])
        writer.writerow([])

        writer.writerow(["PROFILE"])
        if profile:
            writer.writerow(["Name", profile["name"]])
            writer.writerow(["Age", profile["age"]])
            writer.writerow(["Height_cm", profile["height_cm"]])
            writer.writerow(["Weight_kg", profile["weight_kg"]])
            writer.writerow(["Goal_text", profile["goal_text"]])
            writer.writerow(["Goal_weight_kg", profile["goal_weight_kg"]])
        else:
            writer.writerow(["No profile data"])

        writer.writerow([])
        writer.writerow(["PLAN"])
        if plan:
            writer.writerow(["Workout_type", plan["workout_type"]])
            writer.writerow(["Frequency_per_week", plan["frequency_per_week"]])
            writer.writerow(["Goal_type", plan["goal_type"]])
            writer.writerow(["Goal_value", plan["goal_value"]])
        else:
            writer.writerow(["No plan data"])

        writer.writerow([])
        writer.writerow(["CHECKLIST"])
        if checklist:
            for item in checklist:
                writer.writerow([item])
        else:
            writer.writerow(["(none)"])

        writer.writerow([])
        writer.writerow(["QUICK NOTES"])
        if quick_notes:
            for item in quick_notes:
                writer.writerow([item])
        else:
            writer.writerow(["(none)"])

        writer.writerow([])
        writer.writerow(["WORKOUTS (latest first)"])
        if workouts:
            writer.writerow([
                "Workout_id",
                "Date",
                "Type",
                "Duration_minutes",
                "Performance_rating",
                "Feeling_rating",
                "Notes",
            ])
            for w in workouts:
                writer.writerow([
                    w["id"],
                    w["workout_date"],
                    w["workout_type"],
                    w["duration_minutes"],
                    w["performance_rating"],
                    w["feeling_rating"],
                    w["notes"],
                ])
        else:
            writer.writerow(["No workout data"])

        writer.writerow([])
        writer.writerow(["EXERCISES"])
        writer.writerow(["Workout_id", "Exercise", "Sets", "Reps", "Weight_kg"])
        for w in workouts:
            for ex in exercises_by_workout.get(w["id"], []):
                writer.writerow([w["id"], ex["exercise_name"], ex["sets"], ex["reps"], ex["weight_kg"]])


        #important for the download to have UTF-8 so Excel recognizes encoding and shows non-ASCII chars correctly
        mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
        mem.seek(0)
        return send_file(
            mem,
            mimetype="text/csv",
            as_attachment=True,
            download_name="trainsphere_report.csv",
        )

    if format == "pdf":
        has_unicode = _register_fonts()
        mem = io.BytesIO()
        canva = canvas.Canvas(mem, pagesize=A4)
        width, height = A4

        font = "TrainSphereFont" if has_unicode else "Helvetica"
        font_bold = "TrainSphereFont-Bold" if has_unicode else "Helvetica-Bold"

        y = height - 60
        canva.setFont(font_bold, 18)
        canva.drawString(50, y, "TrainSphere Report")
        y -= 30

        canva.setFont(font_bold, 12)
        canva.drawString(50, y, "PROFILE")
        y -= 18
        canva.setFont(font, 11)

        if profile:
            lines = [
                f"Name: {profile['name']}",
                f"Age: {profile['age']}",
                f"Height (cm): {profile['height_cm']}",
                f"Weight (kg): {profile['weight_kg']}",
                f"Goal: {profile['goal_text']}",
                f"Goal weight (kg): {profile['goal_weight_kg']}",
            ]
        else:
            lines = ["No profile data"]

        for line in lines:
            canva.drawString(50, y, line)
            y -= 15

        y -= 10
        canva.setFont(font_bold, 12)
        canva.drawString(50, y, "PLAN")
        y -= 18
        canva.setFont(font, 11)

        if plan:
            lines = [
                f"Workout type: {plan['workout_type']}",
                f"Frequency / week: {plan['frequency_per_week']}",
                f"Goal type: {plan['goal_type']}",
                f"Goal value: {plan['goal_value']}",
            ]
        else:
            lines = ["No plan data"]

        for line in lines:
            canva.drawString(50, y, line)
            y -= 15

        y -= 10
        canva.setFont(font_bold, 12)
        canva.drawString(50, y, "CHECKLIST")
        y -= 18
        canva.setFont(font, 11)
        if checklist:
            for item in checklist:
                canva.drawString(60, y, f"- {item}")
                y -= 14
        else:
            canva.drawString(60, y, "- (none)")
            y -= 14

        y -= 8
        canva.setFont(font_bold, 12)
        canva.drawString(50, y, "QUICK NOTES")
        y -= 18
        canva.setFont(font, 11)
        if quick_notes:
            for item in quick_notes:
                canva.drawString(60, y, f"- {item}")
                y -= 14
        else:
            canva.drawString(60, y, "- (none)")
            y -= 14

        y -= 10
        canva.setFont(font_bold, 12)
        canva.drawString(50, y, "WORKOUTS (latest first)")
        y -= 18
        canva.setFont(font, 11)

        if not workouts:
            canva.drawString(50, y, "No workout data")
            y -= 15
        else:
            for w in workouts:
                header = f"{w['workout_date']} — {w['workout_type']}"
                meta = []
                if w["duration_minutes"]:
                    meta.append(f"{w['duration_minutes']} min")
                if w["performance_rating"] is not None:
                    meta.append(f"perf {w['performance_rating']}/10")
                if w["feeling_rating"] is not None:
                    meta.append(f"feel {w['feeling_rating']}/10")

                canva.setFont(font_bold, 11)
                canva.drawString(50, y, header)
                y -= 14
                canva.setFont(font, 11)
                if meta:
                    canva.drawString(50, y, " · ".join(meta))
                    y -= 14
                if w["notes"]:
                    canva.drawString(50, y, f"Notes: {w['notes']}")
                    y -= 14

                ex_list = exercises_by_workout.get(w["id"], [])
                for ex in ex_list:
                    line = f"- {ex['exercise_name']}  ({ex['sets']}x{ex['reps']}, {ex['weight_kg']}kg)"
                    canva.drawString(60, y, line)
                    y -= 14

                y -= 6
                if y < 80:
                    canva.showPage()
                    y = height - 60
                    canva.setFont(font, 11)

        canva.showPage()
        canva.save()
        mem.seek(0)

        return send_file(
            mem,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="trainsphere_report.pdf",
        )

    # if none or unknown
    return render_template("report.html", active="report")

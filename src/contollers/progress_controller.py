from flask import Flask, request, jsonify
from classes.user import User
from services.file_manager import save_data, load_data
from services.calculations import calculate_bmi, calculate_calories, calculate_macros, calculate_target_calories

app = Flask(__name__)  

WORKOUT_FILE = "data/progress.json"

@app.route("/workout/add", methods=["POST"])
def add_workout():
    """Logs a workout session for a user."""
    data = request.json
    required_fields = ["username", "workout_type", "duration", "weight", "intensity"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required workout details"}), 400

    user_data = User.load_users()
    if data["username"] not in user_data:
        return jsonify({"error": "User not found"}), 404

    calories_burned = calculate_calories(data["weight"], data["duration"], data["intensity"])

    workout_entry = {
        "username": data["username"],
        "workout_type": data["workout_type"],
        "duration": data["duration"],
        "calories_burned": calories_burned,
    }

    save_data(workout_entry, WORKOUT_FILE)

    return jsonify({"message": "Workout logged successfully", "calories_burned": calories_burned}), 201


@app.route("/progress/<username>", methods=["GET"])
def get_progress(username):
    """Retrieve user workout progress and fitness metrics."""
    users = User.load_users()
    workouts = load_data(WORKOUT_FILE)

    if username not in users:
        return jsonify({"error": "User not found"}), 404

    user_data = users[username]
    user_workouts = [w for w in workouts if w["username"] == username]

    bmi = calculate_bmi(user_data["weight"], user_data["height"])
    target_calories = calculate_target_calories(user_data["weight"], user_data["goal"])
    macros = calculate_macros(user_data["weight"], user_data["goal"])

    response = {
        "username": username,
        "bmi": bmi,
        "target_daily_calories": target_calories,
        "macros": macros,
        "workout_history": user_workouts,
    }

    return jsonify(response), 200

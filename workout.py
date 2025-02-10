from flask import Flask, request, jsonify
from user import User
from services.file_manager import save_data

app = Flask(__name__)

class Workout:
    PREDEFINED_WORKOUTS = {
        "Strength Training": ["Weightlifting", "Calisthenics", "Powerlifting", "Bodybuilding"],
        "Cardio": ["Running", "Cycling", "Rowing", "Jump Rope"],
        "Functional": ["CrossFit", "HIIT"],
        "Flexibility & Mobility": ["Yoga", "Pilates", "Stretching"],
        "Sport-Specific": ["Martial Arts", "Swimming", "Football Training"],
        "Rehabilitation": ["Physiotherapy", "Light Gymnastics", "Aerobics"]
    }

    def __init__(self, workout_type, duration, calories_burned):
        self.workout_type = self.validate_workout_type(workout_type)
        self.duration = duration
        self.calories_burned = calories_burned

    def validate_workout_type(self, workout_type):
        for types in self.PREDEFINED_WORKOUTS.items():
            if workout_type in types:
                return workout_type
        raise ValueError(f"Invalid workout type: {workout_type}. Choose from predefined workouts.")

    def to_dict(self):
        return {
            "workout_type": self.workout_type,
            "duration": self.duration,
            "calories_burned": self.calories_burned
        }

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user = User(data["username"], data["age"], data["weight"], data["height"], data["goal"])
    save_data(user.to_dict(), "data/user.json")
    return jsonify({"message": "User registered successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)

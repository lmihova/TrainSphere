from services.file_manager import load_data, save_data
from services.calculations import (
    calculate_bmi,
    calculate_calories,
    calculate_target_calories,
    calculate_macros,
    suggest_intensity
)

class Progress:
    
    WORKOUT_FILE = "data/workout.json"
    USER_FILE = "data/user.json"

    def __init__(self, username):
        self.username = username
        self.user_data = self.load_user()
        self.workout_history = self.load_workout_history()

    def load_user(self):
        """Loads user data from user.json."""
        users = load_data(self.USER_FILE)
        if self.username not in users:
            raise ValueError("User not found.")
        return users[self.username]

    def load_workout_history(self):
        """Loads user's workout history from workout.json."""
        workouts = load_data(self.WORKOUT_FILE)
        return [w for w in workouts if w["username"] == self.username]

    def calculate_bmi(self):
        """Calculates and returns the user's BMI."""
        return calculate_bmi(self.user_data["weight"], self.user_data["height"])

    def calculate_target_calories(self):
        """Estimates the user's daily calories needs based on fitness goal."""
        return calculate_target_calories(self.user_data["weight"], self.user_data["goal"])

    def calculate_macros(self):
        """Estimates daily macronutrient needs."""
        return calculate_macros(self.user_data["weight"], self.user_data["goal"])

    def suggest_intensity(self, activity_type):
        """Suggests an intensity level based on workout type."""
        return suggest_intensity(activity_type)

    def add_workout(self, workout_type, duration):

        intensity = self.suggest_intensity(workout_type)
        calories_burned = calculate_calories(self.user_data["weight"], duration, intensity)

        new_workout = {
            "username": self.username,
            "workout_type": workout_type,
            "duration": duration,
            "calories_burned": calories_burned
        }

        save_data(new_workout, self.WORKOUT_FILE)
        self.workout_history.append(new_workout)
        return f"Workout added successfully. Calories burned: {calories_burned}"

    def get_progress_report(self):
        """Returns a summary of the user's progress, workouts, and fitness metrics."""
        return {
            "username": self.username,
            "bmi": self.calculate_bmi(),
            "target_daily_calories": self.calculate_target_calories(),
            "macros": self.calculate_macros(),
            "workout_history": self.workout_history
        }

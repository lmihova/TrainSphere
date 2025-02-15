import pytest
from classes.workout import Workout


def test_valid_workout():
    workout = Workout("Running", 30, 300)
    assert workout.workout_type == "Running"
    assert workout.duration == 30
    assert workout.calories_burned == 300


def test_invalid_workout():
    with pytest.raises(ValueError, match="Invalid workout type: InvalidWorkout. Choose from predefined workouts."):
        Workout("InvalidWorkout", 30, 300)


def test_workout_to_dict():
    workout = Workout("Cycling", 45, 400)
    workout_dict = workout.to_dict()
    assert workout_dict == {
        "workout_type": "Cycling",
        "duration": 45,
        "calories_burned": 400
    }

from typing import Dict

def calculate_calories(weight: float, duration: float, intensity: float) -> float:
    """
    Calculates the estimated calories burned.
    """
    return round(weight * duration * intensity, 2)

def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculates the Body Mass Index (BMI).
    """
    if height <= 0:
        raise ValueError("Height must be greater than zero.")
    return round(weight / (height ** 2), 2)

def suggest_intensity(activity_type: str) -> float:
    """
    Suggests an intensity multiplier based on the type of workout.
    """
    intensity_levels: Dict[str, float] = {
        "light": 3.0,
        "moderate": 5.0,
        "intense": 8.0
    }
    return intensity_levels.get(activity_type.lower(), 5.0)  # Default 

def calculate_target_calories(weight: float, goal: str) -> float:
    """
    Calculates target daily calorie burn based on a fitness goal.
    """
    goal_multiplier: Dict[str, float] = {
        "weight loss": 1.2,
        "maintenance": 1.0,
        "muscle gain": 1.5
    }
    return round(weight * 30 * goal_multiplier.get(goal.lower(), 1.0), 2)

def calculate_macros(weight: float, goal: str) -> Dict[str, float]:
    """
    Estimates daily macronutrient needs (carbs, protein, fats) in grams.
    """
    goal_ratios: Dict[str, Dict[str, float]] = {
        "weight loss": {"carbs": 0.4, "protein": 0.4, "fats": 0.2},
        "maintenance": {"carbs": 0.5, "protein": 0.3, "fats": 0.2},
        "muscle gain": {"carbs": 0.5, "protein": 0.35, "fats": 0.15}
    }
    ratios = goal_ratios.get(goal.lower(), goal_ratios["maintenance"])
    total_calories = calculate_target_calories(weight, goal)
    return {
        "carbs": round((total_calories * ratios["carbs"]) / 4, 2),
        "protein": round((total_calories * ratios["protein"]) / 4, 2),
        "fats": round((total_calories * ratios["fats"]) / 9, 2)
    }

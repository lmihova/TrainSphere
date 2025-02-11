import pytest
from services.calculations import calculate_calories, calculate_bmi, suggest_intensity, calculate_target_calories, calculate_macros

def test_calculate_calories():
    assert calculate_calories(70, 1, 5) == 350.0
    assert calculate_calories(80, 0.5, 3) == 120.0
    assert calculate_calories(60, 2, 8) == 960.0

def test_calculate_bmi():
    assert calculate_bmi(70, 1.75) == 22.86
    assert calculate_bmi(80, 1.8) == 24.69
    with pytest.raises(ValueError, match="Height must be greater than zero."):
        calculate_bmi(70, 0)

def test_suggest_intensity():
    assert suggest_intensity("light") == 3.0
    assert suggest_intensity("moderate") == 5.0
    assert suggest_intensity("intense") == 8.0
    assert suggest_intensity("unknown") == 5.0  # Default case

def test_calculate_target_calories():
    assert calculate_target_calories(70, "weight loss") == 2520.0
    assert calculate_target_calories(70, "maintenance") == 2100.0
    assert calculate_target_calories(70, "muscle gain") == 3150.0
    assert calculate_target_calories(70, "unknown") == 2100.0  # Default case

def test_calculate_macros():
    macros = calculate_macros(70, "weight loss")
    assert macros["carbs"] == 252.0
    assert macros["protein"] == 252.0
    assert macros["fats"] == 56.0
    
    macros = calculate_macros(70, "maintenance")
    assert macros["carbs"] == 262.5
    assert macros["protein"] == 157.5
    assert macros["fats"] == 46.67
    
    macros = calculate_macros(70, "muscle gain")
    assert macros["carbs"] == 393.75
    assert macros["protein"] == 275.63
    assert macros["fats"] == 52.5

from flask import Flask, request, jsonify  
from models.user import User
from services.file_manager import save_data, load_data
from services.calculations import calculate_bmi, calculate_calories, calculate_target_calories, calculate_macros

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    if "username" not in data or "email" not in data or "age" not in data or "weight" not in data or "height" not in data or "goal" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    user = User(data["username"], data["email"], data["age"], data["weight"], data["height"], data["goal"], data["password"])
    save_data(user.to_dict(), "data/users.json")
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/bmi", methods=["POST"])
def bmi():
    data = request.json
    if "weight" not in data or "height" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        bmi_value = calculate_bmi(data["weight"], data["height"])
        return jsonify({"bmi": bmi_value}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/calories", methods=["POST"])
def calories():
    data = request.json
    if "weight" not in data or "duration" not in data or "intensity" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    calories_burned = calculate_calories(data["weight"], data["duration"], data["intensity"])
    return jsonify({"calories_burned": calories_burned}), 200

@app.route("/target_calories", methods=["POST"])
def target_calories():
    data = request.json
    if "weight" not in data or "goal" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    target = calculate_target_calories(data["weight"], data["goal"])
    return jsonify({"target_calories": target}), 200

@app.route("/macros", methods=["POST"])
def macros():
    data = request.json
    if "weight" not in data or "goal" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    macros_values = calculate_macros(data["weight"], data["goal"])
    return jsonify(macros_values), 200

if __name__ == "__main__":
    app.run(debug=True)

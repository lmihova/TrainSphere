from flask import Flask, request, jsonify
from classes.user import User

app = Flask(__name__)  # Define the Flask app

# File where user data is stored
USER_FILE = "data/user.json"

@app.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.json

    # Validate required fields
    required_fields = ["username", "email", "age", "weight", "height", "goal", "password"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Create user object
    user = User(
        username=data["username"],
        email=data["email"],
        age=data["age"],
        weight=data["weight"],
        height=data["height"],
        goal=data["goal"],
        password=data["password"],
    )

    # Save user
    message = user.register(USER_FILE)
    if "successful" in message:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


@app.route("/login", methods=["POST"])
def login():
    """User login authentication."""
    data = request.json
    if "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    user = User(username=data["username"], email="", age=0, weight=0, height=0, goal="", password=data["password"])
    message = user.login(USER_FILE)

    if "successful" in message:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 401


@app.route("/users", methods=["GET"])
def get_users():
    """Retrieve all registered users (excluding passwords)."""
    users = User.load_users(USER_FILE)
    users_sanitized = {username: {k: v for k, v in data.items() if k != "password"} for username, data in users.items()}
    return jsonify(users_sanitized), 200

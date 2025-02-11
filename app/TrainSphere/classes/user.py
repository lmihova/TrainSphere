import json
import os
from validation import validate_password


class User:
    def __init__(self, username, email, age, weight, height, goal, password):
                
        self.username = username
        self.email = email
        self.age = age
        self.weight = weight
        self.height = height
        self.goal = goal
        self.password = validate_password(password)

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "age": self.age,
            "weight": self.weight,
            "height": self.height,
            "goal": self.goal,
            "password": self.password  
        }

    def save_to_file(self, filename="data/.json"):
        users = User.load_users(filename)
        users[self.username] = self.to_dict()
        with open(filename, "w") as file:
            json.dump(users, file, indent=4)

    def register(self, filename="data/user.json"):
        users = User.load_users(filename)
        if self.username in users:
            return "Username already exists. Choose a different one."
        if not validate_password(self.password):
            return "Password must be at least 8 characters long, include a capital letter, a lower letter, a digit and a special character."
        self.save_to_file(filename)
        return "Registration successful."

    def login(self, filename="data/user.json"):
        users = User.load_users(filename)
        if self.username not in users:
            return "Invalid username or password."
        if users[self.username]["password"] != self.password:
            return "Invalid username or password."
        return "Login successful."

    @staticmethod
    def load_users(filename="data/user.json"):
        if not os.path.exists(filename):
            return {}
        with open(filename, "r") as file:
            return json.load(file)

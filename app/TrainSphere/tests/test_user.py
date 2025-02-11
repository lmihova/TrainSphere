import unittest
from classes.user import User


class TestUser(unittest.TestCase):
    def setUp(self):
        self.data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "age": 25,
            "weight": 70,
            "height": 175,
            "goal": "lose weight",
            "password": "StrongPass1!"
        }

    def test_to_dict(self):
        user = User(**self.data) #create dynamically 
        user_dict = user.to_dict()
        self.assertEqual(user_dict["username"], self.data["username"])
        self.assertEqual(user_dict["email"], self.data["email"])
        self.assertEqual(user_dict["age"], self.data["age"])

    def test_register_successful(self):
        user = User(**self.data)
        result = user.register()
        self.assertEqual(result, "Registration successful.")

    def test_register_existing_user(self):
        user = User(**self.data)
        user.save_to_file()
        duplicate_user = User(**self.data)
        result = duplicate_user.register()
        self.assertEqual(result, "Username already exists. Choose a different one.")

    def test_register_invalid_password(self):
        self.data["password"] = "weak"
        result = User(**self.data).register()
        self.assertEqual(result, "Password must be at least 8 characters long, include a capital letter, a lower letter, a digit and a special character.")

    def test_login_successful(self):
        user = User(**self.data)
        user.save_to_file()
        result = user.login()
        self.assertEqual(result, "Login successful.")

    def test_login_wrong_password(self):
        user = User(**self.data)
        user.save_to_file()
        self.data["password"] = "WrongPass!"
        result = User(**self.data).login()
        self.assertEqual(result, "Invalid username or password.")

    def test_login_nonexistent_user(self):
        result = User(**self.data).login()
        self.assertEqual(result, "Invalid username or password.")

if __name__ == "__main__":
    unittest.main()

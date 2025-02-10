# TrainSphere


## Overview
TrainSphere is a Flask-based web application designed to help users achieve their fitness goals by providing structured workout plans, progress tracking, and performance insights. The app enables users to log their exercises, track burned calories, and receive customized training recommendations.

## Key Features


### Workout Management
 
 -	Create and manage personalized workout plans.
 
 -	Choose from predefined workout categories (strength, cardio, flexibility, etc.).
 
 -	Log training sessions with duration and intensity.

### Progress Tracking

-	Monitor progress through visual data representation.

-	Calculate calories burned and BMI.

-	View daily and weekly workout summaries.


### Reports and Data Export

-	Generate progress reports.

-	Export workout history to CSV or PDF.

### Notifications and Reminders

-	Receive automated reminders before scheduled workouts.

-	Get motivational quotes and weather updates to assist in planning.

### Secure User Authentication

- Register and log in with hashed passwords.

- Store user data securely in JSON

 
## Installation and Setup

- Python 3.8 or higher
- A virtual environment (recommended)

 **Steps to Run the Application**
 
 1. Clone the Repository
```bash
git clone https://github.com/your-username/TrainSphere.git
cd TrainSphere
```
 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```
 3. Install Dependencies
```bash
pip install -r requirements.txt
```
 4. Run the Application
```bash
python app/main.py
```
 5. Access the Application
Open your browser and navigate to:  
[http://127.0.0.1:5000](http://127.0.0.1:5000)



 Coding Test
Check code style with:
```bash
pylint app/
```
Test Coverage
```bash
pytest tests/
coverage run -m pytest tests/
coverage report -m
```



# TrainSphere

TrainSphere is a Flask-based fitness tracker web application for logging workouts and tracking progress.

## Features
- Log workouts (date, type, duration, notes)
- View progress/history
- Workout templates / plans (if implemented)
- Basic reports (if implemented)

---


## Setup the Installation

### 1. Clone the repository

```bash
git clone https://github.com/lmihova/TrainSphere.git
cd TrainSphere
```

---

### 2. Create a virtual environment

**Windows (PowerShell)**

```bash
py -m venv .venv
```

---

### 3. Activate the virtual environment

**Windows (PowerShell)**

```bash
.\.venv\Scripts\Activate.ps1
```

---

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Run the application

```bash
python app.py
```


## Project Structure

```
TrainSphere/
│
├── app.py                # Main application entry point
├── requirements.txt      # Project dependencies
├── static/               # CSS
├── templates/            # HTML pages
├── database/             # Database files 
└── README.md
```

import threading
import time
import requests
import random
from datetime import datetime, timedelta
from classes.user import User

MOTIVATIONAL_QUOTES = [
    "Push yourself because no one else is going to do it for you.",
    "Success starts with self-discipline.",
    "No pain, no gain!", 
    "Train insane or remain the same.",
    "Don’t stop when you’re tired. Stop when you’re done."
]

def get_weather(city="Sofia"):  #use Open Meteo
    url = f"https://api.open-meteo.com/v1/forecast?latitude=42.6975&longitude=23.3242&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_desc = data["current_weather"]["weathercode"]
        temperature = data["current_weather"]["temperature"]
        return f"Current weather in {city}: {weather_desc}, {temperature}°C"
    return "Weather data unavailable."

def send_reminder(user, training_time):
    reminder_time = training_time - timedelta(hours=1)
    while True:
        current_time = datetime.now()
        if current_time >= reminder_time:
            weather_info = get_weather()
            quote = random.choice(MOTIVATIONAL_QUOTES)
            print(f"Reminder for {user.username}: Your training is at {training_time.strftime('%H:%M')}!\n")
            print(f"Motivational Quote: {quote}\n")
            print(f"{weather_info}\n")
            break
        time.sleep(60)  # Check every minute

#Example user
user = User("Ivan", 25, 75, 180, "lose weight")
training_time = datetime.now() + timedelta(hours=2)  # Example training time in 2 hours
thread = threading.Thread(target=send_reminder, args=(user, training_time))
thread.start()

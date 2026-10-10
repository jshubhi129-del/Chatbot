import os
import webbrowser
import datetime
import subprocess
import pyautogui
import pywhatkit
import smtplib
import speech_recognition as sr
import pyttsx3
import threading
import queue
import requests
import time
import psutil
import wikipedia
import random
from askai import askai  # Import AI response function

# Initialize text-to-speech and speech recognition
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Create a queue for managing speech
speech_queue = queue.Queue()

def speech_worker():
    """Runs in the background and processes speech requests sequentially."""
    while True:
        message = speech_queue.get()
        if message is None:
            break  # Exit loop if None is received (for stopping the thread)
        engine.say(message)
        engine.runAndWait()
        speech_queue.task_done()

# Start speech worker thread
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

def say(message, should_speak=True):
    """Queues text to be spoken instead of calling runAndWait() directly."""
    if should_speak:
        speech_queue.put(message)

def listen():
    """Listens to user input and returns recognized text."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            return "I didn't catch that."
        except sr.RequestError:
            return "Error with the speech recognition service."

def stop_jarvis():
    """Stops JARVIS and exits gracefully."""
    say("Shutting down. Goodbye!")
    speech_queue.put(None)  # Stop speech worker thread
    exit()

def play_music(song):
    """Plays a song on YouTube."""
    pywhatkit.playonyt(song)
    say(f"Playing {song} on YouTube.")

def send_email(to_email, subject, message):
    """Sends an email securely."""
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")  # Secure credentials handling
    
    if not sender_email or not sender_password:
        say("Email credentials are missing. Please configure them first.")
        return
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        email_message = f"Subject: {subject}\n\n{message}"
        server.sendmail(sender_email, to_email, email_message)
        server.quit()
        say("Email sent successfully.")
    except Exception as e:
        say("Failed to send email.")
        print(e)

def get_weather():
    """Fetches weather information."""
    api_key = "your_openweather_api_key"
    city = "your_city"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        weather = response['weather'][0]['description']
        temp = response['main']['temp']
        say(f"The weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
    except:
        say("I couldn't fetch the weather details.")

def google_search(query):
    """Performs a Google search."""
    webbrowser.open(f"https://www.google.com/search?q={query}")
    say(f"Searching Google for {query}.")

def control_system(command):
    """Performs system-level commands like shutdown, restart, or checking system status."""
    actions = {
        "shutdown": "shutdown /s /t 1",
        "restart": "shutdown /r /t 1",
        "battery": lambda: say(f"Battery level is at {psutil.sensors_battery().percent} percent."),
        "cpu usage": lambda: say(f"CPU usage is at {psutil.cpu_percent()} percent."),
        "memory usage": lambda: say(f"Memory usage is at {psutil.virtual_memory().percent} percent.")
    }
    
    if command in actions:
        if callable(actions[command]):
            actions[command]()
        else:
            say(f"Executing {command}.")
            os.system(actions[command])
    else:
        say("I can't perform that action yet.")

def tell_joke():
    """Tells a random joke."""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don’t skeletons fight each other? They don’t have the guts!"
    ]
    joke = random.choice(jokes)
    say(joke)
    return joke

def process_command(text):
    """Processes user commands and executes corresponding actions."""
    text = text.lower()
    
    if text in ["stop", "exit", "quit", "close"]:
        stop_jarvis()
    
    commands = {
        "hello": "Hello! How can I help you?",
        "time": f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}",
        "screenshot": "Screenshot taken.",
        "weather": get_weather,
        "play music": play_music,
        "send email": send_email,
        "tell me a joke": tell_joke
    }
    
    if text in commands:
        if callable(commands[text]):
            return commands[text]()
        else:
            say(commands[text])
        return commands[text]
    elif "search for" in text:
        query = text.replace("search for", "").strip()
        google_search(query)
        return f"Searching Google for {query}"
    elif text in ["shutdown", "restart", "battery", "cpu usage", "memory usage"]:
        control_system(text)
        return "System command executed."
    else:
        response = askai(text)  # Fallback to AI chatbot
        say(response, should_speak=True)
        return response

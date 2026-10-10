import os
import webbrowser
import datetime
import subprocess
import pyautogui
import pywhatkit
import smtplib
import speech_recognition as sr
import pyttsx3
from askai import askai  # Import AI response function
import pyttsx3
import speech_recognition as sr
import threading

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def say(message):
    """Speak the message while allowing interruption with 'listen'."""
    
    def speak():
        engine.say(message)
        engine.runAndWait()

    # Start speaking in a separate thread
    thread = threading.Thread(target=speak)
    thread.start()
    
    # Listen while speaking
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for interruption...")
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            if "listen" in text:
                print("Interrupted! Listening again...")
                return listen()  # Restart listening immediately
        except sr.UnknownValueError:
            pass  # Ignore if nothing is recognized
        except sr.RequestError:
            print("Speech Recognition service error.")

def listen():
    """Listen to user input and return as text."""
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


def open_application(app_name):
    if "notepad" in app_name:
        os.system("notepad")
    elif "chrome" in app_name:
        webbrowser.open("https://www.google.com")
    elif "spotify" in app_name:
        os.system("spotify")
    else:
        say("I can't open that application yet.")

def play_music(song):
    pywhatkit.playonyt(song)
    say(f"Playing {song} on YouTube.")

def control_system(command):
    if "shutdown" in command:
        say("Shutting down the system.")
        os.system("shutdown /s /t 1")
    elif "restart" in command:
        say("Restarting the system.")
        os.system("shutdown /r /t 1")
    else:
        say("I can't perform that action yet.")

def send_email(to_email, subject, message):
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"
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

def process_command(text):
    if "hello" in text:
        return "Hello! How can I help you?"
    elif "why" in text:
        return askai(text + " Explain this in short and easy way")
    elif "open" in text:
        app = text.replace("open", "").strip()
        open_application(app)
        return f"Opening {app}" if app else "I couldn't recognize the application."
    elif "search for" in text:
        query = text.replace("search for", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching Google for {query}"
    elif "time" in text:
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
    elif "screenshot" in text:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        return "Screenshot taken."
    elif "send email" in text:
        say("Please provide the recipient email.")
        to_email = listen()
        say("What is the subject?")
        subject = listen()
        say("What should I say?")
        message = listen()
        send_email(to_email, subject, message)
        return "Email process completed."
    elif "play music" in text:
        song = text.replace("play music", "").strip()
        play_music(song)
        return f"Playing {song}"
    elif "shutdown" in text or "restart" in text:
        control_system(text)
        return "System command executed."
    else:
        return askai(text)  # Fallback to chatbot AI

import tkinter as tk
import keyboard
import requests
import pyttsx3  # For text-to-speech
import speech_recognition as sr  # For speech recognition
import threading  # To run speech recognition in the background

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to fetch AI response
def fetch_ai_response():
    user_input = entry.get()
    if not user_input.strip():
        return
    
    try:
        response = requests.get("http://127.0.0.1:8000/alix")
        response_data = response.json()
        
        if "response" in response_data:
            ai_response = response_data["response"]
            label.config(text=ai_response)
            speak(ai_response)
        else:
            label.config(text="Error: Invalid response from AI")
    
    except requests.exceptions.ConnectionError:
        label.config(text="Error: Cannot connect to AI server")


# Function to show overlay when hotkey is pressed
def show_overlay():
    root.deiconify()

# Function to use text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        label.config(text="Listening...")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            entry.delete(0, tk.END)
            entry.insert(0, text)
        except sr.UnknownValueError:
            label.config(text="Could not understand audio")
        except sr.RequestError:
            label.config(text="Speech recognition service unavailable")

# Function to exit application
def exit_app():
    root.destroy()

# Bind global hotkey activation
keyboard.add_hotkey("ctrl+a+i", show_overlay)
keyboard.add_hotkey("ctrl+q", exit_app)  # Add hotkey to exit

# Initialize Tkinter window
root = tk.Tk()
root.geometry("400x200")
root.overrideredirect(True)  # Floating overlay
root.attributes('-topmost', True)  # Always on top

# UI Components
entry = tk.Entry(root)
entry.pack()

button = tk.Button(root, text="Send", command=fetch_ai_response)
button.pack()

voice_button = tk.Button(root, text="🎤 Speak", command=lambda: threading.Thread(target=listen).start())
voice_button.pack()

exit_button = tk.Button(root, text="Exit", command=exit_app)  # Exit button
exit_button.pack()

label = tk.Label(root, text="")
label.pack()

# Run Tkinter main loop
root.mainloop()

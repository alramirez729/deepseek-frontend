import tkinter as tk
import keyboard
import requests
import pyttsx3  # For text-to-speech
import speech_recognition as sr  # For speech recognition
import threading  # To run speech recognition in the background

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to safely update UI text
def update_response_text(text):
    response_text.config(state=tk.NORMAL)
    response_text.delete(1.0, tk.END)
    response_text.insert(tk.END, text)
    response_text.config(state=tk.DISABLED)

# Function to fetch AI response
def fetch_ai_response():
    user_input = entry.get()
    if not user_input.strip():
        return

    try:
        response = requests.post("http://127.0.0.1:8000/alix", json={"text": user_input})
        
        if response.status_code != 200:
            root.after(0, update_response_text, "Error: AI server error")
            return
        
        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError:
            root.after(0, update_response_text, "Error: Invalid JSON response")
            return
        
        if "response" in response_data:
            ai_response = response_data["response"]
            root.after(0, update_response_text, ai_response)  # Update UI safely
            threading.Thread(target=speak, args=(ai_response,)).start()  # Run speak in a thread
        else:
            root.after(0, update_response_text, "Error: Unexpected AI response")

    except requests.exceptions.ConnectionError:
        root.after(0, update_response_text, "Error: Cannot connect to AI server")

# Function to show overlay when hotkey is pressed
def show_overlay():
    root.deiconify()

# Function to use text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to voice input safely
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        root.after(0, update_response_text, "Listening...")  # Safely update UI
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            root.after(0, entry.delete, 0, tk.END)  # Safely update UI
            root.after(0, entry.insert, 0, text)  # Safely update UI
        except sr.UnknownValueError:
            root.after(0, update_response_text, "Could not understand audio")
        except sr.RequestError:
            root.after(0, update_response_text, "Speech recognition unavailable")

# Function to exit application
def exit_app():
    root.quit()  # Graceful exit
    root.destroy()

# Initialize Tkinter window
root = tk.Tk()
root.title("AI Assistant")

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size and position (bottom-right corner)
window_width, window_height = 400, 250
x_position = screen_width - window_width - 20  # 20px padding from the right
y_position = screen_height - window_height - 50  # 50px padding from the bottom
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

root.overrideredirect(True)  # Floating overlay
root.attributes('-topmost', True)  # Always on top

# Bind global hotkey activation
keyboard.add_hotkey("ctrl+a+i", show_overlay)
keyboard.add_hotkey("ctrl+q", exit_app)  # Add hotkey to exit

# UI Components
entry = tk.Entry(root, width=40)
entry.pack(pady=5)

button = tk.Button(root, text="Send", command=fetch_ai_response)
button.pack()

voice_button = tk.Button(root, text="🎤 Speak", command=lambda: threading.Thread(target=listen, daemon=True).start())
voice_button.pack()

exit_button = tk.Button(root, text="Exit", command=exit_app)  # Exit button
exit_button.pack()

# Use a Text widget for response display (word wrapping enabled)
response_text = tk.Text(root, height=5, width=40, wrap=tk.WORD)
response_text.pack(pady=5)
response_text.config(state=tk.DISABLED)  # Make it read-only

# Ensure Tkinter does not freeze
try:
    root.mainloop()
except KeyboardInterrupt:
    print("Application closed manually.")

import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import pyttsx3
import openai

# Initialize the OpenAI API client with your API key
openai.api_key = 'YOUR_API_KEY'

# Initialize the recognizer
r = sr.Recognizer()

audio_data = None

# Function to handle the recording process
def start_recording():
    global audio_data
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.2)
            # Update the status label
            status_label.config(text="Recording... Press 'Stop Recording' to stop.")
            # Start recording
            audio_data = r.listen(source)
    except Exception as e:
        status_label.config(text=f"Recording error: {e}")

# Function to handle stopping the recording and asking GPT
def stop_recording():
    global audio_data
    # Recognize speech and handle the GPT interaction
    try:
        # Recognize audio using Google in the selected language
        MyText = r.recognize_google(audio_data, language=language_var.get())
        MyText = MyText.lower()

        # Display the recognized text in the conversation
        add_message("You", MyText, 'blue', 'w')
        
        # Get the GPT's response
        response = ask_gpt(MyText, selected_model.get())
        
        # Display the GPT's response in the conversation
        add_message("GPT", response, 'green', 'e')
        
        # After displaying the response, speak it using SpeakText
        SpeakText(response, language_var.get())
        
    except Exception as e:
        status_label.config(text=f"Error: {e}")


# Function to convert text to speech in Greek or English
def SpeakText(command, language):
    # Initialize the engine
    engine = pyttsx3.init()
    
    # Map languages to voice names
    voice_mapping = {
        'el-GR': 'Microsoft Stefanos - Greek (Greece)',
        'en-US': 'Microsoft Zira Desktop - English (United States)'
    }
    
    # Try-catch block for exception handling
    try:
        # Get the appropriate voice name from the mapping
        voice_name = voice_mapping.get(language)
        
        # Search for the voice in the available voices
        voices = engine.getProperty('voices')
        voice_found = False
        for voice in voices:
            # Compare the voice name in a case-insensitive manner
            if voice.name.lower() == voice_name.lower():
                engine.setProperty('voice', voice.id)
                voice_found = True
                break
        
        # If the voice is not found, print a message
        if not voice_found:
            print(f"No suitable voice found for {language} language.")
        
        # Speak the command
        engine.say(command)
        engine.runAndWait()
    
    except Exception as e:
        print(f"Error in SpeakText function: {e}")

# Function to interact with GPT API and keep track of previous messages
conversation_history = []

def ask_gpt(question, model):
    # Add the user's message to the conversation history
    conversation_history.append({"role": "user", "content": question})

    # Make a GPT API call with the conversation history using the selected model
    response = openai.chat.completions.create(
        model=model,
        messages=conversation_history
    )
    
    # Get the GPT's response text
    gpt_response_text = response.choices[0].message.content.strip()
    
    # Add the GPT's response to the conversation history
    conversation_history.append({"role": "assistant", "content": gpt_response_text})
    
    # Return the GPT's response text
    return gpt_response_text

# Function to update the `language_code` variable based on the user's choice
def update_language_code(*args):
    global language_code
    language_code = language_var.get()

# Function to add a message bubble to the conversation canvas
def add_message(sender, message, color, alignment):
    global conversation_height
    # Create message bubble
    bubble = tk.Label(conversation_frame_in_canvas, text=f"{sender}: {message}", bg=color, fg="white", padx=10, pady=5, wraplength=400, anchor=alignment)
    # Add message bubble to frame
    bubble.grid(row=conversation_height, column=0, sticky=tk.W)
    # Update conversation height
    conversation_height += 1

# Create the main application window
root = tk.Tk()
root.title("Voice to GPT")
root.minsize(600, 400)

# Define the available GPT models
gpt_models = [
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
    "gpt-3.5-turbo-instruct",
    "gpt-3.5-turbo-instruct-0914",
    "gpt-4",
    "gpt-4-0613",
]

languages = [
    ("English", "en-US"),
    ("Greek", "el-GR"),
]

# Define a variable to hold the language code
language_var = tk.StringVar(value="en-US")
language_var.trace_add('write', update_language_code)

# Frame for the language dropdown
language_frame = tk.Frame(root)
language_frame.pack(side="top", fill="x")

# Dropdown menu for selecting a language
language_menu = tk.OptionMenu(language_frame, language_var, *[code for name, code in languages])
language_menu.config(bg="white", fg="black", padx=5, pady=5)
language_menu.pack(side="left", padx=5, pady=5)

# Frame for the model dropdown
model_frame = tk.Frame(root)
model_frame.pack(side="top", fill="x")

# Dropdown menu for selecting a GPT model
selected_model = tk.StringVar(value=gpt_models[0])
model_menu = tk.OptionMenu(model_frame, selected_model, *gpt_models)
model_menu.config(bg="white", fg="black", padx=5, pady=5)
model_menu.pack(side="left", padx=5, pady=5)

# Frame to contain the buttons
button_frame = tk.Frame(root)
button_frame.pack(side="top", fill="x")

# Button to start recording
start_button = tk.Button(button_frame, text="Start Recording", command=start_recording, bg="green", fg="white", padx=10, pady=5)
start_button.pack(side="left", padx=5, pady=5)

# Button to stop recording and ask GPT
stop_button = tk.Button(button_frame, text="Get Response", command=stop_recording, bg="red", fg="white", padx=10, pady=5)
stop_button.pack(side="left", padx=5, pady=5)

# Frame to contain the conversation canvas
conversation_frame = tk.Frame(root)
conversation_frame.pack(fill=tk.BOTH, expand=True)

# Canvas for displaying the conversation bubbles
conversation_canvas = tk.Canvas(conversation_frame, bg="white", highlightthickness=0)
conversation_canvas.pack(side="top", fill="both", expand=True)

# Create a frame inside the canvas to hold the messages
conversation_frame_in_canvas = tk.Frame(conversation_canvas, bg="white")
conversation_canvas.create_window((0, 0), window=conversation_frame_in_canvas, anchor="nw")

# Make the conversation area scrollable
scrollbar = tk.Scrollbar(conversation_frame, orient="vertical", command=conversation_canvas.yview)
scrollbar.pack(side="right", fill="y")
conversation_canvas.configure(yscrollcommand=scrollbar.set)

# Bind scrollbar to canvas
conversation_canvas.bind("<Configure>", lambda e: conversation_canvas.configure(scrollregion=conversation_canvas.bbox("all")))
conversation_canvas.bind_all("<MouseWheel>", lambda event: conversation_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

# Initial height of the conversation canvas
conversation_height = 0

# Label for displaying status messages
status_label = tk.Label(root, text="", fg="blue")
status_label.pack()

# Run the main event loop
root.mainloop()

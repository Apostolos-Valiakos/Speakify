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

        # Display the recognized text in the text area
        text_area.insert(tk.END, f"You said: {MyText}\n")
        
        # Get the GPT's response
        response = ask_gpt(MyText, selected_model.get())
        
        # Display the GPT's response in the text area
        text_area.insert(tk.END, f"GPT's response: {response}\n")
        
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

# Create the main application window
root = tk.Tk()
root.title("Voice to GPT")

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

# Define the available languages
languages = [
    ("English", "en-US"),
    ("Greek", "el-GR"),
]

# Define a variable to hold the language code
language_var = tk.StringVar(value="en-US")
language_var.trace_add('write', update_language_code)

# Dropdown menu for selecting a language
language_menu = tk.OptionMenu(root, language_var, *[code for name, code in languages])
language_menu.pack()

# Dropdown menu for selecting a GPT model
selected_model = tk.StringVar(value=gpt_models[0])
model_menu = tk.OptionMenu(root, selected_model, *gpt_models)
model_menu.pack()

# Button to start recording
start_button = tk.Button(root, text="Start Recording", command=start_recording)
start_button.pack()

# Button to stop recording and ask GPT
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
stop_button.pack()

# Text area for displaying input and GPT response
text_area = scrolledtext.ScrolledText(root, width=50, height=15)
text_area.pack()

# Label for displaying status messages
status_label = tk.Label(root, text="")
status_label.pack()

# Run the main event loop
root.mainloop()
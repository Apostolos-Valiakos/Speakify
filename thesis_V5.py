import tkinter as tk
from tkinter import ttk, simpledialog
import speech_recognition as sr
import pyttsx3
import openai
from pathlib import Path
from PIL import Image, ImageTk
import requests
from io import BytesIO

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

# Function to handle stopping the recording and processing the input based on the active tab
def stop_recording(tab_name):
    global audio_data
    try:
        # Recognize audio using Google in the selected language
        MyText = r.recognize_google(audio_data, language=language_var.get())
        MyText = MyText.lower()
        
        if tab_name == "Speech Response":
            add_message("You", MyText, 'blue', 'w')
            response = ask_gpt(MyText, selected_model.get())
            add_message("GPT", response, 'green', 'e', True)
            SpeakText(response, language_var.get())
        elif tab_name == "Image Generation":
            generate_image(MyText)
        # elif tab_name == "Sound Generation":
        #     generate_sound(MyText)
        # elif tab_name == "Translation":
        #     translate_audio(audio_data)
        
    except Exception as e:
        status_label.config(text=f"Error: {e}")

# Function to convert text to speech in Greek or English
def SpeakText(command, language, speed=180):
    engine = pyttsx3.init()
    engine.setProperty('rate', speed)
    voice_mapping = {
        'el-GR': 'Microsoft Stefanos - Greek (Greece)',
        'en-US': 'Microsoft Zira Desktop - English (United States)'
    }
    try:
        voice_name = voice_mapping.get(language)
        voices = engine.getProperty('voices')
        for voice in voices:
            if voice.name.lower() == voice_name.lower():
                engine.setProperty('voice', voice.id)
                break
        engine.say(command)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in SpeakText function: {e}")

# Function to interact with GPT API and keep track of previous messages
conversation_history = []

def ask_gpt(question, model):
    conversation_history.append({"role": "user", "content": question})
    response = openai.chat.completions.create(
        model=model,
        messages=conversation_history
    )
    gpt_response_text = response.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": gpt_response_text})
    return gpt_response_text

# Function to generate an image using DALL-E and display it in an iframe
def generate_image(prompt):
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        
        # Create a new window to display the image in an iframe
        image_window = tk.Toplevel(root)
        image_window.title("Generated Image")
        
        # Load the image
        image_response = requests.get(image_url)
        image_data = Image.open(BytesIO(image_response.content))
        photo = ImageTk.PhotoImage(image_data)
        
        # Create a label to display the image
        image_label = tk.Label(image_window, image=photo)
        image_label.image = photo
        image_label.pack()
        
    except Exception as e:
        status_label.config(text=f"Image generation error: {e}")

# Function to generate sound using OpenAI and play it
# def generate_sound(text):
#     try:
#         audio_file_path = Path(__file__).parent / "speech.wav"
#         audio_data.export(audio_file_path, format="wav")

#         with open(audio_file_path, "rb") as audio_file:
#             translation_response = openai.audio.translations.create(
#                 model="whisper-1",
#                 file=audio_file
#             )

#         translated_text = translation_response.text

#         # Now use the translated text in the subsequent speech generation
#         speech_file_path = Path(__file__).parent / "speech.mp3"
#         response = openai.audio.speech.create(
#             model="tts-1",
#             voice="alloy",
#             input=translated_text
#         )
#         response.stream_to_file(speech_file_path)

#     except Exception as e:
#         status_label.config(text=f"Translation error: {e}")
        
#     except Exception as e:
#         status_label.config(text=f"Sound generation error: {e}")

# Function to update the `language_code` variable based on the user's choice
def update_language_code(*args):
    global language_code
    language_code = language_var.get()

# Function to add a message bubble to the conversation canvas
def add_message(sender, message, color, alignment, add_translate_button=False):
    global conversation_height
    bubble = tk.Label(conversation_frame_in_canvas, text=f"{sender}: {message}", bg=color, fg="white", padx=10, pady=5, wraplength=400, anchor=alignment)
    bubble.grid(row=conversation_height, column=0, sticky=tk.W)
    if add_translate_button:
        translate_button = tk.Button(conversation_frame_in_canvas, text="Translate", command=lambda m=message: open_translate_dialog(m), bg="blue", fg="white", padx=5, pady=2)
        translate_button.grid(row=conversation_height, column=1, sticky=tk.E)
    conversation_height += 1

# Function to handle the recording process for translation and subsequent speech generation
# def start_recording_translation():
#     global audio_data
#     try:
#         with sr.Microphone() as source:
#             # Adjust for ambient noise
#             r.adjust_for_ambient_noise(source, duration=0.2)
#             # Update the status label
#             status_label.config(text="Recording... Press 'Stop Recording' to stop.")
#             # Start recording
#             audio_data = r.listen(source)
#     except Exception as e:
#         status_label.config(text=f"Recording error: {e}")

# # Function to handle stopping the recording and processing for translation and subsequent speech generation
# def stop_recording_translation():
#     global audio_data
#     try:
#         # Translate audio using OpenAI API
#         translation_response = translate_audio(audio_data)

#         translated_text = translation_response.text

#         # Now use the translated text in the subsequent speech generation
#         speech_file_path = Path(__file__).parent / "speech.mp3"
#         response = openai.audio.speech.create(
#             model="tts-1",
#             voice="alloy",
#             input=translated_text
#         )
#         response.stream_to_file(speech_file_path)

#     except Exception as e:
#         status_label.config(text=f"Translation error: {e}")
#     try:
#         translation_response = openai.audio.translations.create(
#             model="whisper-1",
#             file=BytesIO(audio_data.get_wav_data())
#         )

#         translated_text = translation_response.text
#         add_message("Translation", translated_text, 'purple', 'e')
#         SpeakText(translated_text, language_var.get())
#         return translation_response

#     except Exception as e:
#         status_label.config(text=f"Translation error: {e}")
# def translate_audio(audio_data):
#     try:
#         # Convert audio data to WAV format
#         with BytesIO() as wav_buffer:
#             wav_data = audio_data.get_wav_data(convert_rate=16000, convert_width=2)
#             wav_buffer.write(wav_data)
#             wav_buffer.seek(0)

#             # Translate audio using OpenAI API
#             translation_response = openai.audio.translations.create(
#                 model="whisper-1",
#                 file=wav_buffer
#             )

#         translated_text = translation_response.text
#         add_message("Translation", translated_text, 'purple', 'e')
#         SpeakText(translated_text, language_var.get())
#         return translation_response

#     except Exception as e:
#         status_label.config(text=f"Translation error: {e}")

# Function to open the translation dialog
def open_translate_dialog(message):
    translate_dialog = TranslateDialog(root, message)

# Class for the translation dialog
class TranslateDialog(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.message = message
        self.title("Select Language")
        self.geometry("300x150")

        tk.Label(self, text="Select the target language:").pack(pady=5)
        
        self.target_language_var = tk.StringVar(value=language_options[0])
        self.language_menu = tk.OptionMenu(self, self.target_language_var, *language_options)
        self.language_menu.pack(pady=5)
        
        self.translate_button = tk.Button(self, text="Translate", command=self.translate_message)
        self.translate_button.pack(pady=5)
        
    def translate_message(self):
        target_language = self.target_language_var.get()
        translation_request = f"Translate the following text to {target_language}: {self.message}"
        try:
            translated_text = ask_gpt(translation_request, selected_model.get())
            add_message("Translated", translated_text, 'purple', 'e')
            SpeakText(translated_text, language_var.get())
        except Exception as e:
            status_label.config(text=f"Translation error: {e}")
        finally:
            self.destroy()

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

language_options = [
    "Chinese",
    "Spanish",
    "English",
    "Hindi",
    "Arabic",
    "Portuguese",
    "Bengali",
    "Russian",
    "Japanese",
    "Punjabi",
    "German",
    "Javanese",
    "Wu (Shanghainese)",
    "Korean",
    "French"
]

# Define a variable to hold the language code
language_var = tk.StringVar(value="en-US")
language_var.trace_add('write', update_language_code)

# Create a notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

# Function to add common widgets to a tab
def add_common_widgets(tab_frame, tab_name):
    # Add the language dropdown
    language_frame = tk.Frame(tab_frame)
    language_frame.pack(side="top", fill="x")

    language_menu = tk.OptionMenu(language_frame, language_var, *[code for name, code in languages])
    language_menu.config(bg="white", fg="black", padx=5, pady=5)
    language_menu.pack(side="left", padx=5, pady=5)

    # Add the start recording button
    start_button = tk.Button(tab_frame, text="Start Recording", command=start_recording, bg="green", fg="white", padx=10, pady=5)
    start_button.pack(side="top", padx=5, pady=5)

    # Add the stop recording button
    stop_button = tk.Button(tab_frame, text="Get Response", command=lambda: stop_recording(tab_name), bg="red", fg="white", padx=10, pady=5)
    stop_button.pack(side="top", padx=5, pady=5)

# Speech Response Tab
speech_response_tab = ttk.Frame(notebook)
notebook.add(speech_response_tab, text="Speech Response")
add_common_widgets(speech_response_tab, "Speech Response")

# Frame to contain the conversation canvas
conversation_frame = tk.Frame(speech_response_tab)
conversation_frame.pack(fill=tk.BOTH, expand=True)

# Canvas for displaying the conversation bubbles
conversation_canvas = tk.Canvas(conversation_frame, bg="white", highlightthickness=0)
conversation_canvas.pack(side="top", fill="both", expand=True)

# Dropdown menu for selecting a GPT model
selected_model = tk.StringVar(value=gpt_models[0])
model_menu = tk.OptionMenu(conversation_frame, selected_model, *gpt_models)
model_menu.config(bg="white", fg="black", padx=5, pady=5)
model_menu.pack(side="left", padx=5, pady=5)

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

# Image Generation Tab
image_generation_tab = ttk.Frame(notebook)
notebook.add(image_generation_tab, text="Image Generation")
add_common_widgets(image_generation_tab, "Image Generation")

# Translation Tab
# translation_tab = ttk.Frame(notebook)
# notebook.add(translation_tab, text="Translation")
# add_common_widgets(translation_tab, "Translation")

# Label for displaying status messages
status_label = tk.Label(root, text="", fg="blue")
status_label.pack()

# Run the main event loop
root.mainloop()

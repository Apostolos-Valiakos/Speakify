import speech_recognition as sr
import pyttsx3 
from openai import OpenAI

# Initialize the OpenAI API client with your API key
OpenAI.api_key = 'YOUR_API_KEY'

# Initialize the recognizer 
r = sr.Recognizer() 

# Function to convert text to speech
def SpeakText(command, language):
    # Initialize the engine
    engine = pyttsx3.init()
    
    # Map languages to voice names
    voice_mapping = {
        'greek': 'Microsoft Stefanos - Greek (Greece)',
        'english': 'Microsoft Zira Desktop - English (United States)'  # Replace with the appropriate English voice name on your system
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

conversation_history = []
# Function to interact with GPT API
def ask_gpt(question):

    conversation_history.append({"role": "user", "content": question})

    client = OpenAI(api_key='YOUR_API_KEY')
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    gpt_response_text = completion.choices[0].message.content.strip()
    conversation_history.append({"role": "assistant", "content": gpt_response_text})
    
    return (gpt_response_text)

# Ask the user for their preferred language at the beginning
language = None
while language not in ['english', 'greek']:
    print("Please choose a language: English or Greek")
    language = input().strip().lower()

# Set the language code based on the user's choice
if language == 'english':
    language_code = 'en-US'
elif language == 'greek':
    language_code = 'el-GR'

# Loop infinitely for user to speak
while True:
    # Exception handling to handle exceptions at the runtime
    try:
        # Use the microphone as source for input.
        with sr.Microphone() as source:
            # Wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level.
            r.adjust_for_ambient_noise(source, duration=0.2)
            # Listen for the user's input.
            audio = r.listen(source)
            # Recognize audio in the chosen language.
            MyText = r.recognize_google(audio, language=language_code)
            MyText = MyText.lower()

            print("You said:", MyText)
            # SpeakText(MyText, language)
            # Get the GPT's response.
            response = ask_gpt(MyText)
            print("GPT's response:", response)
            SpeakText(response, language)

    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
         
    except sr.UnknownValueError:
        print("Unknown error occurred")
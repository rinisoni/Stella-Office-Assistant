import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import datetime
import os
import pygame # type: ignore
from openai import OpenAI

client = OpenAI(api_key="your_openai_api_key_here")  # Replace with your actual API key

# Initialize the recognizer
recognizer = sr.Recognizer()

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Define the wake word
WAKE_WORD = "hey Stella"

def speak(text):
    """Make Stella speak the given text using gTTS and pygame."""
    st.write(f"**Stella:** {text}")
    tts = gTTS(text=text, lang="en", tld="co.uk")  # Use a female voice (British English)
    tts.save("stella_response.mp3")
    
    # Load and play the audio file using pygame
    pygame.mixer.music.load("stella_response.mp3")
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    os.remove("stella_response.mp3")  # Clean up the audio file

def listen():
    """Listen to the user's voice input and convert it to text."""
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        audio = recognizer.listen(source)

        try:
            st.write("Recognizing...")
            query = recognizer.recognize_google(audio, language="en-US")
            st.write(f"**You:** {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Can you repeat?")
            return None
        except sr.RequestError:
            speak("Sorry, my speech service is down. Please try again later.")
            return None

def stella_response(query):
    """Generate a response based on the user's query."""
    if "hello" in query:
        return "Hello! How can I assist you today?"
    elif "how are you" in query:
        return "I'm doing great, thank you for asking!"
    elif "your name" in query:
        return "My name is Stella, your office assistant."
    elif "time" in query:
        now = datetime.datetime.now().strftime("%H:%M")
        return f"The current time is {now}."
    elif "bye" in query:
        return "Goodbye! Have a great day!"
    elif "about office" in query:
        return "Stellarmind is a software company based in Ahmedabad."
    else:
        #use openai for generic questions
        return ask_openai(query)
    
def ask_openai(query):
    """Ask OpenAI GPT for a response to the user's query."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 Turbo
            messages=[
                {"role": "system", "content": "You are Stella, a helpful office assistant."},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def detect_wake_word():
    """Continuously listen for the wake word."""
    with sr.Microphone() as source:
        st.write("Waiting for the wake word...")
        while True:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                st.write("Checking for wake word...")
                query = recognizer.recognize_google(audio, language="en-US").lower()
                st.write(f"Heard: {query}")
                if WAKE_WORD in query:
                    speak("Yes? How can I help you?")
                    return True
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                speak("Sorry, my speech service is down. Please try again later.")
                return False

def main():
    """Streamlit app for Stella."""
    st.title("Stella - Your Office Assistant 🤖")
    st.write("Welcome to Stella! You can interact with her using text or voice commands.")

    # Text input for chatting
    user_input = st.text_input("Type your message here:")
    if st.button("Send"):
        if user_input:
            response = stella_response(user_input.lower())
            speak(response)

    # Voice input for chatting
    if st.button("Start Voice Command"):
        if detect_wake_word():
            while True:
                query = listen()
                if query:
                    if "bye" in query:
                        speak(stella_response(query))
                        break
                    response = stella_response(query)
                    speak(response)

if __name__ == "__main__":
    main()
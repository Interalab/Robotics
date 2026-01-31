import speech_recognition as sr
from google import genai
from elevenlabs.client import ElevenLabs

import os

# 1. Setup Gemini Client (2026 Modern SDK)

gemini_client = genai.Client(api_key="AIzaSyBDxPBWLsEfM7d6r6Vv6gwaxH-FbuicnXQ")


MODEL_ID = "gemini-3-flash-preview" 

# 2. Setup ElevenLabs Client
ELEVENLABS_KEY = "sk_f4b5b8896e27b6adae2639f527d327243f89e24e58f3c968"
el_client = ElevenLabs(api_key=ELEVENLABS_KEY)
import subprocess

def text_to_speech(text):
    print("[Status] Converting text to speech...")
    try:
        response = el_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        audio_bytes = b"".join(response)

        with open("reply.mp3", "wb") as f:
            f.write(audio_bytes)

        print("[Status] Playing audio...")

        # Mac
        subprocess.run(["afplay", "reply.mp3"])

        # Windows
        # subprocess.run(["start", "reply.mp3"], shell=True)

    except Exception as e:
        print(f"[Error] ElevenLabs TTS failed: {e}")


def listen_and_talk():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n[Status] Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[Status] Listening... (Speak now)")
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("[Status] Recognizing speech...")
            
            # vocie to text
            user_text = recognizer.recognize_google(audio, language='en-US')
            print(f"-> You said: {user_text}")
            
            # generate response from Gemini
            print("[Status] Gemini is thinking...")
            try:
                
                response = gemini_client.models.generate_content(
                    model=MODEL_ID,
                    contents=user_text,
                    config={'system_instruction': 'You are a concise voice assistant. Keep answers short.'}
                )
                reply_text = response.text
                print(f"\n[Gemini]: {reply_text}")
                
                # use reply text to generate speech
                text_to_speech(reply_text)
                
            except Exception as e:
                if "429" in str(e):
                    print("[Quota Alert] Gemini 3 Flash is in high demand. Please wait a moment.")
                else:
                    print(f"[Gemini Error] {e}")
            
        except sr.WaitTimeoutError:
            print("[Error] No speech detected.")
        except sr.UnknownValueError:
            print("[Error] Could not understand audio.")
        except Exception as e:
            print(f"[Error] An unexpected error occurred: {e}")

if __name__ == "__main__":
    print(f"--- Voice Assistant ({MODEL_ID}) ---")
    while True:
        user_input = input("\nPress Enter to start, or 'q' to quit: ")
        if user_input.lower() == 'q':
            break
        listen_and_talk()
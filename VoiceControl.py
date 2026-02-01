import speech_recognition as sr
from google import genai
from elevenlabs.client import ElevenLabs
import serial
import time
import subprocess
import os

# ================= 配置区 =================
SERIAL_PORT = "/dev/cu.usbmodem1101" 
BAUD_RATE = 9600

# --- CHANGE 1: Track last_command like your gesture code ---
last_command = None 

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 
    if ser.is_open:
        ser.write(b'0') # Ensure Manual Mode on start
    print(f"[Status] Connected to Robot on {SERIAL_PORT}")
except Exception as e:
    print(f"[Serial Error] Could not open serial port: {e}")
    ser = None

gemini_client = genai.Client(api_key="AIzaSyBcM6NM1mL_YOWI0jXaJiCsnQn6IbBjZqk")
MODEL_ID = "gemini-3-flash-preview" 
ELEVENLABS_KEY = "sk_23b342462d894f254a2de0a5dc205f4c240dc9aa39a4f713"
el_client = ElevenLabs(api_key=ELEVENLABS_KEY)

COMMAND_MAP = {
    "forward": "w",
    "backward": "s",
    "left": "a",
    "right": "d",
    "stop": "x",
    "auto": "1",
    "manual": "0"
}

def send_robot_command(text):
    """Refined to match the stability of your gesture code"""
    global last_command
    if ser is None or not ser.is_open: 
        return
    
    text = text.lower()
    cmd_to_send = None
    
    # Find the matching command
    for word, cmd_char in COMMAND_MAP.items():
        if word in text:
            cmd_to_send = cmd_char
            break
            
    # --- CHANGE 2: Deduplication Logic ---
    if cmd_to_send and cmd_to_send != last_command:
        # If it's a direction, force manual mode '0' first to override 'competitionRun'
        if cmd_to_send in ['w', 's', 'a', 'd']:
            ser.write(b'0')
            time.sleep(0.01)
            
        ser.write(cmd_to_send.encode())
        ser.flush() # Ensure it leaves the Python buffer immediately
        print(f"[Robot] >>> SENT: {cmd_to_send.upper()}")
        last_command = cmd_to_send
    elif not cmd_to_send:
        print(f"[Robot] No command in: '{text}'")

def text_to_speech(text):
    # (Keep your original TTS function exactly as it was)
    print("[Status] Converting text to speech...")
    try:
        response = el_client.text_to_speech.convert(
            voice_id="cgSgspJ2msm6clMCkdW9",
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        audio_bytes = b"".join(response)
        with open("reply.mp3", "wb") as f:
            f.write(audio_bytes)

        print("[Status] Playing audio...")
        subprocess.run(["afplay", "reply.mp3"]) 
    except Exception as e:
        print(f"[TTS Error] {e}")

def listen_and_talk():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n[Status] Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            user_text = recognizer.recognize_google(audio, language='en-US')
            print(f"-> You said: {user_text}")
            
            # --- CHANGE 3: Action occurs BEFORE the Gemini/TTS delay ---
            send_robot_command(user_text)
            
            print("[Status] Gemini is thinking...")
            response = gemini_client.models.generate_content(
                model=MODEL_ID,
                contents=f"The user said: '{user_text}'. Short response for robot control.",
                config={'system_instruction': 'Respond naturally and briefly.'}
            )
            reply_text = response.text
            print(f"\n[Gemini]: {reply_text}")
            text_to_speech(reply_text)
            
        except sr.WaitTimeoutError:
            print("[Mic] No speech detected.")
        except sr.UnknownValueError:
            print("[Mic] Could not understand.")
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    print(f"--- Robot Voice Controller ({MODEL_ID}) ---")
    while True:
        user_input = input("\nPress Enter to speak, or 'q' to quit: ")
        if user_input.lower() == 'q':
            if ser: 
                ser.write(b'x')
                ser.close()
            break
        listen_and_talk()
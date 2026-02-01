# Robotics
This is a repository created for the use of UTRA hackathon.

# 🚗 Wall•e Wall•e - Smart Interactive Car  
### Voice & Gesture Controlled Autonomous Vehicle  

## 🧠 Overview  
**Smart Interactive Car** is an intelligent robotic vehicle that allows users to control movement through **voice commands** or **hand gestures**.  
By combining **AI-powered speech processing**, **real-time gesture recognition**, and **embedded motor control**, the system enables natural and intuitive human-machine interaction with ElevenLabs and Gemini API.

This project demonstrates the potential of **multimodal AI interaction** in robotics, smart mobility, and assistive technology.

---

## ✨ Key Features  

### 🎙 Voice Interaction (Gemini API + ElevenLabs)
- Converts spoken commands into structured actions using **Gemini API**
- Generates natural AI voice feedback with **ElevenLabs**
- Supports real-time command recognition (e.g., *forward*, *left*, *stop*)

### ✋ Gesture Control (OpenCV)
- Detects and tracks hand movements using **OpenCV**
- Maps gestures to vehicle motion commands
- Enables contact-free and intuitive control

### 🚘 Smart Motion System
- Forward / Backward / Turn Left / Turn Right / Stop
- Real-time motor response
- Smooth and stable movement control

---

## 🧩 System Architecture  
User Input
 ├── Voice Module (Gemini API + ElevenLabs)
 ├── Gesture Module (OpenCV)
              ↓
      Command Interpretation Layer
              ↓
         Motion Control System
              ↓
         Smart Car Execution

## 🔧 How to Run the Car
Here is the updated final section for your **README.md**, detailing how to run the car across its different control modes.

---

## 🔧 How to Run the Car

### 1. Hardware Initialization

* **Connect the Arduino**: Plug your Arduino into your computer via USB.
* **Identify the Serial Port**: Open the Arduino IDE or check your system settings to find the correct port (e.g., `/dev/cu.usbmodem1101` on macOS or `COM3` on Windows).
* **Upload Firmware**: Open the `Arduino_Code` folder in the Arduino IDE and upload the code to your board to enable the motor driver and sensors.

### 2. Running Control Modules

You can run any of the three control modes independently from your terminal:

#### 🎙️ Voice Control Mode

1. Open `VoiceControl.py` and ensure your **Gemini** and **ElevenLabs** API keys are set.
2. Run the script:
```bash
python VoiceControl.py

```

3. Press **Enter** to start listening, speak a command (e.g., "Go forward"), and the robot will execute the move and reply.

#### ✋ Gesture Control Mode

1. Ensure your camera (or iPhone via Continuity Camera) is active.
2. Run the script:
```bash
python new_gesture_control.py

```

3. Use your hand in front of the camera:
* **Open Palm**: Forward
* **Fist**: Stop
* **Scissors (Two Fingers)**: Hard Left


#### 👁️ AI Vision Mode

1. Run the YOLOv8-powered autonomous script:
```bash
python new_vision_control.py

```

2. The car will automatically navigate and steer away from obstacles detected in the red "danger zone" on your screen.

### 3. Emergency Stop

* In any Python terminal, press **'q'** to stop the program.
* The system is programmed to send a final **'x'** command to the Arduino to immediately cut power to the motors for safety.

---


---

# 🚗 Wall•E - Multimodal Smart Interactive Robot

**Wall•E** is an advanced robotic vehicle designed for the UTRA hackathon. It integrates cutting-edge AI to enable seamless interaction through **Natural Language**, **Hand Gestures**, and **Autonomous Vision**, specifically tuned for challenging off-road environments.

---

## ✨ Key Features

### 🎙️ AI Voice Interaction (Gemini + ElevenLabs)

* 
**Semantic Command Processing**: Uses the **Gemini-3-Flash** model to interpret natural speech and map it to robot actions like "forward," "stop," or "auto mode".


* 
**Natural Speech Synthesis**: Generates high-fidelity AI voice feedback using **ElevenLabs**, allowing the robot to "talk back" to the user.


* 
**Low-Latency Execution**: Commands are sent to the hardware via Serial immediately before the AI generates a verbal response to ensure responsiveness.



### ✋ Precision Gesture Control (MediaPipe)

* 
**Real-time Tracking**: Utilizes **OpenCV** and **MediaPipe Hands** to track finger landmarks and coordinates.


* 
**Intuitive Mapping**: Features a custom gesture library (e.g., Scissors for Hard Left, Thumbs-up for Backward, Fist for Stop).


* 
**Command Deduplication**: Implements logic to prevent flooding the Serial buffer by only sending commands when a gesture state changes.



### 👁️ Autonomous Vision & Obstacle Avoidance (YOLOv8)

* 
**Object Detection**: Runs a **YOLOv8-nano** model in real-time to identify obstacles in the robot's path.


* 
**Spatial Logic**: Divides the camera frame into Left, Center, and Right sectors to calculate steering decisions based on obstacle proximity.


* 
**Safety Thresholds**: Features a "Red Danger Line" logic where objects crossing 50% of the frame height trigger immediate avoidance maneuvers.



### 🏆 Off-Road Competition Logic (Arduino C++)

* 
**High-Torque Tuning**: Custom motor profiles designed to prevent getting stuck on uneven terrain.


* **Multi-Stage Mission**:
* 
**Stage 0**: Line-following entry to find the main track.


* 
**Stage 1**: Aggressive racing with a 90° pivot-and-return obstacle avoidance algorithm.




* 
**Color Sensing**: Automatically reacts to environmental markers: Blue (Pickup), Green (Speed Control), and Red (Track Locking).



---

## 🛠️ System Architecture

```text
       [ PERCEPTION ]              [ DECISION ]              [ EXECUTION ]
  ----------------------      ----------------------    ----------------------
  Voice (SpeechRecog)   -->   Gemini 1.5 Flash      -->   Arduino Mega/Uno
  Gestures (MediaPipe)  -->   Python Logic Layer    -->   L298N Motor Driver
  Vision (YOLOv8)       -->   Spatial Mapping       -->   Off-Road Chassis

```

---

## 🚀 Getting Started

### 1. Prerequisites

Install the required Python dependencies:

```bash
pip install opencv-python ultralytics mediapipe google-genai elevenlabs pyserial speechrecognition

```

### 2. Hardware Setup

* Connect the Arduino via USB (Default Port: `/dev/cu.usbmodem1101`).


* Ensure the **TCS3200 Color Sensor** and **Ultrasonic Sensor** are calibrated.



### 3. Run Modules

* 
**Voice Mode**: `python VoiceControl.py` (Requires API Keys).


* 
**Gesture Mode**: `python new_gesture_control.py`.


* 
**Vision Mode**: `python new_vision_control.py`.



---

## 📂 Repository Structure

* 
`Arduino_Code`: Low-level firmware and off-road navigation logic.


* 
`VoiceControl.py`: Integration of Gemini AI and ElevenLabs TTS.


* 
`new_gesture_control.py`: Hand-tracking control system.


* 
`new_vision_control.py`: YOLOv8-based autonomous obstacle avoidance.



---

## ⚖️ License

This project is licensed under the **MIT License**.
© 2026 Interalab.

---

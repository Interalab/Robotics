import cv2
import time
import serial
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw

# ================= CONFIGURATION =================
SERIAL_ENABLED = True 
SERIAL_PORT = '/dev/cu.usbmodem1101'  # Update this to your actual serial port path
BAUD_RATE = 9600
# =================================================

# --- Initialize Serial Communication ---
ser = None
last_command = None 

if SERIAL_ENABLED:
    try:
        # Initialize serial connection with 1-second timeout
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        # Required delay for Arduino to reset after serial initialization
        time.sleep(2) 
        # Send '0' to ensure the car enters Manual Mode initially
        ser.write(b'0')
        print(f"✅ Serial connected: {SERIAL_PORT}. Switched to Manual Mode.")
    except Exception as e:
        print(f"❌ Serial connection failed: {e}")
        SERIAL_ENABLED = False

# --- Initialize MediaPipe Hands Solution ---
# static_image_mode=False treats the input as a video stream
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5
)

def get_gesture(fingers, hand_lms):
    """
    Decodes the finger state list into specific vehicle movement commands.
    
    Args:
        fingers (list): A list of 5 integers (0 or 1) representing thumb to pinky state.
        hand_lms: MediaPipe hand landmarks object (reserved for spatial logic).
        
    Returns:
        tuple: (Display String, Command Character)
    """
    # STOP: All fingers closed (Fist)
    if fingers == [0, 0, 0, 0, 0]:
        return "STOP (0)", "x"
    
    # FORWARD: Five fingers open (allows minor thumb detection error)
    if fingers == [1, 1, 1, 1, 1] or fingers == [0, 1, 1, 1, 1]:
        return "FORWARD (5)", "w"
    
    # HARD LEFT: Index and Middle fingers open (Scissors gesture)
    if fingers == [0, 1, 1, 0, 0]:
        return "HARD LEFT (2)", "a"
    
    # HARD RIGHT: Index, Middle, and Ring fingers open
    if fingers == [0, 1, 1, 1, 0]:
        return "HARD RIGHT (3)", "d"
    
    # BACKWARD: Only thumb open (Thumbs-up gesture)
    if fingers == [1, 0, 0, 0, 0]:
        return "BACKWARD (1)", "s"
        
    return "UNKNOWN", "None"

# --- Main Video Capture Loop ---
# Use index 1 for external cameras (e.g., iPhone/Continuity Camera) or 0 for built-in
cap = cv2.VideoCapture(1) 
p_time = 0

print("🚀 Gesture Control System Started! Press 'q' to exit.")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    # Flip image horizontally for a natural mirror-like user experience
    img = cv2.flip(img, 1) 
    # MediaPipe requires RGB images; OpenCV uses BGR by default
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    cmd_char = "None"
    display_text = "WAITING"

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Visualize hand skeleton connections
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            # --- Finger State Detection Logic ---
            fingers = []
            
            # Thumb: Check if the tip (ID 4) is outside the IP joint (ID 3) on the X-axis
            # Note: This logic assumes a right hand facing the camera
            if hand_lms.landmark[4].x < hand_lms.landmark[3].x:
                fingers.append(1)
            else: 
                fingers.append(0)
            
            # Other 4 Fingers: Check if the tip Y-coordinate is above the PIP joint
            # In computer vision, Y-axis increases downwards
            for tip in [8, 12, 16, 20]:
                if hand_lms.landmark[tip].y < hand_lms.landmark[tip-2].y:
                    fingers.append(1)
                else: 
                    fingers.append(0)

            # Map detected finger states to car commands
            display_text, cmd_char = get_gesture(fingers, hand_lms)

            # --- Serial Transmission Logic ---
            # Implements command deduplication to avoid flooding the serial buffer
            if SERIAL_ENABLED and cmd_char != "None":
                if cmd_char != last_command:
                    ser.write(cmd_char.encode())
                    print(f"📡 Sending: {cmd_char} ({display_text})")
                    last_command = cmd_char

    # --- UI Rendering ---
    # Draw status background and overlay current control command
    cv2.rectangle(img, (0, 0), (350, 60), (0, 0, 0), -1)
    cv2.putText(img, f"CONTROL: {display_text}", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Hand Control Mode", img)
    
    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

# --- Resource Cleanup ---
if ser:
    # Safety: Stop the car motors before closing connection
    ser.write(b'x') 
    ser.close()
    print("🔒 Serial connection closed.")

cap.release()
cv2.destroyAllWindows()
import cv2
import torch
import serial
import time
from ultralytics import YOLO

# ================= 1. HARDWARE COMMUNICATION CONFIG =================
# Define the serial port address (specific to macOS/Unix-like systems)
SERIAL_PORT = '/dev/cu.usbmodem101'  
# Baud rate must match the configuration in your Arduino sketch
BAUD_RATE = 9600                     

try:
    # Initialize serial connection with a short timeout for responsiveness
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
    print(f"✅ Serial connected successfully: {SERIAL_PORT}")
    
    # [CORE LOGIC] Wait for Arduino bootloader to reset, then force Manual Mode (mode 0)
    time.sleep(2)  
    ser.write(b'0') 
    print("📡 Mode '0' sent: Car switched to Manual Control Mode.")
except Exception as e:
    print(f"⚠️ Serial connection failed, entering Preview-only mode: {e}")
    ser = None

# ================= 2. VISION MODEL INITIALIZATION =================
# Load the pre-trained YOLOv8-nano model (lightweight for real-time inference)
model = YOLO('yolov8n.pt') 
# Use Apple Silicon GPU (MPS) if available; otherwise, fallback to CPU
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
model.to(device)

def get_drive_command(boxes, frame_width, frame_height):
    """
    Implements obstacle avoidance logic based on spatial object detection.
    
    Args:
        boxes: List of bounding boxes from YOLO results.
        frame_width (int): Width of the video frame.
        frame_height (int): Height of the video frame.
        
    Returns:
        tuple: (Command Character, Descriptive String)
    """
    # [CORE SETTING] Danger zone threshold: objects crossing 50% height trigger avoidance
    danger_line_y = frame_height * 0.5 
    
    # Divide the horizontal frame into three equal sectors: Left, Center, Right
    left_boundary = frame_width // 3
    right_boundary = 2 * (frame_width // 3)
    
    center_blocked = False
    left_blocked = False
    right_blocked = False

    for box in boxes:
        # xyxy format: [top-left-x, top-left-y, bottom-right-x, bottom-right-y]
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        
        # Obstacle Check: Is the bottom of the object (y2) below the danger line?
        if y2 > danger_line_y:
            # Determine which horizontal sectors are obstructed by the object
            if x1 < left_boundary:
                left_blocked = True
            if x2 > right_boundary:
                right_blocked = True
            if (x1 < right_boundary and x2 > left_boundary):
                center_blocked = True

    # --- Decision Tree Logic ---
    if center_blocked:
        if not left_blocked:
            return 'a', "HARD LEFT"   # Front blocked, path clear on left
        elif not right_blocked:
            return 'd', "HARD RIGHT"  # Front/Left blocked, path clear on right
        else:
            return 'x', "STOP"        # No clear path in any direction
    
    return 'w', "FORWARD"             # Path clear in center

# ================= 3. CAMERA & MAIN LOOP =================
def open_iphone_camera():
    """
    Attempts to initialize the camera using common indices.
    Priority: Index 1/2 (Continuity Camera), Index 0 (FaceTime Camera).
    """
    for index in [1, 2, 0]:
        print(f"Attempting to open camera index: {index}...")
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Mandatory handshake delay for Continuity Camera to prevent black frame
            time.sleep(2.0) 
            success, _ = cap.read()
            if success:
                print(f"✅ Successfully connected to camera {index}")
                return cap
            cap.release()
    return None

cap = open_iphone_camera()
if not cap:
    print("❌ No camera found. Ensure iPhone is unlocked and trusted.")
    exit()

last_cmd = ''  # Storage for command deduplication

while True:
    success, frame = cap.read()
    if not success: 
        continue 

    h, w, _ = frame.shape
    draw_line_y = int(h * 0.5)

    # Run YOLOv8 inference (silent mode enabled to keep console clean)
    results = model.predict(frame, conf=0.35, device=device, verbose=False)
    
    # Calculate driving decision based on current detection
    cmd_char, cmd_text = get_drive_command(results[0].boxes, w, h)
    
    # --- Serial Communication Logic ---
    # Only send a byte if the command has changed (reduces serial buffer congestion)
    if ser and cmd_char != last_cmd:
        ser.write(cmd_char.encode())
        last_cmd = cmd_char
        print(f"📡 Serial Command: {cmd_text} ({cmd_char})")

    # --- Visualization & UI ---
    # Draw detected objects and bounding boxes
    annotated_frame = results[0].plot()
    
    # Draw vertical grid lines for the three sectors
    cv2.line(annotated_frame, (w//3, 0), (w//3, h), (200, 200, 200), 1)
    cv2.line(annotated_frame, (2*w//3, 0), (2*w//3, h), (200, 200, 200), 1)
    
    # Draw the [Red Danger Threshold Line]
    cv2.line(annotated_frame, (0, draw_line_y), (w, draw_line_y), (0, 0, 255), 3)
    
    # Display the current command on screen
    text_color = (0, 0, 255) if cmd_char == 'x' else (0, 255, 0)
    cv2.putText(annotated_frame, f"CMD: {cmd_text}", (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, text_color, 3)

    cv2.imshow("Mac-Robot AI Vision Control", annotated_frame)
    
    # Press 'q' to release resources and stop the program
    if cv2.waitKey(1) & 0xFF == ord("q"):
        if ser: 
            ser.write(b'x')  # Emergency stop command
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
if ser: 
    ser.close()
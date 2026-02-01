import cv2
import time
import sys
import serial # 需要先安装 pyserial
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw

# ================= 配置区 =================
SERIAL_ENABLED = False  # 调试阶段设为 False，连接机器车后设为 True
SERIAL_PORT = '/dev/cu.usbserial-110' # 替换为你的机器车串口路径
BAUD_RATE = 9600
# =========================================

# 初始化串口
ser = None
if SERIAL_ENABLED:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"成功连接到串口: {SERIAL_PORT}")
    except Exception as e:
        print(f"串口连接失败: {e}")
        SERIAL_ENABLED = False

# 初始化 MediaPipe
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5
)

def get_gesture(fingers, hand_lms):
    """根据手指状态返回控制指令"""
    if fingers == [0, 0, 0, 0, 0]:
        return "STOP", "S"
    if fingers == [1, 1, 1, 1, 1] or fingers == [0, 1, 1, 1, 1]:
        return "FORWARD", "F"
    if fingers == [0, 1, 0, 0, 0]: # 仅食指伸出
        x_coord = hand_lms.landmark[8].x
        if x_coord < 0.4: # 镜像后，左侧是 0
            return "TURN LEFT", "L"
        elif x_coord > 0.6:
            return "TURN RIGHT", "R"
        return "POINTING", "P"
    if fingers == [1, 0, 0, 0, 0]: # 仅大拇指（假设为后退）
        return "BACKWARD", "B"
    return "UNKNOWN", "None"

cap = cv2.VideoCapture(1) # iPhone 摄像头索引
p_time = 0

print("系统启动成功！识别结果将显示在窗口左上角。")

while cap.isOpened():
    success, img = cap.read()
    if not success: break

    img = cv2.flip(img, 1) # 镜像处理
    h, w, c = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    current_command = "None"
    display_text = "WAITING..."

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            # 手指状态识别逻辑
            fingers = []
            # 大拇指 (根据 x 坐标判断)
            if hand_lms.landmark[4].x < hand_lms.landmark[3].x:
                fingers.append(1)
            else: fingers.append(0)
            
            # 其他四个手指 (根据 y 坐标判断)
            for tip in [8, 12, 16, 20]:
                if hand_lms.landmark[tip].y < hand_lms.landmark[tip-2].y:
                    fingers.append(1)
                else: fingers.append(0)

            # 获取指令
            display_text, current_command = get_gesture(fingers, hand_lms)

            # 发送串口指令
            if SERIAL_ENABLED and current_command != "None":
                ser.write(current_command.encode())

    # 绘制 UI
    cv2.rectangle(img, (0, 0), (300, 100), (0, 0, 0), -1)
    cv2.putText(img, f"CMD: {display_text}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # FPS 显示
    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time
    cv2.putText(img, f"FPS: {int(fps)}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    cv2.imshow("Car Gesture Controller", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

if ser: ser.close()
cap.release()
cv2.destroyAllWindows()

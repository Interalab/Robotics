import cv2
import time
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw

# 初始化模型
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# 尝试捕获 iPhone (通常是 1 或 2)
cap = cv2.VideoCapture(1) 

p_time = 0
print("正在点亮 iPhone 摄像头... 按 'q' 退出")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        print("无法获取画面，请检查 iPhone 是否处于锁屏待机状态，或尝试切换 VideoCapture 索引（0, 1, 2）")
        break

    img = cv2.flip(img, 1) # 镜像
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time
    cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("iPhone Hand Tracker", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
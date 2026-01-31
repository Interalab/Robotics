import cv2
import torch
from ultralytics import YOLO

# 1. 初始化模型并使用 Mac 的 MPS 加速
# 第一次运行会自动下载 yolov8n.pt
model = YOLO('yolov8n.pt') 
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
model.to(device)

def get_drive_command(boxes, frame_width, frame_height):
    """
    避障核心逻辑：三区判定
    """
    # 定义判定区域（左、中、右）
    left_boundary = frame_width // 3
    right_boundary = 2 * (frame_width // 3)
    
    # 警戒线：物体底部 y 坐标超过画面高度的 2/3 则视为危险
    danger_line = 2 * (frame_height // 3)
    
    center_blocked = False
    left_blocked = False
    right_blocked = False

    for box in boxes:
        # 获取坐标 (x1, y1, x2, y2)
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        bottom_y = y2
        center_x = (x1 + x2) / 2

        # 只有在“靠近”小车的情况下才判定为障碍物
        if bottom_y > danger_line:
            if center_x < left_boundary:
                left_blocked = True
            elif center_x > right_boundary:
                right_blocked = True
            else:
                center_blocked = True

    # 决策输出
    if not center_blocked:
        return "FORWARD (直行)"
    elif not left_blocked:
        return "TURN LEFT (左转)"
    elif not right_blocked:
        return "TURN RIGHT (右转)"
    else:
        return "STOP (紧急停止)"

# 2. 打开 iPhone 摄像头 (通常索引为 1 或 0)
cap = cv2.VideoCapture(1)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 3. 运行推理
    results = model.predict(frame, conf=0.5, device=device, verbose=False)
    
    # 获取检测框
    annotated_frame = results[0].plot()
    boxes = results[0].boxes

    # 4. 获取驾驶逻辑输出
    command = get_drive_command(boxes, frame.shape[1], frame.shape[2])
    
    # 在屏幕上显示指令
    cv2.putText(annotated_frame, f"CMD: {command}", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # 绘制三区参考线
    h, w, _ = frame.shape
    cv2.line(annotated_frame, (w//3, 0), (w//3, h), (255, 255, 255), 1)
    cv2.line(annotated_frame, (2*w//3, 0), (2*w//3, h), (255, 255, 255), 1)
    cv2.line(annotated_frame, (0, 2*h//3), (w, 2*h//3), (0, 0, 255), 2) # 警戒线

    # 5. 显示画面
    cv2.imshow("iPhone Obstacle Avoidance", annotated_frame)

    # 打印实时指令给小车控制模块（后续通过串口发送）
    print(f"Robot Command: {command}")

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
import cv2
from ultralytics import YOLO
from PIL import ImageFont, ImageDraw, Image
import numpy as np

# YOLO 모델 로드
model = YOLO('best.pt')

# 한글 폰트 로드 (경로에 NotoSansKR-Regular.ttf가 있어야 함)
font_path = 'NotoSansKR-Regular.ttf'
font = ImageFont.truetype(font_path, 30)

# 웹캠 열기
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.predict(source=frame, conf=0.5, verbose=False)
    battery_detected = False

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_name = model.names[cls_id]
            label = f"{class_name} {conf:.2f}"

            # 조건: 클래스명이 'battery'이고 confidence가 0.6 이상
            if class_name == 'item' and conf >= 0.6:
                battery_detected = True

            # 사각형과 라벨 표시
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 메시지 결정
    if battery_detected:
        message = "감지된 사물은 건전지입니다."
        color = (0, 255, 0)
    else:
        message = "건전지가 아닙니다"
        color = (0, 0, 255)

    # 메시지 출력 (PIL 사용)
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)
    draw.text((10, 10), message, font=font, fill=color)
    frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    cv2.imshow("Battery Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

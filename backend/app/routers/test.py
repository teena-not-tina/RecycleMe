from ultralytics import YOLO
import cv2

model = YOLO(r"D:\student\midleproject\RecycleMe-4\backend\ml_model\main_best1.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # 모델에 프레임 전달 및 추론
    results = model.predict(source=frame, save=False, conf=0.25, verbose=False)

    # 결과 시각화
    annotated_frame = results[0].plot()

    # 출력
    cv2.imshow("YOLOv8 Detection", annotated_frame)

    # 'q' 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
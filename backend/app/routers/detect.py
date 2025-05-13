from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os

router = APIRouter()

# YOLO 모델 초기화
YOLO_CONFIG_PATH = "path/to/yolo.cfg"  # YOLO 설정 파일 경로
YOLO_WEIGHTS_PATH = "path/to/yolo.weights"  # YOLO 가중치 파일 경로
YOLO_CLASSES_PATH = "path/to/coco.names"  # 클래스 이름 파일 경로

# Load YOLO model
net = cv2.dnn.readNet(YOLO_WEIGHTS_PATH, YOLO_CONFIG_PATH)
with open(YOLO_CLASSES_PATH, "r") as f:
    classes = [line.strip() for line in f.readlines()]

@router.post("/api/detect")
async def detect_objects(file: UploadFile = File(...)):
    try:
        # 이미지 읽기
        image_data = await file.read()
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # YOLO 모델로 객체 탐지
        blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        detections = net.forward(output_layers)

        # 탐지된 객체 정보 저장
        height, width, _ = img.shape
        results = []
        for output in detections:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:  # 신뢰도 임계값
                    center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype("int")
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    results.append({
                        "class": classes[class_id],
                        "confidence": float(confidence),
                        "box": [x, y, int(w), int(h)]
                    })

        return JSONResponse(content={"detections": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
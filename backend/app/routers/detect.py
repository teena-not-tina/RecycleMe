from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from ultralytics import YOLO
import cv2
import numpy as np
import os

router = APIRouter()

# 첫 번째 YOLO 모델
model1 = YOLO(r"backend\ml_model\main_best1.pt") 
# 두 번째 YOLO 모델 
model2 = YOLO(r"backend\ml_model\battery_best.pt")

# # Load YOLO model
# net = cv2.dnn.readNet(YOLO_WEIGHTS_PATH, YOLO_CONFIG_PATH)
# with open(YOLO_CLASSES_PATH, "r") as f:
#     classes = [line.strip() for line in f.readlines()]

@router.post("/api/detect")
async def detect_objects(file: UploadFile = File(...)):
    try:
        # 이미지 읽기
        image_data = await file.read()
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # 첫 번째 YOLO 모델로 객체 탐지
        results1 = model1.predict(source=img, save=False, conf=0.5)
        detections1 = []
        for result in results1:
            for box in result.boxes:
                detections1.append({
                    "class": model1.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "box": box.xyxy.tolist()
                })

        # 'other'가 있으면 두 번째 모델 실행
        if any(d["class"] == "other" for d in detections1):
            results2 = model2.predict(source=img, save=False, conf=0.5)
            detections2 = []
            for result in results2:
                for box in result.boxes:
                    detections2.append({
                        "class": model2.names[int(box.cls)],
                        "confidence": float(box.conf),
                        "box": box.xyxy.tolist()
                    })
            # 두 번째 모델 결과만 반환하거나, 아래처럼 합쳐서 반환 가능
            content={
                "detections": detections1,
                "other_detections": detections2
            }
            print("2개 모델 모두 실행한 결과 : " + content) # Debugging line

            return JSONResponse(content)

        print(detections1) # Debugging line

        # 'other'가 없으면 첫 번째 결과만 반환
        return JSONResponse(content={"detections": detections1})
   
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    

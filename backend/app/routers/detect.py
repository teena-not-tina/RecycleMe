from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# 첫 번째 YOLO 모델
model1 = YOLO(r"backend\ml_model\main_best1.pt") 
# 두 번째 YOLO 모델 
model2 = YOLO(r"backend\ml_model\battery_best.pt")

# # Load YOLO model
# net = cv2.dnn.readNet(YOLO_WEIGHTS_PATH, YOLO_CONFIG_PATH)
# with open(YOLO_CLASSES_PATH, "r") as f:
#     classes = [line.strip() for line in f.readlines()]

# /detect/api/detect (main.py와 detect.py의 조합) 으로 연결되고 있었음;
@router.post("/")
async def detect_objects(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

        # 이미지 읽기
        image_data = await file.read()
        np_img = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # 디코딩된 이미지 확인
        if img is None:
            logger.error("Failed to decode image")
            return JSONResponse(
                content={"error": "Failed to decode image"}, 
                status_code=400
            )

        # 첫 번째 YOLO 모델로 객체 탐지
        logger.info("Running first model detection")
        results1 = model1.predict(source=img, save=False, conf=0.5)
        detections1 = []
        for result in results1:
            for box in result.boxes:
                class_id = int(box.cls)
                detection = {
                    "class": model1.names[class_id],
                    "confidence": float(box.conf),
                    "box": [[float(x) for x in xyxy] for xyxy in box.xyxy]
                }
                detections1.append(detection)
                logger.info(f"Detected: {detection['class']} with confidence {detection['confidence']}")

        # 'other'가 있으면 두 번째 모델 실행
        other_found = any(d["class"] == "other" for d in detections1)
        other_detections = []
        if other_found:
            logger.info("'Other' detected, running second model")
            results2 = model2.predict(source=img, save=False, conf=0.5)
            
            for result in results2:
                for box in result.boxes:
                    class_id = int(box.cls)
                    detection = {
                        "class": model2.names[class_id],
                        "confidence": float(box.conf),
                        "box": [[float(x) for x in xyxy] for xyxy in box.xyxy]
                    }
                    other_detections.append(detection)
                    logger.info(f"Secondary detection: {detection['class']} with confidence {detection['confidence']}")
        
            # Prepare response
        response = {
            "detections": detections1
        }

        if other_detections:
            response["other_detections"] = other_detections
        
        logger.info(f"Returning response with {len(detections1)} primary detections and {len(other_detections)} secondary detections")
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error in detect_objects: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": str(e)}, 
            status_code=500
        )
    

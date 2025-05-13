import cv2
import numpy as np
import base64
from typing import Optional, Tuple, List
import io
from PIL import Image
import requests
from app.config import settings

def decode_base64_image(base64_string: str) -> Optional[np.ndarray]:
    """Base64 인코딩된 이미지 문자열을 OpenCV 이미지로 변환"""
    try:
        # Base64 헤더 제거 (있는 경우)
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]
            
        # Base64 디코드
        img_data = base64.b64decode(base64_string)
        
        # 바이트 배열을 넘파이 배열로 변환
        nparr = np.frombuffer(img_data, np.uint8)
        
        # 이미지 디코드
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
        return None

def load_image_from_url(url: str) -> Optional[np.ndarray]:
    """URL에서 이미지 로드"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error loading image from URL: {e}")
        return None

def preprocess_image(image: np.ndarray, target_size: Tuple[int, int] = (640, 640)) -> np.ndarray:
    """이미지 전처리: 크기 조정 및 정규화"""
    try:
        # 이미지 크기 조정
        img_resized = cv2.resize(image, target_size)
        
        # BGR -> RGB 변환 (YOLO는 RGB 이미지 사용)
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        
        # 픽셀값 정규화 [0, 1]
        img_normalized = img_rgb / 255.0
        
        return img_normalized
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        raise

def encode_image_to_base64(image: np.ndarray) -> str:
    """OpenCV 이미지를 Base64 문자열로 인코딩"""
    try:
        # 이미지를 JPEG 형식으로 인코딩
        _, buffer = cv2.imencode('.jpg', image)
        
        # Base64로 인코딩
        img_str = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Error encoding image to base64: {e}")
        return ""

def draw_detections(image: np.ndarray, detections: List[dict], thickness: int = 2) -> np.ndarray:
    """감지된 객체를 이미지에 표시"""
    try:
        img_copy = image.copy()
        
        # 클래스별 색상 정의
        colors = {
            'paper': (0, 255, 0),       # 녹색
            'plastic': (255, 0, 0),     # 파란색
            'can': (0, 0, 255),         # 빨간색
            'vinyl': (255, 255, 0),     # 청록색
            'glass': (0, 255, 255),     # 노란색
            'styrofoam': (255, 0, 255), # 분홍색
            'battery': (128, 0, 128),   # 보라색
            'fluorescent': (255, 165, 0), # 주황색
            'bulky_waste': (139, 69, 19), # 갈색
            'other': (128, 128, 128)    # 회색
        }
        
        for det in detections:
            # 바운딩 박스 좌표
            x1, y1, x2, y2 = det['box'].x1, det['box'].y1, det['box'].x2, det['box'].y2
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # 클래스 및 신뢰도
            category = det['category']
            confidence = det['confidence']
            
            # 색상 선택
            color = colors.get(category, (128, 128, 128))
            
            # 바운딩 박스 그리기
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, thickness)
            
            # 라벨 텍스트
            label = f"{category}: {confidence:.2f}"
            
            # 라벨 배경 크기 계산
            (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # 라벨 배경 그리기
            cv2.rectangle(img_copy, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
            
            # 라벨 텍스트 그리기
            cv2.putText(img_copy, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        return img_copy
    except Exception as e:
        print(f"Error drawing detections: {e}")
        return image

def validate_image_size(image_data: bytes) -> bool:
    """이미지 크기 검증"""
    return len(image_data) <= settings.MAX_IMAGE_SIZE
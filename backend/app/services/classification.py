import os
import cv2
import torch
import numpy as np
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from app.models.recycling import ClassificationResult, Detection, DetectionBox, RecyclingCategory
from app.utils.image import decode_base64_image, load_image_from_url, preprocess_image
from app.utils.firebase_admin import save_classification_result, upload_image_to_storage
from app.config import settings

# 전역 변수로 YOLO 모델 로드
model = None

def load_model():
    """YOLO 모델 로드"""
    global model
    if model is None:
        try:
            # 모델 경로 확인
            model_path = settings.ML_MODEL_PATH
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found at {model_path}")
            
            # YOLO 모델 로드
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
            
            # 추론 설정
            model.conf = 0.4  # 신뢰도 임계값
            model.iou = 0.45  # IoU 임계값
            model.agnostic = False  # 클래스 무관 NMS
            model.multi_label = False  # 다중 레이블 허용
            model.max_det = 10  # 최대 감지 수
            
            print(f"Model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            raise

def get_class_mapping() -> Dict[int, str]:
    """클래스 ID를 카테고리 이름으로 매핑"""
    try:
        classes_path = settings.ML_MODEL_CLASSES
        if not os.path.exists(classes_path):
            # 기본 클래스 맵 반환
            return {
                0: "paper",
                1: "plastic",
                2: "can",
                3: "vinyl",
                4: "glass",
                5: "styrofoam",
                6: "battery",
                7: "fluorescent",
                8: "bulky_waste",
                9: "other"
            }
        
        # 클래스 파일에서 맵핑 로드
        class_map = {}
        with open(classes_path, 'r') as f:
            for i, line in enumerate(f.readlines()):
                class_name = line.strip()
                class_map[i] = class_name
        
        return class_map
    except Exception as e:
        print(f"Error loading class mapping: {e}")
        # 기본 클래스 맵 반환
        return {
            0: "paper",
            1: "plastic",
            2: "can", 
            3: "vinyl",
            4: "glass",
            5: "styrofoam",
            6: "battery",
            7: "fluorescent", 
            8: "bulky_waste",
            9: "other"
        }

def classify_image(image_data: Optional[str] = None, image_url: Optional[str] = None) -> Tuple[ClassificationResult, List[Dict[str, Any]]]:
    """이미지 분류 수행"""
    global model
    
    # 모델 로드 (필요시)
    if model is None:
        load_model()
    
    try:
        # 이미지 데이터 로드
        if image_data:
            img = decode_base64_image(image_data)
        elif image_url:
            img = load_image_from_url(image_url)
        else:
            raise ValueError("Either image_data or image_url must be provided")
        
        if img is None:
            raise ValueError("Failed to load image")
        
        # 이미지 전처리
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 객체 감지 수행
        results = model(img_rgb)
        
        # 결과 파싱
        predictions = results.pandas().xyxy[0]
        
        # 클래스 매핑 로드
        class_map = get_class_mapping()
        
        # Detection 객체 생성
        detections = []
        for _, row in predictions.iterrows():
            try:
                class_id = int(row['class'])
                class_name = class_map.get(class_id, "other")
                
                # 카테고리로 변환
                category = RecyclingCategory(class_name)
                
                # Detection 객체 생성
                detection = Detection(
                    category=category,
                    confidence=float(row['confidence']),
                    box=DetectionBox(
                        x1=float(row['xmin']),
                        y1=float(row['ymin']),
                        x2=float(row['xmax']),
                        y2=float(row['ymax'])
                    )
                )
                detections.append(detection)
            except ValueError:
                # 알 수 없는 카테고리는 'other'로 처리
                print(f"Unknown category: {class_name}, using 'other' instead")
                detection = Detection(
                    category=RecyclingCategory.OTHER,
                    confidence=float(row['confidence']),
                    box=DetectionBox(
                        x1=float(row['xmin']),
                        y1=float(row['ymin']),
                        x2=float(row['xmax']),
                        y2=float(row['ymax'])
                    )
                )
                detections.append(detection)
        
        # 결과 저장
        image_id = str(uuid.uuid4())
        classification_result = ClassificationResult(
            image_id=image_id,
            detections=detections,
            timestamp=datetime.now()
        )
        
        # 특수 메시지 생성
        special_messages = generate_special_messages(classification_result)
        
        # Firebase에 결과 저장
        result_dict = classification_result.dict()
        save_classification_result(result_dict)
        
        return classification_result, special_messages
        
    except Exception as e:
        print(f"Error classifying image: {e}")
        raise

def generate_special_messages(result: ClassificationResult) -> List[Dict[str, Any]]:
    """분류 결과에 따른 특수 메시지 생성"""
    messages = []
    
    # 배터리 발견 시 메시지
    if result.has_battery:
        messages.append({
            "type": "battery",
            "message": "건전지 수거함 위치가 궁금하시면 '주소+ 건전지 수거함'이라고 검색하세요",
            "action": "search_battery_bins"
        })
    
    # 기타 쓰레기 발견 시 메시지
    if result.has_other or result.has_bulky_waste:
        messages.append({
            "type": "other",
            "message": "종량제 봉투를 사용하시거나 대형폐기물일 경우 '관악구 장롱 수수료'라고 검색하세요",
            "action": "search_waste_fees"
        })
    
    # 재활용 가능 항목 발견 시 포인트 적립 메시지
    recyclable_count = result.recyclable_count
    if recyclable_count > 0:
        points = recyclable_count * settings.POINTS_PER_RECYCLABLE
        messages.append({
            "type": "points",
            "message": f"재활용 가능한 항목 {recyclable_count}개가 감지되었습니다. 적립금을 적립하시겠습니까?",
            "points": points,
            "action": "add_points"
        })
    
    return messages

def find_battery_bins(address: str) -> List[Dict[str, Any]]:
    """주소 기반으로 가장 가까운 건전지 수거함 위치 찾기"""
    import pandas as pd
    from difflib import get_close_matches
    
    try:
        # CSV 파일 로드
        csv_path = settings.BATTERY_BINS_CSV
        if not os.path.exists(csv_path):
            return [{"message": f"건전지 수거함 정보를 찾을 수 없습니다. (파일 없음: {csv_path})"}]
        
        # 데이터 로드
        df = pd.read_csv(csv_path)
        
        # 주소 열 이름 확인
        address_column = "지역" if "지역" in df.columns else "address"
        
        # 주소 목록 가져오기
        addresses = df[address_column].tolist()
        
        # 가장 유사한 주소 찾기
        matches = get_close_matches(address, addresses, n=3, cutoff=0.3)
        
        results = []
        for match in matches:
            row = df[df[address_column] == match].iloc[0]
            results.append({
                "address": match,
                "location": row.get("위치", "정보 없음"),
                "opening_hours": row.get("운영시간", "정보 없음"),
                "contact": row.get("연락처", "정보 없음")
            })
        
        if not results:
            return [{"message": "주변에 건전지 수거함을 찾을 수 없습니다."}]
            
        return results
    
    except Exception as e:
        print(f"Error finding battery bins: {e}")
        return [{"message": f"건전지 수거함 검색 중 오류 발생: {str(e)}"}]

def find_waste_fees(region: str, item: str) -> List[Dict[str, Any]]:
    """지역 및 품목 기반으로 폐기물 수수료 찾기"""
    import pandas as pd
    from difflib import get_close_matches
    
    try:
        # CSV 파일 로드
        csv_path = settings.WASTE_FEES_CSV
        if not os.path.exists(csv_path):
            return [{"message": f"폐기물 수수료 정보를 찾을 수 없습니다. (파일 없음: {csv_path})"}]
        
        # 데이터 로드
        df = pd.read_csv(csv_path)
        
        # 열 이름 확인
        region_column = "지역" if "지역" in df.columns else "region"
        item_column = "품목" if "품목" in df.columns else "item"
        
        # 지역 필터링
        df_region = df[df[region_column].str.contains(region)]
        
        # 지역 필터링 결과가 없으면 모든 지역 검색
        if df_region.empty:
            df_region = df
        
        # 품목 찾기
        items = df_region[item_column].tolist()
        matches = get_close_matches(item, items, n=3, cutoff=0.3)
        
        results = []
        for match in matches:
            rows = df_region[df_region[item_column] == match]
            for _, row in rows.iterrows():
                results.append({
                    "region": row[region_column],
                    "item": match,
                    "specification": row.get("규격", "정보 없음"),
                    "fee": row.get("수수료", "정보 없음")
                })
        
        if not results:
            return [{"message": f"{region}의 {item} 수수료 정보를 찾을 수 없습니다."}]
            
        return results
    
    except Exception as e:
        print(f"Error finding waste fees: {e}")
        return [{"message": f"폐기물 수수료 검색 중 오류 발생: {str(e)}"}]
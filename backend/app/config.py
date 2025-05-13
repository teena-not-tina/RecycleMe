
import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 기본 설정
    APP_NAME: str = "Recycling Classification API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API 설정
    API_V1_STR: str = "/api/v1"
    
    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # 프론트엔드 개발 서버
        "http://localhost:8000",  # 백엔드 서버
        "https://yourdomain.com",  # 프로덕션 도메인
    ]
    
    # Firebase 설정
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    FIREBASE_DATABASE_URL: str = os.getenv("FIREBASE_DATABASE_URL", "")
    
    # 포인트 설정
    POINTS_PER_RECYCLABLE: int = 10  # 재활용 가능 항목당 포인트
    
    # 모델 설정
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "ml_model/model.pt")
    ML_MODEL_CLASSES: str = os.getenv("ML_MODEL_CLASSES", "ml_model/classes.txt")
    
    # CSV 파일 경로
    BATTERY_BINS_CSV: str = os.getenv("BATTERY_BINS_CSV", "app/data/battery_bins.csv")
    WASTE_FEES_CSV: str = os.getenv("WASTE_FEES_CSV", "app/data/waste_fees.csv")
    
    # 이미지 설정
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스 생성
settings = Settings()
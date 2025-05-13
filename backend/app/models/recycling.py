
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class RecyclingCategory(str, Enum):
    # 재활용 가능 품목
    PAPER = "paper"
    PLASTIC = "plastic"
    CAN = "can"
    VINYL = "vinyl"
    GLASS = "glass"
    STYROFOAM = "styrofoam"
    
    # 분리배출 필요 품목
    BATTERY = "battery"
    FLUORESCENT = "fluorescent"
    BULKY_WASTE = "bulky_waste"
    
    # 기타
    OTHER = "other"
    
    @classmethod
    def recyclable_items(cls):
        """재활용 가능 품목 목록 반환"""
        return [
            cls.PAPER, 
            cls.PLASTIC, 
            cls.CAN, 
            cls.VINYL, 
            cls.GLASS, 
            cls.STYROFOAM
        ]
    
    @classmethod
    def special_disposal_items(cls):
        """특수 처리 필요 품목 목록 반환"""
        return [
            cls.BATTERY,
            cls.FLUORESCENT,
            cls.BULKY_WASTE
        ]

class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class Detection(BaseModel):
    category: RecyclingCategory
    confidence: float
    box: DetectionBox

class ClassificationResult(BaseModel):
    image_id: str
    detections: List[Detection]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def recyclable_count(self) -> int:
        """재활용 가능 품목 수 반환"""
        return sum(1 for d in self.detections if d.category in RecyclingCategory.recyclable_items())
    
    @property
    def has_battery(self) -> bool:
        """배터리 포함 여부 반환"""
        return any(d.category == RecyclingCategory.BATTERY for d in self.detections)
    
    @property
    def has_bulky_waste(self) -> bool:
        """대형 폐기물 포함 여부 반환"""
        return any(d.category == RecyclingCategory.BULKY_WASTE for d in self.detections)
    
    @property
    def has_other(self) -> bool:
        """기타 품목 포함 여부 반환"""
        return any(d.category == RecyclingCategory.OTHER for d in self.detections)

class ClassificationRequest(BaseModel):
    image_data: Optional[str] = None  # Base64 인코딩 이미지
    image_url: Optional[HttpUrl] = None  # 이미지 URL

class PointsEarnRequest(BaseModel):
    classification_id: str
    user_id: str

class ClassificationResponse(BaseModel):
    result: ClassificationResult
    points_eligible: int
    special_messages: List[Dict[str, Any]] = []
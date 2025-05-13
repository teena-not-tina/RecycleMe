from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, status, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import base64
import io

from app.models.user import User
from app.models.recycling import ClassificationRequest, ClassificationResponse, ClassificationResult
from app.routers.auth import get_current_user
from app.services.classification import classify_image, find_battery_bins, find_waste_fees
from app.utils.firebase_admin import upload_image_to_storage
from app.config import settings

router = APIRouter()

@router.post("/classify", response_model=ClassificationResponse)
async def classify_image_endpoint(
    request: ClassificationRequest,
    current_user: User = Depends(get_current_user)
):
    """이미지 분류 수행"""
    try:
        # 이미지 데이터 또는 URL 검증
        if not request.image_data and not request.image_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either image_data or image_url must be provided"
            )
        
        # 이미지 분류 수행
        result, special_messages = classify_image(
            image_data=request.image_data,
            image_url=request.image_url
        )
        
        # 포인트 계산
        points_eligible = result.recyclable_count * settings.POINTS_PER_RECYCLABLE
        
        # 응답 객체 생성
        response = ClassificationResponse(
            result=result,
            points_eligible=points_eligible,
            special_messages=special_messages
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )

@router.post("/upload", response_model=Dict[str, Any])
async def upload_image_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """이미지 업로드 및 분류"""
    try:
        # 이미지 파일 검증
        content_type = file.content_type
        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {content_type}. Allowed types: {settings.ALLOWED_IMAGE_TYPES}"
            )
        
        # 이미지 파일 읽기
        contents = await file.read()
        if len(contents) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.MAX_IMAGE_SIZE} bytes"
            )
        
        # Firebase Storage에 이미지 업로드
        image_url = upload_image_to_storage(contents, content_type)
        if not image_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image"
            )
        
        # 이미지 분류 수행
        result, special_messages = classify_image(image_url=image_url)
        
        # 포인트 계산
        points_eligible = result.recyclable_count * settings.POINTS_PER_RECYCLABLE
        
        # 응답 데이터 구성
        response_data = {
            "image_url": image_url,
            "result": result.dict(),
            "points_eligible": points_eligible,
            "special_messages": special_messages
        }
        
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload and classification failed: {str(e)}"
        )

@router.get("/battery-bins", response_model=List[Dict[str, Any]])
async def search_battery_bins(
    address: str = Query(..., description="건전지 수거함을 찾을 주소"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """주소 기반으로 건전지 수거함 위치 검색"""
    try:
        results = find_battery_bins(address)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Battery bin search failed: {str(e)}"
        )

@router.get("/waste-fees", response_model=List[Dict[str, Any]])
async def search_waste_fees(
    region: str = Query(..., description="지역 (예: 관악구)"),
    item: str = Query(..., description="폐기물 품목 (예: 장롱)"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """지역 및 품목 기반 폐기물 수수료 검색"""
    try:
        results = find_waste_fees(region, item)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Waste fee search failed: {str(e)}"
        )

@router.get("/webcam-classify", response_model=ClassificationResponse)
async def webcam_classify_endpoint(
    image_data: str = Query(..., description="Base64 인코딩된 웹캠 이미지"),
    current_user: User = Depends(get_current_user)
):
    """웹캠 이미지 분류"""
    try:
        # 이미지 분류 수행
        result, special_messages = classify_image(image_data=image_data)
        
        # 포인트 계산
        points_eligible = result.recyclable_count * settings.POINTS_PER_RECYCLABLE
        
        # 응답 객체 생성
        response = ClassificationResponse(
            result=result,
            points_eligible=points_eligible,
            special_messages=special_messages
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webcam classification failed: {str(e)}"
        )

@router.post("/chatbot-query", response_model=Dict[str, Any])
async def chatbot_query_endpoint(
    query: str = Form(..., description="챗봇 질문"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """챗봇 질문 처리"""
    try:
        # 건전지 수거함 검색 쿼리 처리
        if "건전지 수거함" in query:
            # 주소 추출 (주소 + 건전지 수거함 형식)
            address = query.replace("건전지 수거함", "").strip()
            if address:
                results = find_battery_bins(address)
                return {
                    "type": "battery_bins",
                    "query": query,
                    "results": results
                }
        
        # 폐기물 수수료 검색 쿼리 처리
        elif "수수료" in query:
            # 지역 및 품목 추출 (관악구 장롱 수수료 형식)
            parts = query.replace("수수료", "").strip().split()
            if len(parts) >= 2:
                region = parts[0]
                item = parts[1]
                results = find_waste_fees(region, item)
                return {
                    "type": "waste_fees",
                    "query": query,
                    "results": results
                }
        
        # 기타 쿼리 처리
        return {
            "type": "general",
            "query": query,
            "message": "검색 쿼리를 인식할 수 없습니다. '주소 + 건전지 수거함' 또는 '지역 품목 수수료' 형식으로 질문해주세요."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot query failed: {str(e)}"
        )

@router.get("/realtime-classify", response_model=ClassificationResponse)
async def realtime_classify_endpoint(
    image_data: str = Query(..., description="Base64 인코딩된 실시간 이미지"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """실시간 이미지 분류"""
    try:
        # 이미지 분류 수행
        result, special_messages = classify_image(image_data=image_data)
        
        # 포인트 계산
        points_eligible = result.recyclable_count * settings.POINTS_PER_RECYCLABLE
        
        # 응답 객체 생성
        response = ClassificationResponse(
            result=result,
            points_eligible=points_eligible,
            special_messages=special_messages
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Realtime classification failed: {str(e)}"
        )
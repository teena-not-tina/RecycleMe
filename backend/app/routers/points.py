from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional

from app.models.user import User, PointsBalance, PointsTransaction
from app.models.recycling import PointsEarnRequest
from app.routers.auth import get_current_user
from app.services.points import add_points, get_points_balance, use_points
from app.config import settings

router = APIRouter()

@router.post("/earn", response_model=Dict[str, Any])
async def earn_points(
    request: PointsEarnRequest,
    current_user: User = Depends(get_current_user)
):
    """분류 결과에 따른 포인트 적립"""
    try:
        # 요청한 사용자와 현재 사용자가 일치하는지 확인
        if request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot earn points for another user"
            )
        
        # 포인트 추가
        success, points_earned, message = add_points(
            user_id=request.user_id,
            classification_id=request.classification_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # 응답 데이터
        return {
            "success": True,
            "points_earned": points_earned,
            "message": f"{points_earned} 포인트가 성공적으로 적립되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to earn points: {str(e)}"
        )

@router.get("/balance", response_model=PointsBalance)
async def get_points(current_user: User = Depends(get_current_user)):
    """사용자 포인트 잔액 조회"""
    try:
        balance = get_points_balance(current_user.id)
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Points balance not found"
            )
        
        return balance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get points balance: {str(e)}"
        )

@router.post("/use", response_model=Dict[str, Any])
async def spend_points(
    amount: int = Query(..., description="사용할 포인트 양", gt=0),
    description: str = Query(..., description="포인트 사용 설명"),
    current_user: User = Depends(get_current_user)
):
    """포인트 사용"""
    try:
        # 포인트 사용
        success, remaining_points, message = use_points(
            user_id=current_user.id,
            amount=amount,
            description=description
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # 응답 데이터
        return {
            "success": True,
            "points_used": amount,
            "remaining_points": remaining_points,
            "message": f"{amount} 포인트가 성공적으로 사용되었습니다. 남은 포인트: {remaining_points}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to use points: {str(e)}"
        )

@router.get("/history", response_model=List[PointsTransaction])
async def get_points_history(
    limit: int = Query(10, description="조회할 트랜잭션 수", ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """포인트 사용/적립 내역 조회"""
    try:
        balance = get_points_balance(current_user.id)
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Points balance not found"
            )
        
        return balance.recent_transactions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get points history: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_points_stats(current_user: User = Depends(get_current_user)):
    """포인트 통계 조회"""
    try:
        balance = get_points_balance(current_user.id)
        if not balance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Points balance not found"
            )
        
        # 트랜잭션 분석
        transactions = balance.recent_transactions
        
        total_earned = sum(t.amount for t in transactions if t.transaction_type == "earn")
        total_spent = sum(abs(t.amount) for t in transactions if t.transaction_type == "spend")
        
        # 환경 기여도 계산 (예시: 재활용 항목 1개당 CO2 100g 감소)
        co2_reduction = total_earned / settings.POINTS_PER_RECYCLABLE * 100  # 그램(g) 단위
        
        return {
            "total_points": balance.total_points,
            "total_earned": total_earned,
            "total_spent": total_spent,
            "transaction_count": len(transactions),
            "environmental_impact": {
                "co2_reduction_grams": co2_reduction,
                "recyclable_items": total_earned / settings.POINTS_PER_RECYCLABLE
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get points stats: {str(e)}"
        )
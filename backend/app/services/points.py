from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid

from app.models.recycling import ClassificationResult
from app.models.user import PointsTransaction, PointsBalance
from app.utils.firebase_admin import get_user, get_user_points, add_points_transaction, get_points_transactions, get_classification_result
from app.config import settings

def calculate_points(classification_result: Dict[str, Any]) -> int:
    """재활용 가능 항목에 대한 포인트 계산"""
    try:
        # 재활용 가능한 카테고리 정의
        recyclable_categories = [
            "paper", "plastic", "can", "vinyl", "glass", "styrofoam"
        ]
        
        # 감지된 항목 카운트
        recyclable_count = 0
        
        # 결과 딕셔너리에서 detections 추출
        detections = classification_result.get("detections", [])
        
        # 각 감지 항목 확인
        for detection in detections:
            category = detection.get("category")
            if category in recyclable_categories:
                recyclable_count += 1
        
        # 포인트 계산
        points = recyclable_count * settings.POINTS_PER_RECYCLABLE
        
        return points
    except Exception as e:
        print(f"Error calculating points: {e}")
        return 0

def add_points(user_id: str, classification_id: str) -> Tuple[bool, int, str]:
    """사용자에게 포인트 추가"""
    try:
        # 사용자 존재 확인
        user = get_user(user_id)
        if not user:
            return False, 0, "User not found"
        
        # 분류 결과 가져오기
        classification_result = get_classification_result(classification_id)
        if not classification_result:
            return False, 0, "Classification result not found"
        
        # 포인트 계산
        points = calculate_points(classification_result)
        if points <= 0:
            return False, 0, "No recyclable items found"
        
        # 트랜잭션 데이터 생성
        transaction_data = {
            "user_id": user_id,
            "amount": points,
            "transaction_type": "earn",
            "description": f"재활용 항목 적립금: {classification_id}",
            "created_at": datetime.now(),
            "metadata": {
                "classification_id": classification_id,
                "recyclable_count": points // settings.POINTS_PER_RECYCLABLE
            }
        }
        
        # 포인트 추가
        transaction_id = add_points_transaction(transaction_data)
        if not transaction_id:
            return False, 0, "Failed to add points transaction"
        
        return True, points, transaction_id
    except Exception as e:
        print(f"Error adding points: {e}")
        return False, 0, str(e)

def get_points_balance(user_id: str) -> Optional[PointsBalance]:
    """사용자 포인트 잔액 및 최근 트랜잭션 조회"""
    try:
        # 사용자 존재 확인
        user = get_user(user_id)
        if not user:
            return None
        
        # 포인트 조회
        total_points = get_user_points(user_id)
        
        # 최근 트랜잭션 조회
        transactions = get_points_transactions(user_id, limit=10)
        
        # PointsTransaction 객체로 변환
        transaction_objects = [
            PointsTransaction(
                id=t.get("id", ""),
                user_id=t.get("user_id", ""),
                amount=t.get("amount", 0),
                transaction_type=t.get("transaction_type", ""),
                description=t.get("description", ""),
                created_at=t.get("created_at", datetime.now()),
                metadata=t.get("metadata", {})
            )
            for t in transactions
        ]
        
        # PointsBalance 객체 생성
        balance = PointsBalance(
            user_id=user_id,
            total_points=total_points,
            recent_transactions=transaction_objects
        )
        
        return balance
    except Exception as e:
        print(f"Error getting points balance: {e}")
        return None

def use_points(user_id: str, amount: int, description: str) -> Tuple[bool, int, str]:
    """사용자 포인트 사용"""
    try:
        # 사용자 존재 확인
        user = get_user(user_id)
        if not user:
            return False, 0, "User not found"
        
        # 포인트 잔액 확인
        current_points = get_user_points(user_id)
        if current_points < amount:
            return False, current_points, "Insufficient points"
        
        # 트랜잭션 데이터 생성
        transaction_data = {
            "user_id": user_id,
            "amount": -amount,  # 음수로 저장하여 사용 표시
            "transaction_type": "spend",
            "description": description,
            "created_at": datetime.now(),
            "metadata": {
                "transaction_id": str(uuid.uuid4())
            }
        }
        
        # 포인트 차감
        transaction_id = add_points_transaction(transaction_data)
        if not transaction_id:
            return False, current_points, "Failed to use points"
        
        # 업데이트된 포인트 잔액
        updated_points = current_points - amount
        
        return True, updated_points, transaction_id
    except Exception as e:
        print(f"Error using points: {e}")
        return False, 0, str(e)
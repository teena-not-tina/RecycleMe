import os  # 반드시 os 모듈을 import 해야 합니다
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# 상대 경로 import 대신 try-except로 안전하게 처리
try:
    from app.config import settings
except ImportError:
    # 개발 환경에서의 import 문제 해결을 위한 대체 경로
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from app.config import settings

# Firebase 앱 인스턴스
firebase_app = None
db = None
bucket = None

def initialize_firebase():
    """Firebase Admin SDK 초기화"""
    global firebase_app, db, bucket
    
    if firebase_app is not None:
        return True
    
    try:
        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if not os.path.exists(cred_path):
            print(f"Warning: Firebase credentials file not found at {cred_path}")
            print("Trying to find credentials in environment variables...")
            
            # 환경 변수에서 인증 정보 찾기 시도
            import json
            firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
            if firebase_creds:
                cred = credentials.Certificate(json.loads(firebase_creds))
            else:
                # 개발 환경을 위한 더미 인증 정보
                print("Using dummy credentials for development")
                cred = None
                app_options = {'projectId': 'dummy-project-id'}
                try:
                    firebase_app = firebase_admin.initialize_app(cred, app_options)
                except ValueError:
                    # 이미 초기화된 경우
                    firebase_app = firebase_admin.get_app()
                return False
        else:
            cred = credentials.Certificate(cred_path)
        
        # 앱 초기화 시도
        try:
            firebase_app = firebase_admin.initialize_app(cred, {
                'databaseURL': settings.FIREBASE_DATABASE_URL,
                'storageBucket': f"{settings.FIREBASE_PROJECT_ID}.appspot.com" if hasattr(settings, 'FIREBASE_PROJECT_ID') else None
            })
        except ValueError:
            # 이미 초기화된 경우
            firebase_app = firebase_admin.get_app()
        
        db = firestore.client()
        bucket = storage.bucket()
        
        print("Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Firebase features will be disabled")
        return False

# 사용자 관련 함수
def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """사용자 정보 조회"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 사용자 정보
        return {
            'id': user_id,
            'email': f"user{user_id}@example.com",
            'display_name': f"User {user_id}",
            'created_at': datetime.now(),
            'points': 100,
            'is_active': True
        }
        
    try:
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def create_user(user_data: Dict[str, Any]) -> Optional[str]:
    """새 사용자 생성"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 사용자 ID
        return str(uuid.uuid4())
        
    try:
        # Firebase Auth에 사용자 생성
        user_record = auth.create_user(
            email=user_data.get('email'),
            password=user_data.get('password'),
            display_name=user_data.get('display_name')
        )
        
        # Firestore에 사용자 정보 저장
        user_doc = {
            'id': user_record.uid,
            'email': user_data.get('email'),
            'display_name': user_data.get('display_name'),
            'created_at': datetime.now(),
            'points': 0,
            'is_active': True
        }
        
        db.collection('users').document(user_record.uid).set(user_doc)
        return user_record.uid
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
    """사용자 정보 업데이트"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경에서는 항상 성공으로 처리
        return True
        
    try:
        # Firestore 문서 업데이트
        db.collection('users').document(user_id).update(update_data)
        
        # Firebase Auth 업데이트 (필요한 경우)
        if 'display_name' in update_data or 'email' in update_data or 'password' in update_data:
            auth_update = {}
            if 'display_name' in update_data:
                auth_update['display_name'] = update_data['display_name']
            if 'email' in update_data:
                auth_update['email'] = update_data['email']
            if 'password' in update_data:
                auth_update['password'] = update_data['password']
                
            if auth_update:
                auth.update_user(user_id, **auth_update)
        
        return True
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

# 포인트 관련 함수
def get_user_points(user_id: str) -> int:
    """사용자 포인트 조회"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 포인트
        return 100
        
    try:
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict().get('points', 0)
        return 0
    except Exception as e:
        print(f"Error getting user points: {e}")
        return 0

def add_points_transaction(transaction: Dict[str, Any]) -> Optional[str]:
    """포인트 트랜잭션 추가"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 트랜잭션 ID
        return str(uuid.uuid4())
        
    try:
        transaction_id = transaction.get('id', str(uuid.uuid4()))
        if 'id' not in transaction:
            transaction['id'] = transaction_id
        
        # 트랜잭션 저장
        db.collection('points_transactions').document(transaction_id).set(transaction)
        
        # 사용자 포인트 업데이트
        user_ref = db.collection('users').document(transaction['user_id'])
        user_doc = user_ref.get()
        
        if user_doc.exists:
            current_points = user_doc.to_dict().get('points', 0)
            new_points = current_points + transaction['amount']
            user_ref.update({'points': new_points})
            
        return transaction_id
    except Exception as e:
        print(f"Error adding points transaction: {e}")
        return None

def get_points_transactions(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """사용자 포인트 트랜잭션 내역 조회"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 트랜잭션 데이터
        return [
            {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'amount': 10,
                'transaction_type': 'earn',
                'description': '재활용 항목 적립금',
                'created_at': datetime.now(),
                'metadata': {'recyclable_count': 1}
            }
        ]
        
    try:
        transactions = []
        query = (
            db.collection('points_transactions')
            .where('user_id', '==', user_id)
            .order_by('created_at', direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        
        for doc in query.stream():
            transactions.append(doc.to_dict())
            
        return transactions
    except Exception as e:
        print(f"Error getting points transactions: {e}")
        return []

# 분류 결과 관련 함수
def save_classification_result(result: Dict[str, Any]) -> Optional[str]:
    """분류 결과 저장"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 결과 ID
        result_id = result.get('image_id', str(uuid.uuid4()))
        if 'image_id' not in result:
            result['image_id'] = result_id
        return result_id
        
    try:
        result_id = result.get('image_id', str(uuid.uuid4()))
        if 'image_id' not in result:
            result['image_id'] = result_id
            
        db.collection('classification_results').document(result_id).set(result)
        return result_id
    except Exception as e:
        print(f"Error saving classification result: {e}")
        return None

def get_classification_result(result_id: str) -> Optional[Dict[str, Any]]:
    """분류 결과 조회"""
    if not db:
        print("Warning: Firebase not initialized")
        # 개발 환경을 위한 더미 분류 결과
        return {
            'image_id': result_id,
            'detections': [
                {
                    'category': 'plastic',
                    'confidence': 0.95,
                    'box': {'x1': 10, 'y1': 10, 'x2': 100, 'y2': 100}
                }
            ],
            'timestamp': datetime.now()
        }
        
    try:
        doc_ref = db.collection('classification_results').document(result_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error getting classification result: {e}")
        return None

# 이미지 관련 함수
def upload_image_to_storage(image_data: bytes, content_type: str = 'image/jpeg') -> Optional[str]:
    """이미지를 Firebase Storage에 업로드"""
    if not bucket:
        print("Warning: Firebase Storage not initialized")
        # 개발 환경을 위한 더미 이미지 URL
        image_id = str(uuid.uuid4())
        return f"https://example.com/images/{image_id}"
        
    try:
        image_id = str(uuid.uuid4())
        blob = bucket.blob(f"recycling_images/{image_id}")
        blob.upload_from_string(image_data, content_type=content_type)
        
        # 공개 URL 생성
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None
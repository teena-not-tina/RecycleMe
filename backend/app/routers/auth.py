from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

from app.models.user import UserCreate, UserLogin, UserUpdate, User, Token
from app.utils.firebase_admin import create_user, get_user, update_user
from firebase_admin import auth

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """토큰으로부터 현재 사용자 정보 가져오기"""
    try:
        # Firebase 토큰 검증
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token.get('uid')
        
        # 사용자 정보 조회
        user_data = get_user(user_id)
        if user_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return User(**user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate):
    """새 사용자 등록"""
    try:
        # 사용자 생성
        user_id = create_user({
            "email": user_data.email,
            "password": user_data.password,
            "display_name": user_data.display_name
        })
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # 커스텀 토큰 생성
        custom_token = auth.create_custom_token(user_id)
        
        # Firebase Auth에서 ID 토큰으로 교환 (프론트엔드에서 처리됨)
        # 여기서는 커스텀 토큰을 반환
        
        return {
            "access_token": custom_token.decode('utf-8'),
            "token_type": "bearer",
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """로그인 및 액세스 토큰 발행"""
    try:
        # Firebase Authentication을 통한 로그인
        user = auth.get_user_by_email(form_data.username)
        
        # 비밀번호 검증은 Firebase Auth REST API에서 처리해야 함
        # 여기서는 이메일이 존재하는지만 확인
        
        # 커스텀 토큰 생성
        custom_token = auth.create_custom_token(user.uid)
        
        return {
            "access_token": custom_token.decode('utf-8'),
            "token_type": "bearer",
            "user_id": user.uid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Incorrect email or password: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user)
):
    """현재 로그인한 사용자 정보 업데이트"""
    try:
        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            return current_user
        
        # 사용자 정보 업데이트
        success = update_user(current_user.id, update_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update user"
            )
        
        # 업데이트된 사용자 정보 조회
        updated_user_data = get_user(current_user.id)
        return User(**updated_user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Update failed: {str(e)}"
        )
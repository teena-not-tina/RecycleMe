from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 모듈 임포트 문제 해결
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routers import auth, recycling, points
from app.utils.firebase_admin import initialize_firebase
from app.config import settings

app = FastAPI(
    title="Recycling Classification API",
    description="API for recycling classification and points management",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase 초기화 (try-except로 오류 처리 강화)
try:
    initialize_firebase()
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # 개발 환경에서는 Firebase 초기화 실패해도 계속 진행할 수 있도록 함
    print("Continuing without Firebase - some features may not work")

# 라우터 등록
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(recycling.router, prefix="/api/recycling", tags=["Recycling Classification"])
app.include_router(points.router, prefix="/api/points", tags=["Points Management"])

# 정적 파일 서빙 (선택적)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"Error mounting static files: {e}")
    print("Static file serving disabled")

@app.get("/")
async def root():
    return {"message": "Welcome to Recycling Classification API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
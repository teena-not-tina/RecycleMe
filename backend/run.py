"""
서버 실행 스크립트
이 스크립트는 패키지 구조를 올바르게 설정한 후 FastAPI 서버를 실행합니다.
"""
import os
import sys
import uvicorn

# 현재 스크립트의 디렉토리를 가져옵니다.
current_dir = os.path.dirname(os.path.abspath(__file__))

# 현재 디렉토리를 Python 경로에 추가합니다.
sys.path.insert(0, current_dir)

def run_server():
    """FastAPI 서버를 실행합니다."""
    print("Starting Recycling Classification API Server...")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    
    try:
        # FastAPI 애플리케이션 실행
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
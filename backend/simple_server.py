"""
단순한 HTTP 서버 스크립트
이 스크립트는 Python의 http.server 모듈을 사용하여 정적 파일을 제공합니다.
FastAPI 없이 단순하게 웹 페이지를 표시합니다.
"""
import http.server
import socketserver
import os
import webbrowser
from threading import Timer

# 현재 디렉토리 기준 static 폴더
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    """정적 파일 제공을 위한 핸들러"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def open_browser():
    """브라우저 자동으로 열기"""
    webbrowser.open(f'http://localhost:{PORT}')

def main():
    """서버 시작"""
    # static 디렉토리 확인
    if not os.path.exists(DIRECTORY):
        print(f"오류: static 디렉토리가 없습니다: {DIRECTORY}")
        print("static 디렉토리와 필요한 파일들을 먼저 생성하세요.")
        return

    # index.html 파일 확인
    if not os.path.exists(os.path.join(DIRECTORY, "index.html")):
        print(f"오류: index.html 파일이 없습니다: {os.path.join(DIRECTORY, 'index.html')}")
        print("index.html 파일을 static 디렉토리에 먼저 생성하세요.")
        return

    # CSS 및 JS 디렉토리 확인
    css_dir = os.path.join(DIRECTORY, "css")
    js_dir = os.path.join(DIRECTORY, "js")
    if not os.path.exists(css_dir):
        os.makedirs(css_dir)
        print(f"css 디렉토리를 생성했습니다: {css_dir}")
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
        print(f"js 디렉토리를 생성했습니다: {js_dir}")

    # style.css 파일 확인
    if not os.path.exists(os.path.join(css_dir, "style.css")):
        print(f"경고: style.css 파일이 없습니다: {os.path.join(css_dir, 'style.css')}")

    # app.js 파일 확인
    if not os.path.exists(os.path.join(js_dir, "app.js")):
        print(f"경고: app.js 파일이 없습니다: {os.path.join(js_dir, 'app.js')}")

    # 서버 시작
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"서버가 포트 {PORT}에서 시작되었습니다...")
        print(f"웹 페이지를 보려면 http://localhost:{PORT} 주소로 접속하세요.")
        # 2초 후 브라우저 자동으로 열기
        Timer(2, open_browser).start()
        httpd.serve_forever()

if __name__ == "__main__":
    main()
    
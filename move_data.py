import os
import shutil
from pathlib import Path

def move_images():
    # 소스 폴더와 대상 폴더 경로 설정
    raw_data_path = 'raw_data'
    target_path = 'img'
    
    # 이미지 파일 확장자 정의
    image_extensions = ('.bmp', '.jpg', '.jpeg', '.png', '.gif')
    
    # 대상 폴더가 없으면 생성
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    
    # raw_data 폴더 내 모든 파일 검사
    for root, dirs, files in os.walk(raw_data_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                # 원본 파일의 전체 경로
                source_file = os.path.join(root, file)
                # 대상 파일의 전체 경로
                destination_file = os.path.join(target_path, file)
                
                try:
                    # 파일 이동
                    shutil.move(source_file, destination_file)
                    print(f'이동 완료: {file}')
                except Exception as e:
                    print(f'파일 이동 실패 {file}: {str(e)}')

if __name__ == '__main__':
    move_images()
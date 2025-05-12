from ultralytics import YOLO
import os

# 결과 저장할 폴더 생성
os.makedirs('result', exist_ok=True)

# 모델 로드
model = YOLO("best.pt")

# test 폴더의 모든 이미지에 대해 예측 수행
results = model('test')

# 각 결과 처리
for i, result in enumerate(results):
    # 원본 이미지 파일 이름 가져오기
    orig_filename = os.path.basename(result.path)
    # 결과 파일 이름 생성 (원본 파일명 유지)
    save_path = os.path.join('result', orig_filename)
    
    # 결과 저장 (박스 표시된 이미지)
    result.save(filename=save_path)
    
print("예측 완료! 결과는 'result' 폴더에 저장되었습니다.")
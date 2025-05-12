
import os
import shutil
import random

def create_folders():
    # 필요한 폴더 구조 생성
    folders = [
        'dataset/train/images', 'dataset/train/labels',
        'dataset/val/images', 'dataset/val/labels',
        'test'
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

def split_data():
    # 소스 폴더 경로
    img_path = 'img'
    label_path = 'label'
    
    # 라벨이 있는 이미지 파일 목록 생성
    labeled_images = []
    for label_file in os.listdir(label_path):
        if label_file.endswith('.txt'):
            img_name = os.path.splitext(label_file)[0]
            for ext in ['.bmp', '.jpg', '.jpeg', '.png', '.gif']:
                if os.path.exists(os.path.join(img_path, img_name + ext)):
                    labeled_images.append((img_name, ext))
                    break
    
    # 라벨링된 데이터 훈련/검증 세트로 분할 (8:2)
    random.shuffle(labeled_images)
    split_point = int(len(labeled_images) * 0.8)
    train_set = labeled_images[:split_point]
    val_set = labeled_images[split_point:]
    
    # 훈련 데이터 이동
    for img_name, ext in train_set:
        # 이미지 이동
        shutil.copy2(
            os.path.join(img_path, img_name + ext),
            os.path.join('dataset/train/images', img_name + ext)
        )
        # 라벨 이동
        shutil.copy2(
            os.path.join(label_path, img_name + '.txt'),
            os.path.join('dataset/train/labels', img_name + '.txt')
        )
    
    # 검증 데이터 이동
    for img_name, ext in val_set:
        # 이미지 이동
        shutil.copy2(
            os.path.join(img_path, img_name + ext),
            os.path.join('dataset/val/images', img_name + ext)
        )
        # 라벨 이동
        shutil.copy2(
            os.path.join(label_path, img_name + '.txt'),
            os.path.join('dataset/val/labels', img_name + '.txt')
        )
    
    # 라벨링되지 않은 이미지를 test 폴더로 이동
    for img_file in os.listdir(img_path):
        name, ext = os.path.splitext(img_file)
        if ext.lower() in ['.bmp', '.jpg', '.jpeg', '.png', '.gif']:
            if not os.path.exists(os.path.join(label_path, name + '.txt')):
                shutil.move(
                    os.path.join(img_path, img_file),
                    os.path.join('test', img_file)
                )

if __name__ == '__main__':
    create_folders()
    split_data()
    print("데이터 분할 완료!")

from ultralytics import YOLO
from multiprocessing import freeze_support

if __name__ == '__main__':
    freeze_support()  # Windows에서 멀티프로세싱 문제 방지

    # Load a model
    # model = YOLO("yolo11n.yaml")  # build a new model from YAML
    model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)
    # model = YOLO("yolo11n.yaml").load("yolo11n.pt")  # build from YAML and transfer weights
    model = YOLO("best1.pt")

    # Train the model
    results = model.train(
        data="dataset\data.yaml",
        epochs=100,
        imgsz=640,
        batch=16,
        device=0,
        pretrained=True,
        save=True,
        save_period=10,
        single_cls=True,
    )  # epoch 반복 횟수
import cv2
from ultralytics import YOLO

if __name__ == '__main__':
    Model = YOLO(r"/Users/wfcy/Dev/Module/tht/1024/11x550/detect/train/weights/best.pt")

    image_path = r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/Pic/13.png"
    Model.predict(image_path, save=True, conf=0.05)

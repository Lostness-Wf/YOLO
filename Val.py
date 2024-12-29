import cv2
from ultralytics import YOLO

if __name__ == '__main__':
# 加载模型
    model = YOLO(r"C:\Yolo\YoloTrain\v8x440\detect\train\weights\best.pt")  # 加载自定义模型

    # 验证模型
    metrics = model.val()  # 不需要额外参数，数据集和设置会被记住
    print(metrics.box.map)  # mAP50-95
    print(metrics.box.map50)  # mAP50
    print(metrics.box.map75)  # mAP75
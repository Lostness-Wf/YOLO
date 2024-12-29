from ultralytics import YOLO

if __name__ == '__main__':
    Model = YOLO(r"C:\Yolo\YoloTrain\Module\1024\11x550\detect\train\weights\best.pt")
    for i in range(20):
        str1 = "C:/Yolo/YoloTrain/Pic/"
        str2 = ".png"
        Model.predict(str1 + str(i + 1) + str2, save=True, conf=0.05)

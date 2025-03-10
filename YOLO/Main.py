from ultralytics import YOLO

# import torch
# print(torch.__version__)
# print(torch.cuda.is_available())
# print(torch.version.cuda)

if __name__ == '__main__':
    # YOLOV8
    model = YOLO('yolov8n.pt')
    # done model = YOLO('yolov8s.pt')
    # done model = YOLO('yolov8m.pt')
    # done model = YOLO('yolov8l.pt')
    # done model = YOLO('yolov8x.pt')

    # YOLO11
    # done model = YOLO('yolo11n.pt')
    # done model = YOLO('yolo11s.pt')
    # done model = YOLO('yolo11m.pt')
    # done model = YOLO('yolo11l.pt')
    # done model = YOLO('yolo11x.pt')

    model.train(data="/Users/wfcy/Dev/PycharmProj/YOLOTrain/DataSet/PCB_defect_detection/data.yaml", epochs = 1000, device = "mps", workers = 3, batch = -1, imgsz = 1024)

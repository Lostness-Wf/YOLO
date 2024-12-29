import os
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors

# 加载模型
model = YOLO(r"/Users/wfcy/Dev/Module/tht/1024/11x550/detect/train/weights/best.pt")
names = model.names

# 输入图像路径
image_path = r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/Pic/13.png"
im0 = cv2.imread(image_path)
assert im0 is not None, "Error reading image file"

# 裁剪图像的目录
crop_dir_name = r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/CropTest"
if not os.path.exists(crop_dir_name):
    os.mkdir(crop_dir_name)

# 检测
results = model.predict(im0, show=False)
boxes = results[0].boxes.xyxy.cpu().tolist()
clss = results[0].boxes.cls.cpu().tolist()
annotator = Annotator(im0, line_width=2, example=names)

# 裁剪并保存检测到的对象
idx = 0
if boxes is not None:
    for box, cls in zip(boxes, clss):
        idx += 1
        annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])

        crop_obj = im0[int(box[1]): int(box[3]), int(box[0]): int(box[2])]
        cv2.imwrite(os.path.join(crop_dir_name, str(idx) + ".png"), crop_obj)

cv2.waitKey(0)
cv2.destroyAllWindows()
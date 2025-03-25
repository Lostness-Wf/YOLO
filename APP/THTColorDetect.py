import cv2
import numpy as np
from ultralytics import YOLO

def plot_predictions(image, results, colors):
    """
    在图像上绘制预测框和颜色标签
    :param image: 原始图像
    :param results: YOLO预测结果
    :param colors: 颜色字典 {class_id: color_name}
    :return: 绘制后的图像和颜色信息
    """
    img = image.copy()
    color_info = []
    boxes = results[0].boxes

    # 收集所有检测框的中心点坐标和颜色信息
    detections = []
    for box in boxes:
        class_id = int(box.cls)
        color_name = colors.get(class_id, f"Unknown_{class_id}")
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
        conf = float(box.conf)

        # Skip boxes with very low confidence
        if conf < 0.5:
            continue

        detections.append({
            'box': (x1, y1, x2, y2),
            'center': (center_x, center_y),
            'color': color_name,
            'class_id': class_id,
            'conf': conf
        })

    if not detections:
        return img, []

    # 计算所有检测框之间的间距
    distances = []
    n = len(detections)
    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = detections[i]['center']
            x2, y2 = detections[j]['center']
            distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            distances.append(distance)

    # 排除位置偏差大的检测框
    ref_points = []
    for i, det in enumerate(detections):
        total_dist = 0
        for j, other in enumerate(detections):
            if i != j:
                x1, y1 = det['center']
                x2, y2 = other['center']
                total_dist += np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        ref_points.append((i, total_dist))

    # 通过距离计算框的离群程度，按总距离排序，移除异常框
    ref_points.sort(key=lambda x: -x[1])
    sorted_indices = [x[0] for x in ref_points]
    valid_detections = [detections[i] for i in sorted_indices if detections[i]['conf'] >= 0.5]

    # 根据中心位置对框进行排序
    valid_detections.sort(key=lambda x: x['center'][0])

    # 绘制检测框和标签
    for det in valid_detections:
        x1, y1, x2, y2 = det['box']
        color_name = det['color']
        conf = det['conf']

        # 绘制矩形框
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 绘制标签背景
        label = f"{color_name} {conf:.2f}"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)

        # 绘制标签文本
        cv2.putText(img, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

        color_info.append(color_name)

    return img, color_info


def predict_and_visualize(model_path, img_path, colors):
    """
    加载模型并进行预测可视化
    :param model_path: 模型路径
    :param img_path: 图像路径
    :param colors: 颜色字典 {class_id: color_name}
    :return: 绘制后的图像和颜色信息
    """
    # 加载模型
    model = YOLO(model_path)

    # 读取图像
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error: Could not read image at {img_path}")
        return None, []

    # 进行预测
    results = model.predict(img)

    # 绘制预测结果
    plotted_img, color_info = plot_predictions(img, results, colors)

    return plotted_img, color_info


if __name__ == '__main__':
    num=input("请输入要识别的电阻色环数量（1.四环电阻 2.五环电阻）：")
    # 颜色映射字典 {class_id: color_name}
    COLOR_MAP = {
        0: "red",
        1: "yellow",
        2: "black",
        3: "gold",
        4: "orange",
        5: "blue",
        6: "brown",
        7: "green",
        8: "purple",
        9: "white",
        10: "gray"
    }

    # 模型路径
    if num==4:
        MODEL_PATH = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/train/train4/weights/best.pt'  # 替换为你的模型路径
    else:
        MODEL_PATH = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/train/train5/weights/best.pt'

    # 图像路径
    IMAGE_PATH = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/DataSet/dianzu/five/val/images/70.png'  # 替换为你的测试图像路径

    # 进行预测和可视化
    result_img, colors_detected = predict_and_visualize(MODEL_PATH, IMAGE_PATH, COLOR_MAP)

    if result_img is not None:
        # 显示结果
        cv2.imshow('Detection Results', result_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # 保存结果
        output_path = 'result_' + IMAGE_PATH
        cv2.imwrite(output_path, result_img)
        print(f"Result saved to {output_path}")

        # 打印检测到的颜色（按从左到右的顺序）
        print("\n检测到的颜色（按从左到右顺序排列）:")
        for i, color in enumerate(colors_detected, 1):
            print(f"{i}. {color}")
    else:
        print("预测失败，请检查输入路径。")
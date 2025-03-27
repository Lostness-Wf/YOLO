import cv2
import numpy as np
from ultralytics import YOLO
import os
from tqdm import tqdm


def plot_predictions(image, results, colors):
    """
    在图像上绘制预测框和颜色标签，并按照色环顺序排序
    增加异常框处理逻辑：
    - 处理过于接近的相邻框
    - 处理过于分散的异常框
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

        # 跳过置信度低的框
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

    # 1. 异常框处理 - 过滤过于接近或分散的框
    filtered_detections = []
    if len(detections) > 1:
        # 计算所有相邻框的距离
        distances = []
        for i in range(len(detections) - 1):
            p1 = detections[i]['center']
            p2 = detections[i + 1]['center']
            distance = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
            distances.append(distance)

        # 计算平均距离和标准差
        avg_distance = np.mean(distances)
        std_distance = np.std(distances)

        # 距离阈值设置
        min_threshold = avg_distance * 0.3  # 小于平均距离30%视为过近
        max_threshold = avg_distance * 2.0  # 大于平均距离200%视为过远

        # 保留有效框的索引
        valid_indices = set(range(len(detections)))

        # 处理过近的框对
        for i in range(len(distances)):
            if distances[i] < min_threshold:
                # 保留置信度较高的框
                if detections[i]['conf'] > detections[i + 1]['conf']:
                    valid_indices.discard(i + 1)
                else:
                    valid_indices.discard(i)

        # 处理过远的异常框
        for i in range(len(detections)):
            if i == 0:
                continue
            prev_dist = distances[i - 1] if i < len(distances) else distances[-1]
            next_dist = distances[i] if i < len(distances) else distances[-1]
            if (prev_dist > max_threshold and next_dist > max_threshold):
                valid_indices.discard(i)

        # 创建过滤后的检测列表
        filtered_detections = [detections[i] for i in sorted(valid_indices)]
    else:
        filtered_detections = detections.copy()

    # 如果没有有效检测框，返回空结果
    if not filtered_detections:
        return img, []

    # 2. 判断图像方向（横向或纵向）
    x_coords = [d['center'][0] for d in filtered_detections]
    y_coords = [d['center'][1] for d in filtered_detections]
    x_span = max(x_coords) - min(x_coords)
    y_span = max(y_coords) - min(y_coords)
    horizontal = x_span > y_span  # True表示横向，False表示纵向

    # 3. 根据图像方向进行初步排序
    if horizontal:
        filtered_detections.sort(key=lambda x: x['center'][0])
        print("检测到横向电阻，按X坐标排序")
    else:
        filtered_detections.sort(key=lambda x: x['center'][1])
        print("检测到纵向电阻，按Y坐标排序")

    # 4. 计算相邻色环的距离
    distances = []
    for i in range(len(filtered_detections) - 1):
        x1, y1 = filtered_detections[i]['center']
        x2, y2 = filtered_detections[i + 1]['center']
        distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        distances.append(distance)

    # 5. 确定色环顺序
    if len(distances) > 0:
        # 找到最大间隔的位置
        max_dist_idx = np.argmax(distances)

        # 判断是顺序还是逆序情况
        if max_dist_idx == 0:
            # 最大间隔在最前面 - 顺序情况
            ordered_detections = list(reversed(filtered_detections))
            print("检测到顺序排列的色环")
        elif max_dist_idx == len(distances) - 1:
            # 最大间隔在最后面 - 逆序情况
            ordered_detections = filtered_detections
            print("检测到逆序排列的色环")
        else:
            # 其他情况（非常规排列）
            ordered_detections = filtered_detections[max_dist_idx + 1:] + filtered_detections[:max_dist_idx + 1]
            print("检测到非常规排列的色环，已尝试调整")
    else:
        ordered_detections = filtered_detections

    # 6. 绘制检测框和标签
    for det in ordered_detections:
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




def process_folder(input_folder, output_folder, model_path, colors):
    """
    处理文件夹中的所有图像
    :param input_folder: 输入文件夹路径
    :param output_folder: 输出文件夹路径
    :param model_path: 模型路径
    :param colors: 颜色字典
    """
    # 加载模型
    model = YOLO(model_path)

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 准备保存结果的文本文件
    txt_path = os.path.join(output_folder, "detection_results.txt")
    txt_content = []

    # 获取所有图像文件
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = [f for f in os.listdir(input_folder)
                   if os.path.splitext(f)[1].lower() in image_extensions]

    if not image_files:
        print(f"警告: 在文件夹 {input_folder} 中未找到图像文件")
        return

    # 处理每张图像
    for img_file in tqdm(image_files, desc="处理图像"):
        img_path = os.path.join(input_folder, img_file)

        try:
            # 读取图像
            img = cv2.imread(img_path)
            if img is None:
                print(f"无法读取图像: {img_path}")
                continue

            # 进行预测
            results = model.predict(img)

            # 绘制预测结果
            plotted_img, color_info = plot_predictions(img, results, colors)

            # 保存结果图像
            output_img_path = os.path.join(output_folder, f"result_{img_file}")
            cv2.imwrite(output_img_path, plotted_img)

            # 记录结果
            result_line = f"{img_file}: {', '.join(color_info)}"
            txt_content.append(result_line)

        except Exception as e:
            error_msg = f"处理 {img_file} 时出错: {str(e)}"
            print(error_msg)
            txt_content.append(error_msg)

    # 保存文本结果
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(txt_content))
    print(f"\n检测结果已保存到 {txt_path}")


if __name__ == '__main__':
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
    # COLOR_MAP = {
    #     0: "红",
    #     1: "黄",
    #     2: "黑",
    #     3: "金",
    #     4: "橙",
    #     5: "蓝",
    #     6: "棕",
    #     7: "绿",
    #     8: "紫",
    #     9: "白",
    #     10: "灰"
    # }
    # 模型路径
    MODEL_PATH = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/Module/THTColorDetect/New/best.pt'  # 替换为你的模型路径

    # 输入文件夹路径
    INPUT_FOLDER = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/CropResult'  # 替换为你的输入文件夹路径

    # 输出文件夹路径
    OUTPUT_FOLDER = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/THTColorDetectResult'  # 替换为你想要的输出文件夹路径

    # 处理整个文件夹
    process_folder(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        model_path=MODEL_PATH,
        colors=COLOR_MAP
    )
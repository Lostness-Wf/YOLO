import numpy as np
from PySide6 import QtWidgets, QtCore, QtGui
import cv2
import copy
import os
import shutil
from ultralytics import YOLO
from pathlib import Path
from THTAnnotationWindow import AnnotationWindow


class DetectionModePage1(QtWidgets.QWidget):
    def __init__(self, logger):
        super().__init__()
        self.current_image = None
        self.image_name = None
        self.model = None
        self.model_path = None
        self.base_result_image = None  # 存储基础检测图
        self.results = None  # 存储检测结果对象
        self.logger = logger
        self.output_window = None
        self.cache_annotation = {}

        # 加载色环检测模型
        self.tht_model = YOLO(r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/Module/THTColorDetect/New/best.pt')
        self.COLOR_MAP = {
            0: "红",
            1: "黄",
            2: "黑",
            3: "金",
            4: "橙",
            5: "蓝",
            6: "棕",
            7: "绿",
            8: "紫",
            9: "白",
            10: "灰"
        }

        self.init_default_dirs()
        self.setup_ui()
        self.setup_connections()
        self.logger.log("检测模式一程序启动", "INFO")

    def init_default_dirs(self):
        """初始化默认存储目录"""
        Path("Picture").mkdir(parents=True, exist_ok=True)
        Path("Module").mkdir(parents=True, exist_ok=True)
        Path("CropResult").mkdir(parents=True, exist_ok=True)
        Path("THTColorDetectResult").mkdir(parents=True, exist_ok=True)

    def set_output_window(self, output_window):
        """设置输出窗口引用"""
        self.output_window = output_window

    def setup_ui(self):
        """初始化界面布局和组件"""
        main_layout = QtWidgets.QVBoxLayout(self)

        # 顶部图片显示区域
        top_layout = QtWidgets.QHBoxLayout()
        self.label_original = self.create_image_label("原始图片")
        self.label_result = self.create_image_label("检测结果")
        top_layout.addWidget(self.label_original)
        top_layout.addWidget(self.label_result)
        main_layout.addLayout(top_layout)

        # 控制按钮区域
        control_layout = QtWidgets.QHBoxLayout()
        self.btn_annotate = self.create_button("📝 设置阻值")
        self.btn_open = self.create_button("📂 打开图片")
        self.btn_model = self.create_button("⚙️ 选择模型")
        self.btn_detect = self.create_button("🔍 开始检测")

        control_layout.addWidget(self.btn_annotate)
        control_layout.addWidget(self.btn_open)
        control_layout.addWidget(self.btn_model)
        control_layout.addWidget(self.btn_detect)
        main_layout.addLayout(control_layout)

        # 设置布局比例
        main_layout.setStretch(0, 3)
        main_layout.setStretch(1, 1)

    def create_image_label(self, text):
        """创建图片显示标签"""
        label = QtWidgets.QLabel(text, self)
        label.setMinimumSize(600, 480)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet('''
            QLabel {
                border: 2px solid #4A90E2;
                border-radius: 5px;
                background-color: #F0F4F8;
                color: #666666;
                font-size: 16px;
            }
        ''')
        return label

    def create_button(self, text):
        """创建统一风格的按钮"""
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet('''
            QPushButton {
                padding: 12px 24px;
                font-size: 14px;
                min-width: 140px;
                border: 1px solid #4A90E2;
                border-radius: 6px;
                background-color: #FFFFFF;
                color: #2D2D2D;
            }
            QPushButton:hover {
                background-color: #E8F0FE;
            }
            QPushButton:pressed {
                background-color: #D0E0FC;
            }
        ''')
        return button

    def setup_connections(self):
        """连接按钮信号与槽函数"""
        self.btn_annotate.clicked.connect(self.open_annotation_window)
        self.btn_open.clicked.connect(self.open_image)
        self.btn_model.clicked.connect(self.select_model)
        self.btn_detect.clicked.connect(self.detect_image)

    def open_annotation_window(self):
        """打开标注窗口"""
        if not self.model:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择模型！")
            return
        if self.current_image is None:
            QtWidgets.QMessageBox.warning(self, "警告", "请先打开图片！")
            return

        try:
            self.annot_window = AnnotationWindow(self.model, self.current_image, self.logger, self, self.image_name)
            self.annot_window.exec()
        except Exception as e:
            self.logger.log(f"标注窗口打开失败: {str(e)}", "ERROR")
            QtWidgets.QMessageBox.critical(self, "错误", f"无法启动标注窗口: {str(e)}")

    def select_model(self):
        """选择并加载YOLO模型"""
        default_dir = str(Path("Module").absolute())
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "检测模式一选择模型",
            default_dir,
            "模型文件 (*.pt)"
        )

        if file_path:
            try:
                self.logger.log(f"检测模式一尝试加载模型: {file_path}")
                # 清空现有状态
                self.model = None
                self.label_original.clear()
                self.label_result.clear()
                self.image_name = None
                self.current_image = None
                self.base_result_image = None
                self.results = None
                if self.output_window:
                    self.output_window.clear_results()

                # 加载新模型
                self.model = YOLO(file_path)
                self.model_path = Path(file_path).name
                self.btn_model.setText(f"模型: {self.model_path}")
                self.logger.log(f"检测模式一成功加载模型: {self.model_path}", "SUCCESS")
                QtWidgets.QMessageBox.information(
                    self, "检测模式一模型加载",
                    f"成功加载模型: {self.model_path}"
                )
            except Exception as e:
                self.logger.log(f"检测模式一模型加载失败: {str(e)}", "ERROR")
                QtWidgets.QMessageBox.critical(
                    self, "检测模式一错误",
                    f"模型加载失败: {str(e)}"
                )
                self.btn_model.setText("⚙️ 选择模型")

    def plot_predictions(self, image, results, colors):
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
                self.logger.log(f"跳过低置信度检测框: {color_name} {conf:.2f}", "WARNING")
                continue

            detections.append({
                'box': (x1, y1, x2, y2),
                'center': (center_x, center_y),
                'color': color_name,
                'class_id': class_id,
                'conf': conf
            })

        if not detections:
            self.logger.log("未检测到有效色环", "WARNING")
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
                    self.logger.log(f"检测到过近框对 {i}-{i + 1}，距离{distances[i]:.1f}", "WARNING")
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
                    self.logger.log(f"检测到孤立异常框 {i}，前后距离{prev_dist:.1f}/{next_dist:.1f}", "WARNING")
                    valid_indices.discard(i)

            # 创建过滤后的检测列表
            filtered_detections = [detections[i] for i in sorted(valid_indices)]
        else:
            filtered_detections = detections.copy()

        # 如果没有有效检测框，返回空结果
        if not filtered_detections:
            self.logger.log("异常框过滤后无有效色环保留", "WARNING")
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
            self.logger.log("检测到横向电阻，按X坐标排序", "INFO")
        else:
            filtered_detections.sort(key=lambda x: x['center'][1])
            self.logger.log("检测到横向电阻，按Y坐标排序", "INFO")

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
                self.logger.log("检测到顺序排列的色环", "INFO")
            elif max_dist_idx == len(distances) - 1:
                # 最大间隔在最后面 - 逆序情况
                ordered_detections = filtered_detections
                self.logger.log("检测到逆序排列的色环", "INFO")
            else:
                # 其他情况（非常规排列）
                ordered_detections = filtered_detections[max_dist_idx + 1:] + filtered_detections[:max_dist_idx + 1]
                self.logger.log("检测到非常规排列的色环，已尝试调整", "INFO")
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

    def detect_tht_colors(self, crop_img):
        """对裁剪的电阻图像进行色环检测"""
        try:
            # 进行预测
            results = self.tht_model.predict(crop_img)

            # 获取处理后的颜色信息
            _, color_info = self.plot_predictions(crop_img, results, self.COLOR_MAP)

            # 金开头反转逻辑
            if color_info and len(color_info) > 0:
                # 检查第一个色环是否为金
                if color_info[0] == "金":
                    # 反转色环顺序（保留原始列表）
                    reversed_colors = color_info[::-1]

                    # 日志记录原始和调整后的顺序
                    self.logger.log(f"检测到误差环出现在第一位，排序出错，执行顺序调整: {color_info} -> {reversed_colors}", "WARNING")

                    return " ".join(reversed_colors)

            return " ".join(color_info) if color_info else "未识别到色环"
        except Exception as e:
            self.logger.log(f"色环检测失败: {str(e)}", "ERROR")
            return "色环检测错误"

    def detect_image(self):
        """执行图像检测并显示结果"""
        if self.current_image is None:
            self.logger.log("检测模式一未选择图片", "WARNING")
            QtWidgets.QMessageBox.warning(self, "检测模式一警告", "请先打开图片")
            return

        if self.model is None:
            self.logger.log("检测模式一未选择模型", "WARNING")
            QtWidgets.QMessageBox.warning(self, "检测模式一警告", "请先选择模型")
            return

        try:
            self.logger.log("检测模式一开始图片检测...", "INFO")
            if self.output_window:
                self.output_window.clear_results()

            # 执行YOLO检测
            self.results = self.model(self.current_image, conf=0.05)[0]
            self.base_result_image = self.results.plot(line_width=2).copy()

            # 显示检测结果
            self.show_image(self.label_result, self.base_result_image)

            # 清空并准备裁剪目录
            default_dir = Path("CropResult").absolute()
            shutil.rmtree(default_dir, ignore_errors=True)
            default_dir.mkdir(parents=True, exist_ok=True)

            # 填充检测结果到输出窗口
            if self.output_window and self.results.boxes:
                for i, box in enumerate(self.results.boxes):
                    xyxy = box.xyxy[0].cpu().numpy()
                    class_id = int(box.cls)
                    class_name = self.model.names[class_id]
                    confidence = box.conf.item()
                    x_center = (xyxy[0] + xyxy[2]) / 2
                    y_center = (xyxy[1] + xyxy[3]) / 2

                    # 裁剪处理逻辑
                    x_min, y_min, x_max, y_max = map(int, xyxy)
                    img_height, img_width = self.current_image.shape[:2]
                    x_min = max(0, x_min)
                    y_min = max(0, y_min)
                    x_max = min(img_width, x_max)
                    y_max = min(img_height, y_max)

                    if x_min >= x_max or y_min >= y_max:
                        continue

                    # 执行裁剪
                    crop_img = self.current_image[y_min:y_max, x_min:x_max]

                    # 进行色环检测
                    tht_color = self.detect_tht_colors(crop_img)

                    # 填充结果到界面
                    self.output_window.add_detection_result(
                        (x_center, y_center),
                        class_name,
                        confidence,
                        tht_color  # 传入色环检测结果
                    )

                    # 保存裁剪图片
                    safe_class_name = class_name.replace(' ', '_')
                    filename = default_dir / f"crop_{i}_{safe_class_name}_{confidence:.2f}.jpg"
                    cv2.imwrite(str(filename), crop_img)

            self.logger.log("检测模式一图片检测完成", "SUCCESS")

            # 自动保存结果到CSV
            if self.output_window and self.output_window.table.rowCount() > 0:
                self.output_window.save_to_csv()

        except Exception as e:
            self.logger.log(f"检测模式一检测失败: {str(e)}", "ERROR")
            QtWidgets.QMessageBox.critical(
                self, "检测模式一错误",
                f"检测失败: {str(e)}"
            )

    def show_image(self, label, image):
        """在指定标签显示图像（支持选中框动态绘制）"""
        try:
            if image is None:
                label.clear()
                return

            # 深拷贝基础图像用于绘制
            display_image = copy.deepcopy(image)

            # 仅当显示检测结果时绘制选中框
            if label == self.label_result:
                # 动态绘制选中框（与输出窗口联动）
                if self.results and self.results.boxes and self.output_window:
                    selected_ids = self.output_window.get_selected_ids()

                    for idx, box in enumerate(self.results.boxes, start=1):
                        if idx in selected_ids:
                            xyxy = box.xyxy[0].cpu().numpy().astype(int)
                            cv2.rectangle(
                                display_image,
                                (xyxy[0], xyxy[1]),
                                (xyxy[2], xyxy[3]),
                                color=(0, 255, 0),  # 绿色
                                thickness=15  # 加粗线宽
                            )

            # 转换为QPixmap并显示
            label.clear()
            h, w, ch = display_image.shape
            bytes_per_line = ch * w
            q_img = QtGui.QImage(
                display_image.data, w, h, bytes_per_line,
                QtGui.QImage.Format.Format_BGR888
            )
            scaled_pixmap = QtGui.QPixmap.fromImage(q_img).scaled(
                label.width(), label.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)

        except Exception as e:
            self.logger.log(f"检测模式一图片显示失败: {str(e)}", "ERROR")

    def open_image(self):
        """打开并显示原始图片"""
        default_dir = str(Path("Picture").absolute())
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "检测模式一选择图片",
            default_dir,
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            try:
                # 清空所有检测相关状态
                self.results = None
                self.base_result_image = None
                self.logger.log(f"检测模式一尝试打开图片: {file_path}")
                self.image_name = os.path.basename(file_path)  # 带扩展名的文件名（如：image.jpg）
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.show_image(self.label_original, self.current_image)
                    self.label_result.clear()
                    self.label_result.setText("检测结果")
                    self.logger.log(f"检测模式一成功打开图片: {Path(file_path).name}")
                    # 清空相关缓存
                    self.base_result_image = None
                    self.results = None
                    if self.output_window:
                        self.output_window.clear_results()
                else:
                    self.logger.log("检测模式一图片文件读取失败", "ERROR")
                    QtWidgets.QMessageBox.critical(self, "检测模式一错误", "无法读取图片文件")
            except Exception as e:
                self.logger.log(f"检测模式一图片打开失败: {str(e)}", "ERROR")
                QtWidgets.QMessageBox.critical(self, "检测模式一错误", f"图片加载失败: {str(e)}")

    def refresh_annotations(self):
        self.cache_annotation.clear()
        self.cache_annotation = self.annot_window.annotations
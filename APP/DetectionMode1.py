from PySide6 import QtWidgets, QtCore, QtGui
import cv2
import copy
from ultralytics import YOLO
from pathlib import Path
from THTAnnotationWindow import AnnotationWindow


class DetectionModePage1(QtWidgets.QWidget):
    def __init__(self, logger):
        super().__init__()
        self.current_image = None
        self.model = None
        self.model_path = None
        self.base_result_image = None  # 存储基础检测图
        self.results = None  # 存储检测结果对象
        self.logger = logger
        self.output_window = None

        self.init_default_dirs()
        self.setup_ui()
        self.setup_connections()
        self.logger.log("检测模式一程序启动", "INFO")

    def init_default_dirs(self):
        """初始化默认存储目录"""
        Path("Picture").mkdir(parents=True, exist_ok=True)
        Path("Module").mkdir(parents=True, exist_ok=True)

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
            self.annot_window = AnnotationWindow(self.model, self.current_image, self.logger)
            self.annot_window.exec()
        except Exception as e:
            self.logger.log(f"标注窗口打开失败: {str(e)}", "ERROR")
            QtWidgets.QMessageBox.critical(self, "错误", f"无法启动标注窗口: {str(e)}")

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
                self.logger.log(f"检测模式一尝试打开图片: {file_path}")
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
            self.results = self.model(self.current_image)[0]
            self.base_result_image = self.results.plot(line_width=2).copy()

            # 显示检测结果
            self.show_image(self.label_result, self.base_result_image)

            # 填充检测结果到输出窗口
            if self.output_window and self.results.boxes:
                for box in self.results.boxes:
                    xyxy = box.xyxy[0].cpu().numpy()
                    class_id = int(box.cls)
                    class_name = self.model.names[class_id]
                    confidence = box.conf.item()
                    x_center = (xyxy[0] + xyxy[2]) / 2
                    y_center = (xyxy[1] + xyxy[3]) / 2
                    self.output_window.add_detection_result(
                        (x_center, y_center),
                        class_name,
                        confidence
                    )

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
                            color=(0, 255, 0),  # 红色
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
from PySide6 import QtWidgets, QtCore, QtGui
import cv2
from ultralytics import YOLO
from pathlib import Path

class DetectionModePage2(QtWidgets.QWidget):
    def __init__(self, logger):
        super().__init__()
        self.current_image = None
        self.model = None
        self.model_path = None
        self.result_image = None
        self.logger = logger  # 使用外部传入的logger

        self.init_default_dirs()
        self.setupUI()
        self.setupConnections()

        self.logger.log("检测模式二程序启动", "INFO")

    def init_default_dirs(self):
        Path("Picture").mkdir(parents=True, exist_ok=True)
        Path("Module").mkdir(parents=True, exist_ok=True)

    def setupUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)

        topLayout = QtWidgets.QHBoxLayout()
        self.label_original = self.createImageLabel("原始图片")
        self.label_result = self.createImageLabel("检测结果")
        topLayout.addWidget(self.label_original)
        topLayout.addWidget(self.label_result)
        mainLayout.addLayout(topLayout)

        controlLayout = QtWidgets.QHBoxLayout()
        self.btn_open = self.createButton("📂 打开图片")
        self.btn_model = self.createButton("⚙️ 选择模型")
        self.btn_detect = self.createButton("🔍 开始检测")
        self.btn_test = self.createButton("🧪 测试按钮")
        controlLayout.addWidget(self.btn_open)
        controlLayout.addWidget(self.btn_model)
        controlLayout.addWidget(self.btn_detect)
        controlLayout.addWidget(self.btn_test)
        mainLayout.addLayout(controlLayout)

        mainLayout.setStretch(0, 3)
        mainLayout.setStretch(1, 1)

    def createImageLabel(self, text):
        label = QtWidgets.QLabel(text, self)
        label.setMinimumSize(600, 480)
        label.setAlignment(QtCore.Qt.AlignCenter)
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

    def createButton(self, text):
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

    def setupConnections(self):
        self.btn_open.clicked.connect(self.openImage)
        self.btn_model.clicked.connect(self.selectModel)
        self.btn_detect.clicked.connect(self.detectImage)
        self.btn_test.clicked.connect(self.testFunction)

    def openImage(self):
        default_dir = str(Path("Picture").absolute())
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "检测模式二选择图片",
            default_dir,
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            try:
                self.logger.log(f"检测模式二尝试打开图片: {file_path}")
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.showImage(self.label_original, self.current_image)
                    self.label_result.clear()
                    self.label_result.setText("检测结果")
                    self.logger.log(f"检测模式二成功打开图片: {Path(file_path).name}")
                else:
                    self.logger.log("检测模式二图片文件读取失败", "ERROR")
                    QtWidgets.QMessageBox.critical(self, "检测模式二错误", "无法读取图片文件")
            except Exception as e:
                self.logger.log(f"检测模式二图片打开失败: {str(e)}", "ERROR")
                QtWidgets.QMessageBox.critical(self, "检测模式二错误", f"图片加载失败: {str(e)}")

    def selectModel(self):
        default_dir = str(Path("Module").absolute())
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "检测模式二选择模型",
            default_dir,
            "模型文件 (*.pt)"
        )

        if file_path:
            try:
                self.logger.log(f"检测模式二尝试加载模型: {file_path}")
                self.model = None
                self.label_original.clear()
                self.label_result.clear()
                self.current_image = None

                self.model = YOLO(file_path)
                self.model_path = Path(file_path).name
                self.btn_model.setText(f"模型: {self.model_path}")
                self.logger.log(f"检测模式二成功加载模型: {self.model_path}", "SUCCESS")
                QtWidgets.QMessageBox.information(
                    self, "检测模式二模型加载",
                    f"成功加载模型: {self.model_path}"
                )
            except Exception as e:
                self.logger.log(f"检测模式二模型加载失败: {str(e)}", "ERROR")
                QtWidgets.QMessageBox.critical(
                    self, "检测模式二错误",
                    f"模型加载失败: {str(e)}"
                )
                self.btn_model.setText("⚙️ 选择模型")

    def detectImage(self):
        if self.current_image is None:
            self.logger.log("检测模式二未选择图片", "WARNING")
            QtWidgets.QMessageBox.warning(self, "检测模式二警告", "请先打开图片")
            return

        if self.model is None:
            self.logger.log("检测模式二未选择模型", "WARNING")
            QtWidgets.QMessageBox.warning(self, "检测模式二警告", "请先选择模型")
            return

        try:
            self.logger.log("检测模式二开始图片检测...")
            self.label_result.clear()

            results = self.model(self.current_image)[0]
            self.result_image = results.plot(line_width=2)
            self.showImage(self.label_result, self.result_image)
            self.logger.log("检测模式二图片检测完成", "SUCCESS")

        except Exception as e:
            self.logger.log(f"检测模式二检测失败: {str(e)}", "ERROR")
            QtWidgets.QMessageBox.critical(
                self, "检测模式二错误",
                f"检测失败: {str(e)}"
            )

    def showImage(self, label, image):
        try:
            label.clear()

            if len(image.shape) == 3:
                h, w, ch = image.shape
                q_img = QtGui.QImage(
                    image.data, w, h, ch * w,
                    QtGui.QImage.Format.Format_BGR888
                )
            else:
                h, w = image.shape
                q_img = QtGui.QImage(
                    image.data, w, h, w,
                    QtGui.QImage.Format.Format_Grayscale8
                )

            scaled_pixmap = QtGui.QPixmap.fromImage(q_img).scaled(
                label.width(), label.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(scaled_pixmap)
        except Exception as e:
            self.logger.log(f"检测模式二图片显示失败: {str(e)}", "ERROR")

    def testFunction(self):
        self.logger.log("检测模式二测试按钮被点击", "ERROR")

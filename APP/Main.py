from PySide6 import QtWidgets, QtCore, QtGui
import cv2, os
from ultralytics import YOLO
from pathlib import Path


class MWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.setupConnections()
        self.current_image = None  # 存储当前打开的图片
        self.model = None  # 存储加载的模型
        self.model_path = None  # 存储模型路径

    def setupUI(self):
        self.resize(1200, 800)
        self.setWindowTitle('图片检测APP')

        # 中央部件
        centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QVBoxLayout(centralWidget)

        # 上半部分：图片显示区域
        topLayout = QtWidgets.QHBoxLayout()
        self.label_original = QtWidgets.QLabel("原始图片", self)
        self.label_result = QtWidgets.QLabel("检测结果", self)

        # 设置图片显示区域的样式和尺寸
        for label in [self.label_original, self.label_result]:
            label.setMinimumSize(600, 480)
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet('''
                border: 2px solid #4A90E2;
                border-radius: 5px;
                background-color: #F0F4F8;
            ''')

        topLayout.addWidget(self.label_original)
        topLayout.addWidget(self.label_result)
        mainLayout.addLayout(topLayout)

        # 下半部分：控制区域
        controlLayout = QtWidgets.QHBoxLayout()

        # 按钮组
        self.btn_open = QtWidgets.QPushButton("📂 打开图片", self)
        self.btn_model = QtWidgets.QPushButton("⚙️ 选择模型", self)
        self.btn_detect = QtWidgets.QPushButton("🔍 开始检测", self)

        # 设置按钮样式
        button_style = '''
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                min-width: 120px;
                border: 1px solid #4A90E2;
                border-radius: 5px;
                background-color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #E8F0FE;
            }
        '''
        for btn in [self.btn_open, self.btn_model, self.btn_detect]:
            btn.setStyleSheet(button_style)

        controlLayout.addWidget(self.btn_open)
        controlLayout.addWidget(self.btn_model)
        controlLayout.addWidget(self.btn_detect)
        mainLayout.addLayout(controlLayout)

    def setupConnections(self):
        self.btn_open.clicked.connect(self.openImage)
        self.btn_model.clicked.connect(self.selectModel)
        self.btn_detect.clicked.connect(self.detectImage)

    def openImage(self):
        # 打开图片文件对话框
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择图片",
            str(Path.home()),
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            # 读取并显示图片
            self.current_image = cv2.imread(file_path)
            self.showImage(self.label_original, self.current_image)

    def selectModel(self):
        # 选择模型文件对话框
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择模型",
            str(Path.home()),
            "模型文件 (*.pt)"
        )

        if file_path:
            try:
                self.model = YOLO(file_path)
                self.model_path = Path(file_path).name
                self.btn_model.setText(f"模型: {self.model_path}")
                QtWidgets.QMessageBox.information(
                    self, "模型加载",
                    f"成功加载模型: {self.model_path}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "错误",
                    f"模型加载失败: {str(e)}"
                )

    def detectImage(self):
        if self.current_image is None:
            QtWidgets.QMessageBox.warning(self, "警告", "请先打开图片")
            return

        if self.model is None:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择模型")
            return

        try:
            # 执行检测
            results = self.model(self.current_image)[0]
            result_image = results.plot(line_width=2)

            # 显示检测结果
            self.showImage(self.label_result, result_image)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "错误",
                f"检测失败: {str(e)}"
            )

    def showImage(self, label, image):
        # 将OpenCV图像转换为QImage
        if len(image.shape) == 3:  # 彩色图片
            h, w, ch = image.shape
            bytes_per_line = ch * w
            q_img = QtGui.QImage(
                image.data, w, h, bytes_per_line,
                QtGui.QImage.Format_BGR888
            )
        else:  # 灰度图片
            h, w = image.shape
            q_img = QtGui.QImage(
                image.data, w, h, w,
                QtGui.QImage.Format_Grayscale8
            )

        # 缩放并显示图片
        pixmap = QtGui.QPixmap.fromImage(q_img)
        scaled_pixmap = pixmap.scaled(
            label.width(), label.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    window = MWindow()
    window.show()
    app.exec()
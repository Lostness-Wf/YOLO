from PySide6 import QtWidgets, QtCore, QtGui
import cv2
import copy
from LogWindow import Logger


class AnnotationWindow(QtWidgets.QDialog):
    def __init__(self, yolo_model, input_image, logger, parent=None):
        super().__init__(parent)
        self.model = yolo_model
        self.original_image = copy.deepcopy(input_image)
        self.results = None
        self.annotations = {}
        self.setup_ui()
        self.logger = logger
        self.perform_detection()
        self.setWindowTitle("实时检测标注")
        self.setMinimumSize(1200, 800)

    def setup_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        # 左侧图片显示区域
        self.image_label = QtWidgets.QLabel("检测结果加载中...")
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #4A90E2;")
        main_layout.addWidget(self.image_label, 3)

        # 右侧表格区域
        table_frame = QtWidgets.QFrame()
        table_layout = QtWidgets.QVBoxLayout(table_frame)

        # 创建表格
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["编号", "正确阻值（Ω）"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        # 设置表格选择模式
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.selectionModel().selectionChanged.connect(self.highlight_box)

        # 操作按钮
        self.btn_retry = QtWidgets.QPushButton("🔄 重新检测")
        self.btn_retry.clicked.connect(self.perform_detection)
        self.btn_save = QtWidgets.QPushButton("💾 保存结果")
        self.btn_save.clicked.connect(self.save_annotations)

        table_layout.addWidget(self.table)
        table_layout.addWidget(self.btn_retry)
        table_layout.addWidget(self.btn_save)
        main_layout.addWidget(table_frame, 2)

    def perform_detection(self):
        """执行YOLO检测并更新界面"""
        try:
            # 执行检测
            self.results = self.model(self.original_image)[0]
            self.draw_annotations()  # 初始化绘制
            self.update_table()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "检测错误", f"检测失败: {str(e)}")

    def draw_annotations(self, selected_index=None):
        """根据选中状态重新绘制检测框"""
        if not self.results:
            return

        # 创建深拷贝保持原始图像不变
        annotated_image = copy.deepcopy(self.original_image)

        # 绘制所有检测框
        if self.results.boxes:
            for idx, box in enumerate(self.results.boxes):
                xyxy = box.xyxy[0].cpu().numpy().astype(int)

                # 设置线宽（选中框4px，其他2px）
                line_width = 15 if idx == selected_index else 2
                cv2.rectangle(
                    annotated_image,
                    (xyxy[0], xyxy[1]),
                    (xyxy[2], xyxy[3]),
                    (0, 255, 0),  # BGR颜色
                    thickness=line_width
                )

                # 添加编号
                cv2.putText(
                    annotated_image,
                    f"{idx + 1}",
                    (xyxy[0], xyxy[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

        self.update_image(annotated_image)

    def update_image(self, image):
        """更新图片显示"""
        h, w, ch = image.shape
        bytes_per_line = ch * w
        q_img = QtGui.QImage(image.data, w, h, bytes_per_line,
                             QtGui.QImage.Format.Format_BGR888)
        pixmap = QtGui.QPixmap.fromImage(q_img).scaled(
            self.image_label.width(), self.image_label.height(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(pixmap)

    def update_table(self):
        """更新结果表格"""
        if not self.results or not self.results.boxes:
            return

        self.table.setRowCount(len(self.results.boxes))
        for idx in range(len(self.results.boxes)):
            # 编号列
            number_item = QtWidgets.QTableWidgetItem(str(idx + 1))
            number_item.setFlags(number_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(idx, 0, number_item)

            # 阻值输入列
            value_edit = QtWidgets.QLineEdit()
            value_edit.setPlaceholderText("输入阻值")
            self.table.setCellWidget(idx, 1, value_edit)

    def highlight_box(self):
        """高亮选中的检测框"""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.draw_annotations(selected_row)
        else:
            self.draw_annotations()

    def save_annotations(self):
        """保存标注结果"""
        self.annotations.clear()
        for row in range(self.table.rowCount()):
            # 获取编号列（非空检查）
            number_item = self.table.item(row, 0)
            if not number_item:
                continue  # 跳过无效行
            number = number_item.text()

            # 获取阻值输入列（类型转换 + 空值检查）
            widget = self.table.cellWidget(row, 1)
            if isinstance(widget, QtWidgets.QLineEdit):  # 确保是 QLineEdit 类型
                value = widget.text()
                if value:
                    self.annotations[number] = value
            else:
                self.logger.log(f"第 {row + 1} 行阻值输入控件类型错误", "WARNING")

        self.logger.log(f"已保存的正确阻值：{self.annotations}", "WARNING")
        QtWidgets.QMessageBox.information(self, "保存成功", "标注数据已保存！")

    def closeEvent(self, event):
        self.save_annotations()
        super().closeEvent(event)

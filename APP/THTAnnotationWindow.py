from PySide6 import QtWidgets, QtCore, QtGui
import cv2
import copy
from LogWindow import Logger


class AnnotationWindow(QtWidgets.QDialog):
    def __init__(self, yolo_model, input_image, logger, parent=None):
        super().__init__(parent)
        # 定义颜色配置
        self.base_colors = ["黑", "棕", "红", "橙", "黄", "绿", "蓝", "紫", "灰", "白"]  # 基础颜色环（数字）
        self.multiplier_bands = ["黑", "棕", "红", "橙", "黄", "绿", "蓝", "金", "银"]  # 倍率环
        self.tolerance_bands = ["棕", "红", "绿", "金", "银"]  # 误差环

        self.model = yolo_model
        self.original_image = copy.deepcopy(input_image)
        self.results = None
        self.annotations = {}
        self.setup_ui()
        self.logger = logger
        self.perform_detection()
        self.setWindowTitle("阻值设置")
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
        self.table.setColumnCount(8)
        headers = ["编号", "环数", "环1", "环2", "环3", "环4", "环5", "计算阻值"]

        #设置表格各列宽度
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        for col in range(2, 7):
            self.table.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Fixed)
            self.table.horizontalHeader().resizeSection(col, 70)

        self.table.horizontalHeader().setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().resizeSection(8, 150)

        # 设置表格选择模式
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.selectionModel().selectionChanged.connect(self.highlight_box)

        # 操作按钮
        self.btn_retry = QtWidgets.QPushButton("🔄 重新检测")
        self.btn_retry.clicked.connect(self.perform_detection)

        self.btn_calculate = QtWidgets.QPushButton("💡 计算阻值")
        self.btn_calculate.clicked.connect(self.calculate_resistance)

        self.btn_save = QtWidgets.QPushButton("💾 保存结果")
        self.btn_save.clicked.connect(self.save_annotations)

        table_layout.addWidget(self.table)
        table_layout.addWidget(self.btn_retry)
        table_layout.addWidget(self.btn_calculate)
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

    def update_band_options(self, row):
        """根据环数选择更新下拉框选项"""
        band_combo = self.table.cellWidget(row, 1)
        if not isinstance(band_combo, QtWidgets.QComboBox):
            return

        band_type = band_combo.currentText()

        # 清除所有下拉框并设置新选项
        for col in range(2, 7):
            combo = self.table.cellWidget(row, col)
            if isinstance(combo, QtWidgets.QComboBox):
                combo.clear()
                combo.setCurrentIndex(-1)  # 重置选择状态

                # 四环电阻配置
                if band_type == "四环":
                    if col == 2 or col == 3:  # 环1-2: 基础颜色
                        combo.addItems(self.base_colors)
                    elif col == 4:  # 环3: 倍率环
                        combo.addItems(self.multiplier_bands)
                    elif col == 5:  # 环4: 误差环
                        combo.addItems(self.tolerance_bands)
                        combo.setEnabled(True)
                    elif col == 6:  # 环5: 禁用
                        combo.setEnabled(False)

                # 五环电阻配置
                else:
                    if col in (2, 3, 4):  # 环1-3: 基础颜色
                        combo.addItems(self.base_colors)
                    elif col == 5:  # 环4: 倍率环
                        combo.addItems(self.multiplier_bands)
                    elif col == 6:  # 环5: 误差环
                        combo.addItems(self.tolerance_bands)
                        combo.setEnabled(True)

            combo.setCurrentIndex(-1)  # 重置选择状态

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

            # 环数选择
            band_combo = QtWidgets.QComboBox()
            band_combo.addItems(["四环", "五环"])
            band_combo.currentIndexChanged.connect(lambda _, row=idx: self.update_band_options(row))
            self.table.setCellWidget(idx, 1, band_combo)

            # 初始化所有下拉框
            for col in range(2, 7):
                combo = QtWidgets.QComboBox()
                if isinstance(combo, QtWidgets.QComboBox):
                    combo.setCurrentIndex(-1)  # 默认未选择
                self.table.setCellWidget(idx, col, combo)

            # 初始化选项配置
            self.update_band_options(idx)

            # 计算阻值列（占位）
            self.table.setItem(idx, 7, QtWidgets.QTableWidgetItem(""))

    def highlight_box(self):
        """高亮选中的检测框"""
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.draw_annotations(selected_row)
        else:
            self.draw_annotations()

    def calculate_resistance(self):
        """计算每个电阻的阻值并填入表格最后一列"""
        for row in range(self.table.rowCount()):
            band_combo = self.table.cellWidget(row, 1)
            if not isinstance(band_combo, QtWidgets.QComboBox):
                continue

            band_type = band_combo.currentText()
            colors = []
            valid = True
            for col in range(2, 7):
                combo = self.table.cellWidget(row, col)
                if isinstance(combo, QtWidgets.QComboBox) and combo.isEnabled():
                    if combo.currentIndex() == -1:
                        valid = False
                        break
                    colors.append(combo.currentText())
                else:
                    if band_type == "四环" and col == 6:
                        continue
                    valid = False
                    break

            if valid:
                if band_type == "四环":
                    base_value = int(str(self.base_colors.index(colors[0])) + str(self.base_colors.index(colors[1])))
                    multiplier = self.multiplier_bands.index(colors[2])
                    tolerance = self.tolerance_bands.index(colors[3])
                    multiplier_value = [1, 10, 100, 1000, 10000, 100000, 1000000, 0.1, 0.01][multiplier]
                    tolerance_value = ["±1%", "±2%", "±0.5%", "±5%", "±10%"][tolerance]
                    resistance = base_value * multiplier_value
                else:  # 五环电阻
                    base_value = int(
                        str(self.base_colors.index(colors[0])) + str(self.base_colors.index(colors[1])) + str(
                            self.base_colors.index(colors[2])))
                    multiplier = self.multiplier_bands.index(colors[3])
                    tolerance = self.tolerance_bands.index(colors[4])
                    multiplier_value = [1, 10, 100, 1000, 10000, 100000, 1000000, 0.1, 0.01][multiplier]
                    tolerance_value = ["±1%", "±2%", "±0.5%", "±5%", "±10%"][tolerance]
                    resistance = base_value * multiplier_value

                # 单位转换
                if resistance >= 1e6:
                    resistance_str = f"{resistance / 1e6:.1f}M"
                elif resistance >= 1e3:
                    resistance_str = f"{resistance / 1e3:.1f}K"
                else:
                    resistance_str = f"{resistance:.1f}"

                result = f"{resistance_str}Ω {tolerance_value}"
                self.table.setItem(row, 7, QtWidgets.QTableWidgetItem(result))

    def save_annotations(self):
        """保存标注结果"""
        self.annotations.clear()
        validation_errors = 0

        for row in range(self.table.rowCount()):
            # 获取控件引用
            number_item = self.table.item(row, 0)
            band_combo = self.table.cellWidget(row, 1)

            if not number_item or not isinstance(band_combo, QtWidgets.QComboBox):
                continue

            # 验证必填项
            valid = True
            colors = []
            for col in range(2, 7):
                combo = self.table.cellWidget(row, col)
                if isinstance(combo, QtWidgets.QComboBox) and combo.isEnabled():
                    if combo.currentIndex() == -1:
                        valid = False
                    colors.append(combo.currentText() if combo.currentIndex() != -1 else "")
                else:
                    colors.append("")

            if not valid:
                validation_errors += 1
                continue

            # 保存有效数据
            self.annotations[number_item.text()] = {
                "type": band_combo.currentText(),
                "colors": colors
            }

        if validation_errors > 0:
            self.logger.log(f"存在 {validation_errors} 个未完整填写的电阻数据", "ERROR")
            QtWidgets.QMessageBox.warning(self, "保存警告", f"有 {validation_errors} 个电阻数据未完整填写！")
        else:
            self.logger.log(f"已保存的色环数据：{self.annotations}", "INFO")
            QtWidgets.QMessageBox.information(self, "保存成功", "所有色环数据已完整保存！")

    def closeEvent(self, event):
        self.save_annotations()
        super().closeEvent(event)

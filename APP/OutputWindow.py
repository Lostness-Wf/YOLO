from PySide6 import QtWidgets, QtCore, QtGui

class OutputWindow(QtWidgets.QWidget):
    def __init__(self, logger=None):
        super().__init__()
        self.current_id = 1
        self.logger = logger
        self.setup_ui()

    def setup_ui(self):
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 表格
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编号", "坐标", "类名", "置信度", "测试"])

        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self._setup_floating_button()

        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 4px;
                border: 1px solid #E0E0E0;
            }
            QTableWidget::item {
                border: 1px solid #E0E0E0;
                padding: 2px 4px;
            }
        """)

        main_layout.addWidget(self.table)

    def _setup_floating_button(self):
        # 创建悬浮按钮
        self.btn_float = QtWidgets.QPushButton(self.table)
        self.btn_float.setIcon(QtGui.QIcon("Icons/clear.svg"))
        self.btn_float.setFixedSize(24, 24)
        self.btn_float.setToolTip("清空结果")
        self.btn_float.clicked.connect(self.clear_results)

        # 设置按钮样式
        self.btn_float.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 4px;
            }
        """)

        # 初始定位
        self._position_button()

        # 绑定尺寸变化事件
        self.table.horizontalHeader().geometriesChanged.connect(self._position_button)
        self.table.verticalScrollBar().valueChanged.connect(self._position_button)

    def _position_button(self):
        """动态计算按钮位置"""
        # 获取标题栏高度
        header_height = self.table.horizontalHeader().height()
        # 计算X坐标（左边距4px）
        x_pos = 4
        # 计算Y坐标（垂直居中）
        y_pos = (header_height - self.btn_float.height()) // 2
        # 应用位置
        self.btn_float.move(x_pos, y_pos)

    def add_detection_result(self, coords, class_name, confidence, test_text="测试"):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.current_id)))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"({coords[0]:.1f}, {coords[1]:.1f})"))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(class_name))
        self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{confidence:.2f}"))
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(test_text))
        self.current_id += 1

    def clear_results(self):
        self.table.setRowCount(0)
        self.current_id = 1
        if self.logger:
            self.logger.log("清空检测结果", "WARNING")
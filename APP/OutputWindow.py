from PySide6 import QtWidgets, QtCore, QtGui

class OutputWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.current_id = 1
        self.setup_ui()

    def setup_ui(self):
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)

        # 清除按钮
        self.btn_clear = QtWidgets.QPushButton()
        self.btn_clear.setIcon(QtGui.QIcon("Icons/clear.svg"))
        self.btn_clear.setFixedSize(24, 24)
        self.btn_clear.setToolTip("清空结果")
        self.btn_clear.clicked.connect(self.clear_results)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 4px;
            }
        """)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_clear)

        # 表格
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编号", "坐标", "类名", "置信度", "测试"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # 设置样式
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

        # 组合布局
        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.table)

    def add_detection_result(self, coords, class_name, confidence, test_text = "测试"):
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
from pathlib import Path
from PySide6 import QtWidgets, QtGui
import csv


class OutputWindow(QtWidgets.QWidget):
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger
        self.csv_dir = Path("DetectResult")
        self.mode_caches = {}  # 模式缓存字典 {mode_id: [results]}
        self.current_mode = 0  # 当前显示的模式
        self.selected_rows = set()

        self.initialize_components()
        self.create_result_directory()
        self.table.itemSelectionChanged.connect(self.handle_selection_changed)

    def initialize_components(self):
        """初始化界面组件"""
        # main_layout = QtWidgets.QVBoxLayout(self)
        # main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)

        # 结果表格初始化
        # self.table = QtWidgets.QTableWidget()
        # self.table.setColumnCount(5)
        # self.table.setHorizontalHeaderLabels(["编号", "坐标", "类名", "置信度", "电阻阻值"])
        # self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        # self.table.verticalHeader().setVisible(False)
        # self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 结果表格初始化
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编号", "坐标", "类名", "置信度", "电阻阻值"])

        # 表格样式设置
        for col in range(4):
            self.table.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)

        # 设置第一列宽度（“编号“）
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(0, 100)

        # 设置第三列宽度（“类名“）
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(2, 100)

        # 设置第四列宽度（“置信度“）
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(3, 100)

        # 设置最后一列宽度（“电阻阻值“）
        self.table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(4,  250)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # 表格样式
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

        # 悬浮按钮
        self.setup_floating_button()
        main_layout.addWidget(self.table)

    def setup_floating_button(self):
        """初始化清空结果的悬浮按钮"""
        self.btn_float = QtWidgets.QPushButton(self.table)
        self.btn_float.setIcon(QtGui.QIcon("Icons/clear.svg"))
        self.btn_float.setFixedSize(24, 24)
        self.btn_float.setToolTip("清空结果")
        self.btn_float.clicked.connect(self.clear_results)

        # 按钮样式
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
        self.position_floating_button()
        self.table.horizontalHeader().geometriesChanged.connect(self.position_floating_button)
        self.table.verticalScrollBar().valueChanged.connect(self.position_floating_button)

    def position_floating_button(self):
        """动态计算并定位悬浮按钮"""
        header_height = self.table.horizontalHeader().height()
        x_pos = 4
        y_pos = (header_height - self.btn_float.height()) // 2
        self.btn_float.move(x_pos, y_pos)

    def handle_selection_changed(self):
        """处理表格行选择变化事件"""
        self.selected_rows = {item.row() for item in self.table.selectedItems()}
        self.trigger_redraw()
        selected_ids = self.get_selected_ids()
        self.logger.log(f"选中物体编号: {', '.join(map(str, selected_ids))}", "INFO")

    def trigger_redraw(self):
        """触发检测结果重新绘制"""
        if hasattr(self, 'main_window'):
            for page in self.main_window.pages:
                page.show_image(page.label_result, page.base_result_image)

    def switch_mode_cache(self, mode_id):
        """切换模式缓存"""
        self.current_mode = mode_id
        if mode_id not in self.mode_caches:
            self.mode_caches[mode_id] = []
        self.refresh_table()

    def refresh_table(self):
        """刷新表格显示当前模式数据"""
        self.table.setRowCount(0)
        self.current_id = 1

        for item in self.mode_caches.get(self.current_mode, []):
            self.add_row_to_table(item)

    def get_selected_ids(self):
        """获取选中的物体编号列表（从1开始）"""
        return [
            int(self.table.item(row, 0).text())
            for row in self.selected_rows
            if row < self.table.rowCount()
        ]

    def create_result_directory(self):
        """创建结果保存目录"""
        try:
            self.csv_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            if self.logger:
                self.logger.log(f"创建结果目录失败: {str(e)}", "ERROR")

    def get_next_csvfile(self):
        """获取下一个可用的CSV文件名"""
        index = 1
        while True:
            csv_path = self.csv_dir / f"DetectResult{index}.csv"
            if not csv_path.exists():
                return csv_path
            index += 1

    def save_to_csv(self):
        """保存表格数据到CSV文件"""
        try:
            csv_file = self.get_next_csvfile()
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 写入标题行
                headers = [self.table.horizontalHeaderItem(i).text()
                           for i in range(self.table.columnCount())]
                writer.writerow(headers)

                # 写入数据行
                for row in range(self.table.rowCount()):
                    row_data = [
                        self.table.item(row, col).text()
                        for col in range(self.table.columnCount())
                    ]
                    writer.writerow(row_data)

            if self.logger:
                self.logger.log(f"检测结果已保存到: {csv_file.name}", "SUCCESS")
        except Exception as e:
            if self.logger:
                self.logger.log(f"保存CSV失败: {str(e)}", "ERROR")

    def add_detection_result(self, coords, class_name, confidence, tht_value="测试"):
        """添加检测结果到当前模式缓存"""
        if self.current_mode not in self.mode_caches:
            self.mode_caches[self.current_mode] = []

        self.mode_caches[self.current_mode].append({
            "coords": coords,
            "class": class_name,
            "confidence": confidence,
            "text": tht_value
        })

        self.refresh_table()

    def add_row_to_table(self, data):
        """向表格添加单行数据"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.current_id)))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"({data['coords'][0]:.1f}, {data['coords'][1]:.1f})"))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(data['class']))
        self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{data['confidence']:.2f}"))
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(data['text']))
        self.current_id += 1

    def clear_results(self):
        """清空当前模式检测结果"""
        if self.current_mode in self.mode_caches:
            self.mode_caches[self.current_mode].clear()
        self.table.setRowCount(0)
        self.current_id = 1
        if self.logger:
            self.logger.log(f"已清空模式{self.current_mode}的检测结果", "WARNING")
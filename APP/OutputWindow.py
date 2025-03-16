from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
import csv

class OutputWindow(QtWidgets.QWidget):
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger
        self.csv_dir = Path("DetectResult")
        self.mode_caches = {}  # 新增：模式缓存字典 {mode_id: [results]}
        self.current_mode = 0  # 当前显示的模式
        self.setup_ui()
        self.create_result_dir()
        self.table.itemSelectionChanged.connect(self.handle_selection_changed)
        self.selected_rows = set()

    def handle_selection_changed(self):
        self.selected_rows = {item.row() for item in self.table.selectedItems()}
        self.trigger_redraw()
        selected_ids = self.get_selected_ids()
        log_msg = f"获取选中物体编号: {', '.join(map(str, selected_ids))}"
        self.logger.log(log_msg, "INFO")

    def trigger_redraw(self):
        if hasattr(self, 'main_window'):
            for page in self.main_window.pages:
                page.showImage(page.label_result, page.base_result_image)

    def switch_mode_cache(self, mode_id):
        self.current_mode = mode_id
        if mode_id not in self.mode_caches:
            self.mode_caches[mode_id] = []
        self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(0)
        self.current_id = 1

        for item in self.mode_caches.get(self.current_mode, []):
            self._add_row_to_table(item)

    def get_selected_ids(self):
        """获取选中的物体编号列表（从1开始）"""
        return [
            int(self.table.item(row, 0).text())
            for row in self.selected_rows
            if row < self.table.rowCount()
        ]

    def create_result_dir(self):
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

    def setup_ui(self):
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 表格
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["编号", "坐标", "类名", "置信度", "电阻阻值"])

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
        if self.current_mode not in self.mode_caches:
            self.mode_caches[self.current_mode] = []

        self.mode_caches[self.current_mode].append({
            "coords": coords,
            "class": class_name,
            "confidence": confidence,
            "text": test_text
        })

        self.refresh_table()

    def _add_row_to_table(self, data):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(self.current_id)))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"({data['coords'][0]:.1f}, {data['coords'][1]:.1f})"))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(data['class']))
        self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{data['confidence']:.2f}"))
        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(data['text']))
        self.current_id += 1

    def clear_results(self):
        if self.current_mode in self.mode_caches:
            self.mode_caches[self.current_mode].clear()
        self.table.setRowCount(0)
        self.current_id = 1
        if self.logger:
            self.logger.log(f"清空模式{self.current_mode}的检测结果", "WARNING")
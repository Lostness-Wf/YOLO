from PySide6 import QtWidgets
from detection_mode_page1 import DetectionModePage1
from detection_mode_page2 import DetectionModePage2
from Log import Logger, LogWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PCB缺陷检测（Designed by 卫福春阳）')
        self.resize(1400, 900)

        # 创建全局日志系统
        self.log_widget = LogWidget()
        self.logger = Logger(self.log_widget)

        self.init_ui()
        self.logger.log("应用程序启动", "INFO")

    def init_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # 主内容区域
        content_layout = QtWidgets.QHBoxLayout()

        # 左侧导航栏
        self.tab_list = QtWidgets.QListWidget()
        self.tab_list.addItems(["检测模式一", "检测模式二（测试）"])
        self.tab_list.setFixedWidth(150)
        self.tab_list.currentRowChanged.connect(self.change_tab)
        content_layout.addWidget(self.tab_list)

        # 页面区域
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.pages = [
            DetectionModePage1(self.logger),  # 传入logger实例
            DetectionModePage2(self.logger)  # 传入logger实例
        ]
        for page in self.pages:
            self.stacked_widget.addWidget(page)
        content_layout.addWidget(self.stacked_widget)

        main_layout.addLayout(content_layout, 4)

        # 底部日志区域
        log_group = QtWidgets.QGroupBox("系统日志")
        log_layout = QtWidgets.QVBoxLayout()
        log_layout.addWidget(self.log_widget)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group, 1)

        self.tab_list.setCurrentRow(0)

    def change_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
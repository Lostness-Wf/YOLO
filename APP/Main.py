from PySide6 import QtWidgets
from detection_mode_page1 import DetectionModePage1
from detection_mode_page2 import DetectionModePage2

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PCB缺陷检测（Designed by 卫福春阳）')
        self.resize(1400, 900)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        self.tab_list = QtWidgets.QListWidget()
        self.tab_list.addItems(["检测模式一", "检测模式二（测试）"])
        self.tab_list.currentRowChanged.connect(self.change_tab)
        main_layout.addWidget(self.tab_list, 1)

        self.pages = [
            DetectionModePage1(),
            DetectionModePage2()
        ]

        self.stacked_widget = QtWidgets.QStackedWidget()
        for page in self.pages:
            self.stacked_widget.addWidget(page)
        main_layout.addWidget(self.stacked_widget, 4)

        self.tab_list.setCurrentRow(0)

    def change_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
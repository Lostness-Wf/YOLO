from PySide6 import QtWidgets, QtCore, QtGui
from DetectionMode1 import DetectionModePage1
from DetectionMode2 import DetectionModePage2
from LogWindow import Logger, LogWidget
from OutputWindow import OutputWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PCB缺陷检测（Designed by 卫福春阳）')
        self.resize(1400, 900)

        # 设置任务栏图标
        self.setWindowIcon(QtGui.QIcon("Icons/app_icon.icns"))

        # 初始化日志系统
        self.log_widget = LogWidget()
        self.logger = Logger(self.log_widget)

        # 导航栏属性
        self.is_nav_collapsed = True
        self.nav_width_expanded = 150
        self.nav_width_collapsed = 60

        self.initialize_interface()
        self.logger.log("应用程序启动成功", "INFO")

    def initialize_interface(self):
        """初始化主界面布局"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # 左侧导航栏
        self.nav_container = QtWidgets.QWidget()
        self.nav_container.setFixedWidth(self.nav_width_collapsed)
        self.nav_container.setStyleSheet("""
            QWidget {
                background-color: #F5F5F5;
                border-right: 1px solid #E0E0E0;
            }
        """)

        # 导航栏布局
        nav_layout = QtWidgets.QVBoxLayout(self.nav_container)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(5)

        # 折叠/展开按钮
        self.toggle_btn = QtWidgets.QPushButton()
        self.toggle_btn.setIcon(QtGui.QIcon("Icons/menu.svg"))
        self.toggle_btn.setFixedSize(32, 32)
        self.toggle_btn.clicked.connect(self.toggle_navigation)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 4px;
            }
        """)
        nav_layout.addWidget(self.toggle_btn, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        # 导航按钮
        self.nav_buttons = [
            self.create_navigation_button("    检测模式一", QtGui.QIcon("Icons/mode1.svg"), 0),
            self.create_navigation_button("    （测试）", QtGui.QIcon("Icons/mode2.svg"), 1)
        ]
        for btn in self.nav_buttons:
            nav_layout.addWidget(btn)

        nav_layout.addStretch()

        # 页面堆栈
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.pages = [
            DetectionModePage1(self.logger),
            DetectionModePage2(self.logger)
        ]
        for page in self.pages:
            self.stacked_widget.addWidget(page)

        # 主布局
        main_layout.addWidget(self.nav_container)
        main_layout.addWidget(self.stacked_widget, 1)

        # 底部日志区域
        log_dock = QtWidgets.QDockWidget("系统日志", self)
        log_dock.setWidget(self.log_widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, log_dock)

        # 右侧输出窗口
        self.output_window = OutputWindow(self.logger)
        output_dock = QtWidgets.QDockWidget("检测结果", self)
        output_dock.setWidget(self.output_window)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, output_dock)
        self.output_window.main_window = self

        # 窗口布局设置
        self.splitDockWidget(log_dock, output_dock, QtCore.Qt.Orientation.Horizontal)

        # 传递输出窗口引用
        for page in self.pages:
            if hasattr(page, 'set_output_window'):
                page.set_output_window(self.output_window)

        # 初始化选中状态
        self.nav_buttons[0].setChecked(True)

    def create_navigation_button(self, text, icon, index):
        """创建导航栏按钮"""
        btn = QtWidgets.QToolButton()
        btn.setText(text)
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(40, 40))
        btn.setCheckable(True)
        btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
        btn.setFixedSize(60, 60)
        btn.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: transparent;
                border-radius: 10px; 
                padding: 8px;
                font-size: 14px;
                text-align: center;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
            QToolButton:checked {
                background-color: #BBDEFB;
            }
        """)
        btn.clicked.connect(lambda: self.switch_tab(index))
        return btn

    def toggle_navigation(self):
        """切换导航栏展开/折叠状态"""
        animation = QtCore.QPropertyAnimation(self.nav_container, b"minimumWidth")
        animation.setDuration(200)
        animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
        target_width = self.nav_width_expanded if self.is_nav_collapsed else self.nav_width_collapsed
        animation.setStartValue(self.nav_container.width())
        animation.setEndValue(target_width)
        animation.valueChanged.connect(lambda: self.nav_container.setMinimumWidth(animation.currentValue()))
        animation.finished.connect(self.handle_animation_finished)
        animation.start()

    def handle_animation_finished(self):
        """导航栏动画完成后的处理"""
        if self.is_nav_collapsed:
            for btn in self.nav_buttons:
                btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                btn.setFixedSize(150, 60)
        else:
            for btn in self.nav_buttons:
                btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly)
                btn.setFixedSize(60, 60)
        self.is_nav_collapsed = not self.is_nav_collapsed
        self.nav_container.updateGeometry()
        self.update()

    def switch_tab(self, index):
        """切换功能页面"""
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.output_window.switch_mode_cache(index)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setWindowIcon(QtGui.QIcon("Icons/app_icon.icns"))
    window = MainWindow()
    window.show()
    app.exec()
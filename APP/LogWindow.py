from PySide6 import QtWidgets, QtGui
from pathlib import Path
import time


class Logger:
    def __init__(self, log_widget=None):
        self.log_widget = log_widget
        self.log_dir = Path("Log")
        self.log_file = self.get_next_logfile()
        self.create_log_directory()

    def get_next_logfile(self):
        """获取下一个可用的日志文件名"""
        self.log_dir.mkdir(exist_ok=True)
        index = 1
        while True:
            log_path = self.log_dir / f"Log{index}.txt"
            if not log_path.exists():
                return log_path
            index += 1

    def create_log_directory(self):
        """创建日志存储目录"""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"无法创建日志目录: {str(e)}")

    def log(self, message, level="INFO"):
        """记录日志到文件和GUI组件"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"

        # 写入日志文件
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"写入日志文件失败: {str(e)}")

        # 显示到GUI组件
        if self.log_widget:
            self.log_widget.append_log(log_entry, level)


class LogWidget(QtWidgets.QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_interface()

    def setup_interface(self):
        """初始化日志显示界面"""
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextBrowser {
                background-color: #F8F9FA;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """)

    def append_log(self, text, level):
        """添加带颜色格式的日志条目"""
        color_map = {
            "INFO": "#000000",
            "WARNING": "#E67E22",
            "ERROR": "#E74C3C",
            "SUCCESS": "#2ECC71"
        }

        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

        # 设置文本颜色格式
        text_format = QtGui.QTextCharFormat()
        text_format.setForeground(QtGui.QColor(color_map.get(level, "#000000")))
        cursor.insertText(text + "\n", text_format)

        # 自动滚动到底部
        self.ensureCursorVisible()
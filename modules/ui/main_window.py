import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from sentinel.core.events import Events
import qdarktheme

class JarvisUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SENTINEL Assistant")
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.status_label = QLabel("IDLE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.status_label)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: #00ffff; border: 1px solid #00ffff;")
        self.layout.addWidget(self.log_display)
        self.setCentralWidget(self.central_widget)
        Events.subscribe(Events.STATUS_CHANGED, self.update_status)
        Events.subscribe(Events.USER_SPOKEN_TEXT, self.log_user_text)
        Events.subscribe(Events.ASSISTANT_RESPONSE, self.log_assistant_text)
        Events.subscribe(Events.CLAP_DETECTED, self.handle_clap_visual)
        Events.subscribe(Events.DOUBLE_CLAP_DETECTED, self.handle_double_clap_visual)

    def handle_clap_visual(self):
        self.log_display.append("<i style='color: #5555ff;'>[Clap detected]</i>")

    def handle_double_clap_visual(self):
        self.log_display.append("<b style='color: #ffaa00;'>[Double clap detected — listening...]</b>")
        self.update_status("Listening")

    def update_status(self, status):
        self.status_label.setText(status.upper())
        color = "#ff0000" if status == "Listening" else "#00ffff"
        self.status_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")

    def log_user_text(self, text):
        self.log_display.append(f"<b>You:</b> {text}")

    def log_assistant_text(self, text):
        self.log_display.append(f"<b>Sentinel:</b> {text}")

def start_ui():
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()
    window = JarvisUI()
    window.show()
    return app, window

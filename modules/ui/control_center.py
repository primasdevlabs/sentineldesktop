from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal
from sentinel.core.events import Events

class ModuleCard(QFrame):
    def __init__(self, name, display_name, manager):
        super().__init__()
        self.name = name
        self.manager = manager
        self.setObjectName("ModuleCard")
        self.setStyleSheet("""
            #ModuleCard {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 15px;
            }
            QLabel { color: white; }
        """)
        
        layout = QHBoxLayout(self)
        self.label = QLabel(display_name)
        self.label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.status_indicator = QLabel("●")
        self.update_status_ui()
        
        self.toggle_btn = QPushButton("Toggle")
        self.toggle_btn.setFixedWidth(80)
        self.toggle_btn.clicked.connect(self.on_toggle)
        
        layout.addWidget(self.status_indicator)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.toggle_btn)

    def update_status_ui(self):
        status = self.manager.get_status(self.name)
        colors = {"active": "#00ff88", "inactive": "#ff4444", "error": "#ffaa00"}
        self.status_indicator.setStyleSheet(f"color: {colors.get(status, 'white')}; font-size: 18px;")

    def on_toggle(self):
        status = self.manager.get_status(self.name)
        if status == "active":
            self.manager.disable(self.name)
        else:
            self.manager.enable(self.name)
        self.update_status_ui()

class ControlCenter(QWidget):
    def __init__(self, module_manager):
        super().__init__()
        self.manager = module_manager
        self.setWindowTitle("SENTINEL CONTROL CENTER")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(450, 600)
        
        self.main_layout = QVBoxLayout(self)
        self.container = QFrame()
        self.container.setStyleSheet("background: rgba(15, 15, 20, 0.95); border-radius: 15px; border: 1px solid #333;")
        self.main_layout.addWidget(self.container)
        
        self.layout = QVBoxLayout(self.container)
        self.header = QLabel("SYSTEM CONTROL")
        self.header.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 20px; margin: 10px;")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.header)
        
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        
        # Modules to control
        modules = [
            ("wake_word", "Wake Word"),
            ("clap_detector", "Clap Detection"),
            ("stt", "Speech Recognition"),
            ("tts", "Neural Voice"),
            ("scheduler", "Task Scheduler"),
            ("notification_watcher", "Notifications"),
            ("proactive_engine", "Proactive AI")
        ]
        
        for i, (key, display) in enumerate(modules):
            card = ModuleCard(key, display, self.manager)
            self.grid.addWidget(card, i // 1, i % 1) # Vertical list for now
            
        self.close_btn = QPushButton("CLOSE")
        self.close_btn.clicked.connect(self.hide)
        self.layout.addWidget(self.close_btn)

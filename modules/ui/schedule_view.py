from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from sentinel.core.events import Events

class EventCard(QFrame):
    def __init__(self, title, time_str, event_type="meeting"):
        super().__init__()
        self.setObjectName("EventCard")
        # Glassmorphism/Futuristic Style
        color_map = {"meeting": "#00aaff", "reminder": "#ffaa00", "urgent": "#ff4400"}
        accent = color_map.get(event_type, "#00aaff")
        
        self.setStyleSheet(f"""
            #EventCard {{
                background: rgba(255, 255, 255, 0.05);
                border-left: 4px solid {accent};
                border-radius: 4px;
                padding: 10px;
                margin-bottom: 5px;
            }}
            QLabel {{ color: white; background: transparent; }}
        """)
        
        layout = QVBoxLayout(self)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.time_label = QLabel(time_str)
        self.time_label.setStyleSheet("font-size: 11px; color: #aaaaaa;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.time_label)

class ScheduleView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: rgba(10, 10, 10, 0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px;")
        self.resize(350, 500)
        
        self.layout = QVBoxLayout(self)
        self.header = QLabel("DAILY SCHEDULE")
        self.header.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 18px; margin-bottom: 10px;")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        
        self.layout.addWidget(self.scroll)
        
        Events.subscribe("schedule.updated", self.refresh_events)

    def refresh_events(self, events=None):
        # Clear existing
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
            
        for event in events:
            card = EventCard(event['summary'], event['time'], event.get('type', 'meeting'))
            self.scroll_layout.addWidget(card)

import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from sentinel.core.events import Events
from .orb_renderer import OrbRenderer
from .schedule_view import ScheduleView

class OrbWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.renderer = OrbRenderer()
        self.layout.addWidget(self.renderer)
        
        # Schedule View (Hidden by default)
        self.schedule_view = ScheduleView()
        self.schedule_view.hide()
        
        self.setCentralWidget(self.central_widget)
        self.resize(300, 300)
        self.is_fullscreen = False
        self.move_to_corner()
        
        Events.subscribe(Events.STATUS_CHANGED, self.handle_status_change)
        Events.subscribe(Events.ASSISTANT_RESPONSE, self.handle_speaking)
        Events.subscribe("ui.toggle_schedule", self.toggle_schedule)

    def move_to_corner(self):
        screen = self.screen().availableGeometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 20)

    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal(); self.resize(300, 300); self.move_to_corner()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True

    def toggle_schedule(self, visible=True):
        if visible:
            screen = self.screen().availableGeometry()
            self.schedule_view.move(screen.width() - self.schedule_view.width() - 330, screen.height() - self.schedule_view.height() - 20)
            self.schedule_view.show()
        else:
            self.schedule_view.hide()

    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()

    def handle_status_change(self, status):
        self.renderer.set_state(status)

    def handle_speaking(self, text=None):
        self.renderer.set_state("speaking")
        self.renderer.set_amplitude(1.0)

def start_orb_ui():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    window = OrbWindow()
    window.show()
    return app, window

import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QPoint
from sentinel.core.events import Events
from .orb_renderer import OrbRenderer
from .control_center import ControlCenter
from .dashboard import DashboardUI

class LockOrbHUD(QMainWindow):
    def __init__(self, brain):
        super().__init__()
        self.brain = brain
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.renderer = OrbRenderer()
        self.layout.addWidget(self.renderer)
        self.setCentralWidget(self.central_widget)
        
        # HUD Layers
        self.controls = ControlCenter(self.brain.module_manager)
        self.dashboard = DashboardUI(self.brain)
        
        self.resize(150, 150)
        self.move_to_corner()
        self.oldPos = self.pos()

        Events.subscribe(Events.STATUS_CHANGED, self.renderer.set_state)
        Events.subscribe("ui.toggle_controls", self.toggle_controls)
        Events.subscribe("ui.toggle_dashboard", self.toggle_dashboard)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        context_menu.setStyleSheet("QMenu { background-color: #1a1a1a; color: white; border: 1px solid #333; }")
        
        show_dashboard = QAction("Show Dashboard", self)
        show_dashboard.triggered.connect(lambda: self.toggle_dashboard(True))
        
        show_controls = QAction("Show Control Center", self)
        show_controls.triggered.connect(lambda: self.toggle_controls(True))
        
        quit_action = QAction("Exit Sentinel", self)
        quit_action.triggered.connect(sys.exit)
        
        context_menu.addAction(show_dashboard)
        context_menu.addAction(show_controls)
        context_menu.addSeparator()
        context_menu.addAction(quit_action)
        
        context_menu.exec(event.globalPos())

    def move_to_corner(self):
        screen = self.screen().availableGeometry()
        self.move(screen.width() - self.width() - 50, 100)

    def toggle_controls(self, visible=None):
        if visible: self.controls.show()
        else: self.controls.hide()

    def toggle_dashboard(self, visible=None):
        if visible: self.dashboard.show()
        else: self.dashboard.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

def start_lock_orb(brain):
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    window = LockOrbHUD(brain)
    window.show()
    return app, window

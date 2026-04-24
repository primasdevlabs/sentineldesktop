"""
Primas Dev Labs - Sentinel Theme
"""
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication

def apply_sentinel_theme(app: QApplication) -> None:
    """Applies the Sentinel-Blue dark theme."""
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 170, 255))
    app.setPalette(palette)

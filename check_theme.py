from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
import sys

app = QApplication(sys.argv)
palette = app.palette()

def print_role(role, name):
    color = palette.color(role)
    print(f"{name}: {color.name()} (Alpha: {color.alpha()})")

print("Checking System Palette for Transparency...")
print_role(QPalette.ColorRole.Window, "Window")
print_role(QPalette.ColorRole.WindowText, "WindowText")
print_role(QPalette.ColorRole.Base, "Base (Text Edit Background)")
print_role(QPalette.ColorRole.AlternateBase, "AlternateBase")
print_role(QPalette.ColorRole.ToolTipBase, "ToolTipBase")
print_role(QPalette.ColorRole.Button, "Button")

print("\nNote: If Alpha is 255, the theme is providing opaque colors.")



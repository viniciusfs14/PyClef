import sys
from PySide6.QtWidgets import QApplication
from .gui.intro_window import IntroVideoWindow

class PyClef:

    def __init__(self):
        self.app = QApplication(sys.argv)

    def run(self):

        self.window = IntroVideoWindow()
        self.window.show()

        sys.exit(self.app.exec())
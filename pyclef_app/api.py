import sys

from PySide6.QtWidgets import QApplication

from .window import MainClef


def Pyclef():
    app = QApplication.instance()
    owns_app = app is None
    if owns_app:
        app = QApplication(sys.argv)

    window = MainClef()
    window.show()

    if owns_app:
        return app.exec()
    return window

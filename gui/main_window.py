from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox
)

from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QUrl
)

from PySide6.QtGui import QDesktopServices

import os

from ..ui.mainPyclef import Ui_MainWindow
from ..ui import resources
from ..engine import PyClefEngine


class MainClef(QMainWindow, Ui_MainWindow):

    def __init__(self):

        super().__init__()

        self.setupUi(self)

        self.engine = PyClefEngine()

        self.setup_connections()

    def setup_connections(self):

        self.menuButton.clicked.connect(self.sidebaranimation)

        self.aboutButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.about)
        )

        self.homeButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.Home)
        )

        self.sheetsButton.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page)
        )

        self.selectsheetButton.clicked.connect(self.openFile)

        self.website.mousePressEvent = lambda event: self.open_website()

    def open_website(self):
        QDesktopServices.openUrl(QUrl("https://viniciusfs14.github.io/PyClef/"))

    def openFile(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a sheet",
            "",
            "Images (*.png *.jpg *.jpeg);;All Files (*.*)"
        )

        if file_path:

            print(f"Selected file: {file_path}")

            if self.engine:
                self.processar_imagem(file_path)

            else:

                QMessageBox.warning(
                    self,
                    "Error",
                    "YOLO model was not loaded correctly."
                )

    def sidebaranimation(self):

        width = self.Sidebar.minimumWidth()

        if width == 400:
            newWidth = 70
        else:
            newWidth = 400

        self.animation_min = QPropertyAnimation(self.Sidebar, b"minimumWidth")
        self.animation_min.setDuration(300)
        self.animation_min.setStartValue(width)
        self.animation_min.setEndValue(newWidth)
        self.animation_min.setEasingCurve(QEasingCurve.InOutCubic)

        self.animation_max = QPropertyAnimation(self.Sidebar, b"maximumWidth")
        self.animation_max.setDuration(300)
        self.animation_max.setStartValue(width)
        self.animation_max.setEndValue(newWidth)
        self.animation_max.setEasingCurve(QEasingCurve.InOutCubic)

        self.animation_min.start()
        self.animation_max.start()

    def open_results_folder(self):

        user_path = os.path.expanduser("~")

        results_folder = os.path.join(
            user_path,
            "Desktop",
            "PyClef_Results"
        )

        if os.path.exists(results_folder):

            os.startfile(results_folder)

        else:

            os.makedirs(results_folder, exist_ok=True)
            os.startfile(results_folder)
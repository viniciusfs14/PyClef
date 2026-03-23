from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt
from pathlib import Path

from .main_window import MainClef


class IntroVideoWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        self.player = QMediaPlayer()
        self.audio = QAudioOutput()

        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)

        BASE_DIR = Path(__file__).resolve().parent
        video_path = BASE_DIR.parent / "video" / "intro.mp4"

        self.player.setSource(QUrl.fromLocalFile(str(video_path)))

        self.player.mediaStatusChanged.connect(self.check_video_end)

        # tamanho fixo da intro
        self.resize(800, 450)

        self.show()

        self.player.play()

    def check_video_end(self, status):

        if status == QMediaPlayer.MediaStatus.EndOfMedia:

            self.player.stop()
            self.close()

            self.main = MainClef()
            self.main.showMaximized()
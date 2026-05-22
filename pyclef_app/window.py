import sys
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, QThread, QTimer, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from .engine import process_score_files
from .ui.mainPyclef import Ui_MainWindow
from .ui.resources import *  # noqa: F401,F403


BASE_DIR = Path(__file__).resolve().parent
WEBSITE_URL = "https://viniciusfs14.github.io/PyClef/"

TRANSLATIONS = {
    "en": {
        "sidebar_caption": "Sheet music to audio",
        "language_button": "Português",
        "home_nav": "Home",
        "scores_nav": "Scores",
        "about_nav": "About",
        "home_eyebrow": "Welcome to",
        "home_title": "PyClef",
        "home_subtitle": "AI-powered sheet music analysis for annotations, audio, MIDI, and synchronized playback.",
        "start_button": "Start",
        "select_scores": "Select scores",
        "open_results": "Open results",
        "status_ready": "Ready to select a score.",
        "status_selected": "{count} file(s) selected.",
        "status_processing": "Processing score...",
        "status_done": "Processing complete. Results are ready.",
        "status_error": "Processing found an error.",
        "step1_title": "Choose the score",
        "step1_caption": "PDF, PNG, JPG, or JPEG.",
        "step2_title": "Set the BPM",
        "step2_caption": "Control the tempo before processing.",
        "step3_title": "Process",
        "step3_caption": "Follow progress in real time.",
        "step4_title": "Open files",
        "step4_caption": "MP3, MIDI, video, and annotations when ready.",
        "workflow_title": "Typical workflow",
        "workflow_note": "Use Start to open the score workspace. From there, choose files, set the BPM, and generate the outputs you need.",
        "process_eyebrow": "Direct workflow",
        "process_title": "Processing",
        "process_hint": "Select a PDF or score image, set the BPM, choose the outputs, and follow the progress.",
        "no_files": "No file selected.",
        "bpm": "BPM",
        "choose_files": "Choose files",
        "process": "Process",
        "generate": "Generate",
        "all": "All",
        "annotations": "Annotated score",
        "audio": "MP3",
        "midi": "MIDI",
        "video": "Video",
        "video_warning": "Video output can take longer because PyClef needs to render and synchronize every frame.",
        "progress_waiting": "Waiting to process.",
        "progress_complete": "100% complete.",
        "log_placeholder": "Processing logs appear here.",
        "open_folder": "Open folder",
        "open_annotations": "Open annotations",
        "open_video": "Open video",
        "open_audio": "Open audio",
        "open_midi": "Open MIDI",
        "about_text": "PyClef is a hybrid approach to Optical Music Recognition, combining deep-learning detection with structural staff modeling.\n\nThe desktop workflow is direct: choose pages, set the BPM, and generate synchronized audio, MIDI, video, and annotated score outputs.",
        "about_eyebrow": "About PyClef",
        "about_title": "A practical OMR tool for musicians and students.",
        "about_body": "PyClef combines object detection, music-structure rules, sound synthesis, MIDI export, and synchronized visualization to make sheet music easier to inspect, hear, and study.",
        "about_card_1_title": "Recognition",
        "about_card_1_body": "Detects musical symbols and maps them to notes using staff-aware pitch logic.",
        "about_card_2_title": "Playback",
        "about_card_2_body": "Generates MP3 and MIDI so the detected score can be heard and reused.",
        "about_card_3_title": "Review",
        "about_card_3_body": "Creates annotated pages and video playback to help validate the result.",
        "author_title": "Developed by Vinicius Fernandes",
        "author_body": "Built as a research and creative tool at the intersection of music, computer vision, and signal processing.",
        "website_button": "Visit website",
        "select_dialog": "Select scores",
        "select_filter": "Scores (*.pdf *.png *.jpg *.jpeg);;PDF (*.pdf);;Images (*.png *.jpg *.jpeg);;All files (*.*)",
        "select_score_title": "Select a score",
        "select_score_msg": "Choose a PDF or image before processing.",
        "already_processing_title": "Processing",
        "already_processing_msg": "Processing is already running.",
        "done_title": "Done",
        "done_msg": "Files generated successfully.",
        "error_title": "Processing error",
        "error_msg": "Could not finish. Check the logs for details.",
        "missing_title": "File not found",
        "missing_msg": "This result has not been generated yet.",
    },
    "pt": {
        "sidebar_caption": "Partitura para audio",
        "language_button": "English",
        "home_nav": "Inicio",
        "scores_nav": "Partituras",
        "about_nav": "Sobre",
        "home_eyebrow": "Bem-vindo ao",
        "home_title": "PyClef",
        "home_subtitle": "Analise de partituras com IA para anotacoes, audio, MIDI e reproducao sincronizada.",
        "start_button": "Iniciar",
        "select_scores": "Selecionar partituras",
        "open_results": "Abrir resultados",
        "status_ready": "Pronto para selecionar uma partitura.",
        "status_selected": "{count} arquivo(s) selecionado(s).",
        "status_processing": "Processando partitura...",
        "status_done": "Processamento concluido. Resultados prontos para abrir.",
        "status_error": "O processamento encontrou um erro.",
        "step1_title": "Escolha a partitura",
        "step1_caption": "PDF, PNG, JPG ou JPEG.",
        "step2_title": "Ajuste o BPM",
        "step2_caption": "Controle o andamento antes de processar.",
        "step3_title": "Processe",
        "step3_caption": "Acompanhe os registros em tempo real.",
        "step4_title": "Abra os arquivos",
        "step4_caption": "MP3, MIDI, video e anotacoes quando prontos.",
        "workflow_title": "Fluxo recomendado",
        "workflow_note": "Use Iniciar para abrir o ambiente de partituras. Depois, escolha arquivos, ajuste o BPM e gere as saidas que precisar.",
        "process_eyebrow": "Fluxo direto",
        "process_title": "Processamento",
        "process_hint": "Selecione PDF ou imagem da partitura, defina o BPM, escolha as saidas e acompanhe o progresso.",
        "no_files": "Nenhum arquivo selecionado.",
        "bpm": "BPM",
        "choose_files": "Escolher arquivos",
        "process": "Processar",
        "generate": "Gerar",
        "all": "Tudo",
        "annotations": "Partitura anotada",
        "audio": "MP3",
        "midi": "MIDI",
        "video": "Video",
        "video_warning": "A saida em video pode demorar mais, porque o PyClef precisa renderizar e sincronizar cada quadro.",
        "progress_waiting": "Aguardando processamento.",
        "progress_complete": "100% concluido.",
        "log_placeholder": "Os registros do processamento aparecem aqui.",
        "open_folder": "Abrir pasta",
        "open_annotations": "Abrir anotacoes",
        "open_video": "Abrir video",
        "open_audio": "Abrir audio",
        "open_midi": "Abrir MIDI",
        "about_text": "PyClef e uma abordagem hibrida para Reconhecimento Optico de Partituras Musicais, integrando deteccao por aprendizado profundo com modelagem estrutural da pauta.\n\nO fluxo desktop e direto: escolha as paginas, ajuste o BPM e gere audio, MIDI, video sincronizado e partituras anotadas.",
        "about_eyebrow": "Sobre o PyClef",
        "about_title": "Uma ferramenta OMR pratica para musicos e estudantes.",
        "about_body": "O PyClef combina deteccao de objetos, regras estruturais de partitura, sintese sonora, exportacao MIDI e visualizacao sincronizada para facilitar a leitura, audicao e estudo de partituras.",
        "about_card_1_title": "Reconhecimento",
        "about_card_1_body": "Detecta simbolos musicais e mapeia notas usando logica de altura baseada na pauta.",
        "about_card_2_title": "Reproducao",
        "about_card_2_body": "Gera MP3 e MIDI para ouvir e reutilizar a partitura detectada.",
        "about_card_3_title": "Revisao",
        "about_card_3_body": "Cria paginas anotadas e video sincronizado para validar o resultado.",
        "author_title": "Desenvolvido por Vinicius Fernandes",
        "author_body": "Criado como ferramenta de pesquisa e criatividade na intersecao entre musica, visao computacional e processamento de sinais.",
        "website_button": "Visitar site",
        "select_dialog": "Selecione as partituras",
        "select_filter": "Partituras (*.pdf *.png *.jpg *.jpeg);;PDF (*.pdf);;Imagens (*.png *.jpg *.jpeg);;Todos (*.*)",
        "select_score_title": "Selecione uma partitura",
        "select_score_msg": "Escolha um PDF ou imagem antes de processar.",
        "already_processing_title": "Processando",
        "already_processing_msg": "Ja existe um processamento em andamento.",
        "done_title": "Concluido",
        "done_msg": "Arquivos gerados com sucesso.",
        "error_title": "Erro no processamento",
        "error_msg": "Nao foi possivel finalizar. Veja os registros para identificar o problema.",
        "missing_title": "Arquivo nao encontrado",
        "missing_msg": "Esse resultado ainda nao foi gerado.",
    },
}


class NeonNavButton(QPushButton):
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.property("active") != True:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for inset, width, alpha in ((2, 6, 38), (5, 3, 78), (7, 2, 230)):
            rect = self.rect().adjusted(inset, inset, -inset, -inset)
            painter.setPen(QPen(QColor(64, 214, 255, alpha), width))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(rect, 18, 18)

        painter.end()


class NeonStartButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pulse = 0.0

    def set_pulse(self, value):
        self.pulse = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        radius = 22
        fill = QColor(64, 214, 255)
        if self.isDown():
            fill = QColor(31, 189, 232)
        elif self.underMouse():
            fill = QColor(115, 226, 255)

        button_rect = self.rect().adjusted(8, 8, -8, -8)
        painter.setPen(Qt.NoPen)
        painter.setBrush(fill)
        painter.drawRoundedRect(button_rect, radius, radius)

        pulse_alpha = int(80 + 160 * self.pulse)
        soft_alpha = int(20 + 90 * self.pulse)
        for inset, width, alpha in (
            (1, 7, soft_alpha),
            (4, 4, min(210, pulse_alpha)),
            (8, 2, 255),
        ):
            rect = self.rect().adjusted(inset, inset, -inset, -inset)
            painter.setPen(QPen(QColor(64, 214, 255, alpha), width))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(rect, 22, 22)

        font = QFont(self.font())
        font.setBold(True)
        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(QColor(7, 17, 31))
        painter.drawText(button_rect, Qt.AlignCenter, self.text())
        painter.end()


class ProcessingThread(QThread):
    log = Signal(str)
    progress = Signal(int, str)
    finished = Signal(bool, dict)

    def __init__(self, file_list, bpm, output_options, language):
        super().__init__()
        self.file_list = file_list
        self.bpm = bpm
        self.output_options = output_options
        self.language = language

    def run(self):
        try:
            def emit_progress(message, percent=None):
                self.log.emit(message)
                if percent is not None:
                    self.progress.emit(max(0, min(100, int(percent))), message)

            result = process_score_files(
                self.file_list,
                self.bpm,
                progress_callback=emit_progress,
                output_options={**self.output_options, "language": self.language},
            )
            self.finished.emit(True, result or {})
        except Exception as exc:
            prefix = "Processing error" if self.language == "en" else "Erro durante o processamento"
            self.log.emit(f"{prefix}: {exc}")
            self.finished.emit(False, {})


class MainClef(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.selected_files = []
        self.result_files = {}
        self.processing_thread = None
        self._sidebar_open = True
        self.language = "en"
        self.step_labels = []
        self.about_card_labels = []
        self._progress_pulse = 0
        self._start_pulse = 0
        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(110)
        self.progress_timer.timeout.connect(self._animate_progress_bar)
        self.start_button_timer = QTimer(self)
        self.start_button_timer.setInterval(120)
        self.start_button_timer.timeout.connect(self._animate_start_button)

        self.setWindowTitle("PyClef")
        self.setWindowIcon(QIcon(str(BASE_DIR / "ui" / "logo.png")))
        self.setMinimumSize(980, 640)

        self._configure_existing_ui()
        self._build_home_panel()
        self._build_about_panel()
        self._build_processing_panel()
        self._apply_style()
        self._connect_actions()
        self.apply_language()
        self._set_active_page(self.Home, self.homeButton)
        self.start_button_timer.start()

    def _configure_existing_ui(self):
        self.centralwidget.setStyleSheet("")
        self.widget.setStyleSheet("")
        self.Sidebar.setStyleSheet("")
        self.verticaloptions.setStyleSheet("")
        self.stackedWidget.setStyleSheet("")
        self.Home.setStyleSheet("")
        self.about.setStyleSheet("")
        self.page.setStyleSheet("")
        self.text.setStyleSheet("")
        self.Sidebar.setMinimumWidth(300)
        self.Sidebar.setMaximumWidth(300)
        self.gridLayout.setContentsMargins(16, 16, 16, 16)
        self.gridLayout.setHorizontalSpacing(18)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout_5.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setContentsMargins(14, 18, 14, 18)
        self.verticalLayout.setSpacing(18)
        self.Logo.hide()
        self.widget_2.hide()
        self.logoAbout.setMaximumHeight(240)
        self.label_3.setMaximumSize(260, 260)

        self.sidebar_brand = QLabel()
        self.sidebar_brand.setObjectName("sidebarLogo")
        sidebar_logo = QPixmap(str(BASE_DIR / "ui" / "logo_black.png"))
        self.sidebar_brand.setPixmap(
            sidebar_logo.scaled(
                QSize(180, 132),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        self.sidebar_brand.setScaledContents(False)
        self.sidebar_brand.setFixedHeight(142)
        self.sidebar_brand.setAlignment(Qt.AlignCenter)
        self.sidebar_brand_caption = QLabel("Sheet music to audio")
        self.sidebar_brand_caption.setObjectName("sidebarCaption")
        self.sidebar_brand_caption.setAlignment(Qt.AlignCenter)
        self.language_button = QPushButton("Português")
        self.language_button.setObjectName("languageButton")
        self.language_button.setCursor(Qt.PointingHandCursor)
        self.language_button.setFixedSize(132, 48)
        self.language_button.setIcon(self._language_button_icon())
        self.language_button.setIconSize(QSize(60, 22))
        self.language_button.setText(self._language_button_text())
        self.language_button.setToolTip("Language")
        self.verticalLayout.insertWidget(0, self.sidebar_brand_caption)
        self.verticalLayout.insertWidget(0, self.sidebar_brand)

        self.menuButton.hide()
        self.homeButton = self._replace_nav_button(self.homeButton)
        self.aboutButton = self._replace_nav_button(self.aboutButton)
        self.sheetsButton = self._replace_nav_button(self.sheetsButton)
        self.verticalLayout.addWidget(self.homeButton)
        self.verticalLayout.addWidget(self.sheetsButton)
        self.verticalLayout.addWidget(self.aboutButton)
        self.verticalLayout.addWidget(self.language_button, 0, Qt.AlignHCenter)

        self.selectsheetButton.setToolTip("Select scores")
        self.selectsheetButton.setCursor(Qt.PointingHandCursor)
        self.website.setCursor(Qt.PointingHandCursor)
        self.label.setPixmap(QPixmap(str(BASE_DIR / "ui" / "logo_black.png")))
        self.label_3.setPixmap(QPixmap(str(BASE_DIR / "ui" / "logo_black.png")))

    def _replace_nav_button(self, old_button):
        button = NeonNavButton(self.verticaloptions)
        button.setObjectName(old_button.objectName())
        button.setText(old_button.text())
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(56)
        button.setSizePolicy(old_button.sizePolicy())
        self.verticalLayout.removeWidget(old_button)
        old_button.hide()
        old_button.deleteLater()
        return button


    def _build_home_panel(self):
        self.home_panel = QFrame(self.Home)
        self.home_panel.setObjectName("homePanel")
        self.home_panel.setMinimumHeight(520)

        layout = QVBoxLayout(self.home_panel)
        layout.setContentsMargins(56, 42, 56, 42)
        layout.setSpacing(18)

        self.home_eyebrow = QLabel()
        self.home_eyebrow.setObjectName("homeEyebrow")
        self.home_eyebrow.setAlignment(Qt.AlignCenter)

        self.home_logo = QLabel()
        self.home_logo.setObjectName("homeLogo")
        home_logo = QPixmap(str(BASE_DIR / "ui" / "logo_black.png"))
        self.home_logo.setPixmap(home_logo.scaled(QSize(440, 300), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.home_logo.setAlignment(Qt.AlignCenter)
        self.home_logo.setMinimumHeight(300)

        self.home_title = QLabel()
        self.home_title.setObjectName("homeTitle")
        self.home_title.setWordWrap(True)
        self.home_title.setAlignment(Qt.AlignCenter)

        self.home_subtitle = QLabel()
        self.home_subtitle.setObjectName("homeSubtitle")
        self.home_subtitle.setWordWrap(True)
        self.home_subtitle.setAlignment(Qt.AlignCenter)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.home_select_button = NeonStartButton()
        self.home_select_button.setObjectName("startButton")
        self.home_select_button.setCursor(Qt.PointingHandCursor)
        self.home_select_button.setFixedSize(220, 58)

        self.home_results_button = QPushButton()
        self.home_results_button.setObjectName("secondaryButton")
        self.home_results_button.setCursor(Qt.PointingHandCursor)

        action_row.addStretch(1)
        action_row.addWidget(self.home_select_button)
        action_row.addStretch(1)

        self.home_status_label = QLabel()
        self.home_status_label.setObjectName("statusPill")
        self.home_status_label.setAlignment(Qt.AlignCenter)

        workflow_panel = self._make_workflow_panel()

        layout.addStretch(1)
        layout.addWidget(self.home_eyebrow)
        layout.addWidget(self.home_logo)
        layout.addLayout(action_row)
        layout.addWidget(self.home_status_label)
        layout.addWidget(workflow_panel)
        layout.addStretch(1)

        self.gridLayout_4.addWidget(self.home_panel, 0, 0, 1, 1)

    def _build_about_panel(self):
        self.logoAbout.hide()
        self.aboutText.hide()
        self.picture.hide()

        self.about_panel = QFrame(self.about)
        self.about_panel.setObjectName("aboutPanel")

        layout = QVBoxLayout(self.about_panel)
        layout.setContentsMargins(36, 34, 36, 34)
        layout.setSpacing(18)

        self.about_eyebrow = QLabel()
        self.about_eyebrow.setObjectName("eyebrow")

        self.about_title = QLabel()
        self.about_title.setObjectName("panelTitle")
        self.about_title.setWordWrap(True)

        self.about_body = QLabel()
        self.about_body.setObjectName("panelSubtitle")
        self.about_body.setWordWrap(True)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        cards_row.addWidget(self._make_about_card("about_card_1_title", "about_card_1_body"))
        cards_row.addWidget(self._make_about_card("about_card_2_title", "about_card_2_body"))
        cards_row.addWidget(self._make_about_card("about_card_3_title", "about_card_3_body"))

        author_frame = QFrame()
        author_frame.setObjectName("authorFrame")
        author_layout = QHBoxLayout(author_frame)
        author_layout.setContentsMargins(20, 18, 20, 18)
        author_layout.setSpacing(18)

        author_photo = QLabel()
        author_photo.setObjectName("authorPhoto")
        photo = QPixmap(str(BASE_DIR / "ui" / "vinicius.png"))
        author_photo.setPixmap(photo.scaled(QSize(128, 128), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        author_photo.setAlignment(Qt.AlignCenter)
        author_photo.setFixedSize(138, 138)

        author_text_layout = QVBoxLayout()
        author_text_layout.setSpacing(6)
        self.author_title = QLabel()
        self.author_title.setObjectName("stepTitle")
        self.author_body = QLabel()
        self.author_body.setObjectName("stepCaption")
        self.author_body.setWordWrap(True)
        self.website_button = QPushButton()
        self.website_button.setObjectName("primaryButton")
        self.website_button.setCursor(Qt.PointingHandCursor)
        self.website_button.clicked.connect(self.open_website)

        author_text_layout.addWidget(self.author_title)
        author_text_layout.addWidget(self.author_body)
        author_text_layout.addWidget(self.website_button, 0, Qt.AlignLeft)
        author_text_layout.addStretch(1)

        author_layout.addWidget(author_photo)
        author_layout.addLayout(author_text_layout)

        layout.addWidget(self.about_eyebrow)
        layout.addWidget(self.about_title)
        layout.addWidget(self.about_body)
        layout.addLayout(cards_row)
        layout.addWidget(author_frame)
        layout.addStretch(1)

        self.gridLayout_7.addWidget(self.about_panel, 0, 0, 1, 1)

    def _make_about_card(self, title_key, body_key):
        card = QFrame()
        card.setObjectName("stepCard")
        card.setMinimumHeight(150)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(8)

        title = QLabel()
        title.setObjectName("stepTitle")
        title.setWordWrap(True)

        body = QLabel()
        body.setObjectName("stepCaption")
        body.setWordWrap(True)

        card_layout.addWidget(title)
        card_layout.addWidget(body)
        card_layout.addStretch(1)
        self.about_card_labels.append((title, title_key, body, body_key))
        return card

    def _make_workflow_panel(self):
        panel = QFrame()
        panel.setObjectName("workflowPanel")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 16, 20, 16)
        panel_layout.setSpacing(12)

        self.workflow_title = QLabel()
        self.workflow_title.setObjectName("workflowTitle")
        self.workflow_note = QLabel()
        self.workflow_note.setObjectName("workflowNote")
        self.workflow_note.setWordWrap(True)

        flow_row = QHBoxLayout()
        flow_row.setSpacing(10)
        for index, (title_key, caption_key) in enumerate(
            (
                ("step1_title", "step1_caption"),
                ("step2_title", "step2_caption"),
                ("step3_title", "step3_caption"),
                ("step4_title", "step4_caption"),
            )
        ):
            flow_row.addWidget(self._make_workflow_item(str(index + 1), title_key, caption_key))
            if index < 3:
                arrow = QLabel(">")
                arrow.setObjectName("workflowArrow")
                arrow.setAlignment(Qt.AlignCenter)
                flow_row.addWidget(arrow)

        panel_layout.addWidget(self.workflow_title)
        panel_layout.addLayout(flow_row)
        panel_layout.addWidget(self.workflow_note)
        return panel

    def _make_workflow_item(self, number, title_key, caption_key):
        item = QFrame()
        item.setObjectName("workflowItem")
        item.setCursor(Qt.ArrowCursor)
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(8)

        number_label = QLabel(number)
        number_label.setObjectName("workflowNumber")
        number_label.setAlignment(Qt.AlignCenter)
        number_label.setFixedSize(26, 26)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        title_label = QLabel()
        title_label.setObjectName("workflowItemTitle")
        title_label.setWordWrap(True)
        caption_label = QLabel()
        caption_label.setObjectName("workflowItemCaption")
        caption_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(caption_label)
        item_layout.addWidget(number_label)
        item_layout.addLayout(text_layout)
        self.step_labels.append((title_label, title_key, caption_label, caption_key))
        return item

    def _make_step_card(self, number, title_key, caption_key):
        card = QFrame()
        card.setObjectName("stepCard")
        card.setMinimumHeight(118)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(6)

        number_label = QLabel(number)
        number_label.setObjectName("stepNumber")

        title_label = QLabel()
        title_label.setObjectName("stepTitle")
        title_label.setWordWrap(True)

        caption_label = QLabel()
        caption_label.setObjectName("stepCaption")
        caption_label.setWordWrap(True)

        card_layout.addWidget(number_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(caption_label)
        self.step_labels.append((title_label, title_key, caption_label, caption_key))
        return card

    def _build_processing_panel(self):
        self.processing_panel = QFrame(self.page)
        self.processing_panel.setObjectName("processingPanel")

        layout = QVBoxLayout(self.processing_panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        self.process_eyebrow = QLabel()
        self.process_eyebrow.setObjectName("eyebrow")

        self.process_title = QLabel()
        self.process_title.setObjectName("panelTitle")

        self.files_label = QLabel()
        self.files_label.setObjectName("filesLabel")
        self.files_label.setWordWrap(True)

        options_row = QHBoxLayout()
        options_row.setSpacing(12)

        self.bpm_label = QLabel()
        self.bpm_label.setObjectName("fieldLabel")

        self.bpm_input = QSpinBox()
        self.bpm_input.setRange(30, 300)
        self.bpm_input.setValue(72)
        self.bpm_input.setSingleStep(1)
        self.bpm_input.setObjectName("bpmInput")

        self.choose_button = QPushButton()
        self.choose_button.setObjectName("secondaryButton")
        self.choose_button.setCursor(Qt.PointingHandCursor)

        self.process_button = QPushButton()
        self.process_button.setObjectName("primaryButton")
        self.process_button.setCursor(Qt.PointingHandCursor)
        self.process_button.setEnabled(False)

        options_row.addWidget(self.bpm_label)
        options_row.addWidget(self.bpm_input)
        options_row.addStretch(1)
        options_row.addWidget(self.choose_button)
        options_row.addWidget(self.process_button)

        output_frame = QFrame()
        output_frame.setObjectName("outputFrame")
        output_layout = QHBoxLayout(output_frame)
        output_layout.setContentsMargins(16, 12, 16, 12)
        output_layout.setSpacing(14)

        self.output_label = QLabel()
        self.output_label.setObjectName("fieldLabel")
        self.output_all = QCheckBox()
        self.output_annotations = QCheckBox()
        self.output_annotations.setChecked(True)
        self.output_audio = QCheckBox()
        self.output_midi = QCheckBox()
        self.output_video = QCheckBox()
        for checkbox in (
            self.output_all,
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
        ):
            checkbox.setCursor(Qt.PointingHandCursor)

        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_all)
        output_layout.addWidget(self.output_annotations)
        output_layout.addWidget(self.output_audio)
        output_layout.addWidget(self.output_midi)
        output_layout.addWidget(self.output_video)
        output_layout.addStretch(1)

        self.video_warning_label = QLabel()
        self.video_warning_label.setObjectName("warningPill")
        self.video_warning_label.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)

        self.progress_status_label = QLabel()
        self.progress_status_label.setObjectName("progressStatus")
        self.progress_status_label.setVisible(False)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(180)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        results_row = QHBoxLayout()
        results_row.setSpacing(10)

        self.open_folder_button = QPushButton()
        self.open_folder_button.setObjectName("secondaryButton")
        self.open_folder_button.setCursor(Qt.PointingHandCursor)
        self.open_folder_button.setEnabled(False)

        self.open_video_button = QPushButton()
        self.open_video_button.setObjectName("secondaryButton")
        self.open_video_button.setCursor(Qt.PointingHandCursor)
        self.open_video_button.setEnabled(False)

        self.open_audio_button = QPushButton()
        self.open_audio_button.setObjectName("secondaryButton")
        self.open_audio_button.setCursor(Qt.PointingHandCursor)
        self.open_audio_button.setEnabled(False)

        self.open_midi_button = QPushButton()
        self.open_midi_button.setObjectName("secondaryButton")
        self.open_midi_button.setCursor(Qt.PointingHandCursor)
        self.open_midi_button.setEnabled(False)

        self.open_annotations_button = QPushButton()
        self.open_annotations_button.setObjectName("secondaryButton")
        self.open_annotations_button.setCursor(Qt.PointingHandCursor)
        self.open_annotations_button.setEnabled(False)

        results_row.addWidget(self.open_folder_button)
        results_row.addWidget(self.open_annotations_button)
        results_row.addWidget(self.open_video_button)
        results_row.addWidget(self.open_audio_button)
        results_row.addWidget(self.open_midi_button)
        results_row.addStretch(1)

        self.process_hint = QLabel()
        self.process_hint.setObjectName("panelSubtitle")
        self.process_hint.setWordWrap(True)

        layout.addWidget(self.process_eyebrow)
        layout.addWidget(self.process_title)
        layout.addWidget(self.process_hint)
        layout.addWidget(self.files_label)
        layout.addLayout(options_row)
        layout.addWidget(output_frame)
        layout.addWidget(self.video_warning_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_status_label)
        layout.addWidget(self.log_output)
        layout.addLayout(results_row)

        self.gridLayout_10.addWidget(self.processing_panel, 1, 0, 1, 1)

    def _connect_actions(self):
        self.menuButton.setEnabled(False)
        self.language_button.clicked.connect(self.toggle_language)
        self.homeButton.clicked.connect(lambda: self._set_active_page(self.Home, self.homeButton))
        self.aboutButton.clicked.connect(lambda: self._set_active_page(self.about, self.aboutButton))
        self.sheetsButton.clicked.connect(lambda: self._set_active_page(self.page, self.sheetsButton))

        self.home_select_button.clicked.connect(self.open_scores_page)
        self.selectsheetButton.clicked.connect(self.open_file_dialog)
        self.choose_button.clicked.connect(self.open_file_dialog)
        self.process_button.clicked.connect(self.start_processing)
        self.output_all.toggled.connect(self._sync_output_controls)
        self.output_all.toggled.connect(lambda checked: self._update_video_warning())
        for checkbox in (
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
        ):
            checkbox.toggled.connect(self._ensure_output_selection)
        self.output_video.toggled.connect(lambda checked: self._update_video_warning())

        self.home_results_button.clicked.connect(self.open_results_folder)
        self.open_folder_button.clicked.connect(self.open_results_folder)
        self.open_annotations_button.clicked.connect(lambda: self.open_result("annotations"))
        self.open_video_button.clicked.connect(lambda: self.open_result("video"))
        self.open_audio_button.clicked.connect(lambda: self.open_result("audio"))
        self.open_midi_button.clicked.connect(lambda: self.open_result("midi"))
        self.website.mousePressEvent = lambda event: self.open_website()
        self._sync_output_controls(False)
        self._update_video_warning()

    def open_scores_page(self):
        self._set_active_page(self.page, self.sheetsButton)

    def _sync_output_controls(self, checked):
        for checkbox in (
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
        ):
            checkbox.setEnabled(not checked)
            if checked:
                checkbox.setChecked(False)
        if not checked and not any(
            checkbox.isChecked()
            for checkbox in (
                self.output_annotations,
                self.output_audio,
                self.output_midi,
                self.output_video,
            )
        ):
            self.output_annotations.setChecked(True)
        self._update_video_warning()

    def _ensure_output_selection(self):
        if self.output_all.isChecked():
            return
        if not any(
            checkbox.isChecked()
            for checkbox in (
                self.output_annotations,
                self.output_audio,
                self.output_midi,
                self.output_video,
            )
        ):
            self.output_annotations.setChecked(True)
        self._update_video_warning()

    def _video_output_selected(self):
        return self.output_all.isChecked() or self.output_video.isChecked()

    def _update_video_warning(self):
        if not hasattr(self, "video_warning_label"):
            return
        self.video_warning_label.setText(self.tr("video_warning"))
        self.video_warning_label.setVisible(self._video_output_selected())

    def _selected_output_options(self):
        if self.output_all.isChecked():
            return {
                "annotations": True,
                "audio": True,
                "midi": True,
                "video": True,
            }
        return {
            "annotations": self.output_annotations.isChecked(),
            "audio": self.output_audio.isChecked(),
            "midi": self.output_midi.isChecked(),
            "video": self.output_video.isChecked(),
        }

    def _set_progress_animation(self, active):
        if active:
            self.progress_timer.start()
        else:
            self.progress_timer.stop()
            self.progress_bar.setStyleSheet("")

    def _animate_progress_bar(self):
        self._progress_pulse = (self._progress_pulse + 1) % 18
        alpha = 135 + int((self._progress_pulse / 17) * 70)
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar::chunk {{
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(64, 214, 255, {alpha}),
                    stop:0.45 #73e2ff,
                    stop:1 rgba(64, 214, 255, {alpha}));
            }}
            """
        )

    def _animate_start_button(self):
        if not hasattr(self, "home_select_button"):
            return
        self._start_pulse = (self._start_pulse + 1) % 24
        wave = self._start_pulse / 23
        pulse = 1 - abs((wave * 2) - 1)
        self.home_select_button.set_pulse(pulse)

    def tr(self, key, **kwargs):
        text = TRANSLATIONS[self.language].get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _language_button_text(self):
        return "EN" if self.language == "en" else "PT"

    def _language_button_icon(self):
        icon_pixmap = QPixmap(60, 22)
        icon_pixmap.fill(Qt.transparent)

        br_flag = QPixmap(str(BASE_DIR / "ui" / "flags" / "br.png"))
        us_flag = QPixmap(str(BASE_DIR / "ui" / "flags" / "us.png"))
        br_flag = br_flag.scaled(QSize(28, 20), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        us_flag = us_flag.scaled(QSize(28, 20), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        painter = QPainter(icon_pixmap)
        painter.drawPixmap(0, 1, br_flag)
        painter.drawPixmap(32, 1, us_flag)
        painter.end()
        return QIcon(icon_pixmap)

    def toggle_language(self):
        self.language = "pt" if self.language == "en" else "en"
        self.apply_language()

    def apply_language(self):
        self.sidebar_brand_caption.setText(self.tr("sidebar_caption"))
        self.language_button.setText(self._language_button_text())
        self.language_button.setIcon(self._language_button_icon())
        self.language_button.setToolTip("Idioma" if self.language == "pt" else "Language")
        self.homeButton.setText(self.tr("home_nav"))
        self.sheetsButton.setText(self.tr("scores_nav"))
        self.aboutButton.setText(self.tr("about_nav"))

        self.home_eyebrow.setText(self.tr("home_eyebrow"))
        self.home_select_button.setText(self.tr("start_button"))
        self.home_results_button.setText(self.tr("open_results"))
        self.workflow_title.setText(self.tr("workflow_title"))
        self.workflow_note.setText(self.tr("workflow_note"))
        if self.selected_files:
            self.home_status_label.setText(self.tr("status_selected", count=len(self.selected_files)))
        elif self.result_files:
            self.home_status_label.setText(self.tr("status_done"))
        else:
            self.home_status_label.setText(self.tr("status_ready"))

        for title_label, title_key, caption_label, caption_key in self.step_labels:
            title_label.setText(self.tr(title_key))
            caption_label.setText(self.tr(caption_key))

        self.process_eyebrow.setText(self.tr("process_eyebrow"))
        self.process_title.setText(self.tr("process_title"))
        self.process_hint.setText(self.tr("process_hint"))
        self.bpm_label.setText(self.tr("bpm"))
        self.choose_button.setText(self.tr("choose_files"))
        self.process_button.setText(self.tr("process"))
        self.output_label.setText(self.tr("generate"))
        self.output_all.setText(self.tr("all"))
        self.output_annotations.setText(self.tr("annotations"))
        self.output_audio.setText(self.tr("audio"))
        self.output_midi.setText(self.tr("midi"))
        self.output_video.setText(self.tr("video"))
        self.video_warning_label.setText(self.tr("video_warning"))
        if not self.progress_status_label.isVisible():
            self.progress_status_label.setText(self.tr("progress_waiting"))
        self.log_output.setPlaceholderText(self.tr("log_placeholder"))
        self.open_folder_button.setText(self.tr("open_folder"))
        self.open_annotations_button.setText(self.tr("open_annotations"))
        self.open_video_button.setText(self.tr("open_video"))
        self.open_audio_button.setText(self.tr("open_audio"))
        self.open_midi_button.setText(self.tr("open_midi"))
        self.selectsheetButton.setToolTip(self.tr("select_scores"))
        self.text.setText(self.tr("about_text"))
        self.about_eyebrow.setText(self.tr("about_eyebrow"))
        self.about_title.setText(self.tr("about_title"))
        self.about_body.setText(self.tr("about_body"))
        self.author_title.setText(self.tr("author_title"))
        self.author_body.setText(self.tr("author_body"))
        self.website_button.setText(self.tr("website_button"))
        for title_label, title_key, body_label, body_key in self.about_card_labels:
            title_label.setText(self.tr(title_key))
            body_label.setText(self.tr(body_key))
        self._update_video_warning()
        self._update_selected_files()

    def _set_active_page(self, page, button):
        self.stackedWidget.setCurrentWidget(page)
        for nav_button in (self.homeButton, self.aboutButton, self.sheetsButton):
            is_active = nav_button is button
            nav_button.setProperty("active", is_active)
            if is_active:
                nav_button.setGraphicsEffect(None)
            else:
                nav_button.setGraphicsEffect(None)
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)

    def open_website(self):
        QDesktopServices.openUrl(QUrl(WEBSITE_URL))

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.tr("select_dialog"),
            str(BASE_DIR / "sheets" if (BASE_DIR / "sheets").exists() else Path.cwd()),
            self.tr("select_filter"),
        )

        if not files:
            return

        self.selected_files = sorted(files)
        self.result_files = {}
        self._set_active_page(self.page, self.sheetsButton)
        self._update_selected_files()
        self.home_status_label.setText(self.tr("status_selected", count=len(self.selected_files)))
        self._set_result_buttons_enabled(False)
        self.process_button.setEnabled(True)
        self.log_output.clear()
        self.log(self.tr("status_selected", count=len(self.selected_files)))

    def _update_selected_files(self):
        names = [Path(path).name for path in self.selected_files]
        if len(names) <= 3:
            text = "\n".join(names)
        else:
            text = "\n".join(names[:3]) + f"\n... e mais {len(names) - 3}"
        self.files_label.setText(text or self.tr("no_files"))

    def start_processing(self):
        if not self.selected_files:
            self.show_message(self.tr("select_score_title"), self.tr("select_score_msg"))
            return

        if self.processing_thread and self.processing_thread.isRunning():
            self.show_message(self.tr("already_processing_title"), self.tr("already_processing_msg"))
            return

        self.log_output.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_status_label.setVisible(True)
        self.progress_status_label.setText(self.tr("status_processing"))
        self._set_progress_animation(True)
        self._set_controls_enabled(False)
        self._set_result_buttons_enabled(False)
        self.home_status_label.setText(self.tr("status_processing"))
        self.log(self.tr("status_processing"))
        if self._video_output_selected():
            self.log(self.tr("video_warning"))

        self.processing_thread = ProcessingThread(
            self.selected_files,
            self.bpm_input.value(),
            self._selected_output_options(),
            self.language,
        )
        self.processing_thread.log.connect(self.log)
        self.processing_thread.progress.connect(self.on_progress_update)
        self.processing_thread.finished.connect(self.on_processing_finished)
        self.processing_thread.start()

    def on_progress_update(self, value, message):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(value)
        self.progress_status_label.setVisible(True)
        self.progress_status_label.setText(message)

    def on_processing_finished(self, success, result):
        self._set_progress_animation(False)
        self._set_controls_enabled(True)

        if success:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(100)
            self.progress_status_label.setVisible(True)
            self.progress_status_label.setText(self.tr("progress_complete"))
            self.result_files = {}
            for key, value in result.items():
                if isinstance(value, list):
                    self.result_files[key] = [
                        str((BASE_DIR / item).resolve()) if not Path(item).is_absolute() else item
                        for item in value
                    ]
                else:
                    self.result_files[key] = (
                        str((BASE_DIR / value).resolve()) if not Path(value).is_absolute() else value
                    )
            self._set_result_buttons_enabled(True)
            self.home_status_label.setText(self.tr("status_done"))
            self.log(self.tr("status_done"))
            self.show_message(self.tr("done_title"), self.tr("done_msg"))
        else:
            self.progress_bar.setVisible(False)
            self.progress_status_label.setVisible(True)
            self.progress_status_label.setText(self.tr("status_error"))
            self.home_status_label.setText(self.tr("status_error"))
            self.log(self.tr("status_error"))
            self.show_message(
                self.tr("error_title"),
                self.tr("error_msg"),
            )

    def _set_controls_enabled(self, enabled):
        self.home_select_button.setEnabled(enabled)
        self.selectsheetButton.setEnabled(enabled)
        self.choose_button.setEnabled(enabled)
        self.process_button.setEnabled(enabled and bool(self.selected_files))
        self.bpm_input.setEnabled(enabled)
        self.output_all.setEnabled(enabled)
        if enabled:
            self._sync_output_controls(self.output_all.isChecked())
        else:
            for checkbox in (
                self.output_annotations,
                self.output_audio,
                self.output_midi,
                self.output_video,
            ):
                checkbox.setEnabled(False)

    def _set_result_buttons_enabled(self, enabled):
        self.open_folder_button.setEnabled(enabled)
        self.open_annotations_button.setEnabled(enabled and bool(self.result_files.get("annotations")))
        self.open_video_button.setEnabled(enabled and bool(self.result_files.get("video")))
        self.open_audio_button.setEnabled(enabled and bool(self.result_files.get("audio")))
        self.open_midi_button.setEnabled(enabled and bool(self.result_files.get("midi")))

    def log(self, message):
        self.log_output.append(str(message))
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def open_result(self, key):
        path = self.result_files.get(key)
        if isinstance(path, list):
            path = path[0] if path else None
        if not path or not Path(path).exists():
            self.show_message(self.tr("missing_title"), self.tr("missing_msg"))
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def show_message(self, title, message):
        dialog = QDialog(self)
        dialog.setObjectName("appDialog")
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        body_label = QLabel(message)
        body_label.setObjectName("dialogBody")
        body_label.setWordWrap(True)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        ok_button = QPushButton("OK")
        ok_button.setObjectName("primaryButton")
        ok_button.clicked.connect(dialog.accept)
        button_row.addWidget(ok_button)

        layout.addWidget(title_label)
        layout.addWidget(body_label)
        layout.addLayout(button_row)
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()

    def open_results_folder(self):
        if self.result_files:
            first_value = next(iter(self.result_files.values()))
            if isinstance(first_value, list):
                first_value = first_value[0]
            folder = Path(first_value).parent
        else:
            folder = Path.cwd()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def sidebaranimation(self):
        return

    def _apply_style(self):
        self.setStyleSheet(
            """
            QMainWindow, QWidget#centralwidget, QWidget#widget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #080a12,
                    stop:0.55 #0b1020,
                    stop:1 #101827);
                color: #f7f9ff;
                font-family: "Segoe UI";
            }
            QWidget#Sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(25, 30, 47, 0.96),
                    stop:1 rgba(17, 21, 35, 0.96));
                border: 1px solid rgba(255, 255, 255, 0.13);
                border-radius: 26px;
            }
            QWidget#verticaloptions {
                background: transparent;
            }
            QStackedWidget,
            QWidget#Home,
            QWidget#about,
            QWidget#page {
                background: transparent;
                color: #f7f9ff;
            }
            QLabel {
                color: #f7f9ff;
                background: transparent;
            }
            QLabel#sidebarLogo {
                padding: 6px 0 0 0;
            }
            QLabel#sidebarCaption {
                color: #a3b1c8;
                font-size: 12px;
                font-weight: 600;
                padding: 0 0 28px 0;
            }
            QPushButton {
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
                padding: 11px 18px;
                min-height: 42px;
                background: rgba(255, 255, 255, 0.075);
                color: #f7f9ff;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.13);
                border-color: rgba(64, 214, 255, 0.52);
            }
            QPushButton:pressed {
                background: rgba(64, 214, 255, 0.18);
            }
            QPushButton:disabled {
                color: rgba(248, 250, 252, 0.42);
                background: rgba(255, 255, 255, 0.035);
                border-color: rgba(255, 255, 255, 0.06);
            }
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #45dcff,
                    stop:1 #1fbde8);
                color: #07111f;
                border-color: rgba(115, 226, 255, 0.86);
                border-radius: 18px;
                min-height: 48px;
                font-weight: 900;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #79e8ff,
                    stop:1 #35d2fa);
                border-color: #9aecff;
            }
            QPushButton#secondaryButton {
                background: rgba(255, 255, 255, 0.075);
                color: #f7f9ff;
                border-color: rgba(255, 255, 255, 0.14);
                border-radius: 18px;
                min-height: 48px;
            }
            QPushButton#secondaryButton:hover {
                background: rgba(64, 214, 255, 0.10);
                border-color: rgba(64, 214, 255, 0.42);
            }
            QPushButton#startButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #45dcff,
                    stop:1 #1fbde8);
                color: #07111f;
                border: 1px solid rgba(154, 236, 255, 0.34);
                border-radius: 22px;
                font-size: 16px;
                font-weight: 900;
                padding: 0 24px;
            }
            QPushButton#startButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #82ebff,
                    stop:1 #35d2fa);
                border: 1px solid rgba(199, 246, 255, 0.54);
            }
            QPushButton#startButton:pressed {
                background: #1fbde8;
                border: 1px solid rgba(115, 226, 255, 0.60);
            }
            QPushButton#languageButton {
                background: rgba(255, 255, 255, 0.105);
                border: 1px solid rgba(255, 255, 255, 0.20);
                border-radius: 18px;
                color: #f7f9ff;
                font-family: "Segoe UI";
                font-size: 15px;
                font-weight: 800;
                padding: 0 14px;
                text-align: center;
            }
            QPushButton#languageButton:hover {
                background: rgba(64, 214, 255, 0.14);
                border-color: rgba(64, 214, 255, 0.48);
            }
            QPushButton#languageButton:pressed {
                background: rgba(64, 214, 255, 0.22);
            }
            QPushButton#menuButton,
            QPushButton#homeButton,
            QPushButton#aboutButton,
            QPushButton#sheetsButton {
                color: #f8fafc;
                background: rgba(255, 255, 255, 0.035);
                border: 1px solid transparent;
                border-radius: 18px;
                text-align: center;
                padding: 0 18px;
                min-height: 52px;
                font-size: 16px;
                font-weight: 800;
            }
            QPushButton#homeButton:hover,
            QPushButton#aboutButton:hover,
            QPushButton#sheetsButton:hover,
            QPushButton#menuButton:hover {
                background: rgba(255,255,255,0.10);
                border-color: rgba(255, 255, 255, 0.10);
            }
            QPushButton[active="true"] {
                color: #f7fbff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(64, 214, 255, 0.16),
                    stop:0.08 rgba(64, 214, 255, 0.32),
                    stop:0.5 rgba(115, 226, 255, 0.24),
                    stop:0.92 rgba(64, 214, 255, 0.32),
                    stop:1 rgba(64, 214, 255, 0.16));
                border: 1px solid rgba(115, 226, 255, 0.22);
                border-radius: 18px;
            }
            QPushButton[active="true"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(64, 214, 255, 0.24),
                    stop:0.5 rgba(115, 226, 255, 0.34),
                    stop:1 rgba(64, 214, 255, 0.22));
                border-color: rgba(154, 236, 255, 0.34);
            }
            QPushButton#selectsheetButton {
                border: 1px dashed rgba(64, 214, 255, 0.45);
                background: rgba(255, 255, 255, 0.08);
                border-radius: 18px;
            }
            QPushButton#selectsheetButton:hover {
                background: rgba(64, 214, 255, 0.12);
            }
            QFrame#homePanel,
            QFrame#processingPanel,
            QWidget#Logo,
            QWidget#aboutText,
            QWidget#logoAbout,
            QWidget#picture,
            QWidget#widget_2 {
                background: rgba(14, 18, 30, 0.62);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
            }
            QFrame#homePanel,
            QFrame#processingPanel,
            QFrame#aboutPanel {
                background: rgba(24, 28, 44, 0.42);
            }
            QFrame#authorFrame {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
            }
            QLabel#authorPhoto {
                background: rgba(8, 10, 18, 0.28);
                border-radius: 16px;
            }
            QFrame#outputFrame {
                background: rgba(255, 255, 255, 0.055);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 16px;
            }
            QFrame#stepCard {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 16px;
            }
            QFrame#stepCard:hover {
                border-color: rgba(64, 214, 255, 0.34);
            }
            QFrame#workflowPanel {
                background: rgba(255, 255, 255, 0.035);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
            }
            QFrame#workflowItem {
                background: transparent;
                border: 0;
            }
            QLabel#eyebrow {
                color: #40d6ff;
                font-size: 12px;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QLabel#homeEyebrow {
                color: #40d6ff;
                font-size: 18px;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QLabel#homeLogo {
                padding: 2px 0 0 0;
            }
            QLabel#homeTitle {
                color: #f7f9ff;
                font-size: 48px;
                font-weight: 900;
            }
            QLabel#homeSubtitle {
                color: #d1dcf0;
                font-size: 18px;
                font-weight: 800;
            }
            QLabel#panelTitle {
                font-size: 30px;
                font-weight: 900;
                color: #f7f9ff;
            }
            QLabel#panelSubtitle,
            QLabel#filesLabel,
            QLabel#text {
                font-size: 15px;
                color: #a3b1c8;
                line-height: 1.5;
            }
            QLabel#statusPill {
                color: #f7f9ff;
                background: rgba(64, 214, 255, 0.10);
                border: 1px solid rgba(64, 214, 255, 0.28);
                border-radius: 14px;
                padding: 11px 14px;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#workflowTitle {
                color: #f7f9ff;
                font-size: 14px;
                font-weight: 900;
            }
            QLabel#workflowNote {
                color: #8290a8;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#workflowNumber {
                color: #07111f;
                background: #40d6ff;
                border-radius: 13px;
                font-size: 13px;
                font-weight: 900;
            }
            QLabel#workflowItemTitle {
                color: #f7f9ff;
                font-size: 13px;
                font-weight: 800;
            }
            QLabel#workflowItemCaption {
                color: #95a3ba;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#workflowArrow {
                color: rgba(64, 214, 255, 0.68);
                font-size: 18px;
                font-weight: 900;
                padding: 0 2px;
            }
            QLabel#stepNumber {
                color: #40d6ff;
                font-size: 22px;
                font-weight: 900;
            }
            QLabel#stepTitle {
                color: #f7f9ff;
                font-size: 15px;
                font-weight: 800;
            }
            QLabel#stepCaption {
                color: #a3b1c8;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#fieldLabel {
                color: #f7f9ff;
                font-weight: 700;
            }
            QCheckBox {
                color: #dbe7ff;
                font-size: 14px;
                font-weight: 600;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid rgba(255, 255, 255, 0.22);
                background: rgba(255, 255, 255, 0.06);
            }
            QCheckBox::indicator:checked {
                background: #40d6ff;
                border-color: #40d6ff;
            }
            QCheckBox:disabled {
                color: #68768f;
            }
            QSpinBox {
                min-width: 84px;
                min-height: 36px;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 14px;
                padding: 4px 8px;
                background: rgba(255, 255, 255, 0.08);
                color: #f7f9ff;
                font-weight: 700;
            }
            QTextEdit {
                background: rgba(8, 10, 18, 0.86);
                color: #dbeafe;
                border: 1px solid rgba(64, 214, 255, 0.20);
                border-radius: 18px;
                padding: 12px;
                font-family: "Consolas";
                font-size: 12px;
            }
            QLabel#warningPill {
                color: #f8d98a;
                background: rgba(245, 158, 11, 0.12);
                border: 1px solid rgba(245, 158, 11, 0.32);
                border-radius: 14px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 700;
            }
            QLabel#progressStatus {
                color: #a3b1c8;
                font-size: 13px;
                font-weight: 600;
                padding: 0 2px 4px 2px;
            }
            QProgressBar {
                min-height: 20px;
                max-height: 20px;
                border: 0;
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.10);
                color: #f7f9ff;
                text-align: center;
                font-size: 11px;
                font-weight: 800;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: #40d6ff;
            }
            QDialog#appDialog {
                background: #101827;
                border: 1px solid rgba(64, 214, 255, 0.25);
                border-radius: 18px;
            }
            QLabel#dialogTitle {
                color: #f7f9ff;
                font-size: 22px;
                font-weight: 900;
            }
            QLabel#dialogBody {
                color: #a3b1c8;
                font-size: 14px;
            }
            """
        )


def main():
    app = QApplication(sys.argv)
    window = MainClef()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

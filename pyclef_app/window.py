import base64
import json
import sys
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, QThread, QTimer, Qt, QUrl, QUrlQuery, Signal
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

try:
    from PySide6.QtWebEngineCore import QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView
except Exception:
    QWebEngineSettings = None
    QWebEngineView = None

from .diagnostics import (
    collect_environment_diagnostics,
    diagnostics_overall_status,
    format_diagnostics,
    summarize_diagnostics,
)
from .pipeline import process_score_pipeline
from .review_tools import export_corrected_midi, normalized_label, save_corrections
from .ui.mainPyclef import Ui_MainWindow
from .ui.resources import *  # noqa: F401,F403


BASE_DIR = Path(__file__).resolve().parent
WEBSITE_URL = "https://viniciusfs14.github.io/PyClef/"


def configure_web_view(view):
    if QWebEngineSettings is None:
        return
    settings = view.settings()
    attribute_root = getattr(QWebEngineSettings, "WebAttribute", QWebEngineSettings)
    for attribute_name, enabled in (
        ("JavascriptEnabled", True),
        ("LocalContentCanAccessRemoteUrls", True),
        ("LocalContentCanAccessFileUrls", True),
        ("PlaybackRequiresUserGesture", False),
    ):
        attribute = getattr(attribute_root, attribute_name, None)
        if attribute is not None:
            settings.setAttribute(attribute, enabled)

TRANSLATIONS = {
    "en": {
        "sidebar_caption": "Sheet music to audio",
        "language_button": "Português",
        "home_nav": "Home",
        "scores_nav": "Scores",
        "midi_nav": "MIDI Player",
        "about_nav": "About",
        "home_eyebrow": "Welcome to",
        "home_title": "PyClef",
        "home_subtitle": "AI-assisted sheet music recognition for annotations, MIDI, audio, and synchronized playback.",
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
        "process_hint": "Choose a score, select the outputs you need, and let PyClef do the rest.",
        "selected_score": "Selected score",
        "outputs_title": "Choose your outputs",
        "outputs_hint": "Start with the annotated score, then add audio, MIDI, or video when you need them.",
        "presets_title": "Quick presets",
        "presets_hint": "Pick a workflow and PyClef will configure the outputs for you.",
        "preset_review": "Review score",
        "preset_review_tip": "Detailed annotations and a scientific report. Best for checking recognition before exporting media.",
        "preset_listen": "Listen",
        "preset_listen_tip": "Annotated score, MP3, and MIDI. Best for hearing the recognized notes.",
        "preset_video": "Share video",
        "preset_video_tip": "Annotated score, audio, and synchronized video. Best for demonstrations.",
        "preset_full": "Full export",
        "preset_full_tip": "Generates every available output.",
        "advanced_options": "Advanced options",
        "hide_advanced_options": "Hide advanced options",
        "show_logs": "Show technical logs",
        "hide_logs": "Hide technical logs",
        "help_title": "What is this?",
        "help_all_title": "Generate everything",
        "help_all_body": "Creates every available result: annotated pages, MP3 audio, MIDI, synchronized video, and a scientific report.",
        "help_annotations_title": "Annotated score",
        "help_annotations_body": "Creates score images with note labels and visual markers so you can inspect what PyClef recognized.",
        "help_audio_title": "MP3 audio",
        "help_audio_body": "Creates an audio file from the recognized notes. This is useful when you only want to listen to the result.",
        "help_midi_title": "MIDI",
        "help_midi_body": "Creates a MIDI file that can be opened in music software or in the PyClef MIDI Player.",
        "help_video_title": "Video",
        "help_video_body": "Creates a synchronized video. It can take longer because PyClef renders the visual playback frame by frame.",
        "help_scientific_title": "Scientific report",
        "help_scientific_body": "Exports an HTML and JSON report with detection confidence, musical interpretation, validation checks, and reliability charts for review and regression tests.",
        "help_bpm_title": "BPM",
        "help_bpm_body": "Controls playback as quarter-note beats per minute. Higher values make the generated audio, MIDI, and video faster.",
        "help_annotation_mode_title": "Annotation view",
        "help_annotation_mode_body": "Clean mode is easier to read. Detailed mode shows more detection details for review.",
        "help_sound_title": "Sound",
        "help_sound_body": "Chooses the instrument used for MP3 and video rendering. SoundFont piano is usually the most realistic option.",
        "help_video_mode_title": "Video style",
        "help_video_mode_body": "Score video follows the annotated sheet. Piano roll creates a falling-notes visualization with a piano.",
        "help_preprocess_title": "Image cleanup",
        "help_preprocess_body": "Improves contrast and reduces small scan noise before recognition. The original page is still used for annotations and video.",
        "help_quality_gate_title": "Quality gate",
        "help_quality_gate_body": "Keeps scientific metrics and event data available so the result can be reviewed before sharing or used in regression checks.",
        "help_staff_crop_recovery_title": "Staff crop recovery",
        "help_staff_crop_recovery_body": "Experimental pass. After finding the staves, PyClef scans each system crop again to try to recover missing notes. It can help dense scores, but may also add false positives.",
        "help_diagnostics_title": "Environment check",
        "help_diagnostics_body": "Checks external tools used by PyClef, such as the recognition model, Poppler, FFmpeg, SoundFont, and FluidSynth.",
        "help_review_title": "Review and quality",
        "help_review_body": "Summarizes recognized notes, detection confidence, generated files, and validation warnings so you know what should be reviewed before sharing.",
        "diagnostics_title": "Environment check",
        "diagnostics_pending": "Run a quick check before processing.",
        "diagnostics_button": "Check system",
        "diagnostics_ok": "System ready.",
        "diagnostics_warning": "Review setup warnings.",
        "diagnostics_error": "Setup needs attention.",
        "diagnostics_blocking": "PyClef found a setup issue that can stop processing. Open Advanced options and run Check system before trying again.",
        "no_files": "No file selected.",
        "bpm": "BPM",
        "choose_files": "Choose files",
        "process": "Process",
        "generate": "Generate",
        "all": "Everything",
        "annotations": "Annotated score",
        "audio": "MP3",
        "midi": "MIDI",
        "video": "Video",
        "scientific_report": "Scientific report",
        "annotation_view": "Annotation style",
        "annotation_clean": "Clean",
        "annotation_detailed": "Detailed",
        "sound_label": "Sound",
        "sound_piano": "Piano",
        "sound_soft_piano": "Soft piano",
        "sound_bright_piano": "Bright piano",
        "sound_soundfont_piano": "SoundFont piano",
        "video_mode": "Video style",
        "video_mode_score": "Score video",
        "video_mode_piano_roll": "Piano roll",
        "preprocess": "Image cleanup",
        "quality_gate": "Quality gate",
        "staff_crop_recovery": "Staff crop recovery",
        "video_warning": "Video output can take longer because PyClef needs to render and synchronize every frame.",
        "preview_title": "Annotated preview",
        "preview_empty": "Click the preview to open the annotated page.",
        "review_title": "Review and quality",
        "review_hint": "Process a score to see confidence, detected notes, and output checks here.",
        "review_ready": "Ready",
        "review_attention": "Review suggested",
        "review_empty": "No notes detected",
        "review_events": "Detected notes",
        "review_pages": "Pages",
        "review_confidence": "Average confidence",
        "review_low_confidence": "Needs review",
        "review_hands": "Hands",
        "review_outputs": "Output check",
        "review_duration": "Duration",
        "review_recommendation": "Recommendation",
        "review_recommendation_ready": "Looks ready for listening or sharing. Open the annotations if you want a final visual check.",
        "review_recommendation_check": "Open the detailed annotations and review highlighted notes before sharing.",
        "review_prepare_detailed": "Prepare detailed review",
        "review_editor": "Review detections",
        "review_editor_title": "Review detected notes",
        "review_editor_hint": "Edit labels such as C4, F#3, or Bb2. Uncheck events that should be ignored, then save corrections or export a corrected MIDI.",
        "review_editor_save": "Save corrections",
        "review_editor_export_midi": "Export corrected MIDI",
        "review_editor_saved": "Corrections saved.",
        "review_editor_exported": "Corrected MIDI exported.",
        "review_editor_invalid": "Some labels are invalid. Use formats like C4, F#3, or Bb2.",
        "review_editor_no_events": "No event data is available. Enable Quality gate or Scientific report and process again.",
        "progress_waiting": "Waiting to process.",
        "progress_complete": "100% complete.",
        "log_placeholder": "Processing logs appear here.",
        "open_folder": "Open folder",
        "open_annotations": "Open annotations",
        "open_video": "Open video",
        "open_audio": "Open audio",
        "open_midi": "Open MIDI",
        "open_midi_player": "MIDI player",
        "open_scientific_report": "Open report",
        "scientific_report_title": "Scientific report",
        "scientific_report_hint": "Confidence and musical-distribution charts are more useful than a confusion matrix when there is no ground-truth annotation.",
        "scientific_chart_confidence": "Confidence distribution",
        "scientific_chart_hands": "Hand distribution",
        "scientific_chart_pitch": "Pitch classes",
        "scientific_chart_duration": "Duration profile",
        "scientific_timing": "Timing interpretation",
        "scientific_crop_recovery": "Staff crop recovery",
        "scientific_key_signatures": "Key-signature context",
        "scientific_validation": "Validation notes",
        "scientific_json_note": "The JSON report is still saved in the results folder for regression tests.",
        "close": "Close",
        "midi_page_eyebrow": "SoundFont playback",
        "midi_page_title": "MIDI Player",
        "midi_page_hint": "Open a generated MIDI file or use the selector inside the player. The piano SoundFont is loaded automatically.",
        "midi_page_unavailable": "The embedded MIDI player is unavailable in this installation.",
        "midi_player_unavailable_title": "MIDI player unavailable",
        "midi_player_unavailable_msg": "The embedded MIDI player is unavailable in this installation. PyClef will open the MIDI file with the system app instead.",
        "about_text": "PyClef is a hybrid Optical Music Recognition workflow that combines deep-learning detection with staff-aware musical inference.\n\nThe desktop app keeps the process direct: choose a score, select the outputs, set the BPM, and generate synchronized audio, MIDI, video, and annotated pages.",
        "about_eyebrow": "About PyClef",
        "about_title": "From score images to sound, MIDI, and reviewable results.",
        "about_body": "PyClef turns sheet music images into practical outputs for listening, inspection, and study. It focuses on a simple desktop workflow while keeping the recognition process transparent enough to review.",
        "about_card_1_title": "Staff-aware recognition",
        "about_card_1_body": "Combines neural symbol detection with staff geometry to infer pitch with musical context.",
        "about_card_2_title": "Playable exports",
        "about_card_2_body": "Generates MIDI, MP3, and synchronized video from the notes detected in the score.",
        "about_card_3_title": "Clear review",
        "about_card_3_body": "Exports clean or detailed annotations so each result can be inspected before sharing.",
        "about_stat_1": "OMR workflow",
        "about_stat_2": "MIRP inference",
        "about_stat_3": "MIDI + video",
        "author_title": "Created by Vinicius Fernandes",
        "author_body": "Developed during computer-vision research as a bridge between music notation, machine learning, and signal processing.",
        "website_button": "Visit website",
        "select_dialog": "Select scores",
        "select_filter": "Scores (*.pdf *.png *.jpg *.jpeg);;PDF (*.pdf);;Images (*.png *.jpg *.jpeg);;All files (*.*)",
        "select_score_title": "Select a score",
        "select_score_msg": "Choose a PDF or image before processing.",
        "already_processing_title": "Processing",
        "already_processing_msg": "Processing is already running.",
        "done_title": "Done",
        "done_msg": "Files generated successfully.",
        "validation_ok": "Output check passed.",
        "validation_warning": "Output check found warnings.",
        "validation_error": "Output check found errors.",
        "error_title": "Processing error",
        "error_msg": "Could not finish. Check the logs for details.",
        "missing_title": "File not found",
        "missing_msg": "This result has not been generated yet.",
    },
    "pt": {
        "sidebar_caption": "Partitura para áudio",
        "language_button": "English",
        "home_nav": "Início",
        "scores_nav": "Partituras",
        "midi_nav": "Player MIDI",
        "about_nav": "Sobre",
        "home_eyebrow": "Bem-vindo ao",
        "home_title": "PyClef",
        "home_subtitle": "Reconhecimento de partituras assistido por IA para anotações, MIDI, áudio e reprodução sincronizada.",
        "start_button": "Iniciar",
        "select_scores": "Selecionar partituras",
        "open_results": "Abrir resultados",
        "status_ready": "Pronto para selecionar uma partitura.",
        "status_selected": "{count} arquivo(s) selecionado(s).",
        "status_processing": "Processando partitura...",
        "status_done": "Processamento concluído. Resultados prontos para abrir.",
        "status_error": "O processamento encontrou um erro.",
        "step1_title": "Escolha a partitura",
        "step1_caption": "PDF, PNG, JPG ou JPEG.",
        "step2_title": "Ajuste o BPM",
        "step2_caption": "Controle o andamento antes de processar.",
        "step3_title": "Processe",
        "step3_caption": "Acompanhe os registros em tempo real.",
        "step4_title": "Abra os arquivos",
        "step4_caption": "MP3, MIDI, vídeo e anotações quando prontos.",
        "workflow_title": "Fluxo recomendado",
        "workflow_note": "Use Iniciar para abrir o ambiente de partituras. Depois, escolha arquivos, ajuste o BPM e gere as saídas que precisar.",
        "process_eyebrow": "Fluxo direto",
        "process_title": "Processamento",
        "process_hint": "Escolha uma partitura, selecione o resultado desejado e deixe o PyClef cuidar do resto.",
        "selected_score": "Partitura selecionada",
        "outputs_title": "Escolha as saídas",
        "outputs_hint": "Comece pela partitura anotada e adicione áudio, MIDI ou vídeo quando precisar.",
        "presets_title": "Presets rápidos",
        "presets_hint": "Escolha um fluxo e o PyClef configura as saídas para você.",
        "preset_review": "Revisar partitura",
        "preset_review_tip": "Anotações detalhadas e relatório científico. Ideal para conferir o reconhecimento antes de exportar mídia.",
        "preset_listen": "Ouvir",
        "preset_listen_tip": "Partitura anotada, MP3 e MIDI. Ideal para ouvir as notas reconhecidas.",
        "preset_video": "Compartilhar vídeo",
        "preset_video_tip": "Partitura anotada, áudio e vídeo sincronizado. Ideal para demonstrações.",
        "preset_full": "Exportação completa",
        "preset_full_tip": "Gera todos os resultados disponíveis.",
        "advanced_options": "Opções avançadas",
        "hide_advanced_options": "Ocultar opções avançadas",
        "show_logs": "Mostrar logs técnicos",
        "hide_logs": "Ocultar logs técnicos",
        "help_title": "O que é isto?",
        "help_all_title": "Gerar tudo",
        "help_all_body": "Cria todos os resultados disponíveis: páginas anotadas, áudio MP3, MIDI, vídeo sincronizado e relatório científico.",
        "help_annotations_title": "Partitura anotada",
        "help_annotations_body": "Cria imagens da partitura com nomes das notas e marcadores visuais para conferir o que o PyClef reconheceu.",
        "help_audio_title": "Áudio MP3",
        "help_audio_body": "Cria um arquivo de áudio a partir das notas reconhecidas. Use quando quiser apenas ouvir o resultado.",
        "help_midi_title": "MIDI",
        "help_midi_body": "Cria um arquivo MIDI para abrir em softwares musicais ou no Player MIDI do PyClef.",
        "help_video_title": "Vídeo",
        "help_video_body": "Cria um vídeo sincronizado. Pode demorar mais porque o PyClef renderiza a reprodução quadro por quadro.",
        "help_scientific_title": "Relatório científico",
        "help_scientific_body": "Exporta um relatório HTML e JSON com confiança da detecção, interpretação musical, checagens de validação e gráficos de confiabilidade para revisão e testes de regressão.",
        "help_bpm_title": "BPM",
        "help_bpm_body": "Controla o andamento como semínimas por minuto. Valores maiores deixam o áudio, MIDI e vídeo gerados mais rápidos.",
        "help_annotation_mode_title": "Estilo de anotação",
        "help_annotation_mode_body": "O modo limpo é mais fácil de ler. O modo detalhado mostra mais informações da detecção para revisão.",
        "help_sound_title": "Som",
        "help_sound_body": "Escolhe o instrumento usado no MP3 e no vídeo. Piano SoundFont costuma ser a opção mais realista.",
        "help_video_mode_title": "Estilo do vídeo",
        "help_video_mode_body": "Vídeo da partitura acompanha a folha anotada. Piano roll cria uma visualização de notas caindo com piano.",
        "help_preprocess_title": "Limpeza da imagem",
        "help_preprocess_body": "Melhora contraste e reduz pequenos ruídos da digitalização antes do reconhecimento. A página original continua sendo usada nas anotações e no vídeo.",
        "help_quality_gate_title": "Controle de qualidade",
        "help_quality_gate_body": "Mantém métricas científicas e dados dos eventos disponíveis para revisão antes de compartilhar ou usar em testes de regressão.",
        "help_staff_crop_recovery_title": "Recuperação por recorte",
        "help_staff_crop_recovery_body": "Passe experimental. Depois de encontrar as pautas, o PyClef analisa cada recorte de sistema novamente para tentar recuperar notas perdidas. Pode ajudar em partituras densas, mas também pode adicionar falsos positivos.",
        "help_diagnostics_title": "Checagem do ambiente",
        "help_diagnostics_body": "Verifica ferramentas externas usadas pelo PyClef, como modelo de reconhecimento, Poppler, FFmpeg, SoundFont e FluidSynth.",
        "help_review_title": "Revisão e qualidade",
        "help_review_body": "Resume notas reconhecidas, confiança da detecção, arquivos gerados e avisos de validação para você saber o que revisar antes de compartilhar.",
        "diagnostics_title": "Checagem do ambiente",
        "diagnostics_pending": "Execute uma checagem rápida antes de processar.",
        "diagnostics_button": "Verificar sistema",
        "diagnostics_ok": "Sistema pronto.",
        "diagnostics_warning": "Revise os avisos de configuração.",
        "diagnostics_error": "A configuração precisa de atenção.",
        "diagnostics_blocking": "O PyClef encontrou um problema de configuração que pode impedir o processamento. Abra Opções avançadas e execute Verificar sistema antes de tentar novamente.",
        "no_files": "Nenhum arquivo selecionado.",
        "bpm": "BPM",
        "choose_files": "Escolher arquivos",
        "process": "Processar",
        "generate": "Gerar",
        "all": "Tudo",
        "annotations": "Partitura anotada",
        "audio": "MP3",
        "midi": "MIDI",
        "video": "Vídeo",
        "scientific_report": "Relatório científico",
        "annotation_view": "Estilo de anotação",
        "annotation_clean": "Limpa",
        "annotation_detailed": "Detalhada",
        "sound_label": "Som",
        "sound_piano": "Piano",
        "sound_soft_piano": "Piano suave",
        "sound_bright_piano": "Piano brilhante",
        "sound_soundfont_piano": "Piano SoundFont",
        "video_mode": "Estilo do vídeo",
        "video_mode_score": "Vídeo da partitura",
        "video_mode_piano_roll": "Piano roll",
        "preprocess": "Limpeza da imagem",
        "quality_gate": "Controle de qualidade",
        "staff_crop_recovery": "Recuperação por recorte",
        "video_warning": "A saída em vídeo pode demorar mais, porque o PyClef precisa renderizar e sincronizar cada quadro.",
        "preview_title": "Prévia anotada",
        "preview_empty": "Clique na prévia para abrir a página anotada.",
        "review_title": "Revisão e qualidade",
        "review_hint": "Processe uma partitura para ver aqui confiança, notas detectadas e checagem dos arquivos.",
        "review_ready": "Pronto",
        "review_attention": "Revisão sugerida",
        "review_empty": "Nenhuma nota detectada",
        "review_events": "Notas detectadas",
        "review_pages": "Páginas",
        "review_confidence": "Confiança média",
        "review_low_confidence": "Revisar",
        "review_hands": "Mãos",
        "review_outputs": "Checagem",
        "review_duration": "Duração",
        "review_recommendation": "Recomendação",
        "review_recommendation_ready": "Parece pronto para ouvir ou compartilhar. Abra as anotações se quiser uma conferência visual final.",
        "review_recommendation_check": "Abra as anotações detalhadas e revise as notas destacadas antes de compartilhar.",
        "review_prepare_detailed": "Preparar revisão detalhada",
        "review_editor": "Revisar detecções",
        "review_editor_title": "Revisar notas detectadas",
        "review_editor_hint": "Edite rótulos como C4, F#3 ou Bb2. Desmarque eventos que devem ser ignorados e salve as correções ou exporte um MIDI corrigido.",
        "review_editor_save": "Salvar correções",
        "review_editor_export_midi": "Exportar MIDI corrigido",
        "review_editor_saved": "Correções salvas.",
        "review_editor_exported": "MIDI corrigido exportado.",
        "review_editor_invalid": "Alguns rótulos são inválidos. Use formatos como C4, F#3 ou Bb2.",
        "review_editor_no_events": "Nenhum dado de evento disponível. Ative Controle de qualidade ou Relatório científico e processe novamente.",
        "progress_waiting": "Aguardando processamento.",
        "progress_complete": "100% concluído.",
        "log_placeholder": "Os registros do processamento aparecem aqui.",
        "open_folder": "Abrir pasta",
        "open_annotations": "Abrir anotações",
        "open_video": "Abrir vídeo",
        "open_audio": "Abrir áudio",
        "open_midi": "Abrir MIDI",
        "open_midi_player": "Player MIDI",
        "open_scientific_report": "Abrir relatório",
        "scientific_report_title": "Relatório científico",
        "scientific_report_hint": "Gráficos de confiança e distribuição musical são mais úteis que matriz de confusão quando não há anotação de referência.",
        "scientific_chart_confidence": "Distribuição de confiança",
        "scientific_chart_hands": "Distribuição por mão",
        "scientific_chart_pitch": "Classes de notas",
        "scientific_chart_duration": "Perfil de duração",
        "scientific_timing": "Interpretação temporal",
        "scientific_crop_recovery": "Recuperação por recorte",
        "scientific_key_signatures": "Contexto de armadura",
        "scientific_validation": "Notas de validação",
        "scientific_json_note": "O relatório JSON continua salvo na pasta de resultados para testes de regressão.",
        "close": "Fechar",
        "midi_page_eyebrow": "Reprodução SoundFont",
        "midi_page_title": "Player MIDI",
        "midi_page_hint": "Abra um MIDI gerado ou use o seletor dentro do player. O SoundFont de piano é carregado automaticamente.",
        "midi_page_unavailable": "O player MIDI embutido não está disponível nesta instalação.",
        "midi_player_unavailable_title": "Player MIDI indisponível",
        "midi_player_unavailable_msg": "O player MIDI embutido não está disponível nesta instalação. O PyClef vai abrir o MIDI no aplicativo padrão do sistema.",
        "about_text": "O PyClef é um fluxo híbrido de Reconhecimento Óptico de Partituras que combina detecção por aprendizado profundo com inferência musical baseada na pauta.\n\nO aplicativo desktop mantém o processo direto: escolha a partitura, selecione as saídas, ajuste o BPM e gere áudio, MIDI, vídeo sincronizado e páginas anotadas.",
        "about_eyebrow": "Sobre o PyClef",
        "about_title": "De imagens de partituras para som, MIDI e resultados fáceis de revisar.",
        "about_body": "O PyClef transforma imagens de partituras em saídas práticas para audição, inspeção e estudo. A interface prioriza um fluxo simples, mas mantém o reconhecimento transparente para revisão.",
        "about_card_1_title": "Reconhecimento por pauta",
        "about_card_1_body": "Combina detecção neural de símbolos com geometria da pauta para inferir alturas com contexto musical.",
        "about_card_2_title": "Exportações tocáveis",
        "about_card_2_body": "Gera MIDI, MP3 e vídeo sincronizado a partir das notas detectadas na partitura.",
        "about_card_3_title": "Revisão clara",
        "about_card_3_body": "Exporta anotações limpas ou detalhadas para inspecionar cada resultado antes de compartilhar.",
        "about_stat_1": "Fluxo OMR",
        "about_stat_2": "Inferência MIRP",
        "about_stat_3": "MIDI + vídeo",
        "author_title": "Desenvolvido por Vinicius Fernandes",
        "author_body": "Desenvolvido durante estudos de visão computacional como uma ponte entre notação musical, machine learning e processamento de sinais.",
        "website_button": "Visitar site",
        "select_dialog": "Selecione as partituras",
        "select_filter": "Partituras (*.pdf *.png *.jpg *.jpeg);;PDF (*.pdf);;Imagens (*.png *.jpg *.jpeg);;Todos (*.*)",
        "select_score_title": "Selecione uma partitura",
        "select_score_msg": "Escolha um PDF ou imagem antes de processar.",
        "already_processing_title": "Processando",
        "already_processing_msg": "Já existe um processamento em andamento.",
        "done_title": "Concluído",
        "done_msg": "Arquivos gerados com sucesso.",
        "validation_ok": "Checagem dos arquivos aprovada.",
        "validation_warning": "Checagem dos arquivos encontrou avisos.",
        "validation_error": "Checagem dos arquivos encontrou erros.",
        "error_title": "Erro no processamento",
        "error_msg": "Não foi possível finalizar. Veja os registros para identificar o problema.",
        "missing_title": "Arquivo não encontrado",
        "missing_msg": "Esse resultado ainda não foi gerado.",
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


class InfoButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("i")
        self.setObjectName("infoButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(30, 30)
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.NoFocus)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        is_light = self.property("theme") == "light"
        if is_light:
            fill = QColor(255, 255, 255, 220)
            border = QColor(0, 140, 232, 170)
            text = QColor(0, 86, 136)
            hover_fill = QColor(22, 215, 255, 82)
        else:
            fill = QColor(10, 28, 44, 230)
            border = QColor(64, 214, 255, 220)
            text = QColor(230, 250, 255)
            hover_fill = QColor(26, 83, 108, 245)

        if self.underMouse():
            fill = hover_fill
            border.setAlpha(190)
        if self.isDown():
            fill.setAlpha(min(255, fill.alpha() + 55))

        rect = self.rect().adjusted(3, 3, -3, -3)
        painter.setPen(QPen(border, 1.4))
        painter.setBrush(fill)
        painter.drawEllipse(rect)

        font = QFont(self.font())
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(text)
        painter.drawText(rect, Qt.AlignCenter, "i")
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

            result = process_score_pipeline(
                self.file_list,
                bpm=self.bpm,
                progress_callback=emit_progress,
                output_options={**self.output_options, "language": self.language},
            )
            self.finished.emit(True, result or {})
        except Exception as exc:
            prefix = "Processing error" if self.language == "en" else "Erro durante o processamento"
            self.log.emit(f"{prefix}: {exc}")
            self.finished.emit(False, {})


class MidiPlayerWindow(QMainWindow):
    def __init__(self, midi_path=None, parent=None):
        super().__init__(parent)
        self.midi_path = Path(midi_path) if midi_path else None

        title = "PyClef MIDI Player"
        if self.midi_path:
            title = f"{title} - {self.midi_path.name}"
        self.setWindowTitle(title)
        self.setMinimumSize(1120, 720)
        self.resize(1280, 820)

        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        self._configure_web_settings()
        self.web_view.loadFinished.connect(self._inject_midi_file)

        player_url = QUrl.fromLocalFile(str(BASE_DIR / "player" / "midi_player.html"))
        if self.midi_path:
            query = QUrlQuery()
            query.addQueryItem("name", self.midi_path.name)
            player_url.setQuery(query)
        self.web_view.setUrl(player_url)

    def _configure_web_settings(self):
        configure_web_view(self.web_view)

    def _inject_midi_file(self, ok):
        if not ok or not self.midi_path or not self.midi_path.exists():
            return
        try:
            encoded = base64.b64encode(self.midi_path.read_bytes()).decode("ascii")
        except OSError:
            return

        script = (
            "if (window.pyclefLoadMidiBase64) { "
            f"window.pyclefLoadMidiBase64({json.dumps(encoded)}, {json.dumps(self.midi_path.name)}); "
            "}"
        )
        self.web_view.page().runJavaScript(script)

    def closeEvent(self, event):
        try:
            self.web_view.page().runJavaScript(
                "if (window.pyclefStopPlayback) { window.pyclefStopPlayback(); }"
            )
            self.web_view.stop()
            self.web_view.setUrl(QUrl("about:blank"))
        except RuntimeError:
            pass
        super().closeEvent(event)


class MainClef(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.selected_files = []
        self.result_files = {}
        self.last_result = {}
        self.processing_thread = None
        self.midi_player_window = None
        self._sidebar_open = True
        self.language = "en"
        self.current_theme = "dark"
        self.step_labels = []
        self.about_card_labels = []
        self.output_cards = []
        self.advanced_visible = False
        self.logs_visible = False
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
        self.theme_button = QPushButton()
        self.theme_button.setObjectName("themeButton")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.setFixedSize(132, 48)
        self.theme_button.setText(self._theme_button_text())
        self.theme_button.setToolTip("Theme")
        self.verticalLayout.insertWidget(0, self.sidebar_brand_caption)
        self.verticalLayout.insertWidget(0, self.sidebar_brand)

        self.menuButton.hide()
        self.homeButton = self._replace_nav_button(self.homeButton)
        self.aboutButton = self._replace_nav_button(self.aboutButton)
        self.sheetsButton = self._replace_nav_button(self.sheetsButton)
        self.midiButton = NeonNavButton(self.verticaloptions)
        self.midiButton.setObjectName("midiButton")
        self.midiButton.setCursor(Qt.PointingHandCursor)
        self.midiButton.setMinimumHeight(56)
        self.midiButton.setSizePolicy(self.sheetsButton.sizePolicy())
        self.verticalLayout.addWidget(self.homeButton)
        self.verticalLayout.addWidget(self.sheetsButton)
        self.verticalLayout.addWidget(self.midiButton)
        self.verticalLayout.addWidget(self.aboutButton)
        self.verticalLayout.addWidget(self.language_button, 0, Qt.AlignHCenter)
        self.verticalLayout.addWidget(self.theme_button, 0, Qt.AlignHCenter)

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

    def _make_info_button(self, title_key, body_key):
        button = InfoButton()
        button.setProperty("theme", self.current_theme)
        button.setToolTip(self.tr("help_title"))
        button.clicked.connect(lambda checked=False, tk=title_key, bk=body_key: self.show_help(tk, bk))
        return button

    def _icon(self, name):
        icon_path = BASE_DIR / "ui" / name
        return QIcon(str(icon_path)) if icon_path.exists() else QIcon()

    def _apply_button_icons(self):
        icon_size = QSize(19, 19)
        button_icons = (
            (getattr(self, "home_select_button", None), "icon_play.svg"),
            (getattr(self, "home_results_button", None), "icon_folder.svg"),
            (getattr(self, "selectsheetButton", None), "icon_file.svg"),
            (getattr(self, "choose_button", None), "icon_file.svg"),
            (getattr(self, "process_button", None), "icon_process.svg"),
            (getattr(self, "advanced_toggle_button", None), "icon_options.svg"),
            (getattr(self, "log_toggle_button", None), "icon_options.svg"),
            (getattr(self, "diagnostics_button", None), "icon_options.svg"),
            (getattr(self, "preset_review_button", None), "icon_score.svg"),
            (getattr(self, "preset_listen_button", None), "icon_audio.svg"),
            (getattr(self, "preset_video_button", None), "icon_video.svg"),
            (getattr(self, "preset_full_button", None), "icon_process.svg"),
            (getattr(self, "review_detailed_button", None), "icon_score.svg"),
            (getattr(self, "open_folder_button", None), "icon_folder.svg"),
            (getattr(self, "open_annotations_button", None), "icon_score.svg"),
            (getattr(self, "open_video_button", None), "icon_video.svg"),
            (getattr(self, "open_audio_button", None), "icon_audio.svg"),
            (getattr(self, "open_midi_button", None), "icon_midi.svg"),
            (getattr(self, "open_scientific_button", None), "icon_options.svg"),
            (getattr(self, "website_button", None), "icon_web.svg"),
        )
        for button, icon_name in button_icons:
            if button is None:
                continue
            button.setIcon(self._icon(icon_name))
            button.setIconSize(icon_size)

    def _make_output_card(self, checkbox, title_key, body_key):
        card = QFrame()
        card.setObjectName("outputCard")
        card.setCursor(Qt.PointingHandCursor)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 12, 12, 12)
        layout.setSpacing(8)
        layout.addWidget(checkbox, 1)
        layout.addWidget(self._make_info_button(title_key, body_key), 0, Qt.AlignRight)
        card.mousePressEvent = lambda event, cb=checkbox: cb.setChecked(not cb.isChecked()) if cb.isEnabled() else None
        self.output_cards.append((card, checkbox))
        return card

    def _make_preset_button(self, preset_key):
        button = QPushButton()
        button.setObjectName("presetButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setProperty("preset", preset_key)
        button.clicked.connect(lambda checked=False, key=preset_key: self._apply_output_preset(key))
        return button

    def _make_review_metric(self):
        label = QLabel()
        label.setObjectName("reviewMetricLabel")
        label.setWordWrap(True)
        value = QLabel("-")
        value.setObjectName("reviewMetricValue")
        value.setWordWrap(True)
        return label, value

    def show_help(self, title_key, body_key):
        self.show_message(self.tr(title_key), self.tr(body_key))

    def _set_advanced_visible(self, visible):
        self.advanced_visible = visible
        self.advanced_frame.setVisible(visible)
        self.advanced_toggle_button.setText(
            self.tr("hide_advanced_options") if visible else self.tr("advanced_options")
        )

    def _toggle_advanced_options(self):
        self._set_advanced_visible(not self.advanced_visible)

    def _set_logs_visible(self, visible):
        self.logs_visible = visible
        self.log_output.setVisible(visible)
        self.log_toggle_button.setText(
            self.tr("hide_logs") if visible else self.tr("show_logs")
        )

    def _toggle_logs(self):
        self._set_logs_visible(not self.logs_visible)

    def _refresh_output_cards(self):
        for card, checkbox in getattr(self, "output_cards", []):
            card.setProperty("selected", checkbox.isChecked())
            card.setProperty("disabled", not checkbox.isEnabled())
            card.style().unpolish(card)
            card.style().polish(card)

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
        layout.setContentsMargins(34, 32, 34, 32)
        layout.setSpacing(16)

        hero_frame = QFrame()
        hero_frame.setObjectName("aboutHero")
        hero_layout = QHBoxLayout(hero_frame)
        hero_layout.setContentsMargins(24, 22, 24, 22)
        hero_layout.setSpacing(24)

        hero_text_layout = QVBoxLayout()
        hero_text_layout.setSpacing(12)

        self.about_eyebrow = QLabel()
        self.about_eyebrow.setObjectName("eyebrow")

        self.about_title = QLabel()
        self.about_title.setObjectName("panelTitle")
        self.about_title.setWordWrap(True)

        self.about_body = QLabel()
        self.about_body.setObjectName("panelSubtitle")
        self.about_body.setWordWrap(True)
        self.about_body.setMinimumWidth(420)

        hero_text_layout.addWidget(self.about_eyebrow)
        hero_text_layout.addWidget(self.about_title)
        hero_text_layout.addWidget(self.about_body)
        hero_text_layout.addStretch(1)

        about_logo_card = QFrame()
        about_logo_card.setObjectName("aboutLogoCard")
        about_logo_layout = QVBoxLayout(about_logo_card)
        about_logo_layout.setContentsMargins(20, 18, 20, 18)
        about_logo_layout.setSpacing(12)

        self.about_logo = QLabel()
        self.about_logo.setObjectName("aboutLogo")
        self.about_logo.setAlignment(Qt.AlignCenter)
        logo = QPixmap(str(BASE_DIR / "ui" / "logo_black.png"))
        self.about_logo.setPixmap(logo.scaled(QSize(260, 178), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.about_logo.setMinimumHeight(176)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        self.about_stat_labels = []
        for key in ("about_stat_1", "about_stat_2", "about_stat_3"):
            stat = QLabel()
            stat.setObjectName("aboutStatChip")
            stat.setAlignment(Qt.AlignCenter)
            stat.setWordWrap(True)
            stat.setMinimumHeight(44)
            self.about_stat_labels.append((stat, key))
            stats_row.addWidget(stat)

        about_logo_layout.addWidget(self.about_logo)
        about_logo_layout.addLayout(stats_row)

        hero_layout.addLayout(hero_text_layout, 2)
        hero_layout.addWidget(about_logo_card, 1)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)
        cards_row.addWidget(self._make_about_card("about_card_1_title", "about_card_1_body"))
        cards_row.addWidget(self._make_about_card("about_card_2_title", "about_card_2_body"))
        cards_row.addWidget(self._make_about_card("about_card_3_title", "about_card_3_body"))

        author_frame = QFrame()
        author_frame.setObjectName("authorFrame")
        author_layout = QHBoxLayout(author_frame)
        author_layout.setContentsMargins(22, 18, 22, 18)
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

        layout.addWidget(hero_frame)
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
        self.processing_scroll = QScrollArea(self.page)
        self.processing_scroll.setObjectName("processingScroll")
        self.processing_scroll.setWidgetResizable(True)
        self.processing_scroll.setFrameShape(QFrame.NoFrame)
        self.processing_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.processing_panel = QFrame()
        self.processing_panel.setObjectName("processingPanel")
        self.processing_scroll.setWidget(self.processing_panel)

        layout = QVBoxLayout(self.processing_panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        self.process_eyebrow = QLabel()
        self.process_eyebrow.setObjectName("eyebrow")

        self.process_title = QLabel()
        self.process_title.setObjectName("panelTitle")

        self.process_hint = QLabel()
        self.process_hint.setObjectName("panelSubtitle")
        self.process_hint.setWordWrap(True)

        self.files_section = QFrame()
        self.files_section.setObjectName("selectedFileFrame")
        files_section_layout = QVBoxLayout(self.files_section)
        files_section_layout.setContentsMargins(16, 12, 16, 12)
        files_section_layout.setSpacing(6)

        self.selected_score_label = QLabel()
        self.selected_score_label.setObjectName("sectionTitle")

        self.files_label = QLabel()
        self.files_label.setObjectName("filesLabel")
        self.files_label.setWordWrap(True)
        files_section_layout.addWidget(self.selected_score_label)
        files_section_layout.addWidget(self.files_label)

        self.diagnostics_frame = QFrame()
        self.diagnostics_frame.setObjectName("diagnosticsFrame")
        diagnostics_layout = QGridLayout(self.diagnostics_frame)
        diagnostics_layout.setContentsMargins(16, 12, 16, 12)
        diagnostics_layout.setHorizontalSpacing(12)
        diagnostics_layout.setVerticalSpacing(6)

        self.diagnostics_title = QLabel()
        self.diagnostics_title.setObjectName("diagnosticsTitle")
        self.diagnostics_summary = QLabel()
        self.diagnostics_summary.setObjectName("diagnosticsSummary")
        self.diagnostics_summary.setWordWrap(True)
        self.diagnostics_details = QLabel()
        self.diagnostics_details.setObjectName("diagnosticsDetails")
        self.diagnostics_details.setWordWrap(True)
        self.diagnostics_info_button = self._make_info_button("help_diagnostics_title", "help_diagnostics_body")
        self.diagnostics_button = QPushButton()
        self.diagnostics_button.setObjectName("smallButton")
        self.diagnostics_button.setCursor(Qt.PointingHandCursor)

        diagnostics_layout.addWidget(self.diagnostics_title, 0, 0)
        diagnostics_layout.addWidget(self.diagnostics_info_button, 0, 1, Qt.AlignLeft)
        diagnostics_layout.addWidget(self.diagnostics_button, 0, 2, Qt.AlignRight)
        diagnostics_layout.addWidget(self.diagnostics_summary, 1, 0, 1, 3)
        diagnostics_layout.addWidget(self.diagnostics_details, 2, 0, 1, 3)
        diagnostics_layout.setColumnStretch(0, 1)

        self.options_layout = QGridLayout()
        self.options_layout.setHorizontalSpacing(12)
        self.options_layout.setVerticalSpacing(10)

        self.bpm_label = QLabel()
        self.bpm_label.setObjectName("fieldLabel")
        self.bpm_info_button = self._make_info_button("help_bpm_title", "help_bpm_body")

        self.bpm_input = QSpinBox()
        self.bpm_input.setRange(30, 300)
        self.bpm_input.setValue(72)
        self.bpm_input.setSingleStep(1)
        self.bpm_input.setObjectName("bpmInput")
        self.bpm_input.setMinimumWidth(128)

        self.choose_button = QPushButton()
        self.choose_button.setObjectName("secondaryButton")
        self.choose_button.setCursor(Qt.PointingHandCursor)

        self.process_button = QPushButton()
        self.process_button.setObjectName("primaryButton")
        self.process_button.setCursor(Qt.PointingHandCursor)
        self.process_button.setEnabled(False)

        self.preset_frame = QFrame()
        self.preset_frame.setObjectName("presetFrame")
        preset_frame_layout = QVBoxLayout(self.preset_frame)
        preset_frame_layout.setContentsMargins(16, 14, 16, 16)
        preset_frame_layout.setSpacing(10)

        preset_header = QVBoxLayout()
        preset_header.setContentsMargins(0, 0, 0, 0)
        preset_header.setSpacing(4)
        self.presets_title = QLabel()
        self.presets_title.setObjectName("sectionTitle")
        self.presets_hint = QLabel()
        self.presets_hint.setObjectName("sectionHint")
        self.presets_hint.setWordWrap(True)
        preset_header.addWidget(self.presets_title)
        preset_header.addWidget(self.presets_hint)

        self.preset_buttons_layout = QGridLayout()
        self.preset_buttons_layout.setHorizontalSpacing(12)
        self.preset_buttons_layout.setVerticalSpacing(10)
        self.preset_review_button = self._make_preset_button("review")
        self.preset_listen_button = self._make_preset_button("listen")
        self.preset_video_button = self._make_preset_button("video")
        self.preset_full_button = self._make_preset_button("full")
        preset_frame_layout.addLayout(preset_header)
        preset_frame_layout.addLayout(self.preset_buttons_layout)

        self.output_frame = QFrame()
        self.output_frame.setObjectName("outputFrame")
        self.output_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        output_frame_layout = QVBoxLayout(self.output_frame)
        output_frame_layout.setContentsMargins(16, 14, 16, 16)
        output_frame_layout.setSpacing(10)

        output_header = QVBoxLayout()
        output_header.setContentsMargins(0, 0, 0, 0)
        output_header.setSpacing(4)

        self.output_title = QLabel()
        self.output_title.setObjectName("sectionTitle")
        self.output_hint = QLabel()
        self.output_hint.setObjectName("sectionHint")
        self.output_hint.setWordWrap(True)

        output_header.addWidget(self.output_title)
        output_header.addWidget(self.output_hint)

        self.output_options_layout = QGridLayout()
        self.output_options_layout.setContentsMargins(16, 12, 16, 12)
        self.output_options_layout.setHorizontalSpacing(14)
        self.output_options_layout.setVerticalSpacing(10)
        output_frame_layout.addLayout(output_header)
        output_frame_layout.addLayout(self.output_options_layout)

        self.output_label = QLabel()
        self.output_label.setObjectName("fieldLabel")
        self.output_all = QCheckBox()
        self.output_annotations = QCheckBox()
        self.output_annotations.setChecked(True)
        self.output_audio = QCheckBox()
        self.output_midi = QCheckBox()
        self.output_video = QCheckBox()
        self.output_scientific = QCheckBox()
        self.output_all_card = self._make_output_card(self.output_all, "help_all_title", "help_all_body")
        self.output_annotations_card = self._make_output_card(self.output_annotations, "help_annotations_title", "help_annotations_body")
        self.output_audio_card = self._make_output_card(self.output_audio, "help_audio_title", "help_audio_body")
        self.output_midi_card = self._make_output_card(self.output_midi, "help_midi_title", "help_midi_body")
        self.output_video_card = self._make_output_card(self.output_video, "help_video_title", "help_video_body")
        self.output_scientific_card = self._make_output_card(self.output_scientific, "help_scientific_title", "help_scientific_body")
        self.annotation_mode_label = QLabel()
        self.annotation_mode_label.setObjectName("fieldLabel")
        self.annotation_mode_info_button = self._make_info_button("help_annotation_mode_title", "help_annotation_mode_body")
        self.annotation_mode_combo = QComboBox()
        self.annotation_mode_combo.setObjectName("modeCombo")
        self.annotation_mode_combo.setCursor(Qt.PointingHandCursor)
        self.sound_label = QLabel()
        self.sound_label.setObjectName("fieldLabel")
        self.sound_info_button = self._make_info_button("help_sound_title", "help_sound_body")
        self.sound_combo = QComboBox()
        self.sound_combo.setObjectName("modeCombo")
        self.sound_combo.setCursor(Qt.PointingHandCursor)
        self.video_mode_label = QLabel()
        self.video_mode_label.setObjectName("fieldLabel")
        self.video_mode_info_button = self._make_info_button("help_video_mode_title", "help_video_mode_body")
        self.video_mode_combo = QComboBox()
        self.video_mode_combo.setObjectName("modeCombo")
        self.video_mode_combo.setCursor(Qt.PointingHandCursor)
        self.preprocess_checkbox = QCheckBox()
        self.preprocess_checkbox.setChecked(True)
        self.preprocess_checkbox.setCursor(Qt.PointingHandCursor)
        self.preprocess_info_button = self._make_info_button("help_preprocess_title", "help_preprocess_body")
        self.quality_gate_checkbox = QCheckBox()
        self.quality_gate_checkbox.setChecked(True)
        self.quality_gate_checkbox.setCursor(Qt.PointingHandCursor)
        self.quality_gate_info_button = self._make_info_button("help_quality_gate_title", "help_quality_gate_body")
        self.staff_crop_recovery_checkbox = QCheckBox()
        self.staff_crop_recovery_checkbox.setChecked(False)
        self.staff_crop_recovery_checkbox.setCursor(Qt.PointingHandCursor)
        self.staff_crop_recovery_info_button = self._make_info_button(
            "help_staff_crop_recovery_title",
            "help_staff_crop_recovery_body",
        )
        for checkbox in (
            self.output_all,
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
            self.output_scientific,
        ):
            checkbox.setCursor(Qt.PointingHandCursor)

        self.video_warning_label = QLabel()
        self.video_warning_label.setObjectName("warningPill")
        self.video_warning_label.setWordWrap(True)

        self.advanced_toggle_button = QPushButton()
        self.advanced_toggle_button.setObjectName("secondaryButton")
        self.advanced_toggle_button.setCursor(Qt.PointingHandCursor)

        self.advanced_frame = QFrame()
        self.advanced_frame.setObjectName("advancedFrame")
        self.advanced_frame.setVisible(False)
        self.advanced_options_layout = QGridLayout(self.advanced_frame)
        self.advanced_options_layout.setContentsMargins(16, 14, 16, 16)
        self.advanced_options_layout.setHorizontalSpacing(12)
        self.advanced_options_layout.setVerticalSpacing(10)

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
        self.log_output.setMinimumHeight(150)
        self.log_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.log_output.setVisible(False)

        self.log_toggle_button = QPushButton()
        self.log_toggle_button.setObjectName("smallButton")
        self.log_toggle_button.setCursor(Qt.PointingHandCursor)

        self.review_frame = QFrame()
        self.review_frame.setObjectName("reviewFrame")
        self.review_frame.setVisible(False)
        review_layout = QGridLayout(self.review_frame)
        review_layout.setContentsMargins(16, 14, 16, 16)
        review_layout.setHorizontalSpacing(14)
        review_layout.setVerticalSpacing(10)

        self.review_title = QLabel()
        self.review_title.setObjectName("sectionTitle")
        self.review_info_button = self._make_info_button("help_review_title", "help_review_body")
        self.review_status_label = QLabel()
        self.review_status_label.setObjectName("reviewStatus")
        self.review_status_label.setAlignment(Qt.AlignCenter)
        self.review_detailed_button = QPushButton()
        self.review_detailed_button.setObjectName("smallButton")
        self.review_detailed_button.setCursor(Qt.PointingHandCursor)
        self.review_editor_button = QPushButton()
        self.review_editor_button.setObjectName("smallButton")
        self.review_editor_button.setCursor(Qt.PointingHandCursor)
        self.review_editor_button.setEnabled(False)

        self.review_hint_label = QLabel()
        self.review_hint_label.setObjectName("sectionHint")
        self.review_hint_label.setWordWrap(True)

        review_layout.addWidget(self.review_title, 0, 0)
        review_layout.addWidget(self.review_info_button, 0, 1, Qt.AlignLeft)
        review_layout.addWidget(self.review_status_label, 0, 2)
        review_layout.addWidget(self.review_detailed_button, 0, 3, Qt.AlignRight)
        review_layout.addWidget(self.review_editor_button, 0, 4, Qt.AlignRight)
        review_layout.addWidget(self.review_hint_label, 1, 0, 1, 5)

        self.review_metric_values = {}
        metric_keys = (
            ("review_events", "events"),
            ("review_pages", "pages"),
            ("review_confidence", "confidence"),
            ("review_low_confidence", "low_confidence"),
            ("review_hands", "hands"),
            ("review_duration", "duration"),
            ("review_outputs", "outputs"),
            ("review_recommendation", "recommendation"),
        )
        for index, (label_key, value_key) in enumerate(metric_keys):
            label, value = self._make_review_metric()
            row = 2 + index // 2
            column = (index % 2) * 2
            review_layout.addWidget(label, row, column)
            review_layout.addWidget(value, row, column + 1)
            self.review_metric_values[value_key] = (label, label_key, value)
        review_layout.setColumnStretch(1, 1)
        review_layout.setColumnStretch(3, 1)
        review_layout.setColumnStretch(4, 1)

        self.annotation_preview_frame = QFrame()
        self.annotation_preview_frame.setObjectName("previewFrame")
        self.annotation_preview_frame.setVisible(False)
        self.annotation_preview_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.preview_layout = QHBoxLayout(self.annotation_preview_frame)
        self.preview_layout.setContentsMargins(14, 12, 14, 12)
        self.preview_layout.setSpacing(14)

        self.annotation_preview_image = QLabel()
        self.annotation_preview_image.setObjectName("annotationPreview")
        self.annotation_preview_image.setAlignment(Qt.AlignCenter)
        self.annotation_preview_image.setMinimumSize(220, 120)
        self.annotation_preview_image.setMaximumHeight(180)
        self.annotation_preview_image.setCursor(Qt.PointingHandCursor)

        preview_text_layout = QVBoxLayout()
        preview_text_layout.setSpacing(6)
        self.annotation_preview_title = QLabel()
        self.annotation_preview_title.setObjectName("previewTitle")
        self.annotation_preview_hint = QLabel()
        self.annotation_preview_hint.setObjectName("previewHint")
        self.annotation_preview_hint.setWordWrap(True)
        preview_text_layout.addWidget(self.annotation_preview_title)
        preview_text_layout.addWidget(self.annotation_preview_hint)
        preview_text_layout.addStretch(1)

        self.preview_layout.addWidget(self.annotation_preview_image, 0)
        self.preview_layout.addLayout(preview_text_layout, 1)

        self.results_layout = QGridLayout()
        self.results_layout.setHorizontalSpacing(10)
        self.results_layout.setVerticalSpacing(10)

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

        self.open_scientific_button = QPushButton()
        self.open_scientific_button.setObjectName("secondaryButton")
        self.open_scientific_button.setCursor(Qt.PointingHandCursor)
        self.open_scientific_button.setEnabled(False)

        for button in (
            self.choose_button,
            self.process_button,
            self.open_folder_button,
            self.open_annotations_button,
            self.open_video_button,
            self.open_audio_button,
            self.open_midi_button,
            self.open_scientific_button,
        ):
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(self.process_eyebrow)
        layout.addWidget(self.process_title)
        layout.addWidget(self.process_hint)
        layout.addWidget(self.files_section)
        layout.addLayout(self.options_layout)
        layout.addWidget(self.preset_frame)
        layout.addWidget(self.output_frame)
        layout.addWidget(self.video_warning_label)
        layout.addWidget(self.advanced_toggle_button)
        layout.addWidget(self.advanced_frame)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_status_label)
        layout.addWidget(self.log_toggle_button, 0, Qt.AlignLeft)
        layout.addWidget(self.log_output)
        layout.addWidget(self.review_frame)
        layout.addWidget(self.annotation_preview_frame)
        layout.addLayout(self.results_layout)

        self.gridLayout_10.addWidget(self.processing_scroll, 1, 0, 1, 1)
        self._update_responsive_layout()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_responsive_layout)

    def _clear_grid_layout(self, layout, columns=8):
        while layout.count():
            layout.takeAt(0)
        for column in range(columns):
            layout.setColumnStretch(column, 0)

    def _responsive_mode(self):
        if not hasattr(self, "processing_scroll"):
            return "wide"
        width = self.processing_scroll.viewport().width()
        if width < 160:
            width = max(
                self.page.width(),
                self.stackedWidget.width() - 40,
                self.width() - self.Sidebar.width() - 80,
            )
        if width < 700:
            return "narrow"
        if width < 1080:
            return "medium"
        return "wide"

    def _add_grid_widgets(self, layout, widgets, columns):
        for index, widget in enumerate(widgets):
            row = index // columns
            column = index % columns
            layout.addWidget(widget, row, column)
        for column in range(columns):
            layout.setColumnStretch(column, 1)

    def _update_responsive_layout(self):
        if not hasattr(self, "options_layout"):
            return

        mode = self._responsive_mode()
        if getattr(self, "_processing_layout_mode", None) == mode:
            return
        self._processing_layout_mode = mode

        self._clear_grid_layout(self.options_layout, 6)
        self._clear_grid_layout(self.preset_buttons_layout, 4)
        self._clear_grid_layout(self.output_options_layout, 8)
        self._clear_grid_layout(self.advanced_options_layout, 8)
        self._clear_grid_layout(self.results_layout, 6)
        output_cards = (
            self.output_annotations_card,
            self.output_audio_card,
            self.output_midi_card,
            self.output_video_card,
            self.output_scientific_card,
            self.output_all_card,
        )

        if mode == "wide":
            self.options_layout.addWidget(self.bpm_label, 0, 0)
            self.options_layout.addWidget(self.bpm_info_button, 0, 1)
            self.options_layout.addWidget(self.bpm_input, 0, 2)
            self.options_layout.setColumnStretch(3, 1)
            self.options_layout.addWidget(self.choose_button, 0, 4)
            self.options_layout.addWidget(self.process_button, 0, 5)

            self._add_grid_widgets(
                self.preset_buttons_layout,
                (
                    self.preset_review_button,
                    self.preset_listen_button,
                    self.preset_video_button,
                    self.preset_full_button,
                ),
                4,
            )
            self._add_grid_widgets(self.output_options_layout, output_cards, 3)

            self.advanced_options_layout.addWidget(self.annotation_mode_label, 0, 0)
            self.advanced_options_layout.addWidget(self.annotation_mode_info_button, 0, 1)
            self.advanced_options_layout.addWidget(self.annotation_mode_combo, 0, 2)
            self.advanced_options_layout.addWidget(self.sound_label, 0, 3)
            self.advanced_options_layout.addWidget(self.sound_info_button, 0, 4)
            self.advanced_options_layout.addWidget(self.sound_combo, 0, 5)
            self.advanced_options_layout.addWidget(self.video_mode_label, 1, 0)
            self.advanced_options_layout.addWidget(self.video_mode_info_button, 1, 1)
            self.advanced_options_layout.addWidget(self.video_mode_combo, 1, 2)
            self.advanced_options_layout.addWidget(self.preprocess_checkbox, 1, 3)
            self.advanced_options_layout.addWidget(self.preprocess_info_button, 1, 4)
            self.advanced_options_layout.addWidget(self.quality_gate_checkbox, 1, 5)
            self.advanced_options_layout.addWidget(self.quality_gate_info_button, 1, 6)
            self.advanced_options_layout.addWidget(self.staff_crop_recovery_checkbox, 2, 0)
            self.advanced_options_layout.addWidget(self.staff_crop_recovery_info_button, 2, 1)
            self.advanced_options_layout.addWidget(self.diagnostics_frame, 3, 0, 1, 7)
            self.advanced_options_layout.setColumnStretch(2, 1)
            self.advanced_options_layout.setColumnStretch(5, 1)

            self._add_grid_widgets(
                self.results_layout,
                (
                    self.open_folder_button,
                    self.open_annotations_button,
                    self.open_video_button,
                    self.open_audio_button,
                    self.open_midi_button,
                    self.open_scientific_button,
                ),
                3,
            )
            return

        self.options_layout.addWidget(self.bpm_label, 0, 0)
        self.options_layout.addWidget(self.bpm_info_button, 0, 1)
        self.options_layout.addWidget(self.bpm_input, 0, 2)
        self.options_layout.setColumnStretch(3, 1)

        if mode == "medium":
            self.options_layout.addWidget(self.choose_button, 1, 0, 1, 2)
            self.options_layout.addWidget(self.process_button, 1, 2, 1, 2)

            self._add_grid_widgets(
                self.preset_buttons_layout,
                (
                    self.preset_review_button,
                    self.preset_listen_button,
                    self.preset_video_button,
                    self.preset_full_button,
                ),
                2,
            )
            self._add_grid_widgets(self.output_options_layout, output_cards, 2)

            self.advanced_options_layout.addWidget(self.annotation_mode_label, 0, 0)
            self.advanced_options_layout.addWidget(self.annotation_mode_info_button, 0, 1)
            self.advanced_options_layout.addWidget(self.annotation_mode_combo, 0, 2)
            self.advanced_options_layout.addWidget(self.sound_label, 1, 0)
            self.advanced_options_layout.addWidget(self.sound_info_button, 1, 1)
            self.advanced_options_layout.addWidget(self.sound_combo, 1, 2)
            self.advanced_options_layout.addWidget(self.video_mode_label, 2, 0)
            self.advanced_options_layout.addWidget(self.video_mode_info_button, 2, 1)
            self.advanced_options_layout.addWidget(self.video_mode_combo, 2, 2)
            self.advanced_options_layout.addWidget(self.preprocess_checkbox, 3, 0)
            self.advanced_options_layout.addWidget(self.preprocess_info_button, 3, 1)
            self.advanced_options_layout.addWidget(self.quality_gate_checkbox, 4, 0)
            self.advanced_options_layout.addWidget(self.quality_gate_info_button, 4, 1)
            self.advanced_options_layout.addWidget(self.staff_crop_recovery_checkbox, 5, 0)
            self.advanced_options_layout.addWidget(self.staff_crop_recovery_info_button, 5, 1)
            self.advanced_options_layout.addWidget(self.diagnostics_frame, 6, 0, 1, 3)
            self.advanced_options_layout.setColumnStretch(2, 1)

            self._add_grid_widgets(
                self.results_layout,
                (
                    self.open_folder_button,
                    self.open_annotations_button,
                    self.open_video_button,
                    self.open_audio_button,
                    self.open_midi_button,
                    self.open_scientific_button,
                ),
                3,
            )
            return

        self.options_layout.addWidget(self.choose_button, 1, 0, 1, 4)
        self.options_layout.addWidget(self.process_button, 2, 0, 1, 4)

        self._add_grid_widgets(
            self.preset_buttons_layout,
            (
                self.preset_review_button,
                self.preset_listen_button,
                self.preset_video_button,
                self.preset_full_button,
            ),
            1,
        )
        self._add_grid_widgets(self.output_options_layout, output_cards, 1)

        self.advanced_options_layout.addWidget(self.annotation_mode_label, 0, 0)
        self.advanced_options_layout.addWidget(self.annotation_mode_info_button, 0, 1)
        self.advanced_options_layout.addWidget(self.annotation_mode_combo, 1, 0, 1, 2)
        self.advanced_options_layout.addWidget(self.sound_label, 2, 0)
        self.advanced_options_layout.addWidget(self.sound_info_button, 2, 1)
        self.advanced_options_layout.addWidget(self.sound_combo, 3, 0, 1, 2)
        self.advanced_options_layout.addWidget(self.video_mode_label, 4, 0)
        self.advanced_options_layout.addWidget(self.video_mode_info_button, 4, 1)
        self.advanced_options_layout.addWidget(self.video_mode_combo, 5, 0, 1, 2)
        self.advanced_options_layout.addWidget(self.preprocess_checkbox, 6, 0)
        self.advanced_options_layout.addWidget(self.preprocess_info_button, 6, 1)
        self.advanced_options_layout.addWidget(self.quality_gate_checkbox, 7, 0)
        self.advanced_options_layout.addWidget(self.quality_gate_info_button, 7, 1)
        self.advanced_options_layout.addWidget(self.staff_crop_recovery_checkbox, 8, 0)
        self.advanced_options_layout.addWidget(self.staff_crop_recovery_info_button, 8, 1)
        self.advanced_options_layout.addWidget(self.diagnostics_frame, 9, 0, 1, 2)
        self.advanced_options_layout.setColumnStretch(0, 1)
        self.advanced_options_layout.setColumnStretch(1, 0)

        self._add_grid_widgets(
            self.results_layout,
            (
                self.open_folder_button,
                self.open_annotations_button,
                self.open_video_button,
                self.open_audio_button,
                self.open_midi_button,
                self.open_scientific_button,
            ),
            1,
        )

    def _connect_actions(self):
        self.menuButton.setEnabled(False)
        self.language_button.clicked.connect(self.toggle_language)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.homeButton.clicked.connect(lambda: self._set_active_page(self.Home, self.homeButton))
        self.aboutButton.clicked.connect(lambda: self._set_active_page(self.about, self.aboutButton))
        self.sheetsButton.clicked.connect(lambda: self._set_active_page(self.page, self.sheetsButton))
        self.midiButton.clicked.connect(self.open_midi_page)

        self.home_select_button.clicked.connect(self.open_scores_page)
        self.selectsheetButton.clicked.connect(self.open_file_dialog)
        self.choose_button.clicked.connect(self.open_file_dialog)
        self.process_button.clicked.connect(self.start_processing)
        self.diagnostics_button.clicked.connect(self._refresh_environment_diagnostics)
        self.advanced_toggle_button.clicked.connect(self._toggle_advanced_options)
        self.log_toggle_button.clicked.connect(self._toggle_logs)
        self.review_detailed_button.clicked.connect(self._prepare_detailed_review)
        self.review_editor_button.clicked.connect(self.open_review_editor)
        self.output_all.toggled.connect(self._sync_output_controls)
        self.output_all.toggled.connect(lambda checked: self._update_video_warning())
        self.output_all.toggled.connect(lambda checked: self._update_annotation_mode_enabled())
        self.output_all.toggled.connect(lambda checked: self._refresh_output_cards())
        for checkbox in (
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
            self.output_scientific,
        ):
            checkbox.toggled.connect(self._ensure_output_selection)
            checkbox.toggled.connect(lambda checked: self._refresh_output_cards())
        self.output_annotations.toggled.connect(lambda checked: self._update_annotation_mode_enabled())
        self.output_video.toggled.connect(lambda checked: self._update_video_warning())
        self.annotation_mode_combo.currentIndexChanged.connect(lambda index: self._refresh_preset_buttons())
        self.sound_combo.currentIndexChanged.connect(lambda index: self._refresh_preset_buttons())
        self.video_mode_combo.currentIndexChanged.connect(lambda index: self._refresh_preset_buttons())
        self.quality_gate_checkbox.toggled.connect(self._sync_quality_gate_options)

        self.home_results_button.clicked.connect(self.open_results_folder)
        self.open_folder_button.clicked.connect(self.open_results_folder)
        self.open_annotations_button.clicked.connect(lambda: self.open_result("annotations"))
        self.open_video_button.clicked.connect(lambda: self.open_result("video"))
        self.open_audio_button.clicked.connect(lambda: self.open_result("audio"))
        self.open_midi_button.clicked.connect(self.open_midi_player)
        self.open_scientific_button.clicked.connect(self.open_scientific_report)
        self.annotation_preview_image.mousePressEvent = lambda event: self.open_result("annotations")
        self.website.mousePressEvent = lambda event: self.open_website()
        self._sync_output_controls(False)
        self._update_video_warning()
        self._update_annotation_mode_enabled()
        self._refresh_output_cards()
        self._sync_quality_gate_options(self.quality_gate_checkbox.isChecked())

    def open_scores_page(self):
        self._set_active_page(self.page, self.sheetsButton)

    def open_midi_page(self):
        self._open_midi_player_window(self._result_path("midi"))

    def _sync_output_controls(self, checked):
        for checkbox in (
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
            self.output_scientific,
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
                self.output_scientific,
            )
        ):
            self.output_annotations.setChecked(True)
        self._update_video_warning()
        self._update_annotation_mode_enabled()
        self._refresh_output_cards()
        self._refresh_preset_buttons()

    def _sync_quality_gate_options(self, checked):
        if not hasattr(self, "output_scientific"):
            return
        if checked and not self.output_all.isChecked():
            self.output_scientific.setChecked(True)
        self._refresh_output_cards()

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
                self.output_scientific,
            )
        ):
            self.output_annotations.setChecked(True)
        self._update_video_warning()
        self._update_annotation_mode_enabled()
        self._refresh_preset_buttons()

    def _set_combo_data(self, combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _apply_output_preset(self, preset_key):
        checkboxes = (
            self.output_all,
            self.output_annotations,
            self.output_audio,
            self.output_midi,
            self.output_video,
            self.output_scientific,
        )
        for checkbox in checkboxes:
            checkbox.blockSignals(True)

        self.output_all.setChecked(False)
        self.output_annotations.setChecked(False)
        self.output_audio.setChecked(False)
        self.output_midi.setChecked(False)
        self.output_video.setChecked(False)
        self.output_scientific.setChecked(False)

        if preset_key == "review":
            self.output_annotations.setChecked(True)
            self.output_scientific.setChecked(True)
            self._set_combo_data(self.annotation_mode_combo, "detailed")
            self._set_combo_data(self.video_mode_combo, "score")
        elif preset_key == "listen":
            self.output_annotations.setChecked(True)
            self.output_audio.setChecked(True)
            self.output_midi.setChecked(True)
            self._set_combo_data(self.annotation_mode_combo, "clean")
            self._set_combo_data(self.sound_combo, "soundfont_piano")
        elif preset_key == "video":
            self.output_annotations.setChecked(True)
            self.output_audio.setChecked(True)
            self.output_video.setChecked(True)
            self._set_combo_data(self.annotation_mode_combo, "clean")
            self._set_combo_data(self.video_mode_combo, "piano_roll")
            self._set_combo_data(self.sound_combo, "soundfont_piano")
        elif preset_key == "full":
            self.output_all.setChecked(True)
            self._set_combo_data(self.annotation_mode_combo, "clean")
            self._set_combo_data(self.sound_combo, "soundfont_piano")

        for checkbox in checkboxes:
            checkbox.blockSignals(False)

        self._sync_output_controls(self.output_all.isChecked())

    def _current_preset_key(self):
        if self.output_all.isChecked():
            return "full"
        annotations = self.output_annotations.isChecked()
        audio = self.output_audio.isChecked()
        midi = self.output_midi.isChecked()
        video = self.output_video.isChecked()
        scientific = self.output_scientific.isChecked()
        if annotations and scientific and not audio and not midi and not video and self._current_annotation_mode() == "detailed":
            return "review"
        if annotations and audio and midi and not video:
            return "listen"
        if annotations and audio and video and not midi:
            return "video"
        return None

    def _refresh_preset_buttons(self):
        if not hasattr(self, "preset_review_button"):
            return
        active = self._current_preset_key()
        for button in (
            self.preset_review_button,
            self.preset_listen_button,
            self.preset_video_button,
            self.preset_full_button,
        ):
            button.setProperty("active", button.property("preset") == active)
            button.style().unpolish(button)
            button.style().polish(button)

    def _video_output_selected(self):
        return self.output_all.isChecked() or self.output_video.isChecked()

    def _annotation_output_selected(self):
        return self.output_all.isChecked() or self.output_annotations.isChecked()

    def _update_video_warning(self):
        if not hasattr(self, "video_warning_label"):
            return
        self.video_warning_label.setText(self.tr("video_warning"))
        self.video_warning_label.setVisible(self._video_output_selected())
        self._update_video_mode_enabled()

    def _current_annotation_mode(self):
        if not hasattr(self, "annotation_mode_combo"):
            return "clean"
        mode = self.annotation_mode_combo.currentData()
        return mode if mode in ("clean", "detailed") else "clean"

    def _refresh_annotation_mode_options(self):
        if not hasattr(self, "annotation_mode_combo"):
            return
        current_mode = self._current_annotation_mode()
        self.annotation_mode_combo.blockSignals(True)
        self.annotation_mode_combo.clear()
        self.annotation_mode_combo.addItem(self.tr("annotation_clean"), "clean")
        self.annotation_mode_combo.addItem(self.tr("annotation_detailed"), "detailed")
        index = self.annotation_mode_combo.findData(current_mode)
        self.annotation_mode_combo.setCurrentIndex(max(0, index))
        self.annotation_mode_combo.blockSignals(False)

    def _current_timbre(self):
        if not hasattr(self, "sound_combo"):
            return "piano"
        timbre = self.sound_combo.currentData()
        return timbre if timbre in ("piano", "soft_piano", "bright_piano", "soundfont_piano") else "piano"

    def _refresh_timbre_options(self):
        if not hasattr(self, "sound_combo"):
            return
        current_timbre = self._current_timbre()
        self.sound_combo.blockSignals(True)
        self.sound_combo.clear()
        self.sound_combo.addItem(self.tr("sound_piano"), "piano")
        self.sound_combo.addItem(self.tr("sound_soundfont_piano"), "soundfont_piano")
        self.sound_combo.addItem(self.tr("sound_soft_piano"), "soft_piano")
        self.sound_combo.addItem(self.tr("sound_bright_piano"), "bright_piano")
        index = self.sound_combo.findData(current_timbre)
        self.sound_combo.setCurrentIndex(max(0, index))
        self.sound_combo.blockSignals(False)

    def _current_video_mode(self):
        if not hasattr(self, "video_mode_combo"):
            return "score"
        mode = self.video_mode_combo.currentData()
        return mode if mode in ("score", "piano_roll") else "score"

    def _refresh_video_mode_options(self):
        if not hasattr(self, "video_mode_combo"):
            return
        current_mode = self._current_video_mode()
        self.video_mode_combo.blockSignals(True)
        self.video_mode_combo.clear()
        self.video_mode_combo.addItem(self.tr("video_mode_score"), "score")
        self.video_mode_combo.addItem(self.tr("video_mode_piano_roll"), "piano_roll")
        index = self.video_mode_combo.findData(current_mode)
        self.video_mode_combo.setCurrentIndex(max(0, index))
        self.video_mode_combo.blockSignals(False)

    def _update_video_mode_enabled(self):
        if not hasattr(self, "video_mode_combo"):
            return
        enabled = self._video_output_selected()
        self.video_mode_label.setEnabled(enabled)
        self.video_mode_combo.setEnabled(enabled)

    def _update_annotation_mode_enabled(self):
        if not hasattr(self, "annotation_mode_combo"):
            return
        enabled = self._annotation_output_selected()
        self.annotation_mode_label.setEnabled(enabled)
        self.annotation_mode_combo.setEnabled(enabled)

    def _selected_output_options(self):
        annotation_mode = self._current_annotation_mode()
        timbre = self._current_timbre()
        video_mode = self._current_video_mode()
        quality_gate = self.quality_gate_checkbox.isChecked()
        preprocess = self.preprocess_checkbox.isChecked()
        staff_crop_recovery = self.staff_crop_recovery_checkbox.isChecked()
        if self.output_all.isChecked():
            return {
                "annotations": True,
                "audio": True,
                "midi": True,
                "video": True,
                "scientific_report": True,
                "include_events": True,
                "quality_gate": quality_gate,
                "preprocess": preprocess,
                "staff_crop_recovery": staff_crop_recovery,
                "annotation_mode": annotation_mode,
                "timbre": timbre,
                "video_mode": video_mode,
            }
        scientific_report = self.output_scientific.isChecked() or quality_gate
        return {
            "annotations": self.output_annotations.isChecked(),
            "audio": self.output_audio.isChecked(),
            "midi": self.output_midi.isChecked(),
            "video": self.output_video.isChecked(),
            "scientific_report": scientific_report,
            "include_events": scientific_report,
            "quality_gate": quality_gate,
            "preprocess": preprocess,
            "staff_crop_recovery": staff_crop_recovery,
            "annotation_mode": annotation_mode,
            "timbre": timbre,
            "video_mode": video_mode,
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

    def _theme_button_text(self):
        if self.language == "pt":
            return "Claro" if self.current_theme == "dark" else "Escuro"
        return "Light" if self.current_theme == "dark" else "Dark"

    def _theme_button_tooltip(self):
        if self.language == "pt":
            return "Alternar tema claro/escuro"
        return "Toggle light/dark theme"

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

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_style()
        self.theme_button.setText(self._theme_button_text())
        self.theme_button.setToolTip(self._theme_button_tooltip())
        self._set_active_page(self.stackedWidget.currentWidget(), self._active_nav_button())

    def _active_nav_button(self):
        for nav_button in (self.homeButton, self.sheetsButton, self.midiButton, self.aboutButton):
            if nav_button.property("active") == True:
                return nav_button
        return self.homeButton

    def _apply_theme_assets(self):
        logo_name = "logo_black.png" if self.current_theme == "dark" else "logo.png"
        logo_path = str(BASE_DIR / "ui" / logo_name)
        sidebar_logo = QPixmap(logo_path)
        if not sidebar_logo.isNull():
            self.sidebar_brand.setPixmap(
                sidebar_logo.scaled(
                    QSize(180, 132),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
            if hasattr(self, "home_logo"):
                self.home_logo.setPixmap(
                    sidebar_logo.scaled(
                        QSize(440, 300),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
            if hasattr(self, "about_logo"):
                self.about_logo.setPixmap(
                    sidebar_logo.scaled(
                        QSize(260, 178),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
            self.label.setPixmap(sidebar_logo)
            self.label_3.setPixmap(sidebar_logo)

    def apply_language(self):
        self.sidebar_brand_caption.setText(self.tr("sidebar_caption"))
        self.language_button.setText(self._language_button_text())
        self.language_button.setIcon(self._language_button_icon())
        self.language_button.setToolTip("Idioma" if self.language == "pt" else "Language")
        self.theme_button.setText(self._theme_button_text())
        self.theme_button.setToolTip(self._theme_button_tooltip())
        self.homeButton.setText(self.tr("home_nav"))
        self.sheetsButton.setText(self.tr("scores_nav"))
        self.midiButton.setText(self.tr("midi_nav"))
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
        self.selected_score_label.setText(self.tr("selected_score"))
        self.presets_title.setText(self.tr("presets_title"))
        self.presets_hint.setText(self.tr("presets_hint"))
        self.preset_review_button.setText(self.tr("preset_review"))
        self.preset_review_button.setToolTip(self.tr("preset_review_tip"))
        self.preset_listen_button.setText(self.tr("preset_listen"))
        self.preset_listen_button.setToolTip(self.tr("preset_listen_tip"))
        self.preset_video_button.setText(self.tr("preset_video"))
        self.preset_video_button.setToolTip(self.tr("preset_video_tip"))
        self.preset_full_button.setText(self.tr("preset_full"))
        self.preset_full_button.setToolTip(self.tr("preset_full_tip"))
        self.output_title.setText(self.tr("outputs_title"))
        self.output_hint.setText(self.tr("outputs_hint"))
        self.advanced_toggle_button.setText(
            self.tr("hide_advanced_options") if self.advanced_visible else self.tr("advanced_options")
        )
        self.log_toggle_button.setText(
            self.tr("hide_logs") if self.logs_visible else self.tr("show_logs")
        )
        self.diagnostics_title.setText(self.tr("diagnostics_title"))
        self.diagnostics_button.setText(self.tr("diagnostics_button"))
        if not self.diagnostics_summary.text():
            self.diagnostics_summary.setText(self.tr("diagnostics_pending"))
        self.bpm_label.setText(self.tr("bpm"))
        self.choose_button.setText(self.tr("choose_files"))
        self.process_button.setText(self.tr("process"))
        self.output_label.setText(self.tr("generate"))
        self.output_all.setText(self.tr("all"))
        self.output_annotations.setText(self.tr("annotations"))
        self.output_audio.setText(self.tr("audio"))
        self.output_midi.setText(self.tr("midi"))
        self.output_video.setText(self.tr("video"))
        self.output_scientific.setText(self.tr("scientific_report"))
        self.annotation_mode_label.setText(self.tr("annotation_view"))
        self._refresh_annotation_mode_options()
        self.sound_label.setText(self.tr("sound_label"))
        self._refresh_timbre_options()
        self.video_mode_label.setText(self.tr("video_mode"))
        self._refresh_video_mode_options()
        self.preprocess_checkbox.setText(self.tr("preprocess"))
        self.quality_gate_checkbox.setText(self.tr("quality_gate"))
        self.staff_crop_recovery_checkbox.setText(self.tr("staff_crop_recovery"))
        self.video_warning_label.setText(self.tr("video_warning"))
        self.review_title.setText(self.tr("review_title"))
        self.review_detailed_button.setText(self.tr("review_prepare_detailed"))
        self.review_editor_button.setText(self.tr("review_editor"))
        self.review_hint_label.setText(self.tr("review_hint"))
        if not self.review_status_label.text():
            self.review_status_label.setText(self.tr("review_ready"))
        for label, label_key, value_label in self.review_metric_values.values():
            label.setText(self.tr(label_key))
        self.annotation_preview_title.setText(self.tr("preview_title"))
        self.annotation_preview_hint.setText(self.tr("preview_empty"))
        if not self.progress_status_label.isVisible():
            self.progress_status_label.setText(self.tr("progress_waiting"))
        self.log_output.setPlaceholderText(self.tr("log_placeholder"))
        self.open_folder_button.setText(self.tr("open_folder"))
        self.open_annotations_button.setText(self.tr("open_annotations"))
        self.open_video_button.setText(self.tr("open_video"))
        self.open_audio_button.setText(self.tr("open_audio"))
        self.open_midi_button.setText(self.tr("open_midi_player"))
        self.open_scientific_button.setText(self.tr("open_scientific_report"))
        self.selectsheetButton.setToolTip(self.tr("select_scores"))
        for button in self.findChildren(QPushButton):
            if button.objectName() == "infoButton":
                button.setToolTip(self.tr("help_title"))
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
        for stat_label, stat_key in getattr(self, "about_stat_labels", []):
            stat_label.setText(self.tr(stat_key))
        self._update_video_warning()
        self._update_annotation_mode_enabled()
        self._refresh_output_cards()
        self._update_video_mode_enabled()
        self._update_selected_files()
        self._refresh_output_cards()
        self._refresh_preset_buttons()
        self._refresh_environment_diagnostics(log_details=False)
        if self.review_frame.isVisible() and self.last_result:
            self._update_review_panel(self.last_result)
        self._apply_button_icons()

    def _set_active_page(self, page, button):
        self.stackedWidget.setCurrentWidget(page)
        for nav_button in (self.homeButton, self.aboutButton, self.sheetsButton, self.midiButton):
            is_active = nav_button is button
            nav_button.setProperty("active", is_active)
            if is_active:
                nav_button.setGraphicsEffect(None)
            else:
                nav_button.setGraphicsEffect(None)
            nav_button.style().unpolish(nav_button)
            nav_button.style().polish(nav_button)
        if page is self.page:
            self._processing_layout_mode = None
            QTimer.singleShot(0, self._update_responsive_layout)

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
        self.last_result = {}
        self._set_active_page(self.page, self.sheetsButton)
        self._update_selected_files()
        self.home_status_label.setText(self.tr("status_selected", count=len(self.selected_files)))
        self._set_result_buttons_enabled(False)
        self.process_button.setEnabled(True)
        self.log_output.clear()
        self.log(self.tr("status_selected", count=len(self.selected_files)))

    def _refresh_environment_diagnostics(self, log_details=True):
        checks = collect_environment_diagnostics(self.language)
        status = diagnostics_overall_status(checks)
        status_key = {
            "ok": "diagnostics_ok",
            "warning": "diagnostics_warning",
            "error": "diagnostics_error",
        }.get(status, "diagnostics_pending")
        self.diagnostics_frame.setProperty("severity", status)
        self.diagnostics_frame.style().unpolish(self.diagnostics_frame)
        self.diagnostics_frame.style().polish(self.diagnostics_frame)
        self.diagnostics_summary.setText(
            f"{self.tr(status_key)} {summarize_diagnostics(checks, self.language)}"
        )
        details = format_diagnostics(checks)
        self.diagnostics_details.setText(details)
        if log_details and hasattr(self, "log_output"):
            self.log(self.tr("diagnostics_title"))
            for line in details.splitlines():
                self.log(f"- {line}")

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

        checks = collect_environment_diagnostics(self.language)
        if diagnostics_overall_status(checks) == "error":
            self._refresh_environment_diagnostics(log_details=True)
            self._set_advanced_visible(True)
            self.show_message(self.tr("diagnostics_title"), self.tr("diagnostics_blocking"))
            return

        self.log_output.clear()
        self.annotation_preview_frame.setVisible(False)
        self.review_frame.setVisible(False)
        self.annotation_preview_image.clear()
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
        self._refresh_environment_diagnostics(log_details=False)

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
            self.last_result = dict(result or {})
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(100)
            self.progress_status_label.setVisible(True)
            self.progress_status_label.setText(self.tr("progress_complete"))
            self.result_files = {}
            path_keys = {"output_dir", "annotations", "audio", "midi", "video", "scientific_report", "scientific_data"}
            for key, value in result.items():
                if key not in path_keys:
                    continue
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
            self._update_review_panel(result)
            self._update_annotation_preview()
            self.home_status_label.setText(self.tr("status_done"))
            self.log(self.tr("status_done"))
            self._log_validation_report(result.get("validation"))
            self._notify_processing_done()
            self.show_message(self.tr("done_title"), self.tr("done_msg"))
        else:
            self.progress_bar.setVisible(False)
            self.review_frame.setVisible(False)
            self.progress_status_label.setVisible(True)
            self.progress_status_label.setText(self.tr("status_error"))
            self.home_status_label.setText(self.tr("status_error"))
            self.log(self.tr("status_error"))
            self.show_message(
                self.tr("error_title"),
                self.tr("error_msg"),
            )

    def _notify_processing_done(self):
        QApplication.beep()
        QTimer.singleShot(140, QApplication.beep)

    def _prepare_detailed_review(self):
        self._apply_output_preset("review")
        self._set_advanced_visible(True)
        self._set_active_page(self.page, self.sheetsButton)

    def _format_confidence(self, value):
        if value is None:
            return "N/A"
        return f"{int(round(float(value) * 100))}%"

    def _format_duration(self, seconds):
        seconds = int(round(float(seconds or 0)))
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes}:{seconds:02d}"

    def _format_validation_summary(self, validation):
        if not validation:
            return "-"
        issues = validation.get("issues", [])
        warnings = sum(1 for issue in issues if issue.get("severity") == "warning")
        errors = sum(1 for issue in issues if issue.get("severity") == "error")
        if errors:
            return self.tr("validation_error")
        if warnings:
            return self.tr("validation_warning")
        return self.tr("validation_ok")

    def _set_review_metric(self, key, value):
        if key not in self.review_metric_values:
            return
        label, label_key, value_label = self.review_metric_values[key]
        label.setText(self.tr(label_key))
        value_label.setText(str(value))

    def _update_review_panel(self, result):
        review = result.get("review") or {}
        validation = result.get("validation") or {}
        quality = review.get("quality", "empty")
        has_validation_error = bool(validation and not validation.get("ok", True))
        severity = "warning" if quality in {"review", "empty"} or has_validation_error else "ok"

        status_key = {
            "ready": "review_ready",
            "review": "review_attention",
            "empty": "review_empty",
        }.get(quality, "review_attention")

        self.review_frame.setProperty("severity", severity)
        self.review_frame.style().unpolish(self.review_frame)
        self.review_frame.style().polish(self.review_frame)
        self.review_status_label.setProperty("severity", severity)
        self.review_status_label.style().unpolish(self.review_status_label)
        self.review_status_label.style().polish(self.review_status_label)
        self.review_status_label.setText(self.tr(status_key))

        low_count = review.get("low_confidence_count", 0)
        review_count = review.get("review_confidence_count", 0)
        confidence_attention = low_count + review_count
        left_count = review.get("left_hand_count", 0)
        right_count = review.get("right_hand_count", 0)

        self._set_review_metric("events", review.get("event_count", result.get("event_count", 0)))
        self._set_review_metric("pages", review.get("page_count", "-"))
        self._set_review_metric("confidence", self._format_confidence(review.get("average_confidence")))
        self._set_review_metric("low_confidence", confidence_attention)
        self._set_review_metric("hands", f"L {left_count} / R {right_count}")
        self._set_review_metric("duration", self._format_duration(review.get("duration_seconds", 0)))
        self._set_review_metric("outputs", self._format_validation_summary(validation))
        self._set_review_metric(
            "recommendation",
            self.tr("review_recommendation_check")
            if severity == "warning"
            else self.tr("review_recommendation_ready"),
        )

        self.review_hint_label.setText(self.tr("review_hint"))
        self.review_frame.setVisible(True)
        self.review_editor_button.setEnabled(bool(self._scientific_data_path()))

    def _log_validation_report(self, validation):
        if not validation:
            return
        issues = validation.get("issues", [])
        has_errors = any(issue.get("severity") == "error" for issue in issues)
        has_warnings = any(issue.get("severity") == "warning" for issue in issues)
        if has_errors or not validation.get("ok", True):
            self.log(self.tr("validation_error"))
        elif has_warnings:
            self.log(self.tr("validation_warning"))
        else:
            self.log(self.tr("validation_ok"))
        for issue in issues:
            severity = issue.get("severity", "info").upper()
            message = issue.get("message", "")
            if message:
                self.log(f"- {severity}: {message}")

    def _update_annotation_preview(self):
        annotations = self.result_files.get("annotations")
        if isinstance(annotations, list):
            preview_path = annotations[0] if annotations else None
        else:
            preview_path = annotations

        if not preview_path or not Path(preview_path).exists():
            self.annotation_preview_frame.setVisible(False)
            self.annotation_preview_image.clear()
            return

        pixmap = QPixmap(str(preview_path))
        if pixmap.isNull():
            self.annotation_preview_frame.setVisible(False)
            self.annotation_preview_image.clear()
            return

        self.annotation_preview_image.setPixmap(
            pixmap.scaled(
                QSize(360, 170),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        self.annotation_preview_frame.setVisible(True)

    def _set_controls_enabled(self, enabled):
        self.home_select_button.setEnabled(enabled)
        self.selectsheetButton.setEnabled(enabled)
        self.choose_button.setEnabled(enabled)
        self.diagnostics_button.setEnabled(enabled)
        self.advanced_toggle_button.setEnabled(enabled)
        self.process_button.setEnabled(enabled and bool(self.selected_files))
        self.bpm_input.setEnabled(enabled)
        self.output_all.setEnabled(enabled)
        for button in (
            self.preset_review_button,
            self.preset_listen_button,
            self.preset_video_button,
            self.preset_full_button,
            self.review_detailed_button,
            self.review_editor_button,
        ):
            button.setEnabled(enabled)
        self.sound_label.setEnabled(enabled)
        self.sound_combo.setEnabled(enabled)
        self.preprocess_checkbox.setEnabled(enabled)
        self.quality_gate_checkbox.setEnabled(enabled)
        self.staff_crop_recovery_checkbox.setEnabled(enabled)
        self.video_mode_label.setEnabled(enabled and self._video_output_selected())
        self.video_mode_combo.setEnabled(enabled and self._video_output_selected())
        if enabled:
            self._sync_output_controls(self.output_all.isChecked())
            self._update_annotation_mode_enabled()
            self._update_video_mode_enabled()
        else:
            for checkbox in (
                self.output_annotations,
                self.output_audio,
                self.output_midi,
                self.output_video,
                self.output_scientific,
            ):
                checkbox.setEnabled(False)
            self.annotation_mode_label.setEnabled(False)
            self.annotation_mode_combo.setEnabled(False)
            self.sound_label.setEnabled(False)
            self.sound_combo.setEnabled(False)
            self.video_mode_label.setEnabled(False)
            self.video_mode_combo.setEnabled(False)
        self._refresh_output_cards()

    def _set_result_buttons_enabled(self, enabled):
        self.open_folder_button.setEnabled(enabled)
        self.open_annotations_button.setEnabled(enabled and bool(self.result_files.get("annotations")))
        self.open_video_button.setEnabled(enabled and bool(self.result_files.get("video")))
        self.open_audio_button.setEnabled(enabled and bool(self.result_files.get("audio")))
        self.open_midi_button.setEnabled(enabled and bool(self.result_files.get("midi")))
        self.open_scientific_button.setEnabled(enabled and bool(self.result_files.get("scientific_report")))

    def log(self, message):
        self.log_output.append(str(message))
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def _result_path(self, key):
        path = self.result_files.get(key)
        if isinstance(path, list):
            path = path[0] if path else None
        if not path:
            return None
        path = Path(path)
        return path if path.exists() else None

    def open_result(self, key):
        path = self._result_path(key)
        if not path:
            self.show_message(self.tr("missing_title"), self.tr("missing_msg"))
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _scientific_data_path(self):
        data_path = self._result_path("scientific_data")
        if data_path:
            return data_path
        report_path = self._result_path("scientific_report")
        if report_path:
            candidate = report_path.with_suffix(".json")
            if candidate.exists():
                return candidate
        return None

    def _make_report_metric_card(self, title, value):
        card = QFrame()
        card.setObjectName("outputCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        title_label = QLabel(str(title))
        title_label.setObjectName("reviewMetricLabel")
        title_label.setWordWrap(True)
        value_label = QLabel(str(value))
        value_label.setObjectName("reviewMetricValue")
        value_label.setWordWrap(True)
        value_font = QFont(value_label.font())
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return card

    def _make_report_bar(self, label, value, total):
        row = QHBoxLayout()
        row.setSpacing(10)
        name = QLabel(str(label))
        name.setObjectName("reviewMetricLabel")
        name.setMinimumWidth(96)
        bar = QProgressBar()
        bar.setRange(0, max(1, int(total)))
        bar.setValue(max(0, int(value)))
        percent = int(round((float(value) / max(1, float(total))) * 100))
        bar.setFormat(f"{percent}%")
        amount = QLabel(str(value))
        amount.setObjectName("reviewMetricValue")
        amount.setMinimumWidth(42)
        amount.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(name)
        row.addWidget(bar, 1)
        row.addWidget(amount)
        return row

    def _make_report_chart_card(self, title, items, limit=None):
        card = QFrame()
        card.setObjectName("outputCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        if isinstance(items, dict):
            item_list = list(items.items())
        else:
            item_list = list(items or [])
        item_list = [(str(label), int(value or 0)) for label, value in item_list]
        if limit:
            item_list = sorted(item_list, key=lambda item: item[1], reverse=True)[:limit]
        if not item_list:
            item_list = [("-", 0)]
        total = sum(value for _label, value in item_list) or 1
        for label, value in item_list:
            layout.addLayout(self._make_report_bar(label, value, total))
        return card

    def _report_validation_text(self, validation):
        validation = validation or {}
        issues = validation.get("issues", []) if isinstance(validation, dict) else []
        if not issues:
            return "No validation warnings." if self.language == "en" else "Nenhum aviso de validação."
        lines = []
        for issue in issues[:8]:
            severity = issue.get("severity", "info").upper()
            message = issue.get("message", "")
            lines.append(f"{severity}: {message}")
        if len(issues) > 8:
            suffix = f"+{len(issues) - 8} more" if self.language == "en" else f"+{len(issues) - 8} itens"
            lines.append(suffix)
        return "\n".join(lines)

    def _corrections_path_for_report(self, data_path):
        data_path = Path(data_path)
        name = data_path.name.replace("_scientific_report.json", "_corrections.json")
        if name == data_path.name:
            name = f"{data_path.stem}_corrections.json"
        return data_path.with_name(name)

    def _corrected_midi_path_for_report(self, data_path):
        data_path = Path(data_path)
        name = data_path.name.replace("_scientific_report.json", "_corrected.mid")
        if name == data_path.name:
            name = f"{data_path.stem}_corrected.mid"
        return data_path.with_name(name)

    def _collect_review_corrections(self, table):
        corrections = []
        for row in range(table.rowCount()):
            include_item = table.item(row, 0)
            label_item = table.item(row, 1)
            original_item = table.item(row, 2)
            event_index = int(original_item.data(Qt.UserRole))
            label = normalized_label(label_item.text())
            corrections.append({
                "index": event_index,
                "enabled": include_item.checkState() == Qt.Checked,
                "label": label,
                "original_label": original_item.text(),
            })
        return corrections

    def open_review_editor(self):
        data_path = self._scientific_data_path()
        if not data_path:
            self.show_message(self.tr("missing_title"), self.tr("review_editor_no_events"))
            return
        try:
            payload = json.loads(Path(data_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.show_message(self.tr("error_title"), str(exc))
            return

        events = payload.get("events", [])
        if not events:
            self.show_message(self.tr("missing_title"), self.tr("review_editor_no_events"))
            return

        dialog = QDialog(self)
        dialog.setObjectName("appDialog")
        dialog.setWindowTitle(self.tr("review_editor_title"))
        dialog.setModal(True)
        dialog.setMinimumSize(980, 680)
        dialog.resize(1180, 760)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        title_label = QLabel(self.tr("review_editor_title"))
        title_label.setObjectName("dialogTitle")
        hint_label = QLabel(self.tr("review_editor_hint"))
        hint_label.setObjectName("dialogBody")
        hint_label.setWordWrap(True)

        table = QTableWidget()
        table.setObjectName("reviewTable")
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Use",
            "Label",
            "Original",
            "Hand",
            "Confidence",
            "Start",
            "Duration",
        ])
        table.setRowCount(len(events))
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.AnyKeyPressed
        )

        sorted_events = sorted(
            enumerate(events),
            key=lambda item: (
                float(item[1].get("confidence") if item[1].get("confidence") is not None else 1.0),
                int(item[1].get("start_ms", 0)),
            ),
        )
        for row, (event_index, event) in enumerate(sorted_events):
            include_item = QTableWidgetItem()
            include_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
            include_item.setCheckState(Qt.Checked)
            label_item = QTableWidgetItem(str(event.get("label", "")))
            original_item = QTableWidgetItem(str(event.get("label", "")))
            original_item.setData(Qt.UserRole, event_index)
            original_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            hand_item = QTableWidgetItem(str(event.get("hand", "-")))
            hand_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            confidence = event.get("confidence")
            confidence_text = self._format_confidence(confidence) if confidence is not None else "N/A"
            confidence_item = QTableWidgetItem(confidence_text)
            confidence_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            start_item = QTableWidgetItem(self._format_duration(float(event.get("start_ms", 0)) / 1000))
            start_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            duration_item = QTableWidgetItem(f"{int(event.get('duration_ms', 0))} ms")
            duration_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            for column, item in enumerate((
                include_item,
                label_item,
                original_item,
                hand_item,
                confidence_item,
                start_item,
                duration_item,
            )):
                table.setItem(row, column, item)

        table.resizeColumnsToContents()
        table.setColumnWidth(1, max(92, table.columnWidth(1)))

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        save_button = QPushButton(self.tr("review_editor_save"))
        save_button.setObjectName("secondaryButton")
        export_button = QPushButton(self.tr("review_editor_export_midi"))
        export_button.setObjectName("primaryButton")
        close_button = QPushButton(self.tr("close"))
        close_button.setObjectName("secondaryButton")
        close_button.clicked.connect(dialog.accept)

        def save_current_corrections(show_feedback=True):
            try:
                corrections = self._collect_review_corrections(table)
            except ValueError:
                self.show_message(self.tr("error_title"), self.tr("review_editor_invalid"))
                return None
            path = save_corrections(self._corrections_path_for_report(data_path), corrections)
            if show_feedback:
                self.show_message(self.tr("done_title"), f"{self.tr('review_editor_saved')}\n{path}")
            return path

        def export_current_midi():
            corrections_path = save_current_corrections(show_feedback=False)
            if not corrections_path:
                return
            bpm = int(payload.get("inputs", {}).get("bpm") or self.bpm_input.value())
            midi_path = export_corrected_midi(
                data_path,
                corrections_path,
                self._corrected_midi_path_for_report(data_path),
                bpm=bpm,
            )
            self.result_files["midi"] = str(midi_path)
            self._set_result_buttons_enabled(True)
            self.show_message(self.tr("done_title"), f"{self.tr('review_editor_exported')}\n{midi_path}")

        save_button.clicked.connect(lambda: save_current_corrections(show_feedback=True))
        export_button.clicked.connect(export_current_midi)
        button_row.addWidget(save_button)
        button_row.addWidget(export_button)
        button_row.addWidget(close_button)

        layout.addWidget(title_label)
        layout.addWidget(hint_label)
        layout.addWidget(table, 1)
        layout.addLayout(button_row)
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()

    def open_scientific_report(self):
        data_path = self._scientific_data_path()
        if not data_path:
            self.show_message(self.tr("missing_title"), self.tr("missing_msg"))
            return
        try:
            payload = json.loads(data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.show_message(self.tr("error_title"), str(exc))
            return

        recognition = payload.get("recognition", {})
        review = recognition.get("review", {})
        interpretation = payload.get("musical_interpretation", {})
        timing = payload.get("timing_interpretation", {})
        validation = payload.get("validation") or {}
        reliability = payload.get("reliability_analysis", {})

        dialog = QDialog(self)
        dialog.setObjectName("appDialog")
        dialog.setWindowTitle(self.tr("scientific_report_title"))
        dialog.setModal(True)
        dialog.setMinimumSize(900, 680)
        dialog.resize(1080, 760)

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(24, 22, 24, 20)
        dialog_layout.setSpacing(16)

        title_label = QLabel(self.tr("scientific_report_title"))
        title_label.setObjectName("dialogTitle")
        hint_label = QLabel(self.tr("scientific_report_hint"))
        hint_label.setObjectName("dialogBody")
        hint_label.setWordWrap(True)
        recommendation = reliability.get("message")
        if recommendation and self.language == "en":
            hint_label.setText(f"{hint_label.text()}\n\n{recommendation}")

        scroll = QScrollArea()
        scroll.setObjectName("reportScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setAutoFillBackground(False)
        scroll.viewport().setAutoFillBackground(False)
        scroll.viewport().setStyleSheet("background: transparent;")
        scroll.setStyleSheet(
            """
            QScrollArea#reportScroll {
                background: transparent;
                border: 0;
            }
            QScrollArea#reportScroll > QWidget,
            QScrollArea#reportScroll > QWidget > QWidget,
            QFrame#reportContent {
                background: transparent;
                border: 0;
            }
            """
        )
        scroll_content = QFrame()
        scroll_content.setObjectName("reportContent")
        scroll_content.setAutoFillBackground(False)
        scroll_content.setAttribute(Qt.WA_StyledBackground, True)
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(14)

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(12)
        metrics_grid.setVerticalSpacing(12)
        metrics = (
            ("Events" if self.language == "en" else "Eventos", review.get("event_count", recognition.get("event_count", 0))),
            ("Pages" if self.language == "en" else "Páginas", review.get("page_count", "-")),
            ("Duration" if self.language == "en" else "Duração", self._format_duration(review.get("duration_seconds", 0))),
            ("Confidence" if self.language == "en" else "Confiança", self._format_confidence(review.get("average_confidence"))),
            ("Needs review" if self.language == "en" else "Revisar", review.get("low_confidence_count", 0) + review.get("review_confidence_count", 0)),
            ("Accidentals" if self.language == "en" else "Acidentes", review.get("accidental_count", 0)),
        )
        for index, (label, value) in enumerate(metrics):
            metrics_grid.addWidget(self._make_report_metric_card(label, value), index // 3, index % 3)
        for column in range(3):
            metrics_grid.setColumnStretch(column, 1)
        scroll_layout.addLayout(metrics_grid)

        charts_grid = QGridLayout()
        charts_grid.setHorizontalSpacing(12)
        charts_grid.setVerticalSpacing(12)
        confidence_items = [
            ("Low" if self.language == "en" else "Baixa", recognition.get("confidence_histogram", {}).get("low", 0)),
            ("Review" if self.language == "en" else "Revisar", recognition.get("confidence_histogram", {}).get("review", 0)),
            ("High" if self.language == "en" else "Alta", recognition.get("confidence_histogram", {}).get("high", 0)),
        ]
        charts = (
            self._make_report_chart_card(self.tr("scientific_chart_confidence"), confidence_items),
            self._make_report_chart_card(self.tr("scientific_chart_hands"), interpretation.get("hand_distribution", {})),
            self._make_report_chart_card(self.tr("scientific_chart_pitch"), interpretation.get("pitch_class_counts", {}), limit=10),
            self._make_report_chart_card(self.tr("scientific_chart_duration"), interpretation.get("duration_profile", {})),
        )
        for index, chart in enumerate(charts):
            charts_grid.addWidget(chart, index // 2, index % 2)
        for column in range(2):
            charts_grid.setColumnStretch(column, 1)
        scroll_layout.addLayout(charts_grid)

        timing_items = {
            "Columns" if self.language == "en" else "Colunas": timing.get("column_count", 0) or 0,
            "Max polyphony" if self.language == "en" else "Polifonia máx.": timing.get("max_polyphony", 0) or 0,
            "Dense moments" if self.language == "en" else "Momentos densos": timing.get("dense_moment_count", 0) or 0,
            "Avg gap" if self.language == "en" else "Gap médio": int(timing.get("average_gap_ms", 0) or 0),
        }
        scroll_layout.addWidget(self._make_report_chart_card(self.tr("scientific_timing"), timing_items))

        recovery = review.get("staff_crop_recovery") or {}
        if recovery.get("enabled"):
            recovery_items = {
                "Crops" if self.language == "en" else "Recortes": recovery.get("crop_count", 0) or 0,
                "Recovered" if self.language == "en" else "Recuperados": recovery.get("recovered_count", 0) or 0,
                "Rejected" if self.language == "en" else "Rejeitados": recovery.get("rejected_count", 0) or 0,
            }
            scroll_layout.addWidget(
                self._make_report_chart_card(
                    self.tr("scientific_crop_recovery"),
                    recovery_items,
                )
            )

        details_grid = QGridLayout()
        details_grid.setHorizontalSpacing(12)
        details_grid.setVerticalSpacing(12)
        key_card = QFrame()
        key_card.setObjectName("outputCard")
        key_layout = QVBoxLayout(key_card)
        key_layout.setContentsMargins(16, 14, 16, 16)
        key_layout.setSpacing(8)
        key_title = QLabel(self.tr("scientific_key_signatures"))
        key_title.setObjectName("sectionTitle")
        key_body = QLabel()
        key_body.setObjectName("dialogBody")
        key_body.setWordWrap(True)
        key_signatures = interpretation.get("key_signatures", [])
        if key_signatures:
            page_word = "Page" if self.language == "en" else "Página"
            staff_word = "staff" if self.language == "en" else "pauta"
            key_body.setText("\n".join(
                f"{page_word} {item.get('page', '-')}, {staff_word} {item.get('staff', '-')}: {item.get('key_signature', {})}"
                for item in key_signatures[:8]
            ))
        else:
            key_body.setText("No key-signature context registered." if self.language == "en" else "Nenhum contexto de armadura registrado.")
        key_layout.addWidget(key_title)
        key_layout.addWidget(key_body)

        validation_card = QFrame()
        validation_card.setObjectName("outputCard")
        validation_layout = QVBoxLayout(validation_card)
        validation_layout.setContentsMargins(16, 14, 16, 16)
        validation_layout.setSpacing(8)
        validation_title = QLabel(self.tr("scientific_validation"))
        validation_title.setObjectName("sectionTitle")
        validation_body = QLabel(self._report_validation_text(validation))
        validation_body.setObjectName("dialogBody")
        validation_body.setWordWrap(True)
        validation_layout.addWidget(validation_title)
        validation_layout.addWidget(validation_body)

        details_grid.addWidget(key_card, 0, 0)
        details_grid.addWidget(validation_card, 0, 1)
        details_grid.setColumnStretch(0, 1)
        details_grid.setColumnStretch(1, 1)
        scroll_layout.addLayout(details_grid)

        json_note = QLabel(f"{self.tr('scientific_json_note')}\n{data_path}")
        json_note.setObjectName("dialogBody")
        json_note.setWordWrap(True)
        scroll_layout.addWidget(json_note)
        scroll.setWidget(scroll_content)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        review_button = QPushButton(self.tr("review_editor"))
        review_button.setObjectName("secondaryButton")
        review_button.clicked.connect(self.open_review_editor)
        close_button = QPushButton(self.tr("close"))
        close_button.setObjectName("primaryButton")
        close_button.clicked.connect(dialog.accept)
        button_row.addWidget(review_button)
        button_row.addWidget(close_button)

        dialog_layout.addWidget(title_label)
        dialog_layout.addWidget(hint_label)
        dialog_layout.addWidget(scroll, 1)
        dialog_layout.addLayout(button_row)
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()

    def _open_midi_player_window(self, midi_path=None):
        midi_path = Path(midi_path) if midi_path else None
        if midi_path and not midi_path.exists():
            midi_path = None

        if QWebEngineView is None:
            if midi_path:
                self.show_message(
                    self.tr("midi_player_unavailable_title"),
                    self.tr("midi_player_unavailable_msg"),
                )
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(midi_path)))
            else:
                self.show_message(
                    self.tr("midi_player_unavailable_title"),
                    self.tr("midi_page_unavailable"),
                )
            return

        self.midi_player_window = MidiPlayerWindow(midi_path, self)
        self.midi_player_window.show()
        self.midi_player_window.raise_()
        self.midi_player_window.activateWindow()

    def open_midi_player(self):
        midi_path = self._result_path("midi")
        if not midi_path:
            self.show_message(self.tr("missing_title"), self.tr("missing_msg"))
            return

        self._open_midi_player_window(midi_path)

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
        output_dir = self.result_files.get("output_dir")
        if output_dir and Path(output_dir).exists():
            folder = Path(output_dir)
        elif self.result_files:
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
        spin_up_dark = str(BASE_DIR / "ui" / "spin_up_dark.svg").replace("\\", "/")
        spin_down_dark = str(BASE_DIR / "ui" / "spin_down_dark.svg").replace("\\", "/")
        spin_up_light = str(BASE_DIR / "ui" / "spin_up_light.svg").replace("\\", "/")
        spin_down_light = str(BASE_DIR / "ui" / "spin_down_light.svg").replace("\\", "/")
        combo_down_dark = str(BASE_DIR / "ui" / "combo_down_dark.svg").replace("\\", "/")
        combo_down_light = str(BASE_DIR / "ui" / "combo_down_light.svg").replace("\\", "/")

        dark_style = """
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
            QScrollArea#processingScroll {
                background: transparent;
                border: 0;
            }
            QScrollArea#processingScroll > QWidget,
            QScrollArea#processingScroll > QWidget > QWidget {
                background: transparent;
            }
            QScrollArea#reportScroll {
                background: transparent;
                border: 0;
            }
            QScrollArea#reportScroll > QWidget,
            QScrollArea#reportScroll > QWidget > QWidget,
            QFrame#reportContent {
                background: transparent;
                border: 0;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 4px 0 4px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(64, 214, 255, 0.42);
                border-radius: 5px;
                min-height: 44px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(64, 214, 255, 0.62);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                border: 0;
                background: transparent;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
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
            QPushButton#primaryButton:disabled {
                color: rgba(248, 250, 252, 0.36);
                background: rgba(255, 255, 255, 0.045);
                border-color: rgba(255, 255, 255, 0.08);
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
            QPushButton#presetButton {
                background: rgba(255, 255, 255, 0.055);
                color: #f7f9ff;
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 16px;
                min-height: 44px;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 900;
                text-align: center;
            }
            QPushButton#presetButton:hover {
                background: rgba(64, 214, 255, 0.11);
                border-color: rgba(64, 214, 255, 0.38);
            }
            QPushButton#presetButton[active="true"] {
                background: rgba(64, 214, 255, 0.17);
                border-color: rgba(64, 214, 255, 0.62);
                color: #ffffff;
            }
            QPushButton#smallButton {
                background: rgba(255, 255, 255, 0.075);
                color: #f7f9ff;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 14px;
                min-height: 32px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 800;
            }
            QPushButton#smallButton:hover {
                background: rgba(64, 214, 255, 0.12);
                border-color: rgba(64, 214, 255, 0.42);
            }
            QPushButton#infoButton {
                min-width: 30px;
                max-width: 30px;
                min-height: 30px;
                max-height: 30px;
                padding: 0;
                border-radius: 15px;
                background: rgba(64, 214, 255, 0.10);
                border: 1px solid rgba(64, 214, 255, 0.28);
                color: #bff3ff;
                font-size: 13px;
                font-weight: 900;
            }
            QPushButton#infoButton:hover {
                background: rgba(64, 214, 255, 0.22);
                border-color: rgba(115, 226, 255, 0.62);
                color: #ffffff;
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
            QPushButton#languageButton,
            QPushButton#themeButton {
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
            QPushButton#languageButton:hover,
            QPushButton#themeButton:hover {
                background: rgba(64, 214, 255, 0.14);
                border-color: rgba(64, 214, 255, 0.48);
            }
            QPushButton#languageButton:pressed,
            QPushButton#themeButton:pressed {
                background: rgba(64, 214, 255, 0.22);
            }
            QPushButton#menuButton,
            QPushButton#homeButton,
            QPushButton#aboutButton,
            QPushButton#sheetsButton,
            QPushButton#midiButton {
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
            QPushButton#midiButton:hover,
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
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
            }
            QFrame#aboutHero {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(64, 214, 255, 0.10),
                    stop:0.48 rgba(255, 255, 255, 0.045),
                    stop:1 rgba(115, 226, 255, 0.08));
                border: 1px solid rgba(64, 214, 255, 0.20);
                border-radius: 20px;
            }
            QFrame#aboutLogoCard {
                background: rgba(8, 10, 18, 0.24);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 18px;
            }
            QLabel#aboutStatChip {
                color: #dff8ff;
                background: rgba(64, 214, 255, 0.12);
                border: 1px solid rgba(64, 214, 255, 0.28);
                border-radius: 14px;
                padding: 6px 8px;
                font-size: 11px;
                font-weight: 900;
            }
            QFrame#authorFrame {
                background: rgba(255, 255, 255, 0.055);
                border: 1px solid rgba(64, 214, 255, 0.18);
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
            QFrame#presetFrame,
            QFrame#reviewFrame {
                background: rgba(255, 255, 255, 0.045);
                border: 1px solid rgba(255, 255, 255, 0.095);
                border-radius: 16px;
            }
            QFrame#reviewFrame[severity="ok"] {
                background: rgba(108, 255, 136, 0.045);
                border-color: rgba(108, 255, 136, 0.22);
            }
            QFrame#reviewFrame[severity="warning"] {
                background: rgba(245, 158, 11, 0.070);
                border-color: rgba(245, 158, 11, 0.34);
            }
            QFrame#selectedFileFrame,
            QFrame#advancedFrame {
                background: rgba(255, 255, 255, 0.040);
                border: 1px solid rgba(255, 255, 255, 0.09);
                border-radius: 16px;
            }
            QFrame#outputCard {
                background: rgba(255, 255, 255, 0.050);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 15px;
            }
            QFrame#outputCard:hover {
                background: rgba(64, 214, 255, 0.10);
                border-color: rgba(64, 214, 255, 0.36);
            }
            QFrame#outputCard[selected="true"] {
                background: rgba(64, 214, 255, 0.145);
                border-color: rgba(64, 214, 255, 0.58);
            }
            QFrame#outputCard[disabled="true"] {
                background: rgba(255, 255, 255, 0.025);
                border-color: rgba(255, 255, 255, 0.055);
            }
            QFrame#diagnosticsFrame {
                background: rgba(255, 255, 255, 0.045);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 16px;
            }
            QFrame#diagnosticsFrame[severity="ok"] {
                border-color: rgba(108, 255, 136, 0.26);
                background: rgba(108, 255, 136, 0.055);
            }
            QFrame#diagnosticsFrame[severity="warning"] {
                border-color: rgba(245, 158, 11, 0.36);
                background: rgba(245, 158, 11, 0.08);
            }
            QFrame#diagnosticsFrame[severity="error"] {
                border-color: rgba(248, 113, 113, 0.40);
                background: rgba(248, 113, 113, 0.08);
            }
            QFrame#previewFrame {
                background: #151b2c;
                border: 1px solid rgba(64, 214, 255, 0.18);
                border-radius: 18px;
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
            QLabel#sectionTitle {
                color: #f7f9ff;
                font-size: 15px;
                font-weight: 900;
            }
            QLabel#sectionHint {
                color: #9fb0c9;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#diagnosticsTitle {
                color: #f7f9ff;
                font-size: 14px;
                font-weight: 900;
            }
            QLabel#diagnosticsSummary {
                color: #dbeafe;
                font-size: 13px;
                font-weight: 800;
            }
            QLabel#diagnosticsDetails {
                color: #9fb0c9;
                font-size: 11px;
                font-weight: 600;
                line-height: 1.35;
            }
            QLabel#reviewStatus {
                color: #07111f;
                background: #40d6ff;
                border-radius: 13px;
                padding: 5px 12px;
                font-size: 12px;
                font-weight: 900;
            }
            QLabel#reviewStatus[severity="warning"] {
                background: #f8c15c;
                color: #211500;
            }
            QLabel#reviewMetricLabel {
                color: #8fa0b8;
                font-size: 11px;
                font-weight: 900;
                text-transform: uppercase;
            }
            QLabel#reviewMetricValue {
                color: #f7f9ff;
                font-size: 13px;
                font-weight: 800;
            }
            QLabel#previewTitle {
                color: #f7f9ff;
                font-size: 16px;
                font-weight: 900;
            }
            QLabel#previewHint {
                color: #a3b1c8;
                font-size: 13px;
                font-weight: 600;
            }
            QLabel#annotationPreview {
                background: rgba(8, 10, 18, 0.44);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 14px;
                padding: 6px;
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
                min-width: 112px;
                min-height: 44px;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                padding: 4px 40px 4px 14px;
                background: rgba(255, 255, 255, 0.08);
                color: #f7f9ff;
                font-size: 14px;
                font-weight: 800;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 32px;
                height: 22px;
                border-left: 1px solid rgba(255, 255, 255, 0.12);
                border-top-right-radius: 17px;
                background: rgba(255, 255, 255, 0.075);
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 32px;
                height: 22px;
                border-left: 1px solid rgba(255, 255, 255, 0.12);
                border-bottom-right-radius: 17px;
                background: rgba(255, 255, 255, 0.075);
            }
            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background: rgba(64, 214, 255, 0.20);
            }
            QSpinBox::up-arrow {
                image: url(__SPIN_UP_DARK__);
                width: 14px;
                height: 14px;
            }
            QSpinBox::down-arrow {
                image: url(__SPIN_DOWN_DARK__);
                width: 14px;
                height: 14px;
            }
            QComboBox#modeCombo {
                min-width: 112px;
                min-height: 36px;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-radius: 14px;
                padding: 4px 34px 4px 12px;
                background: rgba(255, 255, 255, 0.08);
                color: #f7f9ff;
                font-weight: 800;
            }
            QComboBox#modeCombo::drop-down {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid rgba(255, 255, 255, 0.12);
                border-top-right-radius: 13px;
                border-bottom-right-radius: 13px;
                background: rgba(255, 255, 255, 0.07);
            }
            QComboBox#modeCombo::drop-down:hover {
                background: rgba(64, 214, 255, 0.20);
            }
            QComboBox#modeCombo::down-arrow {
                image: url(__COMBO_DOWN_DARK__);
                width: 16px;
                height: 16px;
            }
            QComboBox#modeCombo:hover {
                border-color: rgba(64, 214, 255, 0.42);
                background: rgba(64, 214, 255, 0.10);
            }
            QComboBox#modeCombo:disabled {
                color: #68768f;
                background: rgba(255, 255, 255, 0.035);
            }
            QComboBox#modeCombo QAbstractItemView {
                background: #101827;
                color: #f7f9ff;
                border: 1px solid rgba(64, 214, 255, 0.30);
                selection-background-color: rgba(64, 214, 255, 0.28);
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
            QDialog#appDialog QFrame#outputCard {
                background: rgba(255, 255, 255, 0.055);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 16px;
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
            QTableWidget#reviewTable {
                background: rgba(8, 12, 22, 0.82);
                alternate-background-color: rgba(255, 255, 255, 0.035);
                color: #f7f9ff;
                gridline-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(64, 214, 255, 0.18);
                border-radius: 14px;
                selection-background-color: rgba(64, 214, 255, 0.26);
            }
            QHeaderView::section {
                background: rgba(255, 255, 255, 0.07);
                color: #dff8ff;
                border: 0;
                padding: 8px;
                font-weight: 900;
            }
            """
        light_style = """
            QMainWindow, QWidget#centralwidget, QWidget#widget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #eaf7ff,
                    stop:0.52 #f8fdff,
                    stop:1 #dff4ff);
                color: #08121f;
            }
            QWidget#Sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.86),
                    stop:1 rgba(224, 247, 255, 0.66));
                border: 1px solid rgba(0, 92, 150, 0.18);
            }
            QStackedWidget,
            QWidget#Home,
            QWidget#about,
            QWidget#page,
            QLabel {
                color: #08121f;
                background: transparent;
            }
            QLabel#sidebarCaption,
            QLabel#panelSubtitle,
            QLabel#filesLabel,
            QLabel#text,
            QLabel#stepCaption,
            QLabel#workflowNote,
            QLabel#workflowItemCaption,
            QLabel#progressStatus,
            QLabel#dialogBody {
                color: #48627e;
            }
            QPushButton,
            QPushButton#secondaryButton,
            QPushButton#presetButton,
            QPushButton#smallButton,
            QPushButton#languageButton,
            QPushButton#themeButton {
                background: rgba(255, 255, 255, 0.58);
                color: #08121f;
                border-color: rgba(0, 92, 150, 0.16);
            }
            QPushButton:hover,
            QPushButton#secondaryButton:hover,
            QPushButton#presetButton:hover,
            QPushButton#smallButton:hover,
            QPushButton#languageButton:hover,
            QPushButton#themeButton:hover {
                background: rgba(22, 215, 255, 0.14);
                border-color: rgba(0, 140, 232, 0.42);
            }
            QPushButton#presetButton[active="true"] {
                background: rgba(22, 215, 255, 0.20);
                border-color: rgba(0, 140, 232, 0.48);
                color: #06121d;
            }
            QPushButton:disabled {
                color: rgba(8, 18, 31, 0.38);
                background: rgba(255, 255, 255, 0.34);
                border-color: rgba(0, 92, 150, 0.08);
            }
            QPushButton#primaryButton,
            QPushButton#startButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #16d7ff,
                    stop:1 #008ce8);
                color: #031018;
                border-color: rgba(0, 140, 232, 0.46);
            }
            QPushButton#primaryButton:hover,
            QPushButton#startButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6eeaff,
                    stop:1 #10a9f2);
                border-color: rgba(22, 215, 255, 0.72);
            }
            QPushButton#primaryButton:disabled {
                color: rgba(8, 18, 31, 0.38);
                background: rgba(255, 255, 255, 0.34);
                border-color: rgba(0, 92, 150, 0.08);
            }
            QPushButton#infoButton {
                background: rgba(0, 140, 232, 0.11);
                border: 1px solid rgba(0, 140, 232, 0.24);
                color: #006da8;
            }
            QPushButton#infoButton:hover {
                background: rgba(22, 215, 255, 0.22);
                border-color: rgba(0, 140, 232, 0.50);
                color: #031018;
            }
            QPushButton#homeButton,
            QPushButton#aboutButton,
            QPushButton#sheetsButton,
            QPushButton#midiButton {
                color: #08121f;
                background: rgba(255, 255, 255, 0.36);
            }
            QPushButton#homeButton:hover,
            QPushButton#aboutButton:hover,
            QPushButton#sheetsButton:hover,
            QPushButton#midiButton:hover {
                background: rgba(22, 215, 255, 0.12);
                border-color: rgba(0, 140, 232, 0.20);
            }
            QPushButton[active="true"] {
                color: #06121d;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 140, 232, 0.12),
                    stop:0.12 rgba(22, 215, 255, 0.28),
                    stop:0.5 rgba(255, 255, 255, 0.46),
                    stop:0.88 rgba(22, 215, 255, 0.26),
                    stop:1 rgba(0, 140, 232, 0.12));
                border: 1px solid rgba(0, 140, 232, 0.24);
            }
            QPushButton#selectsheetButton {
                border-color: rgba(0, 140, 232, 0.36);
                background: rgba(255, 255, 255, 0.50);
            }
            QFrame#homePanel,
            QFrame#processingPanel,
            QFrame#aboutPanel,
            QFrame#presetFrame,
            QFrame#reviewFrame,
            QFrame#selectedFileFrame,
            QFrame#advancedFrame,
            QWidget#Logo,
            QWidget#aboutText,
            QWidget#logoAbout,
            QWidget#picture,
            QWidget#widget_2 {
                background: rgba(255, 255, 255, 0.54);
                border: 1px solid rgba(0, 92, 150, 0.16);
            }
            QFrame#reviewFrame[severity="ok"] {
                background: rgba(42, 188, 98, 0.11);
                border-color: rgba(42, 188, 98, 0.26);
            }
            QFrame#reviewFrame[severity="warning"] {
                background: rgba(245, 158, 11, 0.14);
                border-color: rgba(194, 120, 3, 0.30);
            }
            QFrame#aboutHero {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(22, 215, 255, 0.12),
                    stop:0.55 rgba(255, 255, 255, 0.48),
                    stop:1 rgba(0, 140, 232, 0.10));
                border: 1px solid rgba(0, 140, 232, 0.18);
                border-radius: 20px;
            }
            QFrame#aboutLogoCard {
                background: rgba(255, 255, 255, 0.46);
                border: 1px solid rgba(0, 92, 150, 0.12);
                border-radius: 18px;
            }
            QLabel#aboutStatChip {
                color: #06466b;
                background: rgba(22, 215, 255, 0.16);
                border: 1px solid rgba(0, 140, 232, 0.22);
                border-radius: 14px;
                padding: 6px 8px;
                font-size: 11px;
                font-weight: 900;
            }
            QFrame#outputCard {
                background: rgba(255, 255, 255, 0.54);
                border: 1px solid rgba(0, 92, 150, 0.13);
                border-radius: 15px;
            }
            QFrame#outputCard:hover {
                background: rgba(22, 215, 255, 0.13);
                border-color: rgba(0, 140, 232, 0.34);
            }
            QFrame#outputCard[selected="true"] {
                background: rgba(22, 215, 255, 0.20);
                border-color: rgba(0, 140, 232, 0.50);
            }
            QFrame#outputCard[disabled="true"] {
                background: rgba(255, 255, 255, 0.32);
                border-color: rgba(0, 92, 150, 0.07);
            }
            QFrame#authorFrame,
            QFrame#outputFrame,
            QFrame#diagnosticsFrame,
            QFrame#stepCard,
            QFrame#workflowPanel {
                background: rgba(255, 255, 255, 0.48);
                border: 1px solid rgba(0, 92, 150, 0.14);
            }
            QFrame#diagnosticsFrame[severity="ok"] {
                background: rgba(42, 188, 98, 0.12);
                border-color: rgba(42, 188, 98, 0.28);
            }
            QFrame#diagnosticsFrame[severity="warning"] {
                background: rgba(245, 158, 11, 0.14);
                border-color: rgba(194, 120, 3, 0.28);
            }
            QFrame#diagnosticsFrame[severity="error"] {
                background: rgba(248, 113, 113, 0.14);
                border-color: rgba(190, 18, 60, 0.28);
            }
            QFrame#previewFrame {
                background: #f8fdff;
                border: 1px solid rgba(0, 140, 232, 0.16);
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 140, 232, 0.34);
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 140, 232, 0.54);
            }
            QLabel#homeTitle,
            QLabel#panelTitle,
            QLabel#workflowTitle,
            QLabel#workflowItemTitle,
            QLabel#stepTitle,
            QLabel#fieldLabel,
            QLabel#sectionTitle,
            QLabel#diagnosticsTitle,
            QLabel#dialogTitle {
                color: #08121f;
            }
            QLabel#sectionHint {
                color: #526a86;
            }
            QLabel#reviewStatus {
                color: #031018;
                background: #16d7ff;
            }
            QLabel#reviewStatus[severity="warning"] {
                background: #f3b84b;
                color: #211500;
            }
            QLabel#reviewMetricLabel {
                color: #5c728d;
            }
            QLabel#reviewMetricValue {
                color: #08121f;
            }
            QLabel#diagnosticsSummary {
                color: #17314d;
            }
            QLabel#diagnosticsDetails {
                color: #526a86;
            }
            QLabel#homeSubtitle {
                color: #27415f;
            }
            QLabel#previewTitle {
                color: #08121f;
            }
            QLabel#previewHint {
                color: #48617e;
            }
            QLabel#annotationPreview {
                background: rgba(255, 255, 255, 0.54);
                border-color: rgba(0, 92, 150, 0.14);
            }
            QLabel#eyebrow,
            QLabel#homeEyebrow,
            QLabel#stepNumber {
                color: #008ce8;
            }
            QLabel#statusPill {
                color: #08121f;
                background: rgba(22, 215, 255, 0.13);
                border: 1px solid rgba(0, 140, 232, 0.26);
            }
            QLabel#workflowNumber {
                color: #031018;
                background: #16d7ff;
            }
            QCheckBox {
                color: #27415f;
            }
            QCheckBox::indicator {
                border: 1px solid rgba(0, 92, 150, 0.20);
                background: rgba(255, 255, 255, 0.58);
            }
            QCheckBox::indicator:checked {
                background: #008ce8;
                border-color: #008ce8;
            }
            QSpinBox {
                background: rgba(255, 255, 255, 0.58);
                color: #08121f;
                border-color: rgba(0, 92, 150, 0.16);
            }
            QSpinBox::up-button,
            QSpinBox::down-button {
                background: rgba(0, 140, 232, 0.08);
                border-left: 1px solid rgba(0, 92, 150, 0.14);
            }
            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background: rgba(0, 140, 232, 0.18);
            }
            QSpinBox::up-arrow {
                image: url(__SPIN_UP_LIGHT__);
                width: 14px;
                height: 14px;
            }
            QSpinBox::down-arrow {
                image: url(__SPIN_DOWN_LIGHT__);
                width: 14px;
                height: 14px;
            }
            QComboBox#modeCombo {
                background: rgba(255, 255, 255, 0.58);
                color: #08121f;
                border-color: rgba(0, 92, 150, 0.16);
            }
            QComboBox#modeCombo::drop-down {
                background: rgba(0, 140, 232, 0.08);
                border-left: 1px solid rgba(0, 92, 150, 0.14);
            }
            QComboBox#modeCombo::drop-down:hover {
                background: rgba(0, 140, 232, 0.18);
            }
            QComboBox#modeCombo::down-arrow {
                image: url(__COMBO_DOWN_LIGHT__);
                width: 16px;
                height: 16px;
            }
            QComboBox#modeCombo QAbstractItemView {
                background: #f8fdff;
                color: #08121f;
                border: 1px solid rgba(0, 140, 232, 0.24);
                selection-background-color: rgba(0, 140, 232, 0.18);
            }
            QTextEdit {
                background: rgba(248, 253, 255, 0.86);
                color: #132943;
                border: 1px solid rgba(0, 140, 232, 0.22);
            }
            QLabel#warningPill {
                color: #805000;
                background: rgba(245, 158, 11, 0.14);
                border-color: rgba(245, 158, 11, 0.34);
            }
            QProgressBar {
                background: rgba(0, 92, 150, 0.10);
                color: #08121f;
            }
            QProgressBar::chunk {
                background: #008ce8;
            }
            QDialog#appDialog {
                background: #f8fdff;
                border: 1px solid rgba(0, 140, 232, 0.28);
            }
            QTableWidget#reviewTable {
                background: rgba(255, 255, 255, 0.78);
                alternate-background-color: rgba(0, 140, 232, 0.05);
                color: #08121f;
                gridline-color: rgba(0, 92, 150, 0.12);
                border: 1px solid rgba(0, 140, 232, 0.18);
            }
            QHeaderView::section {
                background: rgba(0, 140, 232, 0.10);
                color: #08121f;
            }
            QDialog#appDialog QFrame#outputCard {
                background: rgba(255, 255, 255, 0.68);
                border: 1px solid rgba(0, 92, 150, 0.14);
                border-radius: 16px;
            }
        """
        stylesheet = dark_style + (light_style if self.current_theme == "light" else "")
        stylesheet = (
            stylesheet
            .replace("__SPIN_UP_DARK__", spin_up_dark)
            .replace("__SPIN_DOWN_DARK__", spin_down_dark)
            .replace("__SPIN_UP_LIGHT__", spin_up_light)
            .replace("__SPIN_DOWN_LIGHT__", spin_down_light)
            .replace("__COMBO_DOWN_DARK__", combo_down_dark)
            .replace("__COMBO_DOWN_LIGHT__", combo_down_light)
        )
        self.setStyleSheet(stylesheet)
        for button in self.findChildren(InfoButton):
            button.setProperty("theme", self.current_theme)
            button.update()
        self._apply_theme_assets()


def main():
    app = QApplication(sys.argv)
    window = MainClef()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

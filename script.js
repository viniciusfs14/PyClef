const content = {
    en: {
        "nav-home": "Home",
        "nav-method": "Methodology",
        "nav-docs": "Docs",
        "nav-results": "Results",
        "hero-kicker": "Optical Music Recognition",
        "hero-title": "A Python toolkit for sheet music recognition.",
        "hero-lead": "PyClef detects musical symbols in score images and applies MIRP, a staff-referenced inference method, to reconstruct note pitch and export reviewable outputs.",
        "hero-start": "Get started",
        "hero-method": "Read the methodology",
        "metric-classes": "symbol classes",
        "metric-pitch": "TRA with MIRP",
        "intro-kicker": "Overview",
        "intro-title": "Object detection alone is not enough for OMR.",
        "intro-text": "PyClef treats detection as one stage of a larger reconstruction pipeline. The detector locates symbols; MIRP uses the detected clef and staff geometry to infer pitch from relative vertical displacement.",
        "card-neural-title": "Detection model",
        "card-neural-text": "The current model uses YOLOv11S trained on 208 DeepScoresV2 Dense classes, with 0.4126 mAP@[0.5:0.95] in the reported evaluation.",
        "card-mirp-title": "MIRP",
        "card-mirp-text": "The Staff-Referenced Musical Inference Method defines a reference note from the clef and staff, then infers the pitch of detected notes.",
        "pipeline-kicker": "Workflow",
        "pipeline-title": "The processing pipeline is explicit and auditable.",
        "step-detect-title": "Detect",
        "step-detect-text": "Load a PDF or image and detect staves, clefs, notes, rests and related notation symbols.",
        "step-refine-title": "Infer",
        "step-refine-text": "Use MIRP to convert staff-relative geometry into note names and octaves.",
        "step-reconstruct-title": "Review",
        "step-reconstruct-text": "Create annotated pages so the recognition result can be inspected visually.",
        "step-export-title": "Export",
        "step-export-text": "Write MIDI, MP3 and synchronized video files when those outputs are selected.",
        "app-kicker": "Desktop application",
        "app-title": "A focused interface for running PyClef locally.",
        "app-text": "Select a score, choose the desired outputs, set the BPM and run the pipeline. Results are written to a folder named after the input file.",
        "app-f1": "PDF, PNG and JPG input",
        "app-f2": "Annotated score pages",
        "app-f3": "MIDI, MP3 and synchronized video",
        "app-f4": "Integrated MIDI player with waterfall preview",
        "paper-kicker": "Paper",
        "paper-title": "Methodology and evaluation.",
        "paper-text": "The article describes the PyClef pipeline, the MIRP method and the reported detection and pitch reconstruction results.",
        "paper-download": "Coming soon",
        "paper-method": "Methodology",
        "method-kicker": "Methodology",
        "method-title": "MIRP: Staff-Referenced Musical Inference.",
        "method-lead": "MIRP uses the detected clef and staff boundaries to define a reference note. Other notes are inferred from their vertical displacement relative to that reference.",
        "mirp-1-title": "Staff reference",
        "mirp-1-text": "The detected staff provides its upper and lower boundaries. The vertical step is estimated from these coordinates.",
        "mirp-2-title": "Clef reference",
        "mirp-2-text": "The clef determines the reference note used to interpret positions on the staff.",
        "mirp-3-title": "Pitch reconstruction",
        "mirp-3-text": "In the reported YOLOv11S experiment, TRA improved from 0.04 to 0.975 after MIRP.",
        "method-flow-kicker": "Algorithm",
        "method-flow-title": "MIRP is applied after object detection.",
        "flow-1-title": "Collect detections",
        "flow-1-text": "Separate structural detections, such as staves and clefs, from note detections.",
        "flow-2-title": "Estimate staff step",
        "flow-2-text": "Compute the distance between adjacent staff positions from the detected staff box.",
        "flow-3-title": "Infer pitch",
        "flow-3-text": "Measure the vertical displacement between the reference note and each detected note center.",
        "flow-4-title": "Export results",
        "flow-4-text": "Write annotated images and optional playback files for inspection and reuse.",
        "article-kicker": "Article",
        "article-title": "PyClef: Optical Music Recognition with MIRP.",
        "article-text": "The paper reports YOLOv11S results on DeepScoresV2 Dense and shows that MIRP raises pitch reconstruction from about 4% to 97.5%.",
        "docs-kicker": "Documentation",
        "docs-title": "Install PyClef and run the desktop workflow.",
        "docs-lead": "PyClef can be launched from Python. The desktop app writes outputs to a result folder for inspection.",
        "doc-install-title": "Install",
        "doc-install-text": "Install the package from PyPI. On first use, PyClef can download the model file automatically.",
        "doc-launch-title": "Launch",
        "doc-launch-text": "Start the desktop interface from Python.",
        "doc-output-title": "Output files",
        "doc-output-text": "Depending on the selected options, a run can generate annotations, MP3, MIDI and MP4 files.",
        "guide-kicker": "Interface guide",
        "guide-title": "Desktop workflow",
        "guide-lead": "The interface is organized around file selection, output selection, progress logs and result review.",
        "guide-1-title": "Home",
        "guide-1-text": "Open the score workspace from the start screen.",
        "guide-2-title": "Scores",
        "guide-2-text": "Use the Scores page to select files, set BPM and choose outputs.",
        "guide-3-title": "Output options",
        "guide-3-text": "Choose annotation, MP3, MIDI, video or all available outputs.",
        "guide-4-title": "Progress",
        "guide-4-text": "Follow the progress bar and log output while the score is processed.",
        "guide-5-title": "Results",
        "guide-5-text": "Open the result folder or individual generated files after processing.",
        "guide-6-title": "About",
        "guide-6-text": "Review the project summary and links from the About page.",
        "midi-kicker": "MIDI Player",
        "midi-title": "Review generated MIDI files with a piano-roll view.",
        "midi-lead": "PyClef now includes a dedicated MIDI player window. It loads the generated MIDI, applies the piano SoundFont automatically and shows note timing with a waterfall view and responsive keyboard.",
        "midi-card-1-title": "Waterfall playback",
        "midi-card-1-text": "Notes fall toward the keyboard in sync with playback, making timing problems easier to inspect.",
        "midi-card-2-title": "Dynamic keyboard",
        "midi-card-2-text": "The piano range adapts to the MIDI file and labels white keys with note names.",
        "midi-card-3-title": "Hand-aware colors",
        "midi-card-3-text": "Right-hand and left-hand notes use different colors, including darker tones for black-key notes.",
        "midi-shot-label": "Playback view",
        "midi-shot-text": "Use the player to inspect MIDI timing before sharing or exporting the final result.",
        "midi-secondary-caption": "Loaded MIDI with piano range and metadata.",
        "usage-kicker": "Recommended use",
        "usage-title": "A simple workflow for repeatable experiments.",
        "usage-1-title": "Prepare the input",
        "usage-1-text": "Use a clear PDF, PNG or JPG. Cleaner scans usually produce better detections.",
        "usage-2-title": "Select outputs",
        "usage-2-text": "Generate annotations first for a quick check. Add audio, MIDI or video as needed.",
        "usage-3-title": "Check annotations",
        "usage-3-text": "Inspect the labeled image to verify note names and structural interpretation.",
        "usage-4-title": "Review playback",
        "usage-4-text": "Use MIDI, MP3 and video to evaluate the reconstructed score.",
        "cite-kicker": "Citation",
        "cite-title": "Citation",
        "cite-text": "If you use PyClef in academic work, cite the project. The MIRP paper will be available soon.",
        "results-kicker": "Evaluation",
        "results-title": "Detection quality and reconstruction quality are reported separately.",
        "results-lead": "The paper reports object detection metrics and functional pitch reconstruction metrics, since high mAP does not necessarily imply correct musical reconstruction.",
        "result-map": "YOLOv11S reached 0.4126 mAP@[0.5:0.95] on DeepScoresV2 Dense.",
        "result-tra": "With YOLOv11S, MIRP increased TRA from 0.04 to 0.975.",
        "results-balance-kicker": "Model comparison",
        "results-balance-title": "MIRP reduces the practical gap between model sizes.",
        "results-balance-text": "YOLOv11L reached 0.51379 mAP, but both YOLOv11S and YOLOv11L exceeded 97% TRA after MIRP.",
        "table-kicker": "Summary",
        "table-title": "Reported comparison points.",
        "metric-label": "Metric",
        "pitch-rate": "Pitch Reconstruction Rate",
        "model-size": "Model size",
        "training-cost": "Training cost",
        "smaller": "Smaller",
        "larger": "Larger",
        "lower": "Lower",
        "higher": "Higher",
        "footer-text": "Python toolkit for Optical Music Recognition.",
        "lang-btn": "EN"
    },
    pt: {
        "nav-home": "Início",
        "nav-method": "Metodologia",
        "nav-docs": "Docs",
        "nav-results": "Resultados",
        "hero-kicker": "Reconhecimento Óptico de Partituras",
        "hero-title": "Reconhecimento de partituras em Python.",
        "hero-lead": "O PyClef detecta símbolos musicais em imagens de partituras e aplica o MIRP, um método de inferência por referência de pauta, para reconstruir alturas e exportar resultados revisáveis.",
        "hero-start": "Começar",
        "hero-method": "Ler metodologia",
        "metric-classes": "classes de símbolos",
        "metric-pitch": "TRA com MIRP",
        "intro-kicker": "Visão geral",
        "intro-title": "Detecção de objetos, sozinha, não resolve OMR.",
        "intro-text": "O PyClef trata a detecção como uma etapa de um pipeline de reconstrução. O detector localiza símbolos; o MIRP usa a clave detectada e a geometria da pauta para inferir alturas por deslocamento vertical relativo.",
        "card-neural-title": "Modelo de detecção",
        "card-neural-text": "O modelo atual usa YOLOv11S treinado em 208 classes do DeepScoresV2 Dense, com 0,4126 mAP@[0,5:0,95] na avaliação reportada.",
        "card-mirp-title": "MIRP",
        "card-mirp-text": "O Método de Inferência Musical por Referência de Pauta define uma nota de referência pela clave e pela pauta e infere a altura das notas detectadas.",
        "pipeline-kicker": "Fluxo",
        "pipeline-title": "O pipeline de processamento é explícito e verificável.",
        "step-detect-title": "Detectar",
        "step-detect-text": "Carrega PDF ou imagem e detecta pautas, claves, notas, pausas e símbolos relacionados.",
        "step-refine-title": "Inferir",
        "step-refine-text": "Usa o MIRP para converter geometria relativa à pauta em nomes de notas e oitavas.",
        "step-reconstruct-title": "Revisar",
        "step-reconstruct-text": "Cria páginas anotadas para que o resultado do reconhecimento possa ser inspecionado visualmente.",
        "step-export-title": "Exportar",
        "step-export-text": "Gera arquivos MIDI, MP3 e vídeo sincronizado quando essas saídas são selecionadas.",
        "app-kicker": "Aplicação desktop",
        "app-title": "Uma interface focada para executar o PyClef localmente.",
        "app-text": "Selecione uma partitura, escolha as saídas, defina o BPM e execute o pipeline. Os resultados são gravados em uma pasta com o nome do arquivo de entrada.",
        "app-f1": "Entrada PDF, PNG e JPG",
        "app-f2": "Páginas anotadas",
        "app-f3": "MIDI, MP3 e vídeo sincronizado",
        "app-f4": "Player MIDI integrado com visualização em cascata",
        "paper-kicker": "Artigo",
        "paper-title": "Metodologia e avaliação.",
        "paper-text": "O artigo descreve o pipeline do PyClef, o método MIRP e os resultados de detecção e reconstrução de altura reportados.",
        "paper-download": "Coming soon",
        "paper-method": "Metodologia",
        "method-kicker": "Metodologia",
        "method-title": "MIRP: Inferência Musical por Referência de Pauta.",
        "method-lead": "O MIRP usa a clave detectada e os limites da pauta para definir uma nota de referência. As demais notas são inferidas pelo deslocamento vertical em relação a essa referência.",
        "mirp-1-title": "Referência da pauta",
        "mirp-1-text": "A pauta detectada fornece seus limites superior e inferior. O passo vertical é estimado a partir dessas coordenadas.",
        "mirp-2-title": "Referência da clave",
        "mirp-2-text": "A clave determina a nota de referência usada para interpretar posições na pauta.",
        "mirp-3-title": "Reconstrução de altura",
        "mirp-3-text": "No experimento com YOLOv11S, a TRA passou de 0,04 para 0,975 após a aplicação do MIRP.",
        "method-flow-kicker": "Algoritmo",
        "method-flow-title": "O MIRP é aplicado após a detecção de objetos.",
        "flow-1-title": "Coletar detecções",
        "flow-1-text": "Separa detecções estruturais, como pautas e claves, das detecções de notas.",
        "flow-2-title": "Estimar passo da pauta",
        "flow-2-text": "Calcula a distância entre posições adjacentes da pauta a partir da caixa detectada.",
        "flow-3-title": "Inferir altura",
        "flow-3-text": "Mede o deslocamento vertical entre a nota de referência e o centro de cada nota detectada.",
        "flow-4-title": "Exportar resultados",
        "flow-4-text": "Grava imagens anotadas e arquivos opcionais de reprodução para inspeção e reutilização.",
        "article-kicker": "Artigo",
        "article-title": "PyClef: Reconhecimento Óptico de Partituras com MIRP.",
        "article-text": "O artigo reporta resultados com YOLOv11S no DeepScoresV2 Dense e mostra que o MIRP eleva a reconstrução de altura de cerca de 4% para 97,5%.",
        "docs-kicker": "Documentação",
        "docs-title": "Instale o PyClef e execute o fluxo desktop.",
        "docs-lead": "O PyClef pode ser iniciado a partir do Python. A aplicação desktop grava os resultados em uma pasta para inspeção.",
        "doc-install-title": "Instalação",
        "doc-install-text": "Instale o pacote pelo PyPI. No primeiro uso, o PyClef pode baixar o arquivo do modelo automaticamente.",
        "doc-launch-title": "Inicialização",
        "doc-launch-text": "Inicie a interface desktop pelo Python.",
        "doc-output-title": "Arquivos gerados",
        "doc-output-text": "Dependendo das opções selecionadas, uma execução pode gerar anotações, MP3, MIDI e MP4.",
        "guide-kicker": "Guia da interface",
        "guide-title": "Fluxo desktop",
        "guide-lead": "A interface é organizada em seleção de arquivo, seleção de saídas, logs de progresso e revisão dos resultados.",
        "guide-1-title": "Home",
        "guide-1-text": "Abra o ambiente de partituras a partir da tela inicial.",
        "guide-2-title": "Partituras",
        "guide-2-text": "Use a página de Partituras para selecionar arquivos, definir BPM e escolher saídas.",
        "guide-3-title": "Opções de saída",
        "guide-3-text": "Escolha anotação, MP3, MIDI, vídeo ou todas as saídas disponíveis.",
        "guide-4-title": "Progresso",
        "guide-4-text": "Acompanhe a barra de progresso e o log enquanto a partitura é processada.",
        "guide-5-title": "Resultados",
        "guide-5-text": "Abra a pasta de resultados ou arquivos individuais após o processamento.",
        "guide-6-title": "Sobre",
        "guide-6-text": "Consulte o resumo do projeto e links na página Sobre.",
        "midi-kicker": "Player MIDI",
        "midi-title": "Revise arquivos MIDI gerados com uma visão tipo piano roll.",
        "midi-lead": "O PyClef agora inclui uma janela dedicada para reprodução MIDI. Ela carrega o MIDI gerado, aplica automaticamente o SoundFont de piano e mostra o tempo das notas com uma visualização em cascata e teclado responsivo.",
        "midi-card-1-title": "Reprodução em cascata",
        "midi-card-1-text": "As notas descem em direção ao teclado de forma sincronizada com a reprodução, facilitando a inspeção de problemas de tempo.",
        "midi-card-2-title": "Teclado dinâmico",
        "midi-card-2-text": "A extensão do piano se adapta ao arquivo MIDI e identifica as teclas brancas com nomes de notas.",
        "midi-card-3-title": "Cores por mão",
        "midi-card-3-text": "Notas da mão direita e da mão esquerda usam cores diferentes, incluindo tons mais escuros para notas em teclas pretas.",
        "midi-shot-label": "Visualização de reprodução",
        "midi-shot-text": "Use o player para inspecionar o tempo do MIDI antes de compartilhar ou exportar o resultado final.",
        "midi-secondary-caption": "MIDI carregado com extensão do piano e metadados.",
        "usage-kicker": "Uso recomendado",
        "usage-title": "Um fluxo simples para experimentos reproduzíveis.",
        "usage-1-title": "Prepare a entrada",
        "usage-1-text": "Use um PDF, PNG ou JPG nítido. Digitalizações mais limpas tendem a produzir melhores detecções.",
        "usage-2-title": "Selecione saídas",
        "usage-2-text": "Gere anotações primeiro para uma verificação rápida. Adicione áudio, MIDI ou vídeo quando necessário.",
        "usage-3-title": "Verifique as anotações",
        "usage-3-text": "Inspecione a imagem rotulada para conferir nomes de notas e interpretação estrutural.",
        "usage-4-title": "Revise a reprodução",
        "usage-4-text": "Use MIDI, MP3 e vídeo para avaliar a partitura reconstruída.",
        "cite-kicker": "Citação",
        "cite-title": "Citação",
        "cite-text": "Se usar o PyClef em trabalho acadêmico, cite o projeto. O artigo do MIRP estará disponível em breve.",
        "results-kicker": "Avaliação",
        "results-title": "Qualidade de detecção e qualidade de reconstrução são reportadas separadamente.",
        "results-lead": "O artigo reporta métricas de detecção de objetos e métricas funcionais de reconstrução de altura, pois mAP alto não implica necessariamente reconstrução musical correta.",
        "result-map": "A YOLOv11S alcançou 0,4126 mAP@[0,5:0,95] no DeepScoresV2 Dense.",
        "result-tra": "Com YOLOv11S, o MIRP elevou a TRA de 0,04 para 0,975.",
        "results-balance-kicker": "Comparação de modelos",
        "results-balance-title": "O MIRP reduz a diferença prática entre tamanhos de modelo.",
        "results-balance-text": "A YOLOv11L alcançou 0,51379 mAP, mas tanto a YOLOv11S quanto a YOLOv11L superaram 97% de TRA após o MIRP.",
        "table-kicker": "Resumo",
        "table-title": "Pontos de comparação reportados.",
        "metric-label": "Métrica",
        "pitch-rate": "Taxa de Reconstrução de Altura",
        "model-size": "Tamanho do modelo",
        "training-cost": "Custo de treinamento",
        "smaller": "Menor",
        "larger": "Maior",
        "lower": "Menor",
        "higher": "Maior",
        "footer-text": "Biblioteca Python para Reconhecimento Óptico de Partituras.",
        "lang-btn": "PT"
    }
};

let currentLang = localStorage.getItem("pyclef-lang") || "en";

function updateTexts() {
    document.documentElement.lang = currentLang;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        const value = content[currentLang]?.[key];
        if (value) el.innerHTML = value;
    });
    const langText = document.getElementById("lang-text");
    if (langText) langText.innerText = content[currentLang]["lang-btn"];
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("pyclef-theme", theme);
    const icon = document.getElementById("theme-icon");
    if (icon) icon.className = theme === "light" ? "fas fa-sun" : "fas fa-moon";
    document.querySelectorAll(".nav-logo, #main-logo").forEach((logo) => {
        logo.src = theme === "light" ? "imgs/logo_white.png" : "imgs/logo_black.png";
    });
}

document.getElementById("lang-switch")?.addEventListener("click", () => {
    currentLang = currentLang === "en" ? "pt" : "en";
    localStorage.setItem("pyclef-lang", currentLang);
    updateTexts();
});

document.getElementById("theme-switch")?.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    setTheme(isDark ? "light" : "dark");
});

function copyInstall() {
    const text = document.getElementById("install-command")?.innerText || "pip install pyclef";
    navigator.clipboard.writeText(text).then(() => {
        const icon = document.querySelector(".copy-btn i");
        if (!icon) return;
        icon.className = "fas fa-check";
        icon.style.color = "var(--accent)";
        setTimeout(() => {
            icon.className = "far fa-copy";
            icon.style.color = "";
        }, 1600);
    });
}

const modal = document.getElementById("imageModal");
const modalImg = document.getElementById("modalImg");

function openModal(img) {
    if (!modal || !modalImg) return;
    modalImg.src = img.src;
    modal.style.display = "flex";
    setTimeout(() => modal.classList.add("active"), 10);
    document.body.style.overflow = "hidden";
}

function closeModal() {
    if (!modal) return;
    modal.classList.remove("active");
    setTimeout(() => {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
    }, 250);
}

setTheme(localStorage.getItem("pyclef-theme") || "dark");
updateTexts();

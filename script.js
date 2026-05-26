const content = {
    en: {
        "nav-home": "Home",
        "nav-method": "Methodology",
        "nav-docs": "Docs",
        "nav-results": "Results",
        "hero-kicker": "Optical Music Recognition + MIRP",
        "hero-title": "Turn sheet music into structured sound.",
        "hero-lead": "PyClef combines YOLOv11S symbol detection with MIRP, a staff-referenced inference method that turns score geometry into musical pitch.",
        "hero-start": "Read the docs",
        "hero-method": "Explore MIRP",
        "metric-classes": "symbol classes",
        "metric-pitch": "TRA with MIRP",
        "intro-kicker": "Why PyClef exists",
        "intro-title": "A practical bridge between OMR research and usable musical output.",
        "intro-text": "The article shows that geometric detection metrics alone do not guarantee correct musical reconstruction. PyClef adds MIRP, a staff-referenced inference method that uses clefs and staff geometry to infer pitch from relative vertical displacement.",
        "card-neural-title": "Neural detection",
        "card-neural-text": "YOLOv11S detects 208 musical symbol classes from the DeepScoresV2 Dense dataset, reaching 0.4126 mAP@[0.5:0.95].",
        "card-mirp-title": "MIRP refinement",
        "card-mirp-text": "MIRP defines a staff reference note from the detected clef and infers remaining note heights from relative vertical displacement.",
        "pipeline-kicker": "Pipeline",
        "pipeline-title": "From image to music-ready artifacts.",
        "step-detect-title": "Detect",
        "step-detect-text": "Read PDF or image pages and locate staves, braces, clefs, notes, rests and accidentals.",
        "step-refine-title": "Refine",
        "step-refine-text": "Apply MIRP rules to organize detections into musical context instead of isolated boxes.",
        "step-reconstruct-title": "Reconstruct",
        "step-reconstruct-text": "Map vertical positions to pitch, align systems and prepare playback events.",
        "step-export-title": "Export",
        "step-export-text": "Generate annotated score pages, MIDI, MP3 and a synchronized video preview.",
        "app-kicker": "Desktop workflow",
        "app-title": "Designed for quick score experiments.",
        "app-text": "The desktop interface keeps the workflow direct: select the score, choose outputs, process, then inspect the generated files in a results folder.",
        "app-f1": "PDF and image input",
        "app-f2": "Annotated score output",
        "app-f3": "Audio, MIDI and synchronized video",
        "paper-kicker": "Research reference",
        "paper-title": "Read the article and methodology notes.",
        "paper-text": "The site includes a research-oriented methodology page, a documentation page for users, and a downloadable PDF of the current paper draft.",
        "paper-download": "Open paper PDF",
        "paper-method": "View methodology",
        "method-kicker": "Research methodology",
        "method-title": "MIRP: structural refinement for musical reconstruction.",
        "method-lead": "MIRP means Staff-Referenced Musical Inference Method. It uses the detected clef and staff structure to define a reference note, then infers the pitch of other notes from their vertical displacement.",
        "mirp-1-title": "Staff modeling",
        "mirp-1-text": "The detected staff provides y-top, y-bottom and the staff step used to measure adjacent musical positions.",
        "mirp-2-title": "Clef-aware pitch",
        "mirp-2-text": "The detected clef defines the reference note used by MIRP to interpret vertical displacement.",
        "mirp-3-title": "Functional reconstruction",
        "mirp-3-text": "With YOLOv11S, MIRP increased the Pitch Reconstruction Rate from 0.04 to 0.975.",
        "method-flow-kicker": "MIRP flow",
        "method-flow-title": "A deterministic layer after neural detection.",
        "flow-1-title": "Normalize detections",
        "flow-1-text": "Filter overlapping boxes and separate structural objects from musical symbols.",
        "flow-2-title": "Recover score structure",
        "flow-2-text": "Estimate the staff step as the distance between the lower and upper staff boundaries divided by eight.",
        "flow-3-title": "Convert geometry into music",
        "flow-3-text": "Compute the relative displacement between the reference note and each detected note center.",
        "flow-4-title": "Export auditable outputs",
        "flow-4-text": "Create annotated images and playback files so users can inspect both the recognition and the generated sound.",
        "article-kicker": "Article draft",
        "article-title": "PyClef: Optical Music Recognition with MIRP.",
        "article-text": "The paper reports YOLOv11S detection on DeepScoresV2 Dense and shows that MIRP raises pitch reconstruction from approximately 4% to 97.5%.",
        "docs-kicker": "Documentation",
        "docs-title": "Install, run and inspect PyClef outputs.",
        "docs-lead": "PyClef can be used through the desktop interface or called from Python. The generated results are grouped by score name for easier review.",
        "doc-install-title": "Installation",
        "doc-install-text": "Install the package from PyPI. The model can be downloaded automatically on first use.",
        "doc-launch-title": "Launch the app",
        "doc-launch-text": "Open the desktop workflow from Python or from the package entry point.",
        "doc-output-title": "Outputs",
        "doc-output-text": "Each run can create annotations, MP3 audio, MIDI and synchronized MP4 video.",
        "guide-kicker": "Guided interface tour",
        "guide-title": "Follow the desktop workflow visually.",
        "guide-lead": "These screenshots show the main parts of the PyClef interface, from the start screen to output review.",
        "guide-1-title": "Start from Home",
        "guide-1-text": "Use the Start button to move from the welcome screen into the score workspace.",
        "guide-2-title": "Open Scores",
        "guide-2-text": "The Scores page centralizes file selection, BPM, output options, logs and result buttons.",
        "guide-3-title": "Choose outputs",
        "guide-3-text": "After selecting a PDF or image, enable the outputs you need: annotations, MP3, MIDI or video.",
        "guide-4-title": "Track progress",
        "guide-4-text": "The progress bar and log panel show what PyClef is doing during detection, reconstruction and export.",
        "guide-5-title": "Open results",
        "guide-5-text": "When processing finishes, use the result buttons to open the folder or generated files.",
        "guide-6-title": "Learn about PyClef",
        "guide-6-text": "The About page summarizes the recognition, playback and review goals of the project.",
        "usage-kicker": "Recommended workflow",
        "usage-title": "A short path from score to reviewable result.",
        "usage-1-title": "Prepare the score",
        "usage-1-text": "Use a clear PDF, PNG or JPG. Higher quality images improve symbol detection.",
        "usage-2-title": "Choose outputs",
        "usage-2-text": "Generate only annotations for fast inspection, or include audio/MIDI/video when needed.",
        "usage-3-title": "Review annotations",
        "usage-3-text": "Use the labeled score image to verify note naming and structural interpretation.",
        "usage-4-title": "Inspect playback",
        "usage-4-text": "Use MIDI, MP3 and video to audit the musical reconstruction from different perspectives.",
        "cite-kicker": "Citation",
        "cite-title": "Cite PyClef",
        "cite-text": "If PyClef helps your work, cite the project and the MIRP paper.",
        "results-kicker": "Evaluation",
        "results-title": "Detection metrics are only the first half of OMR.",
        "results-lead": "PyClef reports detector performance, but emphasizes functional reconstruction: whether the symbols become correct musical pitch and usable playback artifacts.",
        "result-map": "The YOLOv11S detector reached 0.4126 mAP@[0.5:0.95] on DeepScoresV2 Dense.",
        "result-tra": "MIRP increased pitch reconstruction from 4% to 97.5% with YOLOv11S.",
        "results-balance-kicker": "Model trade-off",
        "results-balance-title": "The selected model balances detection quality and runtime cost.",
        "results-balance-text": "YOLOv11L reached 0.51379 mAP, but after MIRP both models exceeded 97% pitch reconstruction, reducing the practical gap between model sizes.",
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
        "footer-text": "Hybrid Optical Music Recognition research and tooling.",
        "lang-btn": "EN"
    },
    pt: {
        "nav-home": "Início",
        "nav-method": "Metodologia",
        "nav-docs": "Docs",
        "nav-results": "Resultados",
        "hero-kicker": "Reconhecimento Óptico Musical + MIRP",
        "hero-title": "Transforme partituras em som estruturado.",
        "hero-lead": "O PyClef combina detecção de símbolos com YOLOv11S e MIRP, um método de inferência por referência de pauta que transforma geometria da partitura em altura musical.",
        "hero-start": "Ler documentação",
        "hero-method": "Explorar MIRP",
        "metric-classes": "classes de símbolos",
        "metric-pitch": "TRA com MIRP",
        "intro-kicker": "Por que o PyClef existe",
        "intro-title": "Uma ponte prática entre pesquisa em OMR e saída musical utilizável.",
        "intro-text": "O artigo mostra que métricas geométricas de detecção, isoladamente, não garantem reconstrução musical correta. O PyClef adiciona o MIRP, um método de inferência por referência de pauta que usa claves e geometria da pauta para inferir a altura por deslocamento vertical relativo.",
        "card-neural-title": "Detecção neural",
        "card-neural-text": "YOLOv11S detecta 208 classes de símbolos musicais do DeepScoresV2 Dense, alcançando 0,4126 mAP@[0,5:0,95].",
        "card-mirp-title": "Refinamento MIRP",
        "card-mirp-text": "O MIRP define uma nota de referência a partir da clave detectada e infere as demais alturas pelo deslocamento vertical relativo.",
        "pipeline-kicker": "Pipeline",
        "pipeline-title": "Da imagem a artefatos musicais prontos.",
        "step-detect-title": "Detectar",
        "step-detect-text": "Lê páginas PDF ou imagens e localiza pautas, braces, claves, notas, pausas e acidentes.",
        "step-refine-title": "Refinar",
        "step-refine-text": "Aplica regras MIRP para organizar detecções em contexto musical, não como caixas isoladas.",
        "step-reconstruct-title": "Reconstruir",
        "step-reconstruct-text": "Mapeia posições verticais para alturas, alinha sistemas e prepara eventos de playback.",
        "step-export-title": "Exportar",
        "step-export-text": "Gera páginas anotadas, MIDI, MP3 e uma prévia em vídeo sincronizado.",
        "app-kicker": "Fluxo desktop",
        "app-title": "Projetado para experimentos rápidos com partituras.",
        "app-text": "A interface desktop mantém o fluxo direto: selecionar a partitura, escolher as saídas, processar e inspecionar os arquivos gerados.",
        "app-f1": "Entrada em PDF e imagem",
        "app-f2": "Partitura anotada",
        "app-f3": "Áudio, MIDI e vídeo sincronizado",
        "paper-kicker": "Referência de pesquisa",
        "paper-title": "Leia o artigo e as notas da metodologia.",
        "paper-text": "O site inclui uma página de metodologia voltada à pesquisa, uma documentação para usuários e um PDF baixável do rascunho atual do artigo.",
        "paper-download": "Abrir PDF do artigo",
        "paper-method": "Ver metodologia",
        "method-kicker": "Metodologia de pesquisa",
        "method-title": "MIRP: refinamento estrutural para reconstrução musical.",
        "method-lead": "MIRP significa Método de Inferência Musical por Referência de Pauta. Ele usa a clave detectada e a estrutura da pauta para definir uma nota de referência e inferir a altura das demais notas pelo deslocamento vertical.",
        "mirp-1-title": "Modelagem da pauta",
        "mirp-1-text": "A pauta detectada fornece y-top, y-bottom e o passo vertical usado para medir posições musicais adjacentes.",
        "mirp-2-title": "Altura sensível à clave",
        "mirp-2-text": "A clave detectada define a nota de referência usada pelo MIRP para interpretar o deslocamento vertical.",
        "mirp-3-title": "Reconstrução funcional",
        "mirp-3-text": "Com YOLOv11S, o MIRP elevou a Taxa de Reconstrução de Altura de 0,04 para 0,975.",
        "method-flow-kicker": "Fluxo MIRP",
        "method-flow-title": "Uma camada determinística após a detecção neural.",
        "flow-1-title": "Normalizar detecções",
        "flow-1-text": "Filtra caixas sobrepostas e separa objetos estruturais dos símbolos musicais.",
        "flow-2-title": "Recuperar estrutura",
        "flow-2-text": "Estima o passo da pauta pela distância entre os limites inferior e superior dividida por oito.",
        "flow-3-title": "Converter geometria em música",
        "flow-3-text": "Calcula o deslocamento relativo entre a nota de referência e o centro de cada nota detectada.",
        "flow-4-title": "Exportar saídas auditáveis",
        "flow-4-text": "Cria imagens anotadas e arquivos de reprodução para inspecionar o reconhecimento e o som gerado.",
        "article-kicker": "Rascunho do artigo",
        "article-title": "PyClef: Reconhecimento Óptico de Partituras com MIRP.",
        "article-text": "O artigo reporta detecção YOLOv11S no DeepScoresV2 Dense e mostra que o MIRP eleva a reconstrução de altura de aproximadamente 4% para 97,5%.",
        "docs-kicker": "Documentação",
        "docs-title": "Instale, execute e inspecione as saídas do PyClef.",
        "docs-lead": "O PyClef pode ser usado pela interface desktop ou chamado via Python. Os resultados gerados são agrupados pelo nome da partitura.",
        "doc-install-title": "Instalação",
        "doc-install-text": "Instale o pacote pelo PyPI. O modelo pode ser baixado automaticamente no primeiro uso.",
        "doc-launch-title": "Abrir o app",
        "doc-launch-text": "Abra o fluxo desktop pelo Python ou pelo ponto de entrada do pacote.",
        "doc-output-title": "Saídas",
        "doc-output-text": "Cada execução pode criar anotações, áudio MP3, MIDI e vídeo MP4 sincronizado.",
        "guide-kicker": "Tour guiado da interface",
        "guide-title": "Acompanhe visualmente o fluxo desktop.",
        "guide-lead": "Estas capturas mostram as principais partes da interface do PyClef, da tela inicial à revisão dos resultados.",
        "guide-1-title": "Comece pela Home",
        "guide-1-text": "Use o botão Iniciar para sair da tela de boas-vindas e abrir o ambiente de partituras.",
        "guide-2-title": "Abra Partituras",
        "guide-2-text": "A página de Partituras concentra seleção de arquivos, BPM, opções de saída, logs e botões de resultado.",
        "guide-3-title": "Escolha as saídas",
        "guide-3-text": "Depois de selecionar um PDF ou imagem, habilite as saídas necessárias: anotações, MP3, MIDI ou vídeo.",
        "guide-4-title": "Acompanhe o progresso",
        "guide-4-text": "A barra de progresso e o painel de logs mostram o que o PyClef faz durante detecção, reconstrução e exportação.",
        "guide-5-title": "Abra os resultados",
        "guide-5-text": "Quando o processamento terminar, use os botões de resultado para abrir a pasta ou os arquivos gerados.",
        "guide-6-title": "Conheça o PyClef",
        "guide-6-text": "A página Sobre resume os objetivos de reconhecimento, reprodução e revisão do projeto.",
        "usage-kicker": "Fluxo recomendado",
        "usage-title": "Um caminho curto da partitura ao resultado revisável.",
        "usage-1-title": "Prepare a partitura",
        "usage-1-text": "Use um PDF, PNG ou JPG nítido. Imagens melhores aumentam a detecção de símbolos.",
        "usage-2-title": "Escolha as saídas",
        "usage-2-text": "Gere apenas anotações para inspeção rápida, ou inclua áudio/MIDI/vídeo quando necessário.",
        "usage-3-title": "Revise as anotações",
        "usage-3-text": "Use a imagem rotulada para verificar nomes de notas e interpretação estrutural.",
        "usage-4-title": "Inspecione o playback",
        "usage-4-text": "Use MIDI, MP3 e vídeo para auditar a reconstrução musical por diferentes perspectivas.",
        "cite-kicker": "Citação",
        "cite-title": "Cite o PyClef",
        "cite-text": "Se o PyClef ajudar no seu trabalho, cite o projeto e o artigo do MIRP.",
        "results-kicker": "Avaliação",
        "results-title": "Métricas de detecção são apenas metade do OMR.",
        "results-lead": "O PyClef reporta o desempenho do detector, mas enfatiza a reconstrução funcional: se os símbolos viram altura musical correta e artefatos utilizáveis.",
        "result-map": "O detector YOLOv11S alcançou 0,4126 mAP@[0,5:0,95] no DeepScoresV2 Dense.",
        "result-tra": "O MIRP elevou a reconstrução de altura de 4% para 97,5% com YOLOv11S.",
        "results-balance-kicker": "Compromisso do modelo",
        "results-balance-title": "O modelo selecionado equilibra qualidade de detecção e custo de execução.",
        "results-balance-text": "A YOLOv11L alcançou 0,51379 mAP, mas após o MIRP ambos os modelos superaram 97% de reconstrução de altura, reduzindo a diferença prática entre tamanhos de modelo.",
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
        "footer-text": "Pesquisa e ferramenta híbrida de Reconhecimento Óptico Musical.",
        "lang-btn": "PT"
    }
};

let currentLang = localStorage.getItem("pyclef-lang") || "en";

function updateTexts() {
    document.documentElement.lang = currentLang;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (content[currentLang] && content[currentLang][key]) {
            el.innerHTML = content[currentLang][key];
        }
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

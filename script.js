const content = {
    en: {
        "intro-h2": "Introduction",
        "intro-p1": "PyClef is a hybrid approach for Optical Music Recognition (OMR), combining deep learning-based object detection with explicit structural modeling. The system uses the YOLOv11s architecture to identify 208 classes of musical symbols in the DeepScoresV2 (Dense) dataset, characterized by high symbol density and strong class imbalance.",
        "intro-p2": "The model achieved mAP=0.4123 on the validation set. To overcome limitations of purely geometric metrics, a deterministic heuristic module was incorporated to enforce structural consistency in symbolic score reconstruction. Functional evaluation showed that correct musical pitch reconstruction improved from approximately 8% to 94% after explicit staff modeling.",
        "ai-h3": "Neural Engine",
        "ai-detail": "YOLOv11s model fine-tuned for detecting 208 musical symbol classes in high-density scores. Achieved mAP=0.4123 on DeepScoresV2 validation set.",
        "gui-h3": "Interface & UX",
        "gui-detail": "An intuitive experience designed for musicians and developers.",
        "gui-f1": "Minimalist Design",
        "gui-f2": "Direct Workflow",
        "gui-f3": "Real-time Feedback",
        "gui-img-1": "Main Dashboard",
        "gui-img-2": "Native Dark Mode",
        "dsp-h3": "Structural Modeling",
        "dsp-detail": "Deterministic heuristic module for structural consistency in score reconstruction. Improves pitch accuracy from 8% to 94%.",
        "perf-h3": "Performance",
        "perf-detail": "Hybrid approach combining deep learning with domain-specific structural knowledge for robust OMR in dense scenarios.",
        "comp-h1": "YOLOv11s vs YOLOv11l Comparison",
        "comp-p": "Comparative analysis of YOLOv11s (used in PyClef) and YOLOv11l variants, based on the scientific article, evaluating the impact of model size on performance and computational cost.",
        "hero-h1": "The Future of <span>Sheet Music</span> Digitization.",
        "hero-p": "A high-performance OMR pipeline merging deep learning with DSP.",
        "tutorial-h1": "How to Use PyClef",
        "tutorial-p": "A step-by-step guide to get started with PyClef for optical music recognition.",
        "step1-h2": "1. Installation",
        "step1-p": "Install PyClef using pip:",
        "step2-h2": "2. Import the Library",
        "step2-p": "Import PyClef in your Python script:",
        "step3-h2": "3. Load Your Sheet Music",
        "step3-p": "Load an image of sheet music:",
        "step4-h2": "4. Process the Image",
        "step4-p": "Run the OMR pipeline:",
        "step5-h2": "5. Export Results",
        "step5-p": "Save the recognized music data:",
        "analysis-h2": "Analysis",
        "analysis-p1": "The YOLOv11L variant shows better performance in terms of mAP@[0.5:0.95] (0.5138 vs 0.4126), indicating higher detection precision. However, this comes with a higher computational cost, including larger model size and longer training time. YOLOv11s was chosen for PyClef due to the balance between performance and efficiency, especially in high-density score scenarios.",
        "analysis-p2": "The Height Reconstruction Rate (TRA) remains low for both variants without the structural heuristic, highlighting the importance of the hybrid module to improve musical reconstruction.",
        "lang-btn": "EN"
    },
    pt: {
        "intro-h2": "Introdução",
        "intro-p1": "O PyClef é uma abordagem híbrida para Reconhecimento Óptico de Partituras Musicais (OMR), integrando detecção de objetos baseada em aprendizado profundo com modelagem estrutural explícita. O sistema utiliza a arquitetura YOLOv11s para identificar 208 classes de símbolos musicais no dataset DeepScoresV2 (Dense), caracterizado por elevada densidade simbólica e forte desbalanceamento entre classes.",
        "intro-p2": "O modelo alcançou mAP=0.4123 no conjunto de validação. Para superar limitações de métricas puramente geométricas, foi incorporado um módulo heurístico determinístico que impõe coerência estrutural à reconstrução simbólica da partitura. A avaliação funcional demonstrou que a reconstrução correta de altura musical evoluiu de aproximadamente 8% para 94% após a modelagem explícita da pauta musical.",
        "ai-h3": "Motor Neural",
        "ai-detail": "Modelo YOLOv11s ajustado para detectar 208 classes de símbolos musicais em partituras de alta densidade. Alcançou mAP=0.4123 no conjunto de validação DeepScoresV2.",
        "gui-h3": "Interface & UX",
        "gui-detail": "Uma experiência intuitiva projetada para músicos e desenvolvedores.",
        "gui-f1": "Design Minimalista",
        "gui-f2": "Fluxo de Trabalho Direto",
        "gui-f3": "Feedback em Tempo Real",
        "gui-img-1": "Painel Principal",
        "gui-img-2": "Modo Escuro Nativo",
        "dsp-h3": "Modelagem Estrutural",
        "dsp-detail": "Módulo heurístico determinístico para coerência estrutural na reconstrução da partitura. Melhora a precisão de altura de 8% para 94%.",
        "perf-h3": "Performance",
        "perf-detail": "Abordagem híbrida combinando aprendizado profundo com conhecimento estrutural específico do domínio para OMR robusto em cenários densos.",
        "comp-h1": "Comparação entre YOLOv11s e YOLOv11l",
        "comp-p": "Análise comparativa das variantes YOLOv11s (usada no PyClef) e YOLOv11l, baseada no artigo científico, avaliando impacto do tamanho do modelo em desempenho e custo computacional.",
        "hero-h1": "O Futuro da <span>Digitalização de Partituras</span>.",
        "hero-p": "Um pipeline OMR de alta performance unindo deep learning e DSP.",
        "tutorial-h1": "Como Usar o PyClef",
        "tutorial-p": "Um guia passo a passo para começar a usar o PyClef no reconhecimento óptico de partituras.",
        "step1-h2": "1. Instalação",
        "step1-p": "Instale o PyClef usando pip:",
        "step2-h2": "2. Importe a Biblioteca",
        "step2-p": "Importe o PyClef em seu script Python:",
        "step3-h2": "3. Carregue sua Partitura",
        "step3-p": "Carregue uma imagem de partitura:",
        "step4-h2": "4. Processe a Imagem",
        "step4-p": "Execute o pipeline OMR:",
        "step5-h2": "5. Exporte os Resultados",
        "step5-p": "Salve os dados musicais reconhecidos:",
        "analysis-h2": "Análise",
        "analysis-p1": "A variante YOLOv11L apresenta melhor desempenho em termos de mAP@[0.5:0.95] (0.5138 vs 0.4126), indicando maior precisão na detecção. No entanto, isso vem com um custo computacional maior, incluindo tamanho de modelo maior e tempo de treinamento mais longo. A YOLOv11s foi escolhida para o PyClef devido ao equilíbrio entre desempenho e eficiência, especialmente em cenários de partitura de alta densidade.",
        "analysis-p2": "A Taxa de Reconstrução de Altura (TRA) permanece baixa para ambas as variantes sem a heurística estrutural, destacando a importância do módulo híbrido para melhorar a reconstrução musical.",
        "lang-btn": "PT"
    }
};

let currentLang = 'en';

// Função unificada para atualizar textos
function updateTexts() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (content[currentLang][key]) el.innerHTML = content[currentLang][key];
    });
    document.getElementById('lang-text').innerText = content[currentLang]["lang-btn"];
}

// Troca de Idioma
document.getElementById('lang-switch').addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'pt' : 'en';
    updateTexts();
});

// Troca de Tema
document.getElementById('theme-switch').addEventListener('click', () => {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    document.getElementById('theme-icon').className = newTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    const logo = document.getElementById('main-logo');
    if (logo) {
        logo.src = newTheme === 'light' ? 'imgs/logo_white.png' : 'imgs/logo_black.png';
    }
});

function toggleMenu(header) {
    const item = header.parentElement;
    const isActive = item.classList.contains('active');
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    if (!isActive) item.classList.add('active');
}

function copyInstall() {
    const text = document.getElementById('install-command').innerText;
    navigator.clipboard.writeText(text).then(() => {
        const icon = document.querySelector('.copy-btn i');
        icon.className = 'fas fa-check';
        icon.style.color = 'var(--accent)';
        setTimeout(() => {
            icon.className = 'far fa-copy';
            icon.style.color = '';
        }, 2000);
    });
}

const modal = document.getElementById("imageModal");
const modalImg = document.getElementById("modalImg");

function openModal(img) {
    modalImg.src = img.src;
    modal.style.display = "flex";
    setTimeout(() => modal.classList.add('active'), 10);
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.classList.remove('active');
    setTimeout(() => {
        modal.style.display = "none";
        document.body.style.overflow = 'auto';
    }, 300);
}

// Call updateTexts on load
updateTexts();

// Inicializar textos ao carregar
window.onload = updateTexts;
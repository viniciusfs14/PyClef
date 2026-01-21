const content = {
    en: {
        "status": "Research Phase: YOLO11m Pure Inference",
        "hero-h1": "The Future of <span>Sheet Music</span> Digitization.",
        "hero-p": "A high-performance OMR pipeline merging deep learning with digital signal processing principles.",
        "ai-h3": "Neural Engine",
        "ai-p": "Fine-tuned YOLO11m model optimized for sub-millimeter detection.",
        "dsp-h3": "Signal Synthesis (DSP)",
        "dsp-p": "Mathematical mapping of spatial coordinates into discrete Hz frequencies.",
        "lang-btn": "EN",
        "status-h3": "Project Status",
        "status-p": "Neural Training: "
    },
    pt: {
        "status": "Fase de Pesquisa: Inferência Bruta YOLO11m",
        "hero-h1": "O Futuro da Digitalização de <span>Partituras</span>.",
        "hero-p": "Um pipeline OMR de alta performance que une deep learning com princípios de processamento de sinais digitais.",
        "ai-h3": "Motor Neural",
        "ai-p": "Modelo YOLO11m ajustado para detecção submilimétrica.",
        "dsp-h3": "Síntese de Sinais (DSP)",
        "dsp-p": "Mapeamento matemático de coordenadas espaciais em frequências Hz.",
        "lang-btn": "PT",
        "status-h3": "Status do Projeto",
        "status-p": "Treinamento Neural: "
    }
};

let currentLang = 'en';

// Alternar Idioma
document.getElementById('lang-switch').addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'pt' : 'en';
    document.documentElement.setAttribute('data-lang', currentLang);
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.innerHTML = content[currentLang][key];
    });

    document.getElementById('lang-text').innerText = content[currentLang]["lang-btn"];
});

// Alternar Tema e Logo
document.getElementById('theme-switch').addEventListener('click', () => {
    const html = document.documentElement;
    const logo = document.getElementById('main-logo');
    const themeIcon = document.getElementById('theme-icon');
    
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);

    // Lógica de troca de logo por tema
    if (newTheme === 'light') {
        logo.src = 'imgs/logo_white.png'; // Sua logo para fundo claro
        themeIcon.className = 'fas fa-sun';
    } else {
        logo.src = 'imgs/logo_black.png'; // Sua logo para fundo escuro
        themeIcon.className = 'fas fa-moon';
    }
});


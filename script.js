const content = {
    en: {
        "hero-h1": "The Future of <span>Sheet Music</span> Digitization.",
        "hero-p": "A high-performance OMR pipeline merging deep learning with digital signal processing principles.",
        "ai-h3": "Neural Engine",
        "ai-detail": "Fine-tuned YOLO11m model optimized for sub-millimeter detection of musical symbols, recognizing clefs, notes, and rests with high precision.",
        "dsp-h3": "Signal Synthesis (DSP)",
        "dsp-detail": "Mathematical mapping of spatial coordinates into discrete Hz frequencies, converting visual notation into audible digital signals.",
        "status-h3": "Research & Status",
        "status-p": "PyClef is currently in the Research Phase, focusing on pure inference and model refinement for complex sheet music layouts.",
        "lang-btn": "EN"
    },
    pt: {
        "hero-h1": "O Futuro da Digitalização de <span>Partituras</span>.",
        "hero-p": "Um pipeline OMR de alta performance que une deep learning com princípios de processamento de sinais digitais.",
        "ai-h3": "Motor Neural",
        "ai-detail": "Modelo YOLO11m ajustado para detecção submilimétrica de símbolos musicais, reconhecendo claves, notas e pausas com alta precisão.",
        "dsp-h3": "Síntese de Sinais (DSP)",
        "dsp-detail": "Mapeamento matemático de coordenadas espaciais em frequências Hz discretas, convertendo notação visual em sinais digitais audíveis.",
        "status-h3": "Pesquisa & Status",
        "status-p": "O PyClef está atualmente na Fase de Pesquisa, focando em inferência pura e refinamento do modelo para layouts complexos.",
        "lang-btn": "PT"
    }
};

let currentLang = 'en';

// Alternar Idioma
document.getElementById('lang-switch').addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'pt' : 'en';
    document.documentElement.setAttribute('data-lang', currentLang);
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (content[currentLang][key]) {
            el.innerHTML = content[currentLang][key];
        }
    });
    document.getElementById('lang-text').innerText = content[currentLang]["lang-btn"];
});

// Alternar Tema
document.getElementById('theme-switch').addEventListener('click', () => {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    const themeIcon = document.getElementById('theme-icon');
    const logo = document.getElementById('main-logo');
    
    html.setAttribute('data-theme', newTheme);
    themeIcon.className = newTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    logo.src = newTheme === 'light' ? 'imgs/logo_white.png' : 'imgs/logo_black.png';
});

// Controle dos Submenus
function toggleMenu(header) {
    const item = header.parentElement;
    const isActive = item.classList.contains('active');

    // Fecha outros antes de abrir o novo
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));

    if (!isActive) {
        item.classList.add('active');
    }
}
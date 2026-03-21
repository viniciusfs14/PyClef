const content = {
    en: {
        "hero-h1": "The Future of <span>Sheet Music</span> Digitization.",
        "hero-p": "A high-performance OMR pipeline merging deep learning with DSP.",
        "ai-h3": "Neural Engine",
        "ai-detail": "Fine-tuned YOLO11m model optimized for sub-millimeter detection.",
        "gui-h3": "Interface & UX",
        "gui-detail": "Modern interface developed in PySide6 for real-time interaction.",
        "dsp-h3": "Signal Synthesis",
        "dsp-detail": "Mapping spatial coordinates into discrete Hz frequencies.",
        "lang-btn": "EN"
    },
    pt: {
        "hero-h1": "O Futuro da Digitalização de <span>Partituras</span>.",
        "hero-p": "Um pipeline OMR de alta performance unindo deep learning e DSP.",
        "ai-h3": "Motor Neural",
        "ai-detail": "Modelo YOLO11m ajustado para detecção submilimétrica.",
        "gui-h3": "Interface & UX",
        "gui-detail": "Interface moderna em PySide6 para interação em tempo real.",
        "dsp-h3": "Síntese de Sinais",
        "dsp-detail": "Mapeamento de coordenadas espaciais em frequências Hz.",
        "lang-btn": "PT"
    }
};

let currentLang = 'en';

// Troca de Idioma
document.getElementById('lang-switch').addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'pt' : 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (content[currentLang][key]) el.innerHTML = content[currentLang][key];
    });
    document.getElementById('lang-text').innerText = content[currentLang]["lang-btn"];
});

// Troca de Tema
document.getElementById('theme-switch').addEventListener('click', () => {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    document.getElementById('theme-icon').className = newTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    document.getElementById('main-logo').src = newTheme === 'light' ? 'imgs/logo_white.png' : 'imgs/logo_black.png';
});

// Menu Expansível
function toggleMenu(header) {
    const item = header.parentElement;
    const isActive = item.classList.contains('active');
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    if (!isActive) item.classList.add('active');
}

// Lógica do Modal de Zoom (Reforçada para Mobile)
const modal = document.getElementById("imageModal");
const modalImg = document.getElementById("modalImg");
const captionText = document.getElementById("caption");

function openModal(img) {
    modalImg.src = img.src;
    if (captionText) captionText.innerHTML = img.alt;
    
    modal.style.display = "flex";
    setTimeout(() => {
        modal.classList.add('active');
    }, 10);
    
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.classList.remove('active');
    setTimeout(() => {
        modal.style.display = "none";
        document.body.style.overflow = 'auto';
    }, 300);
}

// Fechar com tecla Esc
document.addEventListener('keydown', (e) => {
    if (e.key === "Escape") closeModal();
});
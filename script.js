const content = {
    en: {
        "hero-h1": "The Future of <span>Sheet Music</span> Digitization.",
        "hero-p": "A high-performance OMR pipeline merging AI with DSP.",
        "ai-h3": "Neural Engine", "ai-detail": "YOLO11m for sub-millimeter detection.",
        "gui-h3": "Interface & UX", "gui-detail": "Modern PySide6 interface.",
        "dsp-h3": "Signal Synthesis", "dsp-detail": "Spatial mapping to Hz.",
        "lang-btn": "EN"
    },
    pt: {
        "hero-h1": "O Futuro da Digitalização de <span>Partituras</span>.",
        "hero-p": "Um pipeline OMR que une IA com processamento de sinais.",
        "ai-h3": "Motor Neural", "ai-detail": "YOLO11m para detecção submilimétrica.",
        "gui-h3": "Interface & UX", "gui-detail": "Interface moderna em PySide6.",
        "dsp-h3": "Síntese de Sinais", "dsp-detail": "Mapeamento espacial para Hz.",
        "lang-btn": "PT"
    }
};

let currentLang = 'en';

document.getElementById('lang-switch').addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'pt' : 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (content[currentLang][key]) el.innerHTML = content[currentLang][key];
    });
    document.getElementById('lang-text').innerText = content[currentLang]["lang-btn"];
});

document.getElementById('theme-switch').addEventListener('click', () => {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    document.getElementById('theme-icon').className = newTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    document.getElementById('main-logo').src = newTheme === 'light' ? 'imgs/logo_black.png' : 'imgs/logo_white.png';
});

function toggleMenu(header) {
    const item = header.parentElement;
    const isActive = item.classList.contains('active');
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    if (!isActive) item.classList.add('active');
}

function openModal(img) {
    const modal = document.getElementById("imageModal");
    const modalImg = document.getElementById("modalImg");
    modal.classList.add('active');
    modalImg.src = img.src;
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById("imageModal").classList.remove('active');
    document.body.style.overflow = 'auto';
}
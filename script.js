const content = {
    en: {
        "hero-h1": "The Future of <span>Sheet Music</span> Digitization.",
        "hero-p": "A high-performance OMR pipeline merging deep learning with DSP.",
        "ai-h3": "Neural Engine",
        "ai-detail": "Fine-tuned YOLO11m model optimized for sub-millimeter detection.",
        "gui-h3": "Interface & UX",
        "gui-detail": "An intuitive experience designed for musicians and developers. Simplicity in every click.",
        "gui-f1": "Minimalist Design",
        "gui-f2": "Direct Workflow",
        "gui-f3": "Real-time Feedback",
        "gui-img-1": "Main Dashboard",
        "gui-img-2": "Native Dark Mode",
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
        "gui-detail": "Uma experiência intuitiva projetada para músicos e desenvolvedores. Simplicidade em cada clique.",
        "gui-f1": "Design Minimalista",
        "gui-f2": "Fluxo de Trabalho Direto",
        "gui-f3": "Feedback em Tempo Real",
        "gui-img-1": "Painel Principal",
        "gui-img-2": "Modo Escuro Nativo",
        "dsp-h3": "Síntese de Sinais",
        "dsp-detail": "Mapeamento de coordenadas espaciais em frequências Hz.",
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
    document.getElementById('main-logo').src = newTheme === 'light' ? 'imgs/logo_white.png' : 'imgs/logo_black.png';
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

// Força a atualização dos textos conforme o currentLang ao carregar a página
document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (content[currentLang][key]) el.innerHTML = content[currentLang][key];
});
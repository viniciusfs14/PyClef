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

window.addEventListener('DOMContentLoaded', () => {
    const progressFill = document.querySelector('.progress-fill');
    // Pegamos o valor original definido no HTML
    const targetProgress = getComputedStyle(progressFill).getPropertyValue('--progress');
    
    // Resetamos para 0 e depois animamos até o valor real
    progressFill.style.setProperty('--progress', '0');
    
    setTimeout(() => {
        progressFill.style.transition = "width 2s cubic-bezier(0.4, 0, 0.2, 1)";
        progressFill.style.setProperty('--progress', targetProgress);
    }, 500);
});

const terminalLogs = {
    en: [
        "> Initializing PyClef Engine...",
        "> Loading YOLO11m weights: best.pt",
        "> Model loaded successfully (Inference: 14.2ms)",
        "> Image acquisition: sheet_04.png",
        "> Detecting staff lines... FOUND (5 lines identified)",
        "> Running Pure Inference (No heuristics)...",
        "> Note detected: C4 at (x: 452, y: 128) | Conf: 0.94",
        "> Note detected: E4 at (x: 490, y: 110) | Conf: 0.91",
        "> Applying DSP Frequency Mapping...",
        "> C4 -> 261.63 Hz | E4 -> 329.63 Hz",
        "> Exporting audio: results/output.mp3",
        "> Process finished successfully."
    ],
    pt: [
        "> Inicializando Motor PyClef...",
        "> Carregando pesos YOLO11m: best.pt",
        "> Modelo carregado com sucesso (Inferência: 14.2ms)",
        "> Aquisição de imagem: partitura_04.png",
        "> Detectando pautas... ENCONTRADO (5 linhas identificadas)",
        "> Executando Inferência Pura (Sem heurísticas)...",
        "> Nota detectada: Do4 em (x: 452, y: 128) | Conf: 0.94",
        "> Nota detectada: Mi4 em (x: 490, y: 110) | Conf: 0.91",
        "> Aplicando Mapeamento de Frequência DSP...",
        "> Do4 -> 261.63 Hz | Mi4 -> 329.63 Hz",
        "> Exportando áudio: resultados/saida.mp3",
        "> Processo finalizado com sucesso."
    ]
};

function startTerminal() {
    const body = document.getElementById('terminal-content');
    if (!body) return;
    
    body.innerHTML = "";
    let i = 0;
    const logs = terminalLogs[currentLang] || terminalLogs.en;

    function addLog() {
        if (i < logs.length) {
            const p = document.createElement('p');
            p.innerText = logs[i];
            
            // Estilização dinâmica baseada no conteúdo do log
            if (logs[i].includes('successfully') || logs[i].includes('sucesso')) p.className = 'log-success';
            if (logs[i].includes('YOLO11m')) p.className = 'log-info';
            
            body.appendChild(p);
            body.scrollTop = body.scrollHeight; // Auto-scroll para o final
            i++;
            setTimeout(addLog, Math.random() * 800 + 200); // Tempo aleatório para parecer real
        }
    }
    addLog();
}

// Inicia o terminal ao carregar a página
window.addEventListener('DOMContentLoaded', startTerminal);
// Reinicia o terminal se o idioma mudar (opcional)
document.getElementById('lang-switch').addEventListener('click', () => {
    setTimeout(startTerminal, 500);
});
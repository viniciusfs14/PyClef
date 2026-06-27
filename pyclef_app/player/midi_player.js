const DEFAULT_SOUNDFONT_URL = "https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/GeneralUser-GS.sf2";

const NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
const BLACK_CLASSES = new Set([1, 3, 6, 8, 10]);
const MIN_WHITE_WIDTH = 16;
const MAX_WHITE_WIDTH = 84;
const MIN_BLACK_WIDTH = 10;
const MAX_BLACK_WIDTH = 46;
const PIXELS_PER_SECOND = 135;
const MAX_RENDERED_NOTES = 6000;
const VISIBILITY_PADDING_SECONDS = 0.35;
const TIME_LABEL_INTERVAL_MS = 90;

const state = {
    midiBuffer: null,
    soundFontBuffer: null,
    summary: null,
    audioContext: null,
    synth: null,
    node: null,
    isPlaying: false,
    startedAt: 0,
    audioStartedAt: 0,
    animationFrame: null,
    keyElements: new Map(),
    noteElements: [],
    visibleNoteIndices: new Set(),
    activeKeyMidis: new Map(),
    minMidi: 48,
    maxMidi: 84,
    whiteLefts: new Map(),
    pendingPlay: null,
    maxNoteDuration: 0,
    lastTimeLabelAt: 0,
};

const els = {
    selectMidi: document.getElementById("select-midi"),
    midiInput: document.getElementById("midi-file"),
    loadSoundFont: document.getElementById("load-soundfont"),
    playButton: document.getElementById("play-button"),
    stopButton: document.getElementById("stop-button"),
    statusDot: document.getElementById("status-dot"),
    statusText: document.getElementById("status-text"),
    midiName: document.getElementById("midi-name"),
    noteCount: document.getElementById("note-count"),
    duration: document.getElementById("duration"),
    volume: document.getElementById("volume-slider"),
    waterfall: document.getElementById("waterfall"),
    noteLayer: document.getElementById("note-layer"),
    emptyState: document.getElementById("empty-state"),
    keyboard: document.getElementById("keyboard"),
    progressFill: document.getElementById("progress-fill"),
    timeLabel: document.getElementById("time-label"),
};

function pitchClass(midi) {
    return ((midi % 12) + 12) % 12;
}

function isBlack(midi) {
    return BLACK_CLASSES.has(pitchClass(midi));
}

function midiName(midi) {
    return `${NOTE_NAMES[pitchClass(midi)]}${Math.floor(midi / 12) - 1}`;
}

function formatTime(seconds) {
    if (!Number.isFinite(seconds) || seconds <= 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = String(Math.floor(seconds % 60)).padStart(2, "0");
    return `${mins}:${secs}`;
}

function setStatus(text, playing = false) {
    els.statusText.textContent = text;
    els.statusDot.classList.toggle("playing", playing);
}

function updateButtons() {
    els.playButton.disabled = !(state.midiBuffer && state.soundFontBuffer) || state.isPlaying;
    els.stopButton.disabled = !state.isPlaying;
}

function playbackTime() {
    if (!state.isPlaying) return 0;
    if (state.audioContext && state.audioStartedAt) {
        return Math.max(0, state.audioContext.currentTime - state.audioStartedAt);
    }
    return Math.max(0, (performance.now() - state.startedAt) / 1000);
}

function noteHand(trackIndex, midi) {
    if (trackIndex > 0) return "left";
    return midi < 60 ? "left" : "right";
}

function parseMidi(buffer) {
    if (!window.Midi) {
        throw new Error("Tone MIDI parser did not load.");
    }

    const midi = new Midi(buffer.slice(0));
    const notes = [];
    midi.tracks.forEach((track, trackIndex) => {
        const trackNotes = (track.notes || []).filter((note) => (
            Number.isFinite(note.time) && Number.isFinite(note.midi)
        ));
        trackNotes.forEach((note) => {
            notes.push({
                midi: note.midi,
                name: note.name || midiName(note.midi),
                time: Math.max(0, note.time || 0),
                duration: Math.max(0.06, note.duration || 0.08),
                velocity: note.velocity || 0.75,
                hand: noteHand(trackIndex, note.midi),
            });
        });
    });

    notes.sort((a, b) => a.time - b.time || a.midi - b.midi);
    const duration = Math.max(
        midi.duration || 0,
        ...notes.map((note) => note.time + note.duration),
        0
    );
    return {
        notes,
        duration,
        trackCount: midi.tracks.length,
        noteCount: notes.length,
    };
}

function clampMidiRange(notes) {
    if (!notes.length) {
        state.minMidi = 48;
        state.maxMidi = 84;
        return;
    }

    let min = Math.min(...notes.map((note) => note.midi));
    let max = Math.max(...notes.map((note) => note.midi));
    if (max - min < 24) {
        const center = Math.round((min + max) / 2);
        min = center - 12;
        max = center + 12;
    }
    state.minMidi = Math.max(21, min - pitchClass(min));
    state.maxMidi = Math.min(108, max + (11 - pitchClass(max)));
}

function buildKeyboard() {
    els.keyboard.innerHTML = "";
    state.keyElements.clear();
    state.whiteLefts.clear();

    const visibleWidth = Math.max(
        els.waterfall.clientWidth || 0,
        els.keyboard.clientWidth || 0,
        window.innerWidth - 44,
        640
    );
    const whiteCount = Array.from(
        { length: state.maxMidi - state.minMidi + 1 },
        (_, index) => state.minMidi + index
    ).filter((midi) => !isBlack(midi)).length;
    const fittedWhiteWidth = visibleWidth / Math.max(1, whiteCount);
    const whiteWidth = Math.max(MIN_WHITE_WIDTH, Math.min(MAX_WHITE_WIDTH, fittedWhiteWidth));
    const blackWidth = Math.max(MIN_BLACK_WIDTH, Math.min(MAX_BLACK_WIDTH, whiteWidth * 0.62));

    let whiteIndex = 0;
    for (let midi = state.minMidi; midi <= state.maxMidi; midi += 1) {
        if (isBlack(midi)) continue;
        const left = whiteIndex * whiteWidth;
        state.whiteLefts.set(midi, left);

        const key = document.createElement("div");
        key.className = "key white";
        key.style.left = `${left}px`;
        key.style.width = `${whiteWidth}px`;
        key.textContent = midiName(midi);
        els.keyboard.appendChild(key);
        state.keyElements.set(midi, key);
        whiteIndex += 1;
    }

    for (let midi = state.minMidi; midi <= state.maxMidi; midi += 1) {
        if (!isBlack(midi)) continue;
        let previousWhite = midi - 1;
        while (previousWhite >= state.minMidi && isBlack(previousWhite)) {
            previousWhite -= 1;
        }
        const baseLeft = state.whiteLefts.get(previousWhite);
        if (baseLeft === undefined) continue;

        const key = document.createElement("div");
        key.className = "key black";
        key.style.left = `${baseLeft + whiteWidth - blackWidth / 2}px`;
        key.style.width = `${blackWidth}px`;
        els.keyboard.appendChild(key);
        state.keyElements.set(midi, key);
    }

    const keyboardWidth = Math.max(visibleWidth, whiteIndex * whiteWidth);
    els.waterfall.style.minWidth = `${keyboardWidth}px`;
    els.keyboard.style.minWidth = `${keyboardWidth}px`;
    els.noteLayer.style.minWidth = `${keyboardWidth}px`;
    state.whiteWidth = whiteWidth;
    state.blackWidth = blackWidth;
}

function keyLeft(midi) {
    if (isBlack(midi)) {
        let previousWhite = midi - 1;
        while (previousWhite >= state.minMidi && isBlack(previousWhite)) {
            previousWhite -= 1;
        }
        const left = state.whiteLefts.get(previousWhite);
        return left === undefined ? 0 : left + state.whiteWidth - state.blackWidth / 2;
    }
    return state.whiteLefts.get(midi) ?? 0;
}

function lowerBoundNoteStart(target) {
    let low = 0;
    let high = state.noteElements.length;
    while (low < high) {
        const middle = (low + high) >> 1;
        if (state.noteElements[middle].note.time < target) {
            low = middle + 1;
        } else {
            high = middle;
        }
    }
    return low;
}

function upperBoundNoteStart(target) {
    let low = 0;
    let high = state.noteElements.length;
    while (low < high) {
        const middle = (low + high) >> 1;
        if (state.noteElements[middle].note.time <= target) {
            low = middle + 1;
        } else {
            high = middle;
        }
    }
    return low;
}

function renderNotes() {
    els.noteLayer.innerHTML = "";
    state.noteElements = [];
    state.visibleNoteIndices.clear();
    state.maxNoteDuration = 0;
    if (!state.summary?.notes?.length) {
        els.emptyState.style.display = "grid";
        return;
    }

    els.emptyState.style.display = "none";
    const fragment = document.createDocumentFragment();
    state.summary.notes.slice(0, MAX_RENDERED_NOTES).forEach((note, index) => {
        const noteHeight = Math.max(14, note.duration * PIXELS_PER_SECOND);
        state.maxNoteDuration = Math.max(state.maxNoteDuration, note.duration);
        const noteEl = document.createElement("span");
        noteEl.className = `fall-note ${note.hand} ${isBlack(note.midi) ? "black" : "white"}`;
        noteEl.style.left = `${keyLeft(note.midi)}px`;
        noteEl.style.width = `${isBlack(note.midi) ? state.blackWidth : state.whiteWidth}px`;
        noteEl.style.height = `${noteHeight}px`;
        noteEl.style.transform = "translate3d(0, -9999px, 0)";
        noteEl.title = note.name || midiName(note.midi);
        fragment.appendChild(noteEl);
        state.noteElements.push({
            element: noteEl,
            note,
            index,
            height: noteHeight,
            endTime: note.time + note.duration,
        });
    });
    els.noteLayer.appendChild(fragment);
}

function refreshLayout() {
    buildKeyboard();
    if (state.summary) {
        renderNotes();
        if (!state.isPlaying) resetVisuals();
    }
}

function resetVisuals() {
    state.activeKeyMidis.forEach((_, midi) => {
        const key = state.keyElements.get(midi);
        if (key) {
            key.classList.remove("active-left", "active-right");
        }
    });
    state.activeKeyMidis.clear();
    state.keyElements.forEach((key) => {
        key.classList.remove("active-left", "active-right");
    });
    state.visibleNoteIndices.forEach((index) => {
        const record = state.noteElements[index];
        if (record) {
            record.element.style.opacity = "0";
            record.element.style.transform = "translate3d(0, -9999px, 0)";
        }
    });
    state.visibleNoteIndices.clear();
    els.progressFill.style.transform = "scaleX(0)";
    els.timeLabel.textContent = `0:00 / ${formatTime(state.summary?.duration || 0)}`;
    state.lastTimeLabelAt = 0;
}

function applyActiveKeys(nextActiveKeyMidis) {
    state.activeKeyMidis.forEach((hand, midi) => {
        if (nextActiveKeyMidis.get(midi) === hand) return;
        const key = state.keyElements.get(midi);
        if (key) {
            key.classList.remove("active-left", "active-right");
        }
    });

    nextActiveKeyMidis.forEach((hand, midi) => {
        if (state.activeKeyMidis.get(midi) === hand) return;
        const key = state.keyElements.get(midi);
        if (key) {
            key.classList.remove("active-left", "active-right");
            key.classList.add(hand === "left" ? "active-left" : "active-right");
        }
    });

    state.activeKeyMidis = nextActiveKeyMidis;
}

function updateVisuals() {
    const time = playbackTime();
    const duration = state.summary?.duration || 0;
    const height = els.waterfall.clientHeight || 360;
    const lineY = height - 8;
    const leadSeconds = (height / PIXELS_PER_SECOND) + VISIBILITY_PADDING_SECONDS;
    const startIndex = lowerBoundNoteStart(time - state.maxNoteDuration - VISIBILITY_PADDING_SECONDS);
    const endIndex = upperBoundNoteStart(time + leadSeconds);
    const nextVisible = new Set();
    const nextActiveKeys = new Map();

    for (let index = startIndex; index < endIndex; index += 1) {
        const record = state.noteElements[index];
        if (!record) continue;

        const { element, note } = record;
        if (record.endTime < time - VISIBILITY_PADDING_SECONDS) continue;

        const y = lineY - (note.time - time) * PIXELS_PER_SECOND - record.height;
        const visible = y > -record.height - 32 && y < height + 52;
        if (!visible) continue;

        nextVisible.add(index);
        element.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0)`;
        if (!state.visibleNoteIndices.has(index)) {
            element.style.opacity = "1";
        }
        if (time >= note.time && time <= note.time + note.duration + 0.04) {
            nextActiveKeys.set(note.midi, note.hand);
        }
    }

    state.visibleNoteIndices.forEach((index) => {
        if (nextVisible.has(index)) return;
        const record = state.noteElements[index];
        if (record) {
            record.element.style.opacity = "0";
        }
    });
    state.visibleNoteIndices = nextVisible;
    applyActiveKeys(nextActiveKeys);

    const pct = duration ? Math.min(100, (time / duration) * 100) : 0;
    els.progressFill.style.transform = `scaleX(${pct / 100})`;

    const now = performance.now();
    if (!state.lastTimeLabelAt || now - state.lastTimeLabelAt >= TIME_LABEL_INTERVAL_MS || !state.isPlaying) {
        els.timeLabel.textContent = `${formatTime(time)} / ${formatTime(duration)}`;
        state.lastTimeLabelAt = now;
    }

    if (state.isPlaying) {
        state.animationFrame = requestAnimationFrame(updateVisuals);
    }
}

async function loadMidiBuffer(buffer, name = "score.mid") {
    state.midiBuffer = buffer.slice(0);
    state.summary = parseMidi(buffer.slice(0));
    clampMidiRange(state.summary.notes);
    buildKeyboard();
    renderNotes();
    resetVisuals();

    els.midiName.textContent = name;
    els.noteCount.textContent = `${state.summary.noteCount} notes`;
    els.duration.textContent = formatTime(state.summary.duration);
    setStatus(state.soundFontBuffer ? "Ready to play" : "MIDI ready");
    updateButtons();
}

function base64ToArrayBuffer(encoded) {
    const binary = atob(encoded);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) {
        bytes[index] = binary.charCodeAt(index);
    }
    return bytes.buffer;
}

window.pyclefLoadMidiBase64 = async function pyclefLoadMidiBase64(encoded, fileName) {
    try {
        await loadMidiBuffer(base64ToArrayBuffer(encoded), fileName || "pyclef.mid");
    } catch (error) {
        setStatus(`Could not load MIDI: ${error.message}`);
    }
};

window.pyclefRefreshLayout = refreshLayout;

async function loadDefaultSoundFont() {
    els.loadSoundFont.disabled = true;
    setStatus("Loading piano...");
    try {
        const response = await fetch(DEFAULT_SOUNDFONT_URL);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        state.soundFontBuffer = await response.arrayBuffer();
        setStatus(state.midiBuffer ? "Ready to play" : "Piano ready");
    } catch (error) {
        setStatus(`Piano load failed: ${error.message}`);
    } finally {
        els.loadSoundFont.disabled = false;
        updateButtons();
    }
}

async function ensureAudioEngine() {
    if (!window.JSSynth) {
        throw new Error("SoundFont engine did not load.");
    }
    if (!state.audioContext) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        state.audioContext = new AudioContextClass();
    }
    if (state.audioContext.state === "suspended") {
        await state.audioContext.resume();
    }
    await JSSynth.waitForReady();
}

function disposeSynth() {
    if (state.synth) {
        try {
            state.synth.stopPlayer();
        } catch {
            // Already stopped.
        }
        try {
            state.synth.close();
        } catch {
            // Already closed.
        }
    }
    if (state.node) {
        try {
            state.node.disconnect();
        } catch {
            // Already disconnected.
        }
    }
    state.synth = null;
    state.node = null;
}

async function playMidi() {
    if (!state.midiBuffer || !state.soundFontBuffer || state.isPlaying) return;

    try {
        await ensureAudioEngine();
        disposeSynth();

        const synth = new JSSynth.Synthesizer();
        synth.init(state.audioContext.sampleRate);
        const node = synth.createAudioNode(state.audioContext, 8192);
        node.connect(state.audioContext.destination);

        state.synth = synth;
        state.node = node;
        if (typeof synth.setGain === "function") {
            synth.setGain(Number(els.volume.value || 86) / 100);
        }

        setStatus("Preparing playback");
        await synth.loadSFont(state.soundFontBuffer.slice(0));
        await synth.addSMFDataToPlayer(state.midiBuffer.slice(0));

        state.isPlaying = true;
        state.startedAt = performance.now();
        state.audioStartedAt = state.audioContext.currentTime;
        setStatus("Playing", true);
        updateButtons();
        updateVisuals();

        await synth.playPlayer();
        await synth.waitForPlayerStopped();
        await synth.waitForVoicesStopped();

        state.isPlaying = false;
        state.audioStartedAt = 0;
        cancelAnimationFrame(state.animationFrame);
        updateVisuals();
        setStatus("Finished");
        updateButtons();
    } catch (error) {
        state.isPlaying = false;
        state.audioStartedAt = 0;
        cancelAnimationFrame(state.animationFrame);
        setStatus(`Playback error: ${error.message}`);
        updateButtons();
        disposeSynth();
    }
}

function stopMidi() {
    if (!state.isPlaying) return;
    state.isPlaying = false;
    cancelAnimationFrame(state.animationFrame);
    disposeSynth();
    setStatus("Stopped");
    updateButtons();
    resetVisuals();
}

function forceStopPlayback() {
    state.isPlaying = false;
    cancelAnimationFrame(state.animationFrame);
    disposeSynth();
    if (state.audioContext && state.audioContext.state !== "closed") {
        state.audioContext.suspend().catch(() => {});
    }
}

window.pyclefStopPlayback = forceStopPlayback;

function initEvents() {
    els.selectMidi.addEventListener("click", () => els.midiInput.click());
    els.midiInput.addEventListener("change", async () => {
        const file = els.midiInput.files?.[0];
        if (!file) return;
        await loadMidiBuffer(await file.arrayBuffer(), file.name);
    });
    els.loadSoundFont.addEventListener("click", loadDefaultSoundFont);
    els.playButton.addEventListener("click", playMidi);
    els.stopButton.addEventListener("click", stopMidi);
    els.volume.addEventListener("input", () => {
        if (state.synth && typeof state.synth.setGain === "function") {
            state.synth.setGain(Number(els.volume.value || 86) / 100);
        }
    });
    window.addEventListener("resize", () => {
        window.clearTimeout(state.resizeTimer);
        state.resizeTimer = window.setTimeout(refreshLayout, 120);
    });
}

initEvents();
buildKeyboard();
if (!window.JSSynth) {
    setStatus("SoundFont engine did not load.");
} else {
    loadDefaultSoundFont();
}

window.addEventListener("pagehide", forceStopPlayback);
window.addEventListener("beforeunload", forceStopPlayback);

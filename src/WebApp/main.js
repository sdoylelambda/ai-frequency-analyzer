// main.js
let pyodide = null;
let audioCtx = null;
let analyser = null;
let source = null;
let dataArray = null;
let freqBins = null;
let rafHandle = null;
let running = false;
let latest_peaks = null;
let latest_freqs = null;
let latest_mags = null;

const statusEl = document.getElementById("status");
const logEl = document.getElementById("log");
const canvas = document.getElementById("spectrum");
const ctx = canvas.getContext("2d");
const btnStart = document.getElementById("btn-start");
const btnStop = document.getElementById("btn-stop");
const btnReview = document.getElementById("btn-review");
const fftSizeSelect = document.getElementById("fftSize");
const thresholdRange = document.getElementById("threshold");

function log(msg) {
  const t = new Date().toLocaleTimeString();
  logEl.innerText = `[${t}] ${msg}\n` + logEl.innerText;
}

async function loadPyodideAndPackages() {
  statusEl.innerText = "Pyodide: loading core...";
  pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/" });
  statusEl.innerText = "Pyodide: loading micropackages...";
  // load any micropackages we need (numpy is included in Pyodide core)
  await pyodide.loadPackage(["numpy"]);
  statusEl.innerText = "Pyodide: initializing python app...";
  // inject python app code (see below)
  await pyodide.runPythonAsync(python_app_code);
  statusEl.innerText = "Pyodide: ready — click Start Listening";
  log("Pyodide ready.");
}

// Minimal python app; replace with your full logic later.
const python_app_code = `
import numpy as np
# Chakra bands: (start, end, label, color)
CHAKRA_FREQUENCY_BANDS = [
    (136.1, 136.1, "OM (C#3) 3rd Eye (6th)", "purple"),
    (172.0, 172.0, "172Hz – Inner Balance / Spleen Meridian", "blue"),
    (215.0, 215.0, "215Hz – Emotional Clearing / Regeneration", "skyblue"),
    (285.0, 285.0, "285Hz – Tissue Healing / Restoration", "turquoise"),
    (396.0, 396.0, "396Hz - Root Chakra (1st)", "orange"),
    (417.0, 417.0, "417Hz - Sacral Chakra (2nd)", "orange"),
    (432.0, 432.0, "432Hz - Heart Chakra (4th)", "green"),
    (528.0, 528.0, "528Hz - Solar Plexus Chakra (3rd)", "yellow"),
    (741.0, 741.0, "741Hz - Throat Chakra (5th)", "cyan"),
    (963.0, 963.0, "963Hz - Crown Chakra (7th)", "violet"),
    (777.0, 777.0, "777 - Positive Energy Flow", "violet"),
    (888.0, 888.0, "888 - Abundance and Prosperity", "gold"),
    (999.0, 999.0, "999 - Manifestation and Transformation", "gold"),
    (1111.0, 1111.0, "1111 - Spiritual Awakening", "gold"),
]

def match_frequency_to_band(freq, tolerance_hz=3.0):
    """Return label,color for a freq if it matches a band center within tolerance."""
    for start, end, label, color in CHAKRA_FREQUENCY_BANDS:
        center = (start + end) / 2.0
        if abs(freq - center) <= tolerance_hz:
            return label, color
    return None, None

def detect_peaks_js(freqs, mags, mag_threshold=0.0, top_n=12):
    """Simple peak selection: choose top_n peaks above mag_threshold.
    freqs, mags are numpy arrays."""
    if freqs.size == 0 or mags.size == 0:
        return []
    # keep only finite
    mask = np.isfinite(freqs) & np.isfinite(mags)
    freqs = freqs[mask]
    mags = mags[mask]
    if freqs.size == 0:
        return []
    # find peaks by sorting magnitude descending
    idx = np.argsort(mags)[::-1]
    peaks = []
    used = []
    skip_radius = 2.0
    for i in idx:
        f = float(freqs[i])
        m = float(mags[i])
        if m < mag_threshold:
            continue
        if any(abs(f - u) < skip_radius for u in used):
            continue
        label, color = match_frequency_to_band(f)
        if label:
            peaks.append((f, m, label, color))
            used.append(f)
        if len(peaks) >= top_n:
            break
    return peaks

def analyze_chakra_energy_from_peaks(peaks):
    """Aggregate mags per chakra label, produce percentages, balance score, and flags."""
    chakra_energy = {}
    total = 0.0
    for f, m, label, color in peaks:
        # Simplify label to a short key (take leading number or name)
        key = label.split("–")[-1].strip()
        key = key.replace("Hz", "").strip()
        chakra_energy[key] = chakra_energy.get(key, 0.0) + float(m)
        total += float(m)
    if total == 0.0:
        return {"chakra_energies": {}, "balance_score": 0.0, "flags": ["🔴 No chakra peaks detected."]}
    # percentages
    pct = {k: round((v/total)*100.0, 2) for k,v in chakra_energy.items()}
    # simple balance score: inverse std dev (normalized)
    vals = np.array(list(pct.values()))
    std = float(np.std(vals)) if vals.size>0 else 0.0
    balance_score = round(1.0 - min(std / 40.0, 1.0), 2)
    flags = []
    for k, p in pct.items():
        if p >= 30:
            flags.append(f"🟨 {k} dominating ({p:.1f}%)")
        elif p < 5:
            flags.append(f"🟧 {k} low ({p:.1f}%)")
    if balance_score < 0.5:
        flags.append("🔺 Energy distribution is imbalanced. Consider grounding.")
    return {"chakra_energies": pct, "balance_score": balance_score, "flags": flags}

# Expose a callable to JS: it accepts python lists or np arrays
def process_spectrum(freqs_js, mags_js, mag_threshold=0.0):
    freqs = np.array(freqs_js, dtype=float)
    mags = np.array(mags_js, dtype=float)
    peaks = detect_peaks_js(freqs, mags, mag_threshold=mag_threshold)
    analysis = analyze_chakra_energy_from_peaks(peaks)
    # also return peaks
    return {
        "peaks": peaks,
        "analysis": analysis
    }
`;

async function startAudio() {
  if (running) return;
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    source = audioCtx.createMediaStreamSource(stream);

    analyser = audioCtx.createAnalyser();
    analyser.fftSize = parseInt(fftSizeSelect.value);
    const bufferLength = analyser.frequencyBinCount;
    dataArray = new Float32Array(bufferLength);
    // build frequencies array for the given sampleRate and fft size
    const sampleRate = audioCtx.sampleRate;
    freqBins = new Float32Array(bufferLength);
    for (let i=0;i<bufferLength;i++){
      freqBins[i] = i * (sampleRate / analyser.fftSize);
    }

    source.connect(analyser);
    running = true;
    btnStart.disabled = true;
    btnStop.disabled = false;
    btnReview.disabled = false;
    log("Microphone stream started.");
    renderLoop();
  } catch (e) {
    log("Microphone open failed: " + e);
    console.error(e);
  }
}

function stopAudio() {
  running = false;
  btnStart.disabled = false;
  btnStop.disabled = true;
  if (rafHandle) cancelAnimationFrame(rafHandle);
  if (audioCtx && audioCtx.state !== 'closed') {
    try { audioCtx.close(); } catch(e){}
  }
  audioCtx = null;
  analyser = null;
  source = null;
  log("Microphone stopped.");
}

async function renderLoop() {
  if (!running) return;
  analyser.getFloatFrequencyData(dataArray); // in dB
  // convert dB -> linear magnitude (approx)
  const mags = new Float32Array(dataArray.length);
  for (let i=0;i<dataArray.length;i++){
    const db = dataArray[i];
    // dB is negative or -Infinity when zero; convert to positive magnitude
    const lin = db === -Infinity ? 0.0 : Math.pow(10.0, db / 20.0);
    mags[i] = lin;
  }
  // store latest for review UI
  latest_freqs = Array.from(freqBins);
  latest_mags = Array.from(mags);

  // call python processing
  if (pyodide) {
    try {
      // pass JS arrays into Python; convert using pyodide.toPy auto when calling
      const pyProcess = pyodide.globals.get("process_spectrum");
      const magThreshold = parseFloat(thresholdRange.value) / 100.0; // scaled small
      const res = pyProcess(latest_freqs, latest_mags, magThreshold);
      // res is a Python object — convert to JS
      const jsRes = res.toJs ? res.toJs() : res;
      latest_peaks = jsRes.peaks || [];
      const analysis = jsRes.analysis || jsRes.get("analysis", {});
      drawSpectrum(latest_freqs, latest_mags, latest_peaks);
      // tiny logging
      if (latest_peaks && latest_peaks.length > 0) {
        log(`Peaks count: ${latest_peaks.length}`);
      }
    } catch (ex) {
      console.error("Py processing failed:", ex);
    }
  } else {
    drawSpectrum(latest_freqs, latest_mags, []);
  }

  rafHandle = requestAnimationFrame(renderLoop);
}

function drawSpectrum(freqs, mags, peaks) {
  const w = canvas.width = canvas.clientWidth * devicePixelRatio;
  const h = canvas.height = 220 * devicePixelRatio;
  ctx.clearRect(0,0,w,h);
  // background
  ctx.fillStyle = "#01131a";
  ctx.fillRect(0,0,w,h);
  // draw magnitudes (use first 1000Hz region)
  const maxFreq = 1200;
  const binsToShow = freqs ? freqs.findIndex(f => f > maxFreq) : mags.length;
  const len = Math.max(1, binsToShow);
  // get max mag to scale
  let maxMag = 0;
  for (let i=0;i<len;i++) if (mags[i] > maxMag) maxMag = mags[i];
  if (maxMag <= 0) maxMag = 1;
  ctx.beginPath();
  ctx.moveTo(0,h);
  for (let i=0;i<len;i++){
    const x = (i / len) * w;
    const y = h - (mags[i] / maxMag) * (h - 20);
    ctx.lineTo(x,y);
  }
  ctx.lineTo(w,h);
  ctx.closePath();
  ctx.fillStyle = "rgba(32,200,200,0.12)";
  ctx.fill();
  // mark peaks
  ctx.strokeStyle = "rgba(255,255,255,0.9)";
  ctx.lineWidth = 1 * devicePixelRatio;
  peaks.forEach(p => {
    const f = p[0];
    // find nearest bin
    let idx = 0;
    for (let i=0;i<freqs.length;i++){
      if (freqs[i] >= f) { idx = i; break; }
    }
    const x = (idx / len) * w;
    ctx.beginPath();
    ctx.moveTo(x,0);
    ctx.lineTo(x,h);
    ctx.stroke();
    // label
    ctx.fillStyle = p[3] || "white";
    ctx.fillText(p[2], x+4, 14);
  });
}

function showReviewPopup() {
  // Build a simple review from latest_peaks and call Python analyze_chakra_energy_from_peaks if needed.
  if (!latest_peaks || latest_peaks.length === 0){
    alert("No peaks available for review.");
    return;
  }
  // call Python analyze function quickly (we already got analysis in render loop)
  const pyAnalyze = pyodide.globals.get("analyze_chakra_energy_from_peaks");
  const analysis = pyAnalyze(latest_peaks);
  const jsAnalysis = analysis.toJs ? analysis.toJs() : analysis;
  // create popup window content
  const win = window.open("", "Chakra Review", "width=600,height=700");
  win.document.body.style.background = "#041018";
  win.document.body.style.color = "#ecf8ff";
  win.document.body.style.fontFamily = "system-ui, -apple-system, Roboto, Arial";
  win.document.body.innerHTML = "<h2>Chakra Activation Review</h2>";
  win.document.body.innerHTML += "<pre style='white-space:pre-wrap;'>" + JSON.stringify(jsAnalysis, null, 2) + "</pre>";
}

btnStart.addEventListener("click", async () => {
  await startAudio();
});
btnStop.addEventListener("click", () => {
  stopAudio();
});
btnReview.addEventListener("click", () => {
  showReviewPopup();
});

fftSizeSelect.addEventListener("change", () => {
  if (analyser) {
    analyser.fftSize = parseInt(fftSizeSelect.value);
  }
});

// start
loadPyodideAndPackages().then(() => {
  statusEl.innerText = "Ready — click Start Listening.";
});

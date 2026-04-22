// Glue layer. Pyodide does the math, Plotly does the drawing, this
// file moves state between them.
//
// One Pyodide instance lives for the page. Loading numpy costs ~10MB
// and several seconds, so we initialize once and reuse. The user's
// selection and slider state live in plain vars; recomputing on "Run"
// is cheap compared to the Pyodide boot.

const PYODIDE_CDN = "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/";
const DEFAULT_STATES = ["MS", "ID"];
const MAX_SELECTION = 2;

const ui = {
  status: document.getElementById("status"),
  selection: document.getElementById("selection"),
  runBtn: document.getElementById("run"),
  mapDiv: document.getElementById("map"),
  curvesDiv: document.getElementById("curves"),
  histDiv: document.getElementById("hist"),
  diseaseInputs: () => document.querySelectorAll('input[name="disease"]'),
  nRuns: document.getElementById("n_runs"),
  nRunsVal: document.getElementById("n_runs_val"),
  pop: document.getElementById("pop"),
  popVal: document.getElementById("pop_val"),
  tmax: document.getElementById("tmax"),
  tmaxVal: document.getElementById("tmax_val"),
};

const state = {
  pyodide: null,
  disease: "measles",
  selected: [...DEFAULT_STATES],
  running: false,
};

function setStatus(msg, isErr = false) {
  ui.status.textContent = msg;
  ui.status.classList.toggle("err", !!isErr);
}

function currentDisease() {
  for (const el of ui.diseaseInputs()) if (el.checked) return el.value;
  return "measles";
}

function coverageKey(disease) {
  return disease === "measles" ? "mmr" : "flu";
}

function updateSelectionDisplay() {
  const names = state.selected.map(abb => state_by_abb[abb].name).join(" and ");
  ui.selection.innerHTML = `Selected: <b>${names || "none"}</b> (click the map to change; up to ${MAX_SELECTION})`;
}

// --------------------------------------------------------------- Map

// Plotly's built-in US states geo lets us avoid shipping a topojson
// file. The price is a fixed projection we can't easily restyle, but
// for a pedagogical map the default looks fine.
function drawMap() {
  const disease = currentDisease();
  const key = coverageKey(disease);
  const locations = state_coverage.map(s => s.abb);
  const values = state_coverage.map(s => s[key]);
  const text = state_coverage.map(s => `${s.name}<br>${key.toUpperCase()}: ${s[key]}%`);

  // Selected states get a thick rust border. Per-location arrays are
  // the only way Plotly will honor variable marker.line.width on a
  // choropleth; a scalar applies to everything.
  const lineWidths = locations.map(abb => state.selected.includes(abb) ? 3 : 0.5);
  const lineColors = locations.map(abb => state.selected.includes(abb) ? "#8b2e19" : "#888");

  const data = [{
    type: "choropleth",
    locationmode: "USA-states",
    locations,
    z: values,
    text,
    hoverinfo: "text",
    colorscale: disease === "measles"
      ? [[0, "#f1e6d3"], [0.6, "#c77d5a"], [1, "#5a1f10"]]
      : [[0, "#f1e6d3"], [0.6, "#8aa58a"], [1, "#2f5538"]],
    zmin: disease === "measles" ? 80 : 35,
    zmax: disease === "measles" ? 100 : 60,
    colorbar: { title: { text: `${key.toUpperCase()} %` }, thickness: 12, len: 0.6 },
    marker: { line: { width: lineWidths, color: lineColors } },
  }];

  const layout = {
    geo: { scope: "usa", projection: { type: "albers usa" }, bgcolor: "rgba(0,0,0,0)" },
    margin: { l: 0, r: 0, t: 10, b: 10 },
    paper_bgcolor: "rgba(0,0,0,0)",
    height: 380,
    dragmode: false,
  };

  Plotly.react(ui.mapDiv, data, layout, { displayModeBar: false, responsive: true })
    .then(() => {
      // Rebind on every react() because Plotly drops handlers on redraw.
      ui.mapDiv.on("plotly_click", ev => {
        if (!ev || !ev.points || !ev.points.length) return;
        const abb = ev.points[0].location;
        handleStateClick(abb);
      });
    });
}

function handleStateClick(abb) {
  if (state.selected.includes(abb)) {
    state.selected = state.selected.filter(x => x !== abb);
  } else if (state.selected.length < MAX_SELECTION) {
    state.selected.push(abb);
  } else {
    // Third click replaces oldest. Keeps selection at <= 2 without a
    // mode switch; prior click is shifted out.
    state.selected.shift();
    state.selected.push(abb);
  }
  updateSelectionDisplay();
  drawMap();
}

// --------------------------------------------------------------- Sim

async function bootPyodide() {
  setStatus("Loading Python runtime, about 10 MB...");
  state.pyodide = await loadPyodide({ indexURL: PYODIDE_CDN });
  setStatus("Loading NumPy...");
  await state.pyodide.loadPackage(["numpy"]);
  setStatus("Fetching simulation code...");
  // Fetching sim.py as text and writing it into Pyodide's virtual FS
  // lets us `import sim` like a normal module. Keeps the Python file
  // browsable on its own instead of embedded as a string.
  const res = await fetch("./sim.py");
  if (!res.ok) throw new Error(`Failed to fetch sim.py: ${res.status}`);
  const code = await res.text();
  state.pyodide.FS.writeFile("sim.py", code);
  state.pyodide.runPython("import sim");
  setStatus("Ready.");
}

async function simulateOne(abb, disease, n_runs, pop, tmax, seedOffset) {
  const sc = state_by_abb[abb];
  const coverage = sc[coverageKey(disease)];
  state.pyodide.globals.set("_disease", disease);
  state.pyodide.globals.set("_coverage_pct", coverage);
  state.pyodide.globals.set("_N", pop);
  // I0 = 5. Small but not single-seed so fade-out stochasticity is
  // visible without being the whole story.
  state.pyodide.globals.set("_I0", 5);
  state.pyodide.globals.set("_n_runs", n_runs);
  state.pyodide.globals.set("_tmax", tmax);
  state.pyodide.globals.set("_tau", 0.1);
  state.pyodide.globals.set("_seed", 20260422 + seedOffset);

  const result = state.pyodide.runPython(`
import sim
sim.simulate_state(
    disease=_disease,
    coverage_pct=_coverage_pct,
    N=int(_N),
    I0=int(_I0),
    n_runs=int(_n_runs),
    tmax=int(_tmax),
    tau=float(_tau),
    seed=int(_seed),
)
`);
  const out = result.toJs({ dict_converter: Object.fromEntries });
  result.destroy();
  out.state = sc;
  out.abb = abb;
  return out;
}

async function runSim() {
  if (state.running) return;
  if (!state.pyodide) { setStatus("Still loading Python...", true); return; }
  if (state.selected.length === 0) { setStatus("Select at least one state.", true); return; }

  state.running = true;
  ui.runBtn.disabled = true;
  const disease = currentDisease();
  state.disease = disease;
  const n_runs = parseInt(ui.nRuns.value, 10);
  const pop = parseInt(ui.pop.value, 10);
  const tmax = parseInt(ui.tmax.value, 10);

  setStatus(`Simulating ${n_runs} runs per state...`);
  const results = [];
  try {
    for (let i = 0; i < state.selected.length; i++) {
      // Yield to the event loop between states so the status text
      // actually paints. Pyodide is synchronous inside runPython.
      await new Promise(r => setTimeout(r, 10));
      const r = await simulateOne(state.selected[i], disease, n_runs, pop, tmax, i * 997);
      results.push(r);
    }
    drawCurves(results, disease);
    drawHist(results, disease);
    setStatus(`Done. ${state.selected.length} state(s), ${n_runs} runs each, N = ${pop.toLocaleString()}.`);
  } catch (e) {
    console.error(e);
    setStatus(`Simulation error: ${e.message}`, true);
  } finally {
    state.running = false;
    ui.runBtn.disabled = false;
  }
}

// ------------------------------------------------------------- Plots

const STATE_COLORS = ["#8b2e19", "#2f5538"];

function drawCurves(results, disease) {
  const traces = [];
  results.forEach((r, i) => {
    const color = STATE_COLORS[i % STATE_COLORS.length];
    const name = r.state.name;
    // The band goes first so the median line draws on top. Plotly
    // stacks by trace order within a subplot.
    traces.push({
      x: [...r.t, ...[...r.t].reverse()],
      y: [...r.I_hi, ...[...r.I_lo].reverse()],
      fill: "toself",
      fillcolor: hexA(color, 0.18),
      line: { color: "rgba(0,0,0,0)" },
      hoverinfo: "skip",
      showlegend: false,
      name: `${name} 95% band`,
    });
    traces.push({
      x: r.t, y: r.I_med,
      mode: "lines",
      line: { color, width: 2 },
      name: `${name} median`,
    });
  });

  const reffs = results.map(r =>
    `${r.state.name}: R₀=${r.R0.toFixed(1)}, R_eff(0)=${r.R_eff0.toFixed(2)}`
  ).join("  |  ");

  const layout = {
    title: {
      text: `Infectious count over time (${disease}, median + 95% band)<br><sub>${reffs}</sub>`,
      font: { size: 14 },
    },
    xaxis: { title: "Days since outbreak start" },
    yaxis: { title: "Infectious (I)", rangemode: "tozero" },
    margin: { l: 60, r: 20, t: 70, b: 50 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    legend: { orientation: "h", y: -0.2 },
    height: 420,
  };
  Plotly.react(ui.curvesDiv, traces, layout, { displayModeBar: false, responsive: true });
}

function drawHist(results, disease) {
  const traces = [];
  const shapes = [];
  results.forEach((r, i) => {
    const color = STATE_COLORS[i % STATE_COLORS.length];
    traces.push({
      x: r.attack_rate,
      type: "histogram",
      name: r.state.name,
      opacity: 0.55,
      marker: { color },
      xbins: { start: 0, end: 1, size: 0.025 },
      hovertemplate: "AR: %{x:.1%}<br>count: %{y}<extra></extra>",
    });
    shapes.push({
      type: "line",
      x0: r.attack_rate_median, x1: r.attack_rate_median,
      yref: "paper", y0: 0, y1: 1,
      line: { color, width: 2, dash: "dash" },
    });
  });

  const sub = results.map(r =>
    `${r.state.name}: median AR=${(r.attack_rate_median * 100).toFixed(1)}%, fade-out=${(r.fadeout_frac * 100).toFixed(0)}%`
  ).join("  |  ");

  const layout = {
    title: {
      text: `Final attack-rate distribution (${disease})<br><sub>${sub}</sub>`,
      font: { size: 14 },
    },
    xaxis: { title: "Final attack rate (cum_inc / N)", tickformat: ".0%", range: [0, 1] },
    yaxis: { title: "Runs" },
    barmode: "overlay",
    shapes,
    margin: { l: 60, r: 20, t: 70, b: 50 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    legend: { orientation: "h", y: -0.2 },
    height: 360,
  };
  Plotly.react(ui.histDiv, traces, layout, { displayModeBar: false, responsive: true });
}

function hexA(hex, a) {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  return `rgba(${r},${g},${b},${a})`;
}

// ------------------------------------------------------------- Wiring

function wireControls() {
  const syncLabel = (slider, out, fmt) => {
    const update = () => { out.textContent = fmt(slider.value); };
    slider.addEventListener("input", update);
    update();
  };
  syncLabel(ui.nRuns, ui.nRunsVal, v => `${v}`);
  syncLabel(ui.pop, ui.popVal, v => Number(v).toLocaleString());
  syncLabel(ui.tmax, ui.tmaxVal, v => `${v} days`);

  ui.diseaseInputs().forEach(el => el.addEventListener("change", () => drawMap()));
  ui.runBtn.addEventListener("click", runSim);
}

async function main() {
  wireControls();
  updateSelectionDisplay();
  drawMap();
  try {
    await bootPyodide();
    await runSim();
  } catch (e) {
    console.error(e);
    setStatus(`Startup error: ${e.message}. If you opened the file directly, try 'python -m http.server' instead.`, true);
  }
}

main();

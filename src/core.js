"use strict";
// The Single Income Stress Test. Vanilla JS on canvas; every number is computed here from DATA.
(async function () {
  const root = document.getElementById("ss");
  let framed = false;
  try { framed = window.self !== window.top; } catch (e) { framed = true; }
  const hashFlags = new URLSearchParams(location.hash.slice(1));
  if (hashFlags.get("embed") === "1") framed = true;
  if (framed) { root.classList.add("framed"); document.documentElement.setAttribute("data-theme", "light"); }

  const $ = (id) => document.getElementById(id);
  const TOP_N = 25;
  // Fixed class breaks, the same in every year, so a color change while playing is a real change.
  const BINS = {
    dol: [-10000, -5000, -1000, 1000, 5000, 10000],          // dollars a year
    pct: [70, 85, 97, 103, 115, 130],                        // income as a percent of threshold plus cushion
    dolChg: [-6000, -3000, -1000, 1000, 3000, 6000],         // change in dollars
    pctChg: [-15, -8, -2, 2, 8, 15],                         // change in percentage points
  };
  const VARS = ["--neg3", "--neg2", "--neg1", "--mid", "--pos1", "--pos2", "--pos3"];
  const PCT_NAME = ["10th percentile", "25th percentile", "50th percentile", "75th percentile", "90th percentile"];
  const TEN_NAME = ["renters", "owners with a mortgage", "owners with no mortgage"];
  const TYPE_NAME = { 4: "Metro area", 6: "Nonmetro area" };

  // ---------- data ----------
  async function loadData() {
    const bin = Uint8Array.from(atob(DATA_B64), (c) => c.charCodeAt(0));
    const stream = new Blob([bin]).stream().pipeThrough(new DecompressionStream("gzip"));
    return JSON.parse(await new Response(stream).text());
  }
  const DATA = await loadData();
  const YEARS = DATA.years, NY = YEARS.length, GRID = DATA.grid;
  const A = DATA.areas;
  const byId = new Map();
  for (const a of A) {
    if (byId.has(a.id)) throw new Error("duplicate area id " + a.id);
    byId.set(a.id, a);
  }
  const eraOf = YEARS.map((y) => DATA.eras.findIndex((e) => y >= e.from && y <= e.to));

  // ---------- geometry: one set of shapes per boundary era ----------
  function decodeRing(a) {
    const out = new Float64Array(a.length);
    let x = 0, y = 0;
    for (let i = 0; i < a.length; i += 2) { x += a[i]; y += a[i + 1]; out[i] = x; out[i + 1] = y; }
    return out;
  }
  function buildPath(polys, bb) {
    const p = new Path2D();
    for (const rings of polys) for (const r of rings) {
      const c = decodeRing(r);
      p.moveTo(c[0], c[1]);
      for (let i = 0; i < c.length; i += 2) {
        if (i) p.lineTo(c[i], c[i + 1]);
        if (bb) {
          if (c[i] < bb[0]) bb[0] = c[i]; if (c[i] > bb[2]) bb[2] = c[i];
          if (c[i + 1] < bb[1]) bb[1] = c[i + 1]; if (c[i + 1] > bb[3]) bb[3] = c[i + 1];
        }
      }
      p.closePath();
    }
    return p;
  }
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  const stateBB = {};
  const ERAS = DATA.eras.map((e) => {
    const shapes = new Map();
    for (const id in e.geo) {
      const a = byId.get(id);
      if (!a) throw new Error("shape with no area " + id);
      const bb = [Infinity, Infinity, -Infinity, -Infinity];
      shapes.set(id, { a, path: buildPath(e.geo[id], bb), bb });
      minX = Math.min(minX, bb[0]); minY = Math.min(minY, bb[1]); maxX = Math.max(maxX, bb[2]); maxY = Math.max(maxY, bb[3]);
      const b = stateBB[a.s] || (stateBB[a.s] = [Infinity, Infinity, -Infinity, -Infinity]);
      b[0] = Math.min(b[0], bb[0]); b[1] = Math.min(b[1], bb[1]); b[2] = Math.max(b[2], bb[2]); b[3] = Math.max(b[3], bb[3]);
    }
    return { shapes, list: [...shapes.values()], cells: null };
  });
  const borders = DATA.borders.map((b) => buildPath(b, null));
  // uniform grid index per era for hit testing
  const GX = 60, GY = 40, cellW = (maxX - minX) / GX, cellH = (maxY - minY) / GY;
  for (const E of ERAS) {
    E.cells = Array.from({ length: GX * GY }, () => []);
    for (const s of E.list) {
      const x0 = Math.max(0, Math.floor((s.bb[0] - minX) / cellW)), x1 = Math.min(GX - 1, Math.floor((s.bb[2] - minX) / cellW));
      const y0 = Math.max(0, Math.floor((s.bb[1] - minY) / cellH)), y1 = Math.min(GY - 1, Math.floor((s.bb[3] - minY) / cellH));
      for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) E.cells[y * GX + x].push(s);
    }
  }
  const hitCtx = document.createElement("canvas").getContext("2d");
  function hitTest(gx, gy) {
    const cx = Math.floor((gx - minX) / cellW), cy = Math.floor((gy - minY) / cellH);
    if (cx < 0 || cy < 0 || cx >= GX || cy >= GY) return null;
    for (const s of era().cells[cy * GX + cx]) {
      if (gx < s.bb[0] || gx > s.bb[2] || gy < s.bb[1] || gy > s.bb[3]) continue;
      if (hitCtx.isPointInPath(s.path, gx, gy, "evenodd")) return s.a;
    }
    return null;
  }

  // ---------- state ----------
  const S = { mode: "year", meas: "dol", yi: NY - 1, from: 0, p: 2, ten: 0, cush: 10000, est: true, st: "", sel: null, hover: null, rankTab: 0 };
  const era = () => ERAS[eraOf[S.yi]];
  const shapeOf = (a) => (a ? era().shapes.get(a.id) : null);

  // The stress test for one area and year: income, less the local threshold, less the cushion.
  // kind of threshold in use: m named metro, s state smaller-metro figure, n state nonmetro figure,
  // e our rent-based estimate (replaces s and x when the estimate option is on), x none
  const kindOf = (a, i) => (S.est && a.est[i] ? "e" : a.k[i]);
  function calc(a, i) {
    if (!a.w[i]) return null;                          // not an OEWS area that year
    const inc = a.w[i][S.p];
    const k = kindOf(a, i);
    if (k === "x") return { inc, none: true };         // no published threshold and no estimate
    const thr = (k === "e" ? a.est[i] : a.th[i])[S.ten];
    const dol = inc - thr - S.cush;
    return { inc, thr, dol, pct: (100 * inc) / (thr + S.cush) };
  }
  function binOf(v, bins) { let i = 0; while (i < bins.length && v >= bins[i]) i++; return i; }
  // value of an area in the current view: {v, cls, ...} or {cls:"none"|"nocmp"|"absent"}
  function value(a) {
    const c = calc(a, S.yi);
    if (!c) return { cls: "absent" };
    if (c.none) return { cls: "none", c };
    if (S.mode === "year") { const v = c[S.meas]; return { v, cls: binOf(v, BINS[S.meas]), c }; }
    const b = calc(a, S.from);
    // comparable only if the area existed, had the same outline, and had the same kind of threshold in both years
    if (!b || b.none || a.sh[S.from] !== a.sh[S.yi] || kindOf(a, S.from) !== kindOf(a, S.yi) || S.from === S.yi) return { cls: "nocmp", c, b };
    const v = c[S.meas] - b[S.meas];
    return { v, cls: binOf(v, BINS[S.meas + "Chg"]), c, b };
  }
  const shaded = (v) => typeof v.cls === "number";

  // ---------- colors ----------
  let C = {};
  function hatch(bg, line, w, cross) {
    const pc = document.createElement("canvas"); pc.width = pc.height = 8;
    const x = pc.getContext("2d");
    if (bg) { x.fillStyle = bg; x.fillRect(0, 0, 8, 8); }
    x.strokeStyle = line; x.lineWidth = w; x.beginPath(); x.moveTo(-2, 10); x.lineTo(10, -2); x.moveTo(-2, 2); x.lineTo(2, -2); x.moveTo(6, 10); x.lineTo(10, 6);
    if (cross) { x.moveTo(-2, -2); x.lineTo(10, 10); x.moveTo(-2, 6); x.lineTo(2, 10); x.moveTo(6, -2); x.lineTo(10, 2); }
    x.stroke();
    return bctx.createPattern(pc, "repeat");
  }
  function readColors() {
    const cs = getComputedStyle(root);
    const g = (n) => cs.getPropertyValue(n).trim();
    C = { div: VARS.map(g), nohist: g("--nohist"), hatch: g("--hatch"), mark: g("--mark"),
      edge: g("--edge"), state: g("--state"), hi: g("--hi"), panel: g("--panel"), ink3: g("--ink-3"), accent: g("--accent") };
    C.nonePat = hatch(C.nohist, C.hatch, 1.2, true);    // crosshatch: no threshold, or no comparable figure
    C.markPat = hatch(null, C.mark, 1);                 // overlay: metro on its state's figure for smaller metros
  }
  const colorOf = (val) => (shaded(val) ? C.div[val.cls] : C.nonePat);

  // ---------- canvas & view ----------
  const cv = $("map"), wrap = $("mapbox");
  const ctx = cv.getContext("2d");
  let W = 0, H = 0, dpr = 1;
  const view = { k: 1, tx: 0, ty: 0 };
  function fitBox(bb, pad = 0.06, maxK = Infinity) {
    const bw = bb[2] - bb[0], bh = bb[3] - bb[1];
    const k = Math.min(maxK, Math.min(W * (1 - 2 * pad) / bw, H * (1 - 2 * pad) / bh));
    view.k = k; view.tx = (W - bw * k) / 2 - bb[0] * k; view.ty = (H - bh * k) / 2 - bb[1] * k;
  }
  let homeK = 1, pendingSel = null;
  function home() {
    if (S.st && stateBB[S.st]) fitBox(stateBB[S.st]); else fitBox([minX, minY, maxX, maxY], 0.03);
    if (!S.st) homeK = view.k;
  }
  function resize() {
    const r = wrap.getBoundingClientRect();
    const first = W === 0;
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = r.width; H = r.height;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    if (first) {
      fitBox([minX, minY, maxX, maxY], 0.03); homeK = view.k; home();
      if (pendingSel) { select(pendingSel, true); pendingSel = null; return; }
    }
    draw();
  }

  let vals = new Map();
  function computeVals() { vals = new Map(); for (const a of A) vals.set(a.id, value(a)); }

  // Two layers: fills are rendered once into an offscreen "base" bitmap; hover and selection outlines are
  // drawn on top of a copy of it. While panning or zooming the bitmap is moved and scaled, and a sharp
  // re-render happens once the gesture settles.
  const base = document.createElement("canvas"), bctx = base.getContext("2d");
  let frame = 0, baseDirty = true, baseView = null, settleT = 0;
  function schedule() { if (!W) return; cancelAnimationFrame(frame); frame = requestAnimationFrame(render); }
  function draw() { baseDirty = true; schedule(); }
  function drawOverlay() { schedule(); }
  function interact() {
    if (!baseView) baseDirty = true;
    schedule(); clearTimeout(settleT); settleT = setTimeout(draw, 160);
  }
  function render() {
    if (baseDirty) { renderBase(); baseDirty = false; }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = C.panel; ctx.fillRect(0, 0, cv.width, cv.height);
    const r = view.k / baseView.k;
    ctx.setTransform(r, 0, 0, r, dpr * (view.tx - baseView.tx * r), dpr * (view.ty - baseView.ty * r));
    ctx.drawImage(base, 0, 0);
    ctx.setTransform(dpr * view.k, 0, 0, dpr * view.k, dpr * view.tx, dpr * view.ty);
    const lw = 1 / view.k;
    ctx.lineJoin = "round";
    const outline = (a, w, color) => { const s = shapeOf(a); if (!s) return; ctx.strokeStyle = color; ctx.lineWidth = w * lw; ctx.stroke(s.path); };
    if (S.sel) outline(S.sel, 2.4, C.hi);
    if (S.hover && S.hover !== S.sel) outline(S.hover, 1.6, C.hi);
  }
  function renderBase() {
    if (base.width !== cv.width || base.height !== cv.height) { base.width = cv.width; base.height = cv.height; }
    const c = bctx;
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.fillStyle = C.panel; c.fillRect(0, 0, base.width, base.height);
    c.setTransform(dpr * view.k, 0, 0, dpr * view.k, dpr * view.tx, dpr * view.ty);
    const x0 = -view.tx / view.k, y0 = -view.ty / view.k, x1 = (W - view.tx) / view.k, y1 = (H - view.ty) / view.k;
    const lw = 1 / view.k;
    // patterns are drawn in screen pixels whatever the zoom
    const inv = new DOMMatrix().scale(1 / (dpr * view.k) * dpr);
    C.nonePat.setTransform(inv); C.markPat.setTransform(inv);
    c.lineJoin = "round";
    c.strokeStyle = C.edge; c.lineWidth = 0.7 * lw;
    const dim = S.st;
    for (const s of era().list) {
      if (s.bb[2] < x0 || s.bb[0] > x1 || s.bb[3] < y0 || s.bb[1] > y1) continue;
      const v = vals.get(s.a.id);
      c.globalAlpha = dim && s.a.s !== dim ? 0.3 : 1;
      c.fillStyle = colorOf(v);
      c.fill(s.path, "evenodd");
      if (shaded(v) && "se".includes(kindOf(s.a, S.yi))) { c.fillStyle = C.markPat; c.fill(s.path, "evenodd"); }
      c.stroke(s.path);
    }
    c.globalAlpha = 1;
    c.strokeStyle = C.state; c.lineWidth = 0.9 * lw;
    for (const b of borders) c.stroke(b);
    baseView = { k: view.k, tx: view.tx, ty: view.ty };
  }

  // pan & zoom
  function zoomAt(f, sx, sy) {
    const k = Math.max(homeK * 0.8, Math.min(homeK * 60, view.k * f));
    const gx = (sx - view.tx) / view.k, gy = (sy - view.ty) / view.k;
    view.k = k; view.tx = sx - gx * k; view.ty = sy - gy * k;
    interact();
  }
  cv.addEventListener("wheel", (e) => { e.preventDefault(); const r = cv.getBoundingClientRect(); zoomAt(Math.exp(-e.deltaY * 0.0015), e.clientX - r.left, e.clientY - r.top); }, { passive: false });
  $("zin").onclick = () => zoomAt(1.6, W / 2, H / 2);
  $("zout").onclick = () => zoomAt(1 / 1.6, W / 2, H / 2);
  const ptrs = new Map();
  let drag = null, moved = false, pinch = null;
  cv.addEventListener("pointerdown", (e) => {
    cv.setPointerCapture(e.pointerId); ptrs.set(e.pointerId, [e.clientX, e.clientY]);
    moved = false;
    if (ptrs.size === 1) drag = { x: e.clientX, y: e.clientY, tx: view.tx, ty: view.ty };
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch = { d: Math.hypot(a[0] - b[0], a[1] - b[1]), k: view.k }; drag = null; }
  });
  cv.addEventListener("pointermove", (e) => {
    const r = cv.getBoundingClientRect();
    if (ptrs.has(e.pointerId)) ptrs.set(e.pointerId, [e.clientX, e.clientY]);
    if (pinch && ptrs.size === 2) {
      const [a, b] = [...ptrs.values()];
      const dd = Math.hypot(a[0] - b[0], a[1] - b[1]);
      zoomAt((pinch.k * dd / pinch.d) / view.k, (a[0] + b[0]) / 2 - r.left, (a[1] + b[1]) / 2 - r.top);
      moved = true; return;
    }
    if (drag) {
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) { moved = true; cv.classList.add("drag"); }
      if (moved) { view.tx = drag.tx + dx; view.ty = drag.ty + dy; hideTip(); interact(); return; }
    }
    if (e.pointerType === "mouse") hoverAt(e.clientX - r.left, e.clientY - r.top);
  });
  const endPtr = (e) => {
    ptrs.delete(e.pointerId);
    if (ptrs.size < 2) pinch = null;
    if (ptrs.size === 0) {
      cv.classList.remove("drag");
      if (drag && !moved) {
        const r = cv.getBoundingClientRect();
        const a = pick(e.clientX - r.left, e.clientY - r.top);
        select(a, false);
        if (e.pointerType !== "mouse") { S.hover = a; if (a) showTip(a, e.clientX - r.left, e.clientY - r.top); else hideTip(); }
      }
      drag = null;
    }
  };
  cv.addEventListener("pointerup", endPtr);
  cv.addEventListener("pointercancel", endPtr);
  cv.addEventListener("pointerleave", () => { if (!drag) { S.hover = null; hideTip(); showDetail(S.sel); drawOverlay(); } });

  let clearT = 0;
  function pick(sx, sy) { return hitTest((sx - view.tx) / view.k, (sy - view.ty) / view.k); }
  function hoverAt(sx, sy) {
    const a = pick(sx, sy);
    if (a !== S.hover) {
      S.hover = a; drawOverlay();
      clearTimeout(clearT);
      if (a) showDetail(a); else clearT = setTimeout(() => { if (!S.hover) showDetail(S.sel); }, 250);
    }
    if (a) showTip(a, sx, sy); else hideTip();
  }

  // ---------- formatting ----------
  const nf = new Intl.NumberFormat("en-US");
  const MINUS = "−";
  const usd = (v) => (v < 0 ? MINUS : "") + "$" + nf.format(Math.abs(Math.round(v)));
  const usdS = (v) => (v > 0 ? "+" : "") + usd(v);
  const pc = (v) => v.toFixed(0) + "%";
  const pts = (v) => (v > 0 ? "+" : v < 0 ? MINUS : "") + Math.abs(v).toFixed(1) + " points";
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const stAbbr = (s) => DATA.states[s][0];
  // metro titles already end with their states; nonmetro titles do not always name one
  const label = (a) => (a.t === 4 || a.n.includes(DATA.states[a.s][1]) ? a.n : `${a.n}, ${stAbbr(a.s)}`);
  const fmt = (v) => (S.mode === "year" ? (S.meas === "dol" ? usdS(v) : pc(v)) : (S.meas === "dol" ? usdS(v) : pts(v)));
  function verdict(c) {
    return c.dol < 0 ? `Short by ${usd(-c.dol)}` : `${usd(c.dol)} to spare`;
  }
  // where the threshold comes from, in plain words
  function sourceLine(a, i) {
    const k = kindOf(a, i);
    if (k === "e") return `Threshold: our estimate from this metro's median two-bedroom rent ($${nf.format(a.r2[i])} a month, ${DATA.acs[i]} American Community Survey), using the Census formula. `
      + (a.th[i] ? `Census's figure for ${a.sp[i].replace(/ Metro$/, "")}'s smaller metros combined is ${usd(a.th[i][S.ten])}.` : "Census publishes no figure that covers this metro.");
    if (k === "m") return `Threshold: Census figure for the ${a.sp[i].replace(/ MSA$/, "")} metro area.`;
    if (k === "s") return `Threshold: Census figure for ${a.sp[i].replace(/ Metro$/, "")}'s smaller metros combined. None is published for this metro alone.`;
    if (k === "n") return `Threshold: Census figure for nonmetro ${a.sp[i].replace(/ Nonmetro$/, "")}.`;
    return "Census publishes no threshold that covers this area in this year, and there is no rent figure to estimate one.";
  }
  function mathTable(a, i, c) {
    return `<table class="math"><tr><td>Annual income, ${PCT_NAME[S.p]}</td><td>${usd(c.inc)}</td></tr>`
      + `<tr><td>Less local poverty threshold</td><td>${MINUS}${usd(c.thr)}</td></tr>`
      + `<tr><td>Less money for surprise expenses</td><td>${MINUS}${usd(S.cush)}</td></tr>`
      + `<tr class="eq"><td>${c.dol < 0 ? "Shortfall" : "Excess"}</td><td>${usd(c.dol)}</td></tr></table>`;
  }
  function body(a, v, full) {
    const y = YEARS[S.yi];
    if (v.cls === "absent") return `<div class="src">Not a separate area in the ${y} wage data. Its boundaries were drawn differently that year.</div>`;
    if (v.cls === "none") return `<table class="math"><tr><td>Annual income, ${PCT_NAME[S.p]}</td><td>${usd(v.c.inc)}</td></tr></table><div class="src">${esc(sourceLine(a, S.yi))}</div>`;
    let h = "";
    if (S.mode === "change") {
      const y0 = YEARS[S.from];
      if (v.cls === "nocmp") {
        const why = !v.b ? `it was not a separate area in ${y0}` : v.b.none ? `it had no published threshold in ${y0}`
          : a.sh[S.from] !== a.sh[S.yi] ? "its boundaries changed in between" : S.from === S.yi ? "both years are the same" : "its threshold came from a different kind of Census figure";
        h += `<div class="src">No comparable change from ${y0} to ${y}: ${why}.</div>`;
      } else {
        h += `<table class="math"><tr><td>${y0}</td><td>${S.meas === "dol" ? usd(v.b.dol) : pc(v.b.pct)}</td></tr><tr><td>${y}</td><td>${S.meas === "dol" ? usd(v.c.dol) : pc(v.c.pct)}</td></tr>`
          + `<tr class="eq"><td>Change</td><td>${fmt(v.v)}</td></tr></table>`;
      }
      if (!full) return h;
      h += `<div class="src">${y} in detail:</div>`;
    }
    h += mathTable(a, S.yi, v.c);
    h += `<div class="src">Income is ${pc(v.c.pct)} of the threshold plus the cushion. ${esc(sourceLine(a, S.yi))}</div>`;
    return h;
  }

  // ---------- tooltip ----------
  const tip = $("tip");
  function showTip(a, sx, sy) {
    const v = vals.get(a.id);
    tip.innerHTML = `<b>${esc(label(a))}</b>` + body(a, v, false);
    tip.hidden = false;
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = sx + 14, y = sy + 14;
    if (x + tw > W - 6) x = sx - tw - 14;
    if (y + th > H - 6) y = sy - th - 14;
    tip.style.left = Math.max(4, x) + "px"; tip.style.top = Math.max(4, y) + "px";
  }
  function hideTip() { tip.hidden = true; }

  // ---------- detail card with history chart ----------
  // Income at the chosen percentile against threshold plus cushion, every year the area exists.
  function spark(a) {
    const P = [];
    for (let i = 0; i < NY; i++) { const c = calc(a, i); if (c) P.push({ i, y: YEARS[i], inc: c.inc, need: c.none ? null : c.thr + S.cush, sh: a.sh[i] }); }
    if (!P.length) return "";
    const w = 300, h = 104, l = 38, r = 16, t = 8, b = 18;
    const xs = (y) => l + ((y - YEARS[0]) / (YEARS[NY - 1] - YEARS[0])) * (w - l - r);
    const all = P.flatMap((p) => (p.need === null ? [p.inc] : [p.inc, p.need]));
    const step = 20000, lo = Math.floor(Math.min(...all) / step) * step, hi = Math.max(lo + step, Math.ceil(Math.max(...all) / step) * step);
    const ys = (v) => t + (1 - (v - lo) / (hi - lo)) * (h - t - b);
    const line = (key) => {
      let d = "", prev = null;
      for (const p of P) {
        if (p[key] === null) { prev = null; continue; }
        // a line never runs across a missing year or a boundary change
        const brk = !prev || p.y - prev.y > 1 || p.sh !== prev.sh;
        d += `${brk ? "M" : "L"}${xs(p.y).toFixed(1)},${ys(p[key]).toFixed(1)}`;
        prev = p;
      }
      return d;
    };
    const ticks = [lo, (lo + hi) / 2, hi];
    const grid = ticks.map((v) => `<line x1="${l}" x2="${w - r}" y1="${ys(v)}" y2="${ys(v)}" stroke="var(--grid)"/><text x="${l - 4}" y="${ys(v) + 3.5}" text-anchor="end" font-size="10" fill="var(--ink-3)">$${v / 1000}k</text>`).join("");
    const xl = [YEARS[0], 2020, YEARS[NY - 1]].map((y) => `<text x="${xs(y)}" y="${h - 4}" text-anchor="middle" font-size="10" fill="var(--ink-3)">${y}</text>`).join("");
    let marks = "";
    for (let j = 1; j < P.length; j++) if (P[j].sh !== P[j - 1].sh) { const x = xs(P[j].y - 0.5); marks += `<line x1="${x}" x2="${x}" y1="${t}" y2="${h - b}" stroke="var(--ink-3)" stroke-dasharray="2 3"/>`; }
    const cur = P.find((p) => p.i === S.yi);
    const dots = P.map((p) => `<circle cx="${xs(p.y).toFixed(1)}" cy="${ys(p.inc).toFixed(1)}" r="${p === cur ? 4 : 2}" fill="var(--accent)"${p === cur ? ' stroke="var(--panel)" stroke-width="1.5"' : ""}/>`).join("");
    return `<div class="key"><i></i>Income<i class="need"></i>Threshold plus cushion</div>`
      + `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="Income and threshold plus cushion by year, ${esc(a.n)}">${grid}${xl}${marks}`
      + `<path d="${line("need")}" fill="none" stroke="var(--need)" stroke-width="2" stroke-dasharray="5 3"/>`
      + `<path d="${line("inc")}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/>${dots}</svg>`;
  }
  function historyNote(a) {
    const have = []; for (let i = 0; i < NY; i++) if (a.w[i]) have.push(i);
    const notes = [];
    if (have.length < NY) notes.push(`In the wage data as a separate area from ${YEARS[have[0]]} to ${YEARS[have[have.length - 1]]}.`);
    const ch = []; for (let j = 1; j < have.length; j++) if (a.sh[have[j]] !== a.sh[have[j - 1]]) ch.push(YEARS[have[j]]);
    if (ch.length) notes.push(`Boundaries redrawn in ${ch.join(" and ")} (dotted line); figures before and after cover different places.`);
    const st = have.filter((i) => kindOf(a, i) === "s").map((i) => YEARS[i]), no = have.filter((i) => kindOf(a, i) === "x").map((i) => YEARS[i]);
    const es = have.filter((i) => kindOf(a, i) === "e").map((i) => YEARS[i]);
    const span = (ys) => (ys.length === 1 ? `${ys[0]}` : ys[ys.length - 1] - ys[0] === ys.length - 1 ? `${ys[0]} to ${ys[ys.length - 1]}` : ys.join(", "));
    if (st.length && st.length < have.length) notes.push(`Threshold is the state's smaller-metro figure in ${span(st)}.`);
    if (es.length && es.length < have.length) notes.push(`Threshold is our rent-based estimate in ${span(es)}, and a Census figure for this metro in the other years.`);
    if (no.length) notes.push(`No published threshold in ${span(no)}.`);
    return notes.join(" ");
  }
  function showDetail(a) {
    const el = $("detail");
    if (!a) { el.innerHTML = `<h2>Area</h2><div class="empty">Hover over or tap an area to see the math and its history. The test: one income, less the local poverty threshold for two adults and two children, less money set aside for surprise expenses.</div>`; return; }
    const v = vals.get(a.id);
    let big = "";
    if (shaded(v)) big = S.mode === "year" ? (S.meas === "dol" ? verdict(v.c) : `${pc(v.v)} of what the family needs`) : `${fmt(v.v)} since ${YEARS[S.from]}`;
    el.innerHTML = `<h2>Area</h2><div class="name">${esc(label(a))}</div><div class="meta">${TYPE_NAME[a.t]} &middot; ${DATA.states[a.s][1]} &middot; ${YEARS[S.yi]}</div>`
      + (big ? `<div class="big">${big}</div>` : "") + body(a, v, true) + spark(a) + `<div class="hist">${esc(historyNote(a))}</div>`;
  }

  // ---------- legend ----------
  function legend() {
    const el = $("legend");
    const y = YEARS[S.yi], bins = BINS[S.mode === "year" ? S.meas : S.meas + "Chg"];
    let title, edges, ends;
    if (S.mode === "year") {
      title = S.meas === "dol" ? `Excess or shortfall, ${y}` : `Income as % of threshold + cushion, ${y}`;
      edges = bins.map((b) => (S.meas === "dol" ? (b < 0 ? MINUS : "+") + "$" + Math.abs(b) / 1000 + "k" : b + "%"));
      ends = ["Falls short", "Has room"];
    } else {
      title = S.meas === "dol" ? `Change in dollars, ${YEARS[S.from]} to ${y}` : `Change in points, ${YEARS[S.from]} to ${y}`;
      edges = bins.map((b) => (b < 0 ? MINUS : "+") + (S.meas === "dol" ? "$" + Math.abs(b) / 1000 + "k" : Math.abs(b)));
      ends = ["Got worse", "Got better"];
    }
    let h = `<h2>${esc(title)}</h2><div class="unit" style="display:flex;justify-content:space-between"><span>${ends[0]}</span><span>${ends[1]}</span></div>`
      + `<div class="strip">${C.div.map((c) => `<span style="background:${c}"></span>`).join("")}</div>`
      + `<div class="ticks">${edges.map((t, i) => `<span style="left:${((i + 1) / C.div.length) * 100}%">${t}</span>`).join("")}</div>`;
    h += `<div class="row"><span class="sw" style="background:repeating-linear-gradient(135deg,${C.div[3]} 0 3px,${C.mark} 3px 4px)"></span>${S.est ? "Threshold is our estimate from local rents" : "Metro on a state-level threshold"}</div>`;
    h += `<div class="row"><span class="sw" style="background:repeating-linear-gradient(135deg,transparent 0 3px,${C.hatch} 3px 4.5px),repeating-linear-gradient(45deg,${C.nohist} 0 3px,${C.hatch} 3px 4.5px)"></span>${S.mode === "year" ? "No published threshold" : "No comparable figure"}</div>`;
    el.innerHTML = h;
  }

  // ---------- headline ----------
  function headline() {
    const where = S.st ? DATA.states[S.st][1] : "United States";
    const y = YEARS[S.yi];
    const setup = `${PCT_NAME[S.p]} earner, ${TEN_NAME[S.ten]}, ${usd(S.cush)} for surprise expenses`;
    let n = 0, short = 0, jobs = 0, shortJobs = 0, up = 0, down = 0;
    for (const a of A) {
      if (S.st && a.s !== S.st) continue;
      const v = vals.get(a.id);
      if (!shaded(v)) continue;
      n++;
      if (S.mode === "year") {
        const e = a.e[S.yi] || 0;
        jobs += e;
        if (v.c.dol < 0) { short++; shortJobs += e; }
      } else { if (v.v > 0) up++; if (v.v < 0) down++; }
    }
    if (!n) { $("sub").textContent = `${where}, ${y}: no areas with a figure for this view.`; return; }
    $("sub").textContent = S.mode === "year"
      ? `${where}, ${y}, ${setup}: one income falls short in ${nf.format(short)} of ${nf.format(n)} areas, which hold ${pc((100 * shortJobs) / jobs)} of the jobs.`
      : `${where}, ${YEARS[S.from]} to ${y}, ${setup}: of ${nf.format(n)} areas with comparable figures, the result improved in ${nf.format(up)} and worsened in ${nf.format(down)}.`;
  }

  // ---------- rankings ----------
  function rankings() {
    const el = $("rank");
    const tabs = S.mode === "year" ? ["Largest shortfall", "Most room"] : ["Got worse", "Got better"];
    const rows = [];
    for (const a of A) {
      if (S.st && a.s !== S.st) continue;
      const v = vals.get(a.id);
      if (shaded(v)) rows.push([a, v]);
    }
    const sign = S.rankTab === 0 ? 1 : -1;
    rows.sort((x, y) => sign * (x[1].v - y[1].v) || x[0].n.localeCompare(y[0].n));
    let h = `<h2>Rankings</h2><div class="tabs">${tabs.map((t, i) => `<button type="button" data-t="${i}" aria-pressed="${i === S.rankTab}">${t}</button>`).join("")}</div>`;
    h += `<p class="scope">${esc(S.st ? DATA.states[S.st][1] : "All states")}, ${S.mode === "year" ? YEARS[S.yi] : `${YEARS[S.from]} to ${YEARS[S.yi]}`}. ${nf.format(rows.length)} areas.</p>`;
    if (rows.length < 3) h += `<p class="msg">Not enough areas to rank here.</p>`;
    else h += "<table>" + rows.slice(0, TOP_N).map(([a, v], i) => {
      const sub = S.mode === "year" ? `${usd(v.c.inc)} income, ${usd(v.c.thr)} threshold` : `${S.meas === "dol" ? usd(v.b.dol) : pc(v.b.pct)} to ${S.meas === "dol" ? usd(v.c.dol) : pc(v.c.pct)}`;
      return `<tr data-id="${a.id}"${S.sel === a ? ' class="sel"' : ""}><td class="r">${i + 1}</td><td>${esc(label(a))}<br><small>${sub}</small></td><td class="n">${fmt(v.v)}</td></tr>`;
    }).join("") + "</table>";
    el.innerHTML = h;
    el.querySelectorAll(".tabs button").forEach((b) => (b.onclick = () => { S.rankTab = +b.dataset.t; rankings(); }));
    el.querySelectorAll("tr[data-id]").forEach((tr) => (tr.onclick = () => select(byId.get(tr.dataset.id), true)));
  }

  // ---------- selection ----------
  function select(a, zoom) {
    S.sel = a;
    showDetail(a);
    const s = shapeOf(a);
    if (s && zoom) {
      const pad = Math.max(s.bb[2] - s.bb[0], s.bb[3] - s.bb[1]) * 1.5;
      fitBox([s.bb[0] - pad, s.bb[1] - pad, s.bb[2] + pad, s.bb[3] + pad], 0.05, homeK * 40);
    }
    rankings();
    if (s && zoom) draw(); else drawOverlay();
  }

  // ---------- controls ----------
  function press(on, off) { $(on).setAttribute("aria-pressed", "true"); $(off).setAttribute("aria-pressed", "false"); }
  function setMode(m) {
    S.mode = m; S.rankTab = 0;
    if (m === "year") press("vYear", "vChange"); else press("vChange", "vYear");
    $("fromCtl").hidden = m !== "change";
    $("yearLab").textContent = m === "change" ? "To" : "Year";
    update();
  }
  function update() {
    if (S.hover && !shapeOf(S.hover)) { S.hover = null; hideTip(); }
    computeVals(); legend(); headline(); rankings(); showDetail(S.hover || S.sel);
    $("yearOut").textContent = YEARS[S.yi];
    $("cushOut").textContent = usd(S.cush);
    draw();
  }
  $("vYear").onclick = () => { stopPlay(); setMode("year"); };
  $("vChange").onclick = () => { stopPlay(); setMode("change"); };
  $("mDol").onclick = () => { S.meas = "dol"; press("mDol", "mPct"); update(); };
  $("mPct").onclick = () => { S.meas = "pct"; press("mPct", "mDol"); update(); };
  $("pct").onchange = () => { S.p = +$("pct").value; update(); };
  $("ten").onchange = () => { S.ten = +$("ten").value; update(); };
  $("est").onchange = () => { S.est = $("est").value === "1"; update(); };
  $("cush").oninput = () => { S.cush = +$("cush").value; update(); };
  const yr = $("year");
  yr.max = NY - 1; yr.value = S.yi;
  yr.oninput = () => { S.yi = +yr.value; update(); };
  let playT = null, speed = 1;
  const STEP_MS = 1000;
  function stopPlay() { if (playT) { clearInterval(playT); playT = null; $("play").textContent = "Play"; } }
  function startTimer() {
    clearInterval(playT);
    playT = setInterval(() => { if (S.yi >= NY - 1) return stopPlay(); S.yi++; yr.value = S.yi; update(); }, STEP_MS / speed);
  }
  $("play").onclick = () => {
    if (playT) return stopPlay();
    if (S.yi === NY - 1) S.yi = S.mode === "change" ? Math.min(NY - 1, S.from + 1) : 0;
    $("play").textContent = "Pause";
    yr.value = S.yi; update();
    startTimer();
  };
  $("speed").onclick = () => {
    speed = speed === 3 ? 1 : speed + 1;
    $("speed").textContent = speed + "x";
    $("speed").setAttribute("aria-label", `Play speed ${speed} times`);
    if (playT) startTimer();
  };
  const fromSel = $("from");
  YEARS.forEach((y, i) => fromSel.add(new Option(y, i)));
  fromSel.value = S.from;
  fromSel.onchange = () => { S.from = +fromSel.value; update(); };
  const stSel = $("state");
  Object.entries(DATA.states).sort((a, b) => a[1][1].localeCompare(b[1][1])).forEach(([f, [ab, nm]]) => stSel.add(new Option(nm, f)));
  stSel.onchange = () => { S.st = stSel.value; home(); update(); };
  $("reset").onclick = () => {
    stopPlay(); S.st = ""; stSel.value = ""; S.sel = null; S.hover = null; S.yi = NY - 1; yr.value = S.yi;
    S.p = 2; $("pct").value = 2; S.ten = 0; $("ten").value = 0; S.cush = 10000; $("cush").value = 10000; S.meas = "dol"; press("mDol", "mPct"); S.est = true; $("est").value = "1";
    S.from = 0; fromSel.value = 0; hideTip(); home(); setMode("year");
  };

  // search: areas in the selected year's boundaries first, then the rest
  const q = $("q"), lb = $("lb");
  const searchIdx = A.map((a) => [a, (a.n + " " + DATA.states[a.s][0] + " " + DATA.states[a.s][1]).toLowerCase()]);
  let hits = [], act = -1;
  function renderLb() {
    lb.innerHTML = hits.map((a, i) => `<li role="option" id="o${i}" data-i="${i}" aria-selected="${i === act}">${esc(label(a))}${shapeOf(a) ? "" : ` <small>not in ${YEARS[S.yi]}</small>`}</li>`).join("");
    lb.hidden = !hits.length; q.setAttribute("aria-expanded", String(!!hits.length));
    lb.querySelectorAll("li").forEach((li) => (li.onmousedown = (e) => { e.preventDefault(); choose(hits[+li.dataset.i]); }));
  }
  function choose(a) {
    q.value = a.n; hits = []; renderLb();
    if (!shapeOf(a)) { for (let i = NY - 1; i >= 0; i--) if (a.w[i]) { S.yi = i; yr.value = i; break; } update(); }
    select(a, true);
  }
  q.oninput = () => {
    const t = q.value.trim().toLowerCase();
    act = -1;
    const m = t.length < 2 ? [] : searchIdx.filter(([a, s]) => s.includes(t) && (!S.st || a.s === S.st)).map((x) => x[0]);
    hits = m.filter((a) => shapeOf(a)).concat(m.filter((a) => !shapeOf(a))).slice(0, 12);
    renderLb();
  };
  q.onkeydown = (e) => {
    if (e.key === "ArrowDown" && hits.length) { act = Math.min(hits.length - 1, act + 1); renderLb(); e.preventDefault(); }
    else if (e.key === "ArrowUp" && hits.length) { act = Math.max(0, act - 1); renderLb(); e.preventDefault(); }
    else if (e.key === "Enter" && hits.length) { choose(hits[Math.max(0, act)]); e.preventDefault(); }
    else if (e.key === "Escape") { hits = []; renderLb(); }
  };
  q.onblur = () => setTimeout(() => { hits = []; renderLb(); }, 100);

  const mq = window.matchMedia("(prefers-color-scheme: dark)");
  (mq.addEventListener ? mq.addEventListener("change", () => { readColors(); update(); }) : null);

  // ---------- start ----------
  readColors();
  const hs = hashFlags;
  if (hs.get("y") && YEARS.includes(+hs.get("y"))) { S.yi = YEARS.indexOf(+hs.get("y")); yr.value = S.yi; }
  if (hs.get("p") && +hs.get("p") >= 0 && +hs.get("p") <= 4) { S.p = +hs.get("p"); $("pct").value = S.p; }
  if (hs.get("c") && +hs.get("c") >= 0 && +hs.get("c") <= 25000) { S.cush = +hs.get("c"); $("cush").value = S.cush; }
  if (hs.get("m") === "pct") { S.meas = "pct"; press("mPct", "mDol"); }
  if (hs.get("est") === "0") { S.est = false; $("est").value = "0"; }
  computeVals();
  $("loading").remove();
  new ResizeObserver(resize).observe(wrap);
  if (hs.get("view") === "change") setMode("change"); else update();
  if (hs.get("debug") === "1") window.__ssdbg = { S, vals: () => vals, calc, byId, hoverAt, select, update, view };
  if (hs.get("a") && byId.get(hs.get("a"))) { pendingSel = byId.get(hs.get("a")); if (W) { select(pendingSel, true); pendingSel = null; } }
})().catch((e) => {
  const s = document.getElementById("sub");
  if (s) s.textContent = "The map could not load: " + e.message;
  throw e;
});

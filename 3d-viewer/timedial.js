// timedial.js — the 24-hour dial behind the sky simulation's "Time" control (HKS-115)
//
// A ring you drag around instead of a left-to-right slider: noon at the top, midnight
// at the bottom, 06 on the left and 18 on the right, so the handle sweeps east → west
// the way the sun does over Hong Kong. The band is painted with the sky colour the
// simulation itself renders at each quarter-hour of the selected date
// (skyColour ∘ sunPosition), so sunrise, the golden hour and the length of the night
// read straight off the control and drift with the season; two thin marks pick out
// the exact sunrise and sunset minutes.
//
// The hidden <input type="range" id="skytime"> stays the single source of truth: the
// dial writes its value and dispatches 'input' while you drag, so everything that
// already drives that input (URL state, setSkyControl, Stargaze's tray proxy) keeps
// working untouched. sync() is cheap — the ring is rebuilt only when the date or the
// UI theme changes; otherwise it just moves the handle and the readout.
const CX = 80, CY = 80, R_OUT = 70, R_IN = 58, R_KNOB = 64, SEG = 96;   // viewBox 160 × 160 · 15-minute segments
const NS = 'http://www.w3.org/2000/svg';
const ang = m => (m / 1440) * Math.PI * 2 + Math.PI;                    // minutes → radians clockwise from the top; noon (720) → 0
const pt = (r, a) => [CX + r * Math.sin(a), CY - r * Math.cos(a)];
const f2 = v => v.toFixed(2);
const el = (tag, attrs = {}) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };
const wrap = m => ((Math.round(m) % 1440) + 1440) % 1440;
// annular sector between two angles (always well under a half turn → large-arc flag 0)
function sector(a0, a1, rIn, rOut) {
  const [x0, y0] = pt(rOut, a0), [x1, y1] = pt(rOut, a1), [x2, y2] = pt(rIn, a1), [x3, y3] = pt(rIn, a0);
  return `M${f2(x0)} ${f2(y0)}A${rOut} ${rOut} 0 0 1 ${f2(x1)} ${f2(y1)}L${f2(x2)} ${f2(y2)}A${rIn} ${rIn} 0 0 0 ${f2(x3)} ${f2(y3)}Z`;
}

/**
 * @param {object} o
 * @param {HTMLInputElement} o.input   the hidden #skytime range — the state
 * @param {HTMLElement} o.readout      the HH:MM element shown in the dial's centre
 * @param {HTMLElement} o.mount        the .tdial container (role=slider)
 * @param {() => number} o.minutesNow  minutes to show: real HKT when the sky is live, else the fixed instant
 * @param {() => string} o.dateStr     YYYY-MM-DD the ring is painted for
 * @param {() => boolean} o.isPaper    light UI theme?
 * @param {(date: string, minutes: number) => number} o.sunAltDeg   sun altitude in degrees at that instant
 * @param {(date: string) => {rise: number|null, set: number|null}} o.riseSet   sunrise / sunset in HKT minutes
 * @param {(altDeg: number, paper: boolean) => string} o.skyHex     the sky colour the sim renders for that altitude
 * @param {(minutes: number) => string} o.fmt   minutes → "HH:MM"
 * @param {() => void} [o.onScrub]     fired once per pointer scrub (analytics)
 */
export function createTimeDial({ input, readout, mount, minutesNow, dateStr, isPaper, sunAltDeg, riseSet, skyHex, fmt, onScrub }) {
  const svg = el('svg', { viewBox: '0 0 160 160', 'aria-hidden': 'true', focusable: 'false' });
  const gRing = el('g'), gTicks = el('g'), gRise = el('g');
  const spoke = el('line', { class: 'spoke' });
  const knob = el('circle', { class: 'knob', r: 7 });
  svg.append(gRing, el('circle', { class: 'edge', cx: CX, cy: CY, r: R_OUT }), el('circle', { class: 'edge', cx: CX, cy: CY, r: R_IN }), gTicks, gRise, spoke, knob);
  mount.prepend(svg);

  // hour ticks, longer at the quarters, with 00 · 06 · 12 · 18 inside them
  for (let h = 0; h < 24; h++) {
    const a = ang(h * 60), q = h % 6 === 0;
    const [x0, y0] = pt(q ? 49 : 52.5, a), [x1, y1] = pt(56, a);
    gTicks.append(el('line', { class: q ? 'tk q' : 'tk', x1: f2(x0), y1: f2(y0), x2: f2(x1), y2: f2(y1) }));
    if (q) {
      const [lx, ly] = pt(41, a);
      const t = el('text', { class: 'hl', x: f2(lx), y: f2(ly + 3), 'text-anchor': 'middle' });
      t.textContent = String(h).padStart(2, '0');
      gTicks.append(t);
    }
  }
  // the sky band: 96 quarter-hour sectors (a hair of overlap hides the seams)
  const segs = [];
  for (let i = 0; i < SEG; i++) { const s = el('path', { d: sector(ang(i * 15), ang((i + 1) * 15 + 0.6), R_IN, R_OUT) }); segs.push(s); gRing.append(s); }

  let ringKey = '';
  function paintRing() {
    const d = dateStr(), paper = isPaper(), key = d + '|' + paper;
    if (key === ringKey) return;
    ringKey = key;
    for (let i = 0; i < SEG; i++) segs[i].setAttribute('fill', skyHex(sunAltDeg(d, i * 15 + 7), paper));
    gRise.replaceChildren();
    const rs = riseSet(d);
    for (const m of [rs.rise, rs.set]) {
      if (m == null || !isFinite(m)) continue;
      const a = ang(m), [x0, y0] = pt(R_IN - 1.5, a), [x1, y1] = pt(R_OUT + 1.5, a);
      gRise.append(el('line', { class: 'rs', x1: f2(x0), y1: f2(y0), x2: f2(x1), y2: f2(y1) }));
    }
  }
  let shown = -1;
  function place(m) {
    if (m === shown) return;
    shown = m;
    const a = ang(m), [kx, ky] = pt(R_KNOB, a), [sx, sy] = pt(24, a), [ex, ey] = pt(R_IN - 3, a);
    knob.setAttribute('cx', f2(kx)); knob.setAttribute('cy', f2(ky));
    knob.setAttribute('fill', skyHex(sunAltDeg(dateStr(), m), isPaper()));
    spoke.setAttribute('x1', f2(sx)); spoke.setAttribute('y1', f2(sy)); spoke.setAttribute('x2', f2(ex)); spoke.setAttribute('y2', f2(ey));
    readout.textContent = fmt(m);
    mount.setAttribute('aria-valuenow', String(m));
    mount.setAttribute('aria-valuetext', fmt(m));
  }
  // read the world: greyed when the range is (live / off), handle at the sim's minute
  function sync() {
    const off = input.disabled;
    mount.classList.toggle('off', off);
    mount.setAttribute('aria-disabled', off ? 'true' : 'false');
    mount.tabIndex = off ? -1 : 0;
    paintRing();
    place(wrap(minutesNow()));
  }
  // write the world: the range gets the value, its listeners do the rest, the handle moves at once
  function commit(m) {
    m = wrap(m);
    input.value = String(m);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    place(m);
  }
  // pointer: grab anywhere on the dial — the bearing from the centre is the time, in 5-minute steps
  let dragging = false;
  const minutesAt = ev => {
    const b = mount.getBoundingClientRect();
    const dx = ev.clientX - (b.left + b.width / 2), dy = ev.clientY - (b.top + b.height / 2);
    const a = Math.atan2(dx, -dy);                             // clockwise from the top, −π..π
    return wrap(Math.round((((a - Math.PI) / (Math.PI * 2)) * 1440) / 5) * 5);
  };
  mount.addEventListener('pointerdown', ev => {
    if (input.disabled || ev.button !== 0) return;
    dragging = true;
    mount.classList.add('drag');
    mount.setPointerCapture(ev.pointerId);
    mount.focus({ preventScroll: true });
    commit(minutesAt(ev));
    ev.preventDefault();
  });
  mount.addEventListener('pointermove', ev => { if (dragging) commit(minutesAt(ev)); });
  const release = () => { if (!dragging) return; dragging = false; mount.classList.remove('drag'); onScrub && onScrub(); };
  mount.addEventListener('pointerup', release);
  mount.addEventListener('pointercancel', release);
  // keyboard: ← → ±5 min · Shift ±30 · Alt ±1 · PageUp / PageDown ±1 h · Home midnight · End noon
  mount.addEventListener('keydown', ev => {
    if (input.disabled) return;
    const m = +input.value || 0;
    let d = 0;
    switch (ev.key) {
      case 'ArrowRight': case 'ArrowUp':   d = ev.shiftKey ? 30 : ev.altKey ? 1 : 5; break;
      case 'ArrowLeft':  case 'ArrowDown': d = -(ev.shiftKey ? 30 : ev.altKey ? 1 : 5); break;
      case 'PageUp':   d = 60; break;
      case 'PageDown': d = -60; break;
      case 'Home': commit(0);   ev.preventDefault(); return;
      case 'End':  commit(720); ev.preventDefault(); return;
      default: return;
    }
    commit(m + d);
    ev.preventDefault();
  });
  return { sync, place };
}

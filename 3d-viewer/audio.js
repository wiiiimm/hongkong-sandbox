// audio.js — procedural weather ambience for the Hong Kong Sandbox viewer.
//
// Everything is SYNTHESIZED with the Web Audio API — no samples, no assets,
// no licensing: rain / wind / waves / fog are shaped noise loops whose gains
// crossfade with the live weather intensities, and thunder is a one-shot
// enveloped rumble (with a crack for close strikes) fired per lightning
// strike. Call initAudio() from a user gesture (autoplay policy); the mix is
// driven from outside via setWeatherMix() so this module knows nothing about
// the scene.

let ctx = null, master = null, muffle = null, layers = null, enabled = false;
let masterVol = 0.6;

const AC = () => window.AudioContext || window.webkitAudioContext;
export const audioSupported = () => !!AC();

// 2 s of looping white noise — the raw material for every ambient layer
function noiseBuffer(seconds = 2) {
  const buf = ctx.createBuffer(1, ctx.sampleRate * seconds, ctx.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  return buf;
}

// oscillator → gain, wired into an AudioParam: base value ± depth at rate Hz
function lfo(param, base, depth, rateHz) {
  param.value = base;
  const osc = ctx.createOscillator(); osc.frequency.value = rateHz;
  const g = ctx.createGain(); g.gain.value = depth;
  osc.connect(g); g.connect(param); osc.start();
  return osc;
}

function makeLayer(shape) {
  const src = ctx.createBufferSource();
  src.buffer = noiseBuffer(); src.loop = true;
  const gain = ctx.createGain(); gain.gain.value = 0;
  let node = src;
  for (const f of shape) { node.connect(f); node = f; }
  node.connect(gain); gain.connect(muffle);
  src.start();
  return gain;
}

export function initAudio() {          // must be called from a user gesture
  if (ctx) { ctx.resume(); enabled = true; applyMaster(); return; }
  ctx = new (AC())();
  master = ctx.createGain(); master.gain.value = 0;      // faded in by applyMaster
  master.connect(ctx.destination);
  muffle = ctx.createBiquadFilter();                     // fog closes this down
  muffle.type = 'lowpass'; muffle.frequency.value = 20000;
  muffle.connect(master);

  const bp = (freq, q = 1) => { const f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = freq; f.Q.value = q; return f; };
  const lp = freq => { const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = freq; return f; };
  const hp = freq => { const f = ctx.createBiquadFilter(); f.type = 'highpass'; f.frequency.value = freq; return f; };

  layers = {
    rain: makeLayer([hp(1400), lp(9000)]),               // bright patter bed
    wind: null, waves: null,
  };
  // wind: deep swept howl — LFOs wobble the filter cutoff and gust the gain
  const windLp = lp(520);
  layers.wind = makeLayer([windLp]);
  lfo(windLp.frequency, 520, 180, 0.11);
  lfo(layers.wind.gain, 0, 0, 0.07);                     // depth driven in setWeatherMix
  layers._windGust = layers.wind.gain;
  // waves: slow low swell that laps at ~8 s period
  const waveLp = lp(420);
  layers.waves = makeLayer([waveLp]);
  layers._waveLfo = lfo(layers.waves.gain, 0, 0, 0.125);
  enabled = true;
  applyMaster();
}

function applyMaster() {
  if (!ctx) return;
  master.gain.setTargetAtTime(enabled ? masterVol : 0, ctx.currentTime, 0.25);
}

export function setEnabled(on) {
  enabled = on;
  if (!ctx) { if (on) initAudio(); return; }
  if (on) ctx.resume();
  applyMaster();                                        // fade instead of suspend: clean stop
}
export function isEnabled() { return enabled; }

export function setMasterVolume(v) { masterVol = Math.max(0, Math.min(1, v)); applyMaster(); }

// mix targets from the scene: { rain, wind, waves, fog } all 0..1-ish.
// τ = 0.6 s crossfades so live/storm transitions breathe instead of stepping.
export function setWeatherMix(m) {
  if (!ctx || !layers) return;
  const t = ctx.currentTime, TAU = 0.6;
  layers.rain.gain.setTargetAtTime(0.16 * m.rain, t, TAU);
  layers.wind.gain.setTargetAtTime(0.35 * m.wind, t, TAU);
  layers.waves.gain.setTargetAtTime(0.10 * m.waves, t, TAU);
  // fog muffles the whole mix rather than adding its own bed
  muffle.frequency.setTargetAtTime(m.fog > 0 ? 2200 : 20000, t, 0.8);
}

// aircraft engine (HKS-4): two detuned oscillators through a lowpass — pitch,
// brightness and volume all follow the throttle. level 0 spins it down.
let engine = null;
export function setEngine(level) {
  if (!ctx || !enabled) level = 0;
  if (level > 0 && !engine) {
    if (!ctx) return;
    const o1 = ctx.createOscillator(); o1.type = 'sawtooth';
    const o2 = ctx.createOscillator(); o2.type = 'triangle';
    const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 700;
    const g = ctx.createGain(); g.gain.value = 0;
    o1.connect(f); o2.connect(f); f.connect(g); g.connect(muffle);
    o1.start(); o2.start();
    engine = { o1, o2, f, g };
  }
  if (!engine) return;
  const t = ctx.currentTime;
  if (level <= 0) {
    engine.g.gain.setTargetAtTime(0, t, 0.25);
    const e = engine; engine = null;
    setTimeout(() => { try { e.o1.stop(); e.o2.stop(); } catch (_) {} }, 1200);
    return;
  }
  engine.o1.frequency.setTargetAtTime(68 + level * 65, t, 0.12);
  engine.o2.frequency.setTargetAtTime(34 + level * 32, t, 0.12);   // octave-down growl
  engine.f.frequency.setTargetAtTime(450 + level * 950, t, 0.12);
  engine.g.gain.setTargetAtTime(0.05 + level * 0.10, t, 0.15);
}

// ---- the UFO (HKS-113) -----------------------------------------------------
// A saucer must not growl like a turbofan, so it gets its own voice — still fully
// synthesized, no samples. It's the classic sci-fi theremin, built from three parts:
//
//   · TWO SINES a few Hz apart. The beat between them is the eerie, wavering wobble
//     that makes a theremin sound alive; a shared vibrato LFO bends both.
//   · A SUB sine under it all — the hull hum you feel more than hear.
//   · A WHIRR: a square through a tight resonant bandpass, amplitude-modulated, which
//     reads as the disc spinning. Its pitch tracks the throttle.
//
// `hover` deepens the vibrato: parked over a field the saucer wavers and moans;
// at speed the wobble tightens into a purposeful hum.
let ufoEng = null;
export function setUfoEngine(level, hover = 0) {
  if (!ctx || !enabled) level = 0;
  if (level > 0 && !ufoEng) {
    if (!ctx) return;
    const a = ctx.createOscillator(); a.type = 'sine';
    const b = ctx.createOscillator(); b.type = 'sine';
    const sub = ctx.createOscillator(); sub.type = 'sine'; sub.frequency.value = 46;
    // vibrato: one LFO bending BOTH sines together, so they stay in their beat
    const vib = ctx.createOscillator(); vib.type = 'sine'; vib.frequency.value = 5.2;
    const vibG = ctx.createGain(); vibG.gain.value = 6;              // ± Hz
    vib.connect(vibG); vibG.connect(a.frequency); vibG.connect(b.frequency);
    // the spinning disc
    const whirr = ctx.createOscillator(); whirr.type = 'square'; whirr.frequency.value = 120;
    const wf = ctx.createBiquadFilter(); wf.type = 'bandpass'; wf.frequency.value = 1500; wf.Q.value = 7;
    const wg = ctx.createGain(); wg.gain.value = 0;
    const trem = ctx.createOscillator(); trem.type = 'sine'; trem.frequency.value = 11;
    const tremG = ctx.createGain(); tremG.gain.value = 0.022;        // shallower than the base gain, so it never inverts phase
    trem.connect(tremG); tremG.connect(wg.gain);
    whirr.connect(wf); wf.connect(wg);
    const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 1900; f.Q.value = 3;
    const g = ctx.createGain(); g.gain.value = 0;
    a.connect(f); b.connect(f); sub.connect(f); wg.connect(f);
    f.connect(g); g.connect(muffle);
    for (const o of [a, b, sub, vib, whirr, trem]) o.start();
    ufoEng = { a, b, sub, vib, vibG, whirr, wg, trem, f, g };
  }
  if (!ufoEng) return;
  const t = ctx.currentTime;
  if (level <= 0) {
    ufoEng.g.gain.setTargetAtTime(0, t, 0.3);
    const e = ufoEng; ufoEng = null;                                 // null it NOW so a re-entry builds a fresh voice
    setTimeout(() => {
      try { for (const o of [e.a, e.b, e.sub, e.vib, e.whirr, e.trem]) o.stop(); } catch (_) {}
    }, 1400);
    return;
  }
  const base = 188 + level * 200;
  ufoEng.a.frequency.setTargetAtTime(base, t, 0.28);                 // slow glide: a theremin never snaps
  ufoEng.b.frequency.setTargetAtTime(base + 5.5, t, 0.28);           // …the 5.5 Hz beat against it
  ufoEng.vibG.gain.setTargetAtTime(3.5 + hover * 9, t, 0.35);        // hovering ⇒ a deeper, sicklier wobble
  ufoEng.whirr.frequency.setTargetAtTime(104 + level * 96, t, 0.22);
  ufoEng.wg.gain.setTargetAtTime(0.030 + level * 0.045, t, 0.22);
  ufoEng.f.frequency.setTargetAtTime(1200 + level * 1500, t, 0.25);
  ufoEng.g.gain.setTargetAtTime(0.05 + level * 0.11, t, 0.18);
}

// ---- the abduction (HKS-113) ------------------------------------------------
// Fired the instant a cow is caught in the beam. Two synthesized voices, no samples:
//
//   · The TRACTOR BEAM — noise through a bandpass sweeping UP, plus a sine glissando
//     rising underneath. Everything ascends, because the cow visibly rises and shrinks
//     over exactly this window: the sfx runs CATCH_MS (1.7 s), so the sound lands as
//     the animal disappears into the hull.
//   · The MOO — a startled one. A cow is a formant instrument: a sawtooth larynx driven
//     through two bandpass formants, with the first sweeping up and back down as the
//     mouth opens and closes ("mmMOOoo"). The pitch bends up in alarm, then sags.
//
// Each call is detuned a little, so a field of cattle doesn't moo in unison.
let abducting = 0;                                      // cap the chorus when a whole herd is taken
export function abductionSfx(ms = 1700) {
  if (!ctx || !enabled || abducting >= 4) return;       // 4 at once is a stampede; more is mush
  abducting++;
  setTimeout(() => { abducting--; }, ms);
  const t0 = ctx.currentTime, dur = ms / 1000;
  const rnd = (a, b) => a + Math.random() * (b - a);

  // --- the beam: everything rises
  const src = ctx.createBufferSource();
  src.buffer = noiseBuffer(2); src.loop = true;
  const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.Q.value = 3.5;
  bp.frequency.setValueAtTime(280, t0);
  bp.frequency.exponentialRampToValueAtTime(2600, t0 + dur);          // the sweep UP = the pull
  const bg = ctx.createGain();
  bg.gain.setValueAtTime(0.0001, t0);
  bg.gain.exponentialRampToValueAtTime(0.075, t0 + dur * 0.55);       // swells as it takes hold…
  bg.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);             // …then it's gone
  src.connect(bp); bp.connect(bg); bg.connect(muffle);
  src.start(t0); src.stop(t0 + dur + 0.05);

  // the glissando under it — the "suck"
  const gl = ctx.createOscillator(); gl.type = 'sine';
  gl.frequency.setValueAtTime(rnd(80, 100), t0);
  gl.frequency.exponentialRampToValueAtTime(rnd(620, 780), t0 + dur);
  const gg = ctx.createGain();
  gg.gain.setValueAtTime(0.0001, t0);
  gg.gain.exponentialRampToValueAtTime(0.055, t0 + dur * 0.7);
  gg.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  gl.connect(gg); gg.connect(muffle);
  gl.start(t0); gl.stop(t0 + dur + 0.05);

  // --- the moo: a startled cow, right as the beam grabs it
  const m0 = t0 + rnd(0.04, 0.16), mdur = rnd(0.75, 1.0);
  const f0 = rnd(112, 140);                                            // larynx
  const lar = ctx.createOscillator(); lar.type = 'sawtooth';
  lar.frequency.setValueAtTime(f0, m0);
  lar.frequency.linearRampToValueAtTime(f0 * 1.35, m0 + mdur * 0.28);  // …bends UP in alarm
  lar.frequency.linearRampToValueAtTime(f0 * 0.82, m0 + mdur);         // …then sags away
  // two formants make it a cow rather than a buzz; F1 opens and closes the mouth
  const f1 = ctx.createBiquadFilter(); f1.type = 'bandpass'; f1.Q.value = 4.5;
  f1.frequency.setValueAtTime(340, m0);
  f1.frequency.linearRampToValueAtTime(760, m0 + mdur * 0.3);          // "mm" → "OO"
  f1.frequency.linearRampToValueAtTime(300, m0 + mdur);                // → closed again
  const f2 = ctx.createBiquadFilter(); f2.type = 'bandpass'; f2.Q.value = 6;
  f2.frequency.value = rnd(1000, 1250);
  const mg = ctx.createGain();
  mg.gain.setValueAtTime(0.0001, m0);
  mg.gain.exponentialRampToValueAtTime(0.16, m0 + 0.09);               // sharp intake
  mg.gain.setTargetAtTime(0.10, m0 + 0.12, 0.25);
  mg.gain.exponentialRampToValueAtTime(0.0001, m0 + mdur);
  lar.connect(f1); lar.connect(f2);
  f1.connect(mg); f2.connect(mg); mg.connect(muffle);
  lar.start(m0); lar.stop(m0 + mdur + 0.05);
}

// one-shot rumble per strike. close: short delay, louder, with an initial
// crack; distant sheet lightning: long delay, soft low roll. vol (optional,
// 0..1, default 1) scales the rumble+crack peaks — HKS-68 passes the live
// lightning-field intensity at the camera so a storm across the territory
// rolls faintly while a cell overhead cracks at full level.
export function thunder(close, vol) {
  if (!ctx || !enabled) return;
  const v = Math.min(1, Math.max(0.05, vol ?? 1));   // floor keeps the exponential ramps legal
  const t0 = ctx.currentTime + (close ? 0.25 + Math.random() * 0.5 : 1.2 + Math.random() * 1.8);
  const dur = 2.2 + Math.random() * 1.8;
  const src = ctx.createBufferSource();
  src.buffer = noiseBuffer(4); src.loop = false;
  const f = ctx.createBiquadFilter(); f.type = 'lowpass';
  f.frequency.setValueAtTime(close ? 320 : 140, t0);
  f.frequency.exponentialRampToValueAtTime(60, t0 + dur);      // rumble darkens as it rolls
  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime((close ? 0.9 : 0.35) * v, t0 + 0.07);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  src.connect(f); f.connect(g); g.connect(muffle);
  src.start(t0); src.stop(t0 + dur + 0.1);
  if (close) {                                                  // the initial crack
    const c = ctx.createBufferSource(); c.buffer = src.buffer;
    const cf = ctx.createBiquadFilter(); cf.type = 'bandpass'; cf.frequency.value = 900; cf.Q.value = 0.7;
    const cg = ctx.createGain();
    cg.gain.setValueAtTime(0.0001, t0);
    cg.gain.exponentialRampToValueAtTime(0.5 * v, t0 + 0.02);
    cg.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.35);
    c.connect(cf); cf.connect(cg); cg.connect(muffle);
    c.start(t0); c.stop(t0 + 0.5);
  }
}

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

// one-shot rumble per strike. close: short delay, louder, with an initial
// crack; distant sheet lightning: long delay, soft low roll.
export function thunder(close) {
  if (!ctx || !enabled) return;
  const t0 = ctx.currentTime + (close ? 0.25 + Math.random() * 0.5 : 1.2 + Math.random() * 1.8);
  const dur = 2.2 + Math.random() * 1.8;
  const src = ctx.createBufferSource();
  src.buffer = noiseBuffer(4); src.loop = false;
  const f = ctx.createBiquadFilter(); f.type = 'lowpass';
  f.frequency.setValueAtTime(close ? 320 : 140, t0);
  f.frequency.exponentialRampToValueAtTime(60, t0 + dur);      // rumble darkens as it rolls
  const g = ctx.createGain();
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime(close ? 0.9 : 0.35, t0 + 0.07);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  src.connect(f); f.connect(g); g.connect(muffle);
  src.start(t0); src.stop(t0 + dur + 0.1);
  if (close) {                                                  // the initial crack
    const c = ctx.createBufferSource(); c.buffer = src.buffer;
    const cf = ctx.createBiquadFilter(); cf.type = 'bandpass'; cf.frequency.value = 900; cf.Q.value = 0.7;
    const cg = ctx.createGain();
    cg.gain.setValueAtTime(0.0001, t0);
    cg.gain.exponentialRampToValueAtTime(0.5, t0 + 0.02);
    cg.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.35);
    c.connect(cf); cf.connect(cg); cg.connect(muffle);
    c.start(t0); c.stop(t0 + 0.5);
  }
}

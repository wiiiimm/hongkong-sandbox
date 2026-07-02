/* glass-gl.js — reusable WebGL "liquid glass" engine (framework-agnostic).
 *
 * One fullscreen canvas refracts a BACKGROUND layer (image / canvas / video).
 * A canvas or video background is treated as "live" — re-uploaded every frame —
 * so animated backgrounds (Ken Burns, playing video) refract in real time.
 * Any DOM element you register() becomes a refracting glass surface: the engine
 * reads its screen rect every frame and draws the lens (rounded-rect mask →
 * droplet-profile refraction → blur → chromatic edge → vibrancy → directional
 * rim glint → frost) at that spot. Your content sits on top. To refract
 * text/graphics, bake them into the background.
 *
 *   const glass = createGlass({ canvas, background: '/bg.jpg' });
 *   glass.register(el);
 *   glass.setParams({ refraction: 0.22, blur: 1.2, ... });
 *   glass.unregister(el);  glass.destroy();
 *
 * Options: { dpr } — render at devicePixelRatio (clamped ≤2) so lenses stay
 * sharp on retina; on by default, pass a number for a custom cap or false for
 * legacy 1:1. { transparent: true } — draw ONLY the glass surfaces and leave
 * every other pixel transparent (premultiplied alpha), for when the background
 * you refract IS the page's own live canvas (e.g. a WebGL scene): the page
 * stays crisp and the engine composites just the lenses on top. Default mode
 * paints the background across the whole canvas (glass over a media backdrop).
 *
 * The effect needs a background to bend — that's the one rule of this technique.
 *
 * Copyright (C) 2026 wiiiimm
 * SPDX-License-Identifier: AGPL-3.0-or-later
 * This program is free software: you can redistribute it and/or modify it under
 * the terms of the GNU Affero General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your option) any
 * later version. See the bundled LICENSE file. Distributed WITHOUT ANY WARRANTY.
 */

const MAX = 16; // max simultaneous glass surfaces (shader array size)

// The fragment shader is compiled per-instance: transparent mode drops the
// fullscreen background fetch and outputs premultiplied alpha instead of
// repainting the backdrop, so the host page's own pixels show through crisp.
const FRAG = (transparent) => `
  precision highp float;
  const int MAX = ${MAX};
  uniform vec3  iResolution;
  uniform vec2  uImgRes;
  uniform vec2  uPos[MAX];
  uniform vec2  uHalf[MAX];
  uniform int   uCount;
  uniform float uBlur;     // blur sample spread (px)
  uniform float uLens;     // refraction strength
  uniform float uWhite;    // liquidness (mix toward tint)
  uniform float uEdge;     // edge-light strength
  uniform float uFrost;    // edge frost: rim width + brightness (0..1)
  uniform float uDisperse; // chromatic aberration: R/G/B split at the lens edge (0..1)
  uniform float uSat;      // vibrancy: saturation boost of the refracted backdrop (1 = off)
  uniform float uCurve;    // lens profile exponent: 1 = linear, ~3 = droplet (flat centre, steep rim)
  uniform vec2  uLightDir; // light direction for the specular rim glint (unit vector, y up)
  uniform float uRad[MAX]; // per-surface corner radius (px) — match each element's border-radius
  uniform vec3  uTint;     // milk colour
  uniform sampler2D iChannel0;

  vec2 coverUv(vec2 uv) {
    float ca = iResolution.x / iResolution.y;
    float ia = uImgRes.x / uImgRes.y;
    vec2 s = ca > ia ? vec2(1.0, ia / ca) : vec2(ca / ia, 1.0);
    return (uv - 0.5) * s + 0.5;
  }
  float sdRoundBox(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - b + r;
    return min(max(q.x, q.y), 0.0) + length(max(q, vec2(0.0))) - r;
  }

  void main() {
    vec2 frag = gl_FragCoord.xy;
    vec2 uv = frag / iResolution.xy;
    ${transparent ? "" : "vec4 bg = texture2D(iChannel0, coverUv(uv));"}

    float best = 1e9; vec2 bPos = vec2(0.0); vec2 bHalf = vec2(1.0); float bRad = 0.0;
    for (int i = 0; i < MAX; i++) {
      if (i < uCount) {
        float r = min(uRad[i], min(uHalf[i].x, uHalf[i].y));
        float d = sdRoundBox(frag - uPos[i], uHalf[i], r);
        if (d < best) { best = d; bPos = uPos[i]; bHalf = uHalf[i]; bRad = r; }
      }
    }

    float md = min(bHalf.x, bHalf.y);
    float lensField = 1.0 - clamp(-best / md, 0.0, 1.0);   // 0 centre → 1 edge
    float bodyMask = smoothstep(1.5, -1.5, best);          // crisp body
    float fw = mix(2.0, 20.0, uFrost);
    float rim = clamp(1.0 - abs(best + fw) / fw, 0.0, 1.0);

    vec4 color = ${transparent ? "vec4(0.0)" : "vec4(bg.rgb, 1.0)"};
    if (bodyMask > 0.0) {
      vec2 cuv = bPos / iResolution.xy;

      // droplet lens profile — a real liquid-glass blob is optically flat in the
      // middle and bends hard only near the rim. pow() reshapes the linear field:
      // curve 1 = old linear lens, ~2.5-3.5 = flat centre + steep rim (droplet).
      float prof = pow(lensField, max(uCurve, 1.0));
      vec2 lens = cuv + (uv - cuv) * (1.0 - prof * uLens);

      vec4 acc = vec4(0.0); float total = 0.0;
      for (float x = -4.0; x <= 4.0; x++) {
        for (float y = -4.0; y <= 4.0; y++) {
          vec2 off = vec2(x, y) * uBlur / iResolution.xy;
          acc += texture2D(iChannel0, coverUv(lens + off));
          total += 1.0;
        }
      }
      acc /= total;

      // chromatic aberration — split R/B along the radial direction by a small
      // FIXED offset (independent of surface size), weighted by the lens profile
      // so the fringe lives exactly where the bending is. White edges break into
      // colour, like real glass.
      if (uDisperse > 0.0) {
        vec2 dir = normalize(uv - cuv + vec2(1e-5));
        vec2 disp = dir * uDisperse * prof * 0.010;
        acc.r = texture2D(iChannel0, coverUv(lens + disp)).r;
        acc.b = texture2D(iChannel0, coverUv(lens - disp)).b;
      }

      // vibrancy — saturate the refracted backdrop so the glass reads luminous
      // (Apple materials do the same with backdrop saturate()).
      float luma = dot(acc.rgb, vec3(0.299, 0.587, 0.114));
      acc.rgb = mix(vec3(luma), acc.rgb, uSat);

      // specular rim lighting — surface normal from the SDF gradient, then a
      // bright glint on the rim facing the light and a soft shade opposite.
      // This directional pair is what makes the slab read as a physical object.
      vec2 e = vec2(1.5, 0.0);
      vec2 nrm = normalize(vec2(
        sdRoundBox(frag + e.xy - bPos, bHalf, bRad) - sdRoundBox(frag - e.xy - bPos, bHalf, bRad),
        sdRoundBox(frag + e.yx - bPos, bHalf, bRad) - sdRoundBox(frag - e.yx - bPos, bHalf, bRad)
      ) + vec2(1e-5));
      float band  = pow(lensField, 3.0);                                  // hug the rim
      float glint = pow(max(dot(nrm,  uLightDir), 0.0), 2.0) * band;
      float shade = pow(max(dot(nrm, -uLightDir), 0.0), 2.0) * band;
      float sheen = max(dot(normalize(uv - cuv + vec2(1e-5)), uLightDir), 0.0) * 0.06;

      // rim scales fully with uFrost (no hard-coded floor): edgeFrost 0 = NO rim band
      vec4 lighting = clamp(acc + vec4((glint * 0.55 - shade * 0.22 + sheen) * uEdge)
                                + vec4(rim) * (uFrost * 0.72), 0.0, 1.0);
      lighting = mix(lighting, vec4(uTint, 1.0), uWhite);
      color = ${transparent
        ? "vec4(lighting.rgb * bodyMask, bodyMask)"                 /* premultiplied */
        : "vec4(mix(bg, lighting, bodyMask).rgb, 1.0)"};
    }
    gl_FragColor = color;
  }
`;

const VERT = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;

const DEFAULT_PARAMS = {
  blur: 1.2,        // sample spread (px)
  refraction: 0.22, // lens strength
  liquidness: 0.0,  // 0..~0.6, mix toward tint
  edgeLight: 1.0,   // rim glint strength
  edgeFrost: 0.22,  // rim band 0..1
  dispersion: 0.0,  // chromatic aberration at the edge (0..1)
  saturation: 1.0,  // vibrancy of the refracted backdrop (1 = neutral, ~1.3 = luminous)
  curve: 2.5,       // lens profile: 1 = linear, ~2.5-3.5 = droplet (flat centre, steep rim)
  lightAngle: 0,    // degrees the rim glint comes from (0 = top, 90 = right)
  radius: 30,       // px — keep in sync with the element's border-radius
  tint: [1, 1, 1],  // milk colour (white = light glass)
};

export function createGlass({ canvas, background, params, dpr, transparent = false } = {}) {
  if (!canvas) throw new Error("createGlass: { canvas } is required");
  // alpha + premultipliedAlpha are the WebGL defaults, but transparent mode
  // depends on them for compositing with the page — state them explicitly.
  const gl = canvas.getContext("webgl", { preserveDrawingBuffer: true, alpha: true, premultipliedAlpha: true });
  if (!gl) throw new Error("createGlass: WebGL not available");

  const P = { ...DEFAULT_PARAMS, ...(params || {}) };

  // DPR-aware rendering: buffer at devicePixelRatio (clamped, default ≤2) so
  // the lens isn't soft on retina. { dpr: false | 0 } = legacy 1:1;
  // { dpr: n } = clamp to n. Re-read live — it changes across monitors.
  const DPR = () => (dpr === false || dpr === 0)
    ? 1
    : Math.min(window.devicePixelRatio || 1, typeof dpr === "number" ? dpr : 2);
  const surfaces = new Map();          // registered element -> opts ({ radius? })
  let imgW = 1600, imgH = 1000;
  let liveSource = null;               // canvas/video → re-uploaded every frame
  let raf = 0, alive = true;

  /* ---- program ---- */
  const compile = (type, src) => {
    const s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(s));
    return s;
  };
  const prog = gl.createProgram();
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG(!!transparent)));
  gl.linkProgram(prog); gl.useProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) console.error(gl.getProgramInfoLog(prog));

  const quad = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, quad);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const pLoc = gl.getAttribLocation(prog, "p");
  gl.enableVertexAttribArray(pLoc);
  gl.vertexAttribPointer(pLoc, 2, gl.FLOAT, false, 0, 0);

  const U = {};
  ["iResolution","uImgRes","uPos","uHalf","uCount","uBlur","uLens","uWhite",
   "uEdge","uFrost","uDisperse","uSat","uCurve","uLightDir","uRad","uTint","iChannel0"]
    .forEach(n => U[n] = gl.getUniformLocation(prog, n));

  /* ---- background texture ---- */
  const tex = gl.createTexture();
  function uploadTexture(src, w, h) {
    imgW = w; imgH = h;
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  }
  function proceduralBackground() {
    const c = document.createElement("canvas"); c.width = 1600; c.height = 1000;
    const x = c.getContext("2d");
    x.fillStyle = "#12152b"; x.fillRect(0, 0, 1600, 1000);
    [["#ff6b9d",240,200],["#ffd166",1360,260],["#06d6a0",1120,820],["#4d96ff",320,840]]
      .forEach(([col, cx, cy]) => {
        const g = x.createRadialGradient(cx, cy, 0, cx, cy, 560);
        g.addColorStop(0, col); g.addColorStop(1, "rgba(0,0,0,0)");
        x.fillStyle = g; x.fillRect(0, 0, 1600, 1000);
      });
    uploadTexture(c, 1600, 1000);
  }
  function setBackground(src) {
    liveSource = null;                 // reset; a live source re-arms it below
    if (!src) return proceduralBackground();
    if (typeof src === "string") {
      const im = new Image(); im.crossOrigin = "anonymous";
      im.onload = () => { try { uploadTexture(im, im.naturalWidth, im.naturalHeight); } catch (e) { proceduralBackground(); } };
      im.onerror = proceduralBackground;
      im.src = src;
    } else if (src instanceof HTMLImageElement) {
      if (src.complete && src.naturalWidth) uploadTexture(src, src.naturalWidth, src.naturalHeight);
      else { src.onload = () => uploadTexture(src, src.naturalWidth, src.naturalHeight); }
    } else if (src instanceof HTMLCanvasElement) {
      liveSource = src;                // canvas content changes → refresh each frame
      uploadTexture(src, src.width, src.height);
    } else if (src instanceof HTMLVideoElement) {
      liveSource = src;                // playing video → refresh each frame
      const up = () => {              // ignore if superseded/destroyed before it fires
        if (!alive || liveSource !== src) return;
        try { uploadTexture(src, src.videoWidth, src.videoHeight); } catch (e) {}
      };
      if (src.readyState >= 2) up();
      else src.addEventListener("loadeddata", up, { once: true });
    }
  }
  proceduralBackground();          // instant fill, replaced when the real bg loads
  setBackground(background);

  /* ---- sizing (matches buffer to display; fixes iOS 100vh ≠ innerHeight) ---- */
  function resize() {
    const w = window.innerWidth, h = window.innerHeight, d = DPR();
    canvas.width = Math.round(w * d); canvas.height = Math.round(h * d);   // buffer px
    canvas.style.width = w + "px"; canvas.style.height = h + "px";         // CSS px
  }
  resize();
  window.addEventListener("resize", resize);

  /* ---- render loop ---- */
  const posArr = new Float32Array(MAX * 2);
  const halfArr = new Float32Array(MAX * 2);
  const radArr = new Float32Array(MAX);
  function frame() {
    if (!alive) return;

    // live background (canvas / video): pull a fresh frame into the texture.
    // A failed upload (e.g. a tainted/cross-origin source) disables the live
    // refresh instead of throwing every frame — the last good frame stays.
    if (liveSource) {
      const isVid = (typeof HTMLVideoElement !== "undefined") && liveSource instanceof HTMLVideoElement;
      if (!isVid || liveSource.readyState >= 2) {
        const lw = liveSource.videoWidth || liveSource.width;
        const lh = liveSource.videoHeight || liveSource.height;
        if (lw && lh) { try { uploadTexture(liveSource, lw, lh); } catch (e) { liveSource = null; } }
      }
    }

    let n = 0;
    const d = DPR();                     // rects are CSS px → scale to buffer px
    surfaces.forEach((opts, el) => {
      if (n >= MAX) return;
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return; // hidden (display:none) — no stray lens at origin
      posArr[n*2]   = (r.left + r.width / 2) * d;
      posArr[n*2+1] = canvas.height - (r.top + r.height / 2) * d;  // flip y
      halfArr[n*2]   = (r.width / 2) * d + 2;                      // +2 slack in buffer px
      halfArr[n*2+1] = (r.height / 2) * d + 2;
      radArr[n]      = ((opts && opts.radius != null) ? opts.radius : P.radius) * d;
      n++;
    });

    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform3f(U.iResolution, canvas.width, canvas.height, 1);
    gl.uniform2f(U.uImgRes, imgW, imgH);
    gl.uniform2fv(U.uPos, posArr);
    gl.uniform2fv(U.uHalf, halfArr);
    gl.uniform1i(U.uCount, n);
    gl.uniform1f(U.uBlur, Math.max(0.001, P.blur) * d);   // blur in buffer px → resolution-independent frost
    gl.uniform1f(U.uLens, P.refraction);
    gl.uniform1f(U.uWhite, P.liquidness);
    gl.uniform1f(U.uEdge, P.edgeLight);
    gl.uniform1f(U.uFrost, P.edgeFrost);
    gl.uniform1f(U.uDisperse, P.dispersion);
    gl.uniform1f(U.uSat, P.saturation);
    gl.uniform1f(U.uCurve, P.curve);
    const la = (P.lightAngle || 0) * Math.PI / 180;              // 0° = top; y-up in GL
    gl.uniform2f(U.uLightDir, Math.sin(la), Math.cos(la));
    gl.uniform1fv(U.uRad, radArr);
    gl.uniform3f(U.uTint, P.tint[0], P.tint[1], P.tint[2]);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.uniform1i(U.iChannel0, 0);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    raf = requestAnimationFrame(frame);
  }
  raf = requestAnimationFrame(frame);

  /* ---- public API ---- */
  return {
    register(el, opts = {}) { surfaces.set(el, opts); return () => surfaces.delete(el); },
    unregister(el) { surfaces.delete(el); },
    clear()        { surfaces.clear(); },
    setParams(next) { Object.assign(P, next); },
    getParams()    { return { ...P }; },
    setBackground,
    destroy() {
      alive = false;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      surfaces.clear();
    },
  };
}

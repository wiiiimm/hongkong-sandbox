/* glass-gl.js — reusable WebGL "liquid glass" engine (framework-agnostic).
 *
 * One fullscreen canvas refracts a BACKGROUND layer (image / canvas / video).
 * A canvas or video background is treated as "live" — re-uploaded every frame —
 * so animated backgrounds (Ken Burns, playing video) refract in real time.
 * Any DOM element you register() becomes a refracting glass surface: the engine
 * reads its screen rect every frame and draws the lens (rounded-rect mask →
 * magnification → blur → chromatic edge → edge light/frost) at that spot. Your
 * content sits on top. To refract text/graphics, bake them into the background.
 *
 *   const glass = createGlass({ canvas, background: '/bg.jpg' });
 *   glass.register(el);
 *   glass.setParams({ refraction: 0.22, blur: 1.2, ... });
 *   glass.unregister(el);  glass.destroy();
 *
 * The effect needs a background to bend — that's the one rule of this technique.
 *
 * ---------------------------------------------------------------------------
 * VENDORED for hongkong-3d-model from https://github.com/wiiiimm/glass-gl
 * (packages/glass-gl/glass-gl.js @ 98d9591, MIT). Local patches, candidates
 * for upstreaming:
 *   1. DPR-aware buffer: canvas renders at devicePixelRatio (≤2) so the lens
 *      isn't soft on retina; rects/radius/blur scale to buffer px.
 *   2. Transparent outside the lens: the shader outputs premultiplied alpha
 *      and skips the fullscreen background copy, so the page's own (crisp)
 *      canvas shows through everywhere except the glass surfaces.
 *   3. Hidden elements (zero-size rects) are skipped instead of drawing a
 *      stray lens dot at the origin.
 *   4. edgeFrost 0 now means NO rim band (upstream keeps a 0.12 floor).
 * ---------------------------------------------------------------------------
 */

const MAX = 16; // max simultaneous glass surfaces (shader array size)

const FRAG = `
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

    float best = 1e9; vec2 bPos = vec2(0.0); vec2 bHalf = vec2(1.0);
    for (int i = 0; i < MAX; i++) {
      if (i < uCount) {
        float r = min(uRad[i], min(uHalf[i].x, uHalf[i].y));
        float d = sdRoundBox(frag - uPos[i], uHalf[i], r);
        if (d < best) { best = d; bPos = uPos[i]; bHalf = uHalf[i]; }
      }
    }

    float md = min(bHalf.x, bHalf.y);
    float lensField = 1.0 - clamp(-best / md, 0.0, 1.0);   // 0 centre → 1 edge
    float bodyMask = smoothstep(1.5, -1.5, best);          // crisp body
    float fw = mix(2.0, 20.0, uFrost);
    float rim = clamp(1.0 - abs(best + fw) / fw, 0.0, 1.0);

    // patch 2: transparent outside the lens (premultiplied alpha) — the page's
    // own background shows through crisp; only glass surfaces are drawn.
    vec4 color = vec4(0.0);
    if (bodyMask > 0.0) {
      vec2 cuv = bPos / iResolution.xy;
      vec2 lens = cuv + (uv - cuv) * (1.0 - lensField * uLens);

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
      // FIXED offset (independent of surface size), edge-weighted (lensField^2)
      // so only the rim fringes. White edges break into colour, like real glass.
      if (uDisperse > 0.0) {
        vec2 dir = normalize(uv - cuv + vec2(1e-5));
        vec2 disp = dir * uDisperse * lensField * lensField * 0.010;
        acc.r = texture2D(iChannel0, coverUv(lens + disp)).r;
        acc.b = texture2D(iChannel0, coverUv(lens - disp)).b;
      }

      float dy = clamp(uv.y - cuv.y, 0.0, 0.2);
      float grad = (dy + 0.05) * 0.6;
      // patch 4: rim scales fully with uFrost (no 0.12 floor) so 0 = no rim band
      vec4 lighting = clamp(acc + vec4(grad) * uEdge + vec4(rim) * uFrost * 0.72, 0.0, 1.0);
      lighting = mix(lighting, vec4(uTint, 1.0), uWhite);
      color = vec4(lighting.rgb * bodyMask, bodyMask);
    }
    gl_FragColor = color;
  }
`;

const VERT = `attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }`;

const DEFAULT_PARAMS = {
  blur: 1.2,        // sample spread (px)
  refraction: 0.22, // lens strength
  liquidness: 0.0,  // 0..~0.6, mix toward tint
  edgeLight: 1.0,   // top sheen
  edgeFrost: 0.22,  // rim band 0..1
  dispersion: 0.0,  // chromatic aberration at the edge (0..1)
  radius: 30,       // px — keep in sync with the element's border-radius
  tint: [1, 1, 1],  // milk colour (white = light glass)
};

export function createGlass({ canvas, background, params } = {}) {
  if (!canvas) throw new Error("createGlass: { canvas } is required");
  const gl = canvas.getContext("webgl", { preserveDrawingBuffer: true });
  if (!gl) throw new Error("createGlass: WebGL not available");

  const P = { ...DEFAULT_PARAMS, ...(params || {}) };
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
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG));
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
   "uEdge","uFrost","uDisperse","uRad","uTint","iChannel0"].forEach(n => U[n] = gl.getUniformLocation(prog, n));

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
  // patch 1: render at devicePixelRatio (≤2) so the lens stays sharp on retina
  const DPR = () => Math.min(window.devicePixelRatio || 1, 2);
  function resize() {
    const w = window.innerWidth, h = window.innerHeight, dpr = DPR();
    canvas.width = w * dpr; canvas.height = h * dpr;
    canvas.style.width = w + "px"; canvas.style.height = h + "px";
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
    const dpr = DPR();                 // patch 1: rects → buffer px
    surfaces.forEach((opts, el) => {
      if (n >= MAX) return;
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;   // patch 3: skip hidden elements
      posArr[n*2]   = (r.left + r.width / 2) * dpr;
      posArr[n*2+1] = canvas.height - (r.top + r.height / 2) * dpr;  // flip y
      halfArr[n*2]   = (r.width / 2) * dpr + 2;
      halfArr[n*2+1] = (r.height / 2) * dpr + 2;
      radArr[n]      = ((opts && opts.radius != null) ? opts.radius : P.radius) * dpr;
      n++;
    });

    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform3f(U.iResolution, canvas.width, canvas.height, 1);
    gl.uniform2f(U.uImgRes, imgW, imgH);
    gl.uniform2fv(U.uPos, posArr);
    gl.uniform2fv(U.uHalf, halfArr);
    gl.uniform1i(U.uCount, n);
    gl.uniform1f(U.uBlur, Math.max(0.001, P.blur) * dpr);   // patch 1: blur in buffer px
    gl.uniform1f(U.uLens, P.refraction);
    gl.uniform1f(U.uWhite, P.liquidness);
    gl.uniform1f(U.uEdge, P.edgeLight);
    gl.uniform1f(U.uFrost, P.edgeFrost);
    gl.uniform1f(U.uDisperse, P.dispersion);
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

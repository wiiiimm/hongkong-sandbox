// Hong Kong / Lantau layered 3D terrain viewer.
// Base terrain = Claude's smooth external DEM meshes; skin = draped vector layers.
// Best-of-both: shaded / elevation / matte / bare-wireframe / raster surface styles,
// per-layer vector toggles, and a vertical-exaggeration slider that drives BOTH the
// terrain and the draped skin so contours stay welded to the ridges.
import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';

// ---- source registry (extend with whole-HK + SRTM later) -------------------
const SOURCES = {
  'lantau-hk5m': {
    label: 'Lantau · LandsD 5 m DTM',
    mesh:    'data/lantau-hk5m.json',
    georef:  { file: 'data/lantau-georefs.json', key: 'hk5m' },
    texbb:   'data/lantau-texbb.json',
    overlay: 'data/lantau-b50k-vectors.json',   // re-extracted from B50K GML, grid-aligned
    landcover: 'data/lantau-b50k-landcover.json',
    ve: 2.8,
  },
  'lantau-srtm30': {
    label: 'Lantau · AWS Terrarium ~30 m',
    mesh:    'data/lantau-srtm30.json',
    georef:  { file: 'data/lantau-georefs.json', key: 'srtm30' },
    texbb:   'data/lantau-texbb.json',           // shared: B50K texture geographic bounds
    overlay: 'data/lantau-b50k-vectors.json',    // shared: vectors are in absolute E/N via texbb
    landcover: 'data/lantau-b50k-landcover.json',
    ve: 2.6,
  },
  'hk-landsd-5m': {
    label: 'Hong Kong · LandsD 5 m DTM',
    mesh:    'data/hk-dtm5m.json',
    georef:  { file: 'data/hk-georef.json' },     // flat georef (no key)
    texbb:   'data/hk-texbb.json',
    overlay: 'data/hk-b50k-vectors.json',
    landcover: 'data/hk-b50k-landcover.json',
    ve: 2.2,
  },
  'hk-srtm': {
    label: 'Hong Kong · AWS Terrarium ~30 m',
    mesh:    'data/hk-srtm.json',
    georef:  { file: 'data/hk-georef.json' },
    texbb:   'data/hk-texbb.json',
    overlay: 'data/hk-b50k-vectors.json',
    landcover: 'data/hk-b50k-landcover.json',
    ve: 2.2,
  },
};

// vector layer styling (colour + default visibility)
const LAYER_STYLE = {
  contour:  { colour: 0x7a5a36, on: true,  label: 'Contours' },
  road:     { colour: 0x5b5f68, on: true,  label: 'Roads' },
  trail:    { colour: 0xb0402c, on: true,  label: 'Trails' },
  hydro:    { colour: 0x3f6f82, on: true,  label: 'Hydro' },
  coast:    { colour: 0x2f6090, on: true,  label: 'Coast' },
  boundary: { colour: 0x9c6d8a, on: false, label: 'Boundaries' },
  cliff:    { colour: 0x6d5a4a, on: false, label: 'Cliffs' },
};

const BG = { dark: 0x0e1116, paper: 0xf4f1e9 };
const LINE_ON_PAPER = 0x2f5b43;   // wireframe colour on paper bg (the "geeky" look)
const LINE_ON_DARK  = 0x6fe0c0;

// ---- three.js boilerplate --------------------------------------------------
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(38, 1, 10, 400000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI * 0.495;

const hemi = new THREE.HemisphereLight(0xffffff, 0x2b3038, 1.4); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 2.0); sun.position.set(-1, 2, 1.4); scene.add(sun);

// group everything so spin rotates terrain + skin + labels together
const world = new THREE.Group(); scene.add(world);

// ---- per-source state ------------------------------------------------------
let W, H, cell, elev, zmax, peaks = [];
let meshStep = 1, gridW = 0, gridH = 0, curG = null, curTexbb = null;   // mesh density state
let firstLoad = true;   // apply per-source default VE only on the very first load
let terrain, terrainBase, wireOverlay, sea, skin;      // objects
let skinBase = new Map();                               // layer -> Float32Array of base (unexaggerated) y
let labels = [];
let VE = 2.8, surfStyle = 'none', bgMode = 'dark';
let matShaded, matTint, matMatte, matSolid, matTopo, texTopo = null;
let spinDir = 1, spinSpeed = 1;   // horizontal auto-spin (0 = off; 1 = clockwise)
let wireColor = '#2a4c33';        // mesh-line colour; 'auto' button sets null = auto by background
let solidColor = '#262626';       // fill colour for the "Solid colour" surface
let texRot = 0;                   // B50K raster rotation in degrees (manual alignment)

// ---- helpers (ported from the original viewer) -----------------------------
function hyps(e, zmax) {
  const t = Math.max(0, Math.min(1, e / zmax));
  const s = [[0,[46,92,58]],[0.18,[78,110,60]],[0.42,[150,140,96]],
             [0.68,[140,110,80]],[0.86,[170,150,128]],[1,[235,232,224]]];
  for (let i = 0; i < s.length - 1; i++) {
    const a = s[i], b = s[i + 1];
    if (t >= a[0] && t <= b[0]) {
      const u = (t - a[0]) / (b[0] - a[0]);
      return [a[1][0]+(b[1][0]-a[1][0])*u, a[1][1]+(b[1][1]-a[1][1])*u, a[1][2]+(b[1][2]-a[1][2])*u];
    }
  }
  return s[s.length - 1][1];
}
function sampleE(col, row) {
  col = Math.max(0, Math.min(W - 1.001, col));
  row = Math.max(0, Math.min(H - 1.001, row));
  const c0 = Math.floor(col), r0 = Math.floor(row), fc = col - c0, fr = row - r0;
  const a = elev[r0*W+c0], b = elev[r0*W+c0+1], c = elev[(r0+1)*W+c0], d = elev[(r0+1)*W+c0+1];
  return (a*(1-fc)+b*fc)*(1-fr) + (c*(1-fc)+d*fc)*fr;
}
const skinOffset = () => cell * 0.6; // lift lines just above the surface, scaled to grid

// ---- load a source ---------------------------------------------------------
async function loadSource(id) {
  const s = SOURCES[id];
  document.getElementById('note').textContent = 'Loading ' + s.label + '…';
  // dev: propagate the page's ?v to data fetches so edits bust cache; no-op in prod
  const ver = new URLSearchParams(location.search).get('v');
  const q = ver ? ('?v=' + ver) : '';
  const fj = u => fetch(u + q, { cache: 'no-cache' }).then(r => r.json());   // revalidate (304 if unchanged) so stale DEMs never stick
  const [mesh, georefAll, texbbWrap, overlay, landcover] = await Promise.all([
    fj(s.mesh), fj(s.georef.file), fj(s.texbb), fj(s.overlay), fj(s.landcover),
  ]);
  const g = s.georef.key ? georefAll[s.georef.key] : georefAll;   // keyed (lantau) or flat (hk)
  const texbb = texbbWrap.texbb;

  W = mesh.w; H = mesh.h; cell = mesh.cell; elev = mesh.elev; zmax = mesh.zmax;
  peaks = mesh.peaks || [];
  curG = g; curTexbb = texbb;
  if (firstLoad) VE = s.ve;   // apply source default only on first load; otherwise keep user's setting
  document.getElementById('ve').value = VE;
  document.getElementById('vev').textContent = VE.toFixed(1);

  buildTerrain();
  buildSkin(overlay, g, texbb);
  buildSea();
  buildLabels();
  if (texTopo) texTopo.dispose();
  texTopo = buildBaseTexture(landcover);   // clean B50K base map (fills only), aligned by construction
  matTopo.map = texTopo; matTopo.needsUpdate = true;
  applyTexRot();

  applyStyle(surfStyle);
  applyVE();
  frameCamera();
  updateNote();
  firstLoad = false;
}

function updateNote() {
  document.getElementById('note').textContent =
    `${gridW}×${gridH} mesh · ${(gridW*gridH/1e3).toFixed(0)}k verts · peak ${Math.round(zmax)} m`;
}

// rebuild terrain at the current density, preserving style/VE/camera
function rebuildTerrain() {
  buildTerrain();
  if (texTopo) matTopo.map = texTopo;   // re-attach texture to freshly-made material
  applyStyle(surfStyle);
  applyVE();
  updateNote();
}

// Subsampled sample indices along an axis (always includes the last row/col).
function axisSamples(n, step) {
  const s = []; for (let i = 0; i < n; i += step) s.push(i);
  if (s[s.length - 1] !== n - 1) s.push(n - 1);
  return s;
}

function buildTerrain() {
  if (terrain) { world.remove(terrain); terrain.geometry.dispose(); }
  const rows = axisSamples(H, meshStep), cols = axisSamples(W, meshStep);
  const gW = cols.length, gH = rows.length;
  gridW = gW; gridH = gH;
  const g = curG, tb = curTexbb;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(gW*gH*3), col = new Float32Array(gW*gH*3), uv = new Float32Array(gW*gH*2);
  for (let j = 0; j < gH; j++) for (let i = 0; i < gW; i++) {
    const r = rows[j], c = cols[i], k = j*gW+i, e = elev[r*W+c];
    pos[k*3] = (c-W/2)*cell; pos[k*3+1] = e; pos[k*3+2] = (r-H/2)*cell;
    const cc = hyps(e, zmax); col[k*3] = cc[0]/255; col[k*3+1] = cc[1]/255; col[k*3+2] = cc[2]/255;
    const E = g.aE*c + g.bE, N = g.aN*r + g.bN;
    // the B50K raster is authored rotated 180° (stored upside-down); this UV un-rotates it
    uv[k*2] = (E-tb.E0)/(tb.E1-tb.E0); uv[k*2+1] = (N-tb.N0)/(tb.N1-tb.N0);
  }
  const idx = [];
  for (let j = 0; j < gH-1; j++) for (let i = 0; i < gW-1; i++) {
    const a = j*gW+i, b = a+1, d = a+gW, e = d+1; idx.push(a,d,b, b,d,e);
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setIndex(idx);
  terrainBase = pos.slice();  // unexaggerated heights

  matShaded = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0 });
  matTint   = new THREE.MeshBasicMaterial({ vertexColors: true });                 // flat hypsometric
  matMatte  = new THREE.MeshStandardMaterial({ color: 0x8a8f86, roughness: 1, metalness: 0 });
  matSolid  = new THREE.MeshBasicMaterial({ color: solidColor });                  // flat solid fill
  matTopo   = new THREE.MeshBasicMaterial({});   // unlit: show the map flat, no hillshade darkening

  terrain = new THREE.Mesh(geo, matShaded);
  world.add(terrain);

  // wireframe overlay (mesh lines on top of any fill) — shares live geometry
  if (wireOverlay) { world.remove(wireOverlay); wireOverlay.material.dispose(); }
  wireOverlay = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: LINE_ON_DARK, wireframe: true, transparent: true, opacity: 0.14 }));
  wireOverlay.visible = false;
  world.add(wireOverlay);
}

// build one merged LineSegments per vector layer, draped on the terrain
function buildSkin(overlay, g, texbb) {
  if (skin) { world.remove(skin); skin.traverse(o => o.geometry?.dispose()); }
  skin = new THREE.Group(); skinBase.clear();
  const layersDiv = document.getElementById('layers');
  // preserve the user's per-layer toggle choices across a source switch
  const prev = {};
  for (const inp of layersDiv.querySelectorAll('input')) prev[inp.id.replace('lyr_', '')] = inp.checked;
  layersDiv.innerHTML = '';

  for (const [name, style] of Object.entries(LAYER_STYLE)) {
    const lines = overlay[name]; if (!lines || !lines.length) continue;
    const pos = [], baseY = [];
    for (const line of lines) {
      for (let k = 0; k < line.length - 1; k++) {         // emit segment pairs (connected polyline)
        for (const p of [line[k], line[k+1]]) {
          const E = texbb.E0 + p[0]*(texbb.E1 - texbb.E0);
          const N = texbb.N1 - p[1]*(texbb.N1 - texbb.N0);
          const cc = (E - g.bE)/g.aE, rr = (N - g.bN)/g.aN;
          const y = sampleE(cc, rr);
          pos.push((cc-W/2)*cell, y, (rr-H/2)*cell);
          baseY.push(y);
        }
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    const on = (name in prev) ? prev[name] : style.on;   // keep prior choice, else default
    const seg = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: style.colour }));
    seg.name = name;
    seg.visible = on;
    skin.add(seg);
    skinBase.set(name, new Float32Array(baseY));

    // toggle UI
    const id = 'lyr_' + name;
    const lab = document.createElement('label'); lab.className = 'chk';
    lab.innerHTML = `<input type="checkbox" id="${id}" ${on?'checked':''}/> ${style.label}`;
    layersDiv.appendChild(lab);
    lab.querySelector('input').addEventListener('change', e => { seg.visible = e.target.checked; });
  }
  world.add(skin);
}

function buildSea() {
  if (sea) { world.remove(sea); sea.geometry.dispose(); sea.material.dispose(); }
  const geo = new THREE.PlaneGeometry(cell*W*1.8, cell*H*1.8);
  sea = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x2b5d78, transparent: true, opacity: 0.55, roughness: 0.4, depthWrite: false }));
  sea.rotation.x = -Math.PI/2; sea.position.y = 0.5;
  world.add(sea);
}

function buildLabels() {
  labels.forEach(l => l.div.remove()); labels = [];
  for (const pk of peaks) {
    const div = document.createElement('div'); div.className = 'lbl';
    // names are "English 中文" — split trailing CJK from the English part
    const name = pk.name || '';
    const m = name.match(/^(.*?)\s*([㐀-鿿][㐀-鿿\s]*)$/);
    const english = (m ? m[1] : name).trim();
    const chinese = m ? m[2].trim() : '';
    const top = chinese || english;                       // Chinese on top when present
    const sub = (chinese ? english + ' · ' : '') + Math.round(pk.elev) + ' m';
    div.innerHTML = `${top}<small>${sub}</small>`;
    document.body.appendChild(div);
    labels.push({ div, col: pk.col, row: pk.row });
  }
}

// ---- vertical exaggeration drives terrain AND skin -------------------------
function applyVE() {
  const p = terrain.geometry.attributes.position.array;
  const nVerts = terrainBase.length / 3;
  for (let i = 0; i < nVerts; i++) p[i*3+1] = terrainBase[i*3+1] * VE;
  terrain.geometry.attributes.position.needsUpdate = true;
  terrain.geometry.computeVertexNormals();

  const off = skinOffset();
  for (const seg of skin.children) {
    const base = skinBase.get(seg.name);
    const arr = seg.geometry.attributes.position.array;
    for (let i = 0; i < base.length; i++) arr[i*3+1] = base[i]*VE + off;
    seg.geometry.attributes.position.needsUpdate = true;
  }
}

// ---- surface style + background -------------------------------------------
// colour + opacity of the mesh-line overlay. When the mesh is the *only* thing
// on screen (style 'none') the lines go bold; when overlaid on a fill they stay faint.
function wireLook() {
  const onPaper = bgMode === 'paper';
  const auto = onPaper ? LINE_ON_PAPER : LINE_ON_DARK;
  wireOverlay.material.color.set(wireColor != null ? wireColor : auto);
  const primary = surfStyle === 'none';
  wireOverlay.material.opacity = primary ? (onPaper ? 0.9 : 0.8) : (onPaper ? 0.22 : 0.14);
}

// paint a clean B50K base map (land-cover + water fills, no linework) onto a
// canvas at the grid's geographic aspect -> CanvasTexture. Aligned by construction.
function buildBaseTexture(lc) {
  const tb = curTexbb;
  const aspect = (tb.E1 - tb.E0) / (tb.N1 - tb.N0);
  const W = 2048, H = Math.max(1, Math.round(W / aspect));
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  ctx.fillStyle = '#efe9dd'; ctx.fillRect(0, 0, W, H);   // land base
  const paint = (rings, color) => {
    if (!rings || !rings.length) return;
    ctx.fillStyle = color; ctx.beginPath();
    for (const ring of rings) {
      ctx.moveTo(ring[0][0]*W, ring[0][1]*H);
      for (let i = 1; i < ring.length; i++) ctx.lineTo(ring[i][0]*W, ring[i][1]*H);
      ctx.closePath();
    }
    ctx.fill('evenodd');
  };
  paint(lc.wood,   '#b7cca4');   // woodland
  paint(lc.veg,    '#cfdab3');   // cultivation / other vegetation
  paint(lc.barren, '#ddccae');   // sand / mud / barren
  paint(lc.water,  '#a7c4d6');   // reservoirs / water bodies
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return tex;
}

// rotate the B50K raster around its centre (manual alignment aid)
function applyTexRot() {
  const el = document.getElementById('toporotv');
  if (el) el.textContent = texRot.toFixed(1) + '°';
  if (!texTopo) return;
  texTopo.center.set(0.5, 0.5);
  texTopo.rotation = texRot * Math.PI / 180;
  texTopo.needsUpdate = true;
}

function applyStyle(style) {
  surfStyle = style;
  const mats = { shaded: matShaded, tint: matTint, matte: matMatte, solid: matSolid, topo: matTopo };
  // 'none' = no filled surface; every other style fills the terrain.
  terrain.visible = (style !== 'none');
  if (terrain.visible) terrain.material = mats[style] || matShaded;
  document.getElementById('solidrow').style.display = (style === 'solid') ? '' : 'none';
  document.getElementById('toporow').style.display = (style === 'topo') ? '' : 'none';
  // mesh lines are an independent overlay in ALL styles (incl. none)
  wireOverlay.visible = document.getElementById('meshlines').checked;
  wireLook();
}
function applyBg(mode) {
  bgMode = mode;
  renderer.setClearColor(BG[mode], 1);
  const onPaper = mode === 'paper';
  hemi.intensity = onPaper ? 1.9 : 1.4;
  sun.intensity  = onPaper ? 2.4 : 2.0;
  if (wireOverlay) wireLook();
}

// ---- camera framing + presets ---------------------------------------------
function bounds() {
  const halfX = W*cell/2, halfZ = H*cell/2, peakY = zmax*VE;
  return { halfX, halfZ, peakY, span: Math.max(W,H)*cell };
}
function frameCamera() {
  const b = bounds();
  // tune depth range to the scene scale: a tight near/far ratio gives the depth
  // precision needed to stop the flat sea z-fighting while the camera drifts
  camera.near = b.span * 0.03;
  camera.far  = b.span * 6;
  camera.updateProjectionMatrix();
  controls.target.set(0, b.peakY*0.35, 0);
  // start 30° above the horizontal (sea-level) plane
  const elev = 30 * Math.PI / 180, dist = b.span * 1.1;
  camera.position.set(0, controls.target.y + dist*Math.sin(elev), dist*Math.cos(elev));
  controls.minDistance = b.span*0.3; controls.maxDistance = b.span*3;
  controls.update();
}
function southView() { const b = bounds(); camera.position.set(0, b.peakY*1.2, b.span*1.1); controls.target.set(0, b.peakY*0.3, 0); controls.update(); }
function topView()   { const b = bounds(); camera.position.set(0, b.span*1.4, 0.01);       controls.target.set(0, 0, 0);           controls.update(); }

// ---- UI wiring -------------------------------------------------------------
document.getElementById('src').addEventListener('change', e => {
  loadSource(e.target.value).catch(err => {
    document.getElementById('note').textContent = 'Load failed: ' + err.message; console.error(err);
  });
});
document.getElementById('surf').addEventListener('change', e => applyStyle(e.target.value));
document.getElementById('bg').addEventListener('change', e => applyBg(e.target.value));
document.getElementById('ve').addEventListener('input', e => {
  VE = parseFloat(e.target.value); document.getElementById('vev').textContent = VE.toFixed(1); applyVE();
});
document.getElementById('meshlines').addEventListener('change', e => { wireOverlay.visible = e.target.checked; });
const meshdens = document.getElementById('meshdens'), meshdensv = document.getElementById('meshdensv');
const densStep = () => 13 - parseInt(meshdens.value, 10);   // slider right = finest (step 1)
meshdens.addEventListener('input', () => { const s = densStep(); meshdensv.textContent = s === 1 ? 'full' : '÷' + s; });
meshdens.addEventListener('change', () => { meshStep = densStep(); rebuildTerrain(); });
const mlColor = document.getElementById('mlcolor'), mlHex = document.getElementById('mlhex');
function setWireColor(hex) {
  hex = hex.trim(); if (!/^#?[0-9a-fA-F]{6}$/.test(hex)) return;
  if (hex[0] !== '#') hex = '#' + hex;
  wireColor = hex; mlColor.value = hex; mlHex.value = hex; wireLook();
}
mlColor.addEventListener('input', e => setWireColor(e.target.value));
mlHex.addEventListener('change', e => setWireColor(e.target.value));
document.getElementById('mlauto').addEventListener('click', () => { wireColor = null; wireLook(); });
const solidColorEl = document.getElementById('solidcolor'), solidHexEl = document.getElementById('solidhex');
function setSolidColor(hex) {
  hex = hex.trim(); if (!/^#?[0-9a-fA-F]{6}$/.test(hex)) return;
  if (hex[0] !== '#') hex = '#' + hex;
  solidColor = hex; solidColorEl.value = hex; solidHexEl.value = hex;
  if (matSolid) matSolid.color.set(hex);
}
solidColorEl.addEventListener('input', e => setSolidColor(e.target.value));
solidHexEl.addEventListener('change', e => setSolidColor(e.target.value));
const rot = d => () => { texRot = Math.round((texRot + d) * 10) / 10; applyTexRot(); };
document.getElementById('toporotL').addEventListener('click', rot(-1));
document.getElementById('toporotLf').addEventListener('click', rot(-0.2));
document.getElementById('toporotRf').addEventListener('click', rot(0.2));
document.getElementById('toporotR').addEventListener('click', rot(1));
document.getElementById('toporot0').addEventListener('click', () => { texRot = 0; applyTexRot(); });
document.getElementById('water').addEventListener('change', e => { sea.visible = e.target.checked; });
document.getElementById('labels').addEventListener('change', e => { labels.forEach(l => l.div.style.display = e.target.checked ? '' : 'none'); });
document.getElementById('spindir').addEventListener('change', e => { spinDir = parseInt(e.target.value, 10); });
document.getElementById('spinspd').addEventListener('input', e => { spinSpeed = parseFloat(e.target.value); });
const panelEl = document.getElementById('panel');
document.getElementById('collapse-btn').addEventListener('click', () => panelEl.classList.add('collapsed'));
document.getElementById('expand-btn').addEventListener('click', () => panelEl.classList.remove('collapsed'));
document.getElementById('navhelp-btn').addEventListener('click', () => {
  const n = document.getElementById('navhelp'); n.style.display = n.style.display === 'none' ? '' : 'none';
});
document.getElementById('reset').addEventListener('click', frameCamera);
document.getElementById('south').addEventListener('click', southView);
document.getElementById('top').addEventListener('click', topView);

// ---- label projection + render loop ---------------------------------------
const v = new THREE.Vector3();
function updateLabels() {
  const show = document.getElementById('labels').checked;
  for (const l of labels) {
    if (!show) { l.div.style.display = 'none'; continue; }
    v.set((l.col-W/2)*cell, sampleE(l.col, l.row)*VE, (l.row-H/2)*cell);
    world.localToWorld(v); v.project(camera);
    const behind = v.z > 1;
    l.div.style.display = behind ? 'none' : '';
    l.div.style.left = ((v.x*0.5+0.5)*innerWidth) + 'px';
    l.div.style.top  = ((-v.y*0.5+0.5)*innerHeight) + 'px';
  }
}
function resize() {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

function animate() {
  requestAnimationFrame(animate);
  if (spinDir) world.rotation.y += 0.0016 * spinSpeed * spinDir;
  controls.update();
  renderer.render(scene, camera);
  updateLabels();
}

resize();
applyBg('dark');
loadSource('lantau-hk5m').then(animate).catch(err => {
  document.getElementById('note').textContent = 'Load failed: ' + err.message;
  console.error(err);
});

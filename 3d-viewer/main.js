// Hong Kong / Lantau layered 3D terrain viewer.
// Base terrain = Claude's smooth external DEM meshes; skin = draped vector layers.
// Best-of-both: shaded / elevation / matte / bare-wireframe / raster surface styles,
// per-layer vector toggles, and a vertical-exaggeration slider that drives BOTH the
// terrain and the draped skin so contours stay welded to the ridges.
import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { createGlass } from './vendor/glass-gl.js';
import { sunPosition, sunTimes, moonPosition, moonTimes, moonIllumination, starPosition, compassDeg } from './vendor/astro.js';
import { setEnabled as setAudioEnabled, setMasterVolume, setWeatherMix, thunder, setEngine, audioSupported } from './audio.js';
import { initAnalytics, track, armAnalytics, VercelSink, GA4Sink } from './analytics.js';

// ---- configurable asset base (HKS-46) --------------------------------------
// The heavy bundled data (the /data/ JSON — DEM meshes, vector overlays, POIs)
// can be served from a separate origin (e.g. an object-storage bucket) to keep
// bulk egress off the app host. Defaults to '' (relative), so forks and
// self-hosts serve /data/ from their own origin with zero config and never hit
// anyone else's bucket. Override by setting window.ASSET_BASE before main.js
// loads, or edit this constant.
const ASSET_BASE = (typeof window !== 'undefined' && window.ASSET_BASE) || '';
// Prefix an origin onto a bundled data path only when a base is configured;
// leaves absolute URLs and non-data paths untouched.
const asset = p => (ASSET_BASE && /^data\//.test(p)) ? ASSET_BASE.replace(/\/+$/, '') + '/' + p : p;

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
    ve: 2.8,
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

// ---- i18n (en-hk / zh-hk) --------------------------------------------------
const LOCALES = ['en-hk', 'zh-hk'];
const DEFAULT_LOCALE = 'en-hk';
const I18N = {
  'en-hk': {
    'app.title': 'Hong Kong Sandbox',
    'doc.title': 'Hong Kong Sandbox — 3D terrain, live weather & typhoon sim',
    'meta.desc': 'An interactive 3D Hong Kong — real LiDAR terrain, live Hong Kong Observatory weather, tides and typhoon signals (No.1–10). Fly it yourself. Bilingual (EN / 繁中).',
    'lbl.source': 'Source', 'src.hk5m': 'Hong Kong · LandsD 5 m', 'src.hksrtm': 'Hong Kong · AWS Terrarium ~30 m',
    'src.lan5m': 'Lantau · LandsD 5 m', 'src.lansrtm': 'Lantau · AWS Terrarium ~30 m',
    'lbl.surface': 'Surface', 'surf.none': 'None (no fill)', 'surf.shaded': 'Shaded relief', 'surf.tint': 'Elevation tint (flat)',
    'surf.matte': 'Matte', 'surf.solid': 'Solid colour', 'surf.topo': 'Topographic (B50K)', 'surf.osm': 'Street map (OSM)', 'surf.sat': 'Satellite (Esri)',
    'lbl.fill': 'Fill colour', 'lbl.maprotate': 'Map rotate', 'lbl.background': 'Background', 'bg.dark': 'Dark', 'bg.paper': 'Paper', 'lbl.vertical': 'Vertical ×',
    'grp.mesh': 'Mesh', 'lbl.showmesh': 'Show mesh lines', 'lbl.density': 'Density', 'lbl.colour': 'Colour', 'btn.auto': 'auto',
    'grp.overlays': 'Overlays · stack on top', 'ov.water': 'Water', 'ov.landmarks': 'Landmarks', 'ov.labels': 'Peaks', 'ov.stations': 'Stations (live)', 'ov.aqhi': 'Air · AQHI (live)', 'ov.stationswind': '+ wind/marine stns', 'ov.lift': 'Overlay height',
    'grp.gpx': 'Trails · GPX', 'gpx.drop': 'Drop GPX files here, or tap to load', 'gpx.offmap': 'partly outside the loaded map', 'gpx.remove': 'Remove trail', 'gpx.colour': 'Trail colour', 'gpx.bad': 'No tracks found in that file', 'gpx.trail': 'Custom Trail', 'gpx.name': 'Trail name', 'gpx.start': 'Start', 'gpx.end': 'End', 'gpx.play': 'Play trail', 'gpx.pause': 'Pause', 'gpx.pan': 'Pan to trail', 'gpx.show': 'Show trail', 'gpx.hide': 'Hide trail', 'gpx.details': 'Elevation & stats', 'gpx.dist': 'Distance', 'gpx.dur': 'Time', 'gpx.avg': 'Avg',
    'radar.title': 'Rain radar', 'radar.credit': '© Hong Kong Observatory',
    'sat.title': 'Satellite', 'sat.wide': 'Wide', 'sat.local': 'Local', 'rf.bigger': 'Enlarge radar', 'rf.smaller': 'Restore radar size',
    'lyr.contour': 'Contours', 'lyr.road': 'Roads', 'lyr.trail': 'Trails', 'lyr.hydro': 'Hydro', 'lyr.coast': 'Coast', 'lyr.boundary': 'Boundaries', 'lyr.cliff': 'Cliffs',
    'grp.spin': 'Auto‑spin (horizontal)', 'lbl.direction': 'Direction', 'spin.off': 'Off', 'spin.pause': 'Pause', 'spin.cw': '⟳ Clockwise', 'spin.ccw': '⟲ Counter‑cw', 'lbl.speed': 'Speed',
    'grp.sky': 'Sun & moon', 'lbl.skymode': 'Sky', 'sky.live': 'Live (HKT)', 'sky.fixed': 'Custom time', 'sky.off': 'Off · studio light', 'lbl.date': 'Date', 'lbl.time': 'Time',
    'grp.weather': 'Weather', 'lbl.sound': 'Sound', 'wx.rain': 'Rain', 'wx.clouds': 'Clouds', 'wx.fog': 'Fog', 'wx.thunder': 'Thunder', 'wx.waves': 'Waves', 'wx.snow': 'Snow',
    'lbl.skyheight': 'Sky height ×',
    'lbl.thunderrate': 'Thunder rate', 'lbl.tide': 'Tide', 'lbl.storm': 'Storm signal', 'storm.0': 'None', 'storm.1': 'T1 · Standby', 'storm.3': 'T3 · Strong wind',
    'storm.8': 'T8 · Gale / Storm', 'storm.9': 'T9 · Incr. gale', 'storm.10': 'T10 · Hurricane', 'lbl.wind': 'Wind', 'lbl.windfrom': 'Wind from',
    'btn.reset': 'Reset', 'btn.south': 'South', 'btn.top': 'Top‑down', 'btn.copylink': 'Copy link', 'btn.fly': '✈ Fly',
    'btn.share': 'Share', 'share.title': 'Share this view', 'share.text': 'Hong Kong Sandbox — an interactive 3D Hong Kong, live weather & typhoon sim', 'share.copied': 'Copied!', 'share.inbar': 'Link is in the address bar', 'share.embed': 'Embed', 'share.embedcopied': 'Embed code copied!',
    'fly.help': '↑↓ pitch · ←→ bank · ⇧/⌃ throttle · ␣ gas · drag to look · C camera · Esc exit',
    'fly.touch': 'tap to take off · tilt to steer · hold for gas · drag to look',
    'fly.view': 'view', 'fly.exit': 'exit',
    'fly.landed': 'landed', 'fly.takeoff': '🛫 take off — ␣ or tap',
    'fly.chase': '🎥 Chase', 'fly.cockpit': '🧑‍✈️ Cockpit',
    // HKS-93: three-way fly camera — chase, clean pilot's eye, cockpit interior
    'cam.ext': 'Chase / external camera (C)', 'cam.eye': 'First-person eye camera (C)', 'cam.ck': 'Cockpit camera (C)',
    'lbl.topspeed': 'Top speed',
    'lbl.plane': 'Aircraft', 'plane.prop': 'Prop plane', 'plane.betsy': 'Cathay Pacific Betsy (DC-3)', 'plane.cx747': 'Cathay Pacific 747', 'plane.cx777': 'Cathay Pacific 777', 'plane.a330': 'Cathay Pacific A330-300', 'plane.a350': 'Cathay Pacific A350-1000',
    'btn.walk': '🪂 Walk',
    'btn.matrix': '🕴 Matrix', 'btn.neon': '❄️ Neon Night',
    // HKS-86: the bottom mode dock + contextual tray
    'dock.orbit': 'Orbit', 'dock.fly': 'Fly', 'dock.walk': 'Walk', 'dock.star': 'Stargaze',
    'dock.matrix': 'Matrix', 'dock.neon': '風林火山', 'dock.settings': 'Settings',
    'coach.text': 'New here? Tap the <b>⚙</b> to set up the view — surface, weather, sky &amp; more.', 'coach.ok': 'Got it',
    'tray.end': 'End', 'grp.move': 'Fly & walk',
    'sg.live': '● Live sky', 'sg.custom': '🕐 Custom',
    'sg.orient': '🤳 Point at the sky', 'sg.clock': 'Show / hide the sky time',
    'sg.hint': 'drag to look · tap a constellation',
    'walk.help': 'WASD/↑↓←→ move · drag to look (🖱 to lock) · ⇧ boost · ␣ jump · C view · Esc exit',
    'walk.touch': 'hold to walk · 2-finger hold to run · drag to look', 'walk.jog': 'boosting', 'walk.dist': 'walked', 'walk.auto': 'Auto-walk (play / pause)', 'walk.lock': 'View lock — move the mouse to look (Esc to release)',
    'walk.fp': '👁 POV', 'walk.chase': '🎥 Chase',
    'help.tab': 'Help', 'help.title': 'Help & controls',
    'help.src': 'Modes live in the bottom bar · themes toggle in any mode',
    'help.orbit.t': 'Map view', 'help.orbit.b': 'Drag to rotate\nScroll or pinch to zoom\nRight‑drag or two‑finger to pan\nReset recenters the view',
    'help.fly.t': 'Flying', 'help.fly.b': 'Take off — tap the plane, press Space, or the 🛫 button\nDrag or hold on a parked plane to look at it — it won’t take off\nHold Space (or a finger) to accelerate\nDrag to look around · press C to cycle chase / eye / cockpit\nLand anywhere — even water',
    'help.walk.t': 'On foot', 'help.walk.b': 'Move with the keys, or the on‑screen ▶\nSpace to jump · Shift or a two‑finger hold to run\nDrag to look around — 🖱 locks the mouse for look (Esc releases)\nPress C for first‑person / chase',
    'help.star.t': 'Stargazing', 'help.star.b': 'Drag to look around the sky\nTwo-finger / right-drag to move across the map\nTap a star to trace its constellation\n🤳 Point at the sky — aim with your phone (auto-tracks your GPS)\nGPS button tracks your real position (off → follow → compass)\nDrag the time slider to move the sky',
    'help.gen.t': 'Getting around', 'help.gen.b': 'Pick a mode in the bottom bar — Orbit, Fly, Walk, Stargaze\nMatrix & 風林火山 are looks you can turn on in any mode\nKeys — M / N looks · C camera · Esc leaves a mode\n⚙ opens settings — Trails · GPX drops in your own tracks, plays them back (▶) start→end, and shows each trail\'s elevation profile',
    'title.about': 'About · licence · contact', 'lbl.credits': 'Credits',
    'loc.find': 'Find my location', 'loc.locating': 'Locating…', 'loc.you': 'You', 'loc.relocate': 'Re-locate',
    'loc.follow': 'Follow me', 'loc.following': 'Following', 'loc.stopfollow': 'Stop following',
    'loc.compass': 'Compass view', 'loc.compassoff': 'Exit compass', 'loc.nocompass': 'Compass unavailable on this device.',
    'loc.walk': 'Walk from here', 'loc.remove': 'Remove pin',
    'loc.denied': 'Location blocked — allow it in your browser settings.', 'loc.unavail': 'Location unavailable.',
    'loc.outside': 'You don’t appear to be in Hong Kong.', 'loc.outsrc': 'Off this map — switch source to Hong Kong.',
    'about': '<b>Hong Kong Sandbox · 香港沙盒</b>'
      + '<p>Built by <b>wiiiimm</b> — <a href="https://wiiiimm.design" target="_blank" rel="noopener">portfolio</a>. '
      + 'Originally made for <a href="https://madeinlantau.com" target="_blank" rel="noopener">Made in Lantau</a>’s design work.</p>'
      + '<p><a href="https://github.com/wiiiimm" target="_blank" rel="noopener">GitHub</a> · '
      + '<a href="https://x.com/wiiiimm" target="_blank" rel="noopener">X</a> · '
      + '<a href="https://www.threads.com/@_wiiiimm" target="_blank" rel="noopener">Threads</a></p>'
      + '<p>Liquid‑glass panels by <a href="https://github.com/wiiiimm/glass-gl" target="_blank" rel="noopener">glass‑gl</a> — droplet refraction, blur, liquidness, chromatic dispersion & a directional rim glint, all refracting the live 3D scene.</p>'
      + '<p>Free & open source under <a href="https://github.com/wiiiimm/hongkong-sandbox/blob/main/LICENSE" target="_blank" rel="noopener">AGPL‑3.0</a> · '
      + '<a href="https://github.com/wiiiimm/hongkong-sandbox" target="_blank" rel="noopener">source on GitHub</a>. '
      + 'Feature requests & bug reports → <a href="https://github.com/wiiiimm/hongkong-sandbox/issues" target="_blank" rel="noopener">GitHub issues</a>.</p>'
      + '<p>Contact & commercial licensing: <a href="mailto:email@wiiiimm.codes">email@wiiiimm.codes</a> · '
      + 'licensing <a href="https://github.com/wiiiimm/hongkong-sandbox/blob/main/COMMERCIAL.md" target="_blank" rel="noopener">terms</a>.</p>'
      + '<p>Data: HKO / DATA.GOV.HK · LandsD 5 m DEM & B50K · NASA SRTM · © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors (ODbL) · Esri.</p>'
      + '<p>747 cockpit photo: <a href="https://commons.wikimedia.org/wiki/File:G-bnlp_(45518246055).jpg" target="_blank" rel="noopener">“G-BNLP” by Jeroen Stroes Aviation Photography</a> (<a href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noopener">CC BY 2.0</a>), cropped with instrument displays re-lit.</p>'
      + '<p>Walk-mode hiker: <a href="https://poly.pizza/m/5EGWBMpuXq" target="_blank" rel="noopener">“Adventurer” by Quaternius</a> (CC0 / public domain), trimmed &amp; optimised.</p>'
      + '<p>Fly-mode aircraft (<a href="https://creativecommons.org/licenses/by/3.0/" target="_blank" rel="noopener">CC BY 3.0</a>, optimised &amp; re-tinted): <a href="https://poly.pizza/m/7cvx6ex-xfL" target="_blank" rel="noopener">“Small Airplane” by Vojtěch Balák</a> · <a href="https://sketchfab.com/3d-models/boeing-747-100-6ef67f9995d345ddaee9ec845ac10b69" target="_blank" rel="noopener">“Boeing 747-100” by Marine</a> (<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>, repainted in our own Cathay-jade livery) · <a href="https://sketchfab.com/3d-models/boeing-777-300er-2ee4847b20724a308ef73f33e3823ecb" target="_blank" rel="noopener">“Boeing 777-300er.” by The F-35’s Modeling Hub</a> (<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>, repainted in our own Cathay-jade livery) · <a href="https://sketchfab.com/3d-models/a350-v3-with-animation-965439a6041847a0b8decba253ffdf6f" target="_blank" rel="noopener">“A350 V3 with animation” by Newbie99999993</a> (<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>, decimated &amp; repainted in our own Cathay-jade livery) · <a href="https://sketchfab.com/3d-models/cathay-pacific-airbus-a330-300-45a62d88607145c4afb1f46b281aa277" target="_blank" rel="noopener">“Cathay Pacific Airbus A330-300” by OUTPISTON</a> (<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>, non-commercial — optimised only) · <a href="https://sketchfab.com/3d-models/mcdonnell-douglas-dc-3-7673f61636554c02bf86015f1b6a8333" target="_blank" rel="noopener">“McDonnell Douglas DC-3” by OUTPISTON</a> (<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>, non-commercial — repainted in Betsy’s 1946 bare-metal VR-HDB markings).</p>'
      + '<p>Infrastructure by <a href="https://stealth-company.co" target="_blank" rel="noopener">stealth.co</a>.</p>'
      + '© 2026 wiiiimm',
    'live.sync': '⛅ Sync live weather', 'live.on': '⛅ Live weather · ON',
    'lock.live': '◈ set by live weather — turn off sync below to adjust',
    'lock.storm': '◈ set by the storm signal — choose None to adjust',
    'lock.sky': '◈ following live weather — turn off sync to adjust',
    'lock.stargaze': '◈ weather is off for a clear sky in Stargaze',
    'lock.matrix': '◈ set by Matrix mode — 🕴 to wake up',
    'lock.neon': '◈ set by 風林火山 mode — ❄️ to leave the neon night',
    'note.mesh': 'mesh', 'note.verts': 'verts', 'note.peak': 'peak', 'note.m': 'm', 'note.loading': 'Loading', 'note.layers': 'Loading map layers', 'note.loadfail': 'Load failed',
    'install.ios': 'Add Hong Kong Sandbox to your home screen — tap Share, then "Add to Home Screen".', 'install.android': 'Install Hong Kong Sandbox — a full-screen, offline-ready app.', 'install.action': 'Install',
    'load.osm': 'street map', 'load.sat': 'satellite imagery', 'load.mapfail': 'Map load failed', 'load.offline': 'You’re offline — connect once to load the map, then it works offline.', 'load.failed': 'Couldn’t load the map.', 'load.retry': 'Retry', 'off.banner': '⚠ Offline — live weather, tides, radar & satellite, map tiles and air quality are unavailable · the 3D map, sky and simulation still work', 'dens.full': 'full',
    'sig.1': 'Standby Signal No.1', 'sig.3': 'Strong Wind Signal No.3', 'sig.8': 'Gale or Storm Signal No.8',
    'sig.9': 'Increasing Gale or Storm Signal No.9', 'sig.10': 'Hurricane Signal No.10', 'badge.pre': '⚠ TYPHOON SIGNAL No.', 'badge.post': '',
    'tip.humidity': 'humidity', 'tip.wind': 'wind', 'tip.gust': 'gust', 'tip.rain': 'Rain (district, 1 h):', 'tide.word': 'tide', 'tide.rising': '↑ rising', 'tide.falling': '↓ falling', 'tide.slack': '→ slack',
    'tide.24h': '24 h tide', 'st.QUB': 'Quarry Bay', 'st.CCH': 'Cheung Chau', 'wx.unavail': 'live weather unavailable', 'wx.live': 'Live',
    'wb.title': 'Weather notices', 'wb.chip': 'Notices', 'wb.warn': 'Warnings in force', 'wb.fcast': 'Forecast',
  },
  'zh-hk': {
    'app.title': '香港沙盒',
    'doc.title': '香港沙盒 — 3D 地形、實時天氣與颱風模擬',
    'meta.desc': '互動 3D 香港 — 真實 LiDAR 地形、香港天文台實時天氣、潮汐及颱風信號（一號至十號）。親自駕駛飛越香港。中英雙語。',
    'lbl.source': '資料來源', 'src.hk5m': '香港 · 地政總署 5 米', 'src.hksrtm': '香港 · AWS Terrarium ~30 米',
    'src.lan5m': '大嶼山 · 地政總署 5 米', 'src.lansrtm': '大嶼山 · AWS Terrarium ~30 米',
    'lbl.surface': '表面', 'surf.none': '無填色', 'surf.shaded': '陰影地貌', 'surf.tint': '高程著色（平面）',
    'surf.matte': '霧面', 'surf.solid': '純色', 'surf.topo': '地形圖 (B50K)', 'surf.osm': '街道圖 (OSM)', 'surf.sat': '衛星影像 (Esri)',
    'lbl.fill': '填色', 'lbl.maprotate': '地圖旋轉', 'lbl.background': '背景', 'bg.dark': '深色', 'bg.paper': '紙本', 'lbl.vertical': '垂直誇張 ×',
    'grp.mesh': '網格', 'lbl.showmesh': '顯示網格線', 'lbl.density': '密度', 'lbl.colour': '顏色', 'btn.auto': '自動',
    'grp.overlays': '疊加圖層', 'ov.water': '海水', 'ov.landmarks': '地標', 'ov.labels': '山峰', 'ov.stations': '氣象站（即時）', 'ov.aqhi': '空氣質素（即時）', 'ov.stationswind': '＋風／海事站', 'ov.lift': '疊層高度',
    'grp.gpx': '路徑 · GPX', 'gpx.drop': '拖放 GPX 檔案，或點按載入', 'gpx.offmap': '部分超出已載入地圖範圍', 'gpx.remove': '移除路徑', 'gpx.colour': '路徑顏色', 'gpx.bad': '檔案中找不到路徑', 'gpx.trail': '自訂路徑', 'gpx.name': '路徑名稱', 'gpx.start': '起點', 'gpx.end': '終點', 'gpx.play': '播放路徑', 'gpx.pause': '暫停', 'gpx.pan': '移至路徑', 'gpx.show': '顯示路徑', 'gpx.hide': '隱藏路徑', 'gpx.details': '高度與統計', 'gpx.dist': '距離', 'gpx.dur': '時間', 'gpx.avg': '平均',
    'radar.title': '雨區雷達', 'radar.credit': '© 香港天文台',
    'sat.title': '衛星', 'sat.wide': '廣域', 'sat.local': '本地', 'rf.bigger': '放大雷達', 'rf.smaller': '還原雷達大小',
    'lyr.contour': '等高線', 'lyr.road': '道路', 'lyr.trail': '山徑', 'lyr.hydro': '水系', 'lyr.coast': '海岸線', 'lyr.boundary': '界線', 'lyr.cliff': '懸崖',
    'grp.spin': '自動旋轉（水平）', 'lbl.direction': '方向', 'spin.off': '關閉', 'spin.pause': '暫停', 'spin.cw': '⟳ 順時針', 'spin.ccw': '⟲ 逆時針', 'lbl.speed': '速度',
    'grp.sky': '日與月', 'lbl.skymode': '天空', 'sky.live': '即時（香港時間）', 'sky.fixed': '自訂時間', 'sky.off': '關閉 · 固定光', 'lbl.date': '日期', 'lbl.time': '時間',
    'grp.weather': '天氣', 'lbl.sound': '音效', 'wx.rain': '雨', 'wx.clouds': '雲', 'wx.fog': '霧', 'wx.thunder': '雷暴', 'wx.waves': '波浪', 'wx.snow': '雪',
    'lbl.skyheight': '天空高度 ×',
    'lbl.thunderrate': '雷暴頻率', 'lbl.tide': '潮汐', 'lbl.storm': '風暴信號', 'storm.0': '無', 'storm.1': '一號 · 戒備', 'storm.3': '三號 · 強風',
    'storm.8': '八號 · 烈風/暴風', 'storm.9': '九號 · 烈風增強', 'storm.10': '十號 · 颶風', 'lbl.wind': '風力', 'lbl.windfrom': '風向來自',
    'btn.reset': '重設', 'btn.south': '南面', 'btn.top': '俯視', 'btn.copylink': '複製連結', 'btn.fly': '✈ 飛行',
    'btn.share': '分享', 'share.title': '分享此畫面', 'share.text': '香港沙盒 — 互動 3D 香港，實時天氣與颱風模擬', 'share.copied': '已複製！', 'share.inbar': '連結已在網址列', 'share.embed': '嵌入', 'share.embedcopied': '已複製嵌入碼！',
    'fly.help': '↑↓ 俯仰 · ←→ 轉向 · ⇧/⌃ 油門 · ␣ 加速 · 拖曳環視 · C 鏡頭 · Esc 離開',
    'fly.touch': '點擊起飛 · 傾斜轉向 · 按住加速 · 拖曳環視',
    'fly.view': '視角', 'fly.exit': '離開',
    'fly.landed': '已降落', 'fly.takeoff': '🛫 起飛 — ␣ 或點擊',
    'fly.chase': '🎥 追機', 'fly.cockpit': '🧑‍✈️ 駕駛艙',
    // HKS-93: three-way fly camera — chase, clean pilot's eye, cockpit interior
    'cam.ext': '追機／外部鏡頭 (C)', 'cam.eye': '第一人稱主視角 (C)', 'cam.ck': '駕駛艙鏡頭 (C)',
    'lbl.topspeed': '極速',
    'lbl.plane': '機型', 'plane.prop': '螺旋槳小飛機', 'plane.betsy': '國泰航空「貝茜」DC-3', 'plane.cx747': '國泰航空 747', 'plane.cx777': '國泰航空 777', 'plane.a330': '國泰航空 A330-300', 'plane.a350': '國泰航空 A350-1000',
    'btn.walk': '🪂 步行',
    'btn.matrix': '🕴 Matrix', 'btn.neon': '❄️ 風林火山',
    // HKS-86: the bottom mode dock + contextual tray
    'dock.orbit': '環繞', 'dock.fly': '飛行', 'dock.walk': '步行', 'dock.star': '觀星',
    'dock.matrix': 'Matrix', 'dock.neon': '風林火山', 'dock.settings': '設定',
    'coach.text': '第一次來？點一下 <b>⚙</b> 設定畫面 — 地表、天氣、天空等。', 'coach.ok': '知道了',
    'tray.end': '結束', 'grp.move': '飛行與步行',
    'sg.live': '● 即時星空', 'sg.custom': '🕐 自訂',
    'sg.orient': '🤳 指向天空', 'sg.clock': '顯示／隱藏天空時間',
    'sg.hint': '拖曳環視 · 點選星座',
    'walk.help': 'WASD/↑↓←→ 移動 · 拖曳環視（🖱 鎖定）· ⇧ 加速 · ␣ 跳 · C 視角 · Esc 離開',
    'walk.touch': '按住行走 · 雙指快跑 · 拖動視角', 'walk.jog': '加速中', 'walk.dist': '已行', 'walk.auto': '自動步行（播放／暫停）', 'walk.lock': '視角鎖定 — 移動滑鼠環顧（按 Esc 解除）',
    'walk.fp': '👁 主視角', 'walk.chase': '🎥 跟隨',
    'help.tab': '說明', 'help.title': '操作說明',
    'help.src': '模式在底部工具列 · 風格可於任何模式切換',
    'help.orbit.t': '地圖檢視', 'help.orbit.b': '拖曳旋轉\n滾輪或雙指縮放\n右鍵拖曳或雙指平移\n重設可重新置中',
    'help.fly.t': '飛行', 'help.fly.b': '起飛 — 點擊飛機、按空白鍵，或按 🛫 鍵\n在停泊的飛機上拖曳或按住可環顧它 — 不會起飛\n按住空白鍵（或手指）加速\n拖曳環顧四周 · 按 C 循環切換追機 / 主視角 / 駕駛艙\n可降落任何地方（連水面）',
    'help.walk.t': '步行', 'help.walk.b': '用按鍵或畫面上的 ▶ 移動\n空白鍵跳躍 · Shift 或雙指按住奔跑\n拖曳環顧四周 — 🖱 鎖定滑鼠環視（Esc 解除）\n按 C 切換第一人稱 / 追尾',
    'help.star.t': '觀星', 'help.star.b': '拖曳環顧夜空\n雙指／右鍵拖曳在地圖上移動\n點選星星顯示所屬星座\n🤳 對準天空 — 用手機方向瞄準（自動追蹤 GPS）\nGPS 按鈕追蹤你的實際位置（關 → 跟隨 → 指南針）\n拖動時間軸移動星空',
    'help.gen.t': '基本操作', 'help.gen.b': '在底部工具列選擇模式 — 環繞、飛行、步行、觀星\nMatrix 與 風林火山 是可於任何模式開啟的風格\n按鍵 — M / N 風格 · C 鏡頭 · Esc 離開模式\n⚙ 開啟設定 —— 「路徑 · GPX」可載入自己的路徑、回放（▶）由起點掃至終點，並顯示各路徑的高度剖面',
    'title.about': '關於 · 授權 · 聯絡', 'lbl.credits': '關於',
    'loc.find': '定位', 'loc.locating': '定位中…', 'loc.you': '你', 'loc.relocate': '重新定位',
    'loc.follow': '跟隨我', 'loc.following': '跟隨中', 'loc.stopfollow': '停止跟隨',
    'loc.compass': '指南針視角', 'loc.compassoff': '退出指南針', 'loc.nocompass': '此裝置沒有指南針。',
    'loc.walk': '由此步行', 'loc.remove': '移除定位',
    'loc.denied': '位置被封鎖 —— 請在瀏覽器設定中允許。', 'loc.unavail': '無法取得位置。',
    'loc.outside': '你似乎不在香港範圍內。', 'loc.outsrc': '超出此地圖範圍 —— 請切換至香港圖層。',
    'about': '<b>香港沙盒 · Hong Kong Sandbox</b>'
      + '<p>由 <b>wiiiimm</b> 製作 — <a href="https://wiiiimm.design" target="_blank" rel="noopener">作品集</a>。'
      + '原為 <a href="https://madeinlantau.com" target="_blank" rel="noopener">Made in Lantau</a> 的設計工作而建。</p>'
      + '<p><a href="https://github.com/wiiiimm" target="_blank" rel="noopener">GitHub</a> · '
      + '<a href="https://x.com/wiiiimm" target="_blank" rel="noopener">X</a> · '
      + '<a href="https://www.threads.com/@_wiiiimm" target="_blank" rel="noopener">Threads</a></p>'
      + '<p>液態玻璃面板由 <a href="https://github.com/wiiiimm/glass-gl" target="_blank" rel="noopener">glass‑gl</a> 驅動 — 水滴折射、模糊、乳化、色散及方向性邊緣反光，全部即時折射 3D 場景。</p>'
      + '<p>自由開源軟件，採用 <a href="https://github.com/wiiiimm/hongkong-sandbox/blob/main/LICENSE" target="_blank" rel="noopener">AGPL‑3.0</a> 授權 · '
      + '<a href="https://github.com/wiiiimm/hongkong-sandbox" target="_blank" rel="noopener">GitHub 原始碼</a>。'
      + '功能建議及錯誤回報 → <a href="https://github.com/wiiiimm/hongkong-sandbox/issues" target="_blank" rel="noopener">GitHub issues</a>。</p>'
      + '<p>聯絡及商業授權：<a href="mailto:email@wiiiimm.codes">email@wiiiimm.codes</a> · '
      + '授權<a href="https://github.com/wiiiimm/hongkong-sandbox/blob/main/COMMERCIAL.md" target="_blank" rel="noopener">條款</a>。</p>'
      + '<p>數據：香港天文台 / DATA.GOV.HK · 地政總署 5 米 DEM 及 B50K · NASA SRTM · © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> 貢獻者 (ODbL) · Esri。</p>'
      + '<p>747 駕駛艙照片：<a href="https://commons.wikimedia.org/wiki/File:G-bnlp_(45518246055).jpg" target="_blank" rel="noopener">「G-BNLP」Jeroen Stroes Aviation Photography</a>（<a href="https://creativecommons.org/licenses/by/2.0/" target="_blank" rel="noopener">CC BY 2.0</a>），裁切並重新點亮儀表顯示。</p>'
      + '<p>步行模式行山者：Quaternius 的 <a href="https://poly.pizza/m/5EGWBMpuXq" target="_blank" rel="noopener">「Adventurer」</a>（CC0 公有領域），經裁剪及優化。</p>'
      + '<p>飛行模式飛機（<a href="https://creativecommons.org/licenses/by/3.0/" target="_blank" rel="noopener">CC BY 3.0</a>，經優化及重新調色）：Vojtěch Balák 的 <a href="https://poly.pizza/m/7cvx6ex-xfL" target="_blank" rel="noopener">「Small Airplane」</a> · Marine 的 <a href="https://sketchfab.com/3d-models/boeing-747-100-6ef67f9995d345ddaee9ec845ac10b69" target="_blank" rel="noopener">「Boeing 747-100」</a>（<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>，重繪本作自家國泰翡翠色塗裝） · The F-35’s Modeling Hub 的 <a href="https://sketchfab.com/3d-models/boeing-777-300er-2ee4847b20724a308ef73f33e3823ecb" target="_blank" rel="noopener">「Boeing 777-300er.」</a>（<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>，重繪本作自家國泰翡翠色塗裝） · Newbie99999993 的 <a href="https://sketchfab.com/3d-models/a350-v3-with-animation-965439a6041847a0b8decba253ffdf6f" target="_blank" rel="noopener">「A350 V3 with animation」</a>（<a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>，經大幅簡化並塗上本作自家國泰翡翠色塗裝） · OUTPISTON 的 <a href="https://sketchfab.com/3d-models/cathay-pacific-airbus-a330-300-45a62d88607145c4afb1f46b281aa277" target="_blank" rel="noopener">「Cathay Pacific Airbus A330-300」</a>（<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>，非商業用途 — 僅作優化） · OUTPISTON 的 <a href="https://sketchfab.com/3d-models/mcdonnell-douglas-dc-3-7673f61636554c02bf86015f1b6a8333" target="_blank" rel="noopener">「McDonnell Douglas DC-3」</a>（<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>，非商業用途 — 重繪 1946 年「貝茜」VR-HDB 原色金屬塗裝）。</p>'
      + '<p>基礎設施由 <a href="https://stealth-company.co" target="_blank" rel="noopener">stealth.co</a> 提供。</p>'
      + '© 2026 wiiiimm',
    'live.sync': '⛅ 同步即時天氣', 'live.on': '⛅ 即時天氣 · 開啟',
    'lock.live': '◈ 由即時天氣設定 — 關閉下方同步即可調整',
    'lock.storm': '◈ 由風暴信號設定 — 選「無」即可調整',
    'lock.sky': '◈ 跟隨即時天氣 — 關閉同步即可調整',
    'lock.stargaze': '◈ 觀星模式已關閉天氣，保持淨空',
    'lock.matrix': '◈ 由 Matrix 模式設定 — 按 🕴 醒來',
    'lock.neon': '◈ 由風林火山模式設定 — 按 ❄️ 離開霓虹夜',
    'note.mesh': '網格', 'note.verts': '頂點', 'note.peak': '最高', 'note.m': '米', 'note.loading': '載入中', 'note.layers': '載入地圖圖層中', 'note.loadfail': '載入失敗',
    'install.ios': '將香港沙盒加到主畫面 —— 點擊分享，再選「加入主畫面」。', 'install.android': '安裝香港沙盒 —— 全螢幕、離線使用。', 'install.action': '安裝',
    'load.osm': '街道圖', 'load.sat': '衛星影像', 'load.mapfail': '地圖載入失敗', 'load.offline': '你目前離線 — 請先連線載入地圖一次，之後即可離線使用。', 'load.failed': '無法載入地圖。', 'load.retry': '重試', 'off.banner': '⚠ 離線 — 實時天氣、潮汐、雷達與衛星、地圖圖層及空氣質素無法使用 · 3D 地圖、天空及模擬仍可運作', 'dens.full': '全部',
    'sig.1': '一號戒備信號', 'sig.3': '三號強風信號', 'sig.8': '八號烈風或暴風信號',
    'sig.9': '九號烈風或暴風增強信號', 'sig.10': '十號颶風信號', 'badge.pre': '⚠ 颱風信號 ', 'badge.post': ' 號',
    'tip.humidity': '濕度', 'tip.wind': '風', 'tip.gust': '陣風', 'tip.rain': '雨量（地區，1小時）：', 'tide.word': '潮汐', 'tide.rising': '↑ 上漲', 'tide.falling': '↓ 回落', 'tide.slack': '→ 平潮',
    'tide.24h': '24 小時潮汐', 'st.QUB': '鰂魚涌', 'st.CCH': '長洲', 'wx.unavail': '無法取得即時天氣', 'wx.live': '即時',
    'wb.title': '天氣提示', 'wb.chip': '提示', 'wb.warn': '生效警告', 'wb.fcast': '天氣預報',
  },
};
let locale = DEFAULT_LOCALE;
const t = k => (I18N[locale] && I18N[locale][k] != null) ? I18N[locale][k] : (I18N[DEFAULT_LOCALE][k] != null ? I18N[DEFAULT_LOCALE][k] : k);
const isZh = () => locale === 'zh-hk';

// ---- three.js boilerplate --------------------------------------------------
// Liquid-glass panels (glass-gl) refract the live scene, which needs the drawing
// buffer kept readable. Desktop / fine-pointer only — phones keep the CSS look.
const GLASS_OK = matchMedia('(pointer: fine)').matches && innerWidth > 640;
const app = document.getElementById('app');
// logarithmicDepthBuffer: the flight camera sits metres from geometry while the
// horizon is ~100 km out — a linear depth buffer z-fights the sea against the
// coast at that ratio (bad flicker in flight). Log depth spreads the precision.
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: GLASS_OK, logarithmicDepthBuffer: true });
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
let peaksData = null;   // named HK peaks POI set (data/hk-peaks.json), placed by E/N per source
let landmarksData = null, landmarks = [], landmarkPeakPts = [];   // curated landmarks POI set (data/hk-landmarks.json)
let meshStep = 1, gridW = 0, gridH = 0, curG = null, curTexbb = null;   // mesh density state
let firstLoad = true;   // apply per-source default VE only on the very first load
let terrain, terrainBase, wireOverlay, sea, skin;      // objects
let skinBase = new Map();                               // layer -> Float32Array of base (unexaggerated) y
let skinGrid = new Map();                               // layer -> Float32Array of [col,row] per vertex — re-drape source when mesh density changes (HKS-108)
let loadGen = 0;                                        // bumped per loadSource; late overlay fetches check it before painting (HKS-49)
let labels = [];
let VE = 2.8, surfStyle = 'shaded', bgMode = 'dark';
let matShaded, matTint, matMatte, matSolid, matTopo, texTopo = null;
const tidalMats = [];   // materials with the intertidal "wet band" shader injected
let spinDir = 1, spinSpeed = 0.2;   // horizontal auto-spin (0 = off; 1 = clockwise); default a gentle 20%
let wireColor = '#2a4c33';        // mesh-line colour; 'auto' button sets null = auto by background
let solidColor = '#262626';       // fill colour for the "Solid colour" surface
let texRot = 0;                   // B50K raster rotation in degrees (manual alignment)
let baseUV = null, webTex = null, webUVAttr = null, webKind = null, matWeb = null;   // web-map drape

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
// HKS-108: height on the RENDERED triangle surface (drape sampler). buildTerrain
// splits each quad along the d–b diagonal (bottom-left ↔ top-right: idx a,d,b b,d,e),
// so bilinear sampleE() deviates from the actual mesh by metres on steep coarse
// cells — overlays draped with it float or dip. This sampler reproduces the exact
// planar triangles the GPU rasterises, on the *decimated* grid when the density
// slider sets meshStep>1 (quad corners at multiples of meshStep, ragged last
// row/col snapped to W-1/H-1 like axisSamples does). Used for the overlay drape
// (vector skin + GPX) AND the walk-mode ground height (HKS: on steep/curved coarse
// cells the bilinear surface dips metres below the rendered mesh — ×VE — so the
// hiker sank into the mountain); labels / GPS keep bilinear sampleE.
function sampleEtri(col, row) {
  col = Math.max(0, Math.min(W - 1.001, col));
  row = Math.max(0, Math.min(H - 1.001, row));
  const s = meshStep;
  const c0 = Math.floor(col / s) * s, r0 = Math.floor(row / s) * s;
  const c1 = Math.min(c0 + s, W - 1), r1 = Math.min(r0 + s, H - 1);
  const fc = (col - c0) / (c1 - c0), fr = (row - r0) / (r1 - r0);
  const A = elev[r0*W+c0], B = elev[r0*W+c1], C = elev[r1*W+c0], D = elev[r1*W+c1];
  return (fc + fr <= 1) ? A + fc*(B-A) + fr*(C-A)          // upper-left triangle (a,d,b)
                        : D*(fc+fr-1) + B*(1-fr) + C*(1-fc); // lower-right triangle (b,d,e)
}
let skinLift = 1;                 // overlay drape height in *real* metres above the ground, user-tunable via the Overlays slider (0.2–15 m); URL-synced as 'oh'. polygonOffset on the terrain fill carries z-fighting. HKS-108: the drape samples the rendered triangle surface (sampleEtri), so vertices sit ON the mesh exactly — this small lift only covers line-chord sag between vertices across a convex ridge. skinOffset scales by VE, so residual sag and lift grow together and a ~1 m real value hugs the ground at every exaggeration.
const skinOffset = () => skinLift * VE;

// ---- load a source ---------------------------------------------------------
async function loadSource(id) {
  const s = SOURCES[id];
  const gen = ++loadGen;   // HKS-49: any in-flight overlay from a prior source is now stale
  document.getElementById('note').textContent = t('note.loading') + '…';
  // dev: propagate the page's ?v to data fetches so edits bust cache; no-op in prod
  const ver = new URLSearchParams(location.search).get('v');
  const q = ver ? ('?v=' + ver) : '';
  // streamed fetch with byte progress: the loader and the panel note show real
  // MB downloaded, and a % + bar when Content-Length adds up (with gzip the
  // decoded byte count can pass the compressed total — then we show MB only)
  const prog = {};
  const fmtMB = b => (b / 1048576).toFixed(1) + ' MB';
  const report = () => {
    let got = 0, total = 0, known = true;
    for (const k in prog) { got += prog[k].got; if (prog[k].total > 0) total += prog[k].total; else known = false; }
    const pct = known && total && got <= total ? Math.round(100 * got / total) : null;
    const txt = `${t('note.loading')}… ${fmtMB(got)}${pct != null ? ` / ${fmtMB(total)} · ${pct}%` : ''}`;
    document.getElementById('note').textContent = txt;
    const ld = document.getElementById('loader');
    if (ld && !ld.classList.contains('done')) {
      const ls = document.getElementById('loaderstatus');
      if (ls) ls.textContent = txt;
      const lb = document.getElementById('loaderbar');
      if (lb) lb.style.width = (pct != null ? pct : 30) + '%';
    }
  };
  const fj = async u => {   // revalidate (304 if unchanged) so stale DEMs never stick
    // HKS-109: bound the ENTIRE fetch + body read so a stall at any phase (headers OR
    // a hung stream mid-download) can't leave the boot loader spinning. onLine can lie
    // (dead Wi-Fi / captive portal), so keep the online budget tight too; a SW cache
    // hit resolves far under it. The signal stays armed across the whole read.
    const ctrl = new AbortController();
    const to = setTimeout(() => ctrl.abort(), navigator.onLine ? 15000 : 3500);
    try {
      const res = await fetch(asset(u) + q, { cache: 'no-cache', signal: ctrl.signal });   // HKS-46: honour ASSET_BASE
      if (!res.ok) throw new Error(`HTTP ${res.status} ${u}`);
      if (!res.body || !res.body.getReader) return await res.json();
      prog[u] = { got: 0, total: +res.headers.get('Content-Length') || 0 };
      const rd = res.body.getReader(), chunks = [];
      for (;;) {
        const { done, value } = await rd.read();
        if (done) break;
        chunks.push(value); prog[u].got += value.length; report();
      }
      let n = 0; for (const c of chunks) n += c.length;
      const buf = new Uint8Array(n); let o = 0;
      for (const c of chunks) { buf.set(c, o); o += c.length; }
      return JSON.parse(new TextDecoder().decode(buf));
    } finally { clearTimeout(to); }
  };
  // HKS-49: the 12 MB vector overlay is *not* in the critical path — terrain goes
  // interactive on the lighter payload, then the overlay streams in behind a mini-loader.
  const [mesh, georefAll, texbbWrap, landcover] = await Promise.all([
    fj(s.mesh), fj(s.georef.file), fj(s.texbb), fj(s.landcover),
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
  preRenderLayers();   // HKS-49: layer toggles exist before the overlay lands (URL L= + toggles-during-load)
  buildSea();
  buildWeather();
  updateWindVisuals();     // renderSky + fog + rain/cloud look for the current wind
  if (!peaksData) peaksData = await fj('data/hk-peaks.json').catch(() => ({ peaks: [] }));
  if (!landmarksData) landmarksData = await fj('data/hk-landmarks.json').catch(() => ({ landmarks: [] }));
  buildLabels();
  buildLandmarks();
  if (texTopo) texTopo.dispose();
  texTopo = buildBaseTexture(landcover);   // clean B50K base map (fills only), aligned by construction
  matTopo.map = texTopo; matTopo.needsUpdate = true;
  applyTexRot();

  applyStyle(surfStyle);
  applyVE();
  frameCamera();
  updateNote();
  firstLoad = false;

  // HKS-49: stream the vector overlay in the background; when it lands (and this
  // source is still current) drape the layers at the toggle state the user sees now.
  loadVectorOverlay(asset(s.overlay) + q, gen, g, texbb);   // HKS-46: honour ASSET_BASE
}

// Render the layer toggles from LAYER_STYLE before the vector overlay arrives, so
// applyState's URL L= and any toggles-during-load are captured in checkbox state;
// buildSkin() reads that state back (its `prev` logic) when the lines are built.
function preRenderLayers() {
  const layersDiv = document.getElementById('layers');
  const prev = {};
  for (const inp of layersDiv.querySelectorAll('input')) prev[inp.id.replace('lyr_', '')] = inp.checked;
  // drop any stale vectors from the previous source at once — never paint them under new terrain
  if (skin) { world.remove(skin); skin.traverse(o => o.geometry?.dispose()); }
  skin = new THREE.Group(); skinBase.clear(); skinGrid.clear(); world.add(skin);
  layersDiv.innerHTML = '';
  for (const [name, style] of Object.entries(LAYER_STYLE)) {
    const on = (name in prev) ? prev[name] : style.on;
    const id = 'lyr_' + name;
    const lab = document.createElement('label'); lab.className = 'chk';
    lab.innerHTML = `<input type="checkbox" id="${id}" ${on?'checked':''}/> <span data-i18n="lyr.${name}">${I18N[locale]['lyr.'+name] || style.label}</span>`;
    layersDiv.appendChild(lab);
  }
}

// Stream the vector overlay behind the non-blocking mini-loader, then build the skin.
// Guarded by `gen`: a source switch bumps loadGen, so a superseded fetch is discarded.
async function loadVectorOverlay(url, gen, g, texbb) {
  showMini(t('note.layers'));
  try {
    const res = await fetch(url, { cache: 'no-cache' });
    let overlay;
    if (!res.body || !res.body.getReader) {
      overlay = await res.json();
    } else {
      const total = +res.headers.get('Content-Length') || 0;
      const rd = res.body.getReader(), chunks = []; let got = 0;
      for (;;) {
        const { done, value } = await rd.read();
        if (done) break;
        chunks.push(value); got += value.length;
        if (gen === loadGen) miniProgress(got, total);
      }
      let n = 0; for (const c of chunks) n += c.length;
      const buf = new Uint8Array(n); let o = 0;
      for (const c of chunks) { buf.set(c, o); o += c.length; }
      overlay = JSON.parse(new TextDecoder().decode(buf));
    }
    if (gen !== loadGen) return;   // a newer source superseded us mid-download
    buildSkin(overlay, g, texbb);
    applyVE();                     // drape the fresh lines at the current exaggeration
  } catch (e) {
    console.warn('vector overlay load failed', e);   // silent to the user — layers just stay absent
  } finally {
    if (gen === loadGen) hideMini();
  }
}

// ---- non-blocking mini-loader (HKS-49) ------------------------------------
// A small transparent glass chip, top-centre, for the background overlay stream.
// Unlike #loader it never blocks interaction (pointer-events:none) and never gates boot.
function showMini(label) {
  const el = document.getElementById('miniloader'); if (!el) return;
  const lb = el.querySelector('.mlabel'); if (lb) lb.textContent = label;
  const bar = el.querySelector('.mbar > i'); if (bar) bar.style.width = '8%';
  el.classList.add('show');
  document.body.classList.add('dl-active');   // HKS-91: load bar takes the top-left slot → fade the brand chip out
}
function miniProgress(got, total) {
  const el = document.getElementById('miniloader'); if (!el) return;
  const mb = (got / 1048576).toFixed(1) + ' MB';
  const pct = total && got <= total ? Math.round(100 * got / total) : null;
  const lb = el.querySelector('.mlabel');
  if (lb) lb.textContent = `${t('note.layers')}… ${mb}${pct != null ? ` · ${pct}%` : ''}`;
  const bar = el.querySelector('.mbar > i');
  if (bar) bar.style.width = (pct != null ? pct : 30) + '%';
}
function hideMini() {
  const el = document.getElementById('miniloader'); if (!el) return;
  const bar = el.querySelector('.mbar > i'); if (bar) bar.style.width = '100%';
  el.classList.remove('show');
  document.body.classList.remove('dl-active');   // HKS-91: load bar gone → brand chip fades back in (0.5s delay, via CSS)
}

// HKS-91: lock the viewport zoom. iOS Safari ignores user-scalable=no, so kill its
// pinch gesture directly; touch-action (CSS) handles double-tap + non-iOS pinch.
// The app's own 2-finger gestures use touch events, not gesture events — untouched.
['gesturestart', 'gesturechange', 'gestureend'].forEach(ev =>
  addEventListener(ev, e => e.preventDefault(), { passive: false }));

// HKS-91: full-screen toggle (reclaims the mobile browser chrome, esp. landscape).
// Fullscreen API covers desktop + Android; iOS Safari has no element fullscreen, so
// fall back to the Add-to-Home-Screen nudge (standalone launch has no browser chrome).
const fsRoot = document.documentElement;
const fsActive = () => document.fullscreenElement || document.webkitFullscreenElement;
function toggleFullscreen() {
  if (fsActive()) { (document.exitFullscreen || document.webkitExitFullscreen || (() => {})).call(document); return; }
  const req = fsRoot.requestFullscreen || fsRoot.webkitRequestFullscreen;
  if (req) { const r = req.call(fsRoot); if (r && r.catch) r.catch(() => {}); return; }   // prefixed webkit form returns undefined, not a Promise
  const bar = document.getElementById('installbar');        // iOS: no fullscreen API → show "Add to Home Screen"
  if (bar && !(matchMedia('(display-mode: standalone)').matches || navigator.standalone === true)) bar.classList.add('ios', 'show');
}
function syncFsBtn() { const b = document.getElementById('fsbtn'); if (b) b.classList.toggle('on', !!fsActive()); }
document.getElementById('fsbtn').addEventListener('click', e => { e.stopPropagation(); track('fullscreen', { on: !fsActive() }); toggleFullscreen(); });
document.addEventListener('fullscreenchange', syncFsBtn);
document.addEventListener('webkitfullscreenchange', syncFsBtn);

function updateNote() {
  document.getElementById('note').textContent =
    `${gridW}×${gridH} ${t('note.mesh')} · ${(gridW*gridH/1e3).toFixed(0)}k ${t('note.verts')} · ${t('note.peak')} ${Math.round(zmax)} ${t('note.m')}`;
}

// rebuild terrain at the current density, preserving style/VE/camera
function rebuildTerrain() {
  buildTerrain();
  if (texTopo) matTopo.map = texTopo;   // re-attach texture to freshly-made material
  applyStyle(surfStyle);
  redrapeSkin();   // HKS-108: drape heights are triangle-matched to the mesh, so a density change moves them
  applyVE();
  updateNote();
}

// HKS-108: recompute the vector skin's base drape heights against the CURRENT
// mesh triangulation (sampleEtri depends on meshStep). applyVE() then writes
// the world y from these. GPX re-drapes itself via redrapeGpx() in applyVE().
function redrapeSkin() {
  for (const seg of (skin?.children ?? [])) {
    const gcr = skinGrid.get(seg.name), base = skinBase.get(seg.name);
    if (!gcr || !base) continue;
    for (let i = 0; i < base.length; i++) base[i] = sampleEtri(gcr[i*2], gcr[i*2+1]);
  }
}

// Subsampled sample indices along an axis (always includes the last row/col).
function axisSamples(n, step) {
  const s = []; for (let i = 0; i < n; i += step) s.push(i);
  if (s[s.length - 1] !== n - 1) s.push(n - 1);
  return s;
}

// Tileable blotch texture driving the cloud-shadow pass (blobs re-drawn at ±size
// offsets so the wrap is seamless when it scrolls with the wind)
const CLOUD_SHADOW_TEX = (() => {
  const S = 256, c = document.createElement('canvas'); c.width = c.height = S;
  const x = c.getContext('2d');
  x.fillStyle = '#000'; x.fillRect(0, 0, S, S);
  for (let i = 0; i < 26; i++) {
    const px = Math.random() * S, py = Math.random() * S, r = 26 + Math.random() * 58;
    for (const ox of [-S, 0, S]) for (const oy of [-S, 0, S]) {
      const g = x.createRadialGradient(px + ox, py + oy, 0, px + ox, py + oy, r);
      g.addColorStop(0, 'rgba(255,255,255,.5)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      x.fillStyle = g; x.fillRect(0, 0, S, S);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
})();

// Surface FX injected into every terrain/sea material (HKS-21/22, composing the
// original intertidal band):
//   wet band  — tint within uBand above the waterline (wide on beaches, thin on
//               seawalls; purely geometric). Gated per-material by uWetAmt.
//   cloud shadows — wind-scrolled tileable blotches darken the ground while the
//               cloud layer is on; offset advances with the sprite drift.
//   height fog — geometry below uFogY fades toward the sky/fog colour, so haze
//               sits IN the valleys and over the sea, not just in front of them.
function attachTerrainFX(mat, wet, water) {
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uWaterY = { value: -1e9 };
    sh.uniforms.uBand = { value: 12.0 };
    sh.uniforms.uWetAmt = { value: wet ? 1 : 0 };
    sh.uniforms.uFoamAmt = { value: 0 };
    sh.uniforms.uCloudTex = { value: CLOUD_SHADOW_TEX };
    sh.uniforms.uCloudOfs = { value: new THREE.Vector2(0, 0) };
    sh.uniforms.uCloudScale = { value: 1 / 60000 };
    sh.uniforms.uCloudAmt = { value: 0 };
    sh.uniforms.uFogY = { value: 0 };
    sh.uniforms.uFogAmt = { value: 0 };
    sh.uniforms.uFogCol = { value: new THREE.Color(0x0e1116) };
    sh.uniforms.uTime = { value: 0 };
    sh.uniforms.uWaveAmp = { value: 0 };
    sh.uniforms.uWaveK = { value: 1 / 400 };
    sh.uniforms.uSparkAmt = { value: 0 };
    sh.uniforms.uGlintAmt = { value: 0 };
    sh.uniforms.uSunDirV = { value: new THREE.Vector3(0, 1, 0) };
    sh.uniforms.uSnowAmt = { value: 0 };
    sh.uniforms.uSnowLine = { value: 1e9 };
    // world position: correct height for the rotated sea plane, and an xz frame
    // that spins with the world group exactly like the cloud sprites do
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vWpos;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nvWpos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
        varying vec3 vWpos;
        uniform float uWaterY; uniform float uBand; uniform float uWetAmt; uniform float uFoamAmt;
        uniform sampler2D uCloudTex; uniform vec2 uCloudOfs; uniform float uCloudScale; uniform float uCloudAmt;
        uniform float uFogY; uniform float uFogAmt; uniform vec3 uFogCol;
        uniform float uTime; uniform float uWaveAmp; uniform float uWaveK; uniform float uSparkAmt;
        uniform float uGlintAmt; uniform vec3 uSunDirV;
        uniform float uSnowAmt; uniform float uSnowLine;`)
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>
        { float d = vWpos.y - uWaterY; float wet = step(0.0, d) * (1.0 - smoothstep(0.0, uBand, d));
          gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.29,0.33,0.31), wet * 0.5 * uWetAmt);
          float foam = step(0.0, d) * (1.0 - smoothstep(0.0, uBand * 0.22, d));
          float fn = texture2D(uCloudTex, vWpos.xz * uCloudScale * 60.0 + vec2(uTime * 0.02, uTime * 0.013)).r;
          gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.93,0.96,0.97),
            foam * smoothstep(0.32, 0.78, fn) * uFoamAmt * uWetAmt); }
        { // snow-caps: higher, colder ground whitens first, mottled by the noise tex
          float sl = smoothstep(uSnowLine, uSnowLine * 1.7, vWpos.y);
          float sn = texture2D(uCloudTex, vWpos.xz * uCloudScale * 24.0).r;
          gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.94,0.96,0.99),
            sl * uSnowAmt * (0.85 + 0.15 * sn) * uWetAmt); }
        { float s = texture2D(uCloudTex, vWpos.xz * uCloudScale + uCloudOfs).r;
          gl_FragColor.rgb *= 1.0 - smoothstep(0.35, 0.85, s) * uCloudAmt * 0.34; }
        { float hf = (1.0 - smoothstep(0.0, uFogY, vWpos.y)) * uFogAmt;
          gl_FragColor.rgb = mix(gl_FragColor.rgb, uFogCol, hf * 0.8); }`);
    if (water) {
      // animated wave normals: three sine octaves' analytic slopes, rotated into
      // view space — the PBR sun/moon specular then glints off the moving water
      sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
        { vec2 p = vWpos.xz * uWaveK; float t = uTime;
          float sx = cos(p.x * 1.00 + t * 1.1) * 1.0
                   + cos((p.x + p.y) * 1.7 + t * 1.7) * 0.6
                   + cos(p.x * 3.1 - p.y * 2.2 + t * 2.3) * 0.35;
          float sz = cos(p.y * 1.13 - t * 0.9) * 1.0
                   + cos((p.y - p.x) * 1.9 + t * 1.4) * 0.6
                   + cos(p.y * 2.7 + p.x * 2.4 + t * 2.1) * 0.35;
          vec3 wn = (viewMatrix * vec4(sx, 0.0, sz, 0.0)).xyz;
          normal = normalize(normal + wn * uWaveAmp);
          // rain pocks the surface: fine time-jittered normal noise scatters the
          // glint while it rains, reading as a roughened, drizzled sea
          if (uSparkAmt > 0.0) {
            vec2 rc = floor(vWpos.xz * uWaveK * 60.0) + floor(uTime * 8.0);
            float rj = fract(sin(dot(rc, vec2(12.9898, 78.233))) * 43758.5453) - 0.5;
            float rk = fract(sin(dot(rc, vec2(39.3468, 11.135))) * 24634.6345) - 0.5;
            normal = normalize(normal + (viewMatrix * vec4(rj, 0.0, rk, 0.0)).xyz * uSparkAmt * 0.9);
          } }`);
      // sun-glitter: per-cell micro-facets whose normals slowly rotate — each
      // flashes as it sweeps through alignment between the sun (or moon) and
      // the eye. Injected before the shared passes so height fog dims it.
      sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>', `#include <dithering_fragment>
        if (uGlintAmt > 0.0) {
          vec2 gc = floor(vWpos.xz * uWaveK * 80.0);
          float gr = fract(sin(dot(gc, vec2(127.1, 311.7))) * 43758.5453);
          float ph = gr * 6.2831 + uTime * (1.0 + gr * 2.5);
          vec3 mj = normalize(normal + (viewMatrix * vec4(cos(ph) * 0.22, 0.0, sin(ph) * 0.22, 0.0)).xyz);
          vec3 Hh = normalize(uSunDirV + normalize(vViewPosition));
          gl_FragColor.rgb += vec3(1.0, 0.97, 0.88) * pow(max(dot(mj, Hh), 0.0), 420.0) * uGlintAmt;
        }`);
    }
    mat.userData.sh = sh;
  };
  mat.userData.isWater = !!water;
  mat.needsUpdate = true;
  tidalMats.push(mat);
}

function buildTerrain() {
  if (terrain) { world.remove(terrain); terrain.geometry.dispose(); }
  const rows = axisSamples(H, meshStep), cols = axisSamples(W, meshStep);
  const gW = cols.length, gH = rows.length;
  gridW = gW; gridH = gH;
  const g = curG, tb = curTexbb;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(gW*gH*3), col = new Float32Array(gW*gH*3), uv = new Float32Array(gW*gH*2);
  // baked terrain relief (HKS-15): curvature AO (valleys darken, ridge crests
  // lift) and a slope-based rocky tint on steep faces, folded into the vertex
  // colours at build time — zero per-frame cost, works for shaded + tint styles
  const EV = (r, c) => elev[Math.max(0, Math.min(H - 1, r)) * W + Math.max(0, Math.min(W - 1, c))];
  const ds = meshStep, dd = 2 * ds * cell;
  for (let j = 0; j < gH; j++) for (let i = 0; i < gW; i++) {
    const r = rows[j], c = cols[i], k = j*gW+i, e = elev[r*W+c];
    pos[k*3] = (c-W/2)*cell; pos[k*3+1] = e; pos[k*3+2] = (r-H/2)*cell;
    const eN = EV(r - ds, c), eS = EV(r + ds, c), eE = EV(r, c + ds), eW2 = EV(r, c - ds);
    const curv = ((eN + eS + eE + eW2) / 4 - e) / (ds * cell);
    const shade = Math.max(0.78, Math.min(1.14, 1 - curv * 5));
    const gx = (eE - eW2) / dd, gz = (eS - eN) / dd;
    const rockT = Math.max(0, Math.min(1, (Math.sqrt(gx*gx + gz*gz) - 0.35) / 0.55)) * 0.45;
    const cc = hyps(e, zmax);
    col[k*3]   = Math.min(1, (cc[0] * (1 - rockT) + 122 * rockT) * shade / 255);
    col[k*3+1] = Math.min(1, (cc[1] * (1 - rockT) + 116 * rockT) * shade / 255);
    col[k*3+2] = Math.min(1, (cc[2] * (1 - rockT) + 106 * rockT) * shade / 255);
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
  baseUV = uv; webKind = null;   // keep base UVs for restore; force web-map rebuild after any remesh

  matShaded = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.95, metalness: 0 });
  matTint   = new THREE.MeshBasicMaterial({ vertexColors: true });                 // flat hypsometric
  matMatte  = new THREE.MeshStandardMaterial({ color: 0x8a8f86, roughness: 1, metalness: 0 });
  matSolid  = new THREE.MeshBasicMaterial({ color: solidColor });                  // flat solid fill
  matTopo   = new THREE.MeshBasicMaterial({});   // unlit: show the map flat, no hillshade darkening
  // Push the terrain fill back a hair in the depth buffer so draped vector lines
  // (roads / coastline / contours / GPX) render on the surface with only a tiny
  // geometric lift — polygonOffset auto-scales with view distance, so there's no
  // z-fighting from orbit AND no 42 m float that put overlays above your head afoot.
  [matShaded, matTint, matMatte, matSolid, matTopo].forEach(m => { m.polygonOffset = true; m.polygonOffsetFactor = 1; m.polygonOffsetUnits = 1; });
  tidalMats.length = 0;
  [matShaded, matTint, matMatte].forEach(m => attachTerrainFX(m, true));   // wet band + shadows + fog
  [matSolid, matTopo].forEach(m => attachTerrainFX(m, false));             // raster/solid: shadows + fog only
  if (matWeb) tidalMats.push(matWeb);   // keep the web drape driven across source switches

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
  skin = new THREE.Group(); skinBase.clear(); skinGrid.clear();
  const layersDiv = document.getElementById('layers');
  // preserve the user's per-layer toggle choices across a source switch
  const prev = {};
  for (const inp of layersDiv.querySelectorAll('input')) prev[inp.id.replace('lyr_', '')] = inp.checked;
  layersDiv.innerHTML = '';

  for (const [name, style] of Object.entries(LAYER_STYLE)) {
    const lines = overlay[name]; if (!lines || !lines.length) continue;
    const pos = [], baseY = [], gcr = [];
    for (const line of lines) {
      for (let k = 0; k < line.length - 1; k++) {         // emit segment pairs (connected polyline)
        for (const p of [line[k], line[k+1]]) {
          const E = texbb.E0 + p[0]*(texbb.E1 - texbb.E0);
          const N = texbb.N1 - p[1]*(texbb.N1 - texbb.N0);
          const cc = (E - g.bE)/g.aE, rr = (N - g.bN)/g.aN;
          const y = sampleEtri(cc, rr);                   // HKS-108: drape on the rendered triangles, not bilinear
          pos.push((cc-W/2)*cell, y, (rr-H/2)*cell);
          baseY.push(y); gcr.push(cc, rr);
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
    skinGrid.set(name, new Float32Array(gcr));

    // toggle UI
    const id = 'lyr_' + name;
    const lab = document.createElement('label'); lab.className = 'chk';
    lab.innerHTML = `<input type="checkbox" id="${id}" ${on?'checked':''}/> <span data-i18n="lyr.${name}">${I18N[locale]['lyr.'+name] || style.label}</span>`;
    layersDiv.appendChild(lab);
    lab.querySelector('input').addEventListener('change', e => { seg.visible = e.target.checked; });
  }
  world.add(skin);
}

function buildSea() {
  if (sea) { world.remove(sea); sea.geometry.dispose(); sea.material.dispose(); }
  const geo = new THREE.PlaneGeometry(cell*W*1.8, cell*H*1.8);
  sea = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x2b5d78, transparent: true, opacity: 0.55, roughness: 0.32, depthWrite: false }));
  sea.rotation.x = -Math.PI/2; sea.position.y = 0.5;
  attachTerrainFX(sea.material, false, true);   // living water: waves + glint; shadows + fog too
  world.add(sea);
}

// ---- weather effects: rain / clouds / fog / lightning / waves --------------
let rainPts = null, rainHeads = null, cloudGrp = null, mistGrp = null, wavePhase = 0, waveT = 0, flash = 0;
const _sunDirV = new THREE.Vector3(0, 1, 0);   // key-light direction in view space (for water glitter)
let snowPts = null, snowMeta = null, snowAcc = 0;   // flakes + snow-cap build-up (0..1)
let wallGrp = null, wallOp = 0;                     // T8+ rotating storm wall
const SEA_Y = 0.5;
const weather = { fog: false, rain: false, clouds: false, lightning: false, waves: false, snow: false };
let lastWxData = null;   // HKS-69: last live payload (English rhrread) — lets a source change re-map the WxField grids without a refetch (codex)
let skyScale = 1;        // sky-layer height × — lifts/scales cloud altitude + rain ceiling (view control)
let tideManual = 0.5;    // slider 0..1 — used when not in live mode
let tideLevel  = 0.5;    // effective water level 0..1 (drives the sea height)
let tideSeries = null;   // live prediction: { vals[72] m, nowHour, min, max, cur, stationName } or null

// ---- wind + tropical-cyclone storm system ----------------------------------
let stormLevel = 0;      // 0 none, else HK signal 1 / 3 / 8 / 9 / 10
let windStrength = 0;    // 0..1 wind intensity (storm presets it; slider overrides)
let thunderRate = 0.4;   // 0..1 lightning strike frequency (storm/live preset it)
// HKS-68: live regional lightning state from HKO's LHL feed — { total, rate }
// where total is the territory's real past-hour cloud-to-ground count and rate
// is the strike frequency it maps to. null = no live LHL data (fetch failed or
// live sync off), which keeps today's global thunderRate behaviour.
let liveLtg = null;
const flashfx = document.getElementById('flashfx');   // full-screen lightning flash
let baseHemi = 1.4, baseSun = 2.0;   // light levels before the lightning flash is added
// bounds().span cached per terrain source (set in buildWeather, which every
// source swap runs) so per-frame readers (updateHaze) do a plain read instead
// of allocating a fresh bounds() object each frame (HKS-103).
let mapSpan = 0;
const windVec = { x: 0, z: 1 };      // unit heading the wind blows TOWARD (screen space)
const WIND_VEC = {   // 16-point compass the wind blows FROM -> push vector (toward the opposite)
  N:[0,1], NNE:[-0.383,0.924], NE:[-0.707,0.707], ENE:[-0.924,0.383],
  E:[-1,0], ESE:[-0.924,-0.383], SE:[-0.707,-0.707], SSE:[-0.383,-0.924],
  S:[0,-1], SSW:[0.383,-0.924], SW:[0.707,-0.707], WSW:[0.924,-0.383],
  W:[1,0], WNW:[0.924,0.383], NW:[0.707,0.707], NNW:[0.383,0.924],
};
const STORM_W = { 0:0, 1:0.2, 3:0.45, 8:0.72, 9:0.86, 10:1 };   // signal -> wind strength
const SIGNAL_NAME = {
  1:'Standby Signal No.1', 3:'Strong Wind Signal No.3', 8:'Gale or Storm Signal No.8',
  9:'Increasing Gale or Storm Signal No.9', 10:'Hurricane Signal No.10',
};
const setWindDir = dir => { const v = WIND_VEC[dir] || WIND_VEC.N; windVec.x = v[0]; windVec.z = v[1]; };

// three puff-cluster textures (HKS-12) — overlapping soft blobs with a shaded
// underside, so clouds read as lumpy masses instead of uniform smudges
const CLOUD_TEXS = (() => {
  const mk = () => {
    const c = document.createElement('canvas'); c.width = 256; c.height = 128;
    const x = c.getContext('2d');
    for (let i = 0; i < 9; i++) {
      const px = 40 + Math.random() * 176, py = 46 + Math.random() * 36;
      const r = 26 + Math.random() * 42;
      const g = x.createRadialGradient(px, py, r * 0.1, px, py, r);
      g.addColorStop(0, `rgba(255,255,255,${0.28 + Math.random() * 0.3})`);
      g.addColorStop(0.6, 'rgba(240,244,249,0.16)');
      g.addColorStop(1, 'rgba(255,255,255,0)');
      x.fillStyle = g; x.fillRect(0, 0, 256, 128);
    }
    const sh = x.createLinearGradient(0, 40, 0, 128);   // flat, shaded base
    sh.addColorStop(0, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(120,132,148,0.18)');
    x.globalCompositeOperation = 'source-atop'; x.fillStyle = sh; x.fillRect(0, 0, 256, 128);
    return new THREE.CanvasTexture(c);
  };
  return [mk(), mk(), mk()];
})();

// soft round flake sprite for the snow points (HKS-17)
const SNOW_TEX = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const x = c.getContext('2d');
  const g = x.createRadialGradient(32, 32, 0, 32, 32, 30);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.5, 'rgba(255,255,255,.75)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = g; x.fillRect(0, 0, 64, 64);
  return new THREE.CanvasTexture(c);
})();

// soft blotch deck for the pooled mist (HKS-14) — edge-faded so the plane rim never shows
const MIST_TEX = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d');
  for (let i = 0; i < 14; i++) {
    const px = Math.random()*256, py = Math.random()*256, r = 50 + Math.random()*80;
    const g = x.createRadialGradient(px, py, 0, px, py, r);
    g.addColorStop(0, 'rgba(255,255,255,0.55)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  }
  const m = x.createRadialGradient(128, 128, 60, 128, 128, 128);
  m.addColorStop(0, 'rgba(0,0,0,1)'); m.addColorStop(1, 'rgba(0,0,0,0)');
  x.globalCompositeOperation = 'destination-in'; x.fillStyle = m; x.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
})();

// (re)build rain + clouds sized to the current source; visibility follows toggles
function buildWeather() {
  const b = bounds(), hx = b.halfX, hz = b.halfZ, top = b.span * 0.45;
  mapSpan = b.span;                    // refresh the per-frame span cache on every terrain-source swap (HKS-103)
  if (rainPts) { world.remove(rainPts); rainPts.geometry.dispose(); rainPts.material.dispose(); }
  // rain as velocity-aligned streaks (HKS-11): drop heads live in rainHeads;
  // the geometry holds head+tail per drop, tails stretched along the fall vector
  const N = 6000;
  rainHeads = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    rainHeads[i*3] = (Math.random()*2 - 1) * hx;
    rainHeads[i*3+1] = Math.random() * top;
    rainHeads[i*3+2] = (Math.random()*2 - 1) * hz;
  }
  const rg = new THREE.BufferGeometry();
  rg.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 6), 3));
  rainPts = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0xaec8da, transparent: true, opacity: 0.38, depthWrite: false }));
  rainPts.userData.baseTop = top; rainPts.userData.N = N; rainPts.visible = weather.rain;
  world.add(rainPts);

  // snow (HKS-17): slower, lighter points that wobble as they drift down
  if (snowPts) { world.remove(snowPts); snowPts.geometry.dispose(); snowPts.material.dispose(); }
  const NS = 4500, spos = new Float32Array(NS * 3);
  snowMeta = new Float32Array(NS * 2);                 // [wobble phase, fall-speed factor]
  for (let i = 0; i < NS; i++) {
    spos[i*3] = (Math.random()*2 - 1) * hx;
    spos[i*3+1] = Math.random() * top * 0.8;
    spos[i*3+2] = (Math.random()*2 - 1) * hz;
    snowMeta[i*2] = Math.random() * Math.PI * 2;
    snowMeta[i*2+1] = 0.55 + Math.random() * 0.9;
  }
  const sg = new THREE.BufferGeometry();
  sg.setAttribute('position', new THREE.BufferAttribute(spos, 3));
  snowPts = new THREE.Points(sg, new THREE.PointsMaterial({ map: SNOW_TEX, color: 0xffffff,
    size: b.span * 0.0034, transparent: true, opacity: 0.85, depthWrite: false }));
  snowPts.userData.baseTop = top * 0.8; snowPts.userData.N = NS; snowPts.visible = weather.snow;
  world.add(snowPts);

  if (cloudGrp) { world.remove(cloudGrp); cloudGrp.traverse(o => o.material && o.material.dispose()); }
  cloudGrp = new THREE.Group();
  const size = b.span * 0.34;
  // three altitude decks (HKS-12): low cumulus, mid scattered, high thin veil.
  // cov buckets drive coverage (calm skies hide the tail; storms show everything)
  const DECKS = [
    { n: 18, y: 0.30, s: 1.0, flat: 0.50, op: 0.55 },
    { n: 12, y: 0.42, s: 1.3, flat: 0.34, op: 0.34 },
    { n: 8,  y: 0.56, s: 1.9, flat: 0.18, op: 0.20 },
  ];
  for (const d of DECKS) for (let i = 0; i < d.n; i++) {
    const tex = CLOUD_TEXS[(Math.random() * CLOUD_TEXS.length) | 0];
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color: 0xe2e8ef,
      transparent: true, opacity: d.op, depthWrite: false, rotation: Math.random() * 0.4 - 0.2 }));
    s.position.set((Math.random()*2-1)*hx, 0, (Math.random()*2-1)*hz);
    s.userData.baseY = b.span * (d.y + Math.random() * 0.06);
    s.userData.baseOp = d.op;
    s.userData.cov = Math.random();
    s.userData.drift = 0.6 + Math.random() * 0.8;   // per-cloud speed variance
    const w2 = size * d.s * (0.6 + Math.random());
    s.scale.set(w2, w2 * d.flat, 1);
    cloudGrp.add(s);
  }
  cloudGrp.visible = weather.clouds;
  world.add(cloudGrp);

  // pooled mist decks (HKS-14): translucent noise planes at low ABSOLUTE heights,
  // depth-tested against the terrain — haze fills the harbours and valley floors
  // while the hills poke through. Heights are metres above datum (× VE per frame).
  if (mistGrp) { world.remove(mistGrp); mistGrp.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); }); }
  mistGrp = new THREE.Group();
  const MIST_H = [6, 14, 26, 40];
  for (let i = 0; i < MIST_H.length; i++) {
    const w2 = b.span * (1.5 + i * 0.15);
    const mp = new THREE.Mesh(new THREE.PlaneGeometry(w2, w2),
      new THREE.MeshBasicMaterial({ map: MIST_TEX, transparent: true, opacity: 0.10,
        color: 0xdde6ee, depthWrite: false }));
    mp.rotation.set(-Math.PI / 2, 0, Math.random() * Math.PI);
    mp.userData.h = MIST_H[i];
    mistGrp.add(mp);
  }
  mistGrp.visible = weather.fog;
  world.add(mistGrp);

  // storm wall (HKS-21): a ragged ring of dark cloud circling the territory at
  // low altitude, slowly rotating — the eyewall feel under gale signals (T8+)
  if (wallGrp) { world.remove(wallGrp); wallGrp.traverse(o => o.material && o.material.dispose()); }
  wallGrp = new THREE.Group();
  const NW = 18, rr = b.span * 0.72;
  for (let i = 0; i < NW; i++) {
    const a = i / NW * Math.PI * 2, rj = 0.92 + Math.random() * 0.16;
    const s = new THREE.Sprite(new THREE.SpriteMaterial({
      map: CLOUD_TEXS[(Math.random() * CLOUD_TEXS.length) | 0], color: 0x3a4048,
      transparent: true, opacity: 0, depthWrite: false, rotation: Math.random() * 0.5 - 0.25 }));
    s.position.set(Math.cos(a) * rr * rj, 0, Math.sin(a) * rr * rj);
    s.userData.baseY = b.span * (0.10 + Math.random() * 0.05);
    const w2 = b.span * 0.42 * (0.8 + Math.random() * 0.5);
    s.scale.set(w2, w2 * 0.42, 1);
    wallGrp.add(s);
  }
  wallGrp.visible = false;
  world.add(wallGrp);
  applySkyScale();
  updateWindVisuals();
  if (liveMode) refreshCloudField();   // HKS-101: re-georeference the live field to the new bounds
  if (liveMode && lastWxData) WxField.rebuildFields(lastWxData);   // HKS-69: re-map the WxField rain/cloud grids to the new terrain source (codex)
  celKey = '';   // bounds changed: reposition sun/moon/stars for the new span
  if (matrixOn) applyMatrixLook();   // a source switch rebuilt the materials
}

// sky-layer height ×: view-only lift/scale of the weather layer (clouds + rain
// ceiling), so low clouds don't bury the peaks at high vertical exaggeration
function applySkyScale() {
  if (rainPts) rainPts.userData.top = rainPts.userData.baseTop * skyScale;
  if (snowPts) snowPts.userData.top = snowPts.userData.baseTop * skyScale;
  // storm ceilings hang lower — the decks drop as the wind rises
  const low = stormLevel > 0 ? 1 - 0.18 * windStrength : 1;
  if (cloudGrp) for (const s of cloudGrp.children) s.position.y = s.userData.baseY * skyScale * low;
  if (wallGrp) for (const s of wallGrp.children) s.position.y = s.userData.baseY * skyScale;
}

// shared clamped smoothstep — sky gradient, eclipse curve and star wash all use it
const S01 = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };
// perceptual luminance of the sky renderSky() last cleared to, in THREE's
// linear working space (~0.003 = deep night, ~0.345 = noon blue, ~0.87 = paper).
// stepSky() reads it every frame to decide how much the sky washes the stars
// out. Starts washed so a daytime load never flashes stars before the first
// renderSky().
let skyLum = 1;

// sun-altitude → sky colour: deep night, warm dawn/dusk, clear blue day.
// Chained smoothstep lerps keep the transitions band-free; palette is tunable.
function skyColour(altD, onPaper) {
  const P = onPaper
    ? { day: 0xcfe0f1, dusk: 0xf0a45f, night: 0x121a26 }   // paper: pale blue / soft amber / slate night
    : { day: 0x6ea3d8, dusk: 0xf4813c, night: 0x070a12 };  // dark: clear blue / warm dusk / deep night
  const c = new THREE.Color(P.night);
  c.lerp(new THREE.Color(P.dusk), 0.97 * S01((altD + 14) / 10));   // −14° night → −4° dusk (kept 15% night-blue so the whole dome never goes flat orange)
  c.lerp(new THREE.Color(P.day), S01((altD - 4) / 8));             // −4° dusk → +12° full day (wide golden hour — intentional)
  return c;
}

// clear colour + light levels: celestial sun/moon (when the sim is on) shape
// the key light and sky brightness; a storm then darkens whatever they chose.
function renderSky() {
  const onPaper = bgMode === 'paper';
  const k = stormLevel > 0 ? Math.min(0.6, 0.15 + windStrength * 0.55) : 0;
  const dim = 1 - (stormLevel > 0 ? windStrength * 0.4 : 0);
  // base sky: Stargaze is always a black planetarium (even at noon), Neon Night
  // keeps its noir void, otherwise the sun's altitude drives a day↔night
  // gradient; with the sky sim off the flat background stands.
  let base;
  if (stargaze.on)   base = new THREE.Color(0x05070d);
  else if (neonOn)   base = new THREE.Color(BG.dark);
  else if (cel)      base = skyColour(cel.sunAlt / D2R, onPaper);
  else               base = new THREE.Color(BG[bgMode]);
  // solar eclipse (normal sky only): the moon's coverage of the sun's disc pulls
  // the day sky toward black. The curve is deliberately steep — only deep coverage
  // (>80%) darkens at all, plunging toward night as it nears totality. Annular
  // eclipses cap below 1.0 (rMoon < rSun leaves a lit ring), so even at maximum they
  // bottom out at an eerie dusk rather than full black. Fog inherits it via the clear colour.
  const ecl = (cel && !stargaze.on && !neonOn) ? S01((cel.eclipse - 0.80) / 0.20) : 0;
  if (ecl > 0) base.lerp(new THREE.Color(0x01030a), ecl);
  let sunI = onPaper ? 2.4 : 2.0, hemiI = onPaper ? 1.9 : 1.4;
  if (cel) {
    const altD = cel.sunAlt / D2R;
    const dayF = Math.max(0, Math.min(1, (altD + 6) / 16));      // −6° → 0 … +10° → 1
    const day = altD > -6;
    const az = day ? cel.sunAz : cel.moonAz;
    const alt = Math.max(day ? cel.sunAlt : cel.moonAlt, 0.06);
    sun.position.set(Math.sin(az) * Math.cos(alt), Math.sin(alt), -Math.cos(az) * Math.cos(alt)).multiplyScalar(bounds().span);
    if (day) {
      const warm = Math.max(0, Math.min(1, 1 - altD / 12));      // golden/blue hour
      sun.color.setHex(0xffffff).lerp(new THREE.Color(0xff9a4d), warm * 0.8);
      sunI *= 0.12 + 0.88 * dayF;
      hemiI *= 0.3 + 0.7 * dayF;
    } else {                                                     // moonlight takes over
      const moonUp = Math.max(0, Math.sin(Math.max(cel.moonAlt, 0)));
      sun.color.setHex(0x9db8d8);
      sunI *= 0.18 * cel.frac * (moonUp > 0 ? 0.4 + 0.6 * moonUp : 0);
      hemiI *= 0.22;
    }
  } else sun.color.setHex(0xffffff);
  if (ecl > 0) { sunI *= 1 - 0.9 * ecl; hemiI *= 1 - 0.75 * ecl; }   // totality drops the daylight too, not just the dome
  if (snowAcc > 0 && !stargaze.on) {   // cooler, desaturated grade while snowing — but Stargaze's planetarium stays clear: lingering snowAcc must not tint its black or wash its stars
    sun.color.lerp(new THREE.Color(0xdce8f8), snowAcc * 0.45);
    base.lerp(new THREE.Color(0x9fb3c8), snowAcc * (onPaper ? 0.25 : 0.12));
  }
  base.lerp(new THREE.Color(0x1a2028), k);
  if (matrixOn) {                    // the void: near-black green, phosphor light
    base.setHex(0x020a05);
    sun.color.setHex(0x9cffb0);
  }
  // final sky luminance — the stars are washed out by how bright the sky *reads*.
  // Normally that's the composed dome (day gradient, eclipse, snow, storm), and
  // Stargaze's black planetarium is the deliberate "always stars" case. But Neon
  // Night and Matrix force an artistic dark base purely for the CLEAR COLOUR — the
  // stars must still follow the REAL sky (daylight hides them, night reveals them),
  // not the noir grade — so recompute their driving luminance from the natural sky.
  skyLum = 0.2126 * base.r + 0.7152 * base.g + 0.0722 * base.b;
  if ((neonOn || matrixOn) && !stargaze.on) {
    const realSky = cel ? skyColour(cel.sunAlt / D2R, onPaper) : new THREE.Color(BG[bgMode]);
    skyLum = 0.2126 * realSky.r + 0.7152 * realSky.g + 0.0722 * realSky.b;
  }
  renderer.setClearColor(base, 1);
  baseHemi = hemiI * dim;
  baseSun  = sunI * dim;
  hemi.intensity = baseHemi + flash * 5;
  sun.intensity  = baseSun;
}

function setFog() {
  if (!weather.fog) { scene.fog = null; return; }
  const b = bounds(), w = stormLevel > 0 ? windStrength : 0;
  const near = Math.max(b.span * 0.12, b.span * (0.35 - 0.08 * w));   // storm fog thickens (but stays past the camera)
  const far  = b.span * (1.5 - 0.35 * w);
  scene.fog = new THREE.Fog(renderer.getClearColor(new THREE.Color()).getHex(), near, far);
}

function animateWeather() {
  const b = bounds(), w = windStrength, hx = b.halfX, hz = b.halfZ;
  if (rainPts && rainPts.visible) {
    const g = rainPts.geometry, v = g.attributes.position.array;
    const top = rainPts.userData.top, N = rainPts.userData.N;
    const fall = b.span * 0.012 * (1 + w * 1.6);          // driving rain falls faster in wind
    const dx = windVec.x * b.span * 0.02 * w, dz = windVec.z * b.span * 0.02 * w;   // blown sideways
    // streak tails trail the velocity vector — longer with speed, sheet-like at T8+
    const stretch = (0.55 + w * 1.1) * (stormLevel >= 8 ? 1.5 : 1);
    const sx = -dx * stretch, sy = fall * stretch, sz = -dz * stretch;
    // HKS-69: regional rain — with live sync on, the per-district rainfall
    // field (WxField 'rain', rebuilt each 5-min sync) culls drops over dry
    // districts: each drop runs a stable lottery against its LOCAL density,
    // so a wet district pours while a dry one stays clear. Manual rain and
    // T8+ signals keep today's uniform territory-wide sheets.
    const rf = (liveMode && stormLevel < 8) ? WxField.get('rain') : null;
    const spatial = !!(rf && !rf.empty && rf.max > 0);
    for (let i = 0; i < N; i++) {
      let x = rainHeads[i*3] + dx, y = rainHeads[i*3+1] - fall, z = rainHeads[i*3+2] + dz;
      if (y < 0) y = top;
      if (x >  hx) x -= 2*hx; else if (x < -hx) x += 2*hx;   // wrap horizontally
      if (z >  hz) z -= 2*hz; else if (z < -hz) z += 2*hz;
      rainHeads[i*3] = x; rainHeads[i*3+1] = y; rainHeads[i*3+2] = z;
      const o = i * 6;
      if (spatial && (i * 0.618033988749895) % 1 >= rainMmToDensity(rf.sample(x, z))) {
        // dry district: collapse the streak to a point (invisible) — the head
        // keeps advecting, so the drop re-appears once it drifts somewhere wet
        v[o] = v[o+3] = x; v[o+1] = v[o+4] = y; v[o+2] = v[o+5] = z;
        continue;
      }
      v[o]   = x;      v[o+1] = y;      v[o+2] = z;
      v[o+3] = x + sx; v[o+4] = y + sy; v[o+5] = z + sz;
    }
    g.attributes.position.needsUpdate = true;
    // density tracks intensity: drizzle uses ~55% of the drops, gales all of them
    g.setDrawRange(0, Math.floor(N * (stormLevel >= 8 ? 1 : 0.55 + 0.45 * w)) * 2);
  }
  if (snowPts && snowPts.visible) {
    const p = snowPts.geometry.attributes.position.array, top = snowPts.userData.top, NS = snowPts.userData.N;
    const fall = b.span * 0.0022, wob = b.span * 0.0008;
    const dx = windVec.x * b.span * 0.009 * w, dz = windVec.z * b.span * 0.009 * w;
    for (let i = 0; i < NS; i++) {
      const ph = snowMeta[i*2], sf = snowMeta[i*2+1];
      p[i*3]   += dx + Math.cos(waveT * 1.8 + ph) * wob;         // flutter
      p[i*3+1] -= fall * sf;
      p[i*3+2] += dz + Math.sin(waveT * 1.4 + ph * 1.7) * wob * 0.7;
      if (p[i*3+1] < 0) p[i*3+1] = top;
      if (p[i*3]   >  hx) p[i*3]   -= 2*hx; else if (p[i*3]   < -hx) p[i*3]   += 2*hx;
      if (p[i*3+2] >  hz) p[i*3+2] -= 2*hz; else if (p[i*3+2] < -hz) p[i*3+2] += 2*hz;
    }
    snowPts.geometry.attributes.position.needsUpdate = true;
  }
  // the storm wall fades in and slowly circles the map under gale signals
  if (wallGrp) {
    const target = stormLevel >= 8 ? 0.42 + 0.25 * w : 0;
    wallOp += (target - wallOp) * 0.02;
    wallGrp.visible = wallOp > 0.01;
    if (wallGrp.visible) {
      wallGrp.rotation.y -= 0.0009 * (0.5 + w);          // cyclonic drift
      for (const s of wallGrp.children) s.material.opacity = wallOp;
    }
  }
  // snow-caps build while it snows, melt when it stops (~8 s each way);
  // the sky/light grade cools alongside
  const prevSnow = snowAcc;
  snowAcc = Math.max(0, Math.min(1, snowAcc + (weather.snow ? 0.002 : -0.002)));
  if (snowAcc !== prevSnow) renderSky();
  if (mistGrp && mistGrp.visible) {
    const drift = b.span * 0.00012 * (1 + w * 4), lim = b.span * 0.25;
    for (const mp of mistGrp.children) {
      mp.position.y = mp.userData.h * VE;                 // pooled height follows exaggeration
      mp.position.x += windVec.x * drift; mp.position.z += windVec.z * drift;
      if (mp.position.x >  lim) mp.position.x = -lim; else if (mp.position.x < -lim) mp.position.x = lim;
      if (mp.position.z >  lim) mp.position.z = -lim; else if (mp.position.z < -lim) mp.position.z = lim;
    }
  }
  if (cloudGrp && cloudGrp.visible) {
    const spd = b.span * 0.0006 * (1 + w * 7);            // clouds race with the wind
    const cx = windVec.x * spd, cz = windVec.z * spd, lx = hx * 1.3, lz = hz * 1.3;
    // HKS-101: with live sync on, a spatial cover field says which districts are
    // actually cloudy — each sprite fades toward its LOCAL cover (clear districts
    // genuinely open up, overcast ones fill in). Manual/storm skies keep the
    // uniform behaviour (updateWindVisuals owns opacity/visibility there).
    const fieldOn = cloudFieldActive();
    if (fieldOn) { cloudField.ox += cx; cloudField.oz += cz; }   // the field drifts with the deck
    for (const s of cloudGrp.children) {
      s.position.x += cx * s.userData.drift; s.position.z += cz * s.userData.drift;
      s.material.rotation += 0.00015 * s.userData.drift * (1 + w * 2);   // slow churn
      if (s.position.x >  lx) s.position.x = -lx; else if (s.position.x < -lx) s.position.x = lx;
      if (s.position.z >  lz) s.position.z = -lz; else if (s.position.z < -lz) s.position.z = lz;
      if (fieldOn) {
        const cov = cloudCoverAt(s.position.x, s.position.z);
        // the sprite's cov bucket jitters the threshold, so decks thin cloud-by-cloud
        let k = (cov - 0.12 - s.userData.cov * 0.22) / 0.45;
        k = Math.max(0, Math.min(1, k));
        const target = s.userData.baseOp * (1 + w * 0.9) * k * (0.6 + 0.4 * cov);
        const o = s.material.opacity + (target - s.material.opacity) * 0.05;   // eased — no popping across cells
        s.material.opacity = o;
        s.visible = o > 0.015;
      }
    }
  }
  // tide = slow water level; storm adds a surge on top; waves = ripple that gets
  // choppier (but still upward-only, so it never drains) as the wind picks up.
  if (sea) {
    // sea rests AT the coastline (SEA_Y); tide is a small band around mean (50% = mean),
    // sized to real HK tides (~±3 m) so it never floods the city. Storm adds a modest
    // surge on top, and waves a small upward chop.
    const tide   = (tideLevel - 0.5) * b.span * 0.00016;                       // ~±5 units ≈ ±3 m
    const surge  = stormLevel >= 8 ? (stormLevel >= 10 ? 1 : stormLevel >= 9 ? 0.65 : 0.4) * b.span * 0.00022 : 0;
    const amp    = b.span * (0.00004 + w * 0.0001);
    const ripple = weather.waves ? (Math.sin(wavePhase += 0.03 * (1 + w * 3)) * 0.5 + 0.5) * amp : 0;
    sea.position.y = SEA_Y + tide + surge + ripple;
  }
  // drive the surface FX: wet band from the live water level, cloud shadows
  // scrolling with the sprite drift, height fog pooling below uFogY
  const wy = (sea && sea.visible) ? sea.position.y : -1e9;
  const shadowSpd = b.span * 0.0006 * (1 + w * 7);          // match the cloud sprites
  let cAmt = (weather.clouds && cloudGrp) ? 0.4 + 0.45 * w : 0;
  if (cAmt && cloudFieldActive()) {   // HKS-101: ground shadows track the live field —
    // local cover at the view centre blended with the territory mean
    _cfV.copy(controls.target); world.worldToLocal(_cfV);
    cAmt *= 0.15 + 0.85 * (0.5 * cloudCoverAt(_cfV.x, _cfV.z) + 0.5 * cloudField.mean);
  }
  const fAmt = weather.fog ? 0.5 + 0.5 * w : 0;
  const fogY = (30 + w * 40) * VE;
  const waveAmp = weather.waves ? 0.14 + w * 0.22 : 0.05;   // calm water still shimmers a little
  waveT += 0.016 * (1 + w * 1.5);                           // seas quicken smoothly with the wind
  _sunDirV.copy(sun.position).normalize().transformDirection(camera.matrixWorldInverse);
  for (const m of tidalMats) {
    const sh = m.userData.sh; if (!sh) continue;
    sh.uniforms.uWaterY.value = wy; sh.uniforms.uBand.value = 4.5 * VE;
    const sc = 1.6 / b.span;
    sh.uniforms.uCloudScale.value = sc;
    sh.uniforms.uCloudOfs.value.x -= windVec.x * shadowSpd * sc;
    sh.uniforms.uCloudOfs.value.y -= windVec.z * shadowSpd * sc;
    sh.uniforms.uCloudAmt.value = cAmt;
    sh.uniforms.uFogAmt.value = fAmt;
    sh.uniforms.uFogY.value = fogY;
    sh.uniforms.uTime.value = waveT;
    sh.uniforms.uWaveAmp.value = waveAmp;
    sh.uniforms.uWaveK.value = 1100 / b.span;
    sh.uniforms.uFoamAmt.value = weather.waves ? 0.45 + 0.4 * w : 0.18;
    sh.uniforms.uSparkAmt.value = (m.userData.isWater && weather.rain) ? 0.35 + 0.45 * w : 0;
    if (m.userData.isWater) {
      sh.uniforms.uGlintAmt.value = 0.55 + w * 0.45;
      sh.uniforms.uSunDirV.value.copy(_sunDirV);
    }
    sh.uniforms.uSnowAmt.value = snowAcc * 0.9;
    sh.uniforms.uSnowLine.value = 380 * VE;
    renderer.getClearColor(sh.uniforms.uFogCol.value);
  }
  if (weather.lightning && matrixOn) {
    // HKS-103: the Matrix skin suppresses ALL lightning — live regional strikes
    // and the manual/global fallback alike — matching how updateHaze and
    // updateFloodCue bail out (the skin owns the phosphor palette; no white
    // flashes or bolts over the void). Kill any in-flight strike instantly
    // instead of letting it fade over the green.
    if (flash > 0) { flash = 0; hemi.intensity = baseHemi; }
    if (boltLife > 0) { boltLife = 0; disposeBolt(); if (boltLight) boltLight.intensity = 0; }
  }
  if (weather.lightning && !matrixOn) {
    // HKS-68: with live sync on (and no T8+ storm override, mirroring the rain
    // field gate) the LHL feed owns the strikes — the rate follows the
    // territory's real past-hour cloud-to-ground count (zero live strikes
    // anywhere = zero bolts), bolts land where the 'lightning' field is hot,
    // and thunder is loud under an active cell but a faint roll when the storm
    // is across the territory. Manual toggle / storm presets keep the global
    // uniform sim below.
    const live68 = liveMode && stormLevel < 8 && liveLtg;
    // rate keeps thunderRate's stormy-warning baseline even when the live past-hour
    // strike count is 0, so a warned storm still flashes instead of going dark (review #1)
    const rate = live68 ? Math.max(liveLtg.rate, thunderRate) : thunderRate;
    // localize placement only when the LHL field actually resolved region data;
    // else fall back to the global sim so bolts never land at empty-field/NaN coords (review #3)
    const ltgF = live68 && WxField.get('lightning');
    const localized = !!(ltgF && !ltgF.empty && ltgF.max > 0);
    if (flash > 0) { flash -= 0.08; hemi.intensity = baseHemi + flash * 5; }
    // quadratic, zero-floored: ~0 at low rate, intense near 100% (no always-on base term)
    else if (rate > 0 && Math.random() < rate * rate * 0.1) {
      if (localized) {
        const near = ltgNearCamera();   // 0..1 strike activity over the camera
        if (Math.random() < 0.25 + 0.5 * near) { spawnBolt(pickStrikeXZ()); flash = 0.6 + 0.4 * near; thunder(true, 0.25 + 0.75 * near); }
        else { flash = 0.55 * (0.4 + 0.6 * near); thunder(false, 0.25 + 0.75 * near); }   // sheet flash dims with distance from the cell
      }
      else if (Math.random() < 0.6) { spawnBolt(); flash = 1; thunder(true); }   // close forked strike
      else { flash = 0.55; thunder(false); }                 // distant sheet lightning
    }
  }
  if (boltLife > 0) {
    boltLife = Math.max(0, boltLife - 0.07);
    if (boltGrp) boltGrp.material.opacity = boltLife > 0.7 ? 1 : boltLife / 0.7;
    if (boltLight) boltLight.intensity = boltLife * 4;
    if (boltLife === 0) disposeBolt();
  }
  if (flashfx) flashfx.style.opacity = weather.lightning ? (flash * 0.6).toFixed(3) : 0;   // white screen flash
}

// Build one DOM label per named peak POI (data/hk-peaks.json). Positions are held
// in HK1980 E/N and converted to the current source's grid each frame, so one POI
// set serves every source. Chinese name on top, English · height below.
function buildLabels() {
  labels.forEach(l => l.div.remove()); labels = [];
  const list = (peaksData && peaksData.peaks) || [];
  for (const p of list) {
    const div = document.createElement('div'); div.className = 'lbl';
    const top = p.zh || p.en;
    const sub = (p.zh && p.en ? p.en + ' · ' : '') + p.ele + ' m';
    div.innerHTML = `${top}<small>${sub}</small>`;
    document.body.appendChild(div);
    labels.push({ div, E: p.E, N: p.N, ele: p.ele });
  }
}

// Curated landmark labels (iconic peaks + towns) — a separate, lighter POI layer.
function buildLandmarks() {
  landmarks.forEach(l => l.div.remove()); landmarks = [];
  const list = (landmarksData && landmarksData.landmarks) || [];
  for (const p of list) {
    const div = document.createElement('div'); div.className = 'lbl lmk';
    const icon = p.kind === 'peak' ? '⛰' : '📍';
    const top = `${icon} ${p.zh || p.en}`;
    const sub = p.kind === 'peak' ? (p.en + (p.ele ? ` · ${p.ele} m` : '')) : p.en;
    div.innerHTML = `${top}<small>${sub}</small>`;
    document.body.appendChild(div);
    landmarks.push({ div, E: p.E, N: p.N, ele: p.ele || 0 });
  }
  // positions of landmark peaks — the Peaks layer dedupes against these when both are on
  landmarkPeakPts = landmarks.filter(l => l.ele > 0).map(l => ({ E: l.E, N: l.N }));
}

// ---- vertical exaggeration drives terrain AND skin -------------------------
function applyVE() {
  const p = terrain.geometry.attributes.position.array;
  const nVerts = terrainBase.length / 3;
  for (let i = 0; i < nVerts; i++) p[i*3+1] = terrainBase[i*3+1] * VE;
  terrain.geometry.attributes.position.needsUpdate = true;
  terrain.geometry.computeVertexNormals();

  const off = skinOffset();
  for (const seg of (skin?.children ?? [])) {
    const base = skinBase.get(seg.name);
    const arr = seg.geometry.attributes.position.array;
    for (let i = 0; i < base.length; i++) arr[i*3+1] = base[i]*VE + off;
    seg.geometry.attributes.position.needsUpdate = true;
  }
  redrapeGpx();   // HKS-106: re-drape imported GPX trails onto the new exaggeration / source
  if (hikerGrp) hikerGrp.scale.setScalar(VE);   // review: keep the walk-mode figure sized to the live exaggeration (its scale was baked once at build)
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

// ---- web-map drape (OSM / satellite) --------------------------------------
// The terrain is in the HK1980 grid; web tiles are Web Mercator. We reproject
// the mesh UVs (not the imagery): each vertex E/N -> lon/lat (inverse HK1980 TM)
// -> Web Mercator, so a plain tile mosaic lands exactly on the terrain.
const HK = { a: 6378388.0, FE: 836694.05, FN: 819069.80, k0: 1.0 };
HK.f = 1 / 297; HK.e2 = HK.f * (2 - HK.f);
HK.lat0 = (22 + 18/60 + 43.68/3600) * Math.PI/180;
HK.lon0 = (114 + 10/60 + 42.80/3600) * Math.PI/180;
function meridianArc(lat) {
  const e2 = HK.e2, e4 = e2*e2, e6 = e2*e2*e2;
  return HK.a * ((1 - e2/4 - 3*e4/64 - 5*e6/256)*lat - (3*e2/8 + 3*e4/32 + 45*e6/1024)*Math.sin(2*lat)
    + (15*e4/256 + 45*e6/1024)*Math.sin(4*lat) - (35*e6/3072)*Math.sin(6*lat));
}
function enToLL(E, N) {                    // HK1980 grid -> { lon, lat } degrees
  const e2 = HK.e2, ep2 = e2/(1-e2);
  const M = meridianArc(HK.lat0) + (N - HK.FN)/HK.k0;
  const mu = M / (HK.a*(1 - e2/4 - 3*e2*e2/64 - 5*e2*e2*e2/256));
  const e1 = (1 - Math.sqrt(1-e2))/(1 + Math.sqrt(1-e2));
  const phi1 = mu + (3*e1/2 - 27*e1**3/32)*Math.sin(2*mu) + (21*e1*e1/16 - 55*e1**4/32)*Math.sin(4*mu)
    + (151*e1**3/96)*Math.sin(6*mu) + (1097*e1**4/512)*Math.sin(8*mu);
  const s = Math.sin(phi1), c = Math.cos(phi1), t = Math.tan(phi1);
  const C1 = ep2*c*c, T1 = t*t, N1 = HK.a/Math.sqrt(1 - e2*s*s), R1 = HK.a*(1-e2)/Math.pow(1 - e2*s*s, 1.5);
  const D = (E - HK.FE)/(N1*HK.k0);
  const lat = phi1 - (N1*t/R1)*(D*D/2 - (5 + 3*T1 + 10*C1 - 4*C1*C1 - 9*ep2)*D**4/24
    + (61 + 90*T1 + 298*C1 + 45*T1*T1 - 252*ep2 - 3*C1*C1)*D**6/720);
  const lon = HK.lon0 + (D - (1 + 2*T1 + C1)*D**3/6
    + (5 - 2*C1 + 28*T1 - 3*C1*C1 + 8*ep2 + 24*T1*T1)*D**5/120)/c;
  return { lon: lon*180/Math.PI, lat: lat*180/Math.PI };
}
const lonToMx = lon => (lon + 180)/360;
const latToMy = lat => { const r = lat*Math.PI/180; return (1 - Math.log(Math.tan(r) + 1/Math.cos(r))/Math.PI)/2; };
// constant Web-Mercator shift for the WGS84↔HK1980 datum difference (~270 m), from
// manual alignment on the Esri satellite skin (UV offset 0.0040, -0.0030 on the HK mosaic)
const DATUM_MX = 7.3242e-6, DATUM_MY = 4.3945e-6;
const mxToLon = mx => mx * 360 - 180;
const myToLat = my => Math.atan(Math.sinh(Math.PI * (1 - 2 * my))) * 180 / Math.PI;
// forward HK1980 Transverse Mercator (HK80 geodetic lon/lat -> grid E/N) — the exact
// complement of enToLL, reusing the same HK constants + meridianArc (HKS-83)
function llToEN(lat, lon) {
  const e2 = HK.e2, ep2 = e2 / (1 - e2);
  const phi = lat * Math.PI / 180, lam = lon * Math.PI / 180;
  const s = Math.sin(phi), c = Math.cos(phi), t = Math.tan(phi);
  const N1 = HK.a / Math.sqrt(1 - e2 * s * s), T = t * t, C = ep2 * c * c, A = (lam - HK.lon0) * c;
  const M = meridianArc(phi);
  const E = HK.FE + HK.k0 * N1 * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T * T + 72 * C - 58 * ep2) * A ** 5 / 120);
  const N = HK.FN + HK.k0 * (M - meridianArc(HK.lat0) + N1 * t * (A * A / 2 + (5 - T + 9 * C + 4 * C * C) * A ** 4 / 24 + (61 - 58 * T + T * T + 600 * C - 330 * ep2) * A ** 6 / 720));
  return { E, N };
}
// GPS (WGS84 lat/lon) -> HK1980 grid E/N. The WGS84↔HK80 datum step reverses the SAME
// baked Web-Mercator shift the satellite drape uses, so the marker lands exactly where
// the imagery shows you (a few metres, well under GPS's own error).
function gpsToEN(lat, lon) {
  const hlon = mxToLon(lonToMx(lon) - DATUM_MX), hlat = myToLat(latToMy(lat) - DATUM_MY);
  return llToEN(hlat, hlon);
}
// -> grid col/row against the loaded source; inBounds is false if the user is off the map
function gpsToGrid(lat, lon) {
  const { E, N } = gpsToEN(lat, lon), g = curG;
  if (!g) return null;
  const col = (E - g.bE) / g.aE, row = (N - g.bN) / g.aN;
  return { E, N, col, row, inBounds: col >= 0 && col <= W - 1 && row >= 0 && row <= H - 1 };
}
const TILE_SRC = {
  osm: { url: (z,x,y) => `https://tile.openstreetmap.org/${z}/${x}/${y}.png`, attr: '© OpenStreetMap contributors' },
  sat: { url: (z,x,y) => `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${z}/${y}/${x}`, attr: 'Imagery © Esri, Maxar, Earthstar Geographics' },
};

async function buildWebMap(kind) {
  const g = curG, tb = curTexbb;
  const corners = [[tb.E0,tb.N0],[tb.E1,tb.N0],[tb.E0,tb.N1],[tb.E1,tb.N1]].map(([E,N]) => {
    const ll = enToLL(E, N); return { mx: lonToMx(ll.lon), my: latToMy(ll.lat) };
  });
  const mx0 = Math.min(...corners.map(c=>c.mx)), mx1 = Math.max(...corners.map(c=>c.mx));
  const my0 = Math.min(...corners.map(c=>c.my)), my1 = Math.max(...corners.map(c=>c.my));
  let z = 16; while (z > 8 && (mx1-mx0)*Math.pow(2,z)*256 > 4096) z--;   // ~4k-px mosaic
  const n = Math.pow(2, z);
  const tx0 = Math.floor(mx0*n), tx1 = Math.floor(mx1*n), ty0 = Math.floor(my0*n), ty1 = Math.floor(my1*n);
  const cv = document.createElement('canvas'); cv.width = (tx1-tx0+1)*256; cv.height = (ty1-ty0+1)*256;
  const ctx = cv.getContext('2d'); ctx.fillStyle = '#8aa9c4'; ctx.fillRect(0, 0, cv.width, cv.height);
  const src = TILE_SRC[kind], jobs = [];
  for (let tx = tx0; tx <= tx1; tx++) for (let ty = ty0; ty <= ty1; ty++) {
    jobs.push(new Promise(res => {
      const img = new Image(); img.crossOrigin = 'anonymous';
      img.onload = () => { try { ctx.drawImage(img, (tx-tx0)*256, (ty-ty0)*256); } catch (_) {} res(); };
      img.onerror = () => res();
      img.src = src.url(z, tx, ty);
    }));
  }
  await Promise.all(jobs);
  const cmx0 = tx0/n, cmx1 = (tx1+1)/n, cmy0 = ty0/n, cmy1 = (ty1+1)/n;
  const pos = terrain.geometry.attributes.position.array, nV = pos.length/3, uv = new Float32Array(nV*2);
  for (let i = 0; i < nV; i++) {
    const c = pos[i*3]/cell + W/2, r = pos[i*3+2]/cell + H/2;
    const ll = enToLL(g.aE*c + g.bE, g.aN*r + g.bN);
    uv[i*2]   = (lonToMx(ll.lon) + DATUM_MX - cmx0)/(cmx1 - cmx0);   // + baked datum correction
    uv[i*2+1] = 1 - (latToMy(ll.lat) + DATUM_MY - cmy0)/(cmy1 - cmy0);
  }
  webUVAttr = new THREE.BufferAttribute(uv, 2);
  if (webTex) webTex.dispose();
  webTex = new THREE.CanvasTexture(cv);
  webTex.colorSpace = THREE.SRGBColorSpace;
  webTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  if (!matWeb) { matWeb = new THREE.MeshBasicMaterial(); matWeb.polygonOffset = true; matWeb.polygonOffsetFactor = 1; matWeb.polygonOffsetUnits = 1; attachTerrainFX(matWeb, false); }
  matWeb.map = webTex; matWeb.needsUpdate = true;
  webKind = kind;
}
function applyWebSurface() {
  terrain.visible = true;
  terrain.geometry.setAttribute('uv', webUVAttr);
  terrain.material = matWeb;
  const a = document.getElementById('mapattr'); a.textContent = TILE_SRC[webKind].attr;
}

function applyStyle(style) {
  surfStyle = style;
  const web = (style === 'osm' || style === 'sat');
  document.getElementById('solidrow').style.display = (style === 'solid') ? '' : 'none';
  document.getElementById('toporow').style.display = (style === 'topo') ? '' : 'none';
  document.getElementById('mapattr').style.display = web ? 'block' : 'none';
  // mesh lines are an independent overlay in ALL styles (incl. none)
  wireOverlay.visible = document.getElementById('meshlines').checked;
  wireLook();
  if (web) {
    if (webKind === style && webTex) { applyWebSurface(); return; }
    document.getElementById('note').textContent = t('note.loading') + ' ' + (style === 'osm' ? t('load.osm') : t('load.sat')) + '…';
    buildWebMap(style).then(() => { if (surfStyle === style) applyWebSurface(); updateNote(); })
      .catch(err => { document.getElementById('note').textContent = t('load.mapfail'); console.error(err); });
    return;
  }
  // non-web styles: restore the base (B50K-aligned) UVs
  if (baseUV) terrain.geometry.setAttribute('uv', new THREE.BufferAttribute(baseUV, 2));
  const mats = { shaded: matShaded, tint: matTint, matte: matMatte, solid: matSolid, topo: matTopo };
  terrain.visible = (style !== 'none');   // 'none' = no filled surface
  if (terrain.visible) terrain.material = mats[style] || matShaded;
}
function applyBg(mode) {
  bgMode = mode;
  renderSky();
  if (wireOverlay) wireLook();
  setFog();
  applyGlassPreset(mode);
}

// storm signal badge + wind visuals (rain density, cloud tone, sky) --------
function updateStormBadge() {
  // retired (William): the top-centre badge duplicated the signal already shown
  // in the live-weather box and collided with it on mobile. The panel's Storm
  // signal select (and the wx HUD when live) carry the state.
  document.getElementById('stormbadge').style.display = 'none';
}
// lock the controls that are driven for you: live mode owns everything; a storm
// signal owns the weather effects + wind strength (but you can still steer "wind from").
function applyControlLocks() {
  const g = id => document.getElementById(id);
  const storm = stormLevel > 0;
  const sg = document.body.classList.contains('stargazing');   // Stargaze clears + locks all weather/typhoon/live (HKS-91)
  ['rain', 'clouds', 'fog', 'lightning', 'waves', 'snow', 'wind', 'thunderrate'].forEach(id => g(id).disabled = liveMode || storm || sg);
  if (neonOn) g('snow').disabled = true;   // 風林火山 keeps Hong Kong snowbound
  g('winddir').disabled = liveMode || sg;   // direction stays adjustable under a storm
  g('tide').disabled    = liveMode || sg;
  g('storm').disabled   = liveMode || sg;
  g('skymode').disabled = liveMode;      // live weather owns the clock; Stargaze leaves sky/time adjustable (time=now, unlocked)
  const live = g('livebtn'); if (live) live.disabled = sg;   // no live-weather sync while stargazing
  const lock = g('wxlock');
  if (sg)           { lock.textContent = t('lock.stargaze'); lock.style.display = 'block'; }
  else if (liveMode){ lock.textContent = t('lock.live');  lock.style.display = 'block'; }
  else if (storm)   { lock.textContent = t('lock.storm'); lock.style.display = 'block'; }
  else              { lock.style.display = 'none'; }
  const slock = g('skylock');
  slock.textContent = t('lock.sky');
  slock.style.display = liveMode ? 'block' : 'none';
}
// ---- lightning bolts (HKS-13): forked channel geometry + localized glow ----
// A strike builds a midpoint-displaced main channel from cloud base to a random
// ground point, with 1–3 dying side forks, drawn additive and faded over ~15
// frames. A point light at the channel glows nearby terrain; the existing
// hemisphere pulse + screen flash stay in sync (sheet lightning skips the bolt).
let boltGrp = null, boltLife = 0, boltLight = null;
function disposeBolt() {
  if (boltGrp) { world.remove(boltGrp); boltGrp.geometry.dispose(); boltGrp.material.dispose(); boltGrp = null; }
}
function spawnBolt(at) {   // at: optional terrain-local { x, z } ground point (HKS-68); default random
  const b = bounds();
  disposeBolt();
  const gx = at ? at.x : (Math.random()*2 - 1) * b.halfX * 0.8, gz = at ? at.z : (Math.random()*2 - 1) * b.halfZ * 0.8;
  const low = stormLevel > 0 ? 1 - 0.18 * windStrength : 1;
  const topY = b.span * 0.30 * skyScale * low;               // cloud-base height
  const v = [];
  const jag = (x0, y0, z0, x1, y1, z1, steps, amp, forkDepth) => {
    let px = x0, py = y0, pz = z0;
    for (let i = 1; i <= steps; i++) {
      const t = i / steps;
      const nx = x0 + (x1-x0)*t + (Math.random()*2 - 1) * amp * (1 - t*0.5);
      const ny = y0 + (y1-y0)*t;
      const nz = z0 + (z1-z0)*t + (Math.random()*2 - 1) * amp * (1 - t*0.5);
      v.push(px, py, pz, nx, ny, nz);
      if (forkDepth > 0 && i > 2 && i < steps - 2 && Math.random() < 0.28) {
        jag(nx, ny, nz,
            nx + (Math.random()*2 - 1) * b.span*0.08, Math.max(ny - topY*(0.1 + Math.random()*0.2), 0),
            nz + (Math.random()*2 - 1) * b.span*0.08,
            4 + (Math.random()*3 | 0), amp * 0.6, forkDepth - 1);
      }
      px = nx; py = ny; pz = nz;
    }
  };
  jag(gx + (Math.random()*2-1)*b.span*0.05, topY, gz + (Math.random()*2-1)*b.span*0.05, gx, 0, gz,
      14, b.span * 0.02, 2);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(v), 3));
  boltGrp = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: matrixOn ? 0x66ff88 : 0xeaf4ff,
    transparent: true, opacity: 1, blending: THREE.AdditiveBlending, depthWrite: false }));
  world.add(boltGrp);
  if (!boltLight) { boltLight = new THREE.PointLight(0xcfe0ff, 0); world.add(boltLight); }
  boltLight.distance = b.span * 0.6;
  boltLight.position.set(gx, topY * 0.25, gz);
  boltLife = 1;
}

// HKS-68 helpers over the live 'lightning' WxField (LHL past-hour CG counts,
// one point per LHL region — see the WxField consumer). Both run only at
// strike time (a handful of O(1) bilinear lookups), never per frame.
const _ltgV = new THREE.Vector3();
function ltgField() {   // the field, or null when absent/empty/all-zero
  const f = WxField.get('lightning');
  return f && !f.empty && f.max > 0 ? f : null;
}
function ltgNearCamera() {   // 0..1 strike activity over the camera (0.5 when unknowable)
  const f = ltgField(); if (!f) return 0.5;
  _ltgV.copy(camera.position); world.worldToLocal(_ltgV);
  return Math.max(0, Math.min(1, f.sample(_ltgV.x, _ltgV.z) / f.max));
}
function pickStrikeXZ() {   // weighted-random ground point: P ∝ local field intensity
  const b = bounds(), f = ltgField();
  let x = 0, z = 0;
  for (let i = 0; i < 24; i++) {   // rejection sampling; falls back to the last candidate
    x = (Math.random()*2 - 1) * b.halfX * 0.8; z = (Math.random()*2 - 1) * b.halfZ * 0.8;
    if (!f || Math.random() * f.max <= f.sample(x, z)) break;
  }
  return { x, z };
}

function updateWindVisuals() {
  const w = windStrength;
  if (rainPts) rainPts.material.opacity = 0.3 + 0.4 * w;
  if (mistGrp) for (const mp of mistGrp.children) mp.material.opacity = 0.09 * (1 + w * 1.3);
  if (cloudGrp) {
    const d = stormLevel > 0 ? 1 - w * 0.55 : 1;
    const cover = 0.6 + w * 0.4;              // coverage builds toward overcast with the wind
    for (const s of cloudGrp.children) {
      if (matrixOn) s.material.color.setRGB(0.18 * d, 0.56 * d, 0.31 * d);   // banks of corrupted code
      else s.material.color.setRGB(0.89 * d, 0.91 * d, 0.94 * d);
      s.material.opacity = Math.min(1, s.userData.baseOp * (1 + w * 0.9));
      s.visible = s.userData.cov < cover;
    }
    applySkyScale();
  }
  renderSky(); setFog();
  updateAudioMix();
}
// apply a storm signal: preset the wind + escalate the weather effects
function applyStorm(level) {
  stormLevel = level;
  const sig = document.getElementById('wx-sig');           // compact HUD signal chip (collapsed view)
  if (sig) { sig.textContent = level > 0 ? 'T' + level : ''; sig.classList.toggle('sev', level >= 8); }
  windStrength = STORM_W[level] || 0;
  document.getElementById('wind').value = Math.round(windStrength * 100);
  document.getElementById('windv').textContent = Math.round(windStrength * 100) + '%';
  if (level > 0) {   // "None" just calms the wind and leaves your weather toggles alone
    const chk = (id, on) => { const e = document.getElementById(id); if (e.checked !== on) { e.checked = on; e.dispatchEvent(new Event('change', { bubbles: true })); } };
    chk('clouds', true);
    chk('rain', level >= 3);
    chk('waves', level >= 3);
    chk('fog', level >= 8);
    chk('lightning', level >= 8);
    if (level >= 8) setThunderRate(level >= 10 ? 0.9 : level >= 9 ? 0.65 : 0.45);   // storm drives strike rate
  }
  updateWindVisuals();
  updateStormBadge();
  applyControlLocks();
}
// HKO warning summary -> { level, dir? }
function stormFromWarn(ws) {
  const s = ws && ws.WTCSGNL;
  if (!s || !s.code || s.actionCode === 'CANCEL') return { level: 0 };
  const c = s.code;                                   // TC1 / TC3 / TC8NE.. / TC9 / TC10
  if (c === 'TC1') return { level: 1 };
  if (c === 'TC3') return { level: 3 };
  if (c === 'TC9') return { level: 9 };
  if (c === 'TC10') return { level: 10 };
  if (c.startsWith('TC8')) return { level: 8, dir: c.slice(3) };
  return { level: 0 };
}

// ---- sun & moon simulation (HKS-1) ------------------------------------------
// Real celestial positions over Hong Kong drive the key light, sky brightness
// and two sprite bodies that rise and set behind the actual terrain. Pure math
// (vendor/astro.js) — no API. Defaults to live HKT; a date + time scrub lets
// you replay any sky. World axes: -z = north, +x = east.
const HK_LAT = 22.302, HK_LON = 114.174, D2R = Math.PI / 180;
const skySim = { on: true, live: true, date: '', minutes: 720 };
let cel = null, celKey = '', moonTexPhase = -1;

const hktDateStr = d => new Date(d.getTime() + 8 * 3.6e6).toISOString().slice(0, 10);
const hktMinutes = d => { const t = new Date(d.getTime() + 8 * 3.6e6); return t.getUTCHours() * 60 + t.getUTCMinutes(); };
const mmToHHMM = m => `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
const hktHHMM = d => d ? d.toLocaleTimeString('en-GB', { timeZone: 'Asia/Hong_Kong', hour12: false }).slice(0, 5) : '—';
skySim.date = hktDateStr(new Date());
skySim.minutes = hktMinutes(new Date());
function simDate() {
  return skySim.live ? new Date()
    : new Date(`${skySim.date}T${mmToHHMM(skySim.minutes)}:00+08:00`);
}

// sun: a white-hot disc + a slowly turning crown of soft rays (both additive)
function makeSunTextures() {
  const d = document.createElement('canvas'); d.width = d.height = 128;
  let x = d.getContext('2d');
  let g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.22, 'rgba(255,246,220,1)');
  g.addColorStop(0.38, 'rgba(255,214,140,.85)'); g.addColorStop(0.62, 'rgba(255,176,90,.25)');
  g.addColorStop(1, 'rgba(255,160,70,0)');
  x.fillStyle = g; x.fillRect(0, 0, 128, 128);
  const r = document.createElement('canvas'); r.width = r.height = 256;
  x = r.getContext('2d');
  g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, 'rgba(255,220,160,.55)'); g.addColorStop(0.35, 'rgba(255,190,120,.16)');
  g.addColorStop(1, 'rgba(255,170,90,0)');
  x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  x.translate(128, 128); x.lineCap = 'round';
  for (let i = 0; i < 14; i++) {                          // long/short alternating rays
    const a = i / 14 * Math.PI * 2 + (i % 2 ? 0.13 : 0);
    const len = 112 * (i % 2 ? 0.66 : 1), lw = i % 2 ? 4.5 : 7.5;
    const lg = x.createLinearGradient(0, 0, Math.cos(a) * len, Math.sin(a) * len);
    lg.addColorStop(0, 'rgba(255,236,190,.5)'); lg.addColorStop(0.55, 'rgba(255,210,140,.14)');
    lg.addColorStop(1, 'rgba(255,190,110,0)');
    x.strokeStyle = lg; x.lineWidth = lw;
    x.beginPath(); x.moveTo(Math.cos(a) * 18, Math.sin(a) * 18); x.lineTo(Math.cos(a) * len, Math.sin(a) * len); x.stroke();
  }
  return { disc: new THREE.CanvasTexture(d), rays: new THREE.CanvasTexture(r) };
}

// moon (HKS-78): limb-darkened disc, soft-edged maria + ray craters, a phase
// terminator laid down as a graded penumbra, and earthshine cradling thin
// crescents. Drawn with the lit limb always toward +x — stepSky() then spins
// the sprite so that limb tracks the real sun, which keeps waxing/waning and
// horizon-tilted phases honest without redrawing.
const MOON_MARIA = [   // [dx, dy, r, alpha] in unit-radius moon space, +x = lit limb
  [-0.25, -0.32, 0.30, 0.21], [0.18, -0.14, 0.36, 0.23], [-0.07, 0.21, 0.24, 0.20],
  [0.39, 0.29, 0.16, 0.18], [-0.46, 0.11, 0.14, 0.17], [0.29, -0.46, 0.13, 0.17],
  [0.05, -0.55, 0.10, 0.14], [-0.35, 0.42, 0.10, 0.13]];
const MOON_CRATERS = [ // bright ray craters — [dx, dy, r]
  [0.10, 0.56, 0.050], [-0.52, -0.20, 0.038], [0.58, -0.30, 0.034], [-0.16, 0.70, 0.028]];
function drawMoonTexture(phase, frac) {
  const S = 256, c = document.createElement('canvas'); c.width = c.height = S;
  const x = c.getContext('2d'), cx = S / 2, r = S * 0.44;
  const g = x.createRadialGradient(cx + r * 0.32, cx - r * 0.18, r * 0.1, cx, cx, r);
  g.addColorStop(0, '#f6f8fa'); g.addColorStop(0.55, '#dfe6ee');
  g.addColorStop(0.85, '#bfc9d6'); g.addColorStop(1, '#8b97a7');
  x.fillStyle = g; x.beginPath(); x.arc(cx, cx, r, 0, 7); x.fill();
  for (const [dx, dy, rr, a] of MOON_MARIA) {             // soft-edged seas
    const mx = cx + dx * r, my = cx + dy * r;
    const mg = x.createRadialGradient(mx, my, 0, mx, my, rr * r);
    const ma = Math.min(0.92, a * 1.5);                    // deeper, crisper seas so the texture reads
    mg.addColorStop(0, `rgba(72,84,102,${ma.toFixed(3)})`); mg.addColorStop(0.78, `rgba(72,84,102,${(ma * 0.82).toFixed(3)})`);
    mg.addColorStop(1, 'rgba(72,84,102,0)');
    x.fillStyle = mg; x.beginPath(); x.arc(mx, my, rr * r, 0, 7); x.fill();
  }
  for (const [dx, dy, rr] of MOON_CRATERS) {              // pinpricks of fresh ejecta
    const mx = cx + dx * r, my = cx + dy * r;
    const cg = x.createRadialGradient(mx, my, 0, mx, my, rr * r * 2.4);
    cg.addColorStop(0, 'rgba(255,255,255,.3)'); cg.addColorStop(0.35, 'rgba(255,255,255,.1)');
    cg.addColorStop(1, 'rgba(255,255,255,0)');
    x.fillStyle = cg; x.beginPath(); x.arc(mx, my, rr * r * 2.4, 0, 7); x.fill();
  }
  // terminator: five graded passes give the shadow edge a real penumbra; thin
  // crescents keep a translucent shadow so earthshine lets the maria ghost through
  const k = Math.cos(phase * 2 * Math.PI);                // 1 new → −1 full
  const es = Math.max(0, Math.min(1, (0.25 - frac) / 0.22));   // earthshine strength
  const aPass = 1 - Math.pow(1 - (0.93 - 0.1 * es), 1 / 5);
  x.globalCompositeOperation = 'source-atop';
  x.fillStyle = `rgba(${16 + 18 * es | 0},${21 + 20 * es | 0},${34 + 24 * es | 0},${aPass.toFixed(3)})`;
  for (let i = 0; i < 5; i++) {
    const kk = Math.max(-1, Math.min(1, k + 0.05 * (i / 2 - 1)));
    x.beginPath();
    x.arc(cx, cx, r, -Math.PI / 2, Math.PI / 2, true);    // dark half on the left
    x.ellipse(cx, cx, r * Math.abs(kk), r, 0, Math.PI / 2, -Math.PI / 2, kk > 0);
    x.fill();
  }
  if (es > 0) {                    // ashen light: the old moon in the new moon's arms
    const eg = x.createLinearGradient(0, 0, S, 0);
    eg.addColorStop(0, `rgba(150,166,194,${(0.1 * es).toFixed(3)})`);
    eg.addColorStop(0.55, `rgba(150,166,194,${(0.05 * es).toFixed(3)})`);
    eg.addColorStop(0.75, 'rgba(150,166,194,0)');
    x.fillStyle = eg; x.fillRect(0, 0, S, S);
  }
  x.globalCompositeOperation = 'source-over';
  return new THREE.CanvasTexture(c);
}
const SUN_TEX = makeSunTextures();
const MOON_GLOW_TEX = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d');
  const g = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  g.addColorStop(0, 'rgba(210,226,246,.6)'); g.addColorStop(0.22, 'rgba(198,215,238,.28)');
  g.addColorStop(0.5, 'rgba(186,206,232,.11)'); g.addColorStop(0.78, 'rgba(180,200,230,.035)');
  g.addColorStop(1, 'rgba(180,200,230,0)');
  x.fillStyle = g; x.fillRect(0, 0, 256, 256);
  return new THREE.CanvasTexture(c);
})();
const sunRays = new THREE.Sprite(new THREE.SpriteMaterial({ map: SUN_TEX.rays, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.85 }));
const sunSpr  = new THREE.Sprite(new THREE.SpriteMaterial({ map: SUN_TEX.disc, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
const moonGlow = new THREE.Sprite(new THREE.SpriteMaterial({ map: MOON_GLOW_TEX, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
const moonSpr  = new THREE.Sprite(new THREE.SpriteMaterial({ transparent: true, depthWrite: false }));
sunRays.visible = sunSpr.visible = moonGlow.visible = moonSpr.visible = false;
scene.add(sunRays, sunSpr, moonGlow, moonSpr);            // scene, not world: sky doesn't auto-spin

// ---- star field (HKS-3, deepened for HKS-78): stargazing over Hong Kong ----
// One sidereally-rotated celestial sphere carries three layers: a procedural
// deep field (thousands of faint stars, Milky-Way-weighted, deterministic
// seed), a soft galactic haze wash, and the named-star catalogue with real
// colour temperatures + constellation figures. Each layer is one THREE.Points
// with per-star attributes (size / colour / twinkle phase & depth / halo); a
// uTime uniform breathes them slowly in the vertex shader. Sidereal motion is
// a single rigid rotation of the group per sim-minute — zero per-star JS after
// build. Fades in through astronomical twilight; a bright moon washes out its
// own neighbourhood (uMoonDir) on top of the global dim.
let starLines = null;
const SKY_COARSE = matchMedia('(pointer: coarse)').matches;
const SKY_N = { deep: SKY_COARSE ? 2000 : 4500, haze: SKY_COARSE ? 150 : 340 };
const starGroup = new THREE.Group();
starGroup.visible = false;
scene.add(starGroup);
const starUniforms = { uTime: { value: 0 }, uFade: { value: 0 }, uDpr: { value: 1 },
                       uMoonDir: { value: new THREE.Vector3(0, -1, 0) }, uMoonWash: { value: 0 },
                       uSelGain: { value: 2.3 } };   // HKS-84: brightness gain on selected constellations
const STAR_VERT = `
  attribute float aSize; attribute vec3 aColor;
  attribute float aPhase; attribute float aTwk; attribute float aHalo; attribute float aSel;
  uniform float uTime, uFade, uDpr, uMoonWash, uSelGain;
  uniform vec3 uMoonDir;
  varying vec3 vColor; varying float vI, vHalo;
  void main() {
    vec4 wp = modelMatrix * vec4(position, 1.0);
    vec3 dir = normalize(wp.xyz);
    float horizon = smoothstep(-0.02, 0.055, dir.y);   // melt at the skyline, hide set stars
    float tw = 1.0 - aTwk * (0.5 + 0.3 * sin(uTime * 0.31 + aPhase)
                                 + 0.2 * sin(uTime * 0.53 + aPhase * 2.09));
    tw = mix(tw, 1.0, 0.55 * aSel);                    // selected stars steady their breathing
    float wash = 1.0 - uMoonWash * (0.4 + 0.6 * smoothstep(0.45, 0.99, dot(dir, uMoonDir)));
    wash = mix(wash, 1.0, 0.5 * aSel);                 // and punch through the moon wash
    vI = uFade * horizon * max(tw, 0.0) * max(wash, 0.0) * mix(1.0, uSelGain, aSel);
    vColor = aColor; vHalo = max(aHalo, 0.7 * aSel);
    gl_PointSize = aSize * uDpr * (0.85 + 0.3 * tw) * (1.0 + 0.3 * aSel);
    gl_Position = projectionMatrix * viewMatrix * wp;
  }`;
const STAR_FRAG = `
  varying vec3 vColor; varying float vI, vHalo;
  void main() {
    vec2 q = gl_PointCoord - 0.5;
    float d = length(q) * 2.0;
    float lim = smoothstep(1.0, 0.8, d);
    float core = exp(-d * d * 9.0);
    float glow = exp(-d * 2.4) * 0.62 * max(vHalo, 0.24) * lim;   // wider, brighter halo = more "spread"
    vec2 aq = abs(q);                    // faint diffraction cross on the bright ones
    float spike = exp(-min(aq.x, aq.y) * 30.0) * exp(-d * 2.5) * 0.4 * vHalo * lim;
    float i = (core + glow + spike) * vI;
    if (i < 0.004) discard;
    gl_FragColor = vec4(vColor, i);
  }`;
const HAZE_FRAG = `
  varying vec3 vColor; varying float vI, vHalo;
  void main() {
    float d = length(gl_PointCoord - 0.5) * 2.0;
    float s = max(1.0 - d, 0.0);
    float i = s * s * vI;
    if (i < 0.004) discard;
    gl_FragColor = vec4(vColor, i);
  }`;
const starMat = new THREE.ShaderMaterial({ uniforms: starUniforms, vertexShader: STAR_VERT,
  fragmentShader: STAR_FRAG, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
const hazeMat = new THREE.ShaderMaterial({ uniforms: starUniforms, vertexShader: STAR_VERT,
  fragmentShader: HAZE_FRAG, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending });
function bakeStars(n, fill, mat) {       // fill(i, set) writes one star through set(...)
  const pos = new Float32Array(n * 3), col = new Float32Array(n * 3), size = new Float32Array(n),
        phase = new Float32Array(n), twk = new Float32Array(n), halo = new Float32Array(n);
  const set = (i, v, c, s, ph, tw, ha) => {
    pos[i*3] = v[0]; pos[i*3+1] = v[1]; pos[i*3+2] = v[2];
    col[i*3] = c[0]; col[i*3+1] = c[1]; col[i*3+2] = c[2];
    size[i] = s; phase[i] = ph; twk[i] = tw; halo[i] = ha;
  };
  for (let i = 0; i < n; i++) fill(i, set);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
  g.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
  g.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
  g.setAttribute('aTwk', new THREE.BufferAttribute(twk, 1));
  g.setAttribute('aHalo', new THREE.BufferAttribute(halo, 1));
  g.setAttribute('aSel', new THREE.BufferAttribute(new Float32Array(n), 1));   // HKS-84 selection level
  const p = new THREE.Points(g, mat);
  p.frustumCulled = false;               // we live inside the sphere
  starGroup.add(p);
  return p;
}
// B−V colour index → gentle warm/cool RGB (piecewise fit)
function bvColor(bv, out) {
  const S = [[-0.33, 0.62, 0.75, 1], [0, 0.84, 0.9, 1], [0.4, 1, 0.98, 0.94],
             [0.8, 1, 0.92, 0.81], [1.5, 1, 0.81, 0.59], [2, 1, 0.71, 0.45]];
  bv = Math.max(-0.33, Math.min(2, bv));
  let a = S[0], b = S[1];
  for (let i = 0; i < S.length - 1; i++) if (bv >= S[i][0]) { a = S[i]; b = S[i + 1]; }
  const t = (bv - a[0]) / (b[0] - a[0]);
  out[0] = a[1] + (b[1] - a[1]) * t; out[1] = a[2] + (b[2] - a[2]) * t; out[2] = a[3] + (b[3] - a[3]) * t;
  return out;
}
// galactic (l, b) → equatorial J2000 unit vector (IAU rotation, transposed)
function galToEq(l, b, out) {
  const gx = Math.cos(b) * Math.cos(l), gy = Math.cos(b) * Math.sin(l), gz = Math.sin(b);
  out[0] = -0.0548755604 * gx + 0.4941094279 * gy - 0.8676661490 * gz;
  out[1] = -0.8734370902 * gx - 0.4448296300 * gy - 0.1980763734 * gz;
  out[2] = -0.4838350155 * gx + 0.7469822445 * gy + 0.4559837762 * gz;
  return out;
}
{ // deep field + Milky-Way haze — deterministic seed, so everyone shares one sky
  let seed = 76543210;
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  const v = [0, 0, 0], c = [0, 0, 0];
  bakeStars(SKY_N.deep, (i, set) => {
    const band = rnd() < 0.42;           // extra stars crowd the galactic plane
    if (band) galToEq(rnd() * Math.PI * 2, (rnd() + rnd() - 1) * 0.16, v);
    else { const z = rnd() * 2 - 1, a = rnd() * Math.PI * 2, q = Math.sqrt(1 - z * z);
           v[0] = q * Math.cos(a); v[1] = q * Math.sin(a); v[2] = z; }
    const m = rnd();                     // pseudo-magnitude — most stars stay faint
    bvColor(-0.25 + 2.1 * Math.pow(rnd(), 2.6), c);
    const lum = (0.72 + 0.58 * m) * (band ? 0.9 : 1);   // brighter so faint stars read
    set(i, v, [c[0] * lum, c[1] * lum, c[2] * lum],
        (1.4 + 2.8 * m * m) * (band ? 0.92 : 1), rnd() * Math.PI * 2, 0.24 + 0.3 * rnd(), 0.18 * m);
  }, starMat);
  bakeStars(SKY_N.haze, (i, set) => {    // the soft wash behind the band
    const l = rnd() * Math.PI * 2;
    galToEq(l, (rnd() + rnd() - 1) * 0.13, v);
    const dl = Math.min(l, Math.PI * 2 - l);   // brightest toward the galactic core
    const lum = (0.024 + 0.026 * rnd()) * (0.7 + 0.9 * Math.exp(-(dl / 0.85) * (dl / 0.85)));
    set(i, v, [0.58 * lum, 0.66 * lum, 0.95 * lum], 20 + 26 * rnd(), rnd() * Math.PI * 2, 0.12, 0);
  }, hazeMat);
}
// ---- HKS-84: the real sky — BSC5 catalogue + interactive constellations -----
// data/hk-sky.json (built by source-scripts/hk-sky/build_hk_sky.mjs) carries
// ~1,570 Yale Bright Star Catalogue stars [HR, ra_h, dec°, mag, B−V] and ~24
// curated IAU constellations with stick figures keyed by HR. Member stars
// brighten through a per-star aSel attribute (one buffer upload per selection
// change, eased ~250 ms in stepSky); figures draw twice — a faint always-on
// ghost inviting exploration, and a dynamic highlight layer for the selection.
let skyCat = null;   // { stars, dirs, aSel, cons[], selGeo, selPos, selLvl }
const skySel = { hover: -1, taps: new Set(), auto: new Set(), lastPick: 0, lastAuto: 0, anim: false };
const CON_PICK_RAD = 3.5 * D2R;   // hover/tap: max angular distance ray → figure segment
fetch(asset('data/hk-sky.json')).then(r => {
  if (!r.ok) throw new Error(`hk-sky.json HTTP ${r.status}`);
  return r.json();
}).then(d => {
  const n = d.stars.length;
  const dirs = new Float32Array(n * 3);
  const hrIdx = new Map();
  for (let i = 0; i < n; i++) {
    const s = d.stars[i];                              // [HR, ra_hours, dec_deg, mag, bv]
    const ra = s[1] / 24 * Math.PI * 2, dec = s[2] * D2R;
    dirs[i*3] = Math.cos(dec) * Math.cos(ra); dirs[i*3+1] = Math.cos(dec) * Math.sin(ra);
    dirs[i*3+2] = Math.sin(dec);
    hrIdx.set(s[0], i);
  }
  const c = [0, 0, 0], v = [0, 0, 0];
  const pts = bakeStars(n, (i, set) => {
    const s = d.stars[i], mag = s[3];
    bvColor(s[4], c);
    // magnitude → size/halo/lum: Sirius ~8.6 px full halo, the mag-5 crowd
    // ~1.7 px — meeting the procedural deep field (1.4–4.2 px) where they blend
    const lum = Math.max(0.62, Math.min(1.05, 1.05 - 0.09 * (mag - 1)));
    v[0] = dirs[i*3]; v[1] = dirs[i*3+1]; v[2] = dirs[i*3+2];
    set(i, v, [c[0] * lum, c[1] * lum, c[2] * lum],
        Math.max(1.7, Math.min(10, 7.0 - 1.1 * mag)),
        (i * 2.399) % (Math.PI * 2),     // golden-angle phases: no two neighbours breathe together
        Math.max(0.08, Math.min(0.42, 0.1 + 0.06 * (mag + 1.5))),
        Math.max(0, Math.min(1, (2.0 - mag) / 2.4)));
  }, starMat);
  // constellation records: star indices, figure segments, centroid direction
  const _cv = new THREE.Vector3();
  const cons = d.constellations.map(cd => {
    const idx = cd.stars.map(hr => hrIdx.get(hr));
    const segs = cd.lines.map(([a, b]) => [hrIdx.get(a), hrIdx.get(b)]);
    const ra = cd.centroid[0] / 24 * Math.PI * 2, dec = cd.centroid[1] * D2R;
    const dir = new THREE.Vector3(Math.cos(dec) * Math.cos(ra), Math.cos(dec) * Math.sin(ra), Math.sin(dec));
    let rad = 0;
    for (const i of idx) rad = Math.max(rad, dir.angleTo(_cv.set(dirs[i*3], dirs[i*3+1], dirs[i*3+2])));
    return { iau: cd.iau, en: cd.en, zh: cd.zh, idx, segs, dir, rad, lvl: 0, tgt: 0, div: null };
  });
  // ghost figures: every curated segment, always on but barely-there
  const nSeg = cons.reduce((a, cc) => a + cc.segs.length, 0);
  const ga = new Float32Array(nSeg * 6);
  let k = 0;
  for (const cc of cons) for (const [a, b] of cc.segs) {
    ga.set(dirs.subarray(a*3, a*3+3), k); ga.set(dirs.subarray(b*3, b*3+3), k + 3); k += 6;
  }
  const lg = new THREE.BufferGeometry();
  lg.setAttribute('position', new THREE.BufferAttribute(ga, 3));
  starLines = new THREE.LineSegments(lg, new THREE.ShaderMaterial({
    uniforms: starUniforms, transparent: true, depthWrite: false,
    vertexShader: `varying float vY;
      void main() { vec4 wp = modelMatrix * vec4(position, 1.0);
        vY = normalize(wp.xyz).y; gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform float uFade; varying float vY;
      void main() { float a = uFade * 0.15 * smoothstep(0.0, 0.06, vY);
        if (a < 0.004) discard; gl_FragColor = vec4(0.62, 0.71, 0.85, a); }`,
  }));
  starLines.frustumCulled = false;
  starGroup.add(starLines);
  // highlight figures: a small dynamic buffer, rebuilt only while a selection eases
  const selPos = new Float32Array(nSeg * 6), selLvl = new Float32Array(nSeg * 2);
  const selGeo = new THREE.BufferGeometry();
  selGeo.setAttribute('position', new THREE.BufferAttribute(selPos, 3));
  selGeo.setAttribute('aLvl', new THREE.BufferAttribute(selLvl, 1));
  selGeo.setDrawRange(0, 0);
  const selLines = new THREE.LineSegments(selGeo, new THREE.ShaderMaterial({
    uniforms: starUniforms, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `attribute float aLvl; varying float vY, vL;
      void main() { vec4 wp = modelMatrix * vec4(position, 1.0);
        vY = normalize(wp.xyz).y; vL = aLvl; gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform float uFade; varying float vY, vL;
      void main() { float a = uFade * 0.55 * vL * smoothstep(0.0, 0.06, vY);
        if (a < 0.004) discard; gl_FragColor = vec4(0.62, 0.74, 1.0, a); }`,
  }));
  selLines.frustumCulled = false;
  starGroup.add(selLines);
  skyCat = { stars: d.stars, dirs, aSel: pts.geometry.getAttribute('aSel'), cons, selGeo, selPos, selLvl };
  celKey = '';   // force a celestial refresh so the sky populates immediately
}).catch(err => console.error('HKS-84: failed to load sky catalogue (data/hk-sky.json)', err));
// selection targets: hover (desktop) ∪ taps (mobile toggle) ∪ auto (stargazing walk)
function conRetarget() {
  if (!skyCat) return;
  skyCat.cons.forEach((c, i) => {
    c.tgt = (skySel.hover === i || skySel.taps.has(i) || skySel.auto.has(i)) ? 1 : 0;
    if (c.tgt !== c.lvl) skySel.anim = true;
  });
}
function conClearAll() {
  if (skySel.hover < 0 && !skySel.taps.size && !skySel.auto.size) return;
  skySel.hover = -1; skySel.taps.clear(); skySel.auto.clear();
  conRetarget();
}
// rebuild the highlight-figure buffer from constellations with any glow
function rebuildSelLines() {
  const { cons, dirs, selGeo, selPos, selLvl } = skyCat;
  let k = 0;
  for (const c of cons) {
    if (c.lvl < 0.01) continue;
    for (const [a, b] of c.segs) {
      selPos.set(dirs.subarray(a*3, a*3+3), k*3); selPos.set(dirs.subarray(b*3, b*3+3), k*3+3);
      selLvl[k] = selLvl[k+1] = c.lvl;
      k += 2;
    }
  }
  selGeo.setDrawRange(0, k);
  selGeo.attributes.position.needsUpdate = true;
  selGeo.attributes.aLvl.needsUpdate = true;
}
// hover/tap picking: angular distance from the pointer ray to each figure's
// segments (in the sidereal catalogue frame) — never a Points raycast
const _pkR = new THREE.Vector3(), _pkQ = new THREE.Quaternion(), _pkA = new THREE.Vector3(),
      _pkB = new THREE.Vector3(), _pkN = new THREE.Vector3(), _pkP = new THREE.Vector3();
function arcDist(p, a, b) {   // angular distance from unit vector p to great-circle arc a→b
  _pkN.crossVectors(a, b);
  const nl = _pkN.length();
  if (nl < 1e-6) return p.angleTo(a);
  _pkN.divideScalar(nl);
  const s = p.dot(_pkN);
  _pkP.copy(p).addScaledVector(_pkN, -s).normalize();   // p projected onto the great circle
  const arc = a.angleTo(b);
  if (_pkP.angleTo(a) <= arc && _pkP.angleTo(b) <= arc) return Math.abs(Math.asin(Math.max(-1, Math.min(1, s))));
  return Math.min(p.angleTo(a), p.angleTo(b));
}
function pickConstellation(clientX, clientY) {
  if (!skyCat || !starGroup.visible) return -1;
  _pkR.set((clientX / innerWidth) * 2 - 1, -(clientY / innerHeight) * 2 + 1, 0.5)
      .unproject(camera).sub(camera.position).normalize();
  // the camera is NOT at the celestial sphere's centre — intersect the pointer
  // ray with the sphere and take the hit point's direction, else parallax
  // skews the pick by up to ~25° when orbiting far off-centre
  const R = starGroup.scale.x || 1;
  const od = camera.position.dot(_pkR), oo = camera.position.lengthSq();
  const disc = od * od - oo + R * R;
  if (disc <= 0) return -1;                            // ray misses the sphere entirely
  // nearest intersection ahead of the camera: when zoomed OUTSIDE the dome
  // (maxDistance span×4 vs sphere span×1.5) both roots are positive and the
  // −√ root is the near hit under the cursor; when inside, that root is behind
  // us so we fall through to the +√ (forward) root
  const sq = Math.sqrt(disc); let tHit = -od - sq;
  if (tHit < 1e-6) tHit = -od + sq;
  if (tHit < 1e-6) return -1;                          // whole sphere is behind the camera
  _pkR.multiplyScalar(tHit).add(camera.position).divideScalar(R);
  if (_pkR.y < 0.02) return -1;                        // below the skyline melt: terrain, not sky
  _pkQ.copy(starGroup.quaternion).invert();
  _pkR.applyQuaternion(_pkQ).normalize();              // into the sidereal frame
  const dirs = skyCat.dirs;
  let best = -1, bestD = CON_PICK_RAD;
  skyCat.cons.forEach((c, ci) => {
    if (_pkR.angleTo(c.dir) > c.rad + CON_PICK_RAD) return;
    for (const [i, j] of c.segs) {
      _pkA.set(dirs[i*3], dirs[i*3+1], dirs[i*3+2]);
      _pkB.set(dirs[j*3], dirs[j*3+1], dirs[j*3+2]);
      const dd = arcDist(_pkR, _pkA, _pkB);
      if (dd < bestD) { bestD = dd; best = ci; }
    }
  });
  return best;
}
// desktop hover (throttled ~10 Hz; pointer-locked walk never sends these)
renderer.domElement.addEventListener('pointermove', e => {
  if (SKY_COARSE || walk.on || !skyCat || !starGroup.visible || e.buttons) return;
  const now = performance.now();
  if (now - skySel.lastPick < 100) return;
  skySel.lastPick = now;
  const h = pickConstellation(e.clientX, e.clientY);
  if (h !== skySel.hover) { skySel.hover = h; conRetarget(); }
});
// mobile tap-to-toggle: a touch that barely moved (< 8 px) is a pick, not a
// look-drag; tapping empty sky clears. Works in orbit, flight and walk.
let _skyTap = null;
renderer.domElement.addEventListener('touchstart', e => {
  _skyTap = e.touches.length === 1
    ? { x: e.touches[0].clientX, y: e.touches[0].clientY, t: performance.now() } : null;
}, { passive: true });
renderer.domElement.addEventListener('touchend', e => {
  if (!_skyTap || e.touches.length) return;
  const t = e.changedTouches[0];
  const moved = Math.hypot(t.clientX - _skyTap.x, t.clientY - _skyTap.y);
  const held = performance.now() - _skyTap.t;
  _skyTap = null;
  if (moved > 8 || held > 600 || !skyCat || !starGroup.visible) return;
  const h = pickConstellation(t.clientX, t.clientY);
  if (h < 0) { if (skySel.taps.size) { skySel.taps.clear(); conRetarget(); } return; }
  const on = !skySel.taps.has(h);
  if (skySel.taps.has(h)) skySel.taps.delete(h); else skySel.taps.add(h);
  conRetarget();
  track('constellation_tap', { on });
});
// stargazing walk mode (HKS-84 P2): look up while walking and the figures in
// view light themselves — centroids tested against the camera forward vector
// every ~300 ms, 1–3 at once, with enter/exit hysteresis so nothing flickers
const _saF = new THREE.Vector3(), _saW = new THREE.Vector3(), _saP = new THREE.Vector3();
function updateSkyAuto() {
  if (!skyCat) return;
  if (!(walk.on && starGroup.visible && walk.pitch > 0.35)) {
    if (skySel.auto.size) { skySel.auto.clear(); conRetarget(); }
    return;
  }
  const now = performance.now();
  if (now - skySel.lastAuto < 300) return;
  skySel.lastAuto = now;
  camera.getWorldDirection(_saF);
  const half = camera.fov * 0.5 * D2R;
  const R = starGroup.scale.x || 1;
  const cand = [];
  skyCat.cons.forEach((c, i) => {
    _saW.copy(c.dir).applyQuaternion(starGroup.quaternion);   // sidereal → world (sphere dir)
    if (_saW.y < 0.03) return;                                // set, or melting at the skyline
    // apparent direction from the hiker's eye, not the sphere centre
    _saP.copy(_saW).multiplyScalar(R).sub(camera.position).normalize();
    const ang = _saF.angleTo(_saP);
    const lim = Math.min(half * (skySel.auto.has(i) ? 0.95 : 0.8), c.rad + 0.24);
    if (ang < lim) cand.push([ang, i]);
  });
  cand.sort((a, b) => a[0] - b[0]);
  const next = new Set(cand.slice(0, 3).map(x => x[1]));
  if (next.size !== skySel.auto.size || [...next].some(i => !skySel.auto.has(i)))
    { skySel.auto = next; conRetarget(); }
}
// bilingual name card per lit constellation — the peak-label pattern, aimed at
// the sky: reprojected from the centroid each frame, faded with the starlight
const _clV = new THREE.Vector3();
function updateConstLabels() {
  if (!skyCat) return;
  const fade = starUniforms.uFade.value;
  for (const c of skyCat.cons) {
    const show = starGroup.visible && c.lvl > 0.05 && fade > 0.06;
    if (!show) { if (c.div) c.div.style.display = 'none'; continue; }
    if (!c.div) {
      c.div = document.createElement('div'); c.div.className = 'lbl con';
      document.body.appendChild(c.div);
    }
    if (c.div._loc !== locale) {   // en-hk: English big / 中文 small; zh-hk flips
      c.div.innerHTML = isZh() ? `${c.zh}<small>${c.en}</small>` : `${c.en}<small>${c.zh}</small>`;
      c.div._loc = locale;
    }
    _clV.copy(c.dir).applyMatrix4(starGroup.matrixWorld);
    const horizonY = _clV.y / starGroup.scale.x;               // ≈ unit-sphere height
    _clV.project(camera);
    if (_clV.z > 1 || horizonY < 0.04) { c.div.style.display = 'none'; continue; }
    c.div.style.display = '';
    c.div.style.opacity = (Math.min(1, fade * 1.25) * c.lvl).toFixed(2);
    c.div.style.left = ((_clV.x * 0.5 + 0.5) * innerWidth) + 'px';
    c.div.style.top = ((-_clV.y * 0.5 + 0.5) * innerHeight) + 'px';
  }
}
const _eqM = new THREE.Matrix4(), _eqX = new THREE.Vector3(), _eqY = new THREE.Vector3(), _eqZ = new THREE.Vector3();
function eqAxis(now, ra, dec, out) {
  const p = starPosition(now, HK_LAT, HK_LON, ra, dec);
  const az = compassDeg(p.azimuth) * D2R;
  return out.set(Math.sin(az) * Math.cos(p.altitude), Math.sin(p.altitude), -Math.cos(az) * Math.cos(p.altitude));
}
function updateStars(now) {
  // The stars are always up there — how much they read is decided per frame by
  // stepSky() from the rendered SKY LUMINANCE (bright sky washes them out, dark
  // sky reveals them), so eclipse darkness, Stargaze's black planetarium and the
  // day↔night gradient all reveal stars through one rule, no special cases.
  // This per-sim-minute pass only aims the sphere and the local moon wash.
  // the whole celestial sphere turns as one rigid body: image the equatorial
  // basis through the same hour-angle math the sun/moon use, once a sim-minute
  eqAxis(now, 0, 0, _eqX); eqAxis(now, Math.PI / 2, 0, _eqY); eqAxis(now, 0, Math.PI / 2, _eqZ);
  starGroup.quaternion.setFromRotationMatrix(_eqM.makeBasis(_eqX, _eqY, _eqZ));
  starGroup.scale.setScalar(bounds().span * 1.5);
  starUniforms.uDpr.value = Math.min(devicePixelRatio || 1, 2);
  if (cel.moonAlt > 0) {   // the moon's halo drowns its neighbours first (shader-side)
    starUniforms.uMoonDir.value.set(Math.sin(cel.moonAz) * Math.cos(cel.moonAlt),
      Math.sin(cel.moonAlt), -Math.cos(cel.moonAz) * Math.cos(cel.moonAlt));
    starUniforms.uMoonWash.value = 0.5 * cel.frac * Math.sin(cel.moonAlt);
  } else starUniforms.uMoonWash.value = 0;
}
// shooting stars: one reused trail, rare and quick — blink and you miss it
const METEOR_N = 20;
const meteor = (() => {
  const pos = new Float32Array(METEOR_N * 3), col = new Float32Array(METEOR_N * 3);
  for (let j = 0; j < METEOR_N; j++) {   // white-hot head cooling down the tail
    const w = Math.pow(1 - j / (METEOR_N - 1), 1.6);
    col[j*3] = (0.75 + 0.25 * w) * w; col[j*3+1] = (0.85 + 0.15 * w) * w; col[j*3+2] = w;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const m = new THREE.Line(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true,
    opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  m.visible = false; m.frustumCulled = false; scene.add(m);
  return m;
})();
const met = { t0: 0, dur: 1, next: 0, A: new THREE.Vector3(), B: new THREE.Vector3() };
const _mp = new THREE.Vector3(), _mt = new THREE.Vector3();
function spawnMeteor(tS) {
  const az = Math.random() * Math.PI * 2, alt = (20 + 45 * Math.random()) * D2R;
  met.A.set(Math.sin(az) * Math.cos(alt), Math.sin(alt), -Math.cos(az) * Math.cos(alt));
  _mt.set(Math.random() - 0.5, Math.random() - 0.5, Math.random() - 0.5);
  _mt.addScaledVector(met.A, -_mt.dot(met.A)).normalize();   // tangent to the sky sphere
  if (_mt.y > 0.15) _mt.multiplyScalar(-1);                  // meteors prefer to fall
  met.B.copy(met.A).addScaledVector(_mt, 0.18 + 0.22 * Math.random()).normalize();
  met.t0 = tS; met.dur = 0.7 + 0.6 * Math.random();
  met.next = tS + 20 + Math.random() * 50;
  meteor.visible = true;
}
let celDim = 0;   // HKS-69: eased "overcast over the viewer" 0..1 — dims sun/moon locally
// star wash thresholds on skyLum (linear-space, what THREE actually renders):
// at/below DARK the sky hides nothing (full stars), at/above BRIGHT it washes
// them out completely. Tuned so noon blue (~0.345) and the sunset orange
// (~0.35 — as luminous as noon in linear space) fully wash, stars emerge
// through nautical twilight (sun ~−9° → ~0.08) and reach full by ~−12°
// (~0.01); the deep-night sky (~0.003) / Stargaze black (~0.002) free them all.
const STAR_LUM_DARK = 0.004, STAR_LUM_BRIGHT = 0.10;              // dark theme wash thresholds (linear sky luminance)
// paper's night sky is a lighter slate (never black), so its whole luminance band
// sits higher — shift the thresholds up to match, else stars onset late in twilight
// and never quite reach full at paper night.
const STAR_LUM_DARK_PAPER = 0.012, STAR_LUM_BRIGHT_PAPER = 0.17;
function stepSky() {   // per-frame sky life: star wash, twinkle clock, meteors, moon limb aim
  const tS = performance.now() * 0.001;
  // one cloud probe per frame over the viewer's ground position, shared by the
  // star occlusion and the sun/moon dimming below (each applies its own curve).
  let cover = -1;
  if (cloudFieldActive()) { _cfV.copy(camera.position); world.worldToLocal(_cfV); cover = cloudCoverAt(_cfV.x, _cfV.z); }
  if (cel) {
    // the stars are always there — the sky's own rendered brightness (skyLum,
    // written by renderSky) decides how washed-out they are, every frame. One
    // rule covers day/night, twilight, eclipse darkness and Stargaze's black
    // planetarium. Local effects stack on top: live overcast blots them out
    // (HKS-101 — the cover over the VIEWER decides; Stargaze locks weather off
    // so its sky stays guaranteed-clear) and the moon washes its neighbourhood
    // (uMoonWash, shader-side).
    const paper = bgMode === 'paper';
    const lumDark = paper ? STAR_LUM_DARK_PAPER : STAR_LUM_DARK;
    const lumBright = paper ? STAR_LUM_BRIGHT_PAPER : STAR_LUM_BRIGHT;
    let f0 = 1 - S01((skyLum - lumDark) / (lumBright - lumDark));
    // a bright, high moon washes the whole field a little — the global sky-glow
    // that the local uMoonWash halo (shader-side) can't model.
    if (!stargaze.on && cel.moonAlt > 0) f0 *= 1 - 0.25 * cel.frac * Math.sin(cel.moonAlt);
    starGroup.userData.fade0 = f0;
    let occ = 1;
    if (!stargaze.on && cover >= 0) occ = 1 - 0.94 * Math.min(1, Math.max(0, (cover - 0.12) / 0.55));
    starUniforms.uFade.value = f0 * occ;
    starGroup.visible = starUniforms.uFade.value > 0.005;   // fully washed: skip the draw
    if (starGroup.visible) starUniforms.uTime.value = tS % 4096;
    else conClearAll();                                     // daylight: drop any lit constellations
  }
  // HKS-69: local overcast mutes the sun and moon — the daytime analogue of
  // the star occlusion above, driven by the same probe (cloud cover over the
  // VIEWER's ground position). Over a clear district the sun blazes with its
  // rays; drift under a humid/raining district and disc, rays, glow and the
  // key light all grey down (never to black). Eased so crossing a district
  // boundary never pops, and converging back to full brightness whenever the
  // live field is inactive — manual weather keeps today's global behaviour.
  let cd = 0;
  if (cover >= 0) cd = Math.min(1, Math.max(0, (cover - 0.15) / 0.6));
  celDim += (cd - celDim) * 0.05;
  if (celDim < 0.002) celDim = 0;
  if (cel) {
    sunSpr.material.opacity  = 1 - 0.62 * celDim;
    sunRays.material.opacity = 0.85 * (1 - 0.8 * celDim);
    moonSpr.material.opacity = 1 - 0.55 * celDim;
    const g0 = moonGlow.userData.op0;
    if (g0 != null) moonGlow.material.opacity = g0 * (1 - 0.6 * celDim);
    sun.intensity = baseSun * (1 - 0.4 * celDim);   // key light follows the local sky
  }
  // HKS-84: constellation selection bloom — runs ONLY while a transition is
  // live (~250 ms), touching just the member stars' aSel entries + the small
  // highlight-line buffer. Zero per-frame cost once settled.
  if (skyCat && skySel.anim) {
    let live = false;
    for (const c of skyCat.cons) {
      if (c.lvl === c.tgt) continue;
      c.lvl += (c.tgt - c.lvl) * 0.22;
      if (Math.abs(c.lvl - c.tgt) < 0.02) c.lvl = c.tgt; else live = true;
    }
    const a = skyCat.aSel.array;
    for (const c of skyCat.cons) for (const i of c.idx) a[i] = 0;
    for (const c of skyCat.cons) if (c.lvl > 0)
      for (const i of c.idx) if (c.lvl > a[i]) a[i] = c.lvl;
    skyCat.aSel.needsUpdate = true;
    rebuildSelLines();
    skySel.anim = live;
  }
  if (cel && moonSpr.visible) {   // spin the lit limb toward the real sun (screen space)
    _mp.copy(sunSpr.position).sub(moonSpr.position);
    const e = camera.matrixWorld.elements;
    moonSpr.material.rotation = Math.atan2(
      _mp.x * e[4] + _mp.y * e[5] + _mp.z * e[6],
      _mp.x * e[0] + _mp.y * e[1] + _mp.z * e[2]);
  }
  if (!starGroup.visible || starUniforms.uFade.value < 0.55) { meteor.visible = false; return; }
  if (!meteor.visible) {
    if (!met.next) met.next = tS + 8 + Math.random() * 20;   // first dark sky: a short wait
    if (tS >= met.next) spawnMeteor(tS);
    return;
  }
  const p = (tS - met.t0) / met.dur, R = bounds().span * 1.47;
  if (p > 1.4) { meteor.visible = false; return; }
  const arr = meteor.geometry.attributes.position.array;
  for (let j = 0; j < METEOR_N; j++) {   // trail vertices chase the head down the arc
    const pj = Math.max(0, Math.min(1, p - 0.35 * j / (METEOR_N - 1)));
    _mp.copy(met.A).lerp(met.B, pj).normalize().multiplyScalar(R);
    arr[j*3] = _mp.x; arr[j*3+1] = _mp.y; arr[j*3+2] = _mp.z;
  }
  meteor.geometry.attributes.position.needsUpdate = true;
  meteor.material.opacity = 0.85 * Math.min(1, p * 5) * Math.max(0, 1 - Math.max(0, p - 1) / 0.4);
}

function placeCelestial() {
  if (!cel) return;
  const b = bounds(), R = b.span * 1.35, s = b.span;
  sunSpr.position.set(Math.sin(cel.sunAz) * Math.cos(cel.sunAlt), Math.sin(cel.sunAlt), -Math.cos(cel.sunAz) * Math.cos(cel.sunAlt)).multiplyScalar(R);
  sunRays.position.copy(sunSpr.position);
  moonSpr.position.set(Math.sin(cel.moonAz) * Math.cos(cel.moonAlt), Math.sin(cel.moonAlt), -Math.cos(cel.moonAz) * Math.cos(cel.moonAlt)).multiplyScalar(R);
  moonGlow.position.copy(moonSpr.position);
  sunSpr.scale.set(s * 0.10, s * 0.10, 1); sunRays.scale.set(s * 0.26, s * 0.26, 1);
  moonSpr.scale.set(s * 0.078, s * 0.078, 1);   // a touch larger so it reads as the moon
  sunSpr.visible = sunRays.visible = cel.sunAlt > -4 * D2R;
  moonSpr.visible = moonGlow.visible = cel.moonAlt > -2.5 * D2R;
  const warm = Math.max(0, Math.min(1, 1 - (cel.sunAlt / D2R) / 17));   // golden toward the horizon
  sunSpr.material.color.setHex(0xffffff).lerp(new THREE.Color(0xff8a3d), warm * 0.55);
  sunRays.material.color.setHex(0xfff2da).lerp(new THREE.Color(0xff8a3d), warm * 0.65);
  if (Math.abs(cel.phase - moonTexPhase) > 0.004) {       // redraw the phase only when it moves
    moonTexPhase = cel.phase;
    if (moonSpr.material.map) moonSpr.material.map.dispose();
    moonSpr.material.map = drawMoonTexture(cel.phase, cel.frac);
    moonSpr.material.needsUpdate = true;
  }
  // phase-aware glow: swells + warms toward full, and goes amber near the horizon
  const mWarm = Math.max(0, Math.min(1, 1 - (cel.moonAlt / D2R) / 14));
  const gs = s * (0.10 + 0.09 * cel.frac);
  moonGlow.scale.set(gs, gs, 1);
  moonGlow.material.opacity = moonGlow.userData.op0 = 0.16 + 0.55 * cel.frac;   // op0: pre-dim base (HKS-69)
  moonGlow.material.color.setHex(0xd9e5f4).lerp(new THREE.Color(0xffedc9), Math.min(1, cel.frac * 0.7 + mWarm * 0.45));
  moonSpr.material.color.setHex(0xffffff).lerp(new THREE.Color(0xffc98d), mWarm * 0.35);
}

function updateSkyInfo() {
  const el = document.getElementById('skyinfo'); if (!el) return;
  if (!skySim.on) { el.innerHTML = ''; return; }
  const dstr = skySim.live ? hktDateStr(new Date()) : skySim.date;
  const st = sunTimes(new Date(dstr + 'T12:00:00+08:00'), HK_LAT, HK_LON);
  const mt = moonTimes(new Date(dstr + 'T00:00:00+08:00'), HK_LAT, HK_LON);
  const mi = moonIllumination(simDate());
  const azd = t => t ? Math.round(compassDeg(sunPosition(t, HK_LAT, HK_LON).azimuth)) + '°' : '';
  el.innerHTML = `☀ ↑${hktHHMM(st.sunrise)} ${azd(st.sunrise)} · ↓${hktHHMM(st.sunset)} ${azd(st.sunset)}<br>` +
                 `☾ ↑${hktHHMM(mt.rise)} · ↓${hktHHMM(mt.set)} · ${Math.round(mi.fraction * 100)}%`;
}

// solar-eclipse coverage: what fraction of the SUN's disc area the moon hides,
// as seen from HK. Classic circle–circle intersection on the two apparent radii;
// rMoon varies with the live Earth–Moon distance, so total (rMoon ≥ rSun → 1)
// vs annular (rMoon < rSun → caps at (rMoon/rSun)², a lit ring survives) falls
// out of the geometry. Angles in radians; distance in km.
const SUN_DIST_KM = 149598000, SUN_R_KM = 696000, MOON_R_KM = 1737.4, R_EARTH_KM = 6371;
function eclipseCoverage(sunAlt, sunAz, moonAlt, moonAz, moonDistKm) {
  const rS = Math.asin(SUN_R_KM / SUN_DIST_KM);          // ~0.00465 rad
  // topocentric distance: the observer sits up to ~1 Earth-radius nearer the moon
  // than the geocentre (moonDistKm is geocentric), enlarging the apparent disc —
  // enough to tip a near-boundary total from a false annular to a true total.
  const rho = moonDistKm - R_EARTH_KM * Math.sin(Math.max(0, moonAlt));
  const rM = Math.asin(MOON_R_KM / rho);
  const cosSep = Math.sin(sunAlt) * Math.sin(moonAlt) +
                 Math.cos(sunAlt) * Math.cos(moonAlt) * Math.cos(sunAz - moonAz);
  const sep = Math.acos(Math.max(-1, Math.min(1, cosSep)));   // angular separation
  if (sep >= rS + rM) return 0;                               // discs apart
  if (sep <= Math.abs(rS - rM)) return rM >= rS ? 1 : (rM / rS) ** 2;   // total vs annular cap
  const ac = x => Math.acos(Math.max(-1, Math.min(1, x)));   // clamp: float error at disc contact must not NaN the area
  const A = rS * rS * ac((sep * sep + rS * rS - rM * rM) / (2 * sep * rS)) +
            rM * rM * ac((sep * sep + rM * rM - rS * rS) / (2 * sep * rM)) -
            0.5 * Math.sqrt(Math.max(0, (-sep + rS + rM) * (sep + rS - rM) * (sep - rS + rM) * (sep + rS + rM)));
  return A / (Math.PI * rS * rS);                             // lens area ÷ sun-disc area
}

function updateCelestial() {
  if (!skySim.on) {
    if (cel) {
      cel = null; celKey = '';
      sunSpr.visible = sunRays.visible = moonSpr.visible = moonGlow.visible = false;
      starGroup.visible = false; meteor.visible = false; conClearAll();
      sun.position.set(-1, 2, 1.4); sun.color.setHex(0xffffff);   // legacy fixed light
      renderSky(); setFog(); updateSkyInfo();
    }
    return;
  }
  const now = simDate();
  const key = (skySim.live ? 'L' + Math.floor(now.getTime() / 60000) : 'F' + skySim.date + ':' + skySim.minutes) + (stargaze.on ? 'S' : '');   // include Stargaze in the throttle key — entering/exiting it must recompute the star fade even mid-minute (was: ~30 s black sky when entering live-sky Stargaze by day)
  if (key === celKey) return;
  celKey = key;
  const sp = sunPosition(now, HK_LAT, HK_LON), mp = moonPosition(now, HK_LAT, HK_LON), mi = moonIllumination(now);
  cel = { sunAlt: sp.altitude, sunAz: compassDeg(sp.azimuth) * D2R,
          moonAlt: mp.altitude, moonAz: compassDeg(mp.azimuth) * D2R,
          frac: mi.fraction, phase: mi.phase, moonDist: mp.distance };
  // only meaningful with the sun up — a below-horizon "eclipse" is just night
  cel.eclipse = sp.altitude > 0
    ? eclipseCoverage(cel.sunAlt, cel.sunAz, cel.moonAlt, cel.moonAz, cel.moonDist) : 0;
  placeCelestial();
  updateStars(now);
  if (skySim.live) {   // keep the scrub + date mirroring the live clock
    const tEl = document.getElementById('skytime'), dEl = document.getElementById('skydate');
    if (tEl) { tEl.value = hktMinutes(now); document.getElementById('skytimev').textContent = mmToHHMM(+tEl.value); }
    if (dEl) dEl.value = hktDateStr(now);
  }
  renderSky(); setFog(); updateSkyInfo();
}

// ---- flight mode (HKS-4): fly a little plane over Hong Kong -----------------
// Arcade model: ↑↓ pitch, ←→ bank (banking turns), ⇧/⌃ throttle; stalls sink,
// the wind shoves you, storms rattle the stick, and the DEM heightfield is
// solid — clip a ridge and you bounce off with a jolt. Chase camera; Esc exits.
// HKS-93: view is three-way — 'chase' (external boom), 'eye' (the clean
// first-person pilot's eye, no interior) or 'cockpit' (the flight-deck set)
const flight = { on: false, view: 'chase', pos: new THREE.Vector3(), yaw: 0, pitch: 0, roll: 0,
                 speed: 0, top: 110, keys: {}, prevSpin: 1, helpT: 0, landed: false,
                 tilt: false, tiltRef: null, tiltBeta: 0, tiltGamma: 0,
                 // HKS-53: hold-to-gas + drag-to-look (shared boom offset, both cameras)
                 touchHold: 0, mouseLook: false, lookYaw: 0, lookPitch: 0 };
// lift off from a landing: a short catapult roll into a climb. ␣, a tap on the
// map, or the HUD's take-off button all call this.
function takeOff() {
  if (!flight.on || !flight.landed) return;
  flight.landed = false;
  flight.speed = 55;
  flight.pitch = 0.28;
  track('takeoff');
}
let planeGrp = null;
// ---- plane skins (HKS-93) ---------------------------------------------------
// Each skin is a livery + builder pair. All builders share the flight frame:
// forward = -z, group origin at mid-fuselage, group scale 4, wheels touching
// y = -0.55 (the landed pose parks the origin 2.2 real metres above the deck).
// Adding a skin = one row here + an <option> in #planeskin + its i18n strings.
const PLANE_SKINS = [
  { id: 'prop',  build: buildPropPlane },   // the original red-trim single-prop
  { id: 'betsy', build: buildBetsyDC3 },    // Cathay Pacific "Betsy" — the Douglas DC-3, VR-HDB
  { id: 'cx747', build: buildCX747 },       // Cathay Pacific Boeing 747
  { id: 'cx777', build: buildCX777 },       // Cathay Pacific Boeing 777-300
  { id: 'a330',  build: buildCX777 },       // Cathay Pacific Airbus A330-300 — the 777 widebody twin stands in as loading/offline fallback (the ⚠ NC GLB may be absent on commercial deploys); PLANE_GLBS.a330.fit corrects the length
  { id: 'a350',  build: buildCXA350 },      // Cathay Pacific Airbus A350-1000
];
let planeSkin = 'prop';
function buildPlane() {
  return (PLANE_SKINS.find(k => k.id === planeSkin) || PLANE_SKINS[0]).build();
}
// swap the live model in place — mid-flight the new skin inherits the pose on
// the next stepFlight tick (position/quaternion are re-copied every frame)
function setPlaneSkin(id) {
  if (!PLANE_SKINS.some(k => k.id === id)) id = 'prop';
  if (id === planeSkin) return;
  planeSkin = id;
  if (!planeGrp) return;                    // not built yet — first flight uses the new skin
  const vis = planeGrp.visible;
  clearLookFilter(planeGrp);                // HKS-104: back to real materials first, so the
                                            // dispose below frees THEM (not shared overrides)
  world.remove(planeGrp);
  planeGrp.traverse(o => {                  // free geometry, materials AND their canvas textures
    if (o.geometry) o.geometry.dispose();
    for (const m of Array.isArray(o.material) ? o.material : o.material ? [o.material] : []) {
      if (m.map) m.map.dispose();
      m.dispose();
    }
  });
  planeGrp = buildPlane();
  planeGrp.visible = vis;
  planeGrp.position.copy(flight.pos);
  world.add(planeGrp);
  applyLookFilter(planeGrp);                // HKS-104: the fresh skin inherits the active reality
  // HKS-93: a skin without a flight deck can't hold cockpit view — fall back to
  // the clean eye; the 🧑‍✈️ segment shows/hides with the new skin either way
  if (flight.view === 'cockpit' && !planeGrp.userData.cockpit) flight.view = 'eye';
  syncCamSeg();
  loadPlaneModel(id);          // HKS-110: swap in the real airframe once it arrives
}
document.getElementById('planeskin').addEventListener('change', e => { setPlaneSkin(e.target.value); if (e.isTrusted) track('plane_skin', { skin: e.target.value }); });
// ---- real GLB airframes (HKS-110) -------------------------------------------
// Some skins upgrade from the procedural primitives to a real open-source 3D
// model, lazily fetched from the data/ origin (ASSET_BASE-aware) and precached
// by the service worker — same pattern as the walk-mode hiker. The procedural
// builder stays as the loading stand-in and the offline / load-failure fallback.
// Provenance + licences: data/models/README.md (CC-BY 3.0/4.0 + two nc/-fenced
// BY-NC-SA hulls — LICENSE-ASSETS.md; all credited in the Credits drawer).
// Every skin has a real airframe; the procedural builders remain as the
// loading stand-ins and the offline / missing-nc-file fallbacks.
//
// Each model is normalised to the procedural airframe it replaces: nose -Z
// (rotY flips exporters that face +Z), fuselage length fitted to the builder's
// real-world size, belly/wheels dropped to the same waterline. The nav-light
// spheres (tagged userData.navlight) and the painted flight-deck interior
// (userData.cockpit) are kept in place, so stepFlight strobes/beacons and the
// cockpit camera keep working unchanged.
const PLANE_GLBS = {
  prop:  { url: 'data/models/plane-prop.glb' },                          // “Small Airplane”, Vojtěch Balák
  cx747: { url: 'data/models/plane-747.glb' },                           // “Boeing 747-100”, Marine (nose -Z; our CX repaint baked in)
  cx777: { url: 'data/models/plane-777.glb', rotY: Math.PI },            // “Boeing 777-300er.”, 777_Boeing (tail at -Z; vertex-colour CX livery baked in)
  a350:  { url: 'data/models/plane-a350.glb', rotY: Math.PI / 2 },       // “A350 V3 with animation”, Newbie99999993 (nose at +X; our CX livery + CXGear split baked in)
  // ⚠ NC (CC BY-NC-SA 4.0, OUTPISTON) — fenced under nc/ per LICENSE-ASSETS.md;
  // commercial deploys delete nc/ and the 404 lands on the procedural fallback.
  // fit: A330-300 (63.7 m) drawn against the 777-300 reference builder (73.9 m).
  // gearProc: the source model has NO extended landing gear (lowest geometry is
  // the engine cowls), so the loader lifts it to a gear stance and adds simple
  // procedural gear — see the gearProc block in loadPlaneModel().
  a330:  { url: 'data/models/nc/plane-a330.glb', rotY: Math.PI, fit: 63.69 / 73.86, gearProc: true },
  // ⚠ NC (CC BY-NC-SA 4.0, OUTPISTON) — nc/-fenced like the a330. Bare-metal
  // 1946 VR-HDB livery baked in (Union Jack fin, era titles). fixedGear: a
  // taildragger's semi-fixed gear stays visible in flight (fleet-rule exception).
  betsy: { url: 'data/models/nc/plane-betsy.glb', rotY: Math.PI, fixedGear: true },
};
const planeModelSt = {};   // id → { inflight, fails, warned } — cap retries like the hiker loader
function disposePlaneGltf(scene) {
  scene.traverse(o => {
    if (!o.isMesh) return;
    o.geometry?.dispose();
    for (const m of Array.isArray(o.material) ? o.material : o.material ? [o.material] : []) {
      if (m.map) m.map.dispose();
      m.dispose();
    }
  });
}
function loadPlaneModel(id) {
  const cfg = PLANE_GLBS[id];
  if (!cfg) return;                                    // procedural-only skin
  const st = planeModelSt[id] || (planeModelSt[id] = { inflight: false, fails: 0, warned: false });
  if (st.inflight || st.fails >= 2) return;            // in flight, or gave up (offline / bad file)
  if (planeGrp && planeGrp.userData.glbSkin === id) return;   // already wearing the real airframe
  st.inflight = true;
  new GLTFLoader().load(asset(cfg.url), gltf => {
    st.inflight = false;
    // group gone / skin swapped away mid-fetch / already swapped — try again when reselected
    if (!planeGrp || planeSkin !== id || planeGrp.userData.glbSkin === id) { disposePlaneGltf(gltf.scene); return; }
    const model = gltf.scene;
    let meshCount = 0;
    model.traverse(o => { if (o.isMesh) meshCount++; });
    if (!meshCount) {                                  // a broken re-export must not replace a working plane
      console.warn('[plane] GLB carries no meshes — keeping the procedural airframe:', cfg.url);
      st.fails = 2;
      disposePlaneGltf(model);
      return;
    }
    // fit target: measure a throwaway procedural build (identity pose — the live
    // group may be mid-flight with position/rotation applied), in pre-scale units
    const ref = (PLANE_SKINS.find(k => k.id === id) || PLANE_SKINS[0]).build();
    ref.updateMatrixWorld(true);
    const rbox = new THREE.Box3().setFromObject(ref);
    const rs = ref.scale.x || 1;
    clearLookFilter(ref);
    ref.traverse(o => {
      if (o.geometry) o.geometry.dispose();
      for (const m of Array.isArray(o.material) ? o.material : o.material ? [o.material] : []) {
        if (m.map) m.map.dispose();
        m.dispose();
      }
    });
    const len = (rbox.max.z - rbox.min.z) / rs, floorY = rbox.min.y / rs,
          midZ = (rbox.max.z + rbox.min.z) / 2 / rs;
    // normalise: nose -Z, procedural length, belly on the same waterline
    const inner = new THREE.Group();
    inner.rotation.y = cfg.rotY || 0;
    inner.add(model);
    inner.updateMatrixWorld(true);
    const mbox = new THREE.Box3().setFromObject(inner);
    const k = (cfg.fit || 1) * len / Math.max(0.01, mbox.max.z - mbox.min.z);   // cfg.fit: real-world length vs the reference builder's type (a330 borrows the 777 builder)
    inner.scale.setScalar(k);
    inner.position.set(
      -k * (mbox.max.x + mbox.min.x) / 2,
      floorY - k * mbox.min.y,
      midZ - k * (mbox.max.z + mbox.min.z) / 2);
    // HKS-110: airframes with no authored landing gear (cfg.gearProc — the
    // outpiston A330's lowest geometry is its engine cowls) would otherwise be
    // parked on their engines by the waterline fit and read as floating.
    // Lift the airframe to a real gear stance and add simple procedural gear
    // — nose strut + two main bogies, dark grey — with the wheels reaching the
    // procedural builder's wheel line (floorY), proportions from the real
    // A330-300 (engine clearance ~1 m, main track 10.7 m vs 63.7 m length).
    let procGear = null;
    if (cfg.gearProc) {
      const Lz = k * (mbox.max.z - mbox.min.z);        // final fuselage length
      inner.position.y += 0.016 * Lz;                  // engine-bottom ground clearance
      const dark = new THREE.MeshStandardMaterial({ color: 0x2b2e33, roughness: 0.8 });
      procGear = new THREE.Group();
      const wheelR = 0.013 * Lz;
      const gearAt = (x, z) => {
        const legH = 0.016 * Lz + 0.05 * Lz;           // wheel line up into the belly
        const leg = new THREE.Mesh(new THREE.BoxGeometry(wheelR * 0.6, legH, wheelR * 0.6), dark);
        leg.position.set(x, floorY + wheelR * 0.7 + legH / 2, z);
        procGear.add(leg);
        const wheel = new THREE.Mesh(new THREE.CylinderGeometry(wheelR, wheelR, wheelR * 1.5, 12), dark);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(x, floorY + wheelR, z);
        procGear.add(wheel);
      };
      gearAt(0, midZ - 0.38 * Lz);                     // nose strut
      gearAt(-0.084 * Lz, midZ + 0.045 * Lz);          // main bogies
      gearAt(0.084 * Lz, midZ + 0.045 * Lz);
    }
    // (liveries are baked into the GLBs by their trim scripts — no runtime tint)
    const spinners = [];                               // wire any authored propeller into the shared spin
    model.traverse(o => {                              // outermost matches only — spinning parent AND child would compound
      if (/_(slow|blurred)/i.test(o.name)) { o.visible = false; return; }   // some exports ship still/slow/blurred variants — keep only the still blades
      if (/prop|rotor|spinner/i.test(o.name) && !spinners.some(s => {
        for (let a = o.parent; a; a = a.parent) if (a === s) return true;
        return false;
      })) spinners.push(o);
    });
    // Re-pivot every spinner about ITS OWN hub: many exports bake prop geometry in
    // model space with every node origin at the aircraft centre, so rotating the node
    // spins the prop around the fuselage — on a twin like the DC-3 both props sweep
    // as one. Wrap each in a pivot Group at its bbox centre, as a child of `inner`
    // (inner-local Z is the fuselage/thrust axis, so the shared stepFlight
    // `rotation.z += spin` turns each prop in place on its own nacelle). Done while
    // the subtree is still detached — coordinates are mapped into inner-local space,
    // never through planeGrp, which may be mid-flight.
    if (spinners.length) {
      inner.updateMatrixWorld(true);
      const toInner = new THREE.Matrix4().copy(inner.matrixWorld).invert();
      for (let i = 0; i < spinners.length; i++) {
        const o = spinners[i];
        const c = new THREE.Box3().setFromObject(o).getCenter(new THREE.Vector3()).applyMatrix4(toInner);
        const pivot = new THREE.Group();
        pivot.position.copy(c);
        inner.add(pivot);
        pivot.attach(o);                               // keeps the blade's placement, re-homes its origin to the hub
        spinners[i] = pivot;
      }
    }
    // swap: dress down, replace the hull wholesale — keep nav lights + cockpit
    clearLookFilter(planeGrp);
    for (const c of [...planeGrp.children]) {
      if (c.userData.navlight || c === planeGrp.userData.cockpit) continue;
      planeGrp.remove(c);
      c.traverse(o => {
        if (o.geometry) o.geometry.dispose();
        for (const m of Array.isArray(o.material) ? o.material : o.material ? [o.material] : []) {
          if (m.map) m.map.dispose();
          m.dispose();
        }
      });
    }
    delete planeGrp.userData.prop;                     // the procedural blades are gone
    delete planeGrp.userData.props;
    delete planeGrp.userData.gear;                     // …and the procedural gear group
    if (spinners.length) planeGrp.userData.props = spinners;
    // HKS-110 fleet rule: tag the airframe's landing gear so stepFlight can
    // drop/retract it with the landed state — matched by node name or by the
    // CXGear material the trim scripts split gear geometry into.
    if (!cfg.fixedGear) {                              // taildraggers keep their gear out (betsy)
      const gear = [];
      model.traverse(o => {
        if (!o.isMesh) return;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        if (/gear|wheel|tyre|tire|bogie|undercarriage/i.test(o.name) ||
            mats.some(m => m && /^CXGear/.test(m.name || ''))) gear.push(o);
      });
      if (gear.length) planeGrp.userData.gear = gear;
    }
    if (procGear) {                                    // gearProc airframes: the loader-built gear group
      planeGrp.add(procGear);                          // (visible parked; stepFlight hides it airborne)
      planeGrp.userData.gear = procGear;
    }
    planeGrp.add(inner);
    planeGrp.userData.glbSkin = id;
    applyLookFilter(planeGrp);                         // re-dress the new hull for Matrix/Neon
  }, undefined, err => {                               // offline / 404 (e.g. GLB not yet on R2): keep the procedural build
    st.inflight = false;
    st.fails++;
    if (!st.warned) {
      console.warn('[plane] model load failed — using the procedural airframe:', asset(cfg.url), (err && err.message) || err);
      st.warned = true;
    }
  });
}
// a swept, tapered wing as one symmetric extrusion laid flat: shape x = span
// (± out to the tips), shape y = fore-aft (+aft); `sweep` is how far aft the
// tip leading edge sits. After rotateX the top skin lies at y = 0.
function wingGeo(span, rootChord, tipChord, sweep, th, half) {
  const s = new THREE.Shape();
  s.moveTo(0, 0);
  s.lineTo(span, sweep); s.lineTo(span, sweep + tipChord);
  s.lineTo(0, rootChord);
  if (!half) { s.lineTo(-span, sweep + tipChord); s.lineTo(-span, sweep); }   // symmetric one-piece wing
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: th, bevelEnabled: false });
  g.rotateX(Math.PI / 2);
  return g;
}
// a fin / brush-stroke profile stood upright in the zy plane: pts are
// [fore-aft (+aft), up] outline pairs, extruded `th` across the fuselage.
function finGeo(pts, th) {
  const s = new THREE.Shape();
  s.moveTo(pts[0][0], pts[0][1]);
  for (let i = 1; i < pts.length; i++) s.lineTo(pts[i][0], pts[i][1]);
  s.closePath();
  const g = new THREE.ExtrudeGeometry(s, { depth: th, bevelEnabled: false });
  g.rotateY(-Math.PI / 2);                  // shape +x → +z (aft), thickness across x
  g.translate(th / 2, 0, 0);                // centre on the fuselage line
  return g;
}
// navigation + anti-collision lights (HKS-93), shared by every skin: steady
// position lights — RED port wingtip / GREEN starboard / WHITE tail — plus
// white wingtip+tail strobes (double-flash) and red beacons above and below
// the fuselage. Unlit MeshBasic markers so they glow at night and in rain;
// stepFlight drives the flashing (strobes airborne only, like real ops).
function addNavLights(grp, spec) {
  const mk = (p, color, r, hidden) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(r, 8, 6),
      new THREE.MeshBasicMaterial({ color }));
    m.userData.navlight = true;              // HKS-110: survives the GLB airframe swap
    m.position.set(p[0], p[1], p[2]);
    if (hidden) m.visible = false;          // flashers start dark until stepFlight ticks
    grp.add(m);
    return m;
  };
  const L = { strobes: [], beacons: [] };
  mk(spec.wingL, 0xff2418, 0.045);          // port = red, starboard = green — never swapped
  mk(spec.wingR, 0x1fe04c, 0.045);
  mk(spec.tail, 0xffffff, 0.04);
  for (const p of [spec.wingL, spec.wingR, spec.tail])
    L.strobes.push(mk([p[0], p[1] + 0.06, p[2]], 0xffffff, 0.055, true));
  L.beacons.push(mk(spec.top, 0xff2222, 0.05, true));
  L.beacons.push(mk(spec.bot, 0xff2222, 0.05, true));
  grp.userData.lights = L;
}
// ---- runtime canvas textures (HKS-93) ---------------------------------------
// All livery and cockpit detail below is PAINTED at runtime onto canvases and
// wrapped as CanvasTextures — no build step, no new deps, disposed on skin
// swap. The art is original, drawn from study of reference photography
// (Wikimedia Commons: CX 747-467 B-HUJ & B-HOW exteriors, B-HKU tail close-up,
// a Cathay 747 flight deck, Cessna 170 N2670V for the prop plane, the
// preserved DC-3 VR-HDB "Betsy" at the HK Science Museum for the Betsy skin,
// and CX A350-1000 B-LXA at HKG for the A350). The one
// photographic asset is the 747 POV panel/glareshield photo (CC BY 2.0, see
// DECK_PHOTO_URL below) — properly licensed and credited in the Credits drawer.
//
// Cylindrical unwrap convention (all hull barrels are cylinders laid along -z
// with thetaStart 0): canvas x = around the hull — 0 crown, ¼W starboard
// waterline, ½W belly, ¾W port; canvas y = along the hull, top = nose.
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
// registrations/titles run along the hull = the canvas y axis in the unwrap,
// so text is drawn turned: -90° reads correctly on the starboard side, +90°
// on the port side (glyph tops toward the crown in both cases)
function hullText(ctx, str, x, y, rot, font, color, spacing) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.font = font; ctx.fillStyle = color;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (spacing !== undefined && 'letterSpacing' in ctx) ctx.letterSpacing = spacing;
  ctx.fillText(str, 0, 0);
  ctx.restore();
}
// a subtle riveted-panel tile for wing/tailplane skins (both aircraft)
function wingTileTex(rep) {
  const t = canvasTex(128, 128, (ctx, w, h) => {
    ctx.fillStyle = '#e9edf1'; ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(55,65,78,0.10)'; ctx.lineWidth = 1;
    for (let y = 10; y < h; y += 26) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
    for (let x = 16; x < w; x += 43) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
    ctx.fillStyle = 'rgba(50,60,72,0.08)';
    for (let y = 10; y < h; y += 26)
      for (let x = 4; x < w; x += 13) ctx.fillRect(x, y - 3, 1.5, 1.5);
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(rep, rep);
  return t;
}
// ---- Cathay Pacific brushwing palette (sampled by eye from the references) --
const CX_JADE = '#00655b', CX_RED = '#e8384a', CX_CROWN = '#f4f6f8',
      CX_BAND = '#ccd6dd', CX_BELLY = '#b2bbc2', CX_WIN = '#161d24';
// shared world-height (plane-local metres) colour stops so the white crown /
// grey-blue band / grey belly flow unbroken across barrel, nose and tail cone
const cxHull = yw => yw > 0.135 ? CX_CROWN : yw > -0.115 ? CX_BAND : CX_BELLY;
// the jade nose swoosh + red pinstripe are world slabs too (top just under the
// window line at y≈0.09) so the painted nose meets the painted barrel exactly
const CX_SW = { jadeTop: 0.075, jadeBot: -0.06, redTop: -0.068, redBot: -0.095 };

// main-deck barrel: bands, window rows, doors, titles, the aft half of the
// nose swoosh tapering out, panel lines and a tiny B-HKS registration
function drawCxBarrel(ctx, w, h) {
  for (let x = 0; x < w; x++) {                        // base bands per column
    const a = Math.min(x, w - x) / w * 2 * Math.PI;    // angle from the crown
    ctx.fillStyle = cxHull(0.3 * Math.cos(a));
    ctx.fillRect(x, 0, 1, h);
  }
  const X = a => a / 360 * w;                          // degrees-from-crown → px
  // nose swoosh run-out: jade wedge + red pinstripe, both sides, tapering aft
  for (const m of [0, 1]) {                            // 0 = starboard, 1 = port
    const px = x => m ? w - x : x;
    ctx.fillStyle = CX_JADE;
    ctx.beginPath();
    ctx.moveTo(px(X(75.6)), 0);
    ctx.quadraticCurveTo(px(X(78)), 150, px(X(85)), 252);
    ctx.quadraticCurveTo(px(X(93)), 170, px(X(96.5)), 0);
    ctx.closePath(); ctx.fill();
    ctx.strokeStyle = CX_RED; ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.moveTo(px(X(103.2)), 0);
    ctx.quadraticCurveTo(px(X(99)), 170, px(X(87)), 258);
    ctx.stroke();
  }
  // faint frame/panel lines before windows so they read as under-surface
  ctx.strokeStyle = 'rgba(20,30,40,0.05)'; ctx.lineWidth = 1;
  for (let y = 85; y < h; y += 85) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
  ctx.strokeStyle = 'rgba(255,255,255,0.10)';
  for (const x of [X(30), w - X(30)]) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke(); }
  // doors: outlined at the window line, windows skip around them
  const doors = [150, 436, 737, 935];
  ctx.strokeStyle = 'rgba(90,100,110,0.55)'; ctx.lineWidth = 1.5;
  for (const wx of [X(72.5), w - X(72.5)])
    for (const dy of doors) { ctx.strokeRect(wx - 15, dy - 13, 30, 26); ctx.fillStyle = CX_WIN; ctx.fillRect(wx - 5, dy - 3, 8, 6); }
  // the two window rows (canvas-x span = window height on the hull)
  ctx.fillStyle = CX_WIN;
  for (const wx of [X(72.5), w - X(72.5)])
    for (let y = 120; y < 940; y += 14) {
      if (doors.some(d => Math.abs(y - d) < 22)) continue;
      ctx.fillRect(wx - 5, y, 10, 7);
    }
  // titles on the white crown, aft of the hump, reading correctly per side
  const font = 'bold 28px "Helvetica Neue", Arial, sans-serif';
  hullText(ctx, 'CATHAY PACIFIC', X(45), 615, -Math.PI / 2, font, CX_JADE, '4px');
  hullText(ctx, 'CATHAY PACIFIC', w - X(45), 615, Math.PI / 2, font, CX_JADE, '4px');
  // tiny registration near the tail
  const rfont = 'bold 13px Arial, sans-serif';
  hullText(ctx, 'B-HKS', X(38), 975, -Math.PI / 2, rfont, '#5c666e');
  hullText(ctx, 'B-HKS', w - X(38), 975, Math.PI / 2, rfont, '#5c666e');
}
// nose: per-pixel bands + swoosh wrapping the front above the radome, then the
// four-pane windscreen. The sphere is re-oriented pole-forward, so u wraps the
// hull (crown at ¼W) and v runs tip (row 0) → barrel joint (row h/2).
// mode '747' paints the 90s jade nose swoosh + red pinstripe; mode '777'
// (modern livery) runs the slim jade window-line cheatline through instead;
// mode 'a350' is the clean modern hull plus Airbus's black cockpit "mask" —
// the curved dark surround swallowing the windscreen (panes seamed inside it).
function drawCxNose(ctx, w, h, mode = '747') {
  const img = ctx.createImageData(w, h), px = img.data;
  const C = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
  const crown = C(CX_CROWN), band = C(CX_BAND), belly = C(CX_BELLY), jade = C(CX_JADE), red = C(CX_RED);
  for (let y = 0; y < h; y++) {
    const th = Math.PI * (y + 0.5) / h, sinT = Math.sin(th);
    const zw = -1.6 - 0.54 * Math.cos(th);             // world z of this ring
    for (let x = 0; x < w; x++) {
      const a = ((x + 0.5) / w - 0.25) * 2 * Math.PI;  // 0 at crown
      const yw = 0.3 * Math.cos(a) * sinT;             // world height
      let c = yw > 0.135 ? crown : yw > -0.115 ? band : belly;
      if (mode === '747') {
        if (zw > -2.04 && yw < CX_SW.jadeTop && yw > CX_SW.jadeBot) c = jade;
        else if (zw > -2.05 && yw < CX_SW.redTop && yw > CX_SW.redBot) c = red;
      } else if (mode === '777' && zw > -2.02 && yw < 0.108 && yw > 0.070) c = jade;   // 777 cheatline runs to the radome
      const i = (y * w + x) * 4;
      px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; px[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  // radome seam arc
  ctx.strokeStyle = 'rgba(30,40,50,0.10)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(w * 0.10, 46); ctx.quadraticCurveTo(w * 0.25, 40, w * 0.40, 46); ctx.stroke();
  // the A350 mask: one black curved blob around the whole windscreen band, its
  // outer corners sweeping up-and-aft like the real "sunglasses" — painted
  // UNDER the panes so their seams read as glass inside the mask
  if (mode === 'a350') {
    const mx = w * 0.25;
    ctx.fillStyle = '#14181d';
    ctx.beginPath();
    ctx.moveTo(mx - w * 0.125, 108);                    // lower-forward corner, port
    ctx.quadraticCurveTo(mx, 122, mx + w * 0.125, 108); // curved chin under the panes
    ctx.quadraticCurveTo(mx + w * 0.145, 92, mx + w * 0.115, 68);  // aft corner curls up
    ctx.quadraticCurveTo(mx, 56, mx - w * 0.115, 68);   // brow over the panes
    ctx.quadraticCurveTo(mx - w * 0.145, 92, mx - w * 0.125, 108);
    ctx.closePath(); ctx.fill();
  }
  // windscreen: four panes around the crown (x = w/4), raked outer panes
  ctx.fillStyle = mode === 'a350' ? '#232b33' : CX_WIN;
  const cy0 = 77, cy1 = 97, cx = w * 0.25;
  const pane = (x0, x1, slant) => {
    ctx.beginPath();
    ctx.moveTo(x0, cy0 + slant); ctx.lineTo(x1, cy0);
    ctx.lineTo(x1, cy1); ctx.lineTo(x0, cy1 + slant * 0.6);
    ctx.closePath(); ctx.fill();
  };
  pane(cx - 56, cx - 32, 7); pane(cx - 27, cx - 3, 0);
  ctx.save(); ctx.translate(2 * cx, 0); ctx.scale(-1, 1);   // mirror the pair
  pane(cx - 56, cx - 32, 7); pane(cx - 27, cx - 3, 0);
  ctx.restore();
}
// upper-deck skin for the faired hump lathe (unwrap: canvas x = around the
// deck — 0 crown, ~0.17·W starboard flank, ~0.83·W port; canvas y = along it,
// BOTTOM = aft blend, top = front tip behind the cockpit). White crown skin,
// faint frame rings, and the short upper-deck window row on each flank of the
// level mid-section only — the tapered ends stay clean where they sink into
// the fuselage crown.
function drawCxHump(ctx, w, h) {
  ctx.fillStyle = CX_CROWN; ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = 'rgba(20,30,40,0.05)'; ctx.lineWidth = 1;
  for (let y = 30; y < h; y += 42) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
  ctx.fillStyle = CX_WIN;
  for (let v = 0.46; v <= 0.70; v += 0.028) {          // the level run of the deck
    const y = (1 - v) * h - 3;
    ctx.fillRect(0.168 * w - 3, y, 6, 6);              // starboard row, just off the crest
    ctx.fillRect(0.832 * w - 3, y, 6, 6);              // port row
  }
}
// tail cone: bands follow the shrinking radius, windows curve with them
function drawCxTail(ctx, w, h) {
  const img = ctx.createImageData(w, h), px = img.data;
  const C = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
  const cols = { [CX_CROWN]: C(CX_CROWN), [CX_BAND]: C(CX_BAND), [CX_BELLY]: C(CX_BELLY) };
  for (let y = 0; y < h; y++) {
    const v = 1 - (y + 0.5) / h, r = 0.05 + 0.25 * v;
    for (let x = 0; x < w; x++) {
      const a = Math.min(x, w - x) / w * 2 * Math.PI;
      const c = cols[cxHull(r * Math.cos(a))];
      const i = (y * w + x) * 4;
      px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; px[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  ctx.fillStyle = CX_WIN;                              // last few cabin windows
  for (let v = 0.93; v > 0.5; v -= 0.06) {
    const r = 0.05 + 0.25 * v;
    if (0.09 / r > 0.95) continue;
    const x = Math.acos(0.09 / r) / (2 * Math.PI) * w, y = (1 - v) * h;
    ctx.fillRect(x - 2, y, 4, 6); ctx.fillRect(w - x - 2, y, 4, 6);
  }
  ctx.fillStyle = '#5a6066'; ctx.fillRect(0, h - 8, w, 8);   // APU exhaust ring
}
// fin side: jade field, white cap, red base stripe, and the white brushstroke
// with bristle streaks (the "brushwing"). mirror=true flips the art for the
// starboard face so the stroke sweeps up-and-aft on both sides. red=false
// paints the modern (post-2015) variant: deeper jade field, no red stripe.
function drawCxFin(ctx, w, h, mirror, red = true) {
  if (mirror) { ctx.translate(w, 0); ctx.scale(-1, 1); }
  const Y = up => (1.05 - up) / 1.05 * h;              // fin-up metres → canvas y
  ctx.fillStyle = '#f2f5f6'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = CX_JADE;                             // jade field over the stripe
  ctx.beginPath();
  ctx.moveTo(0, Y(0.90)); ctx.lineTo(w, Y(0.90));
  if (red) { ctx.lineTo(w, Y(0.19)); ctx.lineTo(0, Y(0.13)); }
  else { ctx.lineTo(w, Y(0.06)); ctx.lineTo(0, Y(0.02)); }
  ctx.closePath(); ctx.fill();
  if (red) {
    ctx.fillStyle = CX_RED;                            // red stripe rising aft
    ctx.beginPath();
    ctx.moveTo(0, Y(0.115)); ctx.lineTo(w, Y(0.175));
    ctx.lineTo(w, Y(0.13)); ctx.lineTo(0, Y(0.07));
    ctx.closePath(); ctx.fill();
  }
  // brushstroke: thick body sweeping down-forward from the cap...
  ctx.strokeStyle = '#f2f5f6'; ctx.lineCap = 'round'; ctx.lineWidth = 30;
  ctx.beginPath();
  ctx.moveTo(w * 0.87, Y(0.92));
  ctx.quadraticCurveTo(w * 0.78, Y(0.55), w * 0.66, Y(0.42));
  ctx.stroke();
  ctx.fillStyle = '#f2f5f6';                           // ...ending in the forward hook
  ctx.beginPath();
  ctx.moveTo(w * 0.72, Y(0.52));
  ctx.quadraticCurveTo(w * 0.58, Y(0.30), w * 0.38, Y(0.31));
  ctx.quadraticCurveTo(w * 0.58, Y(0.40), w * 0.645, Y(0.58));
  ctx.closePath(); ctx.fill();
  // bristle streaks fanning off the top of the stroke
  for (let i = 0; i < 8; i++) {
    ctx.strokeStyle = `rgba(242,245,246,${0.35 + 0.07 * i})`;
    ctx.lineWidth = 1.6 + (i % 3);
    ctx.beginPath();
    ctx.moveTo(w * (0.90 - i * 0.022), Y(0.99 - i * 0.012));
    ctx.quadraticCurveTo(w * (0.86 - i * 0.022), Y(0.80), w * (0.80 - i * 0.020), Y(0.62 - i * 0.01));
    ctx.stroke();
  }
  // a couple of jade gaps inside the stroke so it reads as brush hair
  ctx.strokeStyle = 'rgba(0,101,91,0.55)'; ctx.lineWidth = 2;
  for (const o of [-4, 5]) {
    ctx.beginPath();
    ctx.moveTo(w * 0.87 + o, Y(0.90));
    ctx.quadraticCurveTo(w * 0.78 + o, Y(0.56), w * 0.68 + o, Y(0.44));
    ctx.stroke();
  }
}
// 777 main-deck barrel (modern livery, per the CX 777-300 press reference):
// white/grey bands, a slim jade cheatline hugging the single long window row,
// big jade titles FORWARD (no hump in the way), doors, and the registration.
function drawCx777Barrel(ctx, w, h) {
  for (let x = 0; x < w; x++) {                        // base bands per column
    const a = Math.min(x, w - x) / w * 2 * Math.PI;    // angle from the crown
    ctx.fillStyle = cxHull(0.28 * Math.cos(a));
    ctx.fillRect(x, 0, 1, h);
  }
  const X = a => a / 360 * w;                          // degrees-from-crown → px
  // faint frame/panel lines under everything
  ctx.strokeStyle = 'rgba(20,30,40,0.05)'; ctx.lineWidth = 1;
  for (let y = 75; y < h; y += 75) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
  // the slim jade cheatline along the window line, both sides, full length
  ctx.fillStyle = CX_JADE;
  ctx.fillRect(X(68.5), 0, X(8), h);
  ctx.fillRect(w - X(76.5), 0, X(8), h);
  // doors: outlined at the window line, windows skip around them
  const doors = [120, 350, 590, 830, 975];
  ctx.strokeStyle = 'rgba(90,100,110,0.55)'; ctx.lineWidth = 1.5;
  for (const wx of [X(72.5), w - X(72.5)])
    for (const dy of doors) { ctx.strokeRect(wx - 14, dy - 12, 28, 24); ctx.fillStyle = CX_WIN; ctx.fillRect(wx - 4, dy - 3, 8, 6); }
  // one LONG continuous window row — the humpless single deck
  ctx.fillStyle = CX_WIN;
  for (const wx of [X(72.5), w - X(72.5)])
    for (let y = 60; y < 1000; y += 12) {
      if (doors.some(d => Math.abs(y - d) < 20)) continue;
      ctx.fillRect(wx - 4, y, 8, 6);
    }
  // big jade titles on the FORWARD crown (the 777 signature placement)
  const font = 'bold 30px "Helvetica Neue", Arial, sans-serif';
  hullText(ctx, 'CATHAY PACIFIC', X(42), 268, -Math.PI / 2, font, CX_JADE, '4px');
  hullText(ctx, 'CATHAY PACIFIC', w - X(42), 268, Math.PI / 2, font, CX_JADE, '4px');
  // registration near the tail
  const rfont = 'bold 13px Arial, sans-serif';
  hullText(ctx, 'B-HKT', X(38), 985, -Math.PI / 2, rfont, '#5c666e');
  hullText(ctx, 'B-HKT', w - X(38), 985, Math.PI / 2, rfont, '#5c666e');
}
// a big turbofan face for the 777 nacelles: dark intake, a ring of swept fan
// blades and the grey spinner with its white swirl
function drawCxFan(ctx, w, h) {
  const cx = w / 2, cy = h / 2, r = w / 2;
  ctx.fillStyle = '#0d1114'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.fill();
  ctx.strokeStyle = '#2c343b'; ctx.lineWidth = 3;      // swept blades
  for (let i = 0; i < 22; i++) {
    const a = i / 22 * 2 * Math.PI;
    ctx.beginPath();
    ctx.moveTo(cx + 11 * Math.cos(a), cy + 11 * Math.sin(a));
    ctx.quadraticCurveTo(cx + r * 0.6 * Math.cos(a + 0.22), cy + r * 0.6 * Math.sin(a + 0.22),
                         cx + (r - 4) * Math.cos(a + 0.38), cy + (r - 4) * Math.sin(a + 0.38));
    ctx.stroke();
  }
  ctx.strokeStyle = 'rgba(160,170,178,0.5)'; ctx.lineWidth = 2;   // rub-strip ring
  ctx.beginPath(); ctx.arc(cx, cy, r - 3, 0, 7); ctx.stroke();
  ctx.fillStyle = '#8f979e'; ctx.beginPath(); ctx.arc(cx, cy, 11, 0, 7); ctx.fill();   // spinner
  ctx.strokeStyle = '#f2f5f7'; ctx.lineWidth = 3;      // the swirl
  ctx.beginPath(); ctx.moveTo(cx, cy);
  ctx.quadraticCurveTo(cx + 8, cy - 4, cx + 4, cy + 8); ctx.stroke();
}
// ---- photoreal flight deck (HKS-93) -----------------------------------------
// The 747 panel + glareshield are textured from a real 747-400 flight-deck
// photograph: "G-bnlp (45518246055).jpg" by Jeroen Stroes Aviation Photography
// (flickr.com/photos/jeroenstroesphotography/45518246055), a British Airways
// 747-436 — via Wikimedia Commons, licensed CC BY 2.0 (attribution in the
// Credits drawer). The JPEG is cropped into the panel canvases at build time;
// the painted art below fills in until it arrives, then the photo repaints
// over it with the lit PFD/ND/EICAS art composited into its dark CRTs so the
// instruments still glow (and stay readable at night).
const DECK_PHOTO_URL = 'textures/747-deck-gbnlp.jpg';
let deckPhoto = null;
function withDeckPhoto(cb) {
  if (!deckPhoto) { deckPhoto = new Image(); deckPhoto.src = DECK_PHOTO_URL; }
  if (deckPhoto.complete && deckPhoto.naturalWidth) cb(deckPhoto);
  else deckPhoto.addEventListener('load', () => cb(deckPhoto), { once: true });
}
// canvas texture that boots with painted art and upgrades to the photo crop
function photoTex(w, h, drawFallback, drawPhoto) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const ctx = c.getContext('2d');
  drawFallback(ctx, w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  withDeckPhoto(img => { drawPhoto(ctx, w, h, img); t.needsUpdate = true; });
  return t;
}
// lit-CRT painters, shared by the painted panel and the photo composite
function cxScreen(ctx, x, y, sw, sh) {
  ctx.fillStyle = '#191c20'; ctx.fillRect(x - 7, y - 7, sw + 14, sh + 14);
  ctx.strokeStyle = '#3f444b'; ctx.lineWidth = 2; ctx.strokeRect(x - 7, y - 7, sw + 14, sh + 14);
  ctx.fillStyle = '#05080a'; ctx.fillRect(x, y, sw, sh);
}
function cxPFD(ctx, x, y, sw, sh) {
  const ax = x + sw * 0.24, aw = sw * 0.52, ay = y + sh * 0.10, ah = sh * 0.58;
  ctx.fillStyle = '#1565c8'; ctx.fillRect(ax, ay, aw, ah * 0.5);      // sky
  ctx.fillStyle = '#7c5122'; ctx.fillRect(ax, ay + ah * 0.5, aw, ah * 0.5);  // ground
  ctx.fillStyle = '#fff'; ctx.fillRect(ax, ay + ah * 0.5 - 1, aw, 2); // horizon
  for (const p of [0.30, 0.40, 0.60, 0.70]) ctx.fillRect(ax + aw * 0.32, ay + ah * p, aw * 0.36, 1.5);
  ctx.fillStyle = '#e836e8';                                          // FD bars
  ctx.fillRect(ax + aw / 2 - 1, ay + ah * 0.34, 2, ah * 0.32);
  ctx.fillRect(ax + aw * 0.34, ay + ah * 0.5 - 1, aw * 0.32, 2);
  ctx.fillStyle = '#101418';                                          // tapes
  ctx.fillRect(x + 3, ay, sw * 0.15, sh * 0.72); ctx.fillRect(x + sw - 3 - sw * 0.15, ay, sw * 0.15, sh * 0.72);
  ctx.fillStyle = '#cfd4d9';
  for (let i = 0; i < 7; i++) { ctx.fillRect(x + 3, ay + 6 + i * sh * 0.10, 8, 1.5); ctx.fillRect(x + sw - 11, ay + 6 + i * sh * 0.10, 8, 1.5); }
  ctx.fillStyle = '#33e07a'; ctx.font = `bold ${Math.round(sh * 0.09)}px monospace`; ctx.textAlign = 'left';
  ctx.fillText('250', x + 4, ay + sh * 0.40); ctx.fillText('FL118', x + sw * 0.60, ay + sh * 0.40);
  ctx.fillText('SPD LNAV', x + sw * 0.22, y + sh * 0.08);             // FMA row
  ctx.strokeStyle = '#cfd4d9'; ctx.lineWidth = 1.5;                   // compass arc
  ctx.beginPath(); ctx.arc(x + sw / 2, y + sh * 1.28, sh * 0.48, -2.2, -0.94); ctx.stroke();
}
function cxND(ctx, x, y, sw, sh) {
  const cx = x + sw / 2, cy = y + sh * 0.88;
  ctx.strokeStyle = '#2ecc71'; ctx.lineWidth = 1.5;
  for (const r of [0.28, 0.52, 0.76]) { ctx.beginPath(); ctx.arc(cx, cy, sh * r, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
  ctx.strokeStyle = '#e836e8'; ctx.lineWidth = 2.5;                   // route
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx - sw * 0.10, cy - sh * 0.42); ctx.lineTo(cx + sw * 0.14, cy - sh * 0.70); ctx.stroke();
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.moveTo(cx, cy - 8); ctx.lineTo(cx - 6, cy + 4); ctx.lineTo(cx + 6, cy + 4); ctx.closePath(); ctx.fill();
  ctx.fillStyle = '#28d0d0'; ctx.font = `bold ${Math.round(sh * 0.08)}px monospace`; ctx.textAlign = 'left';
  ctx.fillText('SILVA', cx + sw * 0.16, cy - sh * 0.68);
  ctx.fillStyle = '#33e07a'; ctx.fillText('GS 488', x + 5, y + sh * 0.10);
}
function cxEICAS(ctx, x, y, sw, sh) {
  for (let e = 0; e < 4; e++) {
    const gx = x + sw * (0.14 + e * 0.24), gy = y + sh * 0.22, gr = sw * 0.085;
    ctx.strokeStyle = '#3a4046'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(gx, gy, gr, Math.PI * 0.75, Math.PI * 2.1); ctx.stroke();
    ctx.strokeStyle = '#2ecc71';
    ctx.beginPath(); ctx.arc(gx, gy, gr, Math.PI * 0.75, Math.PI * 1.7); ctx.stroke();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(gx, gy); ctx.lineTo(gx + gr * Math.cos(Math.PI * 1.7), gy + gr * Math.sin(Math.PI * 1.7)); ctx.stroke();
    ctx.fillStyle = '#2ecc71'; ctx.font = `bold ${Math.round(sh * 0.058)}px monospace`; ctx.textAlign = 'center';
    ctx.fillText('98.2', gx, gy + gr + sh * 0.07);
    ctx.strokeStyle = '#3a4046'; ctx.lineWidth = 3;                   // EGT row
    ctx.beginPath(); ctx.arc(gx, y + sh * 0.72, gr * 0.7, Math.PI * 0.75, Math.PI * 1.9); ctx.stroke();
  }
  ctx.fillStyle = '#28d0d0'; ctx.font = `bold ${Math.round(sh * 0.053)}px monospace`; ctx.textAlign = 'left';
  ctx.fillText('N1', x + 4, y + sh * 0.06); ctx.fillText('EGT', x + 4, y + sh * 0.66);
}
// 747 main instrument panel: PFD | ND | EICAS | ND | PFD, painted as lit CRTs
function drawCxPanel(ctx, w, h) {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, '#33373d'); g.addColorStop(1, '#26292e');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#1e2126'; ctx.fillRect(0, 0, w, 12);
  const pfd = (x, y, sw, sh) => { cxScreen(ctx, x, y, sw, sh); cxPFD(ctx, x, y, sw, sh); };
  const nd = (x, y, sw, sh) => { cxScreen(ctx, x, y, sw, sh); cxND(ctx, x, y, sw, sh); };
  const eicas = (x, y, sw, sh) => { cxScreen(ctx, x, y, sw, sh); cxEICAS(ctx, x, y, sw, sh); };
  const sy = h * 0.113, sh = h * 0.594;
  pfd(w * 0.055, sy, w * 0.164, sh); nd(w * 0.252, sy, w * 0.164, sh);
  eicas(w * 0.449, sy, w * 0.172, sh);
  nd(w * 0.645, sy, w * 0.164, sh); pfd(w * 0.832, sy, w * 0.164, sh);
  // standby ADI + gear lever between the centre screens and the F/O side
  const ax = w * 0.434, ay = h * 0.28;
  ctx.fillStyle = '#0a0d10'; ctx.beginPath(); ctx.arc(ax, ay, 16, 0, 7); ctx.fill();
  ctx.strokeStyle = '#cfd4d9'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(ax, ay, 16, 0, 7); ctx.stroke();
  ctx.fillStyle = '#1565c8'; ctx.beginPath(); ctx.arc(ax, ay, 11, Math.PI, 2 * Math.PI); ctx.fill();
  ctx.fillStyle = '#7c5122'; ctx.beginPath(); ctx.arc(ax, ay, 11, 0, Math.PI); ctx.fill();
  ctx.fillStyle = '#14171b'; ctx.fillRect(w * 0.63, h * 0.75, 8, h * 0.2);   // gear slot
  ctx.fillStyle = '#d9dde1'; ctx.beginPath(); ctx.arc(w * 0.63 + 4, h * 0.955, 10, 0, 7); ctx.fill();
  // knob row along the bottom edge
  for (let x = w * 0.06; x < w - 40; x += w * 0.06) {
    ctx.fillStyle = '#15181c'; ctx.beginPath(); ctx.arc(x, h * 0.87, 11, 0, 7); ctx.fill();
    ctx.fillStyle = '#8f969e'; ctx.beginPath(); ctx.arc(x, h * 0.87, 8, 0, 7); ctx.fill();
    ctx.fillStyle = '#15181c'; ctx.fillRect(x - 1, h * 0.85 - 7, 2, 7);
  }
}
// photo upgrade for the 747 main panel: the real panel band cropped from the
// flight-deck photograph, with the lit CRT art composited into its five dark
// (powered-down) screens so the instruments read live. Photo-pixel rects were
// measured off the 1024×683 source.
function drawCxPanelPhoto(ctx, w, h, img) {
  const cx0 = 88, cy0 = 238, cw = 848, chh = 196;        // panel band crop (photo px)
  ctx.drawImage(img, cx0, cy0, cw, chh, 0, 0, w, h);
  const R = (x0, y0, x1, y1) => [(x0 - cx0) / cw * w, (y0 - cy0) / chh * h,
                                 (x1 - x0) / cw * w, (y1 - y0) / chh * h];
  const lit = (kind, r) => {
    const [x, y, sw, sh] = r;
    ctx.fillStyle = '#05080a'; ctx.fillRect(x, y, sw, sh);   // wake the dark CRT
    kind(ctx, x, y, sw, sh);
    const glow = ctx.createRadialGradient(x + sw / 2, y + sh / 2, sh * 0.2, x + sw / 2, y + sh / 2, sh * 0.85);
    glow.addColorStop(0, 'rgba(120,200,170,0.10)'); glow.addColorStop(1, 'rgba(120,200,170,0)');
    ctx.fillStyle = glow; ctx.fillRect(x - 4, y - 4, sw + 8, sh + 8);
  };
  lit(cxPFD, R(221, 270, 305, 360));                     // captain PFD | ND
  lit(cxND,  R(317, 267, 397, 357));
  lit(cxEICAS, R(462, 267, 552, 365));                   // upper EICAS
  lit(cxND,  R(612, 270, 697, 362));                     // F/O ND | PFD
  lit(cxPFD, R(702, 270, 788, 362));
}
// photo upgrade for the glareshield face: the MCP strip crop, with the mode
// windows re-lit in amber so the autopilot targets glow like the painted art
function drawCxMCPPhoto(ctx, w, h, img) {
  ctx.drawImage(img, 88, 186, 848, 44, 0, 0, w, h);
  ctx.font = `bold ${Math.round(h * 0.30)}px monospace`; ctx.textAlign = 'center';
  const win = (px, txt) => {                             // photo px → lit window
    const x = (px - 88) / 848 * w, y = h * 0.22, wd = 46 / 848 * w, ht = h * 0.40;
    ctx.fillStyle = '#0b0e10'; ctx.fillRect(x, y, wd, ht);
    ctx.fillStyle = '#d9a13a'; ctx.fillText(txt, x + wd / 2, y + ht * 0.80);
  };
  win(352, '250'); win(464, '088'); win(552, '11000'); win(630, '+0000');
}
// glareshield face: the mode-control panel — amber digit windows and knobs
function drawCxMCP(ctx, w, h) {
  ctx.fillStyle = '#1f2226'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#282b30'; ctx.fillRect(8, 8, w - 16, h - 16);
  ctx.strokeStyle = '#3c4046'; ctx.lineWidth = 1.5; ctx.strokeRect(8, 8, w - 16, h - 16);
  const win = (x, txt, wd) => {
    ctx.fillStyle = '#0b0e10'; ctx.fillRect(x, 22, wd, 19);
    ctx.fillStyle = '#d9a13a'; ctx.font = 'bold 12px monospace'; ctx.textAlign = 'center';
    ctx.fillText(txt, x + wd / 2, 36);
  };
  const knob = x => {
    ctx.fillStyle = '#101316'; ctx.beginPath(); ctx.arc(x, 31, 12, 0, 7); ctx.fill();
    ctx.fillStyle = '#c3c8ce'; ctx.beginPath(); ctx.arc(x, 31, 9, 0, 7); ctx.fill();
    ctx.fillStyle = '#101316'; ctx.fillRect(x - 1.5, 21, 3, 9);
  };
  knob(48); knob(84);                                   // EFIS block
  win(150, '250', 58); knob(238);
  win(300, 'HDG 088', 84); knob(414);
  win(480, '11000', 76); knob(586);
  win(646, 'V/S +0000', 96); knob(772);
  for (let i = 0; i < 3; i++) {                         // A/P engage buttons
    ctx.fillStyle = '#34383e'; ctx.fillRect(820 + i * 44, 20, 34, 22);
    ctx.fillStyle = i === 0 ? '#2ecc71' : '#15181c'; ctx.fillRect(824 + i * 44, 24, 26, 3);
  }
  knob(972);
}
// 747 overhead panel, seen from below: module plates dense with switch rows,
// dim amber annunciators and a few round gauges — the jumbo's switch canopy
// (kept dark so it glows softly, not glaring, at night)
function drawCxOverhead(ctx, w, h) {
  ctx.fillStyle = '#322f2b'; ctx.fillRect(0, 0, w, h);
  const mod = (x, y, mw, mh) => {                       // one panel module
    ctx.fillStyle = '#3d3934'; ctx.fillRect(x, y, mw, mh);
    ctx.strokeStyle = '#4c4740'; ctx.lineWidth = 2; ctx.strokeRect(x, y, mw, mh);
  };
  const toggles = (x, y, n, gap) => {                   // a row of toggle switches
    for (let i = 0; i < n; i++) {
      ctx.fillStyle = '#191715'; ctx.beginPath(); ctx.arc(x + i * gap, y, 6, 0, 7); ctx.fill();
      ctx.fillStyle = '#b9bec4'; ctx.fillRect(x + i * gap - 2, y - 8, 4, 10);
    }
  };
  const lights = (x, y, n, on) => {                     // annunciator strip
    for (let i = 0; i < n; i++) {
      ctx.fillStyle = (i % on === 0) ? '#d9a13a' : '#4a443a';
      ctx.fillRect(x + i * 22, y, 16, 9);
    }
  };
  const gauge = (x, y) => {
    ctx.fillStyle = '#12100e'; ctx.beginPath(); ctx.arc(x, y, 15, 0, 7); ctx.fill();
    ctx.strokeStyle = '#8a847a'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(x, y, 15, 0, 7); ctx.stroke();
    ctx.strokeStyle = '#e4e8ec'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 9, y - 8); ctx.stroke();
  };
  // module grid: fuel / hydraulics / electrics / air-con / anti-ice / lights
  mod(14, 14, 230, 150);  toggles(40, 60, 6, 36);  toggles(40, 120, 6, 36);  lights(34, 24, 9, 4);
  mod(258, 14, 240, 150); gauge(300, 55); gauge(350, 55); gauge(400, 55); gauge(450, 55);
  toggles(292, 120, 5, 40); lights(280, 24, 9, 3);
  mod(14, 178, 230, 150); toggles(40, 220, 6, 36); toggles(40, 290, 6, 36); lights(34, 250, 9, 5);
  mod(258, 178, 240, 150); toggles(292, 220, 5, 40); lights(280, 250, 9, 4);
  gauge(300, 295); gauge(360, 295); gauge(420, 295);
  mod(14, 342, 484, 156);                               // aft block over the pedestal
  toggles(60, 390, 10, 44); toggles(60, 460, 10, 44); lights(46, 352, 19, 6);
  ctx.fillStyle = '#191715';                            // rotary selectors
  for (const x of [150, 260, 370]) { ctx.beginPath(); ctx.arc(x, 425, 13, 0, 7); ctx.fill();
    ctx.fillStyle = '#b9bec4'; ctx.fillRect(x - 2, 412, 4, 13); ctx.fillStyle = '#191715'; }
}
// centre-pedestal top: radio blocks with amber frequency windows, knob rows,
// and the black throttle-quadrant slot up front
function drawCxPedestal(ctx, w, h) {
  ctx.fillStyle = '#33302c'; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#0c0a09'; ctx.fillRect(w * 0.18, 8, w * 0.64, h * 0.30);   // quadrant slot
  ctx.strokeStyle = '#4c4740'; ctx.lineWidth = 2; ctx.strokeRect(w * 0.18, 8, w * 0.64, h * 0.30);
  const radio = (y, txt) => {
    ctx.fillStyle = '#242220'; ctx.fillRect(20, y, w - 40, 44);
    ctx.strokeStyle = '#45403a'; ctx.lineWidth = 1.5; ctx.strokeRect(20, y, w - 40, 44);
    ctx.fillStyle = '#0b0e10'; ctx.fillRect(32, y + 10, 84, 24);
    ctx.fillStyle = '#d9a13a'; ctx.font = 'bold 15px monospace'; ctx.textAlign = 'left';
    ctx.fillText(txt, 38, y + 28);
    for (const kx of [150, 190, 226]) {
      ctx.fillStyle = '#15130f'; ctx.beginPath(); ctx.arc(kx, y + 22, 11, 0, 7); ctx.fill();
      ctx.fillStyle = '#9aa0a7'; ctx.beginPath(); ctx.arc(kx, y + 22, 8, 0, 7); ctx.fill();
    }
  };
  radio(h * 0.36, '118.25'); radio(h * 0.36 + 54, '121.50'); radio(h * 0.36 + 108, '7600');
  ctx.fillStyle = '#e9e5da';                            // stab-trim wheels along the sides
  ctx.fillRect(4, h * 0.06, 10, h * 0.26); ctx.fillRect(w - 14, h * 0.06, 10, h * 0.26);
  ctx.fillStyle = '#1a1815';
  for (let y = h * 0.07; y < h * 0.31; y += 9) { ctx.fillRect(4, y, 10, 3); ctx.fillRect(w - 14, y, 10, 3); }
}
// windscreen rain film: faint wind-driven streaks + clinging droplets on a
// transparent canvas — the plane only shows it while the rain toggle is live
function drawCxRain(ctx, w, h) {
  ctx.clearRect(0, 0, w, h);
  for (let i = 0; i < 90; i++) {                        // runback streaks, slanted by the airflow
    const x = Math.random() * w, y = Math.random() * h, len = 14 + Math.random() * 60;
    ctx.strokeStyle = `rgba(214,228,238,${0.06 + Math.random() * 0.18})`;
    ctx.lineWidth = 0.8 + Math.random() * 1.4;
    ctx.beginPath(); ctx.moveTo(x, y);
    ctx.lineTo(x + len * 0.18 * (Math.random() < 0.5 ? -1 : 1), y + len);
    ctx.stroke();
  }
  for (let i = 0; i < 70; i++) {                        // clinging droplets
    ctx.fillStyle = `rgba(222,234,242,${0.10 + Math.random() * 0.20})`;
    ctx.beginPath();
    ctx.arc(Math.random() * w, Math.random() * h, 0.8 + Math.random() * 2.0, 0, 7);
    ctx.fill();
  }
}
// ---- prop-plane (Cessna-170-informed) canvases ------------------------------
const GA_RED = '#9c2a1e', GA_STRIPE = '#98a1a8', GA_WHITE = '#f3f5f7', GA_REG = '#6d7680';
// cabin barrel: white hull, maroon top wash over the nose, twin-pinstriped
// cheatline, door outlines and rear quarter windows
function drawPropBarrel(ctx, w, h) {
  for (let x = 0; x < w; x++) {
    const a = Math.min(x, w - x) / w * 2 * Math.PI;
    ctx.fillStyle = 0.26 * Math.cos(a) < -0.16 ? '#e2e6ea' : GA_WHITE;
    ctx.fillRect(x, 0, 1, h);
  }
  const X = a => a / 360 * w;
  ctx.fillStyle = GA_RED;                               // top wash aft of the cowl
  for (const m of [0, 1]) {
    const px = x => m ? w - x : x;
    ctx.beginPath();
    ctx.moveTo(px(0), 0); ctx.lineTo(px(X(60)), 0);
    ctx.quadraticCurveTo(px(X(52)), 120, px(X(14)), 158);
    ctx.lineTo(px(0), 162);
    ctx.closePath(); ctx.fill();
  }
  const cheat = (x0, x1) => {                           // maroon band + grey pinstripes
    ctx.fillStyle = GA_RED; ctx.fillRect(x0, 0, x1 - x0, h);
    ctx.fillStyle = GA_STRIPE; ctx.fillRect(x0 - 3, 0, 2, h); ctx.fillRect(x1 + 1, 0, 2, h);
  };
  cheat(X(63.7), X(76.7)); cheat(w - X(76.7), w - X(63.7));
  ctx.fillStyle = '#232e38';                            // rear quarter windows
  for (const m of [0, 1]) {
    const px = x => m ? w - x : x;
    ctx.beginPath();
    ctx.moveTo(px(X(41)), 360); ctx.lineTo(px(X(67)), 355);
    ctx.lineTo(px(X(67)), 408); ctx.lineTo(px(X(46)), 413);
    ctx.closePath(); ctx.fill();
  }
  ctx.strokeStyle = 'rgba(70,80,90,0.5)'; ctx.lineWidth = 2;   // cabin doors
  for (const x of [X(48), w - X(48) - X(38)]) {
    ctx.strokeRect(x, 286, X(38), 86);
    ctx.fillStyle = '#3a444e'; ctx.fillRect(x + X(30), 336, 10, 4);
  }
  ctx.strokeStyle = 'rgba(20,30,40,0.06)'; ctx.lineWidth = 1;  // rivet seams
  for (let y = 90; y < h; y += 84) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
}
// tapering aft hull: cheatline runs out, big retro registration, red sweep
function drawPropAft(ctx, w, h) {
  for (let x = 0; x < w; x++) {
    const a = Math.min(x, w - x) / w * 2 * Math.PI;
    ctx.fillStyle = 0.26 * Math.cos(a) < -0.16 ? '#e2e6ea' : GA_WHITE;
    ctx.fillRect(x, 0, 1, h);
  }
  const X = a => a / 360 * w;
  const fade = ctx.createLinearGradient(0, 0, 0, h * 0.8);
  fade.addColorStop(0, GA_RED); fade.addColorStop(0.85, GA_RED); fade.addColorStop(1, 'rgba(156,42,30,0)');
  for (const [x0, x1] of [[X(63.7), X(76.7)], [w - X(76.7), w - X(63.7)]]) {
    ctx.fillStyle = fade; ctx.fillRect(x0, 0, x1 - x0, h * 0.8);
    ctx.fillStyle = GA_STRIPE; ctx.fillRect(x0 - 3, 0, 2, h * 0.72); ctx.fillRect(x1 + 1, 0, 2, h * 0.72);
  }
  ctx.strokeStyle = GA_RED; ctx.lineWidth = 9; ctx.lineCap = 'round';   // tail sweep
  for (const m of [0, 1]) {
    const px = x => m ? w - x : x;
    ctx.beginPath(); ctx.moveTo(px(100), 205); ctx.quadraticCurveTo(px(112), 330, px(146), 462); ctx.stroke();
  }
  // vintage Hong Kong style registration (fictional — VR-H prefix retired 1997)
  const font = 'bold 46px "Arial Black", Arial, sans-serif';
  hullText(ctx, 'VR-HKS', 70, 130, -Math.PI / 2, font, GA_REG, '2px');
  hullText(ctx, 'VR-HKS', w - 70, 130, Math.PI / 2, font, GA_REG, '2px');
}
// engine cowl: deeper red top, louvres, belly intake, exhaust staining
function drawPropCowl(ctx, w, h) {
  ctx.fillStyle = GA_RED; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#7d1f15';
  ctx.fillRect(0, 0, w * 0.20, h); ctx.fillRect(w * 0.80, 0, w * 0.20, h);   // darker crown
  ctx.fillRect(0, 0, w, 8);                                                  // front lip
  ctx.fillStyle = '#4a120c';
  for (let i = 0; i < 3; i++) { ctx.fillRect(56, 44 + i * 13, 18, 3.5); ctx.fillRect(w - 74, 44 + i * 13, 18, 3.5); }
  ctx.fillStyle = '#20262b';                                                 // belly intake
  ctx.beginPath(); ctx.ellipse(w / 2, 28, 15, 16, 0, 0, 7); ctx.fill();
  ctx.fillStyle = 'rgba(30,34,38,0.14)';                                     // exhaust stain
  ctx.beginPath(); ctx.moveTo(w / 2 - 8, 44); ctx.lineTo(w / 2 + 8, 44); ctx.lineTo(w / 2 + 20, h); ctx.lineTo(w / 2 - 20, h); ctx.closePath(); ctx.fill();
}
// red rudder: ribbed fabric look with a white pinstripe echoing the cheatline
// (kept fore-aft symmetric-ish so the shared extrude UVs read fine on both faces)
function drawPropFin(ctx, w, h) {
  ctx.fillStyle = GA_RED; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#7d1f15'; ctx.fillRect(0, 0, w, h * 0.16);
  ctx.strokeStyle = 'rgba(0,0,0,0.12)'; ctx.lineWidth = 2;
  for (let x = 28; x < w - 10; x += 22) { ctx.beginPath(); ctx.moveTo(x, h * 0.10); ctx.lineTo(x, h * 0.86); ctx.stroke(); }
  ctx.strokeStyle = 'rgba(0,0,0,0.18)'; ctx.beginPath(); ctx.moveTo(w * 0.52, 0); ctx.lineTo(w * 0.52, h); ctx.stroke();
  ctx.fillStyle = '#f3f5f7'; ctx.fillRect(0, h * 0.80, w, 4);
  ctx.fillStyle = GA_STRIPE; ctx.fillRect(0, h * 0.80 + 6, w, 2);
}
// little six-pack panel + radio stack for the prop plane's POV — Betsy reuses
// it with her own registration placard (classic prop-era deck for both)
function drawPropPanel(ctx, w, h, reg = 'VR-HKS') {
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, '#2c2f34'); g.addColorStop(1, '#212327');
  ctx.fillStyle = g; ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = '#191c20'; ctx.fillRect(0, 0, w, 10);
  const gauge = (x, y, kind) => {
    ctx.fillStyle = '#131619'; ctx.beginPath(); ctx.arc(x, y, 25, 0, 7); ctx.fill();
    ctx.strokeStyle = '#43484f'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, 25, 0, 7); ctx.stroke();
    ctx.fillStyle = '#0c0f11'; ctx.beginPath(); ctx.arc(x, y, 21, 0, 7); ctx.fill();
    if (kind === 'ai') {
      ctx.fillStyle = '#1565c8'; ctx.beginPath(); ctx.arc(x, y, 19, Math.PI, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = '#7c5122'; ctx.beginPath(); ctx.arc(x, y, 19, 0, Math.PI); ctx.fill();
      ctx.fillStyle = '#fff'; ctx.fillRect(x - 19, y - 1, 38, 2);
      ctx.fillStyle = '#f4b32e'; ctx.fillRect(x - 8, y - 1.5, 16, 3);
      return;
    }
    ctx.strokeStyle = '#d5dade'; ctx.lineWidth = 1.2;
    for (let i = 0; i < 10; i++) {
      const t = Math.PI * 0.75 + i * Math.PI * 1.5 / 9;
      ctx.beginPath();
      ctx.moveTo(x + 16 * Math.cos(t), y + 16 * Math.sin(t));
      ctx.lineTo(x + 20 * Math.cos(t), y + 20 * Math.sin(t));
      ctx.stroke();
    }
    if (kind === 'asi') {                               // green speed arc
      ctx.strokeStyle = '#2ecc71'; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.arc(x, y, 18, Math.PI * 0.9, Math.PI * 1.7); ctx.stroke();
    }
    const na = kind === 'alt' ? -0.6 : kind === 'vsi' ? Math.PI : Math.PI * 1.35;
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 16 * Math.cos(na), y + 16 * Math.sin(na)); ctx.stroke();
    if (kind === 'alt') { ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + 10 * Math.cos(2.2), y + 10 * Math.sin(2.2)); ctx.stroke(); }
    ctx.fillStyle = '#d5dade'; ctx.beginPath(); ctx.arc(x, y, 2, 0, 7); ctx.fill();
  };
  gauge(100, 58, 'asi'); gauge(172, 58, 'ai'); gauge(244, 58, 'alt');
  gauge(100, 126, 'turn'); gauge(172, 126, 'hdg'); gauge(244, 126, 'vsi');
  for (let r = 0; r < 3; r++) {                         // radio stack
    ctx.fillStyle = '#141619'; ctx.fillRect(300, 32 + r * 42, 120, 30);
    ctx.strokeStyle = '#3a3f45'; ctx.lineWidth = 1.5; ctx.strokeRect(300, 32 + r * 42, 120, 30);
    ctx.fillStyle = r === 2 ? '#2ecc71' : '#d9a13a'; ctx.font = 'bold 11px monospace'; ctx.textAlign = 'left';
    ctx.fillText(r === 0 ? '118.25' : r === 1 ? '121.50' : '7600', 310, 51 + r * 42);
    ctx.fillStyle = '#c3c8ce'; ctx.beginPath(); ctx.arc(406, 47 + r * 42, 6, 0, 7); ctx.fill();
  }
  ctx.fillStyle = '#e8ebee'; ctx.font = 'bold 10px Arial, sans-serif'; ctx.textAlign = 'center';
  ctx.fillText(reg, 360, 180);
}
function buildPropPlane() {
  const s = 4;                                          // ~19 m wingspan: readable, near real scale
  const grp = new THREE.Group();
  // painted skins (Cessna 170 reference): each hull piece carries its livery
  const fusMat  = new THREE.MeshStandardMaterial({ map: canvasTex(512, 512, drawPropBarrel), roughness: 0.45, metalness: 0.15 });
  const aftMat  = new THREE.MeshStandardMaterial({ map: canvasTex(512, 512, drawPropAft), roughness: 0.45, metalness: 0.15 });
  const cowlMat = new THREE.MeshStandardMaterial({ map: canvasTex(256, 128, drawPropCowl), roughness: 0.5, metalness: 0.2 });
  const wingMat = new THREE.MeshStandardMaterial({ map: wingTileTex(0.9), roughness: 0.5, metalness: 0.1 });
  const red   = new THREE.MeshStandardMaterial({ color: 0x9c2a1e, roughness: 0.55 });
  const glass = new THREE.MeshStandardMaterial({ color: 0x27343f, roughness: 0.25, metalness: 0.5 });
  const dark  = new THREE.MeshStandardMaterial({ color: 0x22262b, roughness: 0.8 });
  // fuselage: cabin barrel tapering to the tail, red engine cowl + spinner up front
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 1.7, 20), fusMat);
  fus.rotation.x = -Math.PI / 2; fus.position.z = -0.55;
  grp.add(fus);
  const aft = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.07, 1.9, 20), aftMat);
  aft.rotation.x = -Math.PI / 2; aft.position.z = 1.25;  // wide end forward, tapering to the tail
  grp.add(aft);
  const cowl = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.26, 0.5, 20), cowlMat);
  cowl.rotation.x = -Math.PI / 2; cowl.position.z = -1.62;
  grp.add(cowl);
  const spinner = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.28, 12), red);
  spinner.rotation.x = -Math.PI / 2; spinner.position.z = -2.0;
  grp.add(spinner);
  const canopy = new THREE.Mesh(new THREE.SphereGeometry(0.22, 14, 10), glass);
  canopy.scale.set(0.85, 0.6, 1.5); canopy.position.set(0, 0.16, -0.6);
  grp.add(canopy);
  // high wing with a little sweep, red tips
  const wing = new THREE.Mesh(wingGeo(2.4, 0.78, 0.5, 0.16, 0.07), wingMat);
  wing.position.set(0, 0.2, -0.95);
  grp.add(wing);
  for (const sx of [-1, 1]) {
    const tip = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.075, 0.5), red);
    tip.position.set(sx * 2.34, 0.165, -0.55);
    grp.add(tip);
  }
  // tailplane + the classic rounded rudder — ribbed-fabric texture on its faces
  const tailW = new THREE.Mesh(wingGeo(0.85, 0.42, 0.26, 0.12, 0.05), wingMat);
  tailW.position.set(0, 0.12, 1.55);
  grp.add(tailW);
  const finTex = canvasTex(256, 256, drawPropFin);
  finTex.repeat.set(1 / 0.62, 1 / 0.58);                // extrude UVs are raw shape units
  const finFace = new THREE.MeshStandardMaterial({ map: finTex, roughness: 0.55 });
  const fin = new THREE.Mesh(finGeo([[0.1, 0], [0.62, 0], [0.56, 0.5], [0.3, 0.58], [0, 0.2]], 0.06), [finFace, red]);
  fin.position.set(0, 0.12, 1.4);
  grp.add(fin);
  // gear so the parked plane stands on something (origin lands at +2.2 m) —
  // grouped so stepFlight can hide the wheels once airborne (HKS-93)
  const gear = new THREE.Group();
  for (const sx of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.34, 0.08), dark);
    leg.position.set(sx * 0.42, -0.3, -0.72);
    gear.add(leg);
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.08, 12), dark);
    wheel.rotation.z = Math.PI / 2; wheel.position.set(sx * 0.42, -0.45, -0.72);
    gear.add(wheel);
  }
  const tailWheel = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.05, 10), dark);
  tailWheel.rotation.z = Math.PI / 2; tailWheel.position.set(0, -0.14, 1.7);
  gear.add(tailWheel);
  grp.add(gear);
  grp.userData.gear = gear;
  // two-blade prop, spun by stepFlight (HKS-87 landed behaviour unchanged)
  const prop = new THREE.Group();
  const b1 = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.07, 0.03), dark);
  const b2 = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.6, 0.03), dark);
  prop.add(b1); prop.add(b2);
  prop.position.z = -2.05;                             // hub tucked into the spinner
  grp.add(prop);
  grp.userData.prop = prop;
  // Cockpit (HKS-93): a painted six-pack panel the pilot sees only in the
  // 🧑‍✈️ cockpit view. Built in REAL METRES (cock.scale = 1/s cancels the ×4)
  // around the eye at ~(0, 2.3, -2.2) looking down -z; stepFlight shows it
  // only while F.view === 'cockpit'.
  const cock = new THREE.Group();
  const trim = new THREE.MeshStandardMaterial({ color: 0x0e1013, roughness: 0.95 });
  const panelMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(512, 224, drawPropPanel) }), trim];
  const panel = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.85, 0.18), panelMats);
  panel.position.set(0, 1.72, -3.1); panel.rotation.x = 0.42;
  cock.add(panel);
  const glare = new THREE.Mesh(new THREE.BoxGeometry(2.9, 0.16, 0.5), trim);
  glare.position.set(0, 2.14, -2.9); glare.rotation.x = -0.12;
  cock.add(glare);
  for (const sx of [-1, 1]) {                          // slim canopy posts
    const p = new THREE.Mesh(new THREE.BoxGeometry(0.12, 2.2, 0.12), trim);
    p.position.set(sx * 1.5, 2.6, -3.1); p.rotation.z = sx * 0.42;
    cock.add(p);
  }
  cock.scale.setScalar(1 / s);
  cock.visible = false;
  grp.add(cock);
  grp.userData.cockpit = cock;
  grp.userData.povFwd = 2.2; grp.userData.povUp = 2.3;   // cockpit eye: seated behind the cowl
  grp.userData.eyeFwd = 2.2; grp.userData.eyeUp = 2.3;   // 👁 eye view: same seat, panel hidden
  // nav lights: wingtips, tail, and the beacon on the fin tip (Cessna-style)
  addNavLights(grp, { wingL: [-2.42, 0.165, -0.55], wingR: [2.42, 0.165, -0.55],
                      tail: [0, 0.16, 1.80], top: [0, 0.70, 1.66], bot: [0, -0.30, -0.5] });
  grp.scale.setScalar(s);
  grp.visible = false;
  return grp;
}
// Cathay Pacific Boeing 747 (HKS-93): the classic 90s "brushwing" livery,
// painted onto canvas textures — white crown, grey-blue band, grey belly,
// window rows, jade nose swoosh + titles, and the bristled white brushstroke
// on the jade fin. Low-poly, same frame/scale as the prop plane; no propeller
// (jet), so stepFlight's prop guard skips and the engine audio carries it.
function buildCX747() {
  const s = 4;                                          // ~22 m long / ~23 m span — jumbo next to the prop
  const grp = new THREE.Group();
  const white = new THREE.MeshStandardMaterial({ color: 0xf2f5f7, roughness: 0.4, metalness: 0.2 });
  const jade  = new THREE.MeshStandardMaterial({ color: 0x00655b, roughness: 0.5, metalness: 0.15 });
  const grey  = new THREE.MeshStandardMaterial({ color: 0xb7bec4, roughness: 0.5, metalness: 0.3 });
  const dark  = new THREE.MeshStandardMaterial({ color: 0x22282e, roughness: 0.7 });
  const skin = draw => new THREE.MeshStandardMaterial({ map: canvasTex(512, 1024, draw), roughness: 0.4, metalness: 0.15 });
  // fuselage barrel — one painted cylinder carries bands/windows/titles/swoosh
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 3.4, 24), skin(drawCxBarrel));
  fus.rotation.x = -Math.PI / 2; fus.position.z = 0.1;
  grp.add(fus);
  // nose: pole-forward sphere so u wraps the hull like the barrel; painted
  // windscreen + the jade swoosh wrapping the front above the radome
  const noseMat = new THREE.MeshStandardMaterial({ map: canvasTex(512, 256, drawCxNose), roughness: 0.4, metalness: 0.15 });
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.3, 24, 16), noseMat);
  nose.rotation.x = -Math.PI / 2; nose.scale.set(1, 1.8, 1);
  nose.position.z = -1.6;
  grp.add(nose);
  // tail cone: painted bands + the last cabin windows curving with the taper
  const tailMat = new THREE.MeshStandardMaterial({ map: canvasTex(256, 256, drawCxTail), roughness: 0.4, metalness: 0.15 });
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.05, 1.5, 24), tailMat);
  tail.rotation.x = -Math.PI / 2 - 0.09;               // wide end forward, tip swept slightly up
  tail.position.set(0, 0.06, 2.53);
  grp.add(tail);
  // the signature upper deck — a low, STREAMLINED raised roofline (iterated
  // against the real 747-400 side profile, where the hump adds only ~25% over
  // the main-deck crown and fades out through a long aft fairing): a lathe
  // body of revolution laid along the hull that rises just behind the cockpit,
  // runs nearly level over the forward third, then tapers away gently. The
  // revolve axis sits INSIDE the fuselage (y 0.25 < crown 0.3), so both
  // pointed ends emerge from the skin instead of capping in mid-air.
  const humpMat = new THREE.MeshStandardMaterial({ map: canvasTex(512, 256, drawCxHump), roughness: 0.4, metalness: 0.15 });
  const humpPts = [[0.02, 0], [0.05, 0.5], [0.085, 1.0], [0.118, 1.5], [0.14, 1.95],
                   [0.145, 2.3], [0.145, 2.6], [0.12, 2.8], [0.065, 2.95], [0.02, 3.02]]
    .map(p => new THREE.Vector2(p[0], p[1]));
  const humpG = new THREE.LatheGeometry(humpPts, 20);
  humpG.rotateX(-Math.PI / 2);                          // profile runs forward (-z); u=0 stays at the crown
  const hump = new THREE.Mesh(humpG, humpMat);
  hump.scale.x = 1.45;                                  // the upper deck reads nearly fuselage-wide
  hump.position.set(0, 0.25, 1.15);                     // long aft fairing from z 1.15 → front tip z -1.87, behind the cockpit
  grp.add(hump);
  // swept wings with dihedral, four podded engines slung ahead of the leading edge
  const wingMat = new THREE.MeshStandardMaterial({ map: wingTileTex(0.7), roughness: 0.4, metalness: 0.2, side: THREE.DoubleSide });
  const wingG = wingGeo(2.8, 0.95, 0.28, 1.6, 0.06, true);   // one half, mirrored below
  for (const sx of [-1, 1]) {
    const w = new THREE.Mesh(wingG, wingMat);
    w.scale.x = sx; w.rotation.z = sx * 0.09;          // mirrored halves → dihedral
    w.position.set(0, -0.14, -0.5);
    grp.add(w);
    for (const ex of [1.15, 1.95]) {
      const ey = -0.14 + ex * 0.09 - 0.17;             // hang below the (dihedralled) wing
      const ez = -0.5 + 1.6 * (ex / 2.8) - 0.28;       // ahead of the local leading edge
      const nac = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.085, 0.44, 12), grey);
      nac.rotation.x = -Math.PI / 2; nac.position.set(sx * ex, ey, ez);
      grp.add(nac);
      const inlet = new THREE.Mesh(new THREE.CylinderGeometry(0.105, 0.105, 0.07, 12), dark);
      inlet.rotation.x = -Math.PI / 2; inlet.position.set(sx * ex, ey, ez - 0.2);
      grp.add(inlet);
      const pylon = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.16, 0.3), white);
      pylon.position.set(sx * ex, ey + 0.13, ez + 0.16);
      grp.add(pylon);
    }
  }
  // tailplane + the tall fin: jade core for the edges, painted side faces
  // carrying the brushwing (mirrored art on the starboard face so the stroke
  // sweeps up-and-aft on both sides, like the real livery)
  const tailW = new THREE.Mesh(wingGeo(1.1, 0.5, 0.18, 0.55, 0.05), wingMat);
  tailW.position.set(0, 0.14, 2.55);
  grp.add(tailW);
  const fin = new THREE.Mesh(finGeo([[0, 0], [0.9, 0], [1.3, 1.05], [1.0, 1.05]], 0.07), jade);
  fin.position.set(0, 0.24, 2.15);
  grp.add(fin);
  const finShape = new THREE.Shape();
  finShape.moveTo(0, 0); finShape.lineTo(0.9, 0);
  finShape.lineTo(1.3, 1.05); finShape.lineTo(1.0, 1.05);
  finShape.closePath();
  const finSideG = new THREE.ShapeGeometry(finShape);
  finSideG.rotateY(-Math.PI / 2);                      // faces -x (port)
  for (const sx of [-1, 1]) {
    const tex = canvasTex(320, 256, (c, w2, h2) => drawCxFin(c, w2, h2, sx === 1));
    tex.repeat.set(1 / 1.3, 1 / 1.05);                 // shape UVs are raw metres
    const side = new THREE.Mesh(finSideG, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.5 }));
    if (sx === 1) side.scale.x = -1;                   // starboard: mirrored geometry + art
    side.position.set(sx * 0.041, 0.24, 2.15);
    grp.add(side);
  }
  // gear: nose strut + two main bogies (wheels reach y = -0.55, the landed
  // line), grouped so stepFlight can retract it — wheels only show on the ground
  const gear = new THREE.Group();
  const gearAt = (x, z) => {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.26, 0.06), dark);
    leg.position.set(x, -0.34, z);
    gear.add(leg);
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.095, 0.095, 0.16, 12), dark);
    wheel.rotation.z = Math.PI / 2; wheel.position.set(x, -0.455, z);
    gear.add(wheel);
  };
  gearAt(0, -1.45); gearAt(-0.3, 0.45); gearAt(0.3, 0.45);
  grp.add(gear);
  grp.userData.gear = gear;
  // --- flight-deck interior (HKS-93): the 747 cockpit the pilot sees in the
  // 🧑‍✈️ cockpit view, photo-textured from a real 747-400 deck (see
  // DECK_PHOTO_URL — CC BY 2.0, credited in the Credits drawer) with 3D
  // yokes/throttles/frame in front so head-look still parallaxes. Parented to
  // the plane so it rolls with the horizon; stepFlight shows it only while
  // F.view === 'cockpit' — hidden in chase AND in the clean 👁 eye view. Designed
  // in REAL METRES (cock.scale = 1/s cancels the ×4) around the captain-height
  // eye at (0, 2.72, -2.9) looking down -z with a 6° default nose-down head
  // tilt (povPitch): straight ahead, the glareshield lip crosses just below
  // screen centre, the photo panel + yoke tops fill the lower ~45%, the four
  // throttles peek in at lower-centre, and the upper half stays windscreen.
  // Cinematic-simulator ambience over systems accuracy; no logos inside.
  const cock = new THREE.Group();
  const trim = new THREE.MeshStandardMaterial({ color: 0x15181c, roughness: 0.85 });
  const post = new THREE.MeshStandardMaterial({ color: 0x20242a, roughness: 0.7 });
  const bezel = new THREE.MeshStandardMaterial({ color: 0x24211e, roughness: 0.8 });
  // — main instrument panel (photo band, CRTs re-lit), ~1.15 m ahead of the eye
  const panelMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: photoTex(1024, 240, drawCxPanel, drawCxPanelPhoto) }), trim];
  const panel = new THREE.Mesh(new THREE.BoxGeometry(3.0, 0.72, 0.12), panelMats);
  panel.position.set(0, 2.10, -4.25); panel.rotation.x = 0.30;   // top edge ~0.28 below the eye
  cock.add(panel);
  // — glareshield: a THIN eyebrow shelf over the panel top (the real one is a
  // narrow lip, not a fascia) with the photo MCP strip on its face, re-lit
  const glareMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: photoTex(1024, 48, drawCxMCP, drawCxMCPPhoto) }), trim];
  const glare = new THREE.Mesh(new THREE.BoxGeometry(3.06, 0.10, 0.30), glareMats);
  glare.position.set(0, 2.51, -4.15); glare.rotation.x = -0.08;
  cock.add(glare);
  // — windscreen frame: header and the two slim pane dividers, up in the sky
  // band so terrain stays open; raked side pillars edge the view
  const header = new THREE.Mesh(new THREE.BoxGeometry(3.7, 0.24, 0.26), post);
  header.position.set(0, 3.56, -4.5);
  cock.add(header);
  for (const px of [-0.55, 0.55]) {
    const cpost = new THREE.Mesh(new THREE.BoxGeometry(0.07, 1.0, 0.14), post);
    cpost.position.set(px, 3.0, -4.38); cpost.rotation.x = 0.12;
    cock.add(cpost);
  }
  for (const sx of [-1, 1]) {
    const side = new THREE.Mesh(new THREE.BoxGeometry(0.22, 2.1, 0.24), post);
    side.position.set(sx * 1.75, 2.9, -4.05); side.rotation.z = sx * 0.30; side.rotation.x = 0.12;
    cock.add(side);
    // side walls up to the sill line below the open side glass
    const sill = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.85, 2.4), post);
    sill.position.set(sx * 1.68, 1.9, -2.9);
    cock.add(sill);
    // side console filling floor → sill so a down-glance never leaks terrain
    const console_ = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.5, 2.6), trim);
    console_.position.set(sx * 1.32, 1.78, -2.9);
    cock.add(console_);
  }
  // — overhead panel: the jumbo's switch canopy over both seats, its painted
  // underside dense with toggle rows and dim amber annunciators; pushed up to
  // the header line so it only leans into view when the pilot looks up
  const ovhMats = [trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(512, 512, drawCxOverhead) }), trim, trim];
  const ovh = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.12, 1.2), ovhMats);
  ovh.position.set(0, 3.52, -3.95); ovh.rotation.x = 0.14;   // forward edge dips toward the header
  cock.add(ovh);
  // — twin control YOKES (columns + U-wheels) in front of each seat; their
  // horns rise into the bottom of the forward view for the 3D parallax layer
  // (warm grey-brown like the photo's, so they read against the dark panel)
  const yokeMat = new THREE.MeshStandardMaterial({ color: 0x6e6156, roughness: 0.7 });
  const yokeWheelG = new THREE.TorusGeometry(0.20, 0.036, 8, 20, Math.PI);
  yokeWheelG.rotateZ(Math.PI);                          // U-shape: horns up, open at the top
  for (const sx of [-1, 1]) {
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 0.55, 10), yokeMat);
    col.position.set(sx * 0.48, 1.85, -3.55); col.rotation.x = 0.22;
    cock.add(col);
    const hub = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.15, 0.06), yokeMat);
    hub.position.set(sx * 0.48, 2.10, -3.61);
    cock.add(hub);
    const wheel = new THREE.Mesh(yokeWheelG, yokeMat);
    wheel.position.set(sx * 0.48, 2.21, -3.60); wheel.rotation.x = -0.1;
    cock.add(wheel);
  }
  // — centre pedestal with the FOUR-lever throttle quadrant (one per engine),
  // flanked by the shorter speedbrake (port) and flap (starboard) levers;
  // knob tops reach ~2.42 so they show at lower-centre in the straight-ahead view
  const pedMats = [trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(256, 384, drawCxPedestal) }), trim, trim, trim];
  const ped = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.5, 1.5), pedMats);
  ped.position.set(0, 1.85, -3.15);                     // top face at y 2.10, between the seats
  cock.add(ped);
  const knobW = new THREE.MeshStandardMaterial({ color: 0xc9ced4, roughness: 0.6 });
  const knobD = new THREE.MeshStandardMaterial({ color: 0x3a3f45, roughness: 0.7 });
  for (let i = 0; i < 4; i++) {                         // the four throttles
    const lx = (i - 1.5) * 0.10;
    const lever = new THREE.Mesh(new THREE.BoxGeometry(0.034, 0.26, 0.04), bezel);
    lever.position.set(lx, 2.20, -3.58); lever.rotation.x = -0.28;
    cock.add(lever);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.034, 8, 6), knobW);
    knob.position.set(lx, 2.32, -3.62);
    cock.add(knob);
  }
  for (const sx of [-1, 1]) {                           // speedbrake / flap levers
    const lever = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.20, 0.036), bezel);
    lever.position.set(sx * 0.24, 2.14, -3.46); lever.rotation.x = -0.40;
    cock.add(lever);
    const knob = new THREE.Mesh(new THREE.SphereGeometry(0.03, 8, 6), knobD);
    knob.position.set(sx * 0.24, 2.23, -3.51);
    cock.add(knob);
  }
  // — two pilot seats (pale sheepskin cushions on dark frames), just behind the eye
  const wool = new THREE.MeshStandardMaterial({ color: 0xcfc9ba, roughness: 1.0 });
  for (const sx of [-1, 1]) {
    const cushion = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.16, 0.6), wool);
    cushion.position.set(sx * 0.7, 1.95, -2.35);
    cock.add(cushion);
    const back = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.9, 0.16), wool);
    back.position.set(sx * 0.7, 2.42, -1.95); back.rotation.x = -0.1;
    cock.add(back);
  }
  // — deck floor over the hump crown so a look down reads as cockpit, not hull;
  // it stops short of the raked main panel so it never slices the CRTs
  const floor = new THREE.Mesh(new THREE.BoxGeometry(4.2, 0.1, 4.2),
    new THREE.MeshStandardMaterial({ color: 0x2a2624, roughness: 0.95 }));
  floor.position.set(0, 1.55, -2.6);
  cock.add(floor);
  // — windscreen rain film: streaks + droplets, shown only while it rains
  // (stepFlight syncs visibility with the live weather each POV frame)
  const rainFilm = new THREE.Mesh(new THREE.PlaneGeometry(3.5, 1.15),
    new THREE.MeshBasicMaterial({ map: canvasTex(512, 256, drawCxRain), transparent: true,
                                  opacity: 0.55, depthWrite: false }));
  rainFilm.position.set(0, 2.98, -4.3); rainFilm.rotation.x = 0.12;
  rainFilm.visible = false;
  cock.add(rainFilm);
  cock.userData.rain = rainFilm;
  cock.scale.setScalar(1 / s);                          // cancel the group's ×4 so the metres above are literal
  cock.visible = false;
  grp.add(cock);
  grp.userData.cockpit = cock;
  grp.userData.povFwd = 2.9; grp.userData.povUp = 2.72;  // cockpit eye: captain height behind the panel
  grp.userData.povPitch = -0.105;                        // cockpit resting gaze ~6° below the horizon
  grp.userData.eyeFwd = 5.6; grp.userData.eyeUp = 3.05;   // 👁 eye view: the original clean upper-deck eye — higher, level, no interior
  // nav lights: swept wingtips, tail cone, beacons on the hump crest & belly
  addNavLights(grp, { wingL: [-2.8, 0.11, 1.12], wingR: [2.8, 0.11, 1.12],
                      tail: [0, 0.13, 3.30], top: [0, 0.40, -0.3], bot: [0, -0.32, 0] });
  grp.scale.setScalar(s);
  grp.visible = false;
  return grp;
}
// Cathay Pacific Boeing 777-300 (HKS-93): the humpless long twin-jet, built
// from the CX 777-300 press side profile — one clean single deck, TWO very
// large underwing turbofans with painted fan faces, swept wings ending in the
// 777's raked tips, and the tall single fin carrying the brushwing (modern
// livery: deeper jade, no red stripe). Same frame/scale/texture conventions
// as the 747; no propeller, so stepFlight's prop guard skips it too.
function buildCX777() {
  const s = 4;                                          // ~26 m long / ~26 m span at ×4 — long and lean
  const grp = new THREE.Group();
  const white = new THREE.MeshStandardMaterial({ color: 0xf2f5f7, roughness: 0.4, metalness: 0.2 });
  const jade  = new THREE.MeshStandardMaterial({ color: 0x00655b, roughness: 0.5, metalness: 0.15 });
  const grey  = new THREE.MeshStandardMaterial({ color: 0xb7bec4, roughness: 0.5, metalness: 0.3 });
  const dark  = new THREE.MeshStandardMaterial({ color: 0x22282e, roughness: 0.7 });
  // the LONG single-deck barrel — the 777-300 stretch is the silhouette
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 4.4, 24),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 1024, drawCx777Barrel), roughness: 0.4, metalness: 0.15 }));
  fus.rotation.x = -Math.PI / 2; fus.position.z = 0.1;   // z -2.1 … 2.3
  grp.add(fus);
  // pointed nose, pole-forward like the 747's; the jade cheatline runs through
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.28, 24, 16),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 256, (c, w2, h2) => drawCxNose(c, w2, h2, '777')), roughness: 0.4, metalness: 0.15 }));
  nose.rotation.x = -Math.PI / 2; nose.scale.set(1, 2.1, 1);
  nose.position.z = -2.08;                              // equator tucked 0.02 into the barrel — no seam ring
  grp.add(nose);
  // long tail cone, tip swept slightly up; wide end nosed into the barrel so
  // the join never shows a diameter step
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.04, 1.8, 24),
    new THREE.MeshStandardMaterial({ map: canvasTex(256, 256, drawCxTail), roughness: 0.4, metalness: 0.15 }));
  tail.rotation.x = -Math.PI / 2 - 0.08;               // wide end forward
  tail.position.set(0, 0.055, 3.14);
  grp.add(tail);
  // wing-root belly fairing: an ellipsoid over the wing box so the wings grow
  // out of the hull instead of poking from a bare cylinder
  const fairing = new THREE.Mesh(new THREE.SphereGeometry(0.28, 20, 12),
    new THREE.MeshStandardMaterial({ color: 0xb2bbc2, roughness: 0.45, metalness: 0.2 }));
  fairing.scale.set(1.25, 0.62, 2.4);
  fairing.position.set(0, -0.10, 0.15);
  grp.add(fairing);
  // swept wings with dihedral; the raked tip flows off the leading edge in one
  // smooth curve (no planform kink) and the trailing edge curves back in
  const wingMat = new THREE.MeshStandardMaterial({ map: wingTileTex(0.7), roughness: 0.4, metalness: 0.2, side: THREE.DoubleSide });
  const wShape = new THREE.Shape();                     // half-wing, root at x 0
  wShape.moveTo(0, 0);
  wShape.lineTo(2.3, 1.40);                             // leading edge out to the tip run…
  wShape.quadraticCurveTo(2.85, 1.83, 3.15, 2.42);      // …curving aft into the raked tip
  wShape.lineTo(3.15, 2.52);
  wShape.quadraticCurveTo(2.72, 2.06, 2.3, 1.76);       // trailing edge eases back in
  wShape.lineTo(0, 1.05);
  wShape.closePath();
  const wingG = new THREE.ExtrudeGeometry(wShape, { depth: 0.06, bevelEnabled: false, curveSegments: 8 });
  wingG.rotateX(Math.PI / 2);
  for (const sx of [-1, 1]) {
    const wg = new THREE.Mesh(wingG, wingMat);
    wg.scale.x = sx; wg.rotation.z = sx * 0.10;        // mirrored halves → dihedral
    wg.position.set(0, -0.15, -0.35);
    grp.add(wg);
    // ONE very large turbofan per side — the 777's engines are its signature:
    // nearly half the fuselage diameter, hung under and ahead of the leading
    // edge on a real pylon that bridges nacelle → wing in one piece
    const ex = 0.95, ey = -0.27, ez = -0.12;
    const nac = new THREE.Mesh(new THREE.CylinderGeometry(0.165, 0.15, 0.72, 16), grey);
    nac.rotation.x = -Math.PI / 2; nac.position.set(sx * ex, ey, ez);
    grp.add(nac);
    const lip = new THREE.Mesh(new THREE.TorusGeometry(0.158, 0.022, 10, 18), grey);
    lip.position.set(sx * ex, ey, ez - 0.36);          // rounded inlet ring, not a can rim
    grp.add(lip);
    const fan = new THREE.Mesh(new THREE.CircleGeometry(0.152, 20),
      new THREE.MeshStandardMaterial({ map: canvasTex(128, 128, drawCxFan), roughness: 0.6 }));
    fan.rotation.y = Math.PI;                          // face forward (-z)
    fan.position.set(sx * ex, ey, ez - 0.35);
    grp.add(fan);
    const exh = new THREE.Mesh(new THREE.CylinderGeometry(0.145, 0.085, 0.30, 16), grey);
    exh.rotation.x = -Math.PI / 2; exh.position.set(sx * ex, ey, ez + 0.50);
    grp.add(exh);                                      // tapered exhaust sleeve…
    const core = new THREE.Mesh(new THREE.ConeGeometry(0.055, 0.22, 12), dark);
    core.rotation.x = Math.PI / 2;                     // …around the dark core cone
    core.position.set(sx * ex, ey, ez + 0.70);
    grp.add(core);
    // pylon: a swept wedge sunk into the nacelle crown below and the wing
    // underside above, so engine and wing read as one connected structure
    const pylon = new THREE.Mesh(finGeo([[-0.30, 0], [0.50, 0], [0.50, 0.09], [0.05, 0.09]], 0.075), white);
    pylon.position.set(sx * ex, -0.15, ez + 0.10);     // base in the nacelle, top in the wing skin
    grp.add(pylon);
  }
  // tailplane + the tall single fin: jade core, painted brushwing side faces;
  // the fin base is sunk into the tail-cone crown so it never floats
  const tailW = new THREE.Mesh(wingGeo(1.2, 0.55, 0.18, 0.6, 0.05), wingMat);
  tailW.position.set(0, 0.10, 3.02);
  grp.add(tailW);
  const finPts = [[0.10, 0], [1.05, 0], [1.40, 1.15], [1.07, 1.15]];
  const fin = new THREE.Mesh(finGeo(finPts, 0.07), jade);
  fin.position.set(0, 0.13, 2.52);
  grp.add(fin);
  const finShape = new THREE.Shape();
  finShape.moveTo(0.10, 0); finShape.lineTo(1.05, 0);
  finShape.lineTo(1.40, 1.15); finShape.lineTo(1.07, 1.15);
  finShape.closePath();
  const finSideG = new THREE.ShapeGeometry(finShape);
  finSideG.rotateY(-Math.PI / 2);                      // faces -x (port)
  for (const sx of [-1, 1]) {
    const tex = canvasTex(320, 256, (c, w2, h2) => drawCxFin(c, w2, h2, sx === 1, false));
    tex.repeat.set(1 / 1.40, 1 / 1.15);                // shape UVs are raw metres
    const side = new THREE.Mesh(finSideG, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.5 }));
    if (sx === 1) side.scale.x = -1;                   // starboard: mirrored geometry + art
    side.position.set(sx * 0.041, 0.13, 2.52);
    grp.add(side);
  }
  // gear: nose strut + two main bogies (wheels reach y = -0.55), grouped so
  // stepFlight can retract it — wheels only show on the ground
  const gear = new THREE.Group();
  const gearAt = (x, z) => {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.26, 0.06), dark);
    leg.position.set(x, -0.34, z);
    gear.add(leg);
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.095, 0.095, 0.16, 12), dark);
    wheel.rotation.z = Math.PI / 2; wheel.position.set(x, -0.455, z);
    gear.add(wheel);
  };
  gearAt(0, -1.85); gearAt(-0.3, 0.35); gearAt(0.3, 0.35);
  grp.add(gear);
  grp.userData.gear = gear;
  // Flight deck (glass cockpit): the same painted-panel treatment as the
  // 747 — big-LCD main panel + MCP glareshield + windscreen frame — sat lower,
  // this deck is on the single main level. REAL METRES around the eye at
  // ~(0, 2.4, -2.8) looking down -z; stepFlight shows it only in 🧑‍✈️ cockpit view.
  const cock = new THREE.Group();
  const trim = new THREE.MeshStandardMaterial({ color: 0x15181c, roughness: 0.85 });
  const post = new THREE.MeshStandardMaterial({ color: 0x20242a, roughness: 0.7 });
  const panelMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(1024, 320, drawCxPanel) }), trim];
  const panel = new THREE.Mesh(new THREE.BoxGeometry(5.2, 1.6, 0.3), panelMats);
  panel.position.set(0, 1.22, -4.75); panel.rotation.x = 0.42;
  cock.add(panel);
  const glareMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(1024, 64, drawCxMCP) }), trim];
  const glare = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.34, 0.42), glareMats);
  glare.position.set(0, 2.02, -4.55); glare.rotation.x = -0.18;
  cock.add(glare);
  const header = new THREE.Mesh(new THREE.BoxGeometry(5.6, 0.32, 0.3), post);
  header.position.set(0, 3.9, -5.6);
  cock.add(header);
  const cpost = new THREE.Mesh(new THREE.BoxGeometry(0.16, 1.9, 0.22), post);
  cpost.position.set(0, 3.1, -5.6);
  cock.add(cpost);
  for (const sx of [-1, 1]) {
    const side = new THREE.Mesh(new THREE.BoxGeometry(0.26, 3.6, 0.26), post);
    side.position.set(sx * 2.7, 2.8, -5.2); side.rotation.z = sx * 0.34;
    cock.add(side);
  }
  cock.scale.setScalar(1 / s);                          // cancel the group's ×4 so the metres above are literal
  cock.visible = false;
  grp.add(cock);
  grp.userData.cockpit = cock;
  grp.userData.povFwd = 2.8; grp.userData.povUp = 2.4;   // cockpit eye on the single deck, ahead of the wing
  grp.userData.eyeFwd = 5.6; grp.userData.eyeUp = 2.5;   // 👁 eye view: same seat, deck hidden
  // nav lights: raked wingtips, tail cone, beacons on the crown & belly
  addNavLights(grp, { wingL: [-3.15, 0.17, 2.10], wingR: [3.15, 0.17, 2.10],
                      tail: [0, 0.13, 4.02], top: [0, 0.31, 0.1], bot: [0, -0.31, 0.1] });
  grp.scale.setScalar(s);
  grp.visible = false;
  return grp;
}
// ---- Cathay Pacific "Betsy" — Douglas DC-3 (HKS-93) -------------------------
// Cathay's first aircraft (reg VR-HDB, 1946), restored and hanging in the Hong
// Kong Science Museum today — painted from study of the museum aircraft's
// photos on Wikimedia Commons: polished-metal hull, the black anti-glare nose
// cap, the period CPA globe roundel + dark-teal pennant on the forward
// fuselage, big black VR-HDB on the rear, and a Union Jack up the fin.
const BETSY_TEAL = '#123f4e', BETSY_YEL = '#e8b73a';
const BETSY_HULL = ['#e3e7eb', '#c6ccd2', '#a2a9b0'];
const betsyHull = yw => yw > 0.10 ? BETSY_HULL[0] : yw > -0.10 ? BETSY_HULL[1] : BETSY_HULL[2];
// polished-metal panel grid: frame seams + rivet dots over any silver piece
function betsyPanels(ctx, w, h, step) {
  ctx.strokeStyle = 'rgba(40,50,60,0.10)'; ctx.lineWidth = 1;
  for (let y = step; y < h; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
  ctx.fillStyle = 'rgba(40,50,60,0.09)';
  for (let y = step; y < h; y += step)
    for (let x = 5; x < w; x += 15) ctx.fillRect(x, y - 2, 1.5, 1.5);
}
// cabin barrel: silver bands, the CPA globe + letters + forward pennant, and
// the DC-3's row of squarish cabin windows down each side
function drawBetsyBarrel(ctx, w, h) {
  for (let x = 0; x < w; x++) {                        // metal bands per column
    const a = Math.min(x, w - x) / w * 2 * Math.PI;
    ctx.fillStyle = betsyHull(0.24 * Math.cos(a));
    ctx.fillRect(x, 0, 1, h);
  }
  const X = a => a / 360 * w;
  betsyPanels(ctx, w, h, 80);
  for (const m of [0, 1]) {                            // 0 = starboard, 1 = port
    const px = x => m ? w - x : x;
    // the CPA pennant: a slender dark-teal flag sweeping forward under the titles
    ctx.fillStyle = BETSY_TEAL;
    ctx.beginPath();
    ctx.moveTo(px(X(60)), 150);                        // apex points forward
    ctx.lineTo(px(X(48)), 292); ctx.lineTo(px(X(70)), 300);
    ctx.closePath(); ctx.fill();
    // the globe roundel ahead of the letters: white disc, yellow landmasses
    const gx = px(X(56)), gy = 118;
    ctx.fillStyle = '#f2f4f6'; ctx.beginPath(); ctx.arc(gx, gy, 27, 0, 7); ctx.fill();
    ctx.strokeStyle = BETSY_TEAL; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(gx, gy, 27, 0, 7); ctx.stroke();
    ctx.fillStyle = BETSY_YEL;
    ctx.beginPath(); ctx.ellipse(gx - 6, gy - 8, 12, 8, 0.5, 0, 7); ctx.fill();  // Asia blob
    ctx.beginPath(); ctx.ellipse(gx + 9, gy + 10, 8, 5, -0.4, 0, 7); ctx.fill(); // the islands
    ctx.beginPath(); ctx.ellipse(gx - 11, gy + 12, 5, 4, 0.2, 0, 7); ctx.fill();
  }
  // 'CPA' titles aft of the roundel, reading correctly per side
  const font = 'bold 38px "Arial Black", Arial, sans-serif';
  hullText(ctx, 'CPA', X(56), 218, -Math.PI / 2, font, BETSY_TEAL, '12px');
  hullText(ctx, 'CPA', w - X(56), 218, Math.PI / 2, font, BETSY_TEAL, '12px');
  // squarish cabin windows — the DC-3 has a short row of big panes
  ctx.fillStyle = '#20262c';
  for (const wx of [X(71), w - X(71)])
    for (let y = 360; y <= 880; y += 74) ctx.fillRect(wx - 6, y, 12, 22);
  // aft port cargo/pax door outline
  ctx.strokeStyle = 'rgba(70,80,90,0.5)'; ctx.lineWidth = 2;
  ctx.strokeRect(w - X(80), 900, X(26), 92);
}
// tapering rear fuselage: bands follow the shrinking radius; the big black
// registration rides the taper exactly as on the museum aircraft
function drawBetsyAft(ctx, w, h) {
  const img = ctx.createImageData(w, h), px = img.data;
  const C = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
  const cols = BETSY_HULL.map(C);
  for (let y = 0; y < h; y++) {
    const v = 1 - (y + 0.5) / h, r = 0.05 + 0.19 * v;  // radius shrinking to the tail
    for (let x = 0; x < w; x++) {
      const a = Math.min(x, w - x) / w * 2 * Math.PI;
      const yw = r * Math.cos(a);
      const c = cols[yw > 0.10 ? 0 : yw > -0.10 ? 1 : 2];
      const i = (y * w + x) * 4;
      px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; px[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  betsyPanels(ctx, w, h, 72);
  const font = 'italic bold 56px "Arial Black", Arial, sans-serif';
  hullText(ctx, 'VR-HDB', w * 0.25, 150, -Math.PI / 2, font, '#14181c', '3px');
  hullText(ctx, 'VR-HDB', w * 0.75, 150, Math.PI / 2, font, '#14181c', '3px');
}
// rounded nose: silver bands, the black anti-glare cap over the crown (widest
// at the tip, thinning back to the windscreen) and the DC-3's flat, stepped
// two-pane windscreen with its centre post. Same pole-forward unwrap as the
// jets: u wraps the hull (crown at ¼W), v runs tip → barrel joint.
function drawBetsyNose(ctx, w, h) {
  const img = ctx.createImageData(w, h), px = img.data;
  const C = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
  const cols = BETSY_HULL.map(C), glare = C('#1b1f24');
  for (let y = 0; y < h; y++) {
    const th = Math.PI * (y + 0.5) / h, sinT = Math.sin(th);
    for (let x = 0; x < w; x++) {
      const a = ((x + 0.5) / w - 0.25) * 2 * Math.PI;  // 0 at crown
      const yw = 0.24 * Math.cos(a) * sinT;            // world height on the sphere
      let c = cols[yw > 0.10 ? 0 : yw > -0.10 ? 1 : 2];
      // anti-glare cap: covers the upper nose ahead of the windscreen, wrapping
      // lowest right at the tip and pulling up toward the crown as it runs aft
      if (y < 98 && yw > 0.015 + 0.115 * (y / 98)) c = glare;
      const i = (y * w + x) * 4;
      px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; px[i + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);
  // stepped flat windscreen well aft of the tip, right where the crown meets
  // the cabin roof: two main panes + raked side quarter-panes
  const cx = w * 0.25;
  ctx.fillStyle = '#1c232a';
  ctx.fillRect(cx - 40, 100, 36, 26); ctx.fillRect(cx + 4, 100, 36, 26);   // mains, centre post between
  const quarter = (x0, x1, slant) => {                 // raked side panes
    ctx.beginPath();
    ctx.moveTo(x0, 104 + slant); ctx.lineTo(x1, 102);
    ctx.lineTo(x1, 126); ctx.lineTo(x0, 126 + slant * 0.5);
    ctx.closePath(); ctx.fill();
  };
  quarter(cx - 66, cx - 44, 6);
  ctx.save(); ctx.translate(2 * cx, 0); ctx.scale(-1, 1);
  quarter(cx - 66, cx - 44, 6);
  ctx.restore();
}
// fin/rudder side: silver, the rudder's fabric rib lines, and the Union Jack
// the museum aircraft carries near the top. mirror=true flips for starboard.
function drawBetsyFin(ctx, w, h, mirror) {
  if (mirror) { ctx.translate(w, 0); ctx.scale(-1, 1); }
  ctx.fillStyle = '#ccd2d8'; ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = 'rgba(40,50,60,0.22)'; ctx.lineWidth = 2;   // rudder hinge line
  ctx.beginPath(); ctx.moveTo(w * 0.55, 0); ctx.lineTo(w * 0.62, h); ctx.stroke();
  ctx.strokeStyle = 'rgba(40,50,60,0.12)';                      // fabric ribs on the rudder
  for (let x = w * 0.66; x < w * 0.97; x += w * 0.075) {
    ctx.beginPath(); ctx.moveTo(x, h * 0.10); ctx.lineTo(x - w * 0.03, h * 0.92); ctx.stroke();
  }
  // Union Jack: blue field, white + red diagonals, white + red cross
  const fx = w * 0.60, fy = h * 0.16, fw = w * 0.20, fh = h * 0.19;
  ctx.save();
  ctx.beginPath(); ctx.rect(fx, fy, fw, fh); ctx.clip();
  ctx.fillStyle = '#1f3f8f'; ctx.fillRect(fx, fy, fw, fh);
  ctx.strokeStyle = '#f2f4f6'; ctx.lineWidth = 7;
  ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(fx + fw, fy + fh);
  ctx.moveTo(fx + fw, fy); ctx.lineTo(fx, fy + fh); ctx.stroke();
  ctx.strokeStyle = '#c8322e'; ctx.lineWidth = 3;
  ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(fx + fw, fy + fh);
  ctx.moveTo(fx + fw, fy); ctx.lineTo(fx, fy + fh); ctx.stroke();
  ctx.strokeStyle = '#f2f4f6'; ctx.lineWidth = 11;
  ctx.beginPath(); ctx.moveTo(fx + fw / 2, fy); ctx.lineTo(fx + fw / 2, fy + fh);
  ctx.moveTo(fx, fy + fh / 2); ctx.lineTo(fx + fw, fy + fh / 2); ctx.stroke();
  ctx.strokeStyle = '#c8322e'; ctx.lineWidth = 6;
  ctx.beginPath(); ctx.moveTo(fx + fw / 2, fy); ctx.lineTo(fx + fw / 2, fy + fh);
  ctx.moveTo(fx, fy + fh / 2); ctx.lineTo(fx + fw, fy + fh / 2); ctx.stroke();
  ctx.restore();
}
// open-cowl radial engine face: dark well, a ring of finned cylinders around
// the crankcase, and the bare gear hub — the Twin Wasp stare of the photos
function drawBetsyEngine(ctx, w, h) {
  const cx = w / 2, cy = h / 2, r = w / 2;
  ctx.fillStyle = '#101418'; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.fill();
  for (let i = 0; i < 9; i++) {                        // nine radial cylinders
    const a = i / 9 * 2 * Math.PI - Math.PI / 2;
    const x1 = cx + 18 * Math.cos(a), y1 = cy + 18 * Math.sin(a);
    const x2 = cx + (r - 8) * Math.cos(a), y2 = cy + (r - 8) * Math.sin(a);
    ctx.strokeStyle = '#4c545c'; ctx.lineWidth = 11; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    ctx.strokeStyle = '#2b3238'; ctx.lineWidth = 11;   // cooling-fin shading stripe
    ctx.beginPath(); ctx.moveTo((x1 + x2) / 2, (y1 + y2) / 2); ctx.lineTo(x2, y2); ctx.stroke();
  }
  ctx.fillStyle = '#3a4148'; ctx.beginPath(); ctx.arc(cx, cy, 19, 0, 7); ctx.fill();   // crankcase
  ctx.strokeStyle = '#565e66'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, 19, 0, 7); ctx.stroke();
  ctx.fillStyle = '#20262c'; ctx.beginPath(); ctx.arc(cx, cy, 8, 0, 7); ctx.fill();    // gear hub
  ctx.strokeStyle = 'rgba(200,208,214,0.35)'; ctx.lineWidth = 2;                       // cowl lip glint
  ctx.beginPath(); ctx.arc(cx, cy, r - 2, 0, 7); ctx.stroke();
}
// nacelle cowl wrap: silver with panel seams and the exhaust's oil stain
// trailing under the belly (canvas x = around, y = along, top = front)
function drawBetsyCowl(ctx, w, h) {
  for (let x = 0; x < w; x++) {
    const a = Math.min(x, w - x) / w * 2 * Math.PI;
    ctx.fillStyle = Math.cos(a) < -0.4 ? '#a9b0b7' : '#cfd5da';
    ctx.fillRect(x, 0, 1, h);
  }
  ctx.strokeStyle = 'rgba(40,50,60,0.16)'; ctx.lineWidth = 1.5;
  for (const y of [h * 0.22, h * 0.5]) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
  ctx.fillStyle = 'rgba(30,34,38,0.20)';               // exhaust stain aft of the stack
  ctx.beginPath(); ctx.moveTo(w / 2 - 7, h * 0.4); ctx.lineTo(w / 2 + 7, h * 0.4);
  ctx.lineTo(w / 2 + 16, h); ctx.lineTo(w / 2 - 16, h); ctx.closePath(); ctx.fill();
}
// the DC-3 herself: twin radial engines with spinning three-blade props, low
// tapered wings with dihedral, tail-dragger gear (mains forward under the
// nacelles + a tailwheel) and the rounded swept fin. Same frame/scale as the
// other skins; props wired into the shared prop-spin + HKS-87 landed logic.
function buildBetsyDC3() {
  const s = 4;                                          // ~24 m span / ~16 m long at ×4
  const grp = new THREE.Group();
  const silver = new THREE.MeshStandardMaterial({ color: 0xd4d9de, roughness: 0.4, metalness: 0.3 });
  const dark   = new THREE.MeshStandardMaterial({ color: 0x22262b, roughness: 0.8 });
  const blade  = new THREE.MeshStandardMaterial({ color: 0x3a3e43, roughness: 0.6, metalness: 0.3 });
  const yellow = new THREE.MeshStandardMaterial({ color: 0xe8b73a, roughness: 0.6 });
  // fuselage: cabin barrel + rounded painted nose + the long tapering rear
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 1.9, 20),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 1024, drawBetsyBarrel), roughness: 0.35, metalness: 0.45 }));
  fus.rotation.x = -Math.PI / 2; fus.position.z = -0.4;   // z -1.35 … 0.55
  grp.add(fus);
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.24, 20, 14),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 256, drawBetsyNose), roughness: 0.35, metalness: 0.45 }));
  nose.rotation.x = -Math.PI / 2; nose.scale.set(1, 1.6, 1);
  nose.position.z = -1.35;                              // tip at ≈ -1.73
  grp.add(nose);
  const aft = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.045, 1.75, 20),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 512, drawBetsyAft), roughness: 0.35, metalness: 0.45 }));
  aft.rotation.x = -Math.PI / 2 - 0.05;                 // wide end forward, tip eased up
  aft.position.set(0, 0.02, 1.42);
  grp.add(aft);
  // low tapered wing with the DC-3's swept leading edge, mirrored for dihedral
  const wingMat = new THREE.MeshStandardMaterial({ map: wingTileTex(0.8), roughness: 0.35, metalness: 0.4, side: THREE.DoubleSide });
  const wingG = wingGeo(3.05, 1.05, 0.34, 0.85, 0.055, true);
  for (const sx of [-1, 1]) {
    const wg = new THREE.Mesh(wingG, wingMat);
    wg.scale.x = sx; wg.rotation.z = sx * 0.10;
    wg.position.set(0, -0.19, -0.5);
    grp.add(wg);
    // radial engine nacelle on the leading edge, its open cowl face + prop
    const ny = -0.13, nz = -0.82;
    const nac = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.14, 0.85, 16),
      new THREE.MeshStandardMaterial({ map: canvasTex(256, 128, drawBetsyCowl), roughness: 0.35, metalness: 0.45 }));
    nac.rotation.x = -Math.PI / 2; nac.position.set(sx * 0.8, ny, nz);
    grp.add(nac);
    const face = new THREE.Mesh(new THREE.CircleGeometry(0.152, 18),
      new THREE.MeshStandardMaterial({ map: canvasTex(128, 128, drawBetsyEngine), roughness: 0.6 }));
    face.rotation.y = Math.PI;                          // face forward (-z)
    face.position.set(sx * 0.8, ny, nz - 0.43);
    grp.add(face);
  }
  // three-blade props with yellow tips, one per engine — stepFlight spins
  // everything in userData.props with the shared HKS-87 landed behaviour
  const props = [];
  for (const sx of [-1, 1]) {
    const prop = new THREE.Group();
    for (let i = 0; i < 3; i++) {
      const arm = new THREE.Group();
      arm.rotation.z = i * 2 * Math.PI / 3;
      const bl = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.34, 0.022), blade);
      bl.position.y = 0.21;
      arm.add(bl);
      const tip = new THREE.Mesh(new THREE.BoxGeometry(0.052, 0.06, 0.024), yellow);
      tip.position.y = 0.37;
      arm.add(tip);
      prop.add(arm);
    }
    const hub = new THREE.Mesh(new THREE.SphereGeometry(0.05, 10, 8), dark);
    hub.scale.z = 1.4;
    prop.add(hub);
    prop.position.set(sx * 0.8, -0.13, -1.30);
    grp.add(prop);
    props.push(prop);
  }
  grp.userData.props = props;
  // tailplane + the rounded swept fin with painted sides (Union Jack up top)
  const tailW = new THREE.Mesh(wingGeo(1.05, 0.52, 0.20, 0.4, 0.045), wingMat);
  tailW.position.set(0, 0.05, 1.72);
  grp.add(tailW);
  const finPts = [[0, 0.05], [1.02, 0], [1.10, 0.28], [1.04, 0.46], [0.88, 0.58],
                  [0.66, 0.62], [0.44, 0.56], [0.24, 0.40], [0.08, 0.18]];
  const fin = new THREE.Mesh(finGeo(finPts, 0.05), silver);
  fin.position.set(0, 0.10, 1.18);
  grp.add(fin);
  const finShape = new THREE.Shape();
  finShape.moveTo(finPts[0][0], finPts[0][1]);
  for (let i = 1; i < finPts.length; i++) finShape.lineTo(finPts[i][0], finPts[i][1]);
  finShape.closePath();
  const finSideG = new THREE.ShapeGeometry(finShape);
  finSideG.rotateY(-Math.PI / 2);                      // faces -x (port)
  for (const sx of [-1, 1]) {
    const tex = canvasTex(320, 256, (c, w2, h2) => drawBetsyFin(c, w2, h2, sx === 1));
    tex.repeat.set(1 / 1.10, 1 / 0.62);                // shape UVs are raw metres
    const side = new THREE.Mesh(finSideG, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.45, metalness: 0.15 }));
    if (sx === 1) side.scale.x = -1;                   // starboard: mirrored geometry + art
    side.position.set(sx * 0.028, 0.10, 1.18);
    grp.add(side);
  }
  // tail-dragger gear: main wheels half-hung under the nacelles ahead of the
  // wing + the little tailwheel — grouped so stepFlight retracts it in flight
  const gear = new THREE.Group();
  for (const sx of [-1, 1]) {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.28, 0.07), dark);
    leg.position.set(sx * 0.8, -0.30, -0.60);
    gear.add(leg);
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.10, 14), dark);
    wheel.rotation.z = Math.PI / 2; wheel.position.set(sx * 0.8, -0.42, -0.60);
    gear.add(wheel);
  }
  const tStrut = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.14, 0.03), dark);
  tStrut.position.set(0, -0.15, 1.94);
  gear.add(tStrut);
  const tWheel = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.045, 10), dark);
  tWheel.rotation.z = Math.PI / 2; tWheel.position.set(0, -0.23, 1.96);
  gear.add(tWheel);
  grp.add(gear);
  grp.userData.gear = gear;
  // Cockpit (HKS-93): the classic prop-era six-pack, re-registered VR-HDB —
  // REAL METRES around the eye at ~(0, 1.35, -4.4) looking down -z
  const cock = new THREE.Group();
  const trim = new THREE.MeshStandardMaterial({ color: 0x101317, roughness: 0.95 });
  const panelMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(512, 224, (c, w2, h2) => drawPropPanel(c, w2, h2, 'VR-HDB')) }), trim];
  const panel = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.75, 0.16), panelMats);
  panel.position.set(0, 0.97, -5.45); panel.rotation.x = 0.40;   // top edge well below the 1.6 m eye
  cock.add(panel);
  const glare = new THREE.Mesh(new THREE.BoxGeometry(2.9, 0.16, 0.55), trim);
  glare.position.set(0, 1.38, -5.30); glare.rotation.x = -0.10;  // the coaming the nose peeks over
  cock.add(glare);
  const cpost = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.1, 0.10), trim);   // the DC-3 centre post
  cpost.position.set(0, 2.0, -5.65); cpost.rotation.x = 0.10;
  cock.add(cpost);
  for (const sx of [-1, 1]) {
    const p = new THREE.Mesh(new THREE.BoxGeometry(0.12, 2.0, 0.12), trim);
    p.position.set(sx * 1.25, 1.85, -5.35); p.rotation.z = sx * 0.35;
    cock.add(p);
  }
  cock.scale.setScalar(1 / s);
  cock.visible = false;
  grp.add(cock);
  grp.userData.cockpit = cock;
  grp.userData.povFwd = 4.4; grp.userData.povUp = 1.6;    // cockpit eye right behind the windscreen,
  grp.userData.povPitch = -0.09;                          // high enough that the nose stays past the coaming
  grp.userData.eyeFwd = 4.4; grp.userData.eyeUp = 1.6;    // 👁 eye: the short nose sits low in the frame
  // nav lights: wingtips, tail cone, beacons on the crown & belly
  addNavLights(grp, { wingL: [-2.95, 0.10, 0.62], wingR: [2.95, 0.10, 0.62],
                      tail: [0, 0.05, 2.32], top: [0, 0.32, -0.2], bot: [0, -0.30, -0.2] });
  grp.scale.setScalar(s);
  grp.visible = false;
  return grp;
}
// ---- Cathay Pacific Airbus A350-1000 (HKS-93) -------------------------------
// The modern flagship twin, painted from the B-LXA reference photos at HKG:
// clean white hull with big jade titles + the brushwing glyph forward, grey
// belly, the black Airbus cockpit mask, TWO very large white turbofans, and
// the A350's signature upturned wingtips. Modern (no red stripe) jade fin.
function drawCxA350Barrel(ctx, w, h) {
  for (let x = 0; x < w; x++) {                        // base bands per column
    const a = Math.min(x, w - x) / w * 2 * Math.PI;    // angle from the crown
    ctx.fillStyle = cxHull(0.28 * Math.cos(a));
    ctx.fillRect(x, 0, 1, h);
  }
  const X = a => a / 360 * w;                          // degrees-from-crown → px
  // faint frame/panel lines under everything
  ctx.strokeStyle = 'rgba(20,30,40,0.05)'; ctx.lineWidth = 1;
  for (let y = 75; y < h; y += 75) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke(); }
  // doors: outlined at the window line, windows skip around them
  const doors = [115, 340, 580, 820, 970];
  ctx.strokeStyle = 'rgba(90,100,110,0.55)'; ctx.lineWidth = 1.5;
  for (const wx of [X(72.5), w - X(72.5)])
    for (const dy of doors) { ctx.strokeRect(wx - 14, dy - 12, 28, 24); ctx.fillStyle = CX_WIN; ctx.fillRect(wx - 4, dy - 3, 8, 6); }
  // one long clean window row — no cheatline on the 2015 livery
  ctx.fillStyle = CX_WIN;
  for (const wx of [X(72.5), w - X(72.5)])
    for (let y = 60; y < 1000; y += 12) {
      if (doors.some(d => Math.abs(y - d) < 20)) continue;
      ctx.fillRect(wx - 4, y, 8, 6);
    }
  // big jade titles forward + the little jade brushwing glyph trailing them
  const font = 'bold 30px "Helvetica Neue", Arial, sans-serif';
  hullText(ctx, 'CATHAY PACIFIC', X(42), 265, -Math.PI / 2, font, CX_JADE, '4px');
  hullText(ctx, 'CATHAY PACIFIC', w - X(42), 265, Math.PI / 2, font, CX_JADE, '4px');
  const brush = (bx, by, mirror) => {                  // the brushwing mark aft of the titles
    ctx.save(); ctx.translate(bx, by); ctx.rotate(mirror ? Math.PI / 2 : -Math.PI / 2);
    if (mirror) ctx.scale(-1, 1);                      // the stroke sweeps the same way per side
    ctx.strokeStyle = CX_JADE; ctx.lineCap = 'round'; ctx.lineWidth = 8;
    ctx.beginPath(); ctx.moveTo(16, -13); ctx.quadraticCurveTo(4, 2, -6, 8); ctx.stroke();
    ctx.fillStyle = CX_JADE;
    ctx.beginPath(); ctx.moveTo(0, 4);
    ctx.quadraticCurveTo(-14, 13, -25, 12); ctx.quadraticCurveTo(-11, 5, -3, -3);
    ctx.closePath(); ctx.fill();
    ctx.restore();
  };
  brush(X(42), 448, false); brush(w - X(42), 448, true);
  // registration near the tail
  const rfont = 'bold 13px Arial, sans-serif';
  hullText(ctx, 'B-LXA', X(38), 985, -Math.PI / 2, rfont, '#5c666e');
  hullText(ctx, 'B-LXA', w - X(38), 985, Math.PI / 2, rfont, '#5c666e');
}
function buildCXA350() {
  const s = 4;                                          // the -1000: as long and lean as the 777
  const grp = new THREE.Group();
  const white = new THREE.MeshStandardMaterial({ color: 0xf2f5f7, roughness: 0.4, metalness: 0.2 });
  const jade  = new THREE.MeshStandardMaterial({ color: 0x00655b, roughness: 0.5, metalness: 0.15 });
  const grey  = new THREE.MeshStandardMaterial({ color: 0xd6dade, roughness: 0.45, metalness: 0.25 });
  const dark  = new THREE.MeshStandardMaterial({ color: 0x22282e, roughness: 0.7 });
  // the long clean single-deck barrel
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 4.4, 24),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 1024, drawCxA350Barrel), roughness: 0.4, metalness: 0.15 }));
  fus.rotation.x = -Math.PI / 2; fus.position.z = 0.1;   // z -2.1 … 2.3
  grp.add(fus);
  // curved Airbus nose wearing the black cockpit mask, pole-forward unwrap
  const nose = new THREE.Mesh(new THREE.SphereGeometry(0.28, 24, 16),
    new THREE.MeshStandardMaterial({ map: canvasTex(512, 256, (c, w2, h2) => drawCxNose(c, w2, h2, 'a350')), roughness: 0.4, metalness: 0.15 }));
  nose.rotation.x = -Math.PI / 2; nose.scale.set(1, 1.9, 1);   // the A350 nose is blunter than the 777's
  nose.position.z = -2.08;
  grp.add(nose);
  // long tail cone, tip swept slightly up, nosed into the barrel
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.04, 1.8, 24),
    new THREE.MeshStandardMaterial({ map: canvasTex(256, 256, drawCxTail), roughness: 0.4, metalness: 0.15 }));
  tail.rotation.x = -Math.PI / 2 - 0.08;
  tail.position.set(0, 0.055, 3.14);
  grp.add(tail);
  // wing-root belly fairing (same trick as the 777 — wings grow from the hull)
  const fairing = new THREE.Mesh(new THREE.SphereGeometry(0.28, 20, 12),
    new THREE.MeshStandardMaterial({ color: 0xb2bbc2, roughness: 0.45, metalness: 0.2 }));
  fairing.scale.set(1.25, 0.62, 2.4);
  fairing.position.set(0, -0.10, 0.15);
  grp.add(fairing);
  // swept wings; the tip run curves gently aft, then the upturned winglet —
  // the A350's scimitar tip — cants ~35° off vertical from the very tip
  const wingMat = new THREE.MeshStandardMaterial({ map: wingTileTex(0.7), roughness: 0.4, metalness: 0.2, side: THREE.DoubleSide });
  const wShape = new THREE.Shape();                     // half-wing, root at x 0
  wShape.moveTo(0, 0);
  wShape.lineTo(2.55, 1.42);                            // leading edge out…
  wShape.quadraticCurveTo(2.82, 1.60, 2.92, 1.86);      // …easing aft into the tip
  wShape.lineTo(2.92, 2.02);
  wShape.quadraticCurveTo(2.6, 1.86, 2.3, 1.68);        // trailing edge curves back in
  wShape.lineTo(0, 1.08);
  wShape.closePath();
  const wingG = new THREE.ExtrudeGeometry(wShape, { depth: 0.06, bevelEnabled: false, curveSegments: 8 });
  wingG.rotateX(Math.PI / 2);
  const wingletG = finGeo([[0, 0], [0.30, 0], [0.46, 0.34], [0.36, 0.36]], 0.045);
  for (const sx of [-1, 1]) {
    const wg = new THREE.Mesh(wingG, wingMat);
    wg.scale.x = sx; wg.rotation.z = sx * 0.10;        // mirrored halves → dihedral
    wg.position.set(0, -0.15, -0.35);
    grp.add(wg);
    // the upturned tip: a swept blade rising from the tip chord, canted outward
    const wl = new THREE.Mesh(wingletG, white);
    wl.position.set(sx * 2.89, 0.14, 1.52);            // base on the (dihedralled) tip
    wl.rotation.z = -sx * 0.62;                        // top leans outboard — the scimitar cant
    grp.add(wl);
    // ONE very large turbofan per side, white nacelle with the dark inlet lip
    const ex = 1.0, ey = -0.28, ez = -0.15;
    const nac = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.155, 0.75, 16), grey);
    nac.rotation.x = -Math.PI / 2; nac.position.set(sx * ex, ey, ez);
    grp.add(nac);
    const lip = new THREE.Mesh(new THREE.TorusGeometry(0.162, 0.02, 10, 18), dark);
    lip.position.set(sx * ex, ey, ez - 0.375);         // the A350's black intake ring
    grp.add(lip);
    const fan = new THREE.Mesh(new THREE.CircleGeometry(0.155, 20),
      new THREE.MeshStandardMaterial({ map: canvasTex(128, 128, drawCxFan), roughness: 0.6 }));
    fan.rotation.y = Math.PI;                          // face forward (-z)
    fan.position.set(sx * ex, ey, ez - 0.365);
    grp.add(fan);
    const exh = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.088, 0.30, 16), grey);
    exh.rotation.x = -Math.PI / 2; exh.position.set(sx * ex, ey, ez + 0.52);
    grp.add(exh);
    const core = new THREE.Mesh(new THREE.ConeGeometry(0.055, 0.22, 12), dark);
    core.rotation.x = Math.PI / 2;
    core.position.set(sx * ex, ey, ez + 0.72);
    grp.add(core);
    // pylon bridging nacelle crown → wing underside, one connected structure
    const pylon = new THREE.Mesh(finGeo([[-0.30, 0], [0.50, 0], [0.50, 0.09], [0.05, 0.09]], 0.075), white);
    pylon.position.set(sx * ex, -0.16, ez + 0.12);
    grp.add(pylon);
  }
  // tailplane + the tall fin carrying the modern brushwing (deep jade, no red)
  const tailW = new THREE.Mesh(wingGeo(1.2, 0.55, 0.18, 0.6, 0.05), wingMat);
  tailW.position.set(0, 0.10, 3.02);
  grp.add(tailW);
  const finPts = [[0.10, 0], [1.05, 0], [1.40, 1.12], [1.07, 1.12]];
  const fin = new THREE.Mesh(finGeo(finPts, 0.07), jade);
  fin.position.set(0, 0.13, 2.52);
  grp.add(fin);
  const finShape = new THREE.Shape();
  finShape.moveTo(0.10, 0); finShape.lineTo(1.05, 0);
  finShape.lineTo(1.40, 1.12); finShape.lineTo(1.07, 1.12);
  finShape.closePath();
  const finSideG = new THREE.ShapeGeometry(finShape);
  finSideG.rotateY(-Math.PI / 2);                      // faces -x (port)
  for (const sx of [-1, 1]) {
    const tex = canvasTex(320, 256, (c, w2, h2) => drawCxFin(c, w2, h2, sx === 1, false));
    tex.repeat.set(1 / 1.40, 1 / 1.12);                // shape UVs are raw metres
    const side = new THREE.Mesh(finSideG, new THREE.MeshStandardMaterial({ map: tex, roughness: 0.5 }));
    if (sx === 1) side.scale.x = -1;                   // starboard: mirrored geometry + art
    side.position.set(sx * 0.041, 0.13, 2.52);
    grp.add(side);
  }
  // gear: nose strut + two main bogies (wheels reach y = -0.55), grouped so
  // stepFlight can retract it — wheels only show on the ground
  const gear = new THREE.Group();
  const gearAt = (x, z) => {
    const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.26, 0.06), dark);
    leg.position.set(x, -0.34, z);
    gear.add(leg);
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.095, 0.095, 0.16, 12), dark);
    wheel.rotation.z = Math.PI / 2; wheel.position.set(x, -0.455, z);
    gear.add(wheel);
  };
  gearAt(0, -1.85); gearAt(-0.3, 0.35); gearAt(0.3, 0.35);
  grp.add(gear);
  grp.userData.gear = gear;
  // Flight deck (glass cockpit): the 777 treatment — big-LCD main panel + MCP
  // glareshield + windscreen frame. REAL METRES around the eye at ~(0, 2.4, -2.8)
  const cock = new THREE.Group();
  const trim = new THREE.MeshStandardMaterial({ color: 0x15181c, roughness: 0.85 });
  const post = new THREE.MeshStandardMaterial({ color: 0x20242a, roughness: 0.7 });
  const panelMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(1024, 320, drawCxPanel) }), trim];
  const panel = new THREE.Mesh(new THREE.BoxGeometry(5.2, 1.6, 0.3), panelMats);
  panel.position.set(0, 1.22, -4.75); panel.rotation.x = 0.42;
  cock.add(panel);
  const glareMats = [trim, trim, trim, trim,
    new THREE.MeshBasicMaterial({ map: canvasTex(1024, 64, drawCxMCP) }), trim];
  const glare = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.34, 0.42), glareMats);
  glare.position.set(0, 2.02, -4.55); glare.rotation.x = -0.18;
  cock.add(glare);
  const header = new THREE.Mesh(new THREE.BoxGeometry(5.6, 0.32, 0.3), post);
  header.position.set(0, 3.9, -5.6);
  cock.add(header);
  const cpost = new THREE.Mesh(new THREE.BoxGeometry(0.16, 1.9, 0.22), post);
  cpost.position.set(0, 3.1, -5.6);
  cock.add(cpost);
  for (const sx of [-1, 1]) {
    const side = new THREE.Mesh(new THREE.BoxGeometry(0.26, 3.6, 0.26), post);
    side.position.set(sx * 2.7, 2.8, -5.2); side.rotation.z = sx * 0.34;
    cock.add(side);
  }
  cock.scale.setScalar(1 / s);                          // cancel the ×4 so the metres are literal
  cock.visible = false;
  grp.add(cock);
  grp.userData.cockpit = cock;
  grp.userData.povFwd = 2.8; grp.userData.povUp = 2.4;   // cockpit eye ahead of the wing
  grp.userData.eyeFwd = 5.8; grp.userData.eyeUp = 2.5;   // 👁 eye near the nose — no snout in frame
  // nav lights: winglet tops, tail cone, beacons on the crown & belly
  addNavLights(grp, { wingL: [-3.10, 0.44, 1.93], wingR: [3.10, 0.44, 1.93],
                      tail: [0, 0.13, 4.02], top: [0, 0.31, 0.1], bot: [0, -0.31, 0.1] });
  grp.scale.setScalar(s);
  grp.visible = false;
  return grp;
}
function enterFlight() {
  if (flight.on || !curG) return;
  if (walk.on) exitWalk();
  if (stargaze.on) exitStargaze();
  flight.on = true;
  flight.prevSpin = spinDir; spinDir = 0;              // the world holds still while you fly
  syncSpinSeg();
  if (!planeGrp) { planeGrp = buildPlane(); world.add(planeGrp); }
  loadPlaneModel(planeSkin);   // HKS-110: swap in the real airframe once it arrives
  planeGrp.visible = true;
  applyLookFilter(planeGrp);   // HKS-104: spawn already dressed for Matrix/Neon (no-op otherwise)
  // HKS-93: a remembered cockpit view can't survive onto a skin with no flight deck
  if (flight.view === 'cockpit' && !planeGrp.userData.cockpit) flight.view = 'eye';
  const b = bounds(), g = curG;
  // start LANDED on the HKIA runway (Chek Lap Kok), facing east toward Kowloon —
  // hold-to-gas / ␣ / a tap rolls you down the runway and lifts off (HKS-73).
  // If the airport falls outside this source's extent, fall back to an airborne
  // cruise spawn over the map centre.
  let col = (809897 - g.bE) / g.aE, row = (818635 - g.bN) / g.aN;
  const onRunway = col >= 0 && col <= W - 1 && row >= 0 && row <= H - 1;
  if (onRunway) {
    flight.pos.set((col - W/2) * cell, sampleE(col, row) * VE + 2.2, (row - H/2) * cell);
    flight.speed = 0;                                  // engine idle on the tarmac
    flight.landed = true;
  } else {
    col = W / 2; row = H / 2;
    flight.pos.set((col - W/2) * cell, sampleE(col, row) * VE + 400 * VE, (row - H/2) * cell);
    flight.speed = 62;                                 // m/s — light-aircraft cruise (~120 kt)
    flight.landed = false;
  }
  flight.yaw = -Math.PI / 2;                           // east — down the runway toward Kowloon
  flight.pitch = 0; flight.roll = 0;
  flight.helpT = 480;                                  // show the how-to card for ~8 s
  flight.tilt = false; flight.tiltRef = null;
  // phones fly by tilting — ask iOS for the sensor from this tap's gesture
  if (matchMedia('(pointer: coarse)').matches && typeof DeviceOrientationEvent !== 'undefined') {
    const arm = () => { flight.tilt = true; flight.tiltRef = null; };
    if (typeof DeviceOrientationEvent.requestPermission === 'function')
      DeviceOrientationEvent.requestPermission().then(s => { if (s === 'granted') arm(); }).catch(() => {});
    else arm();
  }
  document.getElementById('flybtn').classList.add('on');
  document.getElementById('flybtn').blur();   // else Space (boost!) re-clicks the button and exits
  document.body.classList.add('flying');
  setTopMode('fly');
  updateViewBtn();
  controls.enabled = false;
  // HKS-86 §2: GPS follow/compass never persists outside Orbit — entering a
  // movement mode spawns at the fix (if it's on this map), then disengages
  if (geo.following || geo.compass) { if (geoInBounds()) teleportToMarker(); gpsDrop(); }   // spawn at the fix, then turn GPS fully off
  refreshDock();
  track('mode_enter', { mode: 'fly' });
}
function exitFlight() {
  if (!flight.on) return;
  flight.on = false;
  flight.keys = {};
  flight.touchHold = 0; flight.mouseLook = false; flight.lookYaw = 0; flight.lookPitch = 0;   // HKS-53
  if (planeGrp) planeGrp.visible = false;
  document.getElementById('flybtn').classList.remove('on');
  spinDir = flight.prevSpin;
  syncSpinSeg();
  setEngine(0);
  setTopMode(null);
  updateSpeedGauge();                                 // park the gauge at —
  camera.up.set(0, 1, 0);
  camera.fov = 38; camera.updateProjectionMatrix();   // back to the map's telephoto look
  controls.enabled = true;
  document.body.classList.remove('flying');
  updateViewBtn();
  frameCamera();
  refreshDock();
  track('mode_exit', { mode: 'fly' });
}
// the camera control beside the compass mirrors the C key — in Fly it cycles
// 🎥 chase → 👁 eye (clean first person) → 🧑‍✈️ cockpit (interior), skipping
// cockpit on any skin without a built flight deck (HKS-93)
function updateViewBtn() { syncCamSeg(); }   // fly camera state reflects in the segmented control
function flyViews() {
  return (planeGrp && planeGrp.userData.cockpit) ? ['chase', 'eye', 'cockpit'] : ['chase', 'eye'];
}
function toggleView() {
  if (!flight.on) return;
  const order = flyViews();                 // indexOf -1 (stale cockpit) cycles back to chase
  setFlightView(order[(order.indexOf(flight.view) + 1) % order.length]);
}
function setFlightView(v) {
  if (!flight.on) return;
  if (v === 'cockpit' && !(planeGrp && planeGrp.userData.cockpit)) v = 'eye';   // no flight deck → clean eye
  flight.view = v;
  camera.up.set(0, 1, 0);
  updateViewBtn();
  track('camera_view', { view: v, mode: 'fly' });
}
document.getElementById('flybtn').addEventListener('click', () => flight.on ? exitFlight() : enterFlight());
// top-speed slider — shared by fly and walk (William: one control, reset on
// mode switch, disabled outside both). It sets what the boost key accelerates
// to: ␣ in flight (knots), ⇧ on foot (km/h — the top end is frankly
// superhuman). Stored in real m/s on the mode's own object.
const TOPSPD = {
  fly:  { min: 130, max: 600, step: 2, def: 214, unit: 'kt',   toMS: v => v / 1.944 },
  walk: { min: 6,   max: 100, step: 1, def: 24,  unit: 'km/h', toMS: v => v / 3.6 },
};
let topMode = null;                                   // null | 'fly' | 'walk'
function setTopMode(mode) {
  topMode = mode;
  const el = document.getElementById('topspd');
  el.disabled = !mode;
  if (!mode) { document.getElementById('topspdv').textContent = '—'; return; }
  const c = TOPSPD[mode];
  el.min = c.min; el.max = c.max; el.step = c.step;
  el.value = c.def;                                   // reset on every mode switch
  applyTopSpeed(c.def);
}
function applyTopSpeed(v) {
  if (!topMode) return;
  const c = TOPSPD[topMode];
  if (topMode === 'fly') flight.top = c.toMS(v); else walk.top = c.toMS(v);
  document.getElementById('topspdv').textContent = `${v} ${c.unit}`;
}
document.getElementById('topspd').addEventListener('input',
  e => applyTopSpeed(+e.target.value));
function updateSpeedGauge() {
  const fill = document.getElementById('spdfill'), pct = document.getElementById('spdpct');
  let p = null, hot = false, label = '—';
  if (flight.on) {
    p = 100 * flight.speed / flight.top;
    hot = p >= 97;
    label = `${Math.round(flight.speed * 1.944)} kt`;          // real airspeed, not %
  } else if (walk.on) {
    p = 100 * walk.spd / walk.top;
    if (walk.spd > 0.2)                               // a human gait is never a steady needle
      p *= 1 + Math.sin(walk.bob * 2.1) * 0.05 + (Math.random() - 0.5) * 0.05;
    hot = p >= 90;
    label = `${Math.round(walk.spd * 3.6)} km/h`;              // real pace, not %
  }
  if (p == null) { fill.style.width = '0%'; pct.textContent = '—'; fill.classList.remove('hot'); return; }
  p = Math.max(0, Math.min(100, p));
  fill.style.width = p.toFixed(1) + '%';                       // the bar still fills by % of top speed
  pct.textContent = label;                                    // the readout shows the actual speed + unit
  fill.classList.toggle('hot', hot);                  // redline glow at full gas
}
// Resolve the LOGICAL key from the physical e.code first: with a CJK/IME input
// source active, letter keydowns arrive as e.key === 'Process' and WASD would
// never register (arrows pass through IMEs, which is why flight seemed fine).
// e.code names the physical key regardless of layout or composition state.
function keyOf(e) {
  const c = e.code || '';
  if (c.startsWith('Key')) return c.slice(3).toLowerCase();
  if (c.startsWith('Arrow')) return c.toLowerCase();
  if (c === 'Space') return ' ';
  if (c.startsWith('Shift')) return 'shift';
  if (c.startsWith('Control')) return 'control';
  return (e.key || '').toLowerCase();
}
addEventListener('keydown', e => {
  if (walk.on) {
    if (e.key === 'Escape') { exitWalk(); return; }
    if (keyOf(e) === 'c') { toggleWalkView(); return; }
    walk.keys[keyOf(e)] = true;
    if (e.code.startsWith('Arrow') || e.code === 'Space') e.preventDefault();
    return;
  }
  if (!flight.on) return;
  if (e.key === 'Escape') { exitFlight(); return; }
  if (keyOf(e) === 'c') { toggleView(); return; }
  flight.keys[keyOf(e)] = true;
  if (e.code.startsWith('Arrow') || e.code === 'Space') e.preventDefault();
});
addEventListener('keyup', e => {
  flight.keys[keyOf(e)] = false;
  walk.keys[keyOf(e)] = false;
});
addEventListener('deviceorientation', e => {           // phone tilt = the stick
  if (!flight.on || !flight.tilt || e.beta == null) return;
  if (flight.tiltRef == null) flight.tiltRef = e.beta;  // first reading calibrates neutral
  flight.tiltBeta = e.beta; flight.tiltGamma = e.gamma || 0;
});
document.getElementById('flyhud').addEventListener('click', e => {   // touch affordances in the HUD
  if (e.target.dataset.fly === 'exit') { exitFlight(); exitWalk(); }
  else if (e.target.dataset.fly === 'takeoff') takeOff();
  else if (e.target.dataset.fly === 'view') toggleView();
  else if (e.target.dataset.fly === 'autowalk') { walk.auto = !walk.auto; track('auto_walk', { on: walk.auto }); }
});
const FLY_DEBUG = new URLSearchParams(location.search).has('debug');
if (FLY_DEBUG) {   // automated-test handles; the flag survives URL re-serialization
  window.__flight = flight;
  window.__stepFlight = () => stepFlight();
  window.__three = () => ({ renderer, scene, camera, sun, hemi, terrain, sea, tidalMats });
  // HKS-108: drape-sampler handles — verify overlays sit on the rendered triangle surface
  window.__drape = { sampleE: (c, r) => sampleE(c, r), sampleEtri: (c, r) => sampleEtri(c, r),
    skinOffset: () => skinOffset(), get VE() { return VE; }, get skinLift() { return skinLift; },
    get W() { return W; }, get H() { return H; }, get cell() { return cell; },
    get meshStep() { return meshStep; }, get elev() { return elev; }, get skin() { return skin; } };
  // sky handles: unit-test the eclipse coverage math, force a coverage value
  // (holds until the next sim-minute cel refresh), read the live sky luminance
  window.__sky = { eclipseCoverage, S01,
    get cel() { return cel; }, get skyLum() { return skyLum; },
    get starFade() { return starUniforms.uFade.value; },
    setEclipse: v => { if (cel) { cel.eclipse = v; renderSky(); setFog(); } } };
}

const _fq = new THREE.Quaternion(), _fe = new THREE.Euler(), _fv = new THREE.Vector3();
const _fc = new THREE.Vector3(), _fl = new THREE.Vector3(), _fu = new THREE.Vector3();
const _sgF = new THREE.Vector3(), _sgR = new THREE.Vector3();   // stargaze surface-pan basis (HKS-90)
// HKS-53: temps for the cockpit head-turn (plane orientation × look offset)
const _fq2 = new THREE.Quaternion(), _lookQ = new THREE.Quaternion(), _fe2 = new THREE.Euler(), _fv2 = new THREE.Vector3();
const CARD = ['N','NE','E','SE','S','SW','W','NW'];
const wrapPI = a => ((a + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;
function stepFlight() {
  if (!flight.on) return;
  const b = bounds(), F = flight, K = F.keys;
  // --- stick: keyboard, or phone tilt when armed (speeds are real m/s at 60 fps)
  let pIn = (K['arrowup'] || K['w'] ? 1 : 0) - (K['arrowdown'] || K['s'] ? 1 : 0);
  let rIn = (K['arrowright'] || K['d'] ? 1 : 0) - (K['arrowleft'] || K['a'] ? 1 : 0);
  const tIn = (K['shift'] || K['e'] ? 1 : 0) - (K['control'] || K['q'] ? 1 : 0);
  if (F.tilt && F.tiltRef != null) {
    pIn = Math.max(-1, Math.min(1, (F.tiltBeta - F.tiltRef) / 22));   // tilt forward = dive
    rIn = Math.max(-1, Math.min(1, F.tiltGamma / 25));                // tilt sideways = bank
  }
  F.pitch = Math.max(-0.55, Math.min(0.55, F.pitch + pIn * 0.007 - F.pitch * 0.012));
  F.roll  = Math.max(-1.0, Math.min(1.0, F.roll + rIn * 0.02 - F.roll * 0.025));
  // --- out of bounds: within the buffer a gentle hand banks you back to the map
  const overX = Math.abs(F.pos.x) - b.halfX, overZ = Math.abs(F.pos.z) - b.halfZ;
  const over = Math.max(overX, overZ), BUF = b.span * 0.18;
  if (over > 0) {
    const dyaw = wrapPI(Math.atan2(F.pos.x, F.pos.z) - F.yaw);        // heading toward centre
    const grip = Math.min(1, over / BUF);
    F.yaw += dyaw * grip * 0.005;                                     // a wide, patient arc
    F.roll += Math.max(-1, Math.min(1, -dyaw)) * grip * 0.010;        // lean into the guided turn
  }
  F.yaw -= F.roll * 0.0016;                            // full bank ≈ 5.5°/s — a real, patient turn
  if (windStrength > 0.15) {                           // turbulence rattles the stick
    F.pitch += (Math.random() - 0.5) * 0.006 * windStrength;
    F.roll  += (Math.random() - 0.5) * 0.010 * windStrength;
  }
  if (!F.landed) {
    F.speed = Math.max(28, Math.min(F.top, F.speed + tIn * 0.3 - (F.speed - 62) * 0.001));
    if (K[' '] || F.touchHold > 0) F.speed = Math.min(F.top, F.speed + 0.8); // ␣ or a held finger steps on the gas (HKS-53)
  }
  _fe.set(F.pitch, F.yaw, -F.roll * 0.9, 'YXZ');       // right bank = right wing down
  _fq.setFromEuler(_fe);
  _fv.set(0, 0, -1).applyQuaternion(_fq);
  const mpf = F.speed / 60;                            // metres per frame
  F.pos.x += _fv.x * mpf;
  F.pos.z += _fv.z * mpf;
  F.pos.y += _fv.y * mpf * VE;                         // climb in exaggerated y: slopes fly true
  F.pos.y -= Math.max(0, 62 - F.speed) * 0.004 * VE;   // below cruise the nose gets heavy
  if (!F.landed) {                                     // parked on the runway you don't drift downwind
    F.pos.x += windVec.x * (25 * windStrength) / 60;   // a full gale drifts you ~25 m/s
    F.pos.z += windVec.z * (25 * windStrength) / 60;
  }
  F.pos.x = Math.max(-(b.halfX + BUF), Math.min(b.halfX + BUF, F.pos.x));
  F.pos.z = Math.max(-(b.halfZ + BUF), Math.min(b.halfZ + BUF, F.pos.z));
  F.pos.y = Math.min(F.pos.y, 4000 * VE);              // service ceiling
  // --- touch the ground or the water and you LAND: wheels down, roll out to a
  // stop, then ␣ / a tap / the HUD button lifts you off again
  const col = F.pos.x / cell + W / 2, row = F.pos.z / cell + H / 2;
  const gy = (col >= 0 && col <= W - 1 && row >= 0 && row <= H - 1 ? sampleE(col, row) : 0) * VE;
  const surfY = Math.max(gy, sea && sea.visible ? sea.position.y : -Infinity);
  const agl = (F.pos.y - surfY) / VE;                  // real metres above ground/water
  if (F.landed) {
    F.speed = Math.max(0, F.speed - 1.5);              // roll-out braking
    F.pitch *= 0.8; F.roll *= 0.75;                    // settle level on the gear
    F.pos.y = surfY + 2.2;
    if (K[' ']) takeOff();   // ␣ launches; a tap/🛫 launches too. Holding no longer auto-launches so you can drag to look at the parked plane; touchHold still feeds the gas once airborne (HKS-53)
  } else if (agl < 4 && _fv.y <= 0.02) {               // only while descending — a fresh
    F.landed = true;                                   // climb-out stays airborne
    F.pitch = Math.max(0, F.pitch * 0.3); F.roll *= 0.5;
    F.pos.y = surfY + 2.2;
    flash = Math.max(flash, 0.15);                     // a soft touchdown bump
  }
  planeGrp.position.copy(F.pos);
  planeGrp.quaternion.copy(_fq);
  // HKS-93: the gear retracts — wheels render only while on the ground.
  // Procedural builders park one Group here; GLB airframes (HKS-110) tag an
  // ARRAY of scattered gear/wheel meshes — both obey the same landed rule.
  const gr = planeGrp.userData.gear;
  if (gr) {
    if (Array.isArray(gr)) { for (const g of gr) g.visible = F.landed; }
    else gr.visible = F.landed;
  }
  // HKS-93: anti-collision flashers — position lights stay steady, the white
  // wingtip/tail strobes double-flash once a second while AIRBORNE (real ops:
  // strobes off on the ground), and the red beacons pulse slower, always on
  if (planeGrp.userData.lights) {
    const Lg = planeGrp.userData.lights, tms = performance.now();
    const ts = tms % 1000;
    const strobeOn = !F.landed && (ts < 60 || (ts > 150 && ts < 210));   // flash-flash-pause
    for (const m of Lg.strobes) m.visible = strobeOn;
    const beaconOn = (tms % 1400) < 240;
    for (const m of Lg.beacons) m.visible = beaconOn;
  }
  // HKS-87/HKS-110 fleet rule: props & fans spin ONLY airborne — a base spin
  // plus a speed term; on the ground they hold still (gear down, props stopped).
  // (userData.props is the multi-engine variant — every prop shares the one spin rate)
  const spinD = F.landed ? 0 : 0.25 + F.speed * 0.004;
  if (planeGrp.userData.prop) planeGrp.userData.prop.rotation.z += spinD;
  if (planeGrp.userData.props) for (const pr of planeGrp.userData.props) pr.rotation.z += spinD;
  // HKS-87: engine audio follows the same landed rule as the prop — on the
  // ground it's driven purely by ground speed, so it fades out through the
  // roll-out and falls silent (setEngine(0) spins the oscillators down) once
  // the plane is stationary/parked. Airborne throttle mapping is unchanged.
  setEngine(sndOn ? (F.landed ? F.speed * 0.004 : 0.25 + 0.75 * (F.speed - 28) / Math.max(20, F.top - 28)) : 0);
  // --- FOV: the orbit view is telephoto (38°); flight goes wide for speed feel
  // — chase 55°, eye/cockpit 68° — and stretches a few degrees more near full
  // throttle. Eased so view switches breathe instead of snapping.
  const fovT = (F.view !== 'chase' ? 68 : 55) + 6 * (F.speed - 62) / Math.max(20, F.top - 62);
  if (Math.abs(camera.fov - fovT) > 0.05) {
    camera.fov += (fovT - camera.fov) * 0.06;
    camera.updateProjectionMatrix();
  }
  // look-around boom (HKS-53): drag offsets the view the same way in both cameras;
  // ease back to centre once nothing is held (no finger down, no mouse drag)
  if (!F.touchHold && !F.mouseLook) { F.lookYaw *= 0.9; F.lookPitch *= 0.9; }
  // --- cameras (world space: survives any leftover world spin)
  if (F.view !== 'chase') {                            // first person: 👁 eye or 🧑‍✈️ cockpit —
    const ud = planeGrp.userData, ck = ud.cockpit;     // interiors exist per skin (HKS-93)
    const inCk = F.view === 'cockpit' && !!ck;         // no deck built → render the clean eye
    if (ck) {
      ck.visible = inCk;                               // the interior shows ONLY in cockpit view
      if (inCk && ck.userData.rain) ck.userData.rain.visible = weather.rain;   // wet windscreen only in rain
    }
    _fu.set(0, 1, 0).applyQuaternion(_fq);             // nose (+ prop / dashboard) stay in frame,
    // eye view sits at the skin's ORIGINAL clean POV seat (eyeFwd/eyeUp — higher
    // and level on the 747); cockpit view uses the reframed captain eye
    const eF = inCk ? (ud.povFwd ?? 2.2) : (ud.eyeFwd ?? ud.povFwd ?? 2.2);
    const eU = inCk ? (ud.povUp ?? 2.3) : (ud.eyeUp ?? ud.povUp ?? 2.3);
    _fc.copy(F.pos).addScaledVector(_fv, eF).addScaledVector(_fu, eU);   // horizon rolls
    world.localToWorld(_fc);
    camera.position.copy(_fc);
    // head-turn: rotate the look direction by the shared boom offset (HKS-53);
    // povPitch (HKS-93) is the cockpit's resting head tilt — a few degrees down
    // so the panel fills the lower view; the clean eye view stays level
    _fe2.set(F.lookPitch + (inCk ? (ud.povPitch || 0) : 0), F.lookYaw, 0, 'YXZ');
    _fq2.copy(_fq).multiply(_lookQ.setFromEuler(_fe2));
    _fv2.set(0, 0, -1).applyQuaternion(_fq2);
    _fl.copy(F.pos).addScaledVector(_fv2, 2000); world.localToWorld(_fl);
    camera.up.copy(_fu);
    camera.lookAt(_fl);
  } else {                                             // chase: boom ~58 m out, orbitable (HKS-53)
    if (planeGrp.userData.cockpit) planeGrp.userData.cockpit.visible = false;   // no interior from outside
    const az = F.yaw + F.lookYaw;                      // lookYaw swings the boom around the plane
    const el = Math.max(0.05, Math.min(1.3, 0.34 + F.lookPitch));   // lookPitch raises/lowers it
    const ce = Math.cos(el);
    _fc.set(Math.sin(az) * ce, Math.sin(el), Math.cos(az) * ce).multiplyScalar(58);
    _fc.add(F.pos);
    world.localToWorld(_fc);
    camera.up.set(0, 1, 0);
    camera.position.lerp(_fc, 0.12);
    _fl.copy(F.pos); world.localToWorld(_fl);
    camera.lookAt(_fl);
  }
  _fl.copy(F.pos); world.localToWorld(_fl);
  controls.target.copy(_fl);                           // keeps the adaptive clip planes honest
  // --- HUD: real numbers (metres, knots), how-to card for the first seconds
  const az = ((-F.yaw / D2R) % 360 + 360) % 360;
  const touch = F.tilt && F.tiltRef != null;
  const stats = `${Math.round(F.pos.y / VE)} m · AGL ${Math.max(0, Math.round(agl))} m` +   // no emoji — ✈/🛬 flickered as landed toggled (HKS-91)
    ` · ${String(Math.round(az)).padStart(3, '0')}° ${CARD[Math.round(az / 45) % 8]}` +   // speed now shows on the speed bar
    (F.landed ? ` · ${t('fly.landed')}` : '');
  // HKS-91: single-line live stats, top-left under the brand chip (how-to lives in
  // the Help drawer, camera toggle by the compass, exit via the dock/Esc)
  document.getElementById('flyhud').innerHTML = stats;
  updateSpeedGauge();
}

// ---- walk mode (HKS-33): first person on foot, at a real walking pace -------
// Drops you at the current view centre, eye 1.7 m over the DEM, 1.4 m/s (Shift
// jogs at 4). WASD/arrows move, pointer-lock mouse looks; phones drag to look
// with a ▶ auto-walk toggle in the HUD. Slopes steeper than ~45° block you.
const walk = { on: false, pos: new THREE.Vector3(), yaw: 0, pitch: -0.04,
               keys: {}, prevSpin: 1, auto: false, helpT: 0, dist: 0, bob: 0,
               vy: 0, land: 0, spd: 0, top: 24 / 3.6, pov: true, touchHold: 0, prevVE: null };
let hikerGrp = null;
function enterWalk(startLocal) {
  if (walk.on || !curG) return;
  if (flight.on) exitFlight();
  if (stargaze.on) exitStargaze();
  walk.on = true;
  walk.prevSpin = spinDir; spinDir = 0;
  syncSpinSeg();
  const b0 = bounds();
  // seed from a given world-local point (e.g. GPS "walk from here", HKS-83) or the view centre
  const t0 = startLocal ? new THREE.Vector3(startLocal.x, 0, startLocal.z) : world.worldToLocal(controls.target.clone());
  walk.pos.set(
    Math.max(-b0.halfX, Math.min(b0.halfX, t0.x)), 0,
    Math.max(-b0.halfZ, Math.min(b0.halfZ, t0.z)));
  const fx = controls.target.x - camera.position.x, fz = controls.target.z - camera.position.z;
  walk.yaw = -(Math.atan2(fx, -fz) + world.rotation.y);   // keep facing the way you looked
  walk.pitch = -0.04;
  walk.auto = false; walk.helpT = 480; walk.dist = 0; walk.bob = 0;
  // spawned against a steep face? turn to look downhill so the first step works
  const sc = walk.pos.x / cell + W / 2, sr = walk.pos.z / cell + H / 2;
  const gx = (sampleE(sc + 0.5, sr) - sampleE(sc - 0.5, sr)) / cell;   // m rise per m east
  const gz = (sampleE(sc, sr + 0.5) - sampleE(sc, sr - 0.5)) / cell;   // m rise per m south
  if (Math.hypot(gx, gz) > 0.7) walk.yaw = Math.atan2(gx, gz);         // > ~35°: face downhill
  // air-drop insertion: start 60 m over the ground and fall in — you always
  // arrive ON the surface (never wedged inside a slope), and it reads as a spawn
  walk.vy = 0; walk.land = 0; walk.spd = 0;
  // On foot the world reads true-to-life: pin vertical exaggeration to 1.0 for the
  // whole walk (slopes, eye height and the hiker all match reality) and lock the
  // slider; the previous value comes back on exit.
  walk.prevVE = VE;
  if (VE !== 1) { VE = 1; document.getElementById('ve').value = 1; document.getElementById('vev').textContent = '1.0'; applyVE(); }
  document.getElementById('ve').disabled = true;
  walk.pov = false;   // arrive in chase view — you see the hiker land, C for first-person
  walk.pos.y = (sampleEtri(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2) + 1.7 + 60) * VE;
  if (!hikerGrp) { hikerGrp = buildHiker(); world.add(hikerGrp); }
  loadHikerModel();            // swap in the real (CC0 Adventurer) hiker once it arrives
  applyLookFilter(hikerGrp);   // HKS-104: spawn already dressed for Matrix/Neon (no-op otherwise)
  setTopMode('walk');
  updateWalkViewBtn();
  camera.fov = 70; camera.updateProjectionMatrix();
  document.getElementById('walkbtn').classList.add('on');
  document.getElementById('walkbtn').blur();  // else Space/Enter re-clicks the button and exits
  document.body.classList.add('flying', 'walking');       // fly/walk shared UI state; walking gates the auto-walk button (HKS-91)
  controls.enabled = false;
  // HKS-86 §2: GPS follow/compass never persists outside Orbit — entering a
  // movement mode spawns at the fix (if it's on this map), then disengages
  if (geo.following || geo.compass) { if (geoInBounds()) teleportToMarker(); gpsDrop(); }   // spawn at the fix, then turn GPS fully off
  syncWalkAuto();
  refreshDock();
  track('mode_enter', { mode: 'walk' });
  // HKS-88: Walk no longer auto-grabs the pointer — look is hold-left-drag by
  // default (like Fly/Stargaze), so the dock/compass/GPS stay clickable. The 🖱
  // view-lock button opts into pointer-lock (immersive FPS) on desktop.
}
function exitWalk() {
  if (!walk.on) return;
  walk.on = false; walk.keys = {};
  if (hikerGrp) hikerGrp.visible = false;
  setTopMode(null);
  updateSpeedGauge();
  if (document.exitPointerLock) document.exitPointerLock();
  document.getElementById('walkbtn').classList.remove('on');
  document.body.classList.remove('flying', 'walking');
  spinDir = walk.prevSpin;
  syncSpinSeg();
  const ve = document.getElementById('ve');   // hand the exaggeration back
  ve.disabled = false;
  if (walk.prevVE != null && walk.prevVE !== VE) {
    VE = walk.prevVE; ve.value = VE; document.getElementById('vev').textContent = VE.toFixed(1); applyVE();
  }
  walk.prevVE = null;
  camera.fov = 38; camera.updateProjectionMatrix();
  camera.up.set(0, 1, 0);
  controls.enabled = true;
  frameCamera();
  refreshDock();
  track('mode_exit', { mode: 'walk' });
}
document.getElementById('walkbtn').addEventListener('click', () => walk.on ? exitWalk() : enterWalk());

// ---- HKS-86: the mode dock (bottom-centre instrument cluster) ---------------
// The dock re-homes the existing mode buttons (same IDs, same handlers) and adds
// Orbit (exit-to-map) + a ⚙ that reopens the settings panel. refreshDock() only
// REFLECTS mode state into the dock/tray — it never owns the mode logic; the
// enter/exit/set* functions stay the single source of truth and call it last.
function refreshDock() {
  const set = (id, v) => {
    const el = document.getElementById(id); if (!el) return;
    el.classList.toggle('on', v);
    if (el.getAttribute('role') === 'radio') el.setAttribute('aria-checked', v ? 'true' : 'false');
    if (el.hasAttribute('aria-pressed')) el.setAttribute('aria-pressed', v ? 'true' : 'false');
  };
  set('orbitbtn', !flight.on && !walk.on && !stargaze.on);
  set('flybtn', flight.on);
  set('walkbtn', walk.on);
  set('stargazebtn', stargaze.on);
  set('matrixbtn', matrixOn);
  set('neonbtn', neonOn);
  const tray = document.getElementById('modetray');
  const mode = flight.on ? 'fly' : walk.on ? 'walk' : stargaze.on ? 'star' : '';
  tray.dataset.mode = mode;
  tray.hidden = mode !== 'star';   // HKS-86: the tray is now Stargaze-only (fly/walk camera lives beside the compass; exit via dock/Esc)
  syncCamSeg();                     // show/hide + sync the camera segmented control
  if (typeof updateHelp === 'function') updateHelp();   // keep the Help drawer's contextual section in sync
}
document.getElementById('orbitbtn').addEventListener('click', () => { exitFlight(); exitWalk(); exitStargaze(); refreshDock(); track('mode_enter', { mode: 'orbit' }); });
document.getElementById('dockgear').addEventListener('click', () => {
  const panel = document.getElementById('panel');
  const opening = panel.classList.contains('collapsed');
  panel.classList.toggle('collapsed');
  track(opening ? 'settings_open' : 'panel_collapse', { via: 'dock' });
});
// no init call: matrixOn/neonOn are declared further down (TDZ) and the static
// HTML default (Orbit active, tray hidden) is already the boot state — every
// later mode change routes through refreshDock().

// ---- GPS "you are here" location (HKS-83) -----------------------------------
// Two modes: set & forget (one getCurrentPosition) and follow (watchPosition). The
// marker stores HK1980 E/N and is reprojected each frame like the AQHI markers, so it
// survives source/VE changes. Nothing is persisted — no URL, no storage, no logs.
const locateBtn = document.getElementById('locatebtn');
const geoToastEl = document.getElementById('geotoast');
const geo = { el: null, ring: null, cone: null, arrow: null, has: false, E: 0, N: 0, acc: 0, watch: null, following: false, prevSpin: null, paused: false, autoStop: null, compass: false };
let geoToastT = null, geoEaseRAF = null, geoHeading = null, geoOrient = false;
// device compass → true-north heading (deg). iOS needs a permission gesture (the
// locate tap); Android/absolute uses alpha; both compensated for screen rotation.
function enableCompass() {
  if (geoOrient) return; geoOrient = true;
  const onOrient = e => {
    let h = null;
    if (typeof e.webkitCompassHeading === 'number') h = e.webkitCompassHeading;   // iOS: true-north, clockwise
    else if (e.absolute && typeof e.alpha === 'number') h = 360 - e.alpha;         // Android absolute
    if (h == null) return;
    const so = (screen.orientation && screen.orientation.angle) || 0;
    geoHeading = ((h + so) % 360 + 360) % 360;
  };
  const attach = () => { addEventListener('deviceorientationabsolute', onOrient, true); addEventListener('deviceorientation', onOrient, true); };
  if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function')
    DeviceOrientationEvent.requestPermission().then(s => { if (s === 'granted') attach(); else geoOrient = false; }).catch(() => { geoOrient = false; });
  else attach();
}
if (!window.isSecureContext || !('geolocation' in navigator)) {
  const lu = document.getElementById('locateui'); if (lu) lu.style.display = 'none';   // needs HTTPS + Geolocation API
}
function geoToast(msg) {
  geoToastEl.textContent = msg; geoToastEl.classList.add('show');
  clearTimeout(geoToastT); geoToastT = setTimeout(() => geoToastEl.classList.remove('show'), 4200);
}
function geoErr(e) { locateBtn.classList.remove('locating'); geoToast(t(e && e.code === 1 ? 'loc.denied' : 'loc.unavail')); }
function ensureGeoMarker() {
  if (geo.el) return;
  const el = document.createElement('div'); el.className = 'geoloc'; el.style.display = 'none';
  el.innerHTML = `<span class="gl-dot"></span><span class="gl-lbl" data-i18n="loc.you">${t('loc.you')}</span>`;
  document.body.appendChild(el); geo.el = el;
  const rg = new THREE.RingGeometry(0.86, 1, 48); rg.rotateX(-Math.PI / 2);
  const dg = new THREE.CircleGeometry(1, 48); dg.rotateX(-Math.PI / 2);
  // Google-location-blue (#4285f4), hard-coded for the GPS indicator only —
  // deliberately NOT the app accent teal.
  const mk = op => new THREE.MeshBasicMaterial({ color: 0x4285f4, transparent: true, opacity: op, depthWrite: false, side: THREE.DoubleSide });
  const grp = new THREE.Group(); grp.add(new THREE.Mesh(dg, mk(0.12)), new THREE.Mesh(rg, mk(0.35)));
  grp.visible = false; world.add(grp); geo.ring = grp;
  // Heading beam (HKS-83) — a single Google-Maps-style translucent blue cone
  // fanning out from the dot toward the phone's heading, brightest at the dot and
  // fading to nothing (radial-gradient canvas texture; CircleGeometry UVs centre
  // the wedge apex on the canvas centre). Sized by camera distance each frame
  // (constant on screen) and depthTest:false so it always draws over the terrain.
  const bc = document.createElement('canvas'); bc.width = bc.height = 128;
  const bx = bc.getContext('2d'), bgrad = bx.createRadialGradient(64, 64, 0, 64, 64, 64);
  bgrad.addColorStop(0, 'rgba(66,133,244,0.55)');
  bgrad.addColorStop(0.55, 'rgba(66,133,244,0.26)');
  bgrad.addColorStop(1, 'rgba(66,133,244,0)');
  bx.fillStyle = bgrad; bx.fillRect(0, 0, 128, 128);
  const half = 0.48;                                        // ~55° total spread
  const cg = new THREE.CircleGeometry(1, 24, Math.PI / 2 - half, 2 * half); cg.rotateX(-Math.PI / 2);
  const cone = new THREE.Mesh(cg, new THREE.MeshBasicMaterial({
    map: new THREE.CanvasTexture(bc), transparent: true,
    depthWrite: false, depthTest: false, side: THREE.DoubleSide }));
  cone.renderOrder = 6;
  const cgrp = new THREE.Group(); cgrp.add(cone); cgrp.visible = false; world.add(cgrp); geo.cone = cgrp;
}
function markerWorld() {
  const g = curG, col = (geo.E - g.bE) / g.aE, row = (geo.N - g.bN) / g.aN;
  const p = new THREE.Vector3((col - W / 2) * cell, sampleE(col, row) * VE, (row - H / 2) * cell);
  world.localToWorld(p); return p;
}
function easeCamera(camTo, tgtTo, ms) {
  cancelAnimationFrame(geoEaseRAF);
  if (ms <= 0) { camera.position.copy(camTo); controls.target.copy(tgtTo); controls.update(); return; }
  const c0 = camera.position.clone(), t0 = controls.target.clone(), t = performance.now();
  const tick = () => {
    const k = Math.min(1, (performance.now() - t) / ms), e = k * k * (3 - 2 * k);
    camera.position.lerpVectors(c0, camTo, e); controls.target.lerpVectors(t0, tgtTo, e); controls.update();
    if (k < 1) geoEaseRAF = requestAnimationFrame(tick);
  };
  geoEaseRAF = requestAnimationFrame(tick);
}
function centreOnMarker(ease, panOnly) {
  if (!geo.has || !curG) return;
  const tgt = markerWorld();
  let camTo;
  if (panOnly) camTo = camera.position.clone().add(tgt.clone().sub(controls.target));   // shift camera by the same delta
  else {
    if (spinDir !== 0) { geo.prevSpin = spinDir; spinDir = 0; syncSpinSeg(); }
    const dist = bounds().span * 0.14;
    let dir = camera.position.clone().sub(controls.target); dir.y = Math.max(dir.y, dist * 0.3);
    if (dir.lengthSq() < 1) dir.set(0, dist, dist);
    camTo = tgt.clone().add(dir.normalize().multiplyScalar(dist));
  }
  easeCamera(camTo, tgt, ease ? 720 : 0);
}
function placeFix(c) {                                    // c = GeolocationCoordinates
  const gg = gpsToGrid(c.latitude, c.longitude);
  if (!gg) return false;
  if (!gg.inBounds) {
    const inHK = c.latitude > 22.13 && c.latitude < 22.58 && c.longitude > 113.82 && c.longitude < 114.45;
    geoToast(t(inHK ? 'loc.outsrc' : 'loc.outside')); return false;
  }
  ensureGeoMarker();
  geo.E = gg.E; geo.N = gg.N; geo.acc = Math.max(6, c.accuracy || 0); geo.has = true; return true;
}
// HKS-86 §2: maps-style state machine. In Orbit the tap cycles
// follow → compass → off (the first tap locates AND follows); in a movement
// mode a tap is a one-shot teleport (see gpsTeleport) — never a persistent
// follow. The underlying locate/watch/compass internals are unchanged.
const GPS_SVG = fill => `<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="7"/><line x1="12" y1="1.5" x2="12" y2="4.5"/><line x1="12" y1="19.5" x2="12" y2="22.5"/><line x1="1.5" y1="12" x2="4.5" y2="12"/><line x1="19.5" y1="12" x2="22.5" y2="12"/>${fill ? '<circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>' : ''}</svg>`;
const GPS_ARROW_SVG = `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none" aria-hidden="true"><path d="M12 2 L19 21 L12 16.4 L5 21 Z"/></svg>`;
const gpsState = () => geo.compass ? 'compass' : geo.following ? 'follow' : 'off';
function refreshGpsBtn() {          // morph the button icon + label to the state
  const st = gpsState();
  locateBtn.innerHTML = st === 'compass' ? GPS_ARROW_SVG : GPS_SVG(st === 'follow' || geo.has);
  locateBtn.classList.toggle('on', geo.has);
  const lbl = st === 'follow' ? t('loc.following') : st === 'compass' ? t('loc.compass') : t('loc.find');
  locateBtn.setAttribute('aria-label', lbl);
  locateBtn.title = lbl;
}
// Try a GPS-accurate fix, then fall back to a coarse WiFi/IP fix — desktops often
// have no GPS chip and return UNAVAILABLE/timeout at high accuracy even with
// permission granted (HKS-86). Permission-denied (code 1) doesn't retry.
function getFix(onOk, onErr) {
  navigator.geolocation.getCurrentPosition(onOk, e => {
    if (e && e.code === 1) { onErr(e); return; }
    navigator.geolocation.getCurrentPosition(onOk, onErr, { enableHighAccuracy: false, timeout: 12000, maximumAge: 60000 });
  }, { enableHighAccuracy: true, timeout: 9000, maximumAge: 30000 });
}
function locateThenFollow() {       // off → follow: one fix, zoom to it, then track
  locateBtn.classList.add('locating');
  getFix(pos => {
    locateBtn.classList.remove('locating');
    if (placeFix(pos.coords)) {
      if (stargaze.on) followVantage(); else centreOnMarker(true, false);   // HKS-90: Stargaze moves the vantage, not the map
      startFollow();
    }
    refreshGpsBtn();
  }, e => { geoErr(e); refreshGpsBtn(); });
}
// HKS-90: drop the Stargaze vantage onto the current fix (clamped to bounds)
function followVantage() {
  if (!stargaze.on || !geoInBounds()) return;
  const b = bounds(), p = markerLocalPoint();
  stargaze.pos.x = Math.max(-b.halfX, Math.min(b.halfX, p.x));
  stargaze.pos.z = Math.max(-b.halfZ, Math.min(b.halfZ, p.z));
}
// HKS-86: fully turn GPS OFF (no pin) — the single "disengage" path now (there's
// no idle located-but-not-following state). Used by the Orbit cycle's off step
// (via removeMarker) and when entering a mode that can't follow (fly/walk/stargaze;
// here it must not touch controls/spinDir — the mode owns them).
function gpsDrop() {
  stopFollow();
  geo.compass = false; locateBtn.classList.remove('compass');
  geo.has = false; geo.prevSpin = null;
  if (geo.el) geo.el.style.display = 'none';
  if (geo.ring) geo.ring.visible = false;
  refreshGpsBtn();
}
function markerLocalPoint() {       // stored fix → world-local grid point
  const g = curG, col = (geo.E - g.bE) / g.aE, row = (geo.N - g.bN) / g.aN;
  return { col, row, x: (col - W / 2) * cell, z: (row - H / 2) * cell };
}
function teleportToMarker() {       // jump the ACTIVE movement mode to the fix
  if (!geoInBounds()) { geoToast(t('loc.outsrc')); return; }
  const p = markerLocalPoint();
  if (walk.on) {                    // re-run the air-drop insertion at the fix
    const b = bounds();
    walk.pos.x = Math.max(-b.halfX, Math.min(b.halfX, p.x));
    walk.pos.z = Math.max(-b.halfZ, Math.min(b.halfZ, p.z));
    walk.vy = 0; walk.land = 0; walk.spd = 0;
    walk.pos.y = (sampleEtri(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2) + 1.7 + 60) * VE;
  } else if (flight.on) {           // pop out airborne over the fix, at cruise
    flight.pos.set(p.x, (sampleE(p.col, p.row) + 300) * VE, p.z);
    flight.landed = false;
    flight.speed = Math.max(flight.speed, 62);
  } else if (stargaze.on) {         // re-plant the planetarium at the fix
    const b = bounds();
    stargaze.pos.x = Math.max(-b.halfX, Math.min(b.halfX, p.x));
    stargaze.pos.z = Math.max(-b.halfZ, Math.min(b.halfZ, p.z));
  }
}
function gpsTeleport() {            // movement modes: locate, jump there, disengage
  locateBtn.classList.add('locating');
  getFix(pos => {
    locateBtn.classList.remove('locating');
    if (placeFix(pos.coords)) teleportToMarker();
    gpsDrop();
  }, e => { geoErr(e); gpsDrop(); });
}
function startWatch() {
  geo.watch = navigator.geolocation.watchPosition(pos => {
    const c = pos.coords, gg = gpsToGrid(c.latitude, c.longitude);
    if (!gg || !gg.inBounds) return;                     // skip out-of-bounds fixes while following
    const gate = Math.max(5, (c.accuracy || 0) * 0.5);   // jitter gate: ignore sub-accuracy wiggle
    if (geo.has && Math.hypot(gg.E - geo.E, gg.N - geo.N) < gate) { geo.acc = Math.max(6, c.accuracy || geo.acc); return; }
    geo.E = gg.E; geo.N = gg.N; geo.acc = Math.max(6, c.accuracy || 0); geo.has = true;
    if (stargaze.on) followVantage();                     // HKS-90: track the vantage under the stars
    else centreOnMarker(true, true);                      // pan to follow, keep the user's zoom/angle
  }, geoErr, { enableHighAccuracy: true, timeout: 15000, maximumAge: 2000 });
}
function startFollow() {
  if (geo.watch != null) return;
  geo.following = true; locateBtn.classList.add('follow', 'on');
  if (geo.el) geo.el.classList.add('live');
  if (geo.has) { if (stargaze.on) followVantage(); else centreOnMarker(true, true); }   // recentre now — the first watch fix is usually the stored one (jitter-gated)
  startWatch();
  clearTimeout(geo.autoStop); geo.autoStop = setTimeout(() => stopFollow(), 15 * 60000);   // battery backstop
  clearInterval(geo.urlTimer); geo.urlTimer = setInterval(syncUrl, 30000);   // HKS-91: keep the shareable gps in the URL fresh (~30s)
}
function stopFollow() {
  if (geo.watch != null) { navigator.geolocation.clearWatch(geo.watch); geo.watch = null; }
  clearInterval(geo.urlTimer); geo.urlTimer = null;
  clearTimeout(geo.autoStop); geo.paused = false; geo.following = false;
  locateBtn.classList.remove('follow'); if (geo.el) geo.el.classList.remove('live');
}
addEventListener('visibilitychange', () => {              // pause the watch while hidden, resume on return
  if (!geo.following) return;
  if (document.hidden && geo.watch != null) { navigator.geolocation.clearWatch(geo.watch); geo.watch = null; geo.paused = true; }
  else if (!document.hidden && geo.paused) { geo.paused = false; startWatch(); }
});
function removeMarker() {
  stopFollow();
  if (geo.compass) setCompassView(false);                 // re-enable orbit controls
  geo.has = false;
  if (geo.el) geo.el.style.display = 'none';
  if (geo.ring) geo.ring.visible = false;
  locateBtn.classList.remove('on');
  if (geo.prevSpin != null) { spinDir = geo.prevSpin; syncSpinSeg(); geo.prevSpin = null; }
}
function geoInBounds() {                                   // is the stored fix on the active source's grid?
  if (!geo.has || !curG) return false;
  const col = (geo.E - curG.bE) / curG.aE, row = (geo.N - curG.bN) / curG.aN;
  return col >= 0 && col <= W - 1 && row >= 0 && row <= H - 1;
}
// heading-up "compass view" (like Google/Apple Maps): the map rotates so the way
// you face is up, you stay centred, the POV cone points forward. (HKS-83)
function setCompassView(on) {
  if (on && !geoOrient) enableCompass();
  geo.compass = on;
  if (!on) controls.enabled = true;                        // restore orbit on exit (updateCompassView won't run)
  locateBtn.classList.toggle('compass', on);
  if (on && spinDir !== 0) { geo.prevSpin = spinDir; spinDir = 0; syncSpinSeg(); }
  if (on && typeof DeviceOrientationEvent === 'undefined') geoToast(t('loc.nocompass'));   // device has no compass at all
}
function updateCompassView() {                            // per-frame camera drive; called from animate()
  if (!geo.compass || flight.on || walk.on || stargaze.on) return;   // yield to the mode cameras
  const drive = geo.has && geoHeading != null && geoInBounds();
  controls.enabled = !drive;                               // stay orbitable until we can actually drive (no heading / off-map)
  if (!drive) return;
  const m = markerWorld(), wy = world.rotation.y, H = geoHeading * Math.PI / 180;
  const lx = Math.sin(H), lz = -Math.cos(H);              // heading dir in world-local (N = −Z)
  const dx = lx * Math.cos(wy) + lz * Math.sin(wy), dz = -lx * Math.sin(wy) + lz * Math.cos(wy);   // → world
  const dist = bounds().span * 0.085, pitch = 52 * Math.PI / 180;
  const hor = dist * Math.cos(pitch), ver = dist * Math.sin(pitch);
  camera.position.lerp(new THREE.Vector3(m.x - dx * hor, m.y + ver, m.z - dz * hor), 0.12);   // smooth = filters compass jitter
  controls.target.lerp(m, 0.12); controls.update();
}
function updateGeoMarker() {                              // called from animate(), like updateAqhi()
  const hide = () => { if (geo.el) geo.el.style.display = 'none'; if (geo.ring) geo.ring.visible = false; if (geo.cone) geo.cone.visible = false; };
  if (!geo.has || !geo.el || !curG) { hide(); return; }
  const g = curG, col = (geo.E - g.bE) / g.aE, row = (geo.N - g.bN) / g.aN;
  if (col < 0 || col > W - 1 || row < 0 || row > H - 1) { hide(); return; }
  const lx = (col - W / 2) * cell, gy = sampleE(col, row) * VE, lz = (row - H / 2) * cell;
  geo.ring.visible = true; geo.ring.position.set(lx, gy + 0.4, lz); geo.ring.scale.set(geo.acc, 1, geo.acc);
  if (geoHeading != null) {                               // beam tracks the phone's compass bearing
    const rot = -geoHeading * Math.PI / 180;
    const camD = camera.position.distanceTo(markerWorld());   // scale so the beam stays a constant on-screen size
    geo.cone.visible = true; geo.cone.position.set(lx, gy + 1, lz);
    geo.cone.scale.set(camD * 0.12, 1, camD * 0.12); geo.cone.rotation.y = rot;
  } else { geo.cone.visible = false; }
  v.set(lx, gy + 2, lz); world.localToWorld(v); v.project(camera);
  if (v.z > 1 || occludedLocal(lx, gy + 2, lz)) { geo.el.style.display = 'none'; return; }
  geo.el.style.display = '';
  geo.el.style.left = ((v.x * 0.5 + 0.5) * innerWidth) + 'px';
  geo.el.style.top = ((-v.y * 0.5 + 0.5) * innerHeight) + 'px';
}
locateBtn.addEventListener('click', e => {
  e.stopPropagation();
  enableCompass();   // request device-orientation on this user gesture (needed for iOS)
  if (flight.on || walk.on) { gpsTeleport(); return; }   // locomotion modes: one-shot teleport, never persistent
  // Orbit AND Stargaze: persistent off → follow → compass → off (HKS-90)
  const st = gpsState();
  if (st === 'off') locateThenFollow();
  else if (st === 'follow') { setCompassView(true); refreshGpsBtn(); }
  else {                                     // compass → off: clear the pin, no ✕ needed
    if (stargaze.orient) setStargazeOrient(false);   // auto-arm needs GPS+compass — drop it too
    removeMarker(); refreshGpsBtn();
  }
  // track the user's intended next state — off→follow's geo.following is set async in the
  // geolocation callback, so re-reading gpsState() here would log 'off' (codex)
  track('gps', { state: st === 'off' ? 'follow' : st === 'follow' ? 'compass' : 'off' });   // never coordinates
});
// HKS-88: walk look — pointer-lock (move = look) when the 🖱 view-lock is engaged,
// otherwise hold-left-drag (cursor stays free for the dock/compass/UI).
addEventListener('mousemove', e => {
  if (!walk.on) return;
  const locked = document.pointerLockElement === renderer.domElement;
  if (!locked && (e.buttons !== 1 || e.target !== renderer.domElement)) return;   // unlocked → only a left-drag on the canvas (dragging UI must not turn the view — codex)
  const k = locked ? 0.0022 : 0.0035;
  walk.yaw -= e.movementX * k;
  walk.pitch = Math.max(-1.25, Math.min(1.25, walk.pitch - e.movementY * k));
});
// A parked plane launches on a quick tap/click on the canvas — but a press that
// drags, or a long hold, is a look-around gesture and must NOT take off (so you can
// inspect the plane from the ground). Track the press: only a short, still gesture
// counts as a tap. Holding no longer auto-launches; Space and the 🛫 button still do.
let _flyTap = null;   // {x,y,t} for a press begun on the canvas while landed, else null
renderer.domElement.addEventListener('pointerdown', e => {
  _flyTap = (flight.on && flight.landed) ? { x: e.clientX, y: e.clientY, t: e.timeStamp } : null;
});
addEventListener('pointermove', e => {
  if (_flyTap && Math.hypot(e.clientX - _flyTap.x, e.clientY - _flyTap.y) > 8) _flyTap = null;   // moved → a look-drag, not a tap
});
addEventListener('pointerup', e => {
  if (_flyTap && e.timeStamp - _flyTap.t < 400 && flight.on && flight.landed) takeOff();          // quick still tap = take off
  _flyTap = null;
});
addEventListener('pointercancel', () => { _flyTap = null; });
// flight: hold the left mouse button and drag to look around (shared boom, HKS-53)
addEventListener('mousemove', e => {
  if (!flight.on || e.buttons !== 1 || e.target !== renderer.domElement) return;   // only a left-drag on the canvas — dragging a panel slider must not turn the view (parity with walk/stargaze)
  flight.lookYaw = Math.max(-2.8, Math.min(2.8, flight.lookYaw - e.movementX * 0.004));
  flight.lookPitch = Math.max(-1.0, Math.min(1.0, flight.lookPitch - e.movementY * 0.004));
  flight.mouseLook = true;
});
addEventListener('mouseup', () => { flight.mouseLook = false; });
let _lastTouch = null;                                    // phones: drag to look
addEventListener('touchmove', e => {
  if (e.target !== renderer.domElement || !(walk.on || flight.on || stargaze.on)) return;
  const t0 = e.touches[0];
  if (_lastTouch) {
    const dx = t0.clientX - _lastTouch.x, dy = t0.clientY - _lastTouch.y;
    if (walk.on) {
      walk.yaw -= dx * 0.005;
      walk.pitch = Math.max(-1.25, Math.min(1.25, walk.pitch - dy * 0.005));
    } else if (stargaze.on) {                            // stargaze: 1 finger looks, 2 fingers move (HKS-90)
      if (e.touches.length >= 2) {
        stargazePan(dx, dy);
      } else {
        stargaze.yaw -= dx * 0.005;
        stargaze.pitch = Math.max(-0.15, Math.min(1.5, stargaze.pitch - dy * 0.005));
      }
    } else {                                             // flight: same drag = look around (HKS-53)
      flight.lookYaw = Math.max(-2.8, Math.min(2.8, flight.lookYaw - dx * 0.005));
      flight.lookPitch = Math.max(-1.0, Math.min(1.0, flight.lookPitch - dy * 0.005));
    }
  }
  _lastTouch = { x: t0.clientX, y: t0.clientY };
}, { passive: true });
// phones: hold the map to walk (or step on the gas in flight), TWO fingers to run;
// the same finger drags to steer/look while you go. touchHold counts live touches.
addEventListener('touchstart', e => {
  if (e.target !== renderer.domElement) return;
  if (walk.on) walk.touchHold = e.touches.length;         // hold = walk
  else if (flight.on) flight.touchHold = e.touches.length; // hold = gas (HKS-53)
}, { passive: true });
addEventListener('touchend', e => {
  _lastTouch = null;
  walk.touchHold = walk.on ? e.touches.length : 0;
  flight.touchHold = flight.on ? e.touches.length : 0;   // HKS-53: lifting the last finger cuts the gas
});
addEventListener('touchcancel', () => { _lastTouch = null; walk.touchHold = 0; flight.touchHold = 0; });

// a low-poly hiker — olive jacket, backpack, sun hat, and the walking stick.
// Built in real metres with limb pivots at hip/shoulder, scaled by VE so the
// body matches the exaggerated eye height (1.7 m × VE).
function buildHiker() {
  const grp = new THREE.Group();
  const m = c => new THREE.MeshStandardMaterial({ color: c, roughness: 0.85 });
  const olive = m(0x5a6b3f), pack = m(0xb0713a), skin = m(0xd7a97c),
        pants = m(0x3b4148), hat = m(0xc9b37e), wood = m(0x6e4f2f);
  const put = (mesh, x, y, z) => { mesh.position.set(x, y, z); grp.add(mesh); return mesh; };
  const legG = new THREE.BoxGeometry(0.16, 0.9, 0.2);  legG.translate(0, -0.45, 0);   // pivot at hip
  const armG = new THREE.BoxGeometry(0.12, 0.62, 0.14); armG.translate(0, -0.31, 0);  // pivot at shoulder
  const legL = put(new THREE.Mesh(legG, pants), -0.12, 0.9, 0);
  const legR = put(new THREE.Mesh(legG, pants),  0.12, 0.9, 0);
  put(new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.62, 0.26), olive), 0, 1.21, 0);    // torso
  put(new THREE.Mesh(new THREE.BoxGeometry(0.36, 0.48, 0.2), pack), 0, 1.26, 0.24);   // backpack
  put(new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 10), skin), 0, 1.64, 0);      // head
  put(new THREE.Mesh(new THREE.ConeGeometry(0.24, 0.18, 12), hat), 0, 1.8, 0);        // sun hat
  const armL = put(new THREE.Mesh(armG, olive), -0.3, 1.46, 0);
  const armR = put(new THREE.Mesh(armG, olive),  0.3, 1.46, 0);
  const stick = put(new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.035, 1.5, 8), wood),
                    0.42, 0.75, -0.12);
  stick.rotation.x = 0.15;
  grp.userData = { legL, legR, armL, armR, stick };
  grp.scale.setScalar(VE);
  grp.visible = false;
  return grp;
}
// ---- the real hiker (HKS): Quaternius' CC0 "Adventurer" ---------------------
// A rigged, animated backpacker replaces the box-primitive stand-in above.
// Source: "Adventurer" by Quaternius — https://poly.pizza/m/5EGWBMpuXq — CC0 /
// public domain, trimmed to the Idle/Walk/Run/Wave clips and quantized (~740 KB;
// provenance + rebuild recipe in data/models/README.md). Served from the same
// data/ origin as the terrain (ASSET_BASE-aware) and precached by the service
// worker, so it works offline like the DEM. The procedural hiker stays as the
// instant stand-in and the permanent fallback — a fork without the file or an
// uncached offline first walk just keeps the box figure.
const HIKER_GLB = 'data/models/hiker-adventurer.glb';
let hikerModelReq = false, hikerModelFails = 0;   // fire the fetch once per session; cap retries after a failure
function loadHikerModel() {
  if (hikerModelReq) return;
  hikerModelReq = true;
  new GLTFLoader().load(asset(HIKER_GLB), gltf => {
    if (!hikerGrp) { hikerModelReq = false; return; }   // group gone before load resolved — allow a later retry
    const model = gltf.scene;
    // updateMatrixWorld first — Box3.setFromObject measures SkinnedMeshes through
    // the bones, and their world matrices are stale until a full update pass.
    model.updateMatrixWorld(true);
    // Build the clip actions BEFORE touching the box: if a re-export/trim renamed
    // the clips so none resolve, we must NOT swap in a model that would freeze in
    // its bind pose — keep the procedural box gait instead. (review: gait contract
    // = mixer present ⇒ ≥1 clip; the stepWalk box branch stays reachable otherwise.)
    const mixer = new THREE.AnimationMixer(model);
    const act = n => {
      const c = THREE.AnimationClip.findByName(gltf.animations, 'CharacterArmature|' + n);
      return c ? mixer.clipAction(c) : null;
    };
    const aIdle = act('Idle'), aWalk = act('Walk'), aRun = act('Run');
    if (!aIdle && !aWalk && !aRun) {
      console.warn('[hiker] GLB carries no Idle/Walk/Run clips — keeping the box hiker');
      model.traverse(o => { if (o.isMesh) { o.geometry?.dispose(); (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => m?.dispose()); } });
      return;                              // hikerModelReq stays true → don't reload; box limb-swing remains
    }
    // normalise: 1.75 m tall, soles on y=0, facing -Z like the box hiker.
    const box = new THREE.Box3().setFromObject(model);
    const inner = new THREE.Group();
    inner.scale.setScalar(1.75 / Math.max(0.01, box.max.y - box.min.y));
    inner.rotation.y = Math.PI;            // glTF forward is +Z; the walk yaw expects -Z
    model.position.y = -box.min.y;
    inner.add(model);
    model.traverse(o => { if (o.isSkinnedMesh) o.frustumCulled = false; });   // animated limbs never clip out mid-swing
    // swap: dress down, replace the primitives wholesale, dress back up
    clearLookFilter(hikerGrp);
    for (const c of [...hikerGrp.children]) {
      hikerGrp.remove(c);
      if (c.isMesh) { c.geometry.dispose(); c.material.dispose(); }
    }
    hikerGrp.add(inner);
    hikerGrp.userData = { mixer, aIdle, aWalk, aRun, cur: null };
    applyLookFilter(hikerGrp);             // re-dress the new meshes for Matrix/Neon
  }, undefined, err => {                    // offline / 404 (e.g. GLB not yet on R2): keep the box stand-in
    console.warn('[hiker] model load failed — using the box stand-in:', asset(HIKER_GLB), (err && err.message) || err);
    if (++hikerModelFails < 2) hikerModelReq = false;   // retry once (transient/offline→online), then stop hammering
  });
}
// walk camera views — first person ↔ chase, mirroring the flight pattern
function updateWalkViewBtn() { syncCamSeg(); }   // walk camera (chase ⇄ first-person) reflects in the segmented control
function toggleWalkView() {
  if (!walk.on) return;
  walk.pov = !walk.pov;
  updateWalkViewBtn();
  track('camera_view', { view: walk.pov ? 'eye' : 'chase', mode: 'walk' });
}
// unified camera segmented control (HKS-86/93): 🎥 external/chase · 👁 first-person
// eye · 🧑‍✈️ cockpit interior. Fly shows all three (cockpit only when the skin
// has a flight deck); Walk keeps the two-way 🎥 ⇄ 👁 — no cockpit on foot.
function syncCamSeg() {
  const mode = flight.on ? flight.view : walk.on ? (walk.pov ? 'eye' : 'chase') : null;
  const ext = document.getElementById('cam-ext'), fp = document.getElementById('cam-pov'),
        ckb = document.getElementById('cam-ck');
  if (!ext || !fp || !ckb) return;
  ckb.hidden = !flight.on || !(planeGrp && planeGrp.userData.cockpit);   // Fly-only, needs a flight deck
  const mark = (btn, on) => { btn.classList.toggle('on', on); btn.setAttribute('aria-pressed', on ? 'true' : 'false'); };
  mark(ext, mode === 'chase'); mark(fp, mode === 'eye'); mark(ckb, mode === 'cockpit');
}
function setCamView(mode) {   // 'chase' | 'eye' | 'cockpit'
  if (flight.on) setFlightView(mode);
  else if (walk.on) { const fp = mode !== 'chase'; if (walk.pov !== fp) toggleWalkView(); }
}
document.getElementById('cam-ext').addEventListener('click', () => setCamView('chase'));
document.getElementById('cam-pov').addEventListener('click', () => setCamView('eye'));
document.getElementById('cam-ck').addEventListener('click', () => setCamView('cockpit'));
// HKS-91: auto-walk play/pause, beside the compass (was a ▶/⏸ link in the walk HUD)
function syncWalkAuto() {
  const b = document.getElementById('walk-auto');
  if (!b) return;
  b.classList.toggle('on', walk.auto);
  b.setAttribute('aria-pressed', walk.auto ? 'true' : 'false');
  b.firstElementChild.textContent = walk.auto ? '⏸' : '▶';   // ▶ = tap to auto-walk, ⏸ = tap to stop
}
document.getElementById('walk-auto').addEventListener('click', () => { walk.auto = !walk.auto; syncWalkAuto(); track('auto_walk', { on: walk.auto }); });
// HKS-88: 🖱 view-lock — opt into pointer-lock (immersive FPS look) in Walk. Default
// is hold-drag; this button captures the pointer so moving the mouse looks around.
// Esc releases it (browser); pointerlockchange keeps the button state honest.
function syncWalkLock() {
  const b = document.getElementById('walk-lock'); if (!b) return;
  const on = document.pointerLockElement === renderer.domElement;
  b.classList.toggle('on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false');
}
document.getElementById('walk-lock').addEventListener('click', e => {
  e.stopPropagation();
  const willLock = document.pointerLockElement !== renderer.domElement;
  if (!willLock) { if (document.exitPointerLock) document.exitPointerLock(); }
  else if (renderer.domElement.requestPointerLock) renderer.domElement.requestPointerLock();
  track('view_lock', { on: willLock });
});
document.addEventListener('pointerlockchange', syncWalkLock);

function stepWalk() {
  if (!walk.on) return;
  const K = walk.keys;
  const fwdIn = Math.max(-1, Math.min(1,
    (K['w'] || K['arrowup'] ? 1 : 0) - (K['s'] || K['arrowdown'] ? 1 : 0) +
    (walk.auto ? 1 : 0) + (walk.touchHold > 0 ? 1 : 0)));   // hold the map = walk
  const strIn = (K['d'] || K['arrowright'] ? 1 : 0) - (K['a'] || K['arrowleft'] ? 1 : 0);
  const boost = K['shift'] || walk.touchHold >= 2;          // ⇧ or a two-finger hold = run
  // ⇧ is the gas on foot: speed winds up toward the top-speed slider (the top
  // end is superhuman) and settles back to a 1.4 m/s stroll when released.
  // Pace scales with the vertical exaggeration: VE lifts the eye (1.7 m × VE),
  // so unscaled real pace reads as standing still on a 5 m DEM with no
  // near-field detail. Scaling by VE keeps motion parallax matched.
  const moving = !!(fwdIn || strIn);
  const target = moving ? (boost ? walk.top : 1.4) : 0;
  walk.spd += (target - walk.spd) * (target > walk.spd ? 0.045 : 0.12);
  if (walk.spd < 0.02) walk.spd = 0;
  const mps = walk.spd * Math.max(1, VE) / 60;
  const sy = Math.sin(walk.yaw), cy = Math.cos(walk.yaw);
  const dx = (-sy * fwdIn + cy * strIn) * mps;
  const dz = (-cy * fwdIn - sy * strIn) * mps;
  const b = bounds();
  if (dx || dz) {
    const gCur = sampleEtri(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2);
    const step = (mx, mz) => {                            // one gated move attempt
      if (!mx && !mz) return false;
      const nx = Math.max(-b.halfX, Math.min(b.halfX, walk.pos.x + mx));
      const nz = Math.max(-b.halfZ, Math.min(b.halfZ, walk.pos.z + mz));
      const gNew = sampleEtri(nx / cell + W / 2, nz / cell + H / 2);
      // ~50° climb gate with a 25 cm step-up allowance. (The old form added the
      // allowance to a 2 cm per-frame run, so it only blocked >85° — cliffs in
      // the 5 m DEM could pin you at spawn while everything else walked through.)
      const run = Math.hypot(mx, mz), rise = gNew - gCur;
      if (rise > run * 1.2 && rise > 0.25) return false;            // too steep this way
      walk.dist += Math.hypot(nx - walk.pos.x, nz - walk.pos.z);    // odometer (real m)
      walk.pos.x = nx; walk.pos.z = nz;
      return true;
    };
    // cliff dead ahead? slide along it (per-axis fallback) instead of freezing —
    // spawning face-first into a mountain used to pin you until you backed out
    if (step(dx, dz) || step(dx, 0) || step(0, dz))
      walk.bob += Math.min(0.55, 0.07 + walk.spd * 0.035);   // cadence rises with speed
  }
  const g = sampleEtri(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2);   // HKS: rest on the RENDERED triangle surface, not bilinear (submerged the hiker, ×VE)
  const eyeY = (g + 1.7) * VE;
  const airborne = walk.pos.y > eyeY + 0.05 * VE || walk.vy > 0;
  if (airborne) {                                         // drop-in / jump: real gravity
    walk.vy = Math.max(-26, walk.vy - 9.81 / 60);         // soft terminal cap
    walk.pos.y += (walk.vy / 60) * VE;
    if (walk.pos.y <= eyeY && walk.vy < 0) {
      walk.pos.y = eyeY;
      walk.land = Math.min(0.7, -walk.vy / 35);           // thud scales with impact
      walk.vy = 0;
    }
  } else {
    walk.pos.y += (eyeY - walk.pos.y) * 0.3;              // smooth over the 5 m DEM stairs
    if (K[' ']) walk.vy = 5.2;                            // ␣ = jump (~1.4 m apex)
  }
  walk.land *= 0.88;
  const bobY = Math.sin(walk.bob) * 0.08 * VE - walk.land * 1.1 * VE;   // bob + landing dip
  _fe.set(walk.pitch, walk.yaw, 0, 'YXZ');
  _fq.setFromEuler(_fe);
  _fv.set(0, 0, -1).applyQuaternion(_fq);
  // the hiker's body: visible in chase view. GLB hiker plays its own clips
  // (Idle/Walk/Run, cadence tied to ground speed); box fallback swings limbs.
  if (hikerGrp) {
    hikerGrp.visible = !walk.pov;
    if (!walk.pov) {
      const u = hikerGrp.userData;
      // the clips already bob the body — keep only the landing dip for the GLB
      const dip = airborne ? 0 : (u.mixer ? -walk.land * 1.1 * VE : bobY);
      hikerGrp.position.set(walk.pos.x, walk.pos.y - 1.7 * VE + dip, walk.pos.z);
      hikerGrp.rotation.y = walk.yaw;
      if (u.mixer) {
        const next = ((airborne || walk.spd < 0.2) ? u.aIdle : walk.spd < 3.2 ? u.aWalk : u.aRun) || u.aIdle || u.aWalk || u.aRun;
        if (next && u.cur !== next) {
          if (u.cur) { u.cur.fadeOut(0.25); next.reset().fadeIn(0.25).play(); }
          else next.reset().play();   // review: first clip after the swap plays at full weight — no bind-pose ease-in
          u.cur = next;
        }
        // feet track the ground speed (clips are authored near 1.4 / 4.8 m/s);
        // capped so a superhuman top-speed slider can't spin the legs comically
        if (u.aWalk) u.aWalk.timeScale = Math.min(1.8, Math.max(0.6, walk.spd / 1.4));
        if (u.aRun)  u.aRun.timeScale  = Math.min(2.2, Math.max(0.7, walk.spd / 4.8));
        u.mixer.update(1 / 60);                           // stepWalk runs on the 60 fps clock
      } else {
        const sw = walk.spd > 0.2 ? Math.sin(walk.bob) * Math.min(0.75, 0.25 + walk.spd * 0.05) : 0;
        u.legL.rotation.x = sw;         u.legR.rotation.x = -sw;
        u.armL.rotation.x = -sw * 0.7;  u.armR.rotation.x = sw * 0.7;
        u.stick.rotation.x = 0.15 + sw * 0.55;            // the stick plants with the stride
      }
    }
  }
  camera.up.set(0, 1, 0);
  if (walk.pov) {                                       // first person: eyes on the ground
    _fc.copy(walk.pos); _fc.y += bobY; world.localToWorld(_fc);
    camera.position.copy(_fc);
    _fl.copy(walk.pos).addScaledVector(_fv, 150); world.localToWorld(_fl);
    camera.lookAt(_fl);
  } else {                                              // chase: ~7 m back, watching the hiker.
    // Mouse pitch swings the boom arm: look down → camera climbs above you,
    // look up → it sinks toward the ground and aims up past the hiker.
    const boomR = 7, cp = Math.cos(walk.pitch);
    _fc.set(walk.pos.x + Math.sin(walk.yaw) * boomR * cp,
            walk.pos.y + 1.4 * VE - Math.sin(walk.pitch) * boomR * 0.7 * VE,
            walk.pos.z + Math.cos(walk.yaw) * boomR * cp);
    const cg = sampleE(_fc.x / cell + W / 2, _fc.z / cell + H / 2);
    _fc.y = Math.max(_fc.y, (cg + 0.5) * VE);           // the boom never digs into the DEM
    world.localToWorld(_fc);
    camera.position.lerp(_fc, 0.18);
    _fl.copy(walk.pos); _fl.y -= 0.5 * VE; world.localToWorld(_fl);
    camera.lookAt(_fl);
  }
  controls.target.copy(_fl);
  const az = ((-walk.yaw / D2R) % 360 + 360) % 360;
  const odo = walk.dist < 1000 ? `${Math.round(walk.dist)} m` : `${(walk.dist / 1000).toFixed(2)} km`;
  const stats = `${Math.round(g)} m · ${String(Math.round(az)).padStart(3, '0')}° ${CARD[Math.round(az / 45) % 8]}` +   // no emoji — 🚶/🪂 flickered as airborne toggled (HKS-91)
    ` · ${t('walk.dist')} ${odo}` +                       // odometer (speed now shows on the speed bar)
    (boost && moving ? ` · ${t('walk.jog')}` : '');
  // HKS-91: stats only — auto-walk is now the ▶/⏸ button beside the compass;
  // how-to lives in the Help drawer, End is the dock's Orbit button.
  document.getElementById('flyhud').innerHTML = stats;
  syncWalkAuto();
  updateSpeedGauge();
}
if (FLY_DEBUG) { window.__walk = walk; window.__stepWalk = () => stepWalk(); }

// ---- Matrix mode (HKS-31): see the simulation for what it is ----------------
// 🕴 (or M) reskins the whole scene into green-phosphor wireframe over a void,
// with the iconic digital rain falling as a glyph overlay (katakana + digits +
// 香港沙盒), green lightning, green fog, glyphified labels and a CRT flicker.
// Works in orbit, flight and walk — it's all materials and overlays. Surface,
// background and mesh controls lock while Matrix owns them (locknote pattern)
// and everything restores cleanly on exit.
// The weather stays live INSIDE the Matrix (you're still jacked in when it
// storms): world rain falls as green code streaks, snow as pale glyph-dust,
// clouds/mist/storm-wall read as banks of corrupted code, the glyph overlay
// falls harder and leans with the wind, and every lightning strike GLITCHES
// the simulation — screen tears, columns jump, the rain surges white-green.
let matrixOn = false;
const MX_CHARS = 'アイウエオカキクケコサシスセソタチツテトナニヌネノ0123456789香港沙盒中環大嶼山日月風雨雷ΦΣΞψ$#*+';
const matMxBlack = new THREE.MeshBasicMaterial({ color: 0x02120a });
const matMxSea = new THREE.MeshBasicMaterial({ color: 0x1c9e50, wireframe: true, transparent: true, opacity: 0.3 });
let mxPrevSea = null;
const matrixCv = document.getElementById('matrixfx');
const matrixCtx = matrixCv.getContext('2d');
let mxCols = [], mxFlakes = [];
function applyMatrixLook() {          // idempotent — re-asserted after source rebuilds
  if (!matrixOn || !terrain) return;
  terrain.visible = true;
  terrain.material = matMxBlack;
  wireOverlay.visible = true;
  wireOverlay.material.color.setHex(0x35ff6e);
  wireOverlay.material.opacity = 0.4;
  if (sea) { if (sea.material !== matMxSea) mxPrevSea = sea.material; sea.material = matMxSea; }
  if (skin) skin.traverse(o => {
    if (o.material && o.material.color) {
      if (o.userData.preMatrix == null) o.userData.preMatrix = o.material.color.getHex();
      o.material.color.setHex(0x2fe463);
    }
  });
  // the weather is code too (colours restored from the buildWeather constants)
  if (rainPts) { rainPts.material.color.setHex(0x39ff6a); rainPts.material.opacity = 0.5; }
  if (snowPts) snowPts.material.color.setHex(0xbfffd6);
  if (cloudGrp) for (const s of cloudGrp.children) s.material.color.setHex(0x2f8f4f);
  if (mistGrp) for (const mp of mistGrp.children) mp.material.color.setHex(0x35995c);
  if (wallGrp) for (const s of wallGrp.children) s.material.color.setHex(0x1a5c30);
}
function setMatrix(on) {
  if (on === matrixOn || !terrain) return;
  if (on && neonOn) setNeon(false);    // one reality at a time
  matrixOn = on;
  document.body.classList.toggle('matrix', on);
  document.getElementById('matrixbtn').classList.toggle('on', on);
  ['surf', 'bg', 'meshlines', 'mlcolor', 'mlhex', 'mlauto', 'solidcolor', 'solidhex']
    .forEach(id => { const el = document.getElementById(id); if (el) el.disabled = on; });
  const lock = document.getElementById('mxlock');
  lock.textContent = t('lock.matrix');
  lock.style.display = on ? 'block' : 'none';
  if (on) {
    applyMatrixLook();
    mxCols = [];
  } else {
    applyStyle(surfStyle);                       // restores surface + mesh overlay + wireLook
    if (sea && mxPrevSea) sea.material = mxPrevSea;
    if (skin) skin.traverse(o => {
      if (o.material && o.material.color && o.userData.preMatrix != null) {
        o.material.color.setHex(o.userData.preMatrix);
        delete o.userData.preMatrix;
      }
    });
    if (rainPts) { rainPts.material.color.setHex(0xaec8da); rainPts.material.opacity = 0.38; }
    if (snowPts) snowPts.material.color.setHex(0xffffff);
    if (cloudGrp) for (const s of cloudGrp.children) s.material.color.setHex(0xe2e8ef);
    if (mistGrp) for (const mp of mistGrp.children) mp.material.color.setHex(0xdde6ee);
    if (wallGrp) for (const s of wallGrp.children) s.material.color.setHex(0x3a4048);
    matrixCtx.clearRect(0, 0, matrixCv.width, matrixCv.height);
  }
  refreshModelLookFilters();   // HKS-104: the hiker/plane wear the reality too
  applyControlLocks();
  updateWindVisuals();       // re-grades clouds/rain for the new reality (calls renderSky + setFog)
  refreshDock();
  syncUrl();
  track('look_matrix', { on });
}
document.getElementById('matrixbtn').addEventListener('click', () => setMatrix(!matrixOn));
addEventListener('keydown', e => {
  if (keyOf(e) !== 'm' || flight.on || walk.on) return;
  const tag = (e.target.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
  setMatrix(!matrixOn);
});
function stepMatrix() {               // the digital rain overlay — weather-aware
  if (!matrixOn) return;
  const cv = matrixCv;
  if (cv.width !== innerWidth || cv.height !== innerHeight) {
    cv.width = innerWidth; cv.height = innerHeight; mxCols = [];
  }
  const fs = 15, nCols = Math.ceil(cv.width / fs);
  if (mxCols.length !== nCols)
    mxCols = Array.from({ length: nCols }, () => ({ y: Math.random() * -cv.height, s: 2 + Math.random() * 4 }));
  // the storm reaches into the code: the code-fall is only an ambient drizzle
  // when dry — turn the rain on and it becomes the full torrent, leaning
  // downwind, surging on every lightning flash
  const wet = weather.rain ? 1 : 0, w = windStrength;
  const act = wet ? 1 : 0.16;                            // fraction of columns streaming
  const rush = 1 + wet * 0.9 + w * 0.8 + (weather.lightning ? flash * 1.5 : 0);
  const lean = windVec.x * w * fs * 14;                  // px of downwind drift over a full fall
  const x = matrixCtx;
  x.globalCompositeOperation = 'destination-out';        // trails melt away
  x.fillStyle = `rgba(0,0,0,${wet ? 0.05 : 0.07})`;      // rain leaves longer trails
  x.fillRect(0, 0, cv.width, cv.height);
  x.globalCompositeOperation = 'source-over';
  x.font = `${fs}px ui-monospace, monospace`;
  const headP = 0.08 + (weather.lightning ? flash * 0.35 : 0);   // strikes whiten the heads
  for (let i = 0; i < nCols; i++) {
    const c = mxCols[i];
    if (c.a == null) c.a = Math.random();                // column activity lottery
    if (c.a > act) continue;                             // dormant until the rain recruits it
    const px = ((i * fs + c.y / cv.height * lean) % cv.width + cv.width) % cv.width;
    x.fillStyle = Math.random() < headP ? '#d6ffe2' : 'rgba(57,255,106,.9)';
    x.fillText(MX_CHARS[(Math.random() * MX_CHARS.length) | 0], px, c.y);
    if (wet && Math.random() < 0.5)                      // heavy rain doubles the stream
      x.fillText(MX_CHARS[(Math.random() * MX_CHARS.length) | 0], px, c.y - fs * (1 + (Math.random() * 3 | 0)));
    c.y += c.s * rush;
    if (c.y > cv.height + 30) { c.y = Math.random() * -300; c.s = 2 + Math.random() * 4; c.a = Math.random(); }
  }
  // glyph snow: when it snows, characters drift down gently and sway like
  // flakes — code falling out of the sky one glyph at a time
  if (weather.snow) {
    if (mxFlakes.length === 0)
      mxFlakes = Array.from({ length: 130 }, () => ({
        x: Math.random(), y: Math.random() * cv.height, v: 0.5 + Math.random() * 0.8,
        ph: Math.random() * Math.PI * 2, fs: 10 + Math.random() * 6 }));
    for (const f of mxFlakes) {
      f.y += f.v * (1 + w * 0.6);
      const fx = ((f.x * cv.width + Math.sin(f.y * 0.008 + f.ph) * 26 + windVec.x * w * f.y * 0.12)
                  % cv.width + cv.width) % cv.width;
      x.font = `${f.fs}px ui-monospace, monospace`;
      x.fillStyle = Math.random() < 0.04 ? '#ffffff' : 'rgba(191,255,214,.8)';
      x.fillText(MX_CHARS[(Math.random() * MX_CHARS.length) | 0], fx, f.y);
      if (f.y > cv.height + 20) { f.y = -20; f.x = Math.random(); }
    }
    x.font = `${fs}px ui-monospace, monospace`;
  } else if (mxFlakes.length) mxFlakes = [];
  // déjà vu: a close strike tears the simulation — horizontal slices of the
  // glyph field jump sideways and a couple of bright scanlines flicker through
  if (weather.lightning && flash > 0.35) {
    for (let n = 0; n < 5; n++) {
      const sy = Math.random() * cv.height, sh = 6 + Math.random() * 26;
      const dx = (Math.random() - 0.5) * 90 * flash;
      x.drawImage(cv, 0, sy, cv.width, sh, dx, sy, cv.width, sh);
    }
    x.fillStyle = `rgba(140,255,170,${(0.25 * flash).toFixed(3)})`;
    for (let n = 0; n < 2; n++) x.fillRect(0, Math.random() * cv.height, cv.width, 1.5);
  }
}
if (FLY_DEBUG) window.__setMatrix = setMatrix;

// ---- Sons of the Neon Night 風林火山 mode (HKS-35) ---------------------------
// Juno Mak's snowbound noir: an alternate-1994 Hong Kong buried in snow, graded
// to the film's desaturated murky grey (grayscale + lifted contrast on the GL
// canvas), under a heavy vignette with live film grain and the odd print
// scratch. Colour "only occasionally seeps through" — here it's the landmark
// labels, restyled as neon signage, the one thing the grade can't touch.
// Snow weather is forced on and locked; ❄️ (or N) toggles; exclusive with 🕴.
let neonOn = false, nnPrevSnow = null;
const NN_FILTER = 'grayscale(1) contrast(1.22) brightness(.9)';
const noirCv = document.getElementById('noirfx');
const noirCtx = noirCv.getContext('2d');
let noirImg = null, noirTick = 0;
function setNeon(on) {
  if (on === neonOn || !terrain) return;
  if (on && matrixOn) setMatrix(false); // one reality at a time
  neonOn = on;
  document.body.classList.toggle('neon', on);
  document.getElementById('neonbtn').classList.toggle('on', on);
  const lock = document.getElementById('nnlock');
  lock.textContent = t('lock.neon');
  lock.style.display = on ? 'block' : 'none';
  const snow = document.getElementById('snow');
  const flip = to => { if (snow.checked !== to) { snow.checked = to; snow.dispatchEvent(new Event('change', { bubbles: true })); } };
  if (on) {
    nnPrevSnow = snow.checked;
    flip(true);                        // the wasteland is snowbound
  } else {
    // Hand the weather back to whoever was driving it (HKS-72). The snapshot
    // always restores: snow is exclusively user-owned — neither the live sim
    // (syncLiveWeather) nor the storm presets (applyStorm) ever touch it — so
    // the old "skip under live/storm" guard just stranded the forced ❄ behind
    // checkboxes those modes keep locked, with no way to clear it.
    if (nnPrevSnow != null) flip(nnPrevSnow);
    nnPrevSnow = null;
    // …then let the live sim re-assert real conditions right away rather than
    // waiting for its next 5-minute refresh. (A storm signal needs no
    // re-assert: Neon only ever displaced snow, which applyStorm ignores.)
    if (liveMode) syncLiveWeather();
    noirCtx.clearRect(0, 0, noirCv.width, noirCv.height);
  }
  refreshModelLookFilters();   // HKS-104: the hiker/plane join the noir
  applyControlLocks();
  renderSky(); setFog();   // clear colour + fog must follow the noir/day toggle even when snow is already saturated (codex)
  refreshDock();
  syncUrl();
  track('look_neon', { on });
}
function stepNoir() {                  // live film grain + the odd print scratch
  if (!neonOn) return;
  if (!noirImg) noirImg = noirCtx.createImageData(noirCv.width, noirCv.height);
  if ((noirTick++ & 1) === 0) {        // re-grain at half rate — film cadence
    const d = noirImg.data;
    for (let i = 0; i < d.length; i += 4) {
      d[i] = d[i+1] = d[i+2] = 128 + (Math.random() - 0.5) * 96 | 0;
      d[i+3] = 30;
    }
    noirCtx.putImageData(noirImg, 0, 0);
    if (Math.random() < 0.025) {
      noirCtx.fillStyle = 'rgba(238,238,238,.55)';
      noirCtx.fillRect((Math.random() * noirCv.width) | 0, 0, 1, noirCv.height);
    }
  }
}
document.getElementById('neonbtn').addEventListener('click', () => setNeon(!neonOn));
addEventListener('keydown', e => {
  if (keyOf(e) !== 'n' || flight.on || walk.on) return;
  const tag = (e.target.tagName || '').toLowerCase();
  if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
  setNeon(!neonOn);
});
if (FLY_DEBUG) window.__setNeon = setNeon;

// ---- HKS-104: Matrix / Neon look filter for the hiker + plane skins ----------
// The reality restyles reach the models through the scene's own mechanisms, not
// a parallel look. Matrix mirrors the terrain treatment exactly — a void-black
// body (matMxBlack's palette) under a phosphor wireframe (wireOverlay's green) —
// by swapping every mesh onto shared singleton materials and hanging a
// same-geometry wireframe child off it; light/window dots (MeshBasicMaterial)
// become bright phosphor points instead of near-invisible wire specks. Neon
// leans on the film grade already covering the GL canvas (NN_FILTER): materials
// are cloned with a hot neon emissive so the model reads as lit signage burning
// through the murky grey; the position/strobe light dots (MeshBasicMaterial —
// no emissive channel) are already the model's brightest points and stay as-is.
// Originals are stashed per-mesh (userData.preLook — the preMatrix pattern) and
// restored exactly; per-apply Neon clones are disposed on restore (their maps
// belong to the originals — not ours to free), and the shared Matrix singletons
// live for the session like matMxBlack/matMxSea. Applies only on mode / skin /
// mode-entry changes — never per frame.
const mxModelBody = new THREE.MeshBasicMaterial({ color: 0x02150b, polygonOffset: true,
                                                  polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
const mxModelWire = new THREE.MeshBasicMaterial({ color: 0x39ff6a, wireframe: true,
                                                  transparent: true, opacity: 0.6 });
const mxModelGlow = new THREE.MeshBasicMaterial({ color: 0x8dffb0 });
function applyLookFilter(grp) {        // idempotent — cheap to re-assert on mode entry
  if (!grp) return;
  const mode = matrixOn ? 'matrix' : neonOn ? 'neon' : null;
  if ((grp.userData.lookFilter || null) === mode) return;   // already dressed for this reality
  clearLookFilter(grp);                // also covers the Matrix ⇄ Neon hand-off
  if (!mode) return;
  const meshes = [];                   // collect first — applying mutates the tree
  grp.traverse(o => { if (o.isMesh && !o.userData.lookOverlay) meshes.push(o); });
  for (const o of meshes) {
    const src = o.material, mats = Array.isArray(src) ? src : [src];
    if (mode === 'matrix') {
      o.userData.preLook = src;
      if (mats[0] && mats[0].isMeshBasicMaterial) { o.material = mxModelGlow; continue; }  // nav lights / windows
      o.material = mxModelBody;
      // geometry shared — overlay costs no memory. Skinned meshes (the GLB hiker)
      // get a SkinnedMesh shell bound to the same skeleton so the wire animates
      // with the body instead of freezing in bind pose.
      const wire = o.isSkinnedMesh ? new THREE.SkinnedMesh(o.geometry, mxModelWire)
                                   : new THREE.Mesh(o.geometry, mxModelWire);
      if (o.isSkinnedMesh) { wire.bind(o.skeleton, o.bindMatrix); wire.frustumCulled = false; }
      wire.userData.lookOverlay = true;
      o.userData.lookWire = wire;
      o.add(wire);
    } else {
      if (!mats.some(m => m && m.emissive)) continue;         // no emissive channel (light dots) — leave lit
      const clones = mats.map(m => {
        const c = m.clone();
        if (c.emissive) { c.emissive.setHex(0xff3d67); c.emissiveIntensity = 1.6; }
        return c;
      });
      o.userData.preLook = src;
      o.userData.lookClones = clones;
      o.material = Array.isArray(src) ? clones : clones[0];
    }
  }
  grp.userData.lookFilter = mode;
}
function clearLookFilter(grp) {
  if (!grp || !grp.userData.lookFilter) return;
  const touched = [];
  grp.traverse(o => { if ('preLook' in o.userData) touched.push(o); });
  for (const o of touched) {
    o.material = o.userData.preLook;   // the exact original object(s) — textures untouched
    delete o.userData.preLook;
    if (o.userData.lookWire) {         // shared geometry + singleton material — remove only
      o.remove(o.userData.lookWire);
      delete o.userData.lookWire;
    }
    if (o.userData.lookClones) {       // per-apply clones — dispose (maps are the originals')
      for (const c of o.userData.lookClones) c.dispose();
      delete o.userData.lookClones;
    }
  }
  delete grp.userData.lookFilter;
}
function refreshModelLookFilters() { applyLookFilter(hikerGrp); applyLookFilter(planeGrp); }

// ---- Stargaze mode (HKS-86 §4) -----------------------------------------------
// A planetarium anchored at the current view centre: the camera plants eye-high
// on the terrain — look-only for the eyes, but the vantage can pan across the
// surface (right-drag / two-finger, HKS-90) — biased up at the star layer (HKS-84
// catalogue + constellations; hover/tap picking keeps working). Its tray now
// carries just the sky clock (#skymode/#skytime); 🤳 auto-arm moved beside the
// compass and 📍 follow-me folded into the standard GPS button (off → follow →
// compass), which now persists in Stargaze. World themes (Matrix/Neon) stay
// combinable. Entering hides the weather chip + radar dial (CSS, body.stargazing);
// everything restores on exit.
const stargaze = { on: false, pos: new THREE.Vector3(), yaw: 0, pitch: 0.9,
                   prevSpin: 1, prevWx: null, orient: false };
function setSkyControl(mode, date, minutes) {   // drive the existing panel controls
  const g = id => document.getElementById(id);
  if (date != null) { g('skydate').value = date; g('skydate').dispatchEvent(new Event('change')); }
  if (minutes != null) { g('skytime').value = minutes; g('skytime').dispatchEvent(new Event('input')); }
  if (g('skymode').value !== mode) { g('skymode').value = mode; g('skymode').dispatchEvent(new Event('change')); }
}
function enterStargaze() {
  if (stargaze.on || !curG) return;
  if (flight.on) exitFlight();
  if (walk.on) exitWalk();
  stargaze.on = true;
  stargaze.prevSpin = spinDir; spinDir = 0;             // the world holds still under the sky
  syncSpinSeg();
  // anchor at the current view centre, eye 1.7 m over the DEM
  const b = bounds();
  const t0 = world.worldToLocal(controls.target.clone());
  stargaze.pos.set(
    Math.max(-b.halfX, Math.min(b.halfX, t0.x)), 0,
    Math.max(-b.halfZ, Math.min(b.halfZ, t0.z)));
  const fx = controls.target.x - camera.position.x, fz = controls.target.z - camera.position.z;
  stargaze.yaw = -(Math.atan2(fx, -fz) + world.rotation.y);   // keep facing the way you looked
  stargaze.pitch = 0.9;                                        // biased up at the sky
  // HKS-90: Stargaze keeps GPS follow/compass (unlike fly/walk) — if it's already
  // engaged, plant at the fix and let the shared watch keep tracking the vantage.
  if ((geo.following || geo.compass) && geoInBounds()) {
    const p = markerLocalPoint(); stargaze.pos.x = p.x; stargaze.pos.z = p.z;
  }
  document.body.classList.add('stargazing');            // hides wx chip + radar dial; drives applyControlLocks (HKS-91)
  // HKS-91: save the pre-stargaze "session", then clear the sky — live weather,
  // all weather effects and the typhoon signal are turned off AND locked, so the
  // planetarium always has a clean sky. Everything restores on exit.
  const g = id => document.getElementById(id);
  stargaze.prevWx = {
    live: liveMode, storm: stormLevel,
    rain: weather.rain, clouds: weather.clouds, fog: weather.fog,
    lightning: weather.lightning, waves: weather.waves, snow: weather.snow,
    wind: +g('wind').value, winddir: g('winddir').value,
    skymode: g('skymode').value, skydate: g('skydate').value, skytime: g('skytime').value,
  };
  if (liveMode) setLiveMode(false);                     // off live weather data
  if (stormLevel > 0) { g('storm').value = '0'; applyStorm(0); }   // off typhoon signal
  ['rain', 'clouds', 'fog', 'lightning', 'waves', 'snow'].forEach(k => {   // off every weather effect
    const cb = g(k); if (cb.checked) { cb.checked = false; cb.dispatchEvent(new Event('change')); }
  });
  if (+g('wind').value) { g('wind').value = 0; g('wind').dispatchEvent(new Event('input')); }
  setSkyControl('live');                                // sky time = now (unlocked — scrub via the 🕐 panel)
  setSgTimeVisible(false);                              // 🕐 sky-time panel hidden by default
  applyControlLocks();                                  // lock the now-cleared weather/typhoon/live controls
  camera.fov = 60; camera.updateProjectionMatrix();     // wide for sky sweep
  controls.enabled = false;
  document.getElementById('stargazebtn').blur();        // else ␣/Enter re-clicks and exits
  syncSgTray();
  refreshDock();
  track('mode_enter', { mode: 'stargaze' });
}
function exitStargaze() {
  if (!stargaze.on) return;
  stargaze.on = false;
  setStargazeOrient(false);   // GPS follow/compass persists into Orbit; only auto-arm drops
  document.body.classList.remove('stargazing');         // drop the lock before restoring (HKS-91)
  // HKS-91: restore the pre-stargaze session (weather, typhoon, live sync, sky/time).
  // If there was none, applyControlLocks below just leaves the current defaults.
  const p = stargaze.prevWx;
  if (p) {
    const g = id => document.getElementById(id);
    if (p.live) {
      setLiveMode(true);                                // live re-derives weather + storm + live sky
    } else {
      if (p.storm > 0) { g('storm').value = String(p.storm); applyStorm(p.storm); }
      else if (stormLevel > 0) { g('storm').value = '0'; applyStorm(0); }
      ['rain', 'clouds', 'fog', 'lightning', 'waves', 'snow'].forEach(k => {
        const cb = g(k); if (cb.checked !== p[k]) { cb.checked = p[k]; cb.dispatchEvent(new Event('change')); }
      });
      if (+g('wind').value !== p.wind) { g('wind').value = p.wind; g('wind').dispatchEvent(new Event('input')); }
      if (g('winddir').value !== p.winddir) { g('winddir').value = p.winddir; g('winddir').dispatchEvent(new Event('change')); }
      setSkyControl(p.skymode, p.skydate, p.skytime);   // hand the sky clock back
    }
    stargaze.prevWx = null;
  }
  spinDir = stargaze.prevSpin;
  syncSpinSeg();
  camera.fov = 38; camera.updateProjectionMatrix();
  camera.up.set(0, 1, 0);
  controls.enabled = true;
  applyControlLocks();                                  // unlock now that stargazing is off
  frameCamera();
  refreshDock();
  track('mode_exit', { mode: 'stargaze' });
}
function stepStargaze() {                               // per-frame planetarium camera
  if (!stargaze.on) return;
  const col = stargaze.pos.x / cell + W / 2, row = stargaze.pos.z / cell + H / 2;
  stargaze.pos.y = (sampleE(col, row) + 1.7) * VE;      // stay planted through VE changes
  _fe.set(stargaze.pitch, stargaze.yaw, 0, 'YXZ');
  _fq.setFromEuler(_fe);
  _fv.set(0, 0, -1).applyQuaternion(_fq);
  _fc.copy(stargaze.pos); world.localToWorld(_fc);
  camera.up.set(0, 1, 0);
  camera.position.copy(_fc);
  _fl.copy(stargaze.pos).addScaledVector(_fv, 1000); world.localToWorld(_fl);
  camera.lookAt(_fl);
  controls.target.copy(_fl);                            // keeps the adaptive clip planes honest
}
// 🤳 point-at-the-sky: device orientation aims the camera (iOS asks permission
// on the toggle tap); hidden where there's no sensor at all
function onSgOrient(e) {
  if (!stargaze.on) return;
  let h = null;
  if (typeof e.webkitCompassHeading === 'number') h = e.webkitCompassHeading;   // iOS: true-north, clockwise
  else if (e.absolute && typeof e.alpha === 'number') h = 360 - e.alpha;         // Android absolute
  if (h != null) {
    const so = (screen.orientation && screen.orientation.angle) || 0;
    // scene-frame azimuth (the star sphere lives in the scene, not the spun world group)
    stargaze.yaw = -(((h + so) % 360 + 360) % 360) * D2R - world.rotation.y;
  }
  if (typeof e.beta === 'number')                        // back camera elevation ≈ beta − 90°
    stargaze.pitch = Math.max(-0.15, Math.min(1.5, (e.beta - 90) * D2R));
}
// Auto-arm (HKS-90): compass heading aims yaw + accelerometer tilts pitch. It's
// linked to GPS compass — arming needs device-orientation permission and flips GPS
// into compass mode (locate → follow → compass); it disengages when GPS goes off.
function setStargazeOrient(on) {
  if (on === stargaze.orient) return;
  const arm = () => {
    stargaze.orient = true;
    addEventListener('deviceorientation', onSgOrient, true);
    if (gpsState() !== 'compass') {                     // pull GPS up to compass mode
      if (gpsState() === 'off') locateThenFollow();     // locate + follow the vantage first
      setCompassView(true); refreshGpsBtn();
    }
    syncSgToggles();
  };
  if (!on) {
    stargaze.orient = false;
    removeEventListener('deviceorientation', onSgOrient, true);
    syncSgToggles();
    return;
  }
  if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function')
    DeviceOrientationEvent.requestPermission().then(s => { if (s === 'granted') arm(); else geoToast(t('loc.nocompass')); }).catch(() => {});
  else arm();
}
function syncSgToggles() {
  const o = document.getElementById('sg-orient');
  o.classList.toggle('on', stargaze.orient);
  o.setAttribute('aria-pressed', stargaze.orient ? 'true' : 'false');
  const timeOn = !document.body.classList.contains('sg-time-hidden');   // 🕐 lit = sky-time panel showing
  const c = document.getElementById('sg-clock');
  c.classList.toggle('on', timeOn);
  c.setAttribute('aria-pressed', timeOn ? 'true' : 'false');
}
// 🕐 show / hide the whole sky-time container for a clean sky (HKS-90)
function setSgTimeVisible(show) {
  document.body.classList.toggle('sg-time-hidden', !show);
  syncSgToggles();
}
function syncSgTray() {   // mirror the panel's sky clock into the tray proxy
  const g = id => document.getElementById(id);
  const live = skySim.on && skySim.live;
  g('sg-live').classList.toggle('on', live);
  g('sg-custom').classList.toggle('on', !live);
  g('sgrow').classList.toggle('live', live);            // 2-line: live shows the clock, custom the slider (HKS-91)
  g('sg-time').disabled = live;
  g('sg-time').value = live ? hktMinutes(new Date()) : skySim.minutes;
  g('sg-timev').textContent = mmToHHMM(+g('sg-time').value);
  if (live) g('sg-livetime').textContent = mmToHHMM(hktMinutes(new Date()));   // current HK time (ticks per frame)
  // auto-arm only makes sense on a device with real motion sensors. Desktop Chrome
  // defines DeviceOrientationEvent even with no compass, so also require a coarse
  // pointer (phone/tablet) — matches the startup gate above (HKS-90).
  g('sg-orient').hidden = !(matchMedia('(pointer: coarse)').matches && typeof DeviceOrientationEvent !== 'undefined');
  syncSgToggles();
}
document.getElementById('stargazebtn').addEventListener('click', () => stargaze.on ? exitStargaze() : enterStargaze());
document.getElementById('sg-live').addEventListener('click', () => { setSkyControl('live'); syncSgTray(); track('sg_time_mode', { mode: 'live' }); });
document.getElementById('sg-custom').addEventListener('click', () => {
  setSkyControl('fixed', hktDateStr(new Date()), skySim.minutes);
  syncSgTray();
  track('sg_time_mode', { mode: 'custom' });
});
document.getElementById('sg-time').addEventListener('input', e => {
  if (skySim.on && skySim.live) return;                 // scrub only drives custom time
  setSkyControl('fixed', null, +e.target.value);
  document.getElementById('sg-timev').textContent = mmToHHMM(+e.target.value);
});
// one committed event per stargaze-time scrub (on release), not per input tick
document.getElementById('sg-time').addEventListener('change', e => { if (e.isTrusted && !(skySim.on && skySim.live)) track('sky_time_scrub', { via: 'stargaze' }); });
document.getElementById('sg-orient').addEventListener('click', () => { const on = !stargaze.orient; setStargazeOrient(on); track('sg_orient', { on }); });
document.getElementById('sg-clock').addEventListener('click', () => { const show = document.body.classList.contains('sg-time-hidden'); setSgTimeVisible(show); track('sg_clock', { on: show }); });
// panel-side sky changes keep the tray proxy honest while stargazing
document.getElementById('skymode').addEventListener('change', () => { if (stargaze.on) syncSgTray(); });
addEventListener('keydown', e => { if (stargaze.on && e.key === 'Escape') exitStargaze(); });
// HKS-90: move the vantage across the terrain surface (right-drag / two-finger).
// Basis is the horizontal facing (yaw only); "grab the ground" feel, clamped to bounds.
function stargazePan(dx, dy) {
  if (geo.following || geo.compass) return;   // GPS owns the vantage while tracking — no manual pan, so "Following" never goes stale (codex P2, HKS-90)
  _fe.set(0, stargaze.yaw, 0, 'YXZ'); _fq.setFromEuler(_fe);
  _sgF.set(0, 0, -1).applyQuaternion(_fq);   // horizontal forward (compass facing)
  _sgR.set(1, 0, 0).applyQuaternion(_fq);    // horizontal right
  const b = bounds(), spd = b.span * 0.00035;
  stargaze.pos.addScaledVector(_sgR, -dx * spd).addScaledVector(_sgF, dy * spd);
  stargaze.pos.x = Math.max(-b.halfX, Math.min(b.halfX, stargaze.pos.x));
  stargaze.pos.z = Math.max(-b.halfZ, Math.min(b.halfZ, stargaze.pos.z));
}
// drag-to-look (desktop): LEFT button looks around; RIGHT button drags across the
// surface. Phones reuse the shared touch path (1 finger look, 2 finger move).
addEventListener('mousemove', e => {
  if (!stargaze.on || e.target !== renderer.domElement) return;   // only the canvas drives look/pan — dragging HUD controls must not (parity with the touch path, CodeRabbit)
  if (e.buttons === 1) {                     // left drag = look
    stargaze.yaw -= e.movementX * 0.003;
    stargaze.pitch = Math.max(-0.15, Math.min(1.5, stargaze.pitch - e.movementY * 0.003));
  } else if (e.buttons === 2) {              // right drag = move across the surface
    stargazePan(e.movementX, e.movementY);
  }
});
renderer.domElement.addEventListener('contextmenu', e => { if (stargaze.on) e.preventDefault(); });   // free the right-drag in Stargaze
if (FLY_DEBUG) { window.__stargaze = stargaze; window.__stepStargaze = () => stepStargaze(); }

// ---- corner UI (HKS-32): compass + snapshot ---------------------------------
// The compass rose tracks the camera heading relative to TERRAIN north (the
// world group may be auto-spun); clicking snaps the view — or the plane — back
// to north. The snapshot renders the scene at a 2× supersampled buffer, bakes
// in the wordmark + tile attribution, and downloads a timestamped PNG. Works
// identically in orbit and flight modes: it's the same scene camera.
const compassCv = document.getElementById('compass');
const compassCtx = compassCv.getContext('2d');
const CARD4 = { 0: 'N', 90: 'E', 180: 'S', 270: 'W' };
function updateCompass() {
  let heading;
  if (flight.on) heading = -flight.yaw;                // in the air the tape IS the plane's heading
  else if (walk.on) heading = -walk.yaw;               // on foot, where you're facing
  else if (stargaze.on) heading = -stargaze.yaw;       // under the stars, where you're looking
  else {
    const fx = controls.target.x - camera.position.x, fz = controls.target.z - camera.position.z;
    if (!fx && !fz) return;
    heading = Math.atan2(fx, -fz) + world.rotation.y;
  }
  const deg = ((heading / D2R) % 360 + 360) % 360;
  if (radarRunning && radarImg) {   // accumulate the shortest step so it never reverses across the 0/360 seam (HKS-74/79)
    radarRot += ((-deg - radarRot + 180) % 360 + 360) % 360 - 180;
    radarImg.style.transform = `rotate(${radarRot}deg)`;
  }
  const w = compassCv.clientWidth, h = compassCv.clientHeight;
  const dpr = Math.min(devicePixelRatio || 1, 2);
  if (compassCv.width !== Math.round(w * dpr)) { compassCv.width = Math.round(w * dpr); compassCv.height = Math.round(h * dpr); }
  const x = compassCtx;
  x.setTransform(dpr, 0, 0, dpr, 0, 0);
  x.clearRect(0, 0, w, h);
  const lightUi = document.body.classList.contains('ui-light');
  const ink = lightUi ? 'rgba(32,38,44,.9)' : 'rgba(238,242,246,.9)';
  const sub2 = lightUi ? 'rgba(32,38,44,.42)' : 'rgba(238,242,246,.38)';
  const acc = lightUi ? '#0b8f66' : '#35cba0';
  const ppd = w / 80;                                  // 80° of tape in view
  x.textAlign = 'center'; x.textBaseline = 'top'; x.lineWidth = 1;
  for (let d = Math.floor((deg - 42) / 5) * 5; d <= deg + 42; d += 5) {
    const px = w / 2 + (d - deg) * ppd;
    if (px < 4 || px > w - 4) continue;
    const dd = ((d % 360) + 360) % 360;
    const major = dd % 30 === 0;
    x.strokeStyle = major ? ink : sub2;
    x.beginPath(); x.moveTo(px, h - 5); x.lineTo(px, h - 5 - (major ? 8 : dd % 10 === 0 ? 6 : 4)); x.stroke();
    if (major) {
      const card = CARD4[dd];
      x.font = `${card ? '700 ' : ''}10px ui-monospace, monospace`;
      x.fillStyle = dd === 0 ? acc : (card ? ink : sub2);
      x.fillText(card || String(dd / 10).padStart(2, '0'), px, 5);
    }
  }
  const fadeW = Math.min(34, w * 0.13);                // ends melt out like a real tape
  x.globalCompositeOperation = 'destination-out';
  let g = x.createLinearGradient(0, 0, fadeW, 0);
  g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = g; x.fillRect(0, 0, fadeW, h);
  g = x.createLinearGradient(w, 0, w - fadeW, 0);
  g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
  x.fillStyle = g; x.fillRect(w - fadeW, 0, fadeW, h);
  x.globalCompositeOperation = 'source-over';
  x.fillStyle = acc;                                   // lubber line
  x.beginPath(); x.moveTo(w / 2 - 4, 0); x.lineTo(w / 2 + 4, 0); x.lineTo(w / 2, 6); x.closePath(); x.fill();
  x.fillRect(w / 2 - 0.5, 6, 1, h - 10);
}
document.getElementById('compass').addEventListener('click', () => {
  track('compass_click', { dir: 'N' });                  // always snaps north
  if (flight.on) { flight.yaw = 0; return; }             // point the plane north
  if (stargaze.on) { stargaze.yaw = 0; return; }         // face north under the stars
  const t = controls.target, p = camera.position, ry = world.rotation.y;
  const d = Math.hypot(p.x - t.x, p.z - t.z);
  p.x = t.x + Math.sin(ry) * d;                          // due terrain-south of the target
  p.z = t.z + Math.cos(ry) * d;
  controls.update();
});
async function snapshot() {
  track('screenshot');
  const btn = document.getElementById('snapbtn');
  const pr = renderer.getPixelRatio();
  const sDpr = starUniforms.uDpr.value;
  starUniforms.uDpr.value = sDpr * Math.min(4, pr * 2) / pr;   // stars keep their size in the supersample
  renderer.setPixelRatio(Math.min(4, pr * 2));           // documented 2× supersample
  renderer.render(scene, camera);
  const shot = renderer.domElement.toDataURL('image/png');
  renderer.setPixelRatio(pr);
  starUniforms.uDpr.value = sDpr;
  const img = new Image();
  await new Promise(res => { img.onload = res; img.src = shot; });
  const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
  const x = c.getContext('2d');
  if (neonOn) x.filter = NN_FILTER;                      // bake the noir grade into the photo
  x.drawImage(img, 0, 0);
  x.filter = 'none';
  if (neonOn) {                                          // …and the vignette
    const vg = x.createRadialGradient(c.width / 2, c.height * 0.45, c.height * 0.5,
                                      c.width / 2, c.height * 0.45, c.width * 0.72);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.62)');
    x.fillStyle = vg; x.fillRect(0, 0, c.width, c.height);
  }
  const pad = Math.round(c.width * 0.012), fs = Math.max(14, Math.round(c.width * 0.011));
  x.textBaseline = 'bottom'; x.shadowColor = 'rgba(0,0,0,.65)'; x.shadowBlur = fs * 0.4;
  x.font = `600 ${fs}px ui-monospace, monospace`;
  x.fillStyle = 'rgba(255,255,255,.82)';
  x.textAlign = 'left';
  x.fillText('Hong Kong Sandbox 香港沙盒 · wiiiimm', pad, c.height - pad);
  const attrEl = document.getElementById('mapattr');     // tile attribution rides along
  if (attrEl.textContent && getComputedStyle(attrEl).display !== 'none') {
    x.textAlign = 'right';
    x.font = `${Math.round(fs * 0.8)}px ui-monospace, monospace`;
    x.fillText(attrEl.textContent, c.width - pad, c.height - pad);
  }
  const n = new Date();
  const ts = `${n.getFullYear()}${String(n.getMonth() + 1).padStart(2, '0')}${String(n.getDate()).padStart(2, '0')}-${String(n.getHours()).padStart(2, '0')}${String(n.getMinutes()).padStart(2, '0')}`;
  const a = document.createElement('a');
  a.download = `hongkong-sandbox_${document.getElementById('src').value}_${ts}.png`;
  a.href = c.toDataURL('image/png');
  a.click();
  btn.classList.add('on'); setTimeout(() => btn.classList.remove('on'), 400);
}
document.getElementById('snapbtn').addEventListener('click', snapshot);

// ---- HKO radar + satellite loop (HKS-74 / HKS-79) ---------------------------
// Animated HKO imagery, embedded straight from hko.gov.hk (the images hotlink
// fine; CORS is irrelevant for <img>). Two views share the circular frame:
//   • radar    — rainfall, HK-centred, 64/128/256 km, HKT 6-min cadence; rotates
//                with the compass so it aligns with the 3D scene.
//   • satellite— Himawari IR, wide (x2M) / local (x8M), UTC 10-min cadence. Lets
//                you see a typhoon while it's still out at sea, beyond radar range.
// Both views rotate with the compass so they align with the 3D scene.
// Frame timestamps are computed client-side (rounded to the cadence, backed off
// one frame for publish lag) so we never need the CORS-less frame-list JSON. A
// frame that 404s (not published yet) is skipped. © Hong Kong Observatory.
let radarImg = document.getElementById('radar-img');
let wxMode = 'radar';                                  // 'radar' | 'sat'
let radarRange = '064', satZoom = 'x2M';               // radar: 064|128|256 · sat: x2M(wide)|x8M(local)
let radarPlaying = true, radarRunning = false, radarReveal = false;
let radarRot = 0;   // continuous (unwrapped) rotation so the dial never spins the long way across the 0/360 seam
let radarBig = false;   // size toggle (default ↔ enlarged)
let radarFrames = [], radarIdx = 0, radarAnimT = null, radarRefreshT = null;
const radarTimeEl = document.getElementById('radar-time');
const p2 = n => String(n).padStart(2, '0');
// stamps YYYYMMDDHHMM[SS] for a cadence in minutes; `utc` false = shift to HKT fields
function wxStamps(n, stepMin, utc, secs) {
  const t = new Date(Date.now() + (utc ? 0 : 8 * 3.6e6));
  t.setUTCSeconds(0, 0);
  t.setUTCMinutes(t.getUTCMinutes() - (t.getUTCMinutes() % stepMin) - stepMin);   // newest published mark
  const out = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(t.getTime() - i * stepMin * 60000);
    out.push(`${d.getUTCFullYear()}${p2(d.getUTCMonth()+1)}${p2(d.getUTCDate())}${p2(d.getUTCHours())}${p2(d.getUTCMinutes())}${secs ? '00' : ''}`);
  }
  return out;                                          // oldest → newest
}
const radarUrl = ts => `https://www.hko.gov.hk/wxinfo/radars/rad_${radarRange}_png/2d${radarRange}nradar_${ts}.jpg`;
const satUrl   = ts => `https://www.hko.gov.hk/wxinfo/intersat/satellite/image/images/h8_ir_${satZoom}_${ts}.jpg`;
const isSat = () => wxMode === 'sat';
function frameStamps() { return isSat() ? wxStamps(10, 10, true, true) : wxStamps(12, 6, false, false); }
function frameUrl(ts)  { return isSat() ? satUrl(ts) : radarUrl(ts); }
// satellite stamps are UTC → show HKT HH:MM; radar stamps are already HKT
function stampLabel(ts) {
  if (!isSat()) return `${ts.slice(8,10)}:${ts.slice(10,12)}`;
  const d = new Date(Date.UTC(+ts.slice(0,4), +ts.slice(4,6)-1, +ts.slice(6,8), +ts.slice(8,10), +ts.slice(10,12)));
  d.setUTCHours(d.getUTCHours() + 8);
  return `${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())}`;
}
function loadFrames() {
  radarFrames = frameStamps().map(ts => { const im = new Image(); im.src = frameUrl(ts); im.dataset.ts = ts; return im; });
  radarIdx = 0;
}
function radarTick() {
  if (!radarFrames.length) return;
  for (let k = 0; k < radarFrames.length; k++) {       // advance to the next frame that actually loaded
    radarIdx = (radarIdx + 1) % radarFrames.length;
    const im = radarFrames[radarIdx];
    if (im.complete && im.naturalWidth > 0) {
      radarImg.src = im.src;
      radarTimeEl.textContent = stampLabel(im.dataset.ts);   // HKT HH:MM
      if (radarReveal) { radarReveal = false; radarImg.style.opacity = '1'; }   // fade the first frame of a switch/reload in
      return;
    }
  }
}
// The HUD floats bottom-right and runs with live weather (started/stopped by
// setLiveMode) rather than a standalone overlay toggle.
const radarHudEl = document.getElementById('radarhud');
function startRadar() {
  radarRunning = true;
  radarHudEl.classList.add('show');
  document.body.classList.add('radar-on');   // GPS button sits above the radar; drops to the camera button when off
  if (radarImg) radarImg.style.opacity = '0';   // fade the current view out; the first fresh frame fades back in
  radarReveal = true;
  loadFrames();
  radarTick();                                  // try to reveal a cached frame immediately, else the interval catches it
  clearInterval(radarAnimT); radarAnimT = setInterval(() => { if (radarPlaying) radarTick(); }, 220);
  clearInterval(radarRefreshT); radarRefreshT = setInterval(loadFrames, (isSat() ? 10 : 6) * 60000);
}
function stopRadar() {
  radarRunning = false;
  radarHudEl.classList.remove('show');
  document.body.classList.remove('radar-on');
  clearInterval(radarAnimT); clearInterval(radarRefreshT);
}

// ---- curved SVG tabs around the dial -----------------------------------------
// viewBox 176×176; tab bands are annular sectors between ri and ro, labels ride a
// mid-band arc. Top band = mode (radar/sat), bottom band = range/zoom.
const RF = { cx: 88, cy: 88, ri: 60, ro: 84, rt: 73 };
const rfPolar = (r, deg) => { const a = (deg - 90) * Math.PI / 180; return [RF.cx + r * Math.cos(a), RF.cy + r * Math.sin(a)]; };
const rfPt = (r, d) => rfPolar(r, d).map(n => n.toFixed(2)).join(' ');
function rfSector(a0, a1) {                      // filled annular sector, clockwise a0→a1
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
  return `M${rfPt(RF.ro, a0)} A${RF.ro} ${RF.ro} 0 ${large} 1 ${rfPt(RF.ro, a1)} L${rfPt(RF.ri, a1)} A${RF.ri} ${RF.ri} 0 ${large} 0 ${rfPt(RF.ri, a0)} Z`;
}
function rfArc(r, a0, a1) {                       // open arc a0→a1 at radius r, for a label to ride
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0, sweep = a1 > a0 ? 1 : 0;
  return `M${rfPt(r, a0)} A${r} ${r} 0 ${large} ${sweep} ${rfPt(r, a1)}`;
}
function rfLabelSvg(d, top) {                     // label follows the mid-band arc (upright top & bottom)
  const id = 'rflab-' + d.key;
  // top band reads left→right along the arc; bottom band reverses so it isn't upside-down
  const path = top ? rfArc(RF.rt, d.a0, d.a1) : rfArc(RF.rt, d.a1, d.a0);
  return `<path id="${id}" d="${path}" fill="none"/>` +
    `<text class="rf-lab${d.on ? ' on' : ''}"><textPath href="#${id}" startOffset="50%">${d.lab}</textPath></text>`;
}
// build the tab dial; state- and locale-dependent, so applyLocale/applyState call it too
function renderWxviewControls() {
  const svg = document.getElementById('rf-tabs');
  if (!svg) return;
  const modes = [
    { a0: -78, a1: -3, ac: -40.5, key: 'radar', lab: t('radar.title'), on: !isSat() },
    { a0: 3,   a1: 78, ac: 40.5,  key: 'sat',   lab: t('sat.title'),   on: isSat() },
  ];
  const opts = isSat() ? [['x2M', t('sat.wide')], ['x8M', t('sat.local')]]
                       : [['064', '64km'], ['128', '128km'], ['256', '256km']];
  const cur = isSat() ? satZoom : radarRange;
  const bStart = 102, bEnd = 258, gap = 4, n = opts.length, w = (bEnd - bStart - gap * (n - 1)) / n;
  const ranges = opts.map(([v, l], i) => { const a0 = bStart + i * (w + gap), a1 = a0 + w; return { a0, a1, ac: (a0 + a1) / 2, key: v, lab: l, on: v === cur }; });
  const tab = (d, grp) => `<path class="rf-tab${d.on ? ' on' : ''}" data-grp="${grp}" data-key="${d.key}" ` +
    `role="button" tabindex="0" aria-pressed="${d.on}" aria-label="${d.lab}" d="${rfSector(d.a0, d.a1)}"/>`;
  // size toggle: a round button in the empty left-side gap (270°)
  const [sx, sy] = rfPolar(RF.rt, 270);
  const sizeBtn = `<g class="rf-size" data-size="1" role="button" tabindex="0" ` +
    `aria-label="${radarBig ? t('rf.smaller') : t('rf.bigger')}"><circle cx="${sx.toFixed(2)}" cy="${sy.toFixed(2)}" r="11"/>` +
    `<text class="rf-glyph" x="${sx.toFixed(2)}" y="${sy.toFixed(2)}">${radarBig ? '−' : '+'}</text></g>`;
  svg.innerHTML =
    modes.map(m => tab(m, 'mode')).join('') + ranges.map(r => tab(r, 'range')).join('') + sizeBtn +
    modes.map(m => rfLabelSvg(m, true)).join('') + ranges.map(r => rfLabelSvg(r, false)).join('');
  // radar carries an HKO legend strip on the right → crop to the left square; satellite is a full map → centre it.
  if (radarImg) radarImg.style.objectPosition = isSat() ? '50% 50%' : 'left center';
}
function setWxMode(m) {
  if (wxMode === m) return;
  wxMode = m;
  renderWxviewControls();
  if (radarRunning) startRadar();
}
function activateRfTab(target) {
  if (target.closest('[data-size]')) {   // size toggle — no reload, not persisted
    radarBig = !radarBig; radarHudEl.classList.toggle('big', radarBig); renderWxviewControls();
    track('radar', { expand: radarBig });
    return;
  }
  const p = target.closest('path[data-grp]'); if (!p) return;
  if (p.dataset.grp === 'mode') { setWxMode(p.dataset.key); track('radar', { mode: p.dataset.key }); }   // radar <-> satellite (HKS-74/79/89)
  else { if (isSat()) satZoom = p.dataset.key; else radarRange = p.dataset.key; renderWxviewControls(); if (radarRunning) startRadar(); track('radar', { size: p.dataset.key }); }   // range 064/128/256 or sat zoom x2M/x8M
  syncUrl();   // write the new mode/range into the address bar (the dial lives outside #panel)
}
const rfTabsEl = document.getElementById('rf-tabs');
rfTabsEl.addEventListener('click', e => activateRfTab(e.target));
rfTabsEl.addEventListener('keydown', e => {   // keyboard access for the SVG tabs (a11y)
  if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
  if (!e.target.closest('[data-grp],[data-size]')) return;
  e.preventDefault(); activateRfTab(e.target);
});

// ---- live spatial cloud field (HKS-101) --------------------------------------
// When live-weather sync is ON, the cloud layer stops being uniform: a coarse
// cover grid (0..1 per cell, over the map extent) says how cloudy each district
// actually is, and the sprites / ground shadows / stars follow it. Two sources,
// best first, with graceful degradation:
//   • satellite — the same HKO Himawari IR frames the wx HUD hotlinks (© Hong
//     Kong Observatory, fetched at runtime, never stored), sampled into the grid
//     through an offscreen canvas. Pixel access needs a CORS grant; hko.gov.hk
//     currently sends no Access-Control-Allow-Origin, so the anonymous load is
//     attempted, its failure detected, and the fallback takes over — if HKO ever
//     enables CORS (or a proxy is added), the spatial path lights up by itself.
//   • procedural — wind-advected, seeded value noise whose coverage tracks a
//     live territory cloudiness derived from HKO obs (weather icon + humidity +
//     rain). Live-driven and believable, just less spatially precise.
// The grid refreshes with the live sync (5 min), never per frame; per-frame cost
// is one bilinear lookup per sprite. Manual toggles and storm presets bypass the
// field entirely (cloudFieldActive gates every consumer on liveMode).
const cloudField = {
  data: null,       // Float32Array(N*N), row-major over the map extent, 0..1 cover
  form: null,       // raw procedural noise (pre-threshold) — HKS-69 local re-shaping
  N: 48,            // grid resolution — ~1.2 km cells on the HK map
  src: '',          // 'sat' | 'proc'
  mean: 0.6,        // field mean (blended into the ground-shadow strength)
  amt: 0.6,         // live territory cloudiness 0..1 (procedural density, from obs)
  ox: 0, oz: 0,     // wind-advection offset (world units; the pattern drifts with the deck)
  satDead: 0,       // consecutive satellite failures; ≥2 → stop retrying this session
  seed: Math.random() * 100,
};
const _cfV = new THREE.Vector3();   // scratch: viewer position in world-local xz
const cloudFieldActive = () => liveMode && weather.clouds && !!cloudField.data;

// bilinear cover lookup at a world-local (x, z) — the only per-frame math.
// The procedural field wraps (its noise lattice tiles), the satellite crop clamps.
function cloudCoverAt(x, z) {
  const f = cloudField, d = f.data;
  if (!d) return 1;
  const b = bounds(), N = f.N, wrap = f.src === 'proc';
  let u = (x - f.ox) / (2 * b.halfX) + 0.5, v = (z - f.oz) / (2 * b.halfZ) + 0.5;
  let gx, gz, x0, z0, x1, z1;
  if (wrap) {
    u -= Math.floor(u); v -= Math.floor(v);
    gx = u * N; gz = v * N;
    x0 = gx | 0; z0 = gz | 0; x1 = (x0 + 1) % N; z1 = (z0 + 1) % N;
    if (x0 >= N) x0 = N - 1; if (z0 >= N) z0 = N - 1;   // guard u/v == 1 exactly
  } else {
    u = Math.max(0, Math.min(1, u)); v = Math.max(0, Math.min(1, v));
    gx = u * (N - 1); gz = v * (N - 1);
    x0 = gx | 0; z0 = gz | 0; x1 = Math.min(N - 1, x0 + 1); z1 = Math.min(N - 1, z0 + 1);
  }
  const fx = gx - x0, fz = gz - z0;
  const a = d[z0 * N + x0] * (1 - fx) + d[z0 * N + x1] * fx;
  const c = d[z1 * N + x0] * (1 - fx) + d[z1 * N + x1] * fx;
  let cov = a * (1 - fz) + c * fz;
  // HKS-69: when live obs give a real per-district cloud AMOUNT (the WxField
  // 'cloud' field — humidity + rainfall, see cloudFromObs), the local amount
  // comes from that field and the procedural noise only shapes the lumps:
  // the same raw lattice (f.form) is re-thresholded per sample with the LOCAL
  // amount instead of the territory-wide cloudField.amt. A dry low-humidity
  // district then genuinely clears while a humid one stays overcast. Only the
  // procedural source is reshaped — the satellite field is already real
  // spatial data — and an empty/no-data 'cloud' field falls back to the
  // territory-amount grid baked into f.data (HKS-101 standalone behaviour).
  if (f.src === 'proc' && f.form) {
    const cf = WxField.get('cloud');
    if (cf && !cf.empty) {
      const fm = f.form;
      const na = fm[z0 * N + x0] * (1 - fx) + fm[z0 * N + x1] * fx;
      const nc = fm[z1 * N + x0] * (1 - fx) + fm[z1 * N + x1] * fx;
      const n = na * (1 - fz) + nc * fz;
      const th = 0.95 - cf.sample(x, z) * 0.9;   // buildProcCloudField's ramp, local amount
      let cc = Math.max(0, Math.min(1, (n - th) / 0.35));
      cov = cc * cc * (3 - 2 * cc);
    }
  }
  // HKS-69 coordination hook: rain falls FROM cloud — floor the local cover
  // with the live rainfall field so an actively raining district never reads
  // as clear sky. Sample-time only and capped at 0.8, so the cloud field
  // itself (HKS-101, satellite/procedural) stays untouched.
  const rd = rainDensityAt(x, z) * 0.8;
  return rd > cov ? rd : cov;
}

// ---- HKS-69: regional rain density helpers ----------------------------------
// mm (district past-hour rainfall) -> rain particle density 0..1. A 0.1 mm
// deadband stops IDW bleed from wetting genuinely dry districts; above it,
// light rain keeps a visible floor (0.25) and ramps to full sheets at ≥10 mm.
function rainMmToDensity(mm) {
  return mm <= 0.1 ? 0 : Math.min(1, 0.25 + 0.75 * (mm / 10));
}
// Local rain density at world-local (x, z): 0 unless live sync is on AND at
// least one district actually reports rain — an all-zero field carries no
// spatial signal (icon-only "rainy" keeps the uniform territory-wide rain).
function rainDensityAt(x, z) {
  if (!liveMode) return 0;
  const f = WxField.get('rain');
  return (f && !f.empty && f.max > 0) ? rainMmToDensity(f.sample(x, z)) : 0;
}

// territory cloudiness 0..1 from what syncLiveWeather already fetched: the HKO
// weather-icon code is the dominant signal, humidity nudges it, rain floors it.
// (Approximate by design — HKO publishes no gridded cloud-cover product.)
const CLOUD_AMT_ICON = { 50: .05, 51: .35, 52: .55, 53: .62, 54: .72, 60: .82, 61: .97,
  62: .9, 63: .95, 64: 1, 65: 1, 70: .05, 71: .1, 72: .15, 73: .2, 74: .25, 75: .3,
  76: .82, 77: .25, 80: .55, 81: .3, 82: .6, 83: .85, 84: .8, 85: .6 };
function cloudAmtFromObs(code, rh, rainMax) {
  let a = CLOUD_AMT_ICON[code];
  if (a == null) a = 0.6;
  if (isFinite(rh)) a += (rh - 78) / 60 * 0.15;
  if (rainMax > 0) a = Math.max(a, 0.85);
  return Math.max(0, Math.min(1, a));
}

// HKS-69: LOCAL cloudiness 0..1 for one spot from real obs — humidity ramps it
// (dry air ⇒ clear sky, near-saturated ⇒ overcast) and rainfall floors it (an
// actively raining district is overcast by definition). Deliberately steeper
// than cloudAmtFromObs: this drives the visible sunny-here/overcast-there
// split across the map, so a genuinely dry low-humidity district must read
// near-clear. Feeds the WxField 'cloud' field; consumed by cloudCoverAt.
function cloudFromObs(rhPct, rainMm) {
  let c = isFinite(rhPct) ? Math.max(0, Math.min(1, (rhPct - 55) / 40)) * 0.9 : 0.5;
  if (rainMm > 0.1) c = Math.max(c, 0.75 + 0.25 * Math.min(1, rainMm / 10));
  return Math.max(0, Math.min(1, c));
}

// fallback: 3-octave seeded value noise on a wrapping lattice, shaped so roughly
// `amt` of the sky is covered — the clear side of the threshold really hits 0
function buildProcCloudField() {
  const f = cloudField, N = f.N;
  const d = (f.data && f.src === 'proc') ? f.data : new Float32Array(N * N);
  const rnd = (i, j, o) => { const s = Math.sin(i * 127.1 + j * 311.7 + o * 74.7 + f.seed) * 43758.5453; return s - Math.floor(s); };
  const val = (u, v, P, o) => {   // one wrapped value-noise octave, period P lattice cells
    const x = u * P, y = v * P;
    const xi = Math.floor(x), yi = Math.floor(y);
    const x0 = ((xi % P) + P) % P, y0 = ((yi % P) + P) % P;
    const x1 = (x0 + 1) % P, y1 = (y0 + 1) % P;
    const fx = x - xi, fy = y - yi;
    const sx = fx * fx * (3 - 2 * fx), sy = fy * fy * (3 - 2 * fy);
    const a = rnd(x0, y0, o) * (1 - sx) + rnd(x1, y0, o) * sx;
    const c = rnd(x0, y1, o) * (1 - sx) + rnd(x1, y1, o) * sx;
    return a * (1 - sy) + c * sy;
  };
  // f.form keeps the raw pre-threshold noise so cloudCoverAt can re-threshold
  // it per sample with a LOCAL amount (HKS-69 'cloud' field) — same lumps,
  // locally-true coverage. f.data stays the territory-amount grid (fallback).
  const fm = (f.form && f.src === 'proc') ? f.form : new Float32Array(N * N);
  const th = 0.95 - f.amt * 0.9;   // the coverage threshold slides with live cloudiness
  let sum = 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const u = i / N, v = j / N;
    const n = val(u, v, 4, 1) * 0.55 + val(u, v, 8, 2) * 0.3 + val(u, v, 16, 3) * 0.15;
    fm[j * N + i] = n;
    let c = (n - th) / 0.35;
    c = Math.max(0, Math.min(1, c));
    sum += (d[j * N + i] = c * c * (3 - 2 * c));
  }
  f.data = d; f.form = fm; f.mean = sum / (N * N);
  if (f.src !== 'proc') {
    f.src = 'proc'; f.ox = f.oz = 0;
    console.info('[HKS-101] cloud field: procedural, live-driven (HKO satellite pixels not readable in-browser)');
  }
}

// primary: sample the HKO Himawari IR "local" (x8M) crop. Approximate linear
// georef of the 750×749 frame, calibrated against the Taiwan / Hainan / Pearl
// River estuary coastlines (~±10 px ≈ ±0.2°; good to a couple of grid cells):
const SAT_GEO = { lon0: 106.0, pxPerLon: 44.2, lat0: 29.7, pxPerLat: 45.0 };
const satFieldUrl = ts => `https://www.hko.gov.hk/wxinfo/intersat/satellite/image/images/h8_ir_x8M_${ts}.jpg`;
function buildSatCloudField(img) {
  const f = cloudField, N = f.N, g = curG;
  if (!g) return false;
  const cv = document.createElement('canvas');
  cv.width = img.naturalWidth; cv.height = img.naturalHeight;
  const ctx = cv.getContext('2d', { willReadFrequently: true });
  ctx.drawImage(img, 0, 0);
  let px;
  try { px = ctx.getImageData(0, 0, cv.width, cv.height); }
  catch (e) { return false; }               // tainted canvas — no CORS pixel grant
  const P = px.data, Wp = px.width, Hp = px.height;
  const d = new Float32Array(N * N);
  let sum = 0;
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    // field cell → grid col/row → HK1980 E/N → lon/lat → satellite pixel
    const c = i / (N - 1) * (W - 1), r = j / (N - 1) * (H - 1);
    const ll = enToLL(g.aE * c + g.bE, g.aN * r + g.bN);
    const sx = Math.round((ll.lon - SAT_GEO.lon0) * SAT_GEO.pxPerLon);
    const sy = Math.round((SAT_GEO.lat0 - ll.lat) * SAT_GEO.pxPerLat);
    // 3×3 box — the IR pixel pitch (~2.5 km here) is near our cell pitch anyway
    let lum = 0, sat = 0, n = 0;
    for (let oy = -1; oy <= 1; oy++) for (let ox = -1; ox <= 1; ox++) {
      const qx = sx + ox, qy = sy + oy;
      if (qx < 0 || qy < 0 || qx >= Wp || qy >= Hp) continue;
      const k = (qy * Wp + qx) * 4, R = P[k], G = P[k + 1], B = P[k + 2];
      if (Math.min(R, G, B) >= 250) continue;   // burnt-in coastline overlay, not cloud
      lum += (R + G + B) / 3;
      sat += Math.max(R, G, B) - Math.min(R, G, B);
      n++;
    }
    if (!n) { sum += (d[j * N + i] = f.amt); continue; }
    lum /= n; sat /= n;
    // IR: bright grey/white = cold cloud tops. Land/sea show through darker and
    // colour-saturated (green/tan/blue), so saturation votes against cloud.
    let cvr = Math.max(0, Math.min(1, (lum - 115) / 100)) * Math.max(0, 1 - sat / 80);
    sum += (d[j * N + i] = cvr * cvr * (3 - 2 * cvr));
  }
  f.data = d; f.mean = sum / (N * N); f.ox = f.oz = 0;
  if (f.src !== 'sat') {
    f.src = 'sat';
    console.info('[HKS-101] cloud field: HKO Himawari IR satellite sampling active');
  }
  return true;
}

// refresh the field: try the newest few satellite frames (anonymous CORS load;
// a 404 or a CORS-refused response both land in onerror), else go procedural.
// Called by syncLiveWeather (5 min cadence) and on a source/bounds rebuild.
let _cfImg = null;   // in-flight loader — a newer refresh supersedes it
function refreshCloudField() {
  if (!liveMode) return;
  if (cloudField.satDead >= 2) { buildProcCloudField(); return; }
  const stamps = wxStamps(3, 10, true, true).reverse();   // newest first, ~30 min back
  let k = 0, timer = 0;
  const attempt = () => {
    if (k >= stamps.length) { cloudField.satDead++; buildProcCloudField(); return; }
    const im = new Image();
    _cfImg = im;
    im.crossOrigin = 'anonymous';           // pixel readback needs the CORS grant
    const fail = () => { clearTimeout(timer); if (_cfImg !== im) return; k++; attempt(); };
    timer = setTimeout(fail, 12000);        // a hung load must not strand the field
    im.onerror = fail;
    im.onload = () => {
      clearTimeout(timer);
      if (_cfImg !== im) return;
      if (buildSatCloudField(im)) { cloudField.satDead = 0; return; }
      cloudField.satDead = 2;               // tainted canvas: CORS is off for good
      buildProcCloudField();
    };
    im.src = satFieldUrl(stamps[k]);
  };
  attempt();
}

// ---- camera framing + presets ---------------------------------------------
function bounds() {
  const halfX = W*cell/2, halfZ = H*cell/2, peakY = zmax*VE;
  return { halfX, halfZ, peakY, span: Math.max(W,H)*cell };
}
function frameCamera() {
  const b = bounds();
  controls.target.set(0, b.peakY*0.35, 0);
  // start 30° above the horizontal (sea-level) plane
  const elev = 30 * Math.PI / 180, dist = b.span * 1.1;
  camera.position.set(0, controls.target.y + dist*Math.sin(elev), dist*Math.cos(elev));
  controls.minDistance = b.span*0.04; controls.maxDistance = b.span*4;   // much more zoom range
  controls.update();
  updateClip();
}

// adaptive depth range: keeps precision (no sea z-fighting) at any zoom, and lets
// the near plane shrink when close so you can zoom right in
let clipNear = -1;
function updateClip() {
  const d = camera.position.distanceTo(controls.target);
  const near = Math.max(d * 0.02, 0.5);
  if (clipNear < 0 || Math.abs(near - clipNear) / clipNear > 0.04) {
    camera.near = near; camera.far = d * 3 + bounds().span * 2.5;
    camera.updateProjectionMatrix(); clipNear = near;
  }
}
function southView() { const b = bounds(); camera.position.set(0, b.peakY*1.2, b.span*1.1); controls.target.set(0, b.peakY*0.3, 0); controls.update(); }
function topView()   { const b = bounds(); camera.position.set(0, b.span*1.4, 0.01);       controls.target.set(0, 0, 0);           controls.update(); }

// ---- UI wiring -------------------------------------------------------------
document.getElementById('src').addEventListener('change', e => {
  if (e.isTrusted) track('map_source', { source: e.target.value });
  loadSource(e.target.value).then(() => { if (liveMode) syncLiveTide(); }).catch(err => {
    document.getElementById('note').textContent = t('note.loadfail') + ': ' + err.message; console.error(err);
  });
});
document.getElementById('surf').addEventListener('change', e => { applyStyle(e.target.value); if (e.isTrusted) track('map_surface', { surface: e.target.value }); });
document.getElementById('bg').addEventListener('change', e => { applyBg(e.target.value); if (e.isTrusted) track('theme', { bg: e.target.value }); });
document.getElementById('ve').addEventListener('input', e => {
  VE = parseFloat(e.target.value); document.getElementById('vev').textContent = VE.toFixed(1); applyVE();
});
{ const sl = document.getElementById('skinlift'), slv = document.getElementById('skinliftv');   // HKS-108: overlay drape height in real metres (0.2–15 m); world lift = skinLift·VE
  const sync = () => { slv.textContent = skinLift.toFixed(skinLift < 10 ? 1 : 0) + ' m'; };
  sl.addEventListener('input', () => { skinLift = parseFloat(sl.value); sync(); applyVE(); });    // live re-drape
  sl.addEventListener('change', e => { if (e.isTrusted) track('overlay_height', { m: skinLift }); });   // once on commit
  sync(); }
document.getElementById('meshlines').addEventListener('change', e => { wireOverlay.visible = e.target.checked; if (e.isTrusted) track('layer_toggle', { layer: 'meshlines', on: e.target.checked }); });
const meshdens = document.getElementById('meshdens'), meshdensv = document.getElementById('meshdensv');
const densStep = () => 13 - parseInt(meshdens.value, 10);   // slider right = finest (step 1)
meshdens.addEventListener('input', () => { const s = densStep(); meshdensv.textContent = s === 1 ? t('dens.full') : '÷' + s; });
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
// buttons fire 'click', not the change/input the panel listens to, so sync the URL explicitly
const rot = d => () => { texRot = Math.round((texRot + d) * 10) / 10; applyTexRot(); syncUrl(); track('topo_rotate', { delta: d }); };
document.getElementById('toporotL').addEventListener('click', rot(-1));
document.getElementById('toporotLf').addEventListener('click', rot(-0.2));
document.getElementById('toporotRf').addEventListener('click', rot(0.2));
document.getElementById('toporotR').addEventListener('click', rot(1));
document.getElementById('toporot0').addEventListener('click', () => { texRot = 0; applyTexRot(); syncUrl(); track('topo_rotate', { delta: 0 }); });
document.getElementById('water').addEventListener('change', e => { sea.visible = e.target.checked; if (e.isTrusted) track('layer_toggle', { layer: 'water', on: e.target.checked }); });
document.getElementById('labels').addEventListener('change', e => { labels.forEach(l => l.div.style.display = e.target.checked ? '' : 'none'); if (e.isTrusted) track('layer_toggle', { layer: 'labels', on: e.target.checked }); });
document.getElementById('landmarks').addEventListener('change', e => { if (e.isTrusted) track('layer_toggle', { layer: 'landmarks', on: e.target.checked }); });

// ---- GPX trail import (HKS-106) --------------------------------------------
// Drop or pick one/more .gpx files; each <trk> (or <rte>) drapes on the terrain
// as a coloured polyline. Projected via the same WGS84→HK1980→grid path as the
// GPS marker (gpsToGrid) + sampleEtri for height, so trails sit on the surface and
// re-drape on source/VE change (applyVE calls redrapeGpx). Random distinct
// colour per trail, user-reassignable. Entirely client-side, session-only —
// nothing is uploaded or stored, and it's not URL-serialised (GPX is too big).
let gpxGroup = null;
const gpxTrails = [];                                    // { name, pts:[[lat,lon]], color, line, visible, off }
const gpxColor = i => new THREE.Color().setHSL(((i * 137.508) % 360) / 360, 0.72, 0.56);   // golden-angle → distinct hues
let gpxSeq = 0;                                          // monotonic — no number reuse after a removal
const gpxName = () => `${t('gpx.trail')} #${++gpxSeq}`;  // locale-aware default; user-renamable (GPX <name> ignored, per spec)
function ensureGpxGroup() { if (!gpxGroup) gpxGroup = new THREE.Group(); if (world && gpxGroup.parent !== world) world.add(gpxGroup); }
function drapeSegments(pts, breaks) {                    // [[lat,lon]] → flat segment-pair verts; breaks at off-map gaps AND <trkseg> discontinuities (codex)
  const verts = [], segs = []; let off = 0; const lift = skinOffset() * 1.6;
  let prev = null, prevIn = false, prevI = -1;
  for (let i = 0; i < pts.length; i++) {
    const [lat, lon] = pts[i];
    const g = gpsToGrid(lat, lon), inB = !!(g && g.inBounds);
    if (!inB) off++;
    const v = inB ? new THREE.Vector3((g.col - W / 2) * cell, sampleEtri(g.col, g.row) * VE + lift, (g.row - H / 2) * cell) : null;   // HKS-108: drape on the rendered triangles
    const brk = breaks && breaks.has(i);                 // don't chord across a segment discontinuity
    if (prevIn && inB && !brk) { verts.push(prev.x, prev.y, prev.z, v.x, v.y, v.z); segs.push([prevI, i]); }   // both on-map → emit segment + its pts indices
    prev = v; prevIn = inB; prevI = i;
  }
  return { verts, off, segs };
}
// ---- inline SVG icons (line-style, Feather/Lucide MIT lineage) -------------
const ICON_PATHS = {
  eye: '<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z"/><circle cx="12" cy="12" r="3"/>',
  'eye-off': '<path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><path d="M17.94 17.94A10 10 0 0 1 12 20C5 20 1 12 1 12a18.4 18.4 0 0 1 5.06-5.94"/><line x1="1" y1="1" x2="23" y2="23"/>',
  play: '<path d="M7 4.5 20 12 7 19.5Z" fill="currentColor" stroke="none"/>',
  pause: '<path d="M7 4.5h3.4v15H7zM13.6 4.5H17v15h-3.4z" fill="currentColor" stroke="none"/>',
  target: '<circle cx="12" cy="12" r="8.5"/><line x1="12" y1="1.5" x2="12" y2="5.2"/><line x1="12" y1="18.8" x2="12" y2="22.5"/><line x1="1.5" y1="12" x2="5.2" y2="12"/><line x1="18.8" y1="12" x2="22.5" y2="12"/><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/>',
  x: '<line x1="5.5" y1="5.5" x2="18.5" y2="18.5"/><line x1="18.5" y1="5.5" x2="5.5" y2="18.5"/>',
  'chevron-down': '<path d="M6 9l6 6 6-6"/>',
  'chevron-up': '<path d="M6 15l6-6 6 6"/>'
};
const svgIcon = n => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON_PATHS[n]}</svg>`;

// ---- GPX per-trail profile: real-world stats + elevation chart (HKS-106) ----
// Map-independent — computed from the GPX lat/lon/ele/time, so it works even for
// a trail that lands off the loaded HK map. Cached on tr.stats (pts never change).
function haversine(aLat, aLon, bLat, bLon) {
  const R = 6371000, r = Math.PI / 180;
  const dLa = (bLat - aLat) * r, dLo = (bLon - aLon) * r, la1 = aLat * r, la2 = bLat * r;
  const h = Math.sin(dLa / 2) ** 2 + Math.cos(la1) * Math.cos(la2) * Math.sin(dLo / 2) ** 2;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(h)));
}
function trailStats(tr) {
  if (tr.stats) return tr.stats;
  const pts = tr.pts, eles = tr.eles, times = tr.times, breaks = tr.breaks;
  let dist = 0, gain = 0, loss = 0, minE = Infinity, maxE = -Infinity;
  const samples = []; let lastE = null;
  for (let i = 0; i < pts.length; i++) {
    const brk = breaks && breaks.has(i);                 // <trkseg> discontinuity — the leg into it isn't a real move (codex P2)
    if (i > 0 && !brk) dist += haversine(pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1]);
    const e = eles[i];
    if (e != null) {
      if (lastE != null && !brk) { const de = e - lastE; if (de > 0) gain += de; else loss -= de; }   // no ascent/descent across a gap
      lastE = e; minE = Math.min(minE, e); maxE = Math.max(maxE, e);
      samples.push({ d: dist, e });
    }
  }
  const t0 = times[0], t1 = times[times.length - 1];
  const durMs = (tr.hasTime && t0 != null && t1 != null && t1 > t0) ? (t1 - t0) : 0;
  const avgKmh = durMs > 0 ? (dist / (durMs / 1000)) * 3.6 : 0;   // total distance ÷ total time — robust (no GPS-spike max)
  return (tr.stats = { distM: dist, gain, loss, minE: isFinite(minE) ? minE : null, maxE: isFinite(maxE) ? maxE : null, hasEle: tr.hasEle, durMs, avgKmh, samples });
}
function elevChartSvg(tr) {                                // elevation-vs-distance area chart (uniform-scaled viewBox)
  const s = trailStats(tr), sm = s.samples;
  if (!s.hasEle || sm.length < 2 || s.maxE === s.minE) return '';   // nothing to chart (no ele / flat)
  const W = 240, H = 60, pad = 3, dmax = s.distM || 1, er = (s.maxE - s.minE) || 1;
  const X = d => pad + (d / dmax) * (W - 2 * pad), Y = e => (H - pad) - ((e - s.minE) / er) * (H - 2 * pad);
  let d = `M${X(sm[0].d).toFixed(1)} ${Y(sm[0].e).toFixed(1)}`;
  for (let i = 1; i < sm.length; i++) d += ` L${X(sm[i].d).toFixed(1)} ${Y(sm[i].e).toFixed(1)}`;
  const area = `${d} L${X(sm[sm.length - 1].d).toFixed(1)} ${H - pad} L${X(sm[0].d).toFixed(1)} ${H - pad} Z`;
  const col = '#' + tr.color.getHexString();
  return `<svg class="gpxchart" viewBox="0 0 ${W} ${H}" width="100%" aria-hidden="true">`
    + `<path d="${area}" fill="${col}" fill-opacity="0.16" stroke="none"/>`
    + `<path d="${d}" fill="none" stroke="${col}" stroke-width="1.5" stroke-linejoin="round"/></svg>`;
}
function trailStatChips(tr) {                              // small text stats: distance, gain/loss, duration, avg pace
  const s = trailStats(tr), out = [];
  out.push(`${t('gpx.dist')} ${s.distM >= 1000 ? (s.distM / 1000).toFixed(1) + ' km' : Math.round(s.distM) + ' m'}`);
  if (s.hasEle && s.minE != null) out.push(`↑${Math.round(s.gain)} ↓${Math.round(s.loss)} m`);
  if (s.durMs > 0) {
    const mins = Math.round(s.durMs / 60000);
    out.push(`${t('gpx.dur')} ${mins >= 60 ? Math.floor(mins / 60) + 'h' + String(mins % 60).padStart(2, '0') : mins + ' min'}`);
    out.push(`${t('gpx.avg')} ${s.avgKmh.toFixed(1)} km/h`);
  }
  return out;
}
function fillTrailDetail(tr, el) {
  el.textContent = '';
  const chart = elevChartSvg(tr);
  if (chart) { const c = document.createElement('div'); c.className = 'gpxchartwrap'; c.innerHTML = chart; el.appendChild(c); }
  const stats = document.createElement('div'); stats.className = 'gpxstats';
  for (const p of trailStatChips(tr)) { const sp = document.createElement('span'); sp.className = 'gpxstat'; sp.textContent = p; stats.appendChild(sp); }
  el.appendChild(stats);
}

// ---- GPX start/end labels + trail playback (HKS-106) -----------------------
const GPX_GHOST_OP = 0.28;                                // whole-trail opacity while a playback dot sweeps it
const GPX_ANIM_DUR = 14000;                               // ms to replay a whole trail (real pacing when timestamps exist)
const gpxPlaying = new Set();                             // trails currently animating (driven by stepGpxAnim in the RAF loop)
let GPX_DOT_TEX = null;
function gpxDotTex() {
  if (GPX_DOT_TEX) return GPX_DOT_TEX;
  const cv = document.createElement('canvas'); cv.width = cv.height = 64;
  const c = cv.getContext('2d'), g = c.createRadialGradient(32, 32, 0, 32, 32, 32);
  g.addColorStop(0, 'rgba(255,255,255,1)'); g.addColorStop(0.5, 'rgba(255,255,255,1)'); g.addColorStop(1, 'rgba(255,255,255,0)');
  c.fillStyle = g; c.beginPath(); c.arc(32, 32, 32, 0, 7); c.fill();
  GPX_DOT_TEX = new THREE.CanvasTexture(cv); return GPX_DOT_TEX;
}
// Start/End are DOM labels (constant screen size + terrain occlusion, like the
// peak labels) anchored in HK1980 E/N so they re-project at any zoom/source. The
// Start label doubles as the on-map ▶/⏸ playback control.
function refreshGpxStartLabel(tr) {
  const s = tr.startLbl; if (!s) return;
  s.innerHTML = svgIcon(tr.playing ? 'pause' : 'play') + `<span>${t('gpx.start')}</span>`;
  const lab = t(tr.playing ? 'gpx.pause' : 'gpx.play');
  s.title = lab; s.setAttribute('aria-label', lab); s.setAttribute('aria-pressed', tr.playing ? 'true' : 'false');
}
function makeGpxLabels(tr) {
  const s = document.createElement('div'); s.className = 'gpxlbl start';
  s.setAttribute('role', 'button'); s.tabIndex = 0;                    // keyboard-operable: focusable + Enter/Space
  s.addEventListener('click', () => toggleTrailAnim(tr));
  s.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); toggleTrailAnim(tr); } });
  const e = document.createElement('div'); e.className = 'gpxlbl end'; e.textContent = t('gpx.end');
  s.style.display = e.style.display = 'none';
  document.body.append(s, e);
  tr.startLbl = s; tr.endLbl = e; refreshGpxStartLabel(tr);
}
function removeGpxLabels(tr) {
  if (tr.startLbl) { tr.startLbl.remove(); tr.startLbl = null; }
  if (tr.endLbl) { tr.endLbl.remove(); tr.endLbl = null; }
}
// project both labels each frame — reuses the peak-label occlusion + screen math
function updateGpxLabels() {
  if (!gpxTrails.length) return;
  const g = curG; if (!g) return;
  for (const tr of gpxTrails) {
    const pairs = [[tr.startLbl, tr.startEN], [tr.endLbl, tr.endEN]];
    for (const [lbl, en] of pairs) {
      if (!lbl) continue;
      if (!tr.visible || !en) { lbl.style.display = 'none'; continue; }
      const col = (en.E - g.bE) / g.aE, row = (en.N - g.bN) / g.aN;
      if (col < 0 || col > W - 1 || row < 0 || row > H - 1) { lbl.style.display = 'none'; continue; }
      const lx = (col - W / 2) * cell, ly = sampleE(col, row) * VE, lz = (row - H / 2) * cell;
      v.set(lx, ly, lz); world.localToWorld(v); v.project(camera);
      if (v.z > 1 || occludedLocal(lx, ly, lz)) { lbl.style.display = 'none'; continue; }
      lbl.style.display = 'flex';
      lbl.style.left = ((v.x * 0.5 + 0.5) * innerWidth) + 'px';
      lbl.style.top = ((-v.y * 0.5 + 0.5) * innerHeight) + 'px';
    }
  }
}
function disposeGpxAnimObj(tr) {                          // drop the THREE objects, keep tr.anim.p so playback survives a re-drape
  const A = tr.anim; if (!A) return;
  if (A.bright) { gpxGroup.remove(A.bright); A.bright.geometry.dispose(); A.bright.material.dispose(); A.bright = null; }
  if (A.dot) { gpxGroup.remove(A.dot); A.dot.material.dispose(); A.dot = null; }
}
function buildTrailAnim(tr, verts, segs) {                // keyed segments for the sweep: by real time if present, else by distance
  const useTime = tr.hasTime, keyed = []; let cum = 0;
  for (let k = 0; k < segs.length; k++) {
    const o = k * 6;
    const a = new THREE.Vector3(verts[o], verts[o + 1], verts[o + 2]);
    const b = new THREE.Vector3(verts[o + 3], verts[o + 4], verts[o + 5]);
    let w;
    if (useTime) { const ta = tr.times[segs[k][0]], tb = tr.times[segs[k][1]]; w = (ta != null && tb != null) ? Math.max(0, tb - ta) : 0; }
    else w = a.distanceTo(b);
    keyed.push({ a, b, s: cum, e: cum + w }); cum += w;
  }
  if (cum <= 0) { for (let k = 0; k < keyed.length; k++) { keyed[k].s = k; keyed[k].e = k + 1; } cum = keyed.length || 1; }   // degenerate weights → uniform by index
  const A = tr.anim = tr.anim || { p: 0 };
  A.seg = keyed; A.total = cum;
  const bgeo = new THREE.BufferGeometry();
  bgeo.setAttribute('position', new THREE.Float32BufferAttribute(verts.slice(), 3));
  bgeo.setDrawRange(0, 0);
  A.bright = new THREE.LineSegments(bgeo, new THREE.LineBasicMaterial({ color: tr.color }));
  A.bright.renderOrder = 7; A.bright.visible = false; gpxGroup.add(A.bright);
  const dot = new THREE.Sprite(new THREE.SpriteMaterial({ map: gpxDotTex(), color: tr.color, transparent: true, depthTest: false, depthWrite: false }));
  dot.renderOrder = 9; dot.visible = false;               // scale set per-frame in applyTrailProgress (constant on-screen size)
  A.dot = dot; gpxGroup.add(dot);
}
function applyTrailProgress(tr) {                         // place the dot at p, reveal the bright line behind it, keep the dot a constant on-screen size
  const A = tr.anim, seg = A.seg; if (!seg || !seg.length) return;
  const target = A.p * A.total; let i = 0;
  while (i < seg.length - 1 && seg[i].e < target) i++;
  const s = seg[i], span = (s.e - s.s) || 1, local = Math.min(1, Math.max(0, (target - s.s) / span));
  A.dot.position.copy(s.a).lerp(s.b, local);
  A.bright.geometry.setDrawRange(0, i * 2);               // full segments strictly behind the dot (each = 2 verts)
  const ds = Math.max(bounds().span * 0.004, camera.position.distanceTo(controls.target) * 0.018);
  A.dot.scale.set(ds, ds, 1);
}
// visuals are "in playback" while playing OR paused partway (0<p<1); idle/finished = solid full trail
function applyTrailVisual(tr) {
  const A = tr.anim;
  const hasObj = !!(A && A.bright && A.dot);   // disposeGpxAnimObj nulls bright/dot between a re-drape and the buildTrailAnim rebuild
  const active = !!(hasObj && tr.visible && (tr.playing || (A.p > 0 && A.p < 1)));
  if (tr.line) { tr.line.material.transparent = true; tr.line.material.opacity = active ? GPX_GHOST_OP : 1; }
  if (hasObj) {
    A.bright.visible = active; A.dot.visible = active;
    if (active) applyTrailProgress(tr); else A.bright.geometry.setDrawRange(0, 0);
  }
}
function setTrailPlaying(tr, on) {
  tr.playing = on && !!tr.anim;
  if (tr.playing) { if (tr.anim.p == null || tr.anim.p >= 1) tr.anim.p = 0; gpxPlaying.add(tr); }   // restart from the top once finished
  else gpxPlaying.delete(tr);                             // pause → freeze the dot & partial line where they are
  applyTrailVisual(tr);
  refreshGpxStartLabel(tr); syncGpxPlayBtns();
}
function toggleTrailAnim(tr) { if (tr.anim) { setTrailPlaying(tr, !tr.playing); track('gpx_play', { on: tr.playing }); } }
function syncGpxPlayBtns() {
  for (const tr of gpxTrails) if (tr.playBtn) {
    tr.playBtn.innerHTML = svgIcon(tr.playing ? 'pause' : 'play');
    tr.playBtn.title = t(tr.playing ? 'gpx.pause' : 'gpx.play');
    tr.playBtn.setAttribute('aria-pressed', tr.playing ? 'true' : 'false');
  }
}
let _gpxAnimLast = 0;
function stepGpxAnim() {
  if (!gpxPlaying.size) { _gpxAnimLast = 0; return; }
  const now = performance.now(), dt = _gpxAnimLast ? now - _gpxAnimLast : 16; _gpxAnimLast = now;
  for (const tr of gpxPlaying) {
    const A = tr.anim; if (!A) continue;
    A.p = Math.min(1, (A.p || 0) + dt / GPX_ANIM_DUR);
    applyTrailProgress(tr);
    if (A.p >= 1) setTrailPlaying(tr, false);             // finished → solid full trail, dot gone
  }
}
function panToTrail(tr) {                                 // ease the view to centre on the trail (keeps zoom & angle)
  if (!tr.centerLocal || !curG) return;
  if (typeof exitFlight === 'function' && flight.on) exitFlight();
  if (typeof exitWalk === 'function' && walk.on) exitWalk();
  if (typeof exitStargaze === 'function' && stargaze.on) exitStargaze();
  const w = tr.centerLocal.clone(); world.localToWorld(w);
  const camTo = camera.position.clone().add(w.clone().sub(controls.target));
  easeCamera(camTo, w, 600);
  track('gpx_pan');
}
function trailPtEN(tr, i) { const p = tr.pts[i], g = gpsToGrid(p[0], p[1]); return g ? { E: g.E, N: g.N } : null; }
function buildTrailLine(tr) {
  if (tr.line) { gpxGroup.remove(tr.line); tr.line.geometry.dispose(); tr.line.material.dispose(); tr.line = null; }
  disposeGpxAnimObj(tr);
  const { verts, off, segs } = drapeSegments(tr.pts, tr.breaks); tr.off = off;
  if (verts.length < 6) { tr.startEN = tr.endEN = null; tr.centerLocal = null; if (tr.playing) setTrailPlaying(tr, false); return; }   // fully off the loaded map
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  tr.line = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: tr.color, transparent: true, opacity: 1 }));
  tr.line.visible = tr.visible; tr.line.renderOrder = 6;
  gpxGroup.add(tr.line);
  tr.startEN = trailPtEN(tr, segs[0][0]);                 // HK1980 E/N of the first & last on-map points (label anchors)
  tr.endEN = trailPtEN(tr, segs[segs.length - 1][1]);
  let cx = 0, cy = 0, cz = 0; const nv = verts.length / 3;
  for (let k = 0; k < verts.length; k += 3) { cx += verts[k]; cy += verts[k + 1]; cz += verts[k + 2]; }
  tr.centerLocal = new THREE.Vector3(cx / nv, cy / nv, cz / nv);   // centroid → pan target
  if (!tr.startLbl) makeGpxLabels(tr); else refreshGpxStartLabel(tr);
  buildTrailAnim(tr, verts, segs);
  if (tr.playing) gpxPlaying.add(tr);
  applyTrailVisual(tr);                                   // restore solid/ghost + dot for the current play state (survives re-drape)
}
function redrapeGpx() {                                   // source/VE changed → re-project every trail
  if (!gpxTrails.length) return;
  ensureGpxGroup();
  for (const tr of gpxTrails) buildTrailLine(tr);
  syncGpxWarnings();     // update ⚠ in place — don't rebuild the list (would drop a name mid-edit)
}
function syncGpxWarnings() { for (const tr of gpxTrails) if (tr.warnEl) tr.warnEl.style.display = tr.off ? '' : 'none'; }
function parseGpx(text) {                                 // → [{ name, pts:[[lat,lon]], times, eles, hasTime, hasEle, breaks:Set }]
  const doc = new DOMParser().parseFromString(text, 'application/xml');
  if (doc.getElementsByTagName('parsererror').length) return [];
  // `segments` = continuous runs (each <trkseg>); the first point of a later run marks a
  // discontinuity (pause / GPS loss) so consumers don't join across it (codex P2).
  const grab = (segments, tag) => {
    const pts = [], times = [], eles = [], breaks = new Set();   // times ms|null, eles m|null (aligned to pts); breaks = indices that start a new run
    let hasTime = false, hasEle = false;
    for (const seg of segments) {
      let first = true;
      for (const p of seg.getElementsByTagName(tag)) {
        const lat = +p.getAttribute('lat'), lon = +p.getAttribute('lon');
        if (!(isFinite(lat) && isFinite(lon))) continue;
        if (first && pts.length) breaks.add(pts.length);  // leg (prev run's end → here) is a gap, not a real move
        first = false;
        pts.push([lat, lon]);
        const te = p.getElementsByTagName('time')[0];     // <trkpt>'s own child; trkpts have no deeper nesting
        const ms = te ? Date.parse(te.textContent.trim()) : NaN;
        if (isFinite(ms)) { times.push(ms); hasTime = true; } else times.push(null);
        const ee = p.getElementsByTagName('ele')[0];
        const m = ee ? parseFloat(ee.textContent) : NaN;
        if (isFinite(m)) { eles.push(m); hasEle = true; } else eles.push(null);
      }
    }
    return { pts, times, eles, hasTime, hasEle, breaks };
  };
  const nameOf = (el, dflt) => { const n = el.getElementsByTagName('name')[0]; return (n && n.textContent.trim()) || dflt; };
  const out = [];
  for (const trk of doc.getElementsByTagName('trk')) {
    const segs = trk.getElementsByTagName('trkseg');
    const g = grab(segs.length ? [...segs] : [trk], 'trkpt');   // fall back to the whole <trk> if it has no <trkseg>
    if (g.pts.length >= 2) out.push({ name: nameOf(trk, 'Track'), ...g });
  }
  if (!out.length) for (const rte of doc.getElementsByTagName('rte')) { const g = grab([rte], 'rtept'); if (g.pts.length >= 2) out.push({ name: nameOf(rte, 'Route'), ...g }); }
  return out;
}
function addGpxText(text) {
  ensureGpxGroup();
  const tracks = parseGpx(text);
  if (!tracks.length) { flashGpxNote(t('gpx.bad')); track('gpx_import', { trails: 0 }); return; }   // failed/empty import — funnel signal
  const added = [];
  for (const trk of tracks) {
    const tr = { name: gpxName(), pts: trk.pts, times: trk.times, eles: trk.eles, hasTime: trk.hasTime, hasEle: trk.hasEle, breaks: trk.breaks,
                 color: gpxColor(gpxTrails.length), visible: true, line: null, off: 0, warnEl: null,
                 startLbl: null, endLbl: null, startEN: null, endEN: null, centerLocal: null,
                 anim: null, playing: false, playBtn: null, expanded: false, stats: null };
    gpxTrails.push(tr); buildTrailLine(tr); added.push(tr);
  }
  track('gpx_import', { trails: added.length, timed: added.some(t => t.hasTime), drew: added.some(t => !!t.line) });   // drew=false → landed off the loaded map
  renderGpxList();
}
function removeGpxTrail(tr) {
  gpxPlaying.delete(tr);
  if (tr.line) { gpxGroup.remove(tr.line); tr.line.geometry.dispose(); tr.line.material.dispose(); }
  removeGpxLabels(tr); disposeGpxAnimObj(tr); tr.anim = null;
  gpxTrails.splice(gpxTrails.indexOf(tr), 1);
  renderGpxList();
}
function renderGpxList() {
  const list = document.getElementById('gpxlist'); if (!list) return;
  list.textContent = '';
  for (const tr of gpxTrails) {
    const row = document.createElement('div'); row.className = 'gpxrow';
    const sw = document.createElement('input'); sw.type = 'color'; sw.className = 'gpxsw'; sw.value = '#' + tr.color.getHexString(); sw.title = t('gpx.colour');
    sw.addEventListener('input', () => { tr.color.set(sw.value); if (tr.line) tr.line.material.color.copy(tr.color); if (tr.anim) { if (tr.anim.bright) tr.anim.bright.material.color.copy(tr.color); if (tr.anim.dot) tr.anim.dot.material.color.copy(tr.color); } });
    sw.addEventListener('change', e => { if (e.isTrusted) track('gpx_recolour'); });   // once on commit, not per drag frame
    const nm = document.createElement('input'); nm.type = 'text'; nm.className = 'gpxname'; nm.value = tr.name; nm.spellcheck = false; nm.maxLength = 60; nm.setAttribute('aria-label', t('gpx.name'));
    nm.addEventListener('input', () => { tr.name = nm.value; });
    nm.addEventListener('keydown', e => { if (e.key === 'Enter') nm.blur(); });
    nm.addEventListener('change', e => { if (e.isTrusted) track('gpx_rename'); });      // commit only (blur/Enter), never the name text
    const warn = document.createElement('span'); warn.className = 'gpxwarn'; warn.textContent = '⚠'; warn.title = t('gpx.offmap'); warn.style.display = tr.off ? '' : 'none';
    tr.warnEl = warn;
    const pan = document.createElement('button'); pan.type = 'button'; pan.className = 'gpxbtn'; pan.innerHTML = svgIcon('target'); pan.title = t('gpx.pan'); pan.setAttribute('aria-label', t('gpx.pan'));
    pan.addEventListener('click', () => panToTrail(tr));
    const vis = document.createElement('button'); vis.type = 'button'; vis.className = 'gpxbtn'; vis.innerHTML = svgIcon(tr.visible ? 'eye' : 'eye-off'); vis.title = t(tr.visible ? 'gpx.hide' : 'gpx.show'); vis.setAttribute('aria-pressed', tr.visible ? 'true' : 'false');
    vis.addEventListener('click', () => {
      tr.visible = !tr.visible;
      if (tr.line) tr.line.visible = tr.visible;
      applyTrailVisual(tr);                                // re-derive bright/dot visibility; labels follow tr.visible next frame
      vis.innerHTML = svgIcon(tr.visible ? 'eye' : 'eye-off'); vis.title = t(tr.visible ? 'gpx.hide' : 'gpx.show'); vis.setAttribute('aria-pressed', tr.visible ? 'true' : 'false');
      track('gpx_visibility', { on: tr.visible });
    });
    const play = document.createElement('button'); play.type = 'button'; play.className = 'gpxbtn'; play.innerHTML = svgIcon(tr.playing ? 'pause' : 'play'); play.title = t(tr.playing ? 'gpx.pause' : 'gpx.play'); play.setAttribute('aria-pressed', tr.playing ? 'true' : 'false');
    play.addEventListener('click', () => toggleTrailAnim(tr));
    tr.playBtn = play;
    const rm = document.createElement('button'); rm.type = 'button'; rm.className = 'gpxbtn'; rm.innerHTML = svgIcon('x'); rm.title = t('gpx.remove'); rm.setAttribute('aria-label', t('gpx.remove'));
    rm.addEventListener('click', () => { track('gpx_remove'); removeGpxTrail(tr); });
    // disclosure: elevation profile + distance/gain/pace stats (map-independent)
    const chev = document.createElement('button'); chev.type = 'button'; chev.className = 'gpxbtn gpxchev'; chev.innerHTML = svgIcon(tr.expanded ? 'chevron-up' : 'chevron-down'); chev.title = t('gpx.details'); chev.setAttribute('aria-label', t('gpx.details')); chev.setAttribute('aria-expanded', tr.expanded ? 'true' : 'false');
    const detail = document.createElement('div'); detail.className = 'gpxdetail'; detail.style.display = tr.expanded ? '' : 'none';
    if (tr.expanded) { fillTrailDetail(tr, detail); detail.dataset.filled = '1'; }
    chev.addEventListener('click', () => {
      tr.expanded = !tr.expanded;
      detail.style.display = tr.expanded ? '' : 'none';
      chev.innerHTML = svgIcon(tr.expanded ? 'chevron-up' : 'chevron-down'); chev.setAttribute('aria-expanded', tr.expanded ? 'true' : 'false');
      if (tr.expanded && !detail.dataset.filled) { fillTrailDetail(tr, detail); detail.dataset.filled = '1'; track('gpx_profile'); }
    });
    row.append(sw, nm, warn, chev, pan, vis, rm, play);
    list.append(row, detail);
  }
}
let _gpxNoteT = null;
function flashGpxNote(msg) {
  const d = document.getElementById('gpxdrop'); if (!d) return;
  d.textContent = msg; clearTimeout(_gpxNoteT);
  _gpxNoteT = setTimeout(() => { d.textContent = t('gpx.drop'); }, 2600);
}
(() => {   // dropzone: drag-drop + click/tap → picker; keyboard (Enter/Space) too
  const drop = document.getElementById('gpxdrop'), input = document.getElementById('gpxfile');
  if (!drop || !input) return;
  const readFiles = files => { for (const f of files) if (/\.gpx$/i.test(f.name) || /gpx|xml/i.test(f.type)) f.text().then(addGpxText).catch(() => flashGpxNote(t('gpx.bad'))); };
  drop.addEventListener('click', () => input.click());
  drop.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.click(); } });
  input.addEventListener('change', () => { readFiles(input.files); input.value = ''; });
  ['dragenter', 'dragover'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('drag'); }));
  ['dragleave', 'dragend', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('drag'); }));
  drop.addEventListener('drop', e => { if (e.dataTransfer) readFiles(e.dataTransfer.files); });
})();
if (FLY_DEBUG) window.__gpx = { addGpxText, gpxTrails, redrapeGpx, toggleTrailAnim, setTrailPlaying, stepGpxAnim, applyTrailProgress, panToTrail, updateGpxLabels, trailStats, elevChartSvg, trailStatChips, getTarget: () => ({ x: controls.target.x, y: controls.target.y, z: controls.target.z }), get group() { return gpxGroup; } };
// auto-spin direction is a segmented control (⟲ left / ⏸ pause / ⟳ right); syncSpinSeg
// reflects the current spinDir, and every mode transition that used to set the old
// <select>'s .value now calls it instead.
function syncSpinSeg() {
  const seg = document.getElementById('spinseg'); if (!seg) return;
  for (const b of seg.children) b.setAttribute('aria-pressed', parseInt(b.dataset.dir, 10) === spinDir ? 'true' : 'false');
}
for (const b of document.querySelectorAll('#spinseg button')) {
  b.addEventListener('click', () => { spinDir = parseInt(b.dataset.dir, 10); syncSpinSeg(); syncUrl(); track('spin', { dir: spinDir > 0 ? 'cw' : spinDir < 0 ? 'ccw' : 'off' }); });
}
syncSpinSeg();
document.getElementById('spinspd').addEventListener('input', e => { spinSpeed = parseFloat(e.target.value); });
const panelEl = document.getElementById('panel');
document.getElementById('collapse-btn').addEventListener('click', () => { panelEl.classList.add('collapsed'); track('panel_collapse', { via: 'panel' }); });
// ---- mobile drawers (HKS-16): panel is a bottom sheet, HUD a tap-to-expand chip.
// Start tucked away on phones so the map is unobstructed; tapping the map dismisses both.
const mobileMQ = matchMedia('(max-width: 640px), (pointer: coarse) and (max-height: 500px)');
const wxhudEl = document.getElementById('wxhud');
function applyMobileLayout(mobile) {
  if (mobile) panelEl.classList.add('collapsed');   // HKS-86: phones always tuck it away; desktop keeps its state (starts collapsed, opened via the dock ⚙) — never auto-open
  else wxhudEl.classList.remove('expanded');
}
applyMobileLayout(mobileMQ.matches);
mobileMQ.addEventListener('change', e => applyMobileLayout(e.matches));
document.getElementById('sheetgrip').addEventListener('click', () => { panelEl.classList.add('collapsed'); track('panel_collapse', { via: 'grip' }); });
wxhudEl.addEventListener('click', () => { if (mobileMQ.matches) wxhudEl.classList.toggle('expanded'); });
app.addEventListener('pointerdown', () => {
  if (!mobileMQ.matches) return;
  panelEl.classList.add('collapsed');
  wxhudEl.classList.remove('expanded');
}, { passive: true });

// ---- liquid-glass panels (glass-gl) -----------------------------------------
// The panel and weather HUD are real refracting lenses over the live scene: the
// three.js canvas is the glass background, re-uploaded every frame. Two fixed
// presets follow the background mode (dark → obsidian glass, paper → milk
// glass) — no user-facing glass controls. Falls back to the CSS look if WebGL
// is unavailable.
let glassFx = null;
if (GLASS_OK) {
  try {
    const gcv = document.createElement('canvas');
    gcv.id = 'glassgl';
    document.body.insertBefore(gcv, document.getElementById('flashfx'));
    glassFx = createGlass({ canvas: gcv, background: renderer.domElement, transparent: true });
    glassFx.register(panelEl, { radius: 16 });
    glassFx.register(wxhudEl, { radius: 14 });
    glassFx.register(document.getElementById('compass'), { radius: 10 });   // corner controls too
    glassFx.register(document.getElementById('snapbtn'), { radius: 19 });
    document.body.classList.add('glass');
  } catch (e) {
    console.warn('glass-gl unavailable, keeping CSS panels', e);
    const gcv = document.getElementById('glassgl'); if (gcv) gcv.remove();
    glassFx = null;
  }
}
const GLASS_PRESETS = {
  dark:  { refraction: 0.15, blur: 2.6, liquidness: 0.30, edgeLight: 0.8,
           edgeFrost: 0, dispersion: 0.28, tint: [0.05, 0.075, 0.10] },
  paper: { refraction: 0.13, blur: 2.4, liquidness: 0.34, edgeLight: 1.05,
           edgeFrost: 0, dispersion: 0.22, tint: [1, 1, 1] },
};
function applyGlassPreset(mode) {
  document.body.classList.toggle('ui-light', mode === 'paper');
  if (glassFx) glassFx.setParams(GLASS_PRESETS[mode] || GLASS_PRESETS.dark);
  drawTideGraph();   // tide-graph ink follows the theme
}
// ---- unified left-edge drawer: Weather · Help · Credits (HKS-86) ------------
// Both share ONE sliding panel. Two tabs stack together on the edge (always
// visible); the active tab is highlighted and clicking a tab swaps the panel's
// content — no cross-fade, no per-drawer slide. Weather (HKO warnings + forecast)
// never auto-opens; the amber tab + ⚠ chip flag a warning. Session-only, no storage.
const sideDrawer = document.getElementById('sidedrawer');
const sdTitleEl = document.getElementById('sd-title');
const SD = {
  wx:      { tab: document.getElementById('sd-tab-wx'),      body: document.getElementById('sd-wx'),      title: 'wb.title' },
  help:    { tab: document.getElementById('sd-tab-help'),    body: document.getElementById('sd-help'),    title: 'help.title' },
  credits: { tab: document.getElementById('sd-tab-credits'), body: document.getElementById('sd-credits'), title: 'title.about' },
};
let sdActive = null;   // null | 'wx' | 'help' | 'credits'
// fill a section with a bold label + one <div> per paragraph (textContent = no injection)
function fillWbSection(elm, label, body) {
  elm.textContent = '';
  if (!body) return;
  const b = document.createElement('b'); b.textContent = label; elm.appendChild(b);
  body.split(/\n+/).map(s => s.trim()).filter(Boolean).forEach(para => {
    const d = document.createElement('div'); d.textContent = para; elm.appendChild(d);
  });
}
function updateHelp() {   // adaptive help: general section always, contextual follows the mode
  const ctx = document.getElementById('hp-context'), gen = document.getElementById('hp-general');
  if (!ctx || !gen) return;
  const mode = flight.on ? 'fly' : walk.on ? 'walk' : stargaze.on ? 'star' : 'orbit';
  fillWbSection(ctx, t('help.' + mode + '.t'), t('help.' + mode + '.b'));
  fillWbSection(gen, t('help.gen.t'), t('help.gen.b'));
}
function renderSide() {
  const open = sdActive != null;
  sideDrawer.classList.toggle('open', open);
  for (const k in SD) {
    const on = k === sdActive;
    SD[k].tab.classList.toggle('on', on);
    SD[k].tab.setAttribute('aria-selected', on ? 'true' : 'false');
    SD[k].body.hidden = !on;
  }
  if (open) sdTitleEl.textContent = t(SD[sdActive].title);
}
function setSide(which) {   // which: 'wx' | 'help' | null — swap content, no slide
  sdActive = which;
  if (which === 'help') updateHelp();
  renderSide();
}
SD.wx.tab.addEventListener('click',      () => { const open = sdActive !== 'wx';      setSide(open ? 'wx' : null);      if (open) track('weather_panel_open'); });
SD.help.tab.addEventListener('click',    () => { const open = sdActive !== 'help';    setSide(open ? 'help' : null);    if (open) track('help_open'); });
SD.credits.tab.addEventListener('click', () => { const open = sdActive !== 'credits'; setSide(open ? 'credits' : null); if (open) track('credits_open'); });
document.getElementById('sd-close').addEventListener('click', () => setSide(null));
document.getElementById('wx-warn').addEventListener('click', e => {
  e.stopPropagation();                      // don't collapse the weather chip on mobile
  if (document.getElementById('wx-warn').textContent.trim()) { setSide('wx'); track('weather_panel_open', { via: 'chip' }); }
});
document.addEventListener('keydown', e => { if (e.key === 'Escape' && sdActive) setSide(null); });
updateHelp();
requestAnimationFrame(() => sideDrawer.classList.add('ready'));

document.getElementById('fog').addEventListener('change', e => {
  weather.fog = e.target.checked; setFog();
  if (mistGrp) mistGrp.visible = weather.fog;
  if (e.isTrusted) track('weather_toggle', { kind: 'fog', on: e.target.checked });
});
document.getElementById('rain').addEventListener('change', e => { weather.rain = e.target.checked; if (rainPts) rainPts.visible = weather.rain; if (e.isTrusted) track('weather_toggle', { kind: 'rain', on: e.target.checked }); });
document.getElementById('clouds').addEventListener('change', e => { weather.clouds = e.target.checked; if (cloudGrp) cloudGrp.visible = weather.clouds; if (e.isTrusted) track('weather_toggle', { kind: 'clouds', on: e.target.checked }); });
document.getElementById('lightning').addEventListener('change', e => {
  weather.lightning = e.target.checked;
  if (!weather.lightning) { flash = 0; boltLife = 0; disposeBolt(); if (boltLight) boltLight.intensity = 0; applyBg(bgMode); }
  if (e.isTrusted) track('weather_toggle', { kind: 'lightning', on: e.target.checked });
});
document.getElementById('waves').addEventListener('change', e => { weather.waves = e.target.checked; if (e.isTrusted) track('weather_toggle', { kind: 'waves', on: e.target.checked }); });
document.getElementById('snow').addEventListener('change', e => { weather.snow = e.target.checked; if (snowPts) snowPts.visible = weather.snow; if (e.isTrusted) track('weather_toggle', { kind: 'snow', on: e.target.checked }); });
// ---- weather soundboard (HKS-2): procedural ambience, gesture-gated --------
let sndOn = false;
const sndBtn = document.getElementById('sndbtn');
function setSound(on) {
  sndOn = on && audioSupported();
  setAudioEnabled(sndOn);
  sndBtn.textContent = sndOn ? '🔊' : '🔇';
  sndBtn.classList.toggle('on', sndOn);
  if (sndOn) updateAudioMix();
  syncUrl();
}
function updateAudioMix() {
  if (!sndOn) return;
  const w = windStrength;
  setWeatherMix({
    rain:  weather.rain  ? 0.35 + 0.65 * Math.max(w, stormLevel >= 8 ? 0.6 : 0) : 0,
    wind:  Math.max(w, stormLevel > 0 ? 0.25 : 0),
    waves: weather.waves ? 0.3 + 0.7 * w : 0,
    fog:   weather.fog ? 1 : 0,
  });
}
sndBtn.addEventListener('click', () => { setSound(!sndOn); track('sound', { on: sndOn }); });
document.getElementById('sndvol').addEventListener('input', e => setMasterVolume(parseInt(e.target.value, 10) / 100));
setInterval(updateAudioMix, 700);   // live/tide/storm drift folds into the mix

function syncSkyControls() {
  const g = id => document.getElementById(id);
  const manual = skySim.on && !skySim.live;    // Custom time = the only scrubable mode
  g('skydate').disabled = !manual;
  g('skytime').disabled = !manual;
  if (manual) {                // entering custom: the scrub shows the fixed instant again
    g('skydate').value = skySim.date;
    g('skytime').value = skySim.minutes;
    g('skytimev').textContent = mmToHHMM(skySim.minutes);
  }
}
document.getElementById('skymode').addEventListener('change', e => {
  const v = e.target.value;                    // live | fixed | off
  skySim.on = v !== 'off';
  skySim.live = v === 'live';
  celKey = ''; syncSkyControls(); updateCelestial();
  if (e.isTrusted) track('sky_mode', { mode: v });
});
document.getElementById('skydate').addEventListener('change', e => { if (e.target.value) skySim.date = e.target.value; celKey = ''; updateCelestial(); });
document.getElementById('skytime').addEventListener('input', e => {
  skySim.minutes = parseInt(e.target.value, 10) || 0;
  document.getElementById('skytimev').textContent = mmToHHMM(skySim.minutes);
  celKey = ''; updateCelestial();
});
// scrub commits on release ('change'), so we log one canonical event per scrub, not
// one per input tick — and applyState()'s synthetic 'input' never trips it.
document.getElementById('skytime').addEventListener('change', e => { if (e.isTrusted) track('sky_time_scrub', { via: 'panel' }); });
document.getElementById('skydate').value = skySim.date;
document.getElementById('skytime').value = skySim.minutes;
document.getElementById('skytimev').textContent = mmToHHMM(skySim.minutes);
syncSkyControls();
document.getElementById('skyh').addEventListener('input', e => {
  skyScale = parseFloat(e.target.value);
  document.getElementById('skyhv').textContent = skyScale.toFixed(1);
  applySkyScale();
});
document.getElementById('tide').addEventListener('input', e => {
  tideManual = parseInt(e.target.value, 10) / 100;
  if (!liveMode) tideLevel = tideManual;                 // live mode drives tideLevel from data instead
  document.getElementById('tidev').textContent = Math.round(tideManual * 100) + '%';
});
document.getElementById('storm').addEventListener('change', e => {
  const level = parseInt(e.target.value, 10);
  applyStorm(level);
  if (e.isTrusted) track('typhoon', { signal: level > 0 ? 'T' + level : 'none' });
});
document.getElementById('wind').addEventListener('input', e => {
  windStrength = parseInt(e.target.value, 10) / 100;     // fine wind override (keeps the current signal)
  document.getElementById('windv').textContent = Math.round(windStrength * 100) + '%';
  updateWindVisuals();
});
// commit the wind-strength scrub on release (bucketed, low-cardinality)
document.getElementById('wind').addEventListener('change', e => {
  if (e.isTrusted) track('wind', { dir: document.getElementById('winddir').value, strength_bucket: windBucket() });
});
function setThunderRate(v) {
  thunderRate = Math.max(0, Math.min(1, v));
  const el = document.getElementById('thunderrate'); if (el) el.value = Math.round(thunderRate * 100);
  const d = document.getElementById('thunderratev'); if (d) d.textContent = Math.round(thunderRate * 100) + '%';
}
document.getElementById('thunderrate').addEventListener('input', e => {
  thunderRate = parseInt(e.target.value, 10) / 100;
  document.getElementById('thunderratev').textContent = Math.round(thunderRate * 100) + '%';
});
document.getElementById('winddir').addEventListener('change', e => { setWindDir(e.target.value); updateStormBadge(); if (e.isTrusted) track('wind', { dir: e.target.value, strength_bucket: windBucket() }); });

// ---- live weather from HKO / data.gov.hk -----------------------------------
const HKO_ICON = {
  50:'Sunny',51:'Sunny periods',52:'Sunny intervals',53:'Sunny periods · a few showers',
  54:'Sunny intervals · showers',60:'Cloudy',61:'Overcast',62:'Light rain',63:'Rain',
  64:'Heavy rain',65:'Thunderstorms',70:'Fine',71:'Fine',72:'Fine',73:'Fine',74:'Fine',75:'Fine',
  76:'Mainly cloudy',77:'Mainly fine',80:'Windy',81:'Dry',82:'Humid',83:'Fog',84:'Mist',85:'Haze',
  90:'Hot',91:'Warm',92:'Cool',93:'Cold'
};
const HKO_ICON_ZH = {
  50:'天晴',51:'部分時間有陽光',52:'短暫時間有陽光',53:'天晴，有幾陣驟雨',
  54:'短暫時間有陽光，有驟雨',60:'多雲',61:'密雲',62:'微雨',63:'雨',
  64:'大雨',65:'雷暴',70:'天色良好',71:'天色良好',72:'天色良好',73:'天色良好',74:'天色良好',75:'天色良好',
  76:'大致多雲',77:'天色大致良好',80:'有風',81:'乾燥',82:'潮濕',83:'霧',84:'薄霧',85:'煙霞',
  90:'炎熱',91:'和暖',92:'清涼',93:'寒冷'
};
const wxIcon = code => (isZh() ? HKO_ICON_ZH : HKO_ICON)[code];
let liveMode = false, wxClockT = null, wxRefreshT = null;
const wxStation = arr => (arr || []).find(d => /observatory/i.test(d.place)) || (arr || [])[0];
const windFromForecast = desc => { const m = (desc || '').match(/[^.]*\bwind[s]?\b[^.]*/i); return m ? m[0].trim().replace(/\s+/g, ' ') : ''; };

// ---- live tide prediction (HKO HHOT hourly heights) + HUD waveform ---------
// nearest tide station per source (Cheung Chau for Lantau, Quarry Bay for HK-wide)
const TIDE_STATION = {
  'lantau-hk5m':  ['CCH', 'Cheung Chau'], 'lantau-srtm30': ['CCH', 'Cheung Chau'],
  'hk-landsd-5m': ['QUB', 'Quarry Bay'],  'hk-srtm':       ['QUB', 'Quarry Bay'],
};
// HK-local calendar parts for today ± offsetDays (HKT = UTC+8, no DST)
function hkYMD(offsetDays) {
  const d = new Date(Date.now() + offsetDays * 86400000);
  const [y, m, dd] = d.toLocaleDateString('en-CA', { timeZone: 'Asia/Hong_Kong' }).split('-');
  return { y: +y, m: +m, d: +dd };
}
function hkHourFloat() {
  const [H, M] = new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Hong_Kong', hour12: false }).split(':').map(Number);
  return H + M / 60;
}
// vals[i] is the predicted height at clock hour (i+1) measured from yesterday 00:00;
// sample (with linear interpolation) at an absolute window-hour
function tideAt(vals, absHour) {
  const idx = absHour - 1, i0 = Math.floor(idx);
  const cl = i => vals[Math.max(0, Math.min(vals.length - 1, i))];
  const a = cl(i0), b = cl(i0 + 1);
  return (isFinite(a) && isFinite(b)) ? a + (b - a) * (idx - i0) : NaN;
}

async function syncLiveTide() {
  const [st, stName] = TIDE_STATION[document.getElementById('src').value] || ['QUB', 'Quarry Bay'];
  const base = 'https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=HHOT&lang=en&rformat=json&station=' + st;
  const day = off => { const { y, m, d } = hkYMD(off); return fetch(`${base}&year=${y}&month=${m}&day=${d}`).then(r => r.json()).catch(() => null); };
  try {
    const rows = await Promise.all([day(-1), day(0), day(1)]);   // yesterday, today, tomorrow
    const dayVals = j => (j && j.data && j.data[0]) ? j.data[0].slice(2).map(Number) : new Array(24).fill(NaN);
    const vals = [...dayVals(rows[0]), ...dayVals(rows[1]), ...dayVals(rows[2])];   // 72 hourly heights
    const nowHour = 24 + hkHourFloat();                          // today 00:00 sits at window-hour 24
    // min/max over the ±12 h window drives both the graph scale and the level normalisation
    let mn = Infinity, mx = -Infinity;
    for (let x = Math.ceil(nowHour - 12); x <= Math.floor(nowHour + 12); x++) {
      const v = tideAt(vals, x); if (isFinite(v)) { mn = Math.min(mn, v); mx = Math.max(mx, v); }
    }
    const cur = tideAt(vals, nowHour);
    tideSeries = { vals, nowHour, min: mn, max: mx, cur, stationName: stName };
    if (mx > mn && isFinite(cur)) tideLevel = Math.max(0, Math.min(1, (cur - mn) / (mx - mn)));
    // reflect the live level on the (locked) slider
    document.getElementById('tide').value = Math.round(tideLevel * 100);
    document.getElementById('tidev').textContent = Math.round(tideLevel * 100) + '%';
    // HUD readout + trend
    const trend = tideAt(vals, nowHour + 0.5) - cur;
    const arrow = trend > 0.02 ? t('tide.rising') : trend < -0.02 ? t('tide.falling') : t('tide.slack');
    document.getElementById('wx-tide').textContent = isFinite(cur) ? `${t('tide.word')} ${cur.toFixed(2)} m  ${arrow}` : '';
    document.getElementById('wx-tidecap').textContent = `${t('tide.24h')} · ${I18N[locale]['st.' + st] || stName}`;
    drawTideGraph();
  } catch (e) { console.error('tide', e); }
}

// past-and-upcoming tide waveform for the HUD (±12 h around now)
function drawTideGraph() {
  const cv = document.getElementById('wx-tidegraph');
  if (!cv || !tideSeries) return;
  const { vals, nowHour, min, max } = tideSeries;
  const dpr = Math.min(devicePixelRatio || 1, 2), Wc = 224, Hc = 56;
  if (cv.width !== Wc * dpr) { cv.width = Wc * dpr; cv.height = Hc * dpr; }
  const ctx = cv.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  cv.style.display = 'block'; ctx.clearRect(0, 0, Wc, Hc);
  const lo = nowHour - 12, hi = nowHour + 12, pad = 6, gTop = 7, gBot = Hc - 13;
  const range = Math.max(0.2, max - min);
  const ymin = min - range * 0.18, ymax = max + range * 0.18;
  const xOf = h => pad + (h - lo) / (hi - lo) * (Wc - pad * 2);
  const yOf = v => gBot - (v - ymin) / (ymax - ymin) * (gBot - gTop);
  // curve
  ctx.beginPath(); let started = false;
  for (let h = lo; h <= hi + 1e-6; h += 0.2) {
    const v = tideAt(vals, h); if (!isFinite(v)) continue;
    const x = xOf(h), y = yOf(v);
    started ? ctx.lineTo(x, y) : (ctx.moveTo(x, y), started = true);
  }
  const lightUi = document.body.classList.contains('ui-light');
  ctx.lineJoin = 'round'; ctx.strokeStyle = lightUi ? 'rgba(28,110,150,.95)' : 'rgba(120,200,235,.95)';
  ctx.lineWidth = 1.8; ctx.stroke();
  // fill under the curve
  ctx.lineTo(xOf(hi), gBot); ctx.lineTo(xOf(lo), gBot); ctx.closePath();
  ctx.fillStyle = lightUi ? 'rgba(40,120,160,.14)' : 'rgba(90,170,215,.16)'; ctx.fill();
  // "now" marker + dot
  const nx = xOf(nowHour), nv = tideAt(vals, nowHour);
  ctx.strokeStyle = lightUi ? 'rgba(11,143,102,.8)' : 'rgba(53,203,160,.85)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(nx, gTop - 3); ctx.lineTo(nx, gBot); ctx.stroke();
  if (isFinite(nv)) { ctx.fillStyle = lightUi ? '#0b8f66' : '#35cba0'; ctx.beginPath(); ctx.arc(nx, yOf(nv), 2.8, 0, 7); ctx.fill(); }
  // axis ticks + high-water marker
  ctx.font = '9px ui-monospace, monospace';
  ctx.fillStyle = lightUi ? 'rgba(20,30,40,.55)' : 'rgba(255,255,255,.5)';
  ctx.textAlign = 'left';   ctx.fillText('−12h', pad, Hc - 3);
  ctx.textAlign = 'center'; ctx.fillText('now', nx, Hc - 3);
  ctx.textAlign = 'right';  ctx.fillText('+12h', Wc - pad, Hc - 3);
  ctx.fillStyle = lightUi ? 'rgba(20,30,40,.45)' : 'rgba(255,255,255,.4)';
  ctx.fillText(max.toFixed(1) + ' m', Wc - pad, gTop + 7);
}

// HKS-101: live wind DIRECTION. The drift vector (windVec) was only ever set by the
// manual dropdown or a T8 typhoon signal, so in ordinary live weather the clouds/rain
// drifted in the default (northerly) direction regardless of the real wind — not
// matching the radar. Derive the actual territory wind from HKO's 10-min station winds
// and steer windVec so the whole weather deck moves the way the radar shows.
const COMPASS_DEG = {
  N: 0, NNE: 22.5, NE: 45, ENE: 67.5, E: 90, ESE: 112.5, SE: 135, SSE: 157.5,
  S: 180, SSW: 202.5, SW: 225, WSW: 247.5, W: 270, WNW: 292.5, NW: 315, NNW: 337.5,
  NORTH: 0, NORTHNORTHEAST: 22.5, NORTHEAST: 45, EASTNORTHEAST: 67.5, EAST: 90,
  EASTSOUTHEAST: 112.5, SOUTHEAST: 135, SOUTHSOUTHEAST: 157.5, SOUTH: 180,
  SOUTHSOUTHWEST: 202.5, SOUTHWEST: 225, WESTSOUTHWEST: 247.5, WEST: 270,
  WESTNORTHWEST: 292.5, NORTHWEST: 315, NORTHNORTHWEST: 337.5,
};
function windFromBearing(v) {              // HKO wind-direction cell → degrees the wind blows FROM
  if (v == null) return null;
  const s = String(v).trim();
  if (!s || /^(n\/?a|variable|calm)$/i.test(s)) return null;
  if (/^\d+(\.\d+)?$/.test(s)) return +s % 360;
  const k = s.toUpperCase().replace(/[^A-Z]/g, '');
  return k in COMPASS_DEG ? COMPASS_DEG[k] : null;
}
async function syncLiveWind() {            // steer windVec from the real HKO 10-min station winds
  if (!liveMode) return;
  let sx = 0, sz = 0, n = 0;
  try {
    const txt = await fetch(regUrl('latest_10min_wind.csv')).then(r => r.ok ? r.text() : '').catch(() => '');
    for (const r of parseCsv(txt)) {       // r = [type, station, wdir, wspd, gust]
      const b = windFromBearing(r[2]), spd = parseFloat(r[3]);
      if (b == null || !isFinite(spd) || spd <= 0) continue;
      const from = b * Math.PI / 180;      // speed-weighted toward-vector: (−sin, cos); world −z=N, +x=E
      sx += -Math.sin(from) * spd; sz += Math.cos(from) * spd; n++;
    }
  } catch (_) { return; }
  if (!liveMode || n < 3) return;          // too few stations reporting → keep the current vector
  const mag = Math.hypot(sx, sz);
  if (mag < 1e-3) return;                   // light & variable → don't spin the deck on noise
  windVec.x = sx / mag; windVec.z = sz / mag;                     // continuous, matches the radar
  const toward = (Math.atan2(windVec.x, -windVec.z) * 180 / Math.PI + 360) % 360;
  const CARD16 = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const sel = document.getElementById('winddir');
  if (sel) sel.value = CARD16[Math.round(((toward + 180) % 360) / 22.5) % 16];   // wind-from, nearest 16-pt (dropdown display only — no snap to windVec)
  updateWindVisuals();
  if (typeof updateStormBadge === 'function') updateStormBadge();
}
async function syncLiveWeather() {
  const el = id => document.getElementById(id);
  const chk = (id, on) => { const e = el(id); if (e.checked !== on) { e.checked = on; e.dispatchEvent(new Event('change', { bubbles: true })); } };
  try {
    const base = `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=${isZh() ? 'tc' : 'en'}&dataType=`;
    const oBase = 'https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?lang=en&rformat=json&dataType=';
    const enBase = 'https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=en&dataType=';
    const [rh, fl, ws, lhl, rhEn] = await Promise.all([
      fetch(base + 'rhrread').then(r => r.json()),
      fetch(base + 'flw').then(r => r.json()).catch(() => ({})),
      fetch(base + 'warnsum').then(r => r.json()).catch(() => ({})),
      fetch(oBase + 'LHL').then(r => r.json()).catch(() => ({})),   // past-hour lightning counts by region
      // HKS-69: the WxField consumers match HKO place/station names against the English
      // STATION_DISTRICT map, so the spatial-field data must be English even when the UI is
      // zh-hk (rh above stays localized for the displayed warning text). (codex)
      isZh() ? fetch(enBase + 'rhrread').then(r => r.json()).catch(() => null) : Promise.resolve(null),
    ]);
    const tst = wxStation(rh.temperature && rh.temperature.data), h = wxStation(rh.humidity && rh.humidity.data);
    const code = (rh.icon || [])[0];
    let warn = rh.warningMessage || ''; if (Array.isArray(warn)) warn = warn.join(' ');
    let rainMax = 0; for (const r of ((rh.rainfall && rh.rainfall.data) || [])) rainMax = Math.max(rainMax, +r.max || 0);
    el('wx-status').textContent = wxIcon(code) || t('wx.live');
    el('wx-temp').textContent = tst ? `${tst.value}°${tst.unit || 'C'}` : '—';
    el('wx-hum').textContent = h ? `${t('tip.humidity')} ${h.value}%` : '';
    el('wx-wind').textContent = windFromForecast(fl.forecastDesc) || '—';
    // route the long texts into the pull-up bulletin; the box keeps only a compact chip (HKS-80)
    const fcast = [fl.generalSituation, fl.forecastDesc, fl.outlook].filter(Boolean).join('\n');
    fillWbSection(el('wb-warn'), t('wb.warn'), warn);
    fillWbSection(el('wb-fcast'), t('wb.fcast'), fcast);
    // HKS-86: never auto-open — flag a warning by amber-ing the weather tab + the ⚠ chip
    document.getElementById('sd-tab-wx').classList.toggle('warn', !!warn);
    const warnChip = el('wx-warn');
    warnChip.classList.toggle('warn', !!warn);
    warnChip.textContent = warn ? `⚠ ${t('wb.chip')}` : (fcast ? t('wb.chip') : '');
    const rainy = [53,54,62,63,64,65].includes(code) || rainMax > 0;
    chk('rain', rainy);
    // real past-hour cloud-to-ground lightning count (data.gov.hk LHL), region-aware
    const lregion = /lantau/.test(el('src').value) ? 'Lantau' : 'Hong Kong territory';
    let cg = 0; for (const row of (lhl.data || [])) if (row[1] === 'Cloud-to-ground' && row[2] === lregion) cg = +row[3] || 0;
    const stormy = cg > 0 || code === 65 || /thunderstorm|雷暴/i.test(warn);
    chk('lightning', stormy);
    setThunderRate(cg > 0 ? Math.min(1, 0.15 + cg / 150) : (stormy ? 0.4 : 0));   // strikes/hr → rate
    el('wx-warn').dataset.ltg = cg;                     // (available for a HUD readout if wanted)
    // HKS-101: derive the live territory cloudiness and refresh the spatial
    // cloud field. Partial skies (sunny periods/intervals) now turn the cloud
    // layer ON with a sparse field, instead of an all-or-nothing toggle.
    cloudField.amt = cloudAmtFromObs(code, h ? +h.value : NaN, rainMax);
    chk('clouds', rainy || [60,61,76].includes(code) || cloudField.amt >= 0.3);
    refreshCloudField();
    chk('fog', [83,84,85].includes(code) || (h && +h.value >= 90));
    chk('waves', true);
    // real tropical-cyclone signal from the HKO warning summary
    const tc = stormFromWarn(ws);
    if (tc.dir) { el('winddir').value = tc.dir; setWindDir(tc.dir); }
    el('storm').value = String(tc.level);
    applyStorm(tc.level);
    // HKS-67/69: hand the fetched payloads to WxField so registered consumers
    // (rain/cloud/lightning/haze/flood fields) rebuild on this same 5-min cadence
    // without refetching; rebuildFields isolates consumer errors internally. The
    // English rhrread drives the spatial fields so name lookups work in zh-hk.
    lastWxData = { rhrread: rhEn || rh, flw: fl, warnsum: ws, lhl };   // cached for source-change re-maps (codex)
    WxField.rebuildFields(lastWxData);
    syncLiveWind();                        // HKS-101: steer the drift to the real observed wind (overrides the default / tc.dir)
  } catch (e) { el('wx-status').textContent = t('wx.unavail'); console.error(e); }
}

function tickHKClock() {
  document.getElementById('wx-clock').textContent =
    new Date().toLocaleTimeString('en-GB', { timeZone: 'Asia/Hong_Kong', hour12: false }) + ' HKT';
}

function setLiveMode(on) {
  liveMode = on;
  document.getElementById('wxhud').style.display = on ? '' : 'none';
  if (on) {                // live weather forces the sky to live HKT as well
    const m = document.getElementById('skymode');
    if (m.value !== 'live') { m.value = 'live'; m.dispatchEvent(new Event('change')); }
  }
  applyControlLocks();     // live data owns everything; keeps storm-driven locks coherent too
  const btn = document.getElementById('livebtn');
  btn.textContent = on ? t('live.on') : t('live.sync');
  btn.classList.toggle('on', on);
  clearInterval(wxClockT); clearInterval(wxRefreshT);
  if (on) {
    tickHKClock(); wxClockT = setInterval(tickHKClock, 1000);
    syncLiveWeather(); syncLiveTide();
    wxRefreshT = setInterval(() => { syncLiveWeather(); syncLiveTide(); }, 300000);
    startRadar();                                         // radar rides with the live weather box (HKS-74)
  } else {
    stopRadar();
    // HKS-101: drop the live cloud field; the sprite deck returns to the uniform
    // manual behaviour (updateWindVisuals restores opacity/visibility)
    cloudField.data = null; cloudField.form = null; cloudField.src = ''; cloudField.satDead = 0;
    setWindDir(document.getElementById('winddir').value);   // HKS-101: revert the drift to the manual dropdown (live steered windVec continuously)
    if (cloudGrp) updateWindVisuals();
    // keep whatever live sync produced: adopt the last live tide level as the manual value
    tideManual = tideLevel; tideSeries = null;
    document.getElementById('tide').value = Math.round(tideManual * 100);
    document.getElementById('tidev').textContent = Math.round(tideManual * 100) + '%';
  }
}
document.getElementById('livebtn').addEventListener('click', () => { setLiveMode(!liveMode); track('live_weather', { on: liveMode }); });
document.getElementById('reset').addEventListener('click', () => { frameCamera(); track('reset_view'); });
document.getElementById('south').addEventListener('click', southView);
document.getElementById('top').addEventListener('click', topView);

// ---- live per-station weather overlay (HKO automatic weather stations) -----
// Coordinates are baked (data/hko-stations.json, HK1980 grid). Live readings
// come from HKO's regional-weather CSVs, which lack CORS headers — so we route
// them through data.gov.hk's historical-archive, which re-serves with CORS *.
let stationData = null, stationMarkers = [], stationsOn = false, stationT = null, wxEmoji = '⛅';
let lastStationReadings = {};   // cache so the wind/marine toggle re-filters without a refetch
// When true, only plot stations that report air temperature — HKO's wind/marine-only
// stations (Central Pier, Star Ferry, Waglan…) are hidden. The "+ wind/marine stns"
// checkbox flips this (HKS-7); the wind-lead rendering below stays intact.
let stationsTempOnly = true;
// Per-station rainfall isn't published — HKO's regional-weather set has no rainfall CSV,
// only district totals (18) via rhrread. So map each station to its district and show
// that district's past-hour rainfall on the card/tooltip, honestly labelled (HKS-6).
const STATION_DISTRICT = {
  'Central Pier': 'Central & Western District', 'Chek Lap Kok': 'Islands District', 'Cheung Chau': 'Islands District',
  'Cheung Chau Beach': 'Islands District', 'Clear Water Bay': 'Sai Kung', 'Green Island': 'Central & Western District',
  'HK Observatory': 'Yau Tsim Mong', 'HK Park': 'Central & Western District', 'Happy Valley': 'Wan Chai',
  'Hong Kong Sea School': 'Southern District', 'Kai Tak': 'Kowloon City', 'Kai Tak Runway Park': 'Kowloon City',
  'Kau Sai Chau': 'Sai Kung', "King's Park": 'Yau Tsim Mong', 'Kowloon City': 'Kowloon City', 'Kwun Tong': 'Kwun Tong',
  'Lamma Island': 'Islands District', 'Lau Fau Shan': 'Yuen Long', 'Ngong Ping': 'Islands District', 'North Point': 'Eastern District',
  'Pak Tam Chung': 'Sai Kung', 'Peng Chau': 'Islands District', 'Sai Kung': 'Sai Kung', 'Sha Chau': 'Islands District',
  'Sha Tin': 'Sha Tin', 'Sham Shui Po': 'Sham Shui Po', 'Shau Kei Wan': 'Eastern District', 'Shek Kong': 'Yuen Long',
  'Sheung Shui': 'North District', 'Stanley': 'Southern District', 'Star Ferry': 'Yau Tsim Mong', 'Ta Kwu Ling': 'North District',
  'Tai Lung': 'North District', 'Tai Mei Tuk': 'Tai Po', 'Tai Mo Shan': 'Tsuen Wan', 'Tai Po': 'Tai Po', 'Tai Po Kau': 'Tai Po',
  'Tap Mun': 'Tai Po', "Tate's Cairn": 'Wong Tai Sin', 'The Peak': 'Central & Western District', 'Tseung Kwan O': 'Sai Kung',
  'Tsing Yi': 'Kwai Tsing', 'Tsuen Wan Ho Koon': 'Tsuen Wan', 'Tsuen Wan Shing Mun Valley': 'Tsuen Wan', 'Tuen Mun': 'Tuen Mun',
  'Waglan Island': 'Islands District', 'Wetland Park': 'Yuen Long', 'Wong Chuk Hang': 'Southern District',
  'Wong Tai Sin': 'Wong Tai Sin', 'Yuen Long Park': 'Yuen Long',
};
let districtRain = {};   // { district: max mm, past hour } from rhrread
const ARCHIVE = 'https://api.data.gov.hk/v1/historical-archive/get-file?url=';
const REGIONAL = 'https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/';

function ghTime() {   // HKT ~15 min ago as YYYYMMDD-HHMM: the archive only has snapshots
  const m = new Date(Date.now() - 15 * 60000)   // up to the last archived version, not the current minute
    .toLocaleString('en-CA', { timeZone: 'Asia/Hong_Kong', hour12: false })
    .match(/(\d{4})-(\d{2})-(\d{2})[,\s]+(\d{2}):(\d{2})/);
  return m ? `${m[1]}${m[2]}${m[3]}-${m[4]}${m[5]}` : '';
}
const regUrl = file => ARCHIVE + encodeURIComponent(REGIONAL + file) + '&time=' + ghTime();
function parseCsv(text) {
  const out = [];
  for (const line of (text || '').trim().split(/\r?\n/).slice(1)) {
    const c = line.split(','); if (c.length >= 2) out.push(c);
  }
  return out;
}
async function fetchStationReadings() {
  const grab = f => fetch(regUrl(f)).then(r => r.ok ? r.text() : '').catch(() => '');
  const [t, h, w, p] = await Promise.all([
    grab('latest_1min_temperature.csv'), grab('latest_1min_humidity.csv'),
    grab('latest_10min_wind.csv'), grab('latest_1min_pressure.csv'),
  ]);
  const R = {}, at = n => (R[n] || (R[n] = {}));
  for (const r of parseCsv(t)) at(r[1].trim()).temp = r[2];
  for (const r of parseCsv(h)) at(r[1].trim()).rh = r[2];
  for (const r of parseCsv(w)) { const s = at(r[1].trim()); s.wdir = r[2]; s.wspd = r[3]; s.gust = r[4]; }
  for (const r of parseCsv(p)) at(r[1].trim()).pres = r[2];
  return R;
}
function iconEmoji(c) {            // HKO weather-icon code -> emoji (rain/sun status)
  if (c == null) return '⛅';
  if (c === 50) return '☀️';
  if ([51, 52, 77].includes(c)) return '🌤️';
  if ([53, 54, 62, 63].includes(c)) return '🌦️';
  if ([60, 61, 76].includes(c)) return '☁️';
  if (c === 64) return '🌧️';
  if (c === 65) return '⛈️';
  if ([83, 84, 85].includes(c)) return '🌫️';
  if ([70, 71, 72, 73, 74, 75].includes(c)) return '🌙';
  if (c === 80) return '💨';
  if ([90, 91].includes(c)) return '🔥';
  if ([92, 93].includes(c)) return '❄️';
  return '⛅';
}
async function fetchWxEmoji() {   // territory-wide condition + per-district rainfall (rhrread is CORS-open)
  try {
    const j = await fetch('https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=en&dataType=rhrread').then(r => r.json());
    wxEmoji = iconEmoji((j.icon || [])[0]);
    const R = {};
    for (const d of ((j.rainfall && j.rainfall.data) || [])) if (d.place != null && isFinite(+d.max)) R[d.place] = +d.max;
    districtRain = R;
  } catch (_) {}
}
function tempColor(t) {           // 12°C (blue) -> 36°C (red)
  const x = Math.max(0, Math.min(1, (t - 12) / 24));
  return `rgb(${Math.round(70 + x*170)},${Math.round(130 - x*40)},${Math.round(210 - x*170)})`;
}
async function ensureStations() {
  if (stationData) return;
  const ver = new URLSearchParams(location.search).get('v');
  stationData = await fetch(asset('data/hko-stations.json') + (ver ? '?v=' + ver : '')).then(r => r.json());
}
function clearStationMarkers() { stationMarkers.forEach(m => m.el.remove()); stationMarkers = []; }
function buildStationMarkers() {
  clearStationMarkers();
  for (const s of stationData.stations) {
    const el = document.createElement('div'); el.className = 'stn'; el.style.display = 'none';
    const nm = `<span class="nm">${s.zh ? `<span class="zh">${s.zh}</span>` : ''}<span class="en">${s.name}</span></span>`;
    el.innerHTML = `<div class="row"><span class="ic">·</span><span class="t">–</span></div><span class="rh"></span>${nm}<div class="tip"></div>`;
    document.body.appendChild(el);
    stationMarkers.push({ el, E: s.E, N: s.N, name: s.name, zh: s.zh });
  }
}
function applyStationReadings(R) {
  for (const m of stationMarkers) {
    const d = R[m.name] || {}, temp = parseFloat(d.temp);
    const rain = districtRain[STATION_DISTRICT[m.name]];   // district past-hour rainfall, mm (HKS-6)
    const ic = m.el.querySelector('.ic'), tEl = m.el.querySelector('.t'), rhEl = m.el.querySelector('.rh');
    // in temp-only mode, flag stations with no thermometer so updateStations skips them
    m.hidden = stationsTempOnly && !isFinite(temp);
    if (m.hidden) { m.el.style.display = 'none'; continue; }
    // temperature stations lead with temp; wind-only stations lead with wind
    if (isFinite(temp)) {
      ic.textContent = wxEmoji;
      tEl.textContent = Math.round(temp) + '°'; tEl.style.color = tempColor(temp);
      rhEl.textContent = [d.rh ? `💧 ${d.rh}%` : '', rain > 0 ? `🌧${rain}` : ''].filter(Boolean).join(' · ');
    } else if (isFinite(parseFloat(d.wspd))) {
      const gust = parseFloat(d.gust), dir = d.wdir && d.wdir !== 'N/A' ? d.wdir : '';
      ic.textContent = '💨';
      tEl.textContent = Math.round(parseFloat(d.wspd)); tEl.style.color = 'rgba(224,236,245,.9)';
      rhEl.textContent = `${dir}${isFinite(gust) ? ` · ${t('tip.gust')} ${gust}` : ''}`.trim();
    } else {
      ic.textContent = wxEmoji;
      tEl.textContent = '–'; tEl.style.color = 'var(--sub)';
      rhEl.textContent = d.pres ? `${d.pres} hPa` : '';
    }
    const rows = [`<b>${m.zh ? m.zh + ' · ' : ''}${m.name}</b>`];
    if (isFinite(temp)) rows.push(`${temp}°C`);
    if (d.rh) rows.push(`${t('tip.humidity')} ${d.rh}%`);
    if (d.wdir) rows.push(`${t('tip.wind')} ${d.wdir} ${d.wspd || '–'} km/h${d.gust ? ` · ${t('tip.gust')} ${d.gust}` : ''}`);
    if (d.pres) rows.push(`${d.pres} hPa`);
    if (rain != null) rows.push(`${t('tip.rain')} ${rain} mm`);
    m.el.querySelector('.tip').innerHTML = rows.join('<br>');
  }
}
async function refreshStations() {
  await ensureStations();
  if (!stationMarkers.length) buildStationMarkers();
  try {
    const [readings] = await Promise.all([fetchStationReadings(), fetchWxEmoji()]);
    lastStationReadings = readings;
    applyStationReadings(readings);
  } catch (e) { console.error('stations', e); }
}
async function setStations(on) {
  stationsOn = on;
  clearInterval(stationT);
  if (on) { await refreshStations(); stationT = setInterval(refreshStations, 300000); }
  else clearStationMarkers();
}
document.getElementById('stations').addEventListener('change', e => { setStations(e.target.checked); if (e.isTrusted) track('layer_toggle', { layer: 'stations', on: e.target.checked }); });
// HKS-7: include HKO's wind/marine-only stations (checked) vs temperature stations only
document.getElementById('stationswind').addEventListener('change', e => {
  stationsTempOnly = !e.target.checked;
  if (stationsOn && stationMarkers.length) { applyStationReadings(lastStationReadings); updateStations(); }
  if (e.isTrusted) track('layer_toggle', { layer: 'stationswind', on: e.target.checked });
});

// ---- EPD air quality (HKS-5): AQHI chips per monitoring station -------------
// dashboard.data.gov.hk serves the individual-station AQHI feed with open CORS
// (the EPD origin itself doesn't) — no proxy needed. Chips are coloured by the
// official AQHI bands and refresh every 10 minutes while the layer is on.
let aqhiData = null, aqhiMarkers = [], aqhiOn = false, aqhiT = null;
const AQHI_URL = 'https://dashboard.data.gov.hk/api/aqhi-individual?format=json';
const AQHI_RISK_ZH = { 'Low': '低', 'Moderate': '中', 'High': '高', 'Very High': '甚高', 'Serious': '嚴重' };
function aqhiBand(v) {             // official band colours: low→serious
  if (v >= 11) return '#3d3a45';   // serious (black)
  if (v >= 8)  return '#8d5524';   // very high (brown)
  if (v >= 7)  return '#d23c2a';   // high (red)
  if (v >= 4)  return '#e8892b';   // moderate (orange)
  return '#3f9e4d';                // low (green)
}
async function ensureAqhiStations() {
  if (aqhiData) return;
  aqhiData = await fetch(asset('data/epd-aqhi-stations.json')).then(r => r.json());
}
function clearAqhiMarkers() { aqhiMarkers.forEach(m => m.el.remove()); aqhiMarkers = []; }
function buildAqhiMarkers() {
  clearAqhiMarkers();
  for (const s of aqhiData.stations) {
    const el = document.createElement('div'); el.className = 'aqm'; el.style.display = 'none';
    el.innerHTML = `<span class="ix">–</span>` +
      `<span class="nm"><span class="zh">${s.zh}</span><span class="en">${s.name}</span></span><div class="tip"></div>`;
    document.body.appendChild(el);
    aqhiMarkers.push({ el, E: s.E, N: s.N, name: s.name, zh: s.zh, kind: s.kind, hidden: true });
  }
}
async function refreshAqhi() {
  await ensureAqhiStations();
  if (!aqhiMarkers.length) buildAqhiMarkers();
  try {
    const rows = await fetch(AQHI_URL).then(r => r.json());
    const byName = new Map(rows.map(r => [r.station, r]));
    for (const m of aqhiMarkers) {
      const d = byName.get(m.name);
      m.hidden = !d || !isFinite(+d.aqhi);
      if (m.hidden) { m.el.style.display = 'none'; continue; }
      const ix = m.el.querySelector('.ix');
      ix.textContent = d.aqhi;
      ix.style.background = aqhiBand(+d.aqhi);
      const risk = isZh() ? (AQHI_RISK_ZH[d.health_risk] || d.health_risk) : d.health_risk;
      m.el.querySelector('.tip').innerHTML =
        `<b>${m.zh} · ${m.name}</b><br>AQHI ${d.aqhi} · ${risk}` +
        `<br>${m.kind === 'roadside' ? (isZh() ? '路邊監測站' : 'roadside station') : (isZh() ? '一般監測站' : 'general station')}` +
        `<br>${(d.publish_date || '').replace('T', ' ')}`;
    }
  } catch (e) { console.error('aqhi', e); }
}
async function setAqhi(on) {
  aqhiOn = on;
  clearInterval(aqhiT);
  if (on) { await refreshAqhi(); aqhiT = setInterval(refreshAqhi, 600000); }
  else clearAqhiMarkers();
}
document.getElementById('aqhi').addEventListener('change', e => { setAqhi(e.target.checked); if (e.isTrusted) track('layer_toggle', { layer: 'aqhi', on: e.target.checked }); });
function updateAqhi() {
  if (!aqhiOn || !aqhiMarkers.length || !curG) return;
  const g = curG;
  for (const m of aqhiMarkers) {
    if (m.hidden) { m.el.style.display = 'none'; continue; }
    const col = (m.E - g.bE) / g.aE, row = (m.N - g.bN) / g.aN;
    if (col < 0 || col > W - 1 || row < 0 || row > H - 1) { m.el.style.display = 'none'; continue; }
    const lx = (col - W/2)*cell, ly = sampleE(col, row)*VE, lz = (row - H/2)*cell;
    v.set(lx, ly, lz);
    world.localToWorld(v); v.project(camera);
    if (v.z > 1 || occludedLocal(lx, ly, lz)) { m.el.style.display = 'none'; continue; }
    m.el.style.display = '';
    m.el.style.left = ((v.x*0.5 + 0.5) * innerWidth) + 'px';
    m.el.style.top  = ((-v.y*0.5 + 0.5) * innerHeight) + 'px';
  }
}

// project station markers onto the terrain each frame (like the peak labels)
function updateStations() {
  if (!stationsOn || !stationMarkers.length || !curG) return;
  const g = curG;
  for (const m of stationMarkers) {
    if (m.hidden) { m.el.style.display = 'none'; continue; }   // no-temperature station (temp-only mode)
    const col = (m.E - g.bE) / g.aE, row = (m.N - g.bN) / g.aN;
    if (col < 0 || col > W - 1 || row < 0 || row > H - 1) { m.el.style.display = 'none'; continue; }
    const lx = (col - W/2)*cell, ly = sampleE(col, row)*VE, lz = (row - H/2)*cell;
    v.set(lx, ly, lz);
    world.localToWorld(v); v.project(camera);
    if (v.z > 1 || occludedLocal(lx, ly, lz)) { m.el.style.display = 'none'; continue; }
    m.el.style.display = '';
    m.el.style.left = ((v.x*0.5 + 0.5) * innerWidth) + 'px';
    m.el.style.top  = ((-v.y*0.5 + 0.5) * innerHeight) + 'px';
  }
}

// ---- WxField (HKS-67): region → geography scalar fields --------------------
// Foundation for the regional-weather epic (HKS-66). Turns per-region scalar
// readings (one number per HKO/EPD station, baked HK1980 E/N coordinates) into
// a smooth spatial field that the render loop can sample cheaply at any
// terrain-local coordinate. No user-visible output of its own — the phenomenon
// issues each feed it their own scalars:
//   rain (HKS-69), lightning (HKS-68), AQHI haze (HKS-71), flood (HKS-70).
//
// How a consumer uses it (all coordinates are terrain-LOCAL x/z — the same
// frame as rainPts/cloudGrp children of `world`, metres × mesh cell):
//   WxField.onRefresh(data => {              // runs after each live-data sync
//     const pts = myScalars(data)            // data = { rhrread, flw, warnsum, lhl }
//       .map(s => ({ ...WxField.mapStationToWorld(s), v: s.value }));
//     WxField.set('rain', pts);              // precomputes the coarse grid
//   });
//   ...per frame / per particle:  WxField.sample('rain', x, z)   // O(1) bilinear
//
// Interpolation: inverse-distance weighting (power 2 by default) over the
// station points, precomputed once per refresh into a coarse grid covering the
// map extent; sample() bilinearly interpolates that grid — smooth everywhere,
// no blocky region boundaries, and graceful at the edges (clamped) and with
// sparse/no data (fallback value).
const WxField = (() => {
  const fields = Object.create(null);   // name -> last built field
  const refreshCbs = [];                // consumer callbacks, run per live sync

  // HK1980 grid E/N -> terrain-local { x, z }. This is the SAME transform the
  // station cards / AQHI chips / GPS marker use (see updateStations):
  //   col = (E - g.bE) / g.aE, row = (N - g.bN) / g.aN, then grid-centre offset.
  // Returns null until the terrain (curG) is loaded or for bad input.
  function mapStationToWorld(station) {
    if (!curG || !station || !isFinite(station.E) || !isFinite(station.N)) return null;
    const g = curG, col = (station.E - g.bE) / g.aE, row = (station.N - g.bN) / g.aN;
    return { x: (col - W / 2) * cell, z: (row - H / 2) * cell };
  }

  // Look up a baked HKO station (data/hko-stations.json) by the names the live
  // feeds use. Normalised so rhrread's "Hong Kong Observatory" / "Hong Kong
  // Park" match the JSON's "HK Observatory" / "HK Park". Consumers must
  // `await ensureStations()` first — returns null until that JSON is loaded.
  let hkoIdx = null, hkoIdxSrc = null;
  const normName = s => String(s).toLowerCase().replace(/hong kong/g, 'hk').replace(/[^a-z0-9]/g, '');
  function hkoStationEN(name) {
    if (!stationData) return null;
    if (!hkoIdx || hkoIdxSrc !== stationData) {
      hkoIdx = new Map(stationData.stations.map(s => [normName(s.name), s]));
      hkoIdxSrc = stationData;
    }
    const s = hkoIdx.get(normName(name));
    return s ? { E: s.E, N: s.N, name: s.name } : null;
  }

  // Build a smooth field from points = [{ x, z, v }] (terrain-local coords +
  // scalar). opts: { res = 48 grid cells per side, power = 2 IDW exponent,
  // fallback = 0 value when there is no data }. Cost: res² × nPoints once per
  // refresh (48² × ~50 ≈ 115k mul — negligible); sample() is a bilinear lookup.
  function makeField(points, opts) {
    const o = opts || {}, res = Math.max(2, o.res || 48), power = o.power || 2, fallback = o.fallback ?? 0;
    const pts = (points || []).filter(p => p && isFinite(p.x) && isFinite(p.z) && isFinite(p.v));
    if (!curG || !W || !pts.length)   // no terrain yet or no data: constant field
      return { sample: () => fallback, grid: null, res: 0, min: fallback, max: fallback, n: 0, empty: true };
    const b = bounds(), x0 = -b.halfX, z0 = -b.halfZ, dx = (2 * b.halfX) / (res - 1), dz = (2 * b.halfZ) / (res - 1);
    // soften the IDW kernel by ~one grid cell so the surface stays smooth (no
    // singular spikes) right on top of a station, and never divides by zero
    const soft2 = Math.pow(Math.max(dx, dz), 2);
    const grid = new Float32Array(res * res);
    let min = Infinity, max = -Infinity;
    for (let iz = 0; iz < res; iz++) {
      const z = z0 + iz * dz;
      for (let ix = 0; ix < res; ix++) {
        const x = x0 + ix * dx;
        let sw = 0, sv = 0;
        for (const p of pts) {
          const ddx = p.x - x, ddz = p.z - z;
          const w = 1 / Math.pow(ddx * ddx + ddz * ddz + soft2, power / 2);
          sw += w; sv += w * p.v;
        }
        const val = sv / sw;
        grid[iz * res + ix] = val;
        if (val < min) min = val;
        if (val > max) max = val;
      }
    }
    function sample(x, z) {          // O(1) bilinear lookup, clamped at the edges
      const fx = Math.min(res - 1, Math.max(0, (x - x0) / dx));
      const fz = Math.min(res - 1, Math.max(0, (z - z0) / dz));
      const ix = Math.min(res - 2, fx | 0), iz = Math.min(res - 2, fz | 0);
      const tx = fx - ix, tz = fz - iz, r0 = iz * res + ix, r1 = r0 + res;
      const a = grid[r0] + (grid[r0 + 1] - grid[r0]) * tx;
      const c = grid[r1] + (grid[r1 + 1] - grid[r1]) * tx;
      return a + (c - a) * tz;
    }
    return { sample, grid, res, x0, z0, dx, dz, min, max, n: pts.length, empty: false };
  }

  // District → world-centroid accumulators over STATION_DISTRICT — the shared
  // anchor pattern of every regional consumer (rain, cloud, lightning via LHL
  // regions, flood; HKS-103 DRY of the HKS-69 loop). Values are ACCUMULATORS
  // ({ x, z, n } sums plus the raw district name), not finished means, so a
  // consumer divides (c.x / c.n) itself and lightning can roll districts up
  // into LHL regions without changing today's arithmetic. `keyOf` maps a raw
  // district name to the grouping key (return null/undefined to skip the
  // station — checked BEFORE the station lookup, as the lightning consumer
  // always did); default: normalised district name. Callers must have awaited
  // ensureStations() first. Rebuilt per call on purpose: the terrain source
  // (HK/Lantau) and bounds can change between refreshes, and 50 station
  // lookups every 5 minutes cost nothing.
  const normDistrict = s => String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  function districtCentroids(keyOf) {
    const key = keyOf || normDistrict;
    const cent = Object.create(null);
    for (const [stn, dist] of Object.entries(STATION_DISTRICT)) {
      const k = key(dist); if (k == null) continue;
      const en = hkoStationEN(stn), w = en && mapStationToWorld(en);
      if (!w) continue;
      const c = cent[k] || (cent[k] = { x: 0, z: 0, n: 0, district: dist });
      c.x += w.x; c.z += w.z; c.n++;
    }
    return cent;
  }

  function set(name, points, opts) { return (fields[name] = makeField(points, opts)); }
  function get(name) { return fields[name] || null; }
  function sample(name, x, z, fallback) {
    const f = fields[name];
    return f && !f.empty ? f.sample(x, z) : (fallback ?? 0);
  }
  function onRefresh(cb) { refreshCbs.push(cb); }
  // Called by syncLiveWeather after each live fetch (5-min cadence) with the
  // payloads it already has — { rhrread, flw, warnsum, lhl } — so consumers
  // rebuild their fields without refetching. Errors in one consumer never
  // break the weather HUD or other consumers.
  function rebuildFields(data) {
    for (const cb of refreshCbs) {
      try {
        const p = cb(data || {});
        if (p && typeof p.catch === 'function') p.catch(e => console.error('wxfield', e));
      } catch (e) { console.error('wxfield', e); }
    }
  }

  // Field → ground-plane scaffolding shared by the ?debug canopy and the flood
  // sheen (HKS-103 DRY): paint a res×res RGBA canvas via pixel(data, q, i, ix, iz)
  // (write 4 bytes at q; i = iz * res + ix), upload it as a LinearFilter
  // CanvasTexture (GPU bilinear ≈ sample()) on a unit plane laid flat over the
  // map — rotation.x = -π/2 puts canvas row 0 at z = -halfZ (grid iz = 0) —
  // and scale it to bounds(). `st` is a caller-owned { cv, tex, mesh } holder
  // (canvas/texture/mesh are created once and repainted in place); the caller
  // keeps its own colour ramp, opacity animation, height and visibility.
  function fieldPlane(st, res, pixel, opts) {
    const o = opts || {};
    if (!st.cv) st.cv = document.createElement('canvas');
    st.cv.width = res; st.cv.height = res;
    const ctx = st.cv.getContext('2d'), img = ctx.createImageData(res, res);
    for (let iz = 0; iz < res; iz++) for (let ix = 0; ix < res; ix++) {
      const i = iz * res + ix;
      pixel(img.data, i * 4, i, ix, iz);
    }
    ctx.putImageData(img, 0, 0);
    const b = bounds();
    if (!st.mesh) {
      st.tex = new THREE.CanvasTexture(st.cv);
      st.tex.minFilter = st.tex.magFilter = THREE.LinearFilter;
      st.mesh = new THREE.Mesh(
        new THREE.PlaneGeometry(1, 1),
        new THREE.MeshBasicMaterial({ map: st.tex, transparent: true, opacity: o.opacity ?? 1, depthWrite: false }));
      st.mesh.rotation.x = -Math.PI / 2;
      st.mesh.renderOrder = o.renderOrder ?? 0;
      if (o.hidden) st.mesh.visible = false;
      world.add(st.mesh);
    }
    st.tex.needsUpdate = true;
    st.mesh.scale.set(2 * b.halfX, 2 * b.halfZ, 1);
    return st.mesh;
  }

  // ?debug heatmap: paint a field as a low-opacity canopy plane floating above
  // the terrain (added to `world`, so it spins with the map) to eyeball the
  // interpolation smoothness. Never created without the FLY_DEBUG flag.
  const dbgPlane = { cv: null, tex: null, mesh: null };
  function debugShowField(name) {
    if (!FLY_DEBUG || !curG || !W) return;
    const f = fields[name];
    if (!f || f.empty) { if (dbgPlane.mesh) dbgPlane.mesh.visible = false; return; }
    const span = Math.max(1e-9, f.max - f.min);
    const mesh = fieldPlane(dbgPlane, f.res, (d, q, i) => {   // blue→cyan→yellow→red ramp
      const t = (f.grid[i] - f.min) / span;
      d[q]     = Math.round(255 * Math.min(1, Math.max(0, 2 * t - 0.5)));
      d[q + 1] = Math.round(255 * Math.min(1, Math.max(0, t < 0.5 ? 2.4 * t : 2.4 * (1 - t))));
      d[q + 2] = Math.round(255 * Math.min(1, Math.max(0, 1.4 - 2.4 * t)));
      d[q + 3] = 235;
    }, { opacity: 0.35, renderOrder: 3 });
    mesh.position.y = zmax * VE + bounds().span * 0.02;   // canopy just above the peaks
    mesh.visible = true;
  }

  return { mapStationToWorld, hkoStationEN, normDistrict, districtCentroids, makeField, set, get, sample,
           onRefresh, rebuildFields, fieldPlane, debugShowField, fields };
})();

// ---- HKS-69: regional rain — per-district rainfall feeds the 'rain' field --
// WxField consumer (the first real phenomenon on the HKS-67 foundation): every
// live sync rebuilds a smooth 'rain' scalar field (mm, past hour) from
// rhrread's 18 district totals. rhrread names DISTRICTS, not stations, so each
// district is anchored at the centroid of its member stations — the same
// STATION_DISTRICT mapping the station cards already use for the district-
// rainfall tooltip (HKS-6), inverted. The render loop then samples the field
// per rain drop (animateWeather) and per cloud-cover lookup (cloudCoverAt).
WxField.onRefresh(async data => {
  const rows = (((data.rhrread || {}).rainfall || {}).data) || [];
  await ensureStations();                      // baked E/N for the station names
  // district → world-centroid accumulators of its stations (HKS-103: the
  // shared WxField.districtCentroids loop — see its notes on rebuild cadence)
  const cent = WxField.districtCentroids();
  const pts = [];
  for (const r of rows) {
    const c = r.place != null && cent[WxField.normDistrict(r.place)];
    if (c) pts.push({ x: c.x / c.n, z: c.z / c.n, v: Math.max(0, +r.max || 0) });
  }
  WxField.set('rain', pts, { fallback: 0 });
});

// ---- HKS-69: per-district cloud — real humidity + rainfall feed 'cloud' ----
// Second WxField consumer: every live sync rebuilds a smooth 'cloud' amount
// field (0..1 local cloudiness, cloudFromObs) from the SAME rhrread payload —
// per-station humidity (stations map directly via hkoStationEN) and the
// per-district rainfall totals anchored at their station centroids, exactly
// like the 'rain' consumer above. cloudCoverAt then reads the LOCAL amount
// from this field (procedural noise just shapes the lumps), so a dry
// low-humidity district shows broken/clear sky while a humid or raining one
// sits under overcast — the real sunny-side/rainy-side split. With no usable
// rows the field is set empty and cloudCoverAt keeps the HKS-101
// territory-amount behaviour.
WxField.onRefresh(async data => {
  const rr = data.rhrread || {};
  const humRows = ((rr.humidity || {}).data) || [];
  const rainRows = ((rr.rainfall || {}).data) || [];
  await ensureStations();                      // baked E/N for the station names
  // per-station humidity → world points (rhrread often carries a single
  // station; the IDW field then degrades to a flat territory RH — the spatial
  // signal still comes from the district rainfall below)
  const humPts = [];
  for (const r of humRows) {
    const en = WxField.hkoStationEN(r.place), w = en && WxField.mapStationToWorld(en);
    if (w && isFinite(+r.value)) humPts.push({ x: w.x, z: w.z, v: +r.value });
  }
  const rhAvg = humPts.length ? humPts.reduce((s, p) => s + p.v, 0) / humPts.length : NaN;
  const humF = humPts.length > 1 ? WxField.makeField(humPts, { fallback: rhAvg }) : null;
  // district centroids — the shared loop, same anchors as the 'rain' consumer (HKS-103)
  const cent = WxField.districtCentroids();
  const pts = [];
  for (const r of rainRows) {
    const c = r.place != null && cent[WxField.normDistrict(r.place)];
    if (!c) continue;
    const x = c.x / c.n, z = c.z / c.n;
    const rhHere = (humF && !humF.empty) ? humF.sample(x, z) : rhAvg;
    pts.push({ x, z, v: cloudFromObs(rhHere, Math.max(0, +r.max || 0)) });
  }
  // no district rainfall rows: fall back to the humidity stations alone
  if (!pts.length) for (const p of humPts) pts.push({ x: p.x, z: p.z, v: cloudFromObs(p.v, 0) });
  WxField.set('cloud', pts, { fallback: 0.5 });
});

// ---- HKS-68: regional lightning — LHL CG counts feed the 'lightning' field -
// HKO's LHL feed reports past-hour cloud-to-ground lightning counts for four
// regions — New Territories West / New Territories East / Hong Kong Island and
// Kowloon / Lantau — plus a "Hong Kong territory" total, as rows of
// [DateTime, Type, Region, count]. The regions name no coordinates, so each is
// anchored at the world centroid of the stations whose STATION_DISTRICT
// district falls inside it (the HKS-69 rain-centroid pattern, one level up).
// Every sync rebuilds the smooth 'lightning' field + liveLtg; the render loop
// then rate-limits strikes by the territory total, places bolts by
// rejection-sampling the field, and scales thunder by the field at the camera.
// An LHL fetch failure leaves liveLtg null -> today's global behaviour.
const LHL_DISTRICT_REGION = {
  'Yuen Long': 'New Territories West', 'Tuen Mun': 'New Territories West',
  'Tsuen Wan': 'New Territories West', 'Kwai Tsing': 'New Territories West',
  'North District': 'New Territories East', 'Tai Po': 'New Territories East',
  'Sha Tin': 'New Territories East', 'Sai Kung': 'New Territories East',
  'Central & Western District': 'Hong Kong Island and Kowloon', 'Wan Chai': 'Hong Kong Island and Kowloon',
  'Eastern District': 'Hong Kong Island and Kowloon', 'Southern District': 'Hong Kong Island and Kowloon',
  'Yau Tsim Mong': 'Hong Kong Island and Kowloon', 'Sham Shui Po': 'Hong Kong Island and Kowloon',
  'Kowloon City': 'Hong Kong Island and Kowloon', 'Wong Tai Sin': 'Hong Kong Island and Kowloon',
  'Kwun Tong': 'Hong Kong Island and Kowloon',
  'Islands District': 'Lantau',
};
WxField.onRefresh(async data => {
  const rows = (data.lhl || {}).data;
  if (!Array.isArray(rows)) { liveLtg = null; WxField.set('lightning', [], { fallback: 0 }); return; }
  await ensureStations();                      // baked E/N for the station names
  // LHL region -> world centroid of the stations in its districts: the shared
  // district-centroid loop keyed straight by LHL region (HKS-103) — stations
  // accumulate into each region in the same order as ever, so the centroids
  // stay bit-identical to the pre-refactor per-consumer loop.
  const cent = WxField.districtCentroids(d => LHL_DISTRICT_REGION[d]);
  const counts = Object.create(null);
  let territory = NaN;
  for (const r of rows) {
    if (!r || r[1] !== 'Cloud-to-ground') continue;      // cloud-to-cloud never grounds a bolt
    if (r[2] === 'Hong Kong territory') territory = Math.max(0, +r[3] || 0);
    else if (r[2] != null) counts[r[2]] = Math.max(0, +r[3] || 0);
  }
  const pts = []; let sum = 0;
  for (const [reg, c] of Object.entries(cent)) {
    const v = counts[reg] || 0; sum += v;
    pts.push({ x: c.x / c.n, z: c.z / c.n, v });
  }
  const total = isFinite(territory) ? territory : sum;   // territory row is authoritative (covers waters)
  // same strikes/hr -> rate curve syncLiveWeather uses, territory-wide
  liveLtg = { rate: total > 0 ? Math.min(1, 0.15 + total / 150) : 0 };   // total is derived here, not stored (review #10)
  WxField.set('lightning', pts, { fallback: 0 });
});

// ---- HKS-71: regional haze — EPD per-station AQHI feeds the 'haze' field ---
// WxField consumer over the same EPD air-quality feed the AQHI chip layer uses
// (dashboard.data.gov.hk, open CORS) with the baked HK1980 E/N per station in
// data/epd-aqhi-stations.json. Every live sync rebuilds a smooth 'haze' field
// of raw AQHI (1..10+); the feed itself updates ~hourly, so the rows are
// cached and refetched at the chip layer's 10-min cadence rather than every
// 5-min sync. The render loop samples the field at the camera (updateHaze).
// A fetch failure keeps the last rows; no rows at all leaves the field empty
// -> zero haze, today's behaviour.
let hazeRows = null, hazeRowsAt = 0;
WxField.onRefresh(async () => {
  try {
    await ensureAqhiStations();                  // baked E/N (also used by the chip layer)
    if (!hazeRows || Date.now() - hazeRowsAt > 600000) {
      const j = await fetch(AQHI_URL).then(r => r.json());
      if (Array.isArray(j)) { hazeRows = j; hazeRowsAt = Date.now(); }   // don't cache a 200-but-non-array error body for 10 min (review #4)
    }
  } catch (e) { console.error('haze', e); }      // keep any stale rows
  if (!Array.isArray(hazeRows) || !aqhiData) { WxField.set('haze', [], { fallback: 0 }); return; }
  const byName = new Map(hazeRows.filter(r => r && r.station != null).map(r => [r.station, r]));   // skip malformed feed rows (CodeRabbit)
  const pts = [];
  for (const s of aqhiData.stations) {
    const d = byName.get(s.name), w = WxField.mapStationToWorld(s);
    const a = d ? parseFloat(d.aqhi) : NaN;   // parseFloat so "10+" (Serious band) reads 10, not NaN → keeps haze heaviest under worst air (review #2)
    if (w && isFinite(a)) pts.push({ x: w.x, z: w.z, v: a });
  }
  WxField.set('haze', pts, { fallback: 0 });     // fallback = clean air
});

// Per-frame pollution haze (called from animate() once _camLocal is fresh).
// Samples local AQHI at the camera and eases hazeAmt toward it — flying or
// walking into a polluted district thickens the haze, leaving it clears.
// Pollution haze ≠ weather fog: a faint warm-brown desaturating distance
// tint, never white cloud. With the weather fog up (manual toggle or live)
// haze only warms its colour — an additive tint term; near/far stay the
// weather fog's own, so the two never fight. With no weather fog it owns a
// light THREE.Fog of its own (tagged __haze so setFog's fog is never
// mistaken for it) whose density scales with local AQHI, always thinner
// than the real weather fog. AQHI ≤ 3 (low band) is the clean-air baseline
// -> zero haze, today's behaviour; the live gates mirror the rain/lightning
// fields (liveMode, no T8+ storm override), and the Matrix skin keeps its
// own phosphor palette.
let hazeAmt = 0, hazeTinted = false;
const _hazeC = new THREE.Color(), HAZE_TINT = new THREE.Color(0x967f5f);
function updateHaze() {
  if (matrixOn) hazeAmt = 0;   // Matrix owns the palette — clear instantly, no eased brown fog over the phosphor void (review #6)
  let target = 0;
  if (liveMode && stormLevel < 8 && !matrixOn) {
    const f = WxField.get('haze');
    if (f && !f.empty) target = Math.max(0, Math.min(1, (f.sample(_camLocal.x, _camLocal.z) - 3) / 7));
  }
  hazeAmt += (target - hazeAmt) * 0.03;          // eased — district borders never pop
  if (hazeAmt < 0.005) {
    if (scene.fog && scene.fog.__haze) scene.fog = null;   // remove our fog
    else if (hazeTinted) setFog();                         // un-tint the weather fog
    hazeTinted = false;
    return;
  }
  renderer.getClearColor(_hazeC);                // sky base — same source as setFog / uFogCol
  if (!scene.fog) { scene.fog = new THREE.Fog(0xffffff, 1, 2); scene.fog.__haze = true; }
  if (scene.fog.__haze) {                        // haze-owned fog: subtle, AQHI-scaled visibility
    const span = mapSpan || bounds().span;   // cached by buildWeather — no per-frame bounds() allocation (HKS-103)
    scene.fog.near = span * (0.55 - 0.20 * hazeAmt);
    scene.fog.far  = span * (3.2  - 1.50 * hazeAmt);   // even AQHI 10+ stays lighter than weather fog
    scene.fog.color.copy(_hazeC).lerp(HAZE_TINT, 0.22 + 0.38 * hazeAmt);
    hazeTinted = false;
  } else {                                       // weather fog up: only warm/brown its colour
    scene.fog.color.copy(_hazeC).lerp(HAZE_TINT, 0.35 * hazeAmt);
    hazeTinted = true;
  }
}

// ---- HKS-70: regional flood / landslip cues — warnsum feeds the 'flood' field
// WxField consumer over the HKO warning summary syncLiveWeather already
// fetches (no new endpoint). warnsum is an object keyed by warning type —
// each member { name, code, actionCode, issueTime, ... }; a warning counts as
// active unless it is absent or its actionCode is CANCEL. Three warnings
// become a ground-hazard cue:
//   WFNTSA — Special Announcement on Flooding in the Northern New Territories:
//            AREA-specific → the northern-NT districts (North District,
//            Tai Po, Yuen Long), anchored by the HKS-69 district-centroid
//            pattern so the cue fades smoothly out of the region.
//   WL     — Landslip Warning: HKO issues it territory-wide → a low uniform
//            floor everywhere, tinted silty (saturated ground / muddy runoff).
//   WRAIN  — Rainstorm Warning Signal: territory-wide flood-risk context,
//            scaled by colour (Amber 0.25 / Red 0.55 / Black 0.85).
// The visual (rebuildFloodCue) is ONE quiet "risen water" sheen: a translucent
// plane a few metres above sea level whose per-cell alpha comes from the
// smooth 'flood' field masked to low-lying LAND — it pools in the flood
// plains of the affected regions and higher terrain hides it naturally.
// Deliberately non-alarmist: ≤ ~0.16 opacity, slow breathing, eased in/out
// (updateFloodCue), live-mode only, no new UI. No active warning, or live
// sync off → the sheen fades away and manual behaviour is untouched.
const FLOOD_NNT_DISTRICT = { 'North District': 1, 'Tai Po': 0.85, 'Yuen Long': 0.7 };
let floodCue = null;                  // { lvl 0..1, slipMix 0..1 } while a cue is active, else null
const floodPlane = { cv: null, tex: null, mesh: null };   // WxField.fieldPlane state (HKS-103)
let floodCueOp = 0;
WxField.onRefresh(async data => {
  const ws = data.warnsum || {};
  const on = w => !!(w && w.code && w.actionCode !== 'CANCEL');
  const nnt  = on(ws.WFNTSA) ? 1 : 0;                                    // flooding in the northern NT
  const slip = on(ws.WL) ? 0.45 : 0;                                     // landslip, territory-wide
  const rain = on(ws.WRAIN) ? ({ WRAINA: 0.25, WRAINR: 0.55, WRAINB: 0.85 }[ws.WRAIN.code] || 0.25) : 0;
  const base = Math.max(slip, rain);                                     // territory-wide floor
  if (!nnt && !base) {                                                   // nothing active → no cue
    floodCue = null; WxField.set('flood', [], { fallback: 0 });
    return;
  }
  await ensureStations();                      // baked E/N for the station names
  // district → world centroid of its stations — the shared HKS-69 loop
  // (WxField.districtCentroids, HKS-103); each accumulator carries its raw
  // district name for the FLOOD_NNT_DISTRICT lookup below.
  const cent = WxField.districtCentroids();
  // every district carries the territory-wide floor; the WFNTSA districts add
  // the area-specific flooding on top, so IDW fades the cue out of the region
  const pts = [];
  for (const c of Object.values(cent))
    pts.push({ x: c.x / c.n, z: c.z / c.n,
               v: Math.min(1, Math.max(base, nnt * (FLOOD_NNT_DISTRICT[c.district] || 0))) });
  WxField.set('flood', pts, { fallback: base });
  // silt share: landslip alone reads muddy; alongside flood/rain it only warms
  floodCue = { lvl: Math.max(base, nnt), slipMix: slip > 0 ? ((nnt || rain) ? 0.4 : 0.8) : 0 };
  rebuildFloodCue();
});

// Paint the sheen texture from the current 'flood' field: per-cell alpha =
// field intensity masked to land above ~1 m (the open sea is already water),
// colour a muted flood-water blue pulled toward silt while the landslip
// warning is up. Runs once per live sync (≤ 48² field cells) — negligible.
function rebuildFloodCue() {
  if (!floodCue || !curG || !W) return;
  const f = WxField.get('flood');
  const res = (f && !f.empty) ? f.res : 32;    // no field (stations not loaded): uniform floor
  const b = bounds(), x0 = -b.halfX, z0 = -b.halfZ, dx = 2 * b.halfX / (res - 1), dz = 2 * b.halfZ / (res - 1);
  const mix = 0.65 * floodCue.slipMix;         // water blue → silt
  const R = Math.round(96 + (168 - 96) * mix), G = Math.round(148 + (132 - 148) * mix), B = Math.round(196 + (84 - 196) * mix);
  // plane/texture scaffolding is WxField.fieldPlane (HKS-103); only the flood
  // colour ramp + land mask live here (renderOrder 2: over the translucent sea,
  // starting at opacity 0 / hidden until updateFloodCue eases it in)
  WxField.fieldPlane(floodPlane, res, (d, q, i, ix, iz) => {
    const x = x0 + ix * dx, z = z0 + iz * dz;
    let a = (f && !f.empty) ? f.grid[i] : floodCue.lvl;
    if (sampleE(x / cell + W / 2, z / cell + H / 2) < 1) a = 0;   // open water / shoreline
    d[q] = R; d[q + 1] = G; d[q + 2] = B;
    d[q + 3] = Math.round(255 * Math.max(0, Math.min(1, a)));
  }, { opacity: 0, renderOrder: 2, hidden: true });
}

// Per-frame flood-cue fade (called from animate()). Eases the sheen in/out
// and keeps it riding a few metres above sea level, breathing slowly. Gates
// mirror the other regional fields: live mode only, no T8+ storm override
// (the storm owns the drama), and never under the Matrix skin.
function updateFloodCue() {
  if (!floodPlane.mesh) return;
  const active = floodCue && liveMode && stormLevel < 8 && !matrixOn;
  const breath = 0.85 + 0.15 * Math.sin(performance.now() * 0.0005);
  const target = active ? (0.06 + 0.10 * Math.min(1, floodCue.lvl)) * breath : 0;
  floodCueOp += (target - floodCueOp) * 0.03;  // eased — warnings never pop
  if (floodCueOp < 0.005) { floodPlane.mesh.visible = false; return; }
  floodPlane.mesh.visible = true;
  floodPlane.mesh.material.opacity = floodCueOp;
  floodPlane.mesh.position.y = SEA_Y + 8 * VE;    // ~8 m of "risen water": pools in the flood plains
}

if (FLY_DEBUG) {
  window.__wxField = WxField;   // inspect fields / sample() from the console
  // demo consumer proving the plumbing: per-station air temperature from the
  // same rhrread payload syncLiveWeather fetched, rendered as the debug canopy.
  // Later phenomenon issues follow this exact pattern with their own scalars.
  WxField.onRefresh(async data => {
    const rows = (((data.rhrread || {}).temperature || {}).data) || [];
    if (!rows.length) return;
    await ensureStations();                    // baked E/N for the rhrread names
    const pts = [];
    for (const r of rows) {
      const en = WxField.hkoStationEN(r.place), w = en && WxField.mapStationToWorld(en);
      if (w && isFinite(+r.value)) pts.push({ x: w.x, z: w.z, v: +r.value });
    }
    WxField.set('demo-temp', pts);
    WxField.debugShowField('demo-temp');
  });
}

// ---- label projection + render loop ---------------------------------------
const v = new THREE.Vector3();

// Terrain occlusion for the DOM overlays (labels + station cards): hide a marker
// when a mountain sits between it and the camera. Instead of raycasting the huge
// mesh, we ray-march the elevation grid (heightfield) in the world group's LOCAL
// frame — cheap (O(steps) height lookups) and correct while the model spins.
const LABEL_OCCLUSION = true;   // set false to always show markers regardless of terrain
const _camLocal = new THREE.Vector3();
function occludedLocal(lx, ly, lz) {
  if (!LABEL_OCCLUSION) return false;
  const cx = _camLocal.x, cy = _camLocal.y, cz = _camLocal.z;
  const STEPS = 22, EPS = cell * 0.35;                 // small tolerance so grazing sightlines don't flicker
  for (let s = 1; s < STEPS; s++) {
    const f = s / STEPS;
    if (f > 0.9) break;                                // ignore the anchor's own surface near the target
    const px = cx + (lx - cx) * f, py = cy + (ly - cy) * f, pz = cz + (lz - cz) * f;
    const col = px / cell + W / 2, row = pz / cell + H / 2;
    if (col < 0 || col > W - 1 || row < 0 || row > H - 1) continue;
    if (py < sampleE(col, row) * VE - EPS) return true;   // terrain rises above the sightline → hidden
  }
  return false;
}
// Peaks dedupe against landmark peaks when the Landmarks layer is also on (landmarks win).
function updateLabels() {
  const lmOn = document.getElementById('landmarks').checked;
  projectLabelSet(labels, document.getElementById('labels').checked, lmOn ? landmarkPeakPts : null);
}
function updateLandmarks() { projectLabelSet(landmarks, document.getElementById('landmarks').checked); }

// shared: project a label set to screen, drop off-mesh/behind/occluded, then declutter
// (tallest first; hide overlaps). Used by both the peaks layer and the landmarks layer.
// `dedupe` (optional) is a list of {E,N} — labels within ~400 m of one are skipped.
function projectLabelSet(set, show, dedupe) {
  if (!show) { for (const l of set) l.div.style.display = 'none'; return; }
  const g = curG; if (!g) return;
  const cand = [];
  for (const l of set) {
    const col = (l.E - g.bE) / g.aE, row = (l.N - g.bN) / g.aN;
    if (col < 0 || col > W - 1 || row < 0 || row > H - 1) { l.div.style.display = 'none'; continue; }
    if (dedupe) { let dup = false; for (const p of dedupe) { const dE = p.E - l.E, dN = p.N - l.N; if (dE*dE + dN*dN < 160000) { dup = true; break; } } if (dup) { l.div.style.display = 'none'; continue; } }
    const lx = (col - W/2)*cell, ly = sampleE(col, row)*VE, lz = (row - H/2)*cell;
    v.set(lx, ly, lz); world.localToWorld(v); v.project(camera);
    if (v.z > 1 || occludedLocal(lx, ly, lz)) { l.div.style.display = 'none'; continue; }
    l._sx = (v.x*0.5 + 0.5) * innerWidth; l._sy = (-v.y*0.5 + 0.5) * innerHeight;
    cand.push(l);
  }
  // 2) declutter: tallest peaks win; hide any that would overlap one already placed
  //    (naturally reveals more peaks as you zoom in, since anchors spread apart)
  cand.sort((a, b) => b.ele - a.ele);
  const placed = [], PADX = 68, PADY = 36;
  for (const l of cand) {
    if (placed.some(q => Math.abs(q._sx - l._sx) < PADX && Math.abs(q._sy - l._sy) < PADY)) { l.div.style.display = 'none'; continue; }
    placed.push(l);
    l.div.style.display = '';
    l.div.style.left = l._sx + 'px';
    l.div.style.top  = l._sy + 'px';
  }
}
function resize() {
  renderer.setSize(innerWidth, innerHeight);
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
}
addEventListener('resize', resize);

// screen drips (HKS-20): droplets run down the "lens" in driving rain (T8+ or
// rain with strong wind) — subtle, capped, and cleared the moment it eases
const dripCv = document.getElementById('dripfx');
const dripCtx = dripCv.getContext('2d');
let drips = [], dripActive = false;
function stepDrips() {
  const heavy = weather.rain && (windStrength >= 0.55 || stormLevel >= 8);
  if (!heavy && !drips.length) {
    if (dripActive) { dripCtx.clearRect(0, 0, dripCv.width, dripCv.height); dripActive = false; }
    return;
  }
  dripActive = true;
  if (dripCv.width !== innerWidth || dripCv.height !== innerHeight) { dripCv.width = innerWidth; dripCv.height = innerHeight; }
  dripCtx.clearRect(0, 0, dripCv.width, dripCv.height);
  if (heavy && drips.length < 14 && Math.random() < 0.05 + windStrength * 0.06)
    drips.push({ x: Math.random() * innerWidth, y: -30, v: 2 + Math.random() * 4,
                 r: 1.5 + Math.random() * 2.5, wob: Math.random() * 6.28 });
  const slant = windVec.x * windStrength * 0.8;
  const mx = matrixOn;                                   // in the Matrix the lens streaks green
  for (const d of drips) {
    d.y += d.v * (0.7 + Math.random() * 0.6);            // stutter like real drips
    d.x += slant + Math.sin(d.y * 0.02 + d.wob) * 0.4;
    const tail = d.r * 14;
    const g = dripCtx.createLinearGradient(d.x, d.y - tail, d.x, d.y);
    g.addColorStop(0, mx ? 'rgba(57,255,106,0)' : 'rgba(205,222,240,0)');
    g.addColorStop(1, mx ? 'rgba(57,255,106,0.22)' : 'rgba(212,230,246,0.26)');
    dripCtx.fillStyle = g;
    dripCtx.beginPath(); dripCtx.roundRect(d.x - d.r * 0.6, d.y - tail, d.r * 1.2, tail, d.r); dripCtx.fill();
    dripCtx.fillStyle = mx ? 'rgba(150,255,180,0.4)' : 'rgba(226,239,250,0.4)';
    dripCtx.beginPath(); dripCtx.arc(d.x, d.y, d.r, 0, 7); dripCtx.fill();
  }
  drips = drips.filter(d => d.y < innerHeight + 30);
}

function animate() {
  requestAnimationFrame(animate);
  if (spinDir) world.rotation.y += 0.0016 * spinSpeed * spinDir;
  updateCelestial();                    // throttled internally to the sim minute
  stepSky();                            // twinkle clock, shooting stars, moon limb aim (HKS-78)
  if (sunRays.visible) sunRays.material.rotation += 0.0004;   // slow crown turn
  stepDrips();
  stepFlight();
  stepWalk();
  stepStargaze();
  stepMatrix();
  stepNoir();
  stepGpxAnim();                        // HKS-106: advance any playing GPX trail sweeps
  updateCompass();
  animateWeather();
  // storm screen shake — the terrain judders under the strongest signals
  const sh = stormLevel >= 10 ? 1 : stormLevel >= 9 ? 0.6 : stormLevel >= 8 ? 0.32 : 0;
  if (sh > 0) { const a = bounds().span * 0.0012 * sh; world.position.set((Math.random()*2-1)*a, (Math.random()*2-1)*a, (Math.random()*2-1)*a); }
  else if (world.position.x || world.position.y || world.position.z) world.position.set(0, 0, 0);
  // flight, walk and stargaze own the camera; OrbitControls.update() ignores
  // .enabled and would re-seat the camera on its orbit sphere every frame (the
  // walk-mode "rotating from a weird point" bug) — so skip it in all three
  if (!flight.on && !walk.on && !stargaze.on) controls.update();
  updateClip();                 // keep near/far tuned to the current zoom distance
  renderer.render(scene, camera);
  world.updateMatrixWorld();    // camera position in the terrain's local frame, for occlusion tests
  _camLocal.copy(camera.position); world.worldToLocal(_camLocal);
  updateHaze();                 // HKS-71: local AQHI haze at the camera (renders next frame)
  updateFloodCue();             // HKS-70: regional flood/landslip warning sheen
  updateLabels();
  updateLandmarks();
  updateGpxLabels();            // HKS-106: GPX Start/End labels — constant screen size, terrain-occluded
  updateStations();
  updateAqhi();
  updateGeoMarker();
  updateCompassView();
  updateSkyAuto();        // stargazing walk mode: figures in view light up (HKS-84)
  updateConstLabels();    // bilingual constellation name cards (HKS-84)
}

// ---- shareable state: sync all controls + camera to the URL ----------------
function serializeState() {
  const g = id => document.getElementById(id);
  const p = new URLSearchParams();
  p.set('s', g('src').value);
  p.set('surf', g('surf').value);
  p.set('bg', g('bg').value);
  p.set('ve', walk.on && walk.prevVE != null ? String(walk.prevVE) : g('ve').value);   // mid-walk the slider is pinned to 1 — share the REAL exaggeration so it survives the link
  p.set('oh', g('skinlift').value);   // overlay drape height (real m; world lift = oh·VE)
  p.set('d', String(meshStep));
  p.set('ml', g('meshlines').checked ? '1' : '0');
  p.set('w', g('water').checked ? '1' : '0');
  p.set('lb', g('labels').checked ? '1' : '0');
  p.set('lm', g('landmarks').checked ? '1' : '0');
  p.set('L', [...document.querySelectorAll('#layers input:checked')].map(i => i.id.slice(4)).join('.'));
  if (wireColor) p.set('mc', wireColor.slice(1));
  p.set('sc', solidColor.slice(1));
  if (texRot) p.set('tx', String(texRot));          // B50K topo raster rotation (only when nudged)
  p.set('sp', String(spinDir));
  p.set('ss', String(spinSpeed));
  p.set('fo', weather.fog ? '1' : '0');
  p.set('ra', weather.rain ? '1' : '0');
  p.set('cl', weather.clouds ? '1' : '0');
  p.set('li', weather.lightning ? '1' : '0');
  p.set('wv', weather.waves ? '1' : '0');
  // under Neon Night snow is forced on — share the user's own pre-Neon value so
  // a reloaded link re-snapshots it and still exits the mode cleanly (HKS-72)
  p.set('sn', (neonOn && nnPrevSnow != null ? nnPrevSnow : weather.snow) ? '1' : '0');
  if (FLY_DEBUG) p.set('debug', '1');
  p.set('mx', matrixOn ? '1' : '0');
  p.set('nn', neonOn ? '1' : '0');
  const md = flight.on ? 'fly' : walk.on ? 'walk' : stargaze.on ? 'star' : '';   // HKS-91: share the movement mode
  if (md) p.set('md', md);
  if (g('planeskin').value !== 'prop') p.set('pl', g('planeskin').value);        // HKS-93: aircraft skin (only off the default)
  if (geo.has) p.set('gps', Math.round(geo.E) + ',' + Math.round(geo.N));         // HKS-91: share your location (HK1980 grid E,N)
  // HKS-91: the Stargaze vantage + look — the serialized `cam` target is 1000m in
  // front of the viewer (stepStargaze), so restore the anchor from this instead (codex)
  if (stargaze.on) p.set('sg', [Math.round(stargaze.pos.x), Math.round(stargaze.pos.z), stargaze.yaw.toFixed(3), stargaze.pitch.toFixed(3)].join(','));
  p.set('au', sndOn ? '1' : '0');
  p.set('av', g('sndvol').value);
  p.set('su', skySim.on ? '1' : '0');
  p.set('sl', skySim.live ? '1' : '0');
  if (!skySim.live) { p.set('sd', skySim.date); p.set('sm', String(skySim.minutes)); }
  p.set('sk', g('skyh').value);
  p.set('ti', String(Math.round(tideManual * 100)));
  p.set('tr', String(Math.round(thunderRate * 100)));
  p.set('st', String(stormLevel));
  p.set('wi', String(Math.round(windStrength * 100)));
  p.set('wd', g('winddir').value);
  p.set('lv', liveMode ? '1' : '0');
  p.set('ws', stationsOn ? '1' : '0');
  p.set('wm', document.getElementById('stationswind').checked ? '1' : '0');
  p.set('aq', aqhiOn ? '1' : '0');
  p.set('rdr', radarRange === '256' ? '2' : radarRange === '128' ? '1' : '0');   // radar range 0/1/2 = 64/128/256 (HKS-74)
  if (wxMode === 'sat') p.set('wxv', 's');          // weather-imagery view: radar (default) | satellite (HKS-79)
  if (satZoom === 'x8M') p.set('sz', '1');          // satellite zoom: wide (default) | local
  if (!pathRouted()) p.set('locale', locale);   // in path mode the locale lives in the URL path instead
  const r = n => Math.round(n);
  p.set('cam', [r(camera.position.x), r(camera.position.y), r(camera.position.z),
                r(controls.target.x), r(controls.target.y), r(controls.target.z),
                world.rotation.y.toFixed(3)].join(','));
  return p.toString();
}

let syncTimer = null, restoring = false;
function syncUrl() {
  if (restoring) return;
  clearTimeout(syncTimer);
  syncTimer = setTimeout(() => history.replaceState(null, '', '?' + serializeState()), 200);
}

function applyState(p) {
  restoring = true;
  const g = id => document.getElementById(id);
  const fire = (el, ev) => el.dispatchEvent(new Event(ev));
  const setVal = (id, v, ev = 'change') => { const el = g(id); el.value = v; fire(el, ev); };
  const setChk = (id, on) => { const el = g(id); if (el && el.checked !== on) { el.checked = on; fire(el, 'change'); } };
  if (p.has('bg'))   setVal('bg', p.get('bg'));
  if (p.has('surf')) setVal('surf', p.get('surf'));
  if (p.has('ve'))   setVal('ve', p.get('ve'), 'input');
  if (p.has('oh'))   setVal('skinlift', p.get('oh'), 'input');
  if (p.has('d'))    setVal('meshdens', String(13 - parseInt(p.get('d'), 10)), 'change');
  if (p.has('ml'))   setChk('meshlines', p.get('ml') === '1');
  if (p.has('w'))    setChk('water', p.get('w') === '1');
  if (p.has('lb'))   setChk('labels', p.get('lb') === '1');
  if (p.has('lm'))   setChk('landmarks', p.get('lm') === '1');
  if (p.has('L')) {
    const on = new Set(p.get('L').split('.').filter(Boolean));
    for (const inp of document.querySelectorAll('#layers input')) setChk(inp.id, on.has(inp.id.slice(4)));
  }
  if (p.has('mc')) setWireColor('#' + p.get('mc'));
  if (p.has('sc')) setSolidColor('#' + p.get('sc'));
  if (p.has('tx')) { texRot = parseFloat(p.get('tx')) || 0; applyTexRot(); }   // topo raster rotation
  if (p.has('sp')) { spinDir = parseInt(p.get('sp'), 10); syncSpinSeg(); }
  if (p.has('ss')) setVal('spinspd', p.get('ss'), 'input');
  if (p.has('fo')) setChk('fog', p.get('fo') === '1');
  if (p.has('ra')) setChk('rain', p.get('ra') === '1');
  if (p.has('cl')) setChk('clouds', p.get('cl') === '1');
  if (p.has('li')) setChk('lightning', p.get('li') === '1');
  if (p.has('wv')) setChk('waves', p.get('wv') === '1');
  if (p.has('sn')) setChk('snow', p.get('sn') === '1');
  if (p.has('av')) setVal('sndvol', p.get('av'), 'input');
  if (p.get('mx') === '1') setMatrix(true);
  if (p.get('nn') === '1') setNeon(true);
  if (p.get('au') === '1')                       // autoplay policy: arm on first gesture
    addEventListener('pointerdown', () => setSound(true), { once: true });
  if (p.has('sd')) setVal('skydate', p.get('sd'));
  if (p.has('sm')) setVal('skytime', p.get('sm'), 'input');
  if (p.has('su') || p.has('sl')) {
    const on = p.get('su') !== '0', live = p.get('sl') !== '0';
    setVal('skymode', on ? (live ? 'live' : 'fixed') : 'off');
  }
  if (p.has('sk')) setVal('skyh', p.get('sk'), 'input');
  if (p.has('ti')) setVal('tide', p.get('ti'), 'input');
  if (p.has('tr')) setVal('thunderrate', p.get('tr'), 'input');
  if (p.has('wd')) setVal('winddir', p.get('wd'));       // direction before signal (badge quadrant)
  if (p.has('st')) setVal('storm', p.get('st'));         // applies the signal preset
  if (p.has('wi')) setVal('wind', p.get('wi'), 'input'); // then any custom wind override
  if (p.has('wm')) setChk('stationswind', p.get('wm') === '1');   // before stations so the filter is set when they load
  if (p.has('ws')) setChk('stations', p.get('ws') === '1');
  if (p.has('aq')) setChk('aqhi', p.get('aq') === '1');
  if (p.has('rdr')) radarRange = p.get('rdr') === '2' ? '256' : p.get('rdr') === '1' ? '128' : '064';   // radar range (HKS-74)
  if (p.get('sz') === '1') satZoom = 'x8M';                      // satellite zoom (HKS-79)
  if (p.get('wxv') === 's') wxMode = 'sat';                      // satellite view
  renderWxviewControls();
  if (radarRunning) startRadar();                                // live weather may have started it already
  if (p.has('cam')) {
    const c = p.get('cam').split(',').map(Number);
    if (c.length >= 6 && c.every(isFinite)) {
      camera.position.set(c[0], c[1], c[2]); controls.target.set(c[3], c[4], c[5]);
      if (c.length >= 7) world.rotation.y = c[6];
      controls.update();
    }
  }
  // HKS-91: restore a shared GPS location as a "you are here" pin (before the mode,
  // so Stargaze can spawn on it). Matrix/Neon were applied above via mx/nn.
  if (p.has('gps') && curG) {
    const [E, N] = p.get('gps').split(',').map(Number);
    if (isFinite(E) && isFinite(N)) { ensureGeoMarker(); geo.E = E; geo.N = N; geo.acc = Math.max(6, geo.acc); geo.has = true; refreshGpsBtn(); }
  }
  if (p.has('pl')) setVal('planeskin', p.get('pl'));       // HKS-93: aircraft skin — before md, so Fly spawns in it
  const md = p.get('md');                                  // HKS-91: restore the movement mode
  if (md === 'fly' && !flight.on) enterFlight();
  else if (md === 'walk' && !walk.on) enterWalk();
  else if (md === 'star' && !stargaze.on) {
    enterStargaze();
    if (p.has('sg')) {                                     // anchor the vantage + look from the shared sg (not the 1000m-forward cam target)
      const s = p.get('sg').split(',').map(Number);
      if (s.length >= 4 && s.every(isFinite)) {
        const b = bounds();
        stargaze.pos.x = Math.max(-b.halfX, Math.min(b.halfX, s[0]));
        stargaze.pos.z = Math.max(-b.halfZ, Math.min(b.halfZ, s[1]));
        stargaze.yaw = s[2]; stargaze.pitch = s[3];
      }
    }
  }
  restoring = false;
}

const shareUrl = () => location.origin + location.pathname + '?' + serializeState();

// ---- share sheet (HKS-92) --------------------------------------------------
// A share icon (panel header + brand chip) opens a custom icon-only sheet of
// services; one button drives the OS native share sheet where it exists. Icons
// carry the service name as aria-label/title only (no visible text).
const shareSheet = document.getElementById('sharesheet');
const ssStatus = document.getElementById('ss-status');
let ssFlashT = null;
function ssFlash(msg) { ssStatus.textContent = msg; clearTimeout(ssFlashT); ssFlashT = setTimeout(() => { ssStatus.textContent = ''; }, 1600); }
let ssReturnFocus = null;                                        // element to restore focus to on close (a11y)
function openShareSheet() {
  history.replaceState(null, '', '?' + serializeState());       // address bar == exactly what we share (incl. live GPS)
  document.getElementById('embedcode').hidden = true;
  ssStatus.textContent = '';
  document.getElementById('ss-native').hidden = !navigator.share;   // native button only where the OS sheet exists
  ssReturnFocus = document.activeElement;
  shareSheet.hidden = false;
  document.getElementById('ss-close').focus();                  // move focus into the dialog (CodeRabbit)
  track('share_open');
}
function closeShareSheet() {
  shareSheet.hidden = true;
  if (ssReturnFocus && ssReturnFocus.focus) ssReturnFocus.focus();   // restore focus to the trigger
  ssReturnFocus = null;
}
document.getElementById('share-hdr').addEventListener('click', e => { e.stopPropagation(); openShareSheet(); });
document.getElementById('share-brand').addEventListener('click', e => { e.stopPropagation(); openShareSheet(); });
document.getElementById('ss-close').addEventListener('click', closeShareSheet);
shareSheet.querySelector('.ss-backdrop').addEventListener('click', closeShareSheet);
addEventListener('keydown', e => {                               // Esc closes; Tab is trapped inside the dialog (CodeRabbit)
  if (shareSheet.hidden) return;
  if (e.key === 'Escape') { closeShareSheet(); return; }
  if (e.key === 'Tab') {
    const f = [...shareSheet.querySelectorAll('button')].filter(b => !b.hidden && b.offsetParent !== null);
    if (!f.length) return;
    const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }
});

document.getElementById('ss-native').addEventListener('click', () => {
  if (!navigator.share) return;
  track('share_action', { channel: 'native' });
  navigator.share({ title: t('share.title'), text: t('share.text'), url: shareUrl() }).then(closeShareSheet).catch(() => {});
});
function shareLink(target) {
  const url = shareUrl(), text = t('share.text'), e = encodeURIComponent;
  const links = {
    wa: `https://wa.me/?text=${e(text + ' ' + url)}`,
    x:  `https://twitter.com/intent/tweet?text=${e(text)}&url=${e(url)}`,
    th: `https://www.threads.net/intent/post?text=${e(text + ' ' + url)}`,
  };
  if (links[target]) window.open(links[target], '_blank', 'noopener,noreferrer');
}
document.getElementById('ss-wa').addEventListener('click', () => { track('share_action', { channel: 'whatsapp' }); shareLink('wa'); });
document.getElementById('ss-x').addEventListener('click', () => { track('share_action', { channel: 'x' }); shareLink('x'); });
document.getElementById('ss-th').addEventListener('click', () => { track('share_action', { channel: 'threads' }); shareLink('th'); });
document.getElementById('ss-copy').addEventListener('click', async () => {
  track('share_action', { channel: 'copy' });
  try { await navigator.clipboard.writeText(shareUrl()); ssFlash(t('share.copied')); }
  catch (_) { history.replaceState(null, '', '?' + serializeState()); ssFlash(t('share.inbar')); }   // honest: clipboard failed, URL is in the bar (CodeRabbit)
});
// ---- embed (HKS-27): copy-paste <iframe> snippet ---------------------------
// The embed URL carries the current view plus embed=1, which boots map-forward.
function embedSnippet() {
  const url = shareUrl() + (shareUrl().includes('?') ? '&' : '?') + 'embed=1';
  return `<iframe src="${url}" width="800" height="600" style="border:0;border-radius:12px" `
    + `loading="lazy" allow="fullscreen" allowfullscreen title="Hong Kong Sandbox · 香港沙盒"></iframe>`;
}
document.getElementById('ss-embed').addEventListener('click', async () => {
  track('share_action', { channel: 'embed' });
  const ta = document.getElementById('embedcode');
  ta.value = embedSnippet(); ta.hidden = false; ta.focus(); ta.select();
  try { await navigator.clipboard.writeText(ta.value); ssFlash(t('share.embedcopied')); }
  catch (_) { ssFlash(t('share.embed')); }
});

// ---- locale routing + toggle ----------------------------------------------
function pathLocale() { const seg = location.pathname.split('/')[1]; return LOCALES.includes(seg) ? seg : null; }
function pathRouted() { return pathLocale() !== null; }
function detectLocale() {
  const fromPath = pathLocale(); if (fromPath) return fromPath;                 // /en-hk/ (CF Function route)
  const q = new URLSearchParams(location.search).get('locale'); if (LOCALES.includes(q)) return q;
  try { const s = localStorage.getItem('locale'); if (LOCALES.includes(s)) return s; } catch (_) {}
  for (const p of (navigator.languages || [navigator.language || ''])) {        // browser preference
    const l = p.toLowerCase(); if (LOCALES.includes(l)) return l;
    const m = LOCALES.find(x => x.split('-')[0] === l.split('-')[0]); if (m) return m;
  }
  return DEFAULT_LOCALE;
}
function applyLocale(loc) {
  locale = LOCALES.includes(loc) ? loc : DEFAULT_LOCALE;
  document.documentElement.lang = isZh() ? 'zh-HK' : 'en';
  document.title = t('doc.title');
  const canon = document.getElementById('canonical'); if (canon) canon.href = location.origin + location.pathname;
  // keep social-share meta (HKS-28) in sync with the active locale
  const setMeta = (id, v) => { const el = document.getElementById(id); if (el) el.setAttribute('content', v); };
  setMeta('og-title', t('doc.title')); setMeta('tw-title', t('doc.title'));
  setMeta('og-desc', t('meta.desc'));  setMeta('tw-desc', t('meta.desc'));
  setMeta('og-url', location.origin + location.pathname);
  setMeta('og-locale', isZh() ? 'zh_HK' : 'en_HK');
  setMeta('og-locale-alt', isZh() ? 'en_HK' : 'zh_HK');
  document.body.dataset.locale = locale;
  for (const el of document.querySelectorAll('[data-i18n]'))       el.textContent = t(el.getAttribute('data-i18n'));
  for (const el of document.querySelectorAll('[data-i18n-title]')) el.title = t(el.getAttribute('data-i18n-title'));
  for (const el of document.querySelectorAll('[data-i18n-aria-label]')) el.setAttribute('aria-label', t(el.getAttribute('data-i18n-aria-label')));
  for (const el of document.querySelectorAll('[data-i18n-html]'))  el.innerHTML = t(el.getAttribute('data-i18n-html'));
  const ob = document.getElementById('offbar');   // HKS-109: keep the offline banner in-language on an in-place switch
  if (ob && !ob.hidden) { ob.querySelector('.offbar-msg').textContent = t('off.banner'); requestAnimationFrame(layoutOffbar); }
  try { localStorage.setItem('locale', locale); } catch (_) {}
  const lb = document.getElementById('langbtn'); if (lb) lb.textContent = isZh() ? 'EN' : '中';
  renderWxviewControls();   // radar/satellite labels are set in JS, refresh them for the new locale
  const md = document.getElementById('meshdensv'); if (md) md.textContent = meshStep === 1 ? t('dens.full') : '÷' + meshStep;
  if (gridW) updateNote();
  updateStormBadge(); applyControlLocks();
  const btn = document.getElementById('livebtn'); if (btn) btn.textContent = liveMode ? t('live.on') : t('live.sync');
  updateViewBtn();   // chase/cockpit label follows the locale
  updateWalkViewBtn();
  if (typeof updateHelp === 'function') updateHelp();     // Help section bodies follow the locale (HKS-86)
  if (typeof renderSide === 'function') renderSide();     // drawer title + tab state follow the locale
  refreshGpsBtn();   // GPS button label/icon follows the locale + state (HKS-86)
  if (stargaze.on) syncSgTray();   // stargaze tray hint/pills follow too
  if (liveMode) { syncLiveWeather(); syncLiveTide(); }
  if (stationsOn) refreshStations();
}
function switchLocale(loc) {
  if (!LOCALES.includes(loc) || loc === locale) return;
  track('language', { to: loc === 'zh-hk' ? 'zh' : 'en' });   // before any navigation (prod path-routes away)
  try { localStorage.setItem('locale', loc); } catch (_) {}
  if (pathRouted()) {                       // prod: navigate to /<loc>/… (CF Function stamps the cookie)
    const rest = location.pathname.split('/').slice(2).join('/');
    location.href = `/${loc}/${rest}${location.search}${location.hash}`;
  } else {                                  // dev / query mode: switch in place
    const p = new URLSearchParams(location.search); p.set('locale', loc);
    history.replaceState(null, '', location.pathname + '?' + p.toString() + location.hash);
    applyLocale(loc);
  }
}
document.getElementById('langbtn').addEventListener('click', () => switchLocale(isZh() ? 'en-hk' : 'zh-hk'));

// ---- analytics (HKS-102): provider-agnostic custom events -------------------
// Every instrumented control calls track()/trackDebounced() — never window.va or
// gtag directly. The library attaches locale/mode/theme/device centrally, gates out
// embed mode + programmatic URL-state restore, and fans out to each enabled sink.
// VercelSink ships now; GA4Sink is registered too but opts itself out until a
// measurement ID exists (set window.__GA4_ID, or pass one here — no call-site edits).
const ANALYTICS_EMBED = new URLSearchParams(location.search).get('embed') === '1';
const ANALYTICS_TOUCH = matchMedia('(pointer: coarse)').matches;
function analyticsMode() { return flight.on ? 'fly' : walk.on ? 'walk' : stargaze.on ? 'stargaze' : 'orbit'; }
function windBucket() {
  const w = windStrength;
  return w <= 0 ? 'calm' : w < 0.25 ? 'light' : w < 0.5 ? 'moderate' : w < 0.75 ? 'strong' : 'severe';
}
initAnalytics({
  enabled: !ANALYTICS_EMBED,                       // embeds are excluded entirely
  debug: new URLSearchParams(location.search).has('adebug'),
  isRestoring: () => restoring,                    // never count applyState()'s synthetic sets
  baseProps: () => ({
    locale: isZh() ? 'zh' : 'en',                  // language segment (en / zh-HK)
    mode: analyticsMode(),                         // orbit | fly | walk | stargaze
    theme: bgMode,                                 // dark | paper
    device: ANALYTICS_TOUCH ? 'touch' : 'pointer',
  }),
  sinks: [VercelSink(), GA4Sink({ measurementId: window.__GA4_ID || '' })],
});

resize();
applyBg('dark');
locale = detectLocale();
applyLocale(locale);
// Curated default view: a bare visit boots into this scene. Any shared/deep link
// that carries a recognised viewer-state key is honoured verbatim and wins.
// "State" is decided by the canonical key set below — NOT "any unknown key" — so a
// marketing/tracking link (?utm_source=…, ?fbclid=…), a lang-only or embed-only URL
// still lands on the curated default, with its own extra params carried through.
const DEFAULT_STATE = 's=hk-landsd-5m&surf=shaded&bg=dark&ve=2.8&oh=1&d=1&ml=0&w=1&lb=0&lm=1&L=road&mc=2a4c33&sc=262626&sp=1&ss=0.2&fo=0&ra=0&cl=1&li=0&wv=1&sn=0&mx=0&nn=0&au=0&av=60&su=1&sl=1&sk=1&ti=50&tr=0&st=0&wi=0&wd=N&lv=1&ws=0&wm=0&aq=0&rdr=0&cam=-35853,34284,-26934,0,933,0,1.715';
const urlParams = new URLSearchParams(location.search);
// Always start from the curated default and overlay whatever the URL carries. A full
// shared link sets every core key so it overrides the default entirely; a partial link
// (e.g. ?pl=cx747 or ?md=star) inherits the default camera/weather/layers instead of
// falling back to raw HTML defaults. Non-state keys (locale/embed/utm) ride along too. (codex P2)
const startParams = new URLSearchParams(DEFAULT_STATE);
for (const [k, v] of urlParams) startParams.set(k, v);
const startSrc = SOURCES[startParams.get('s')] ? startParams.get('s') : 'hk-landsd-5m';
document.getElementById('src').value = startSrc;
loadSource(startSrc).then(() => {
  applyState(startParams);
  controls.addEventListener('change', syncUrl);     // camera orbit/zoom/pan
  const panel = document.getElementById('panel');
  panel.addEventListener('change', syncUrl);         // selects + checkboxes
  panel.addEventListener('input', syncUrl);          // sliders + colour
  syncUrl();
  // embed mode (HKS-27): boot map-forward with the panel collapsed to the gear;
  // the scene fills the iframe and the controls are one tap away.
  if (startParams.get('embed') === '1') document.getElementById('panel').classList.add('collapsed');
  animate();
  // default to live weather on (unless a shared link explicitly opted out with lv=0,
  // or we booted straight into Stargaze — which owns a clean, weather-free sky, HKS-91).
  // Offline (HKS-109): skip the doomed HKO fetches and start manual, then arm live
  // once the moment the connection returns.
  const wantLive = !stargaze.on && (startParams.has('lv') ? startParams.get('lv') === '1' : true);
  if (wantLive && navigator.onLine) setLiveMode(true);
  else if (wantLive) addEventListener('online', () => { if (!liveMode && !stargaze.on) setLiveMode(true); }, { once: true });
  const ld = document.getElementById('loader');           // terrain is in: fade the boot screen
  if (ld) { ld.classList.add('done'); setTimeout(() => ld.remove(), 700); }
  window.__hkLoaded = true; dispatchEvent(new Event('hk:loaded'));   // boot screen done → arm post-load UI (coach-mark)
  sessionStorage.removeItem('hks-boot-retry');   // HKS-109: clean boot → reset the auto-retry cap
  if (!navigator.onLine) setOffbar(true);   // HKS-109: booted from cache while offline → flag the disabled live features
  // HKS-102: boot + URL-state restore are done — arm analytics and log the session.
  // "shared" = the visited URL carried a recognised viewer-state key (a deep/share
  // link), so we can tell organic visits from shared ones.
  const SHARE_KEYS = new Set([...new URLSearchParams(DEFAULT_STATE).keys(), 'md', 'pl', 'gps', 'sg', 'mx', 'nn']);
  const shared = [...urlParams.keys()].some(k => SHARE_KEYS.has(k));
  armAnalytics();
  track('app_load', {
    shared,
    embed: ANALYTICS_EMBED,
    start_mode: startParams.get('md') || 'orbit',
    start_skin: startParams.get('pl') || 'prop',
    surface: startParams.get('surf') || surfStyle,
    source: startSrc,
  });
}).catch(err => {
  // HKS-109: terrain never loaded (usually offline + not-yet-cached). Don't leave
  // the spinner running behind a raw error — say what's wrong and offer a retry.
  console.error('boot: terrain load failed', err);
  // HKS-109: navigator.onLine lies (can be true on a dead link / captive portal), so
  // also treat a classic fetch network failure as offline. Our own AbortError (the fj
  // timeout) is a hang while nominally online, not an offline state.
  const netMsg = (err && (err.message || String(err))) || '';
  const offline = !navigator.onLine
    || (err?.name !== 'AbortError' && /failed to fetch|networkerror|load failed/i.test(netMsg));
  const msg = offline ? t('load.offline') : t('load.failed');
  document.getElementById('note').textContent = msg;
  const ld = document.getElementById('loader');
  if (ld) {
    ld.classList.add('err');   // CSS hides the spinner (#loader.err .ring) + bar
    const ls = document.getElementById('loaderstatus');
    if (ls && !ls.querySelector('button')) {
      ls.textContent = msg;
      const btn = document.createElement('button');
      btn.textContent = t('load.retry');
      btn.style.cssText = 'display:block;margin:16px auto 0;padding:7px 18px;font:inherit;font-size:12px;letter-spacing:.04em;cursor:pointer;border-radius:9px;border:1px solid currentColor;background:transparent;color:inherit';
      btn.onclick = () => location.reload();
      ls.appendChild(btn);
    }
    // reconnected while the error screen is up → retry the boot automatically, but
    // cap it (sessionStorage, survives reloads) so an offline↔online flap can't
    // thrash-reload; after the cap the Retry button still works. Debounced + re-checks
    // navigator.onLine to ignore spurious events.
    const onBack = () => {
      removeEventListener('online', onBack);
      if (!navigator.onLine) return;
      const tries = +(sessionStorage.getItem('hks-boot-retry') || 0);
      if (tries >= 2) return;
      sessionStorage.setItem('hks-boot-retry', tries + 1);
      setTimeout(() => location.reload(), 400);
    };
    addEventListener('online', onBack);
  }
});

// ---- HKS-109: offline alert bar (fixed, full-width, top edge) ----------------
// A deliberately loud red bar listing what's disabled while offline. It marquee-
// scrolls if the message overflows the viewport, wraps (no motion) under reduced-
// motion, and hides the instant the connection returns. A cold-offline boot is
// handled by the loader screen; this covers going — or booting from cache — offline
// with the app already usable.
function layoutOffbar() {
  const bar = document.getElementById('offbar');
  if (!bar || bar.hidden) return;
  const track = bar.querySelector('.offbar-track');
  const msg = bar.querySelector('.offbar-msg');
  bar.classList.remove('scroll', 'wrap');
  while (track.children.length > 1) track.removeChild(track.lastChild);   // drop any marquee clone
  const msgW = msg.getBoundingClientRect().width;                         // inline <span> scrollWidth is unreliable
  if (msgW <= bar.clientWidth + 2) return;                                // fits → static, centred
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) { bar.classList.add('wrap'); return; }
  const clone = msg.cloneNode(true); clone.setAttribute('aria-hidden', 'true');   // 2nd copy → seamless loop; hide from SR
  track.appendChild(clone);
  bar.style.setProperty('--offdur', Math.max(8, Math.round(msgW / 55)) + 's');   // ~55 px/s
  bar.classList.add('scroll');
}
function setOffbar(on) {
  const bar = document.getElementById('offbar');
  if (!bar) return;
  if (on) {
    bar.querySelector('.offbar-msg').textContent = t('off.banner');
    bar.hidden = false;
    requestAnimationFrame(() => {
      layoutOffbar();                                   // measure after the browser lays it out
      document.documentElement.style.setProperty('--offbar-h', bar.offsetHeight + 'px');
      document.body.classList.add('has-offbar');        // engage the top-UI offset
    });
  } else {
    bar.hidden = true;
    bar.classList.remove('scroll', 'wrap');
    bar.style.removeProperty('--offdur');
    document.body.classList.remove('has-offbar');
    document.documentElement.style.removeProperty('--offbar-h');
  }
}
addEventListener('offline', () => setOffbar(true));
addEventListener('online', () => setOffbar(false));
addEventListener('resize', layoutOffbar);

// ---- PWA: register the offline service worker (HKS-29) ----------------------
// Static app, so this only adds offline resilience + installability; failure is
// non-fatal (e.g. unsupported browser, or opened over file://).
if ('serviceWorker' in navigator) {
  const registerSW = () => navigator.serviceWorker.register('/sw.js')
    .catch(err => console.warn('service worker registration failed', err));
  if (document.readyState === 'complete') registerSW();
  else addEventListener('load', registerSW);
}

// ---- PWA install nudge (HKS-64): mobile "add to home screen" reminder --------
// The SW + installability already work without this; it's just a dismissable
// nudge. Android/Chromium uses the native beforeinstallprompt event; iOS Safari
// (which has no such API) gets manual Share → Add to Home Screen instructions.
// Never shown on desktop, when already installed (standalone), or if dismissed
// within the re-show window.
(() => {
  const bar = document.getElementById('installbar');
  if (!bar) return;
  const KEY = 'hks-install-dismissed', RESHOW_DAYS = 21;
  // the dismissal is remembered on PRODUCTION only — on previews/localhost we
  // ignore any stored key so the bar always shows fresh for testing (HKS-64)
  const isProd = location.hostname === 'hongkong-sandbox.wiiiimm.codes';
  // launched from the installed home-screen icon → runs standalone → never nudge
  const standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone === true;
  // touch devices only (mobile / iPad, incl. iPadOS masquerading as desktop)
  const touch = matchMedia('(pointer:coarse)').matches || navigator.maxTouchPoints > 0;
  if (standalone || !touch) return;                        // desktop (no touch) / already installed → never
  if (isProd) {
    const last = +localStorage.getItem(KEY) || 0;
    if (last && Date.now() - last < RESHOW_DAYS * 864e5) return;   // dismissed recently → don't nag
  }

  const ua = navigator.userAgent;
  const isIOS = /iP(hone|od|ad)/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const isSafari = /safari/i.test(ua) && !/(chrome|crios|fxios|edg|android)/i.test(ua);

  const dismiss = () => { bar.classList.remove('show'); if (isProd) localStorage.setItem(KEY, String(Date.now())); };
  document.getElementById('ib-close').addEventListener('click', dismiss);
  const platform = (isIOS && isSafari) ? 'ios' : 'android';
  let shownOnce = false;
  const show = () => { bar.classList.add('show'); if (!shownOnce) { shownOnce = true; track('install_prompt_shown', { platform }); } };

  let deferred = null;
  if (isIOS && isSafari) {
    bar.classList.add('ios');                              // manual instructions, no button
    setTimeout(show, 15000);                               // after a little engagement, not on first paint
  } else {
    addEventListener('beforeinstallprompt', (e) => {       // Chromium fires this only when installable
      e.preventDefault(); deferred = e;                    // stash it for our own button
      bar.classList.add('android');
      setTimeout(show, 8000);
    });
    document.getElementById('ib-install').addEventListener('click', async () => {
      if (!deferred) return;
      deferred.prompt();
      const choice = await deferred.userChoice.catch(() => null);
      if (choice && choice.outcome) track('install_result', { outcome: choice.outcome });
      deferred = null; dismiss();
    });
  }
  addEventListener('appinstalled', dismiss);               // installed → stop nudging
})();

// HKS-86: UI chrome (panel, drawer, dock/tray/compass, GPS, corner buttons,
// weather/radar, coach, install bar, brand chip) must not leak pointer/touch/click
// events to the document/window viewport handlers (hold-to-gas, take-off, etc.).
// Stop them bubbling — the canvas keeps its own listeners either way.
for (const el of document.querySelectorAll('#panel,#sidedrawer,#dockwrap,#locateui,#cornerui,#wxhud,#radarhud,#coachtip,#installbar,#brandchip,#stormbadge,#miniloader,#sharesheet'))
  for (const ev of ['pointerdown', 'pointerup', 'touchstart', 'touchend', 'click'])
    el.addEventListener(ev, e => e.stopPropagation());

// ---- first-visit coach-mark (HKS-86): a blue halo on the dock ⚙ nudging new
// visitors to open the settings. Shown once; the dismissal is stored on
// production only (previews always re-show for testing), like the install nudge.
(() => {
  const gear = document.getElementById('dockgear'), tip = document.getElementById('coachtip');
  if (!gear || !tip) return;
  if (startParams.get('embed') === '1') return;            // no chrome nudges inside embeds
  const KEY = 'hks-coach-dismissed';
  const isProd = location.hostname === 'hongkong-sandbox.wiiiimm.codes';
  if (isProd) { try { if (localStorage.getItem(KEY)) return; } catch (_) {} }
  const arrow = tip.querySelector('.ct-arrow');
  let shown = false;
  const place = () => {                                     // park the bubble above the ⚙, arrow pointing at it
    const g = gear.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
    const left = Math.max(10, Math.min(g.left + g.width / 2 - tw / 2, innerWidth - tw - 10));
    tip.style.left = left + 'px';
    tip.style.top = (g.top - th - 12) + 'px';
    arrow.style.left = (g.left + g.width / 2 - left - 6) + 'px';
  };
  const dismiss = () => {
    if (!shown) return;
    shown = false;
    track('coach_dismiss');
    gear.classList.remove('coach');
    tip.classList.remove('show');
    setTimeout(() => { tip.style.display = 'none'; }, 220);
    removeEventListener('resize', place);
    if (isProd) { try { localStorage.setItem(KEY, '1'); } catch (_) {} }   // remember the dismissal (prod only)
  };
  const show = () => {
    if (shown || !panelEl.classList.contains('collapsed')) return;   // panel already open → they found it
    shown = true;
    gear.classList.add('coach');
    tip.style.display = 'block';
    place();
    requestAnimationFrame(() => tip.classList.add('show'));
    addEventListener('resize', place);
  };
  document.getElementById('coach-ok').addEventListener('click', dismiss);
  gear.addEventListener('click', dismiss);                 // tapped the ⚙ (which opens the panel) → done
  const armCoach = () => setTimeout(show, 5000);           // 5s after the boot screen finishes
  if (window.__hkLoaded) armCoach();                       // load already done → start the 5s timer now
  else addEventListener('hk:loaded', armCoach, { once: true });
})();

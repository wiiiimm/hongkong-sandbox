// Hong Kong / Lantau layered 3D terrain viewer.
// Base terrain = Claude's smooth external DEM meshes; skin = draped vector layers.
// Best-of-both: shaded / elevation / matte / bare-wireframe / raster surface styles,
// per-layer vector toggles, and a vertical-exaggeration slider that drives BOTH the
// terrain and the draped skin so contours stay welded to the ridges.
import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { createGlass } from './vendor/glass-gl.js';
import { sunPosition, sunTimes, moonPosition, moonTimes, moonIllumination, starPosition, compassDeg } from './vendor/astro.js';
import { setEnabled as setAudioEnabled, setMasterVolume, setWeatherMix, thunder, setEngine, audioSupported } from './audio.js';

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
    'grp.overlays': 'Overlays · stack on top', 'ov.water': 'Water', 'ov.landmarks': 'Landmarks', 'ov.labels': 'Peaks', 'ov.stations': 'Stations (live)', 'ov.aqhi': 'Air · AQHI (live)', 'ov.stationswind': '+ wind/marine stns',
    'radar.title': 'Rain radar', 'radar.credit': '© Hong Kong Observatory',
    'sat.title': 'Satellite', 'sat.wide': 'Wide', 'sat.local': 'Local', 'rf.bigger': 'Enlarge radar', 'rf.smaller': 'Restore radar size',
    'lyr.contour': 'Contours', 'lyr.road': 'Roads', 'lyr.trail': 'Trails', 'lyr.hydro': 'Hydro', 'lyr.coast': 'Coast', 'lyr.boundary': 'Boundaries', 'lyr.cliff': 'Cliffs',
    'grp.spin': 'Auto‑spin (horizontal)', 'lbl.direction': 'Direction', 'spin.off': 'Off', 'spin.cw': '⟳ Clockwise', 'spin.ccw': '⟲ Counter‑cw', 'lbl.speed': 'Speed',
    'grp.sky': 'Sun & moon', 'lbl.skymode': 'Sky', 'sky.live': 'Live (HKT)', 'sky.fixed': 'Custom time', 'sky.off': 'Off · studio light', 'lbl.date': 'Date', 'lbl.time': 'Time',
    'grp.weather': 'Weather', 'lbl.sound': 'Sound', 'wx.rain': 'Rain', 'wx.clouds': 'Clouds', 'wx.fog': 'Fog', 'wx.thunder': 'Thunder', 'wx.waves': 'Waves', 'wx.snow': 'Snow',
    'lbl.skyheight': 'Sky height ×',
    'lbl.thunderrate': 'Thunder rate', 'lbl.tide': 'Tide', 'lbl.storm': 'Storm signal', 'storm.0': 'None', 'storm.1': 'T1 · Standby', 'storm.3': 'T3 · Strong wind',
    'storm.8': 'T8 · Gale / Storm', 'storm.9': 'T9 · Incr. gale', 'storm.10': 'T10 · Hurricane', 'lbl.wind': 'Wind', 'lbl.windfrom': 'Wind from',
    'btn.reset': 'Reset', 'btn.south': 'South', 'btn.top': 'Top‑down', 'btn.copylink': 'Copy link', 'btn.fly': '✈ Fly',
    'btn.share': 'Share', 'share.title': 'Share this view', 'share.text': 'Hong Kong Sandbox — an interactive 3D Hong Kong, live weather & typhoon sim', 'share.copied': 'Copied!', 'share.embed': 'Embed', 'share.embedcopied': 'Embed code copied!',
    'fly.help': '↑↓ pitch · ←→ bank · ⇧/⌃ throttle · ␣ gas · drag to look · C cockpit · Esc exit',
    'fly.touch': 'tilt to steer · hold for gas · drag to look',
    'fly.view': 'view', 'fly.exit': 'exit',
    'fly.landed': 'landed', 'fly.takeoff': '🛫 take off — ␣ or tap',
    'fly.chase': '🎥 Chase', 'fly.cockpit': '🧑‍✈️ Cockpit',
    'lbl.topspeed': 'Top speed',
    'btn.walk': '🪂 Walk',
    'btn.matrix': '🕴 Matrix', 'btn.neon': '❄️ Neon Night',
    // HKS-86: the bottom mode dock + contextual tray
    'dock.orbit': 'Orbit', 'dock.fly': 'Fly', 'dock.walk': 'Walk', 'dock.star': 'Stargaze',
    'dock.matrix': 'Matrix', 'dock.neon': '風林火山', 'dock.settings': 'Settings',
    'tray.end': 'End', 'grp.move': 'Fly & walk',
    'sg.live': '● Live sky', 'sg.custom': '🕐 Custom',
    'sg.orient': '🧭 Point at the sky', 'sg.follow': '📍 Follow me',
    'sg.hint': 'drag to look · tap a constellation',
    'walk.help': 'WASD/↑↓←→ move · mouse look · ⇧ boost · ␣ jump · C view · Esc exit',
    'walk.touch': 'hold to walk · 2-finger hold to run · drag to look', 'walk.jog': 'boosting', 'walk.dist': 'walked',
    'walk.fp': '👁 POV', 'walk.chase': '🎥 Chase',
    'help.tab': 'Help', 'help.title': 'Help & controls',
    'help.src': 'Modes live in the bottom bar · themes toggle in any mode',
    'help.orbit.t': 'Map view', 'help.orbit.b': 'Drag to rotate\nScroll or pinch to zoom\nRight‑drag or two‑finger to pan\nReset recenters the view',
    'help.fly.t': 'Flying', 'help.fly.b': 'Hold to accelerate — Space, or press & hold\nDrag to look around\nPress C for chase / cockpit\nLand anywhere (even water), then take off again',
    'help.walk.t': 'On foot', 'help.walk.b': 'Move with the keys, or the on‑screen ▶\nSpace to jump\nShift or a two‑finger hold to run\nDrag to look around\nPress C for first‑person / chase',
    'help.star.t': 'Stargazing', 'help.star.b': 'Drag to look around the sky\nTap a star to trace its constellation\n🧭 Point at the sky — aim with your phone\n📍 Follow me — track your GPS position\nDrag the time slider to move the sky',
    'help.gen.t': 'Getting around', 'help.gen.b': 'Pick a mode in the bottom bar — Orbit, Fly, Walk, Stargaze\nMatrix & 風林火山 are looks you can turn on in any mode\nKeys — M / N looks · C camera · Esc leaves a mode\n⚙ opens settings',
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
      + '<p>Infrastructure by <a href="https://stealth-company.co" target="_blank" rel="noopener">stealth.co</a>.</p>'
      + '© 2026 wiiiimm',
    'live.sync': '⛅ Sync live weather', 'live.on': '⛅ Live weather · ON',
    'lock.live': '◈ set by live weather — turn off sync below to adjust',
    'lock.storm': '◈ set by the storm signal — choose None to adjust',
    'lock.sky': '◈ following live weather — turn off sync to adjust',
    'lock.matrix': '◈ set by Matrix mode — 🕴 to wake up',
    'lock.neon': '◈ set by 風林火山 mode — ❄️ to leave the neon night',
    'note.mesh': 'mesh', 'note.verts': 'verts', 'note.peak': 'peak', 'note.m': 'm', 'note.loading': 'Loading', 'note.layers': 'Loading map layers', 'note.loadfail': 'Load failed',
    'install.ios': 'Add Hong Kong Sandbox to your home screen — tap Share, then "Add to Home Screen".', 'install.android': 'Install Hong Kong Sandbox — a full-screen, offline-ready app.', 'install.action': 'Install',
    'load.osm': 'street map', 'load.sat': 'satellite imagery', 'load.mapfail': 'Map load failed', 'dens.full': 'full',
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
    'grp.overlays': '疊加圖層', 'ov.water': '海水', 'ov.landmarks': '地標', 'ov.labels': '山峰', 'ov.stations': '氣象站（即時）', 'ov.aqhi': '空氣質素（即時）', 'ov.stationswind': '＋風／海事站',
    'radar.title': '雨區雷達', 'radar.credit': '© 香港天文台',
    'sat.title': '衛星', 'sat.wide': '廣域', 'sat.local': '本地', 'rf.bigger': '放大雷達', 'rf.smaller': '還原雷達大小',
    'lyr.contour': '等高線', 'lyr.road': '道路', 'lyr.trail': '山徑', 'lyr.hydro': '水系', 'lyr.coast': '海岸線', 'lyr.boundary': '界線', 'lyr.cliff': '懸崖',
    'grp.spin': '自動旋轉（水平）', 'lbl.direction': '方向', 'spin.off': '關閉', 'spin.cw': '⟳ 順時針', 'spin.ccw': '⟲ 逆時針', 'lbl.speed': '速度',
    'grp.sky': '日與月', 'lbl.skymode': '天空', 'sky.live': '即時（香港時間）', 'sky.fixed': '自訂時間', 'sky.off': '關閉 · 固定光', 'lbl.date': '日期', 'lbl.time': '時間',
    'grp.weather': '天氣', 'lbl.sound': '音效', 'wx.rain': '雨', 'wx.clouds': '雲', 'wx.fog': '霧', 'wx.thunder': '雷暴', 'wx.waves': '波浪', 'wx.snow': '雪',
    'lbl.skyheight': '天空高度 ×',
    'lbl.thunderrate': '雷暴頻率', 'lbl.tide': '潮汐', 'lbl.storm': '風暴信號', 'storm.0': '無', 'storm.1': '一號 · 戒備', 'storm.3': '三號 · 強風',
    'storm.8': '八號 · 烈風/暴風', 'storm.9': '九號 · 烈風增強', 'storm.10': '十號 · 颶風', 'lbl.wind': '風力', 'lbl.windfrom': '風向來自',
    'btn.reset': '重設', 'btn.south': '南面', 'btn.top': '俯視', 'btn.copylink': '複製連結', 'btn.fly': '✈ 飛行',
    'btn.share': '分享', 'share.title': '分享此畫面', 'share.text': '香港沙盒 — 互動 3D 香港，實時天氣與颱風模擬', 'share.copied': '已複製！', 'share.embed': '嵌入', 'share.embedcopied': '已複製嵌入碼！',
    'fly.help': '↑↓ 俯仰 · ←→ 轉向 · ⇧/⌃ 油門 · ␣ 加速 · 拖曳環視 · C 駕駛艙 · Esc 離開',
    'fly.touch': '傾斜轉向 · 按住加速 · 拖曳環視',
    'fly.view': '視角', 'fly.exit': '離開',
    'fly.landed': '已降落', 'fly.takeoff': '🛫 起飛 — ␣ 或點擊',
    'fly.chase': '🎥 追機', 'fly.cockpit': '🧑‍✈️ 駕駛艙',
    'lbl.topspeed': '極速',
    'btn.walk': '🪂 步行',
    'btn.matrix': '🕴 Matrix', 'btn.neon': '❄️ 風林火山',
    // HKS-86: the bottom mode dock + contextual tray
    'dock.orbit': '環繞', 'dock.fly': '飛行', 'dock.walk': '步行', 'dock.star': '觀星',
    'dock.matrix': 'Matrix', 'dock.neon': '風林火山', 'dock.settings': '設定',
    'tray.end': '結束', 'grp.move': '飛行與步行',
    'sg.live': '● 即時星空', 'sg.custom': '🕐 自訂',
    'sg.orient': '🧭 指向天空', 'sg.follow': '📍 跟隨我',
    'sg.hint': '拖曳環視 · 點選星座',
    'walk.help': 'WASD/↑↓←→ 移動 · 滑鼠視角 · ⇧ 加速 · ␣ 跳 · C 視角 · Esc 離開',
    'walk.touch': '按住行走 · 雙指快跑 · 拖動視角', 'walk.jog': '加速中', 'walk.dist': '已行',
    'walk.fp': '👁 主視角', 'walk.chase': '🎥 跟隨',
    'help.tab': '說明', 'help.title': '操作說明',
    'help.src': '模式在底部工具列 · 風格可於任何模式切換',
    'help.orbit.t': '地圖檢視', 'help.orbit.b': '拖曳旋轉\n滾輪或雙指縮放\n右鍵拖曳或雙指平移\n重設可重新置中',
    'help.fly.t': '飛行', 'help.fly.b': '按住加速 — 空白鍵，或長按畫面\n拖曳環顧四周\n按 C 切換追尾 / 座艙視角\n可降落任何地方（連水面），再起飛',
    'help.walk.t': '步行', 'help.walk.b': '用按鍵或畫面上的 ▶ 移動\n空白鍵跳躍\nShift 或雙指按住奔跑\n拖曳環顧四周\n按 C 切換第一人稱 / 追尾',
    'help.star.t': '觀星', 'help.star.b': '拖曳環顧夜空\n點選星星顯示所屬星座\n🧭 對準天空 — 用手機方向瞄準\n📍 跟隨我 — 追蹤你的 GPS 位置\n拖動時間軸移動星空',
    'help.gen.t': '基本操作', 'help.gen.b': '在底部工具列選擇模式 — 環繞、飛行、步行、觀星\nMatrix 與 風林火山 是可於任何模式開啟的風格\n按鍵 — M / N 風格 · C 鏡頭 · Esc 離開模式\n⚙ 開啟設定',
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
      + '<p>基礎設施由 <a href="https://stealth-company.co" target="_blank" rel="noopener">stealth.co</a> 提供。</p>'
      + '© 2026 wiiiimm',
    'live.sync': '⛅ 同步即時天氣', 'live.on': '⛅ 即時天氣 · 開啟',
    'lock.live': '◈ 由即時天氣設定 — 關閉下方同步即可調整',
    'lock.storm': '◈ 由風暴信號設定 — 選「無」即可調整',
    'lock.sky': '◈ 跟隨即時天氣 — 關閉同步即可調整',
    'lock.matrix': '◈ 由 Matrix 模式設定 — 按 🕴 醒來',
    'lock.neon': '◈ 由風林火山模式設定 — 按 ❄️ 離開霓虹夜',
    'note.mesh': '網格', 'note.verts': '頂點', 'note.peak': '最高', 'note.m': '米', 'note.loading': '載入中', 'note.layers': '載入地圖圖層中', 'note.loadfail': '載入失敗',
    'install.ios': '將香港沙盒加到主畫面 —— 點擊分享，再選「加入主畫面」。', 'install.android': '安裝香港沙盒 —— 全螢幕、離線使用。', 'install.action': '安裝',
    'load.osm': '街道圖', 'load.sat': '衛星影像', 'load.mapfail': '地圖載入失敗', 'dens.full': '全部',
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
const skinOffset = () => cell * 0.6; // lift lines just above the surface, scaled to grid

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
    const res = await fetch(asset(u) + q, { cache: 'no-cache' });   // HKS-46: honour ASSET_BASE
    if (!res.body || !res.body.getReader) return res.json();
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
  skin = new THREE.Group(); skinBase.clear(); world.add(skin);
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
}

function updateNote() {
  document.getElementById('note').textContent =
    `${gridW}×${gridH} ${t('note.mesh')} · ${(gridW*gridH/1e3).toFixed(0)}k ${t('note.verts')} · ${t('note.peak')} ${Math.round(zmax)} ${t('note.m')}`;
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
let skyScale = 1;        // sky-layer height × — lifts/scales cloud altitude + rain ceiling (view control)
let tideManual = 0.5;    // slider 0..1 — used when not in live mode
let tideLevel  = 0.5;    // effective water level 0..1 (drives the sea height)
let tideSeries = null;   // live prediction: { vals[72] m, nowHour, min, max, cur, stationName } or null

// ---- wind + tropical-cyclone storm system ----------------------------------
let stormLevel = 0;      // 0 none, else HK signal 1 / 3 / 8 / 9 / 10
let windStrength = 0;    // 0..1 wind intensity (storm presets it; slider overrides)
let thunderRate = 0.4;   // 0..1 lightning strike frequency (storm/live preset it)
const flashfx = document.getElementById('flashfx');   // full-screen lightning flash
let baseHemi = 1.4, baseSun = 2.0;   // light levels before the lightning flash is added
const windVec = { x: 0, z: 1 };      // unit heading the wind blows TOWARD (screen space)
const WIND_VEC = {   // compass the wind blows FROM -> push vector (toward the opposite)
  N:[0,1], NE:[-0.707,0.707], E:[-1,0], SE:[-0.707,-0.707],
  S:[0,-1], SW:[0.707,-0.707], W:[1,0], NW:[0.707,0.707],
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

// clear colour + light levels: celestial sun/moon (when the sim is on) shape
// the key light and sky brightness; a storm then darkens whatever they chose.
function renderSky() {
  const onPaper = bgMode === 'paper';
  const k = stormLevel > 0 ? Math.min(0.6, 0.15 + windStrength * 0.55) : 0;
  const dim = 1 - (stormLevel > 0 ? windStrength * 0.4 : 0);
  const base = new THREE.Color(BG[bgMode]);
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
    // paper dims to a deep night blue; dark keeps its void, just a touch deeper
    base.lerp(new THREE.Color(onPaper ? 0x1b2430 : 0x04060a), (onPaper ? 0.82 : 0.6) * (1 - dayF));
  } else sun.color.setHex(0xffffff);
  if (snowAcc > 0) {           // cooler, desaturated grade while snowing
    sun.color.lerp(new THREE.Color(0xdce8f8), snowAcc * 0.45);
    base.lerp(new THREE.Color(0x9fb3c8), snowAcc * (onPaper ? 0.25 : 0.12));
  }
  base.lerp(new THREE.Color(0x1a2028), k);
  if (matrixOn) {                    // the void: near-black green, phosphor light
    base.setHex(0x020a05);
    sun.color.setHex(0x9cffb0);
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
    for (let i = 0; i < N; i++) {
      let x = rainHeads[i*3] + dx, y = rainHeads[i*3+1] - fall, z = rainHeads[i*3+2] + dz;
      if (y < 0) y = top;
      if (x >  hx) x -= 2*hx; else if (x < -hx) x += 2*hx;   // wrap horizontally
      if (z >  hz) z -= 2*hz; else if (z < -hz) z += 2*hz;
      rainHeads[i*3] = x; rainHeads[i*3+1] = y; rainHeads[i*3+2] = z;
      const o = i * 6;
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
    for (const s of cloudGrp.children) {
      s.position.x += cx * s.userData.drift; s.position.z += cz * s.userData.drift;
      s.material.rotation += 0.00015 * s.userData.drift * (1 + w * 2);   // slow churn
      if (s.position.x >  lx) s.position.x = -lx; else if (s.position.x < -lx) s.position.x = lx;
      if (s.position.z >  lz) s.position.z = -lz; else if (s.position.z < -lz) s.position.z = lz;
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
  const cAmt = (weather.clouds && cloudGrp) ? 0.4 + 0.45 * w : 0;
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
  if (weather.lightning) {
    if (flash > 0) { flash -= 0.08; hemi.intensity = baseHemi + flash * 5; }
    // quadratic, zero-floored: ~0 at low rate, intense near 100% (no always-on base term)
    else if (Math.random() < thunderRate * thunderRate * 0.1) {
      if (Math.random() < 0.6) { spawnBolt(); flash = 1; thunder(true); }   // close forked strike
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
  if (!matWeb) { matWeb = new THREE.MeshBasicMaterial(); attachTerrainFX(matWeb, false); }
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
  ['rain', 'clouds', 'fog', 'lightning', 'waves', 'snow', 'wind', 'thunderrate'].forEach(id => g(id).disabled = liveMode || storm);
  if (neonOn) g('snow').disabled = true;   // 風林火山 keeps Hong Kong snowbound
  g('winddir').disabled = liveMode;      // direction stays adjustable under a storm
  g('tide').disabled    = liveMode;
  g('storm').disabled   = liveMode;
  g('skymode').disabled = liveMode;      // live weather owns the clock too (sky = live HKT)
  const lock = g('wxlock');
  if (liveMode)     { lock.textContent = t('lock.live');  lock.style.display = 'block'; }
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
function spawnBolt() {
  const b = bounds();
  disposeBolt();
  const gx = (Math.random()*2 - 1) * b.halfX * 0.8, gz = (Math.random()*2 - 1) * b.halfZ * 0.8;
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
  if (skySel.taps.has(h)) skySel.taps.delete(h); else skySel.taps.add(h);
  conRetarget();
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
  // fade: 0 above -4° sun altitude → 1 below -10°; a bright high moon washes stars out
  const sunAltD = cel.sunAlt / D2R;
  let fade = Math.max(0, Math.min(1, (-4 - sunAltD) / 6));
  if (skySim.on && fade > 0 && cel.moonAlt > 0) fade *= 1 - 0.25 * cel.frac * Math.sin(cel.moonAlt);
  starGroup.visible = skySim.on && fade > 0.01;
  if (!starGroup.visible) { conClearAll(); return; }   // daylight: drop any lit constellations
  // the whole celestial sphere turns as one rigid body: image the equatorial
  // basis through the same hour-angle math the sun/moon use, once a sim-minute
  eqAxis(now, 0, 0, _eqX); eqAxis(now, Math.PI / 2, 0, _eqY); eqAxis(now, 0, Math.PI / 2, _eqZ);
  starGroup.quaternion.setFromRotationMatrix(_eqM.makeBasis(_eqX, _eqY, _eqZ));
  starGroup.scale.setScalar(bounds().span * 1.5);
  starUniforms.uFade.value = fade;
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
function stepSky() {   // per-frame sky life: twinkle clock, meteors, moon limb aim
  const tS = performance.now() * 0.001;
  if (starGroup.visible) starUniforms.uTime.value = tS % 4096;
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
  moonGlow.material.opacity = 0.16 + 0.55 * cel.frac;
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
  const key = skySim.live ? 'L' + Math.floor(now.getTime() / 60000) : 'F' + skySim.date + ':' + skySim.minutes;
  if (key === celKey) return;
  celKey = key;
  const sp = sunPosition(now, HK_LAT, HK_LON), mp = moonPosition(now, HK_LAT, HK_LON), mi = moonIllumination(now);
  cel = { sunAlt: sp.altitude, sunAz: compassDeg(sp.azimuth) * D2R,
          moonAlt: mp.altitude, moonAz: compassDeg(mp.azimuth) * D2R,
          frac: mi.fraction, phase: mi.phase };
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
const flight = { on: false, pov: false, pos: new THREE.Vector3(), yaw: 0, pitch: 0, roll: 0,
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
}
let planeGrp = null;
function buildPlane() {
  const s = 4;                                          // ~18 m wingspan: readable, near real scale
  const grp = new THREE.Group();
  const body = new THREE.MeshStandardMaterial({ color: 0xe3e8f0, roughness: 0.55, metalness: 0.15 });
  const red  = new THREE.MeshStandardMaterial({ color: 0xc23b2e, roughness: 0.6 });
  const fus = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.3, 3.0, 10), body);
  fus.rotation.x = -Math.PI / 2;                       // axis along z, taper to the nose
  grp.add(fus);
  const nose = new THREE.Mesh(new THREE.ConeGeometry(0.21, 0.7, 10), red);
  nose.rotation.x = -Math.PI / 2; nose.position.z = -1.8;
  grp.add(nose);
  const wing = new THREE.Mesh(new THREE.BoxGeometry(4.6, 0.07, 0.85), body);
  wing.position.set(0, 0.05, -0.25);
  grp.add(wing);
  const tail = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.06, 0.5), body);
  tail.position.set(0, 0.1, 1.35);
  grp.add(tail);
  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.65, 0.55), red);
  fin.position.set(0, 0.4, 1.4);
  grp.add(fin);
  const prop = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.07, 0.04), red);   // ~2.2 m blade
  prop.position.z = -2.16;
  grp.add(prop);
  grp.userData.prop = prop;
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
  document.getElementById('spindir').value = '0';
  if (!planeGrp) { planeGrp = buildPlane(); world.add(planeGrp); }
  planeGrp.visible = true;
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
  document.getElementById('flyhud').style.display = 'block';
  document.getElementById('flybtn').classList.add('on');
  document.getElementById('flybtn').blur();   // else Space (boost!) re-clicks the button and exits
  document.body.classList.add('flying');
  setTopMode('fly');
  updateViewBtn();
  controls.enabled = false;
  // HKS-86 §2: GPS follow/compass never persists outside Orbit — entering a
  // movement mode spawns at the fix (if it's on this map), then disengages
  if (geo.following || geo.compass) { if (geoInBounds()) teleportToMarker(); gpsDisengage(); }
  refreshDock();
}
function exitFlight() {
  if (!flight.on) return;
  flight.on = false;
  flight.keys = {};
  flight.touchHold = 0; flight.mouseLook = false; flight.lookYaw = 0; flight.lookPitch = 0;   // HKS-53
  if (planeGrp) planeGrp.visible = false;
  document.getElementById('flyhud').style.display = 'none';
  document.getElementById('flybtn').classList.remove('on');
  spinDir = flight.prevSpin;
  document.getElementById('spindir').value = String(spinDir);
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
}
// the view button beside Fly mirrors the C key: chase ↔ cockpit
function updateViewBtn() {
  const b = document.getElementById('viewbtn');
  b.disabled = !flight.on;
  b.classList.toggle('on', flight.on && flight.pov);
  b.textContent = flight.pov ? t('fly.cockpit') : t('fly.chase');
}
function toggleView() {
  if (!flight.on) return;
  flight.pov = !flight.pov;
  camera.up.set(0, 1, 0);
  updateViewBtn();
}
document.getElementById('flybtn').addEventListener('click', () => flight.on ? exitFlight() : enterFlight());
document.getElementById('viewbtn').addEventListener('click', toggleView);
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
  let p = null, hot = false;
  if (flight.on) {
    p = 100 * flight.speed / flight.top;
    hot = p >= 97;
  } else if (walk.on) {
    p = 100 * walk.spd / walk.top;
    if (walk.spd > 0.2)                               // a human gait is never a steady needle
      p *= 1 + Math.sin(walk.bob * 2.1) * 0.05 + (Math.random() - 0.5) * 0.05;
    hot = p >= 90;
  }
  if (p == null) { fill.style.width = '0%'; pct.textContent = '—'; fill.classList.remove('hot'); return; }
  p = Math.max(0, Math.min(100, p));
  fill.style.width = p.toFixed(1) + '%';
  pct.textContent = Math.round(p) + '%';
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
  else if (e.target.dataset.fly === 'autowalk') walk.auto = !walk.auto;
});
const FLY_DEBUG = new URLSearchParams(location.search).has('debug');
if (FLY_DEBUG) {   // automated-test handles; the flag survives URL re-serialization
  window.__flight = flight;
  window.__stepFlight = () => stepFlight();
  window.__three = () => ({ renderer, scene, camera, sun, hemi, terrain, sea, tidalMats });
}

const _fq = new THREE.Quaternion(), _fe = new THREE.Euler(), _fv = new THREE.Vector3();
const _fc = new THREE.Vector3(), _fl = new THREE.Vector3(), _fu = new THREE.Vector3();
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
    if (K[' '] || F.touchHold > 0) takeOff();   // HKS-53: hold to launch, then keep the gas on
  } else if (agl < 4 && _fv.y <= 0.02) {               // only while descending — a fresh
    F.landed = true;                                   // climb-out stays airborne
    F.pitch = Math.max(0, F.pitch * 0.3); F.roll *= 0.5;
    F.pos.y = surfY + 2.2;
    flash = Math.max(flash, 0.15);                     // a soft touchdown bump
  }
  planeGrp.position.copy(F.pos);
  planeGrp.quaternion.copy(_fq);
  if (planeGrp.userData.prop) planeGrp.userData.prop.rotation.z += 0.25 + F.speed * 0.004;
  setEngine(sndOn ? (F.landed ? 0.12 : 0.25 + 0.75 * (F.speed - 28) / Math.max(20, F.top - 28)) : 0);
  // --- FOV: the orbit view is telephoto (38°); flight goes wide for speed feel
  // — chase 55°, cockpit 68° — and stretches a few degrees more near full
  // throttle. Eased so view switches breathe instead of snapping.
  const fovT = (F.pov ? 68 : 55) + 6 * (F.speed - 62) / Math.max(20, F.top - 62);
  if (Math.abs(camera.fov - fovT) > 0.05) {
    camera.fov += (fovT - camera.fov) * 0.06;
    camera.updateProjectionMatrix();
  }
  // look-around boom (HKS-53): drag offsets the view the same way in both cameras;
  // ease back to centre once nothing is held (no finger down, no mouse drag)
  if (!F.touchHold && !F.mouseLook) { F.lookYaw *= 0.9; F.lookPitch *= 0.9; }
  // --- cameras (world space: survives any leftover world spin)
  if (F.pov) {                                         // cockpit: seated just behind the cowl —
    _fu.set(0, 1, 0).applyQuaternion(_fq);             // nose + spinning prop stay in frame,
    _fc.copy(F.pos).addScaledVector(_fv, 2.2).addScaledVector(_fu, 2.3);   // horizon rolls
    world.localToWorld(_fc);
    camera.position.copy(_fc);
    // head-turn: rotate the look direction by the shared boom offset (HKS-53)
    _fe2.set(F.lookPitch, F.lookYaw, 0, 'YXZ');
    _fq2.copy(_fq).multiply(_lookQ.setFromEuler(_fe2));
    _fv2.set(0, 0, -1).applyQuaternion(_fq2);
    _fl.copy(F.pos).addScaledVector(_fv2, 2000); world.localToWorld(_fl);
    camera.up.copy(_fu);
    camera.lookAt(_fl);
  } else {                                             // chase: boom ~58 m out, orbitable (HKS-53)
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
  const stats = `${F.landed ? '🛬' : '✈'} ${Math.round(F.pos.y / VE)} m · AGL ${Math.max(0, Math.round(agl))} m` +
    ` · ${String(Math.round(az)).padStart(3, '0')}° ${CARD[Math.round(az / 45) % 8]}` +
    ` · ${Math.round(F.speed * 1.944)} kt` +
    (F.landed ? ` · ${t('fly.landed')}` : '');
  // HKS-86: the how-to now lives in the Help drawer — the HUD keeps only the live
  // stats + the functional tap-controls (takeoff / view / exit)
  const hints = (F.landed
    ? `<span data-fly="takeoff" style="cursor:pointer;text-decoration:underline;font-weight:700">${t('fly.takeoff')}</span>`
    : `<span data-fly="view" style="cursor:pointer;text-decoration:underline">${t('fly.view')}</span>`) +
    ` · <span data-fly="exit" style="cursor:pointer;text-decoration:underline">${t('fly.exit')}</span>`;
  if (F.helpT > 0) F.helpT--;
  document.getElementById('flyhud').innerHTML = F.helpT > 0
    ? `${stats}<small style="font-size:11px;line-height:1.9">${hints}</small>`
    : `${stats}<small>${hints}</small>`;
  updateSpeedGauge();
}

// ---- walk mode (HKS-33): first person on foot, at a real walking pace -------
// Drops you at the current view centre, eye 1.7 m over the DEM, 1.4 m/s (Shift
// jogs at 4). WASD/arrows move, pointer-lock mouse looks; phones drag to look
// with a ▶ auto-walk toggle in the HUD. Slopes steeper than ~45° block you.
const walk = { on: false, pos: new THREE.Vector3(), yaw: 0, pitch: -0.04,
               keys: {}, prevSpin: 1, auto: false, helpT: 0, dist: 0, bob: 0,
               vy: 0, land: 0, spd: 0, top: 24 / 3.6, pov: true, touchHold: 0 };
let hikerGrp = null;
// ?nolock=1 — debug switch: skip pointer lock; mouse look becomes drag-to-look
// so the keyboard path can be tested in isolation from the lock
const NO_LOCK = new URLSearchParams(location.search).has('nolock');
function enterWalk(startLocal) {
  if (walk.on || !curG) return;
  if (flight.on) exitFlight();
  if (stargaze.on) exitStargaze();
  walk.on = true;
  walk.prevSpin = spinDir; spinDir = 0;
  document.getElementById('spindir').value = '0';
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
  walk.pos.y = (sampleE(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2) + 1.7 + 60) * VE;
  if (!hikerGrp) { hikerGrp = buildHiker(); world.add(hikerGrp); }
  setTopMode('walk');
  updateWalkViewBtn();
  camera.fov = 70; camera.updateProjectionMatrix();
  document.getElementById('flyhud').style.display = 'block';
  document.getElementById('walkbtn').classList.add('on');
  document.getElementById('walkbtn').blur();  // else Space/Enter re-clicks the button and exits
  document.body.classList.add('flying');                  // fly/walk shared UI state (speed gauge, no-select)
  controls.enabled = false;
  // HKS-86 §2: GPS follow/compass never persists outside Orbit — entering a
  // movement mode spawns at the fix (if it's on this map), then disengages
  if (geo.following || geo.compass) { if (geoInBounds()) teleportToMarker(); gpsDisengage(); }
  refreshDock();
  if (!NO_LOCK && renderer.domElement.requestPointerLock) renderer.domElement.requestPointerLock();
}
function exitWalk() {
  if (!walk.on) return;
  walk.on = false; walk.keys = {};
  if (hikerGrp) hikerGrp.visible = false;
  setTopMode(null);
  updateSpeedGauge();
  if (document.exitPointerLock) document.exitPointerLock();
  document.getElementById('flyhud').style.display = 'none';
  document.getElementById('walkbtn').classList.remove('on');
  document.body.classList.remove('flying');
  spinDir = walk.prevSpin;
  document.getElementById('spindir').value = String(spinDir);
  camera.fov = 38; camera.updateProjectionMatrix();
  camera.up.set(0, 1, 0);
  controls.enabled = true;
  frameCamera();
  refreshDock();
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
  tray.hidden = !mode;
  if (typeof updateHelp === 'function') updateHelp();   // keep the Help drawer's contextual section in sync
}
document.getElementById('orbitbtn').addEventListener('click', () => { exitFlight(); exitWalk(); exitStargaze(); refreshDock(); });
document.getElementById('trayend').addEventListener('click', () => { exitFlight(); exitWalk(); exitStargaze(); });
document.getElementById('dockgear').addEventListener('click', () =>
  document.getElementById('panel').classList.toggle('collapsed'));
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
    if (spinDir !== 0) { geo.prevSpin = spinDir; spinDir = 0; document.getElementById('spindir').value = '0'; }
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
  const rm = document.getElementById('locateremove');
  if (rm) rm.hidden = !geo.has;
}
function locateThenFollow() {       // off → follow: one fix, zoom to it, then track
  locateBtn.classList.add('locating');
  navigator.geolocation.getCurrentPosition(pos => {
    locateBtn.classList.remove('locating');
    if (placeFix(pos.coords)) { centreOnMarker(true, false); startFollow(); }
    refreshGpsBtn();
  }, e => { geoErr(e); refreshGpsBtn(); }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 });
}
function gpsDisengage() {           // drop follow + compass; the pin stays
  stopFollow();
  if (geo.compass) setCompassView(false);
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
    walk.pos.y = (sampleE(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2) + 1.7 + 60) * VE;
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
  navigator.geolocation.getCurrentPosition(pos => {
    locateBtn.classList.remove('locating');
    if (placeFix(pos.coords)) teleportToMarker();
    gpsDisengage();
  }, e => { geoErr(e); gpsDisengage(); }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 30000 });
}
function startWatch() {
  geo.watch = navigator.geolocation.watchPosition(pos => {
    const c = pos.coords, gg = gpsToGrid(c.latitude, c.longitude);
    if (!gg || !gg.inBounds) return;                     // skip out-of-bounds fixes while following
    const gate = Math.max(5, (c.accuracy || 0) * 0.5);   // jitter gate: ignore sub-accuracy wiggle
    if (geo.has && Math.hypot(gg.E - geo.E, gg.N - geo.N) < gate) { geo.acc = Math.max(6, c.accuracy || geo.acc); return; }
    geo.E = gg.E; geo.N = gg.N; geo.acc = Math.max(6, c.accuracy || 0); geo.has = true;
    centreOnMarker(true, true);                           // pan to follow, keep the user's zoom/angle
  }, geoErr, { enableHighAccuracy: true, timeout: 15000, maximumAge: 2000 });
}
function startFollow() {
  if (geo.watch != null) return;
  geo.following = true; locateBtn.classList.add('follow', 'on');
  if (geo.el) geo.el.classList.add('live');
  if (geo.has) centreOnMarker(true, true);                 // recentre now — the first watch fix is usually the stored one (jitter-gated)
  startWatch();
  clearTimeout(geo.autoStop); geo.autoStop = setTimeout(() => stopFollow(), 15 * 60000);   // battery backstop
}
function stopFollow() {
  if (geo.watch != null) { navigator.geolocation.clearWatch(geo.watch); geo.watch = null; }
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
  if (geo.prevSpin != null) { spinDir = geo.prevSpin; document.getElementById('spindir').value = String(spinDir); geo.prevSpin = null; }
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
  if (on && spinDir !== 0) { geo.prevSpin = spinDir; spinDir = 0; document.getElementById('spindir').value = '0'; }
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
// is a movement mode driving the camera? then GPS never persists (HKS-86 §2)
const inMovementMode = () => flight.on || walk.on || stargaze.on;
locateBtn.addEventListener('click', e => {
  e.stopPropagation();
  enableCompass();   // request device-orientation on this user gesture (needed for iOS)
  if (inMovementMode()) { gpsTeleport(); return; }
  const st = gpsState();                    // Orbit: follow → compass → off
  if (st === 'off') locateThenFollow();
  else if (st === 'follow') { setCompassView(true); refreshGpsBtn(); }
  else gpsDisengage();
});
document.getElementById('locateremove').addEventListener('click', e => {
  e.stopPropagation();
  removeMarker();
  refreshGpsBtn();
});
addEventListener('mousemove', e => {                      // pointer-lock look
  if (!walk.on || document.pointerLockElement !== renderer.domElement) return;
  walk.yaw -= e.movementX * 0.0022;
  walk.pitch = Math.max(-1.25, Math.min(1.25, walk.pitch - e.movementY * 0.0022));
});
renderer.domElement.addEventListener('click', () => {     // re-arm the lock after Esc
  if (walk.on && !NO_LOCK && renderer.domElement.requestPointerLock) renderer.domElement.requestPointerLock();
});
renderer.domElement.addEventListener('pointerdown', () => {   // tap anywhere = take off
  if (flight.on && flight.landed) takeOff();
});
// flight: hold the left mouse button and drag to look around (shared boom, HKS-53)
addEventListener('mousemove', e => {
  if (!flight.on || e.buttons !== 1) return;
  flight.lookYaw = Math.max(-2.8, Math.min(2.8, flight.lookYaw - e.movementX * 0.004));
  flight.lookPitch = Math.max(-1.0, Math.min(1.0, flight.lookPitch - e.movementY * 0.004));
  flight.mouseLook = true;
});
addEventListener('mouseup', () => { flight.mouseLook = false; });
// nolock debug mode: hold the left button and drag to look
addEventListener('mousemove', e => {
  if (!walk.on || !NO_LOCK || e.buttons !== 1) return;
  walk.yaw -= e.movementX * 0.0035;
  walk.pitch = Math.max(-1.25, Math.min(1.25, walk.pitch - e.movementY * 0.0035));
});
let _lastTouch = null;                                    // phones: drag to look
addEventListener('touchmove', e => {
  if (e.target !== renderer.domElement || !(walk.on || flight.on || stargaze.on)) return;
  const t0 = e.touches[0];
  if (_lastTouch) {
    const dx = t0.clientX - _lastTouch.x, dy = t0.clientY - _lastTouch.y;
    if (walk.on) {
      walk.yaw -= dx * 0.005;
      walk.pitch = Math.max(-1.25, Math.min(1.25, walk.pitch - dy * 0.005));
    } else if (stargaze.on) {                            // stargaze: drag pans the sky (HKS-86)
      stargaze.yaw -= dx * 0.005;
      stargaze.pitch = Math.max(-0.15, Math.min(1.5, stargaze.pitch - dy * 0.005));
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
// walk camera views — first person ↔ chase, mirroring the flight pattern
function updateWalkViewBtn() {
  const b = document.getElementById('walkviewbtn');
  b.textContent = walk.pov ? t('walk.fp') : t('walk.chase');
  b.classList.toggle('on', !walk.pov);
}
function toggleWalkView() {
  if (!walk.on) return;
  walk.pov = !walk.pov;
  updateWalkViewBtn();
}
document.getElementById('walkviewbtn').addEventListener('click', toggleWalkView);

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
    const gCur = sampleE(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2);
    const step = (mx, mz) => {                            // one gated move attempt
      if (!mx && !mz) return false;
      const nx = Math.max(-b.halfX, Math.min(b.halfX, walk.pos.x + mx));
      const nz = Math.max(-b.halfZ, Math.min(b.halfZ, walk.pos.z + mz));
      const gNew = sampleE(nx / cell + W / 2, nz / cell + H / 2);
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
  const g = sampleE(walk.pos.x / cell + W / 2, walk.pos.z / cell + H / 2);
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
  // the hiker's body: visible in chase view, gait swings limbs + stick
  if (hikerGrp) {
    hikerGrp.visible = !walk.pov;
    if (!walk.pov) {
      hikerGrp.position.set(walk.pos.x, walk.pos.y - 1.7 * VE + (airborne ? 0 : bobY), walk.pos.z);
      hikerGrp.rotation.y = walk.yaw;
      const u = hikerGrp.userData;
      const sw = walk.spd > 0.2 ? Math.sin(walk.bob) * Math.min(0.75, 0.25 + walk.spd * 0.05) : 0;
      u.legL.rotation.x = sw;         u.legR.rotation.x = -sw;
      u.armL.rotation.x = -sw * 0.7;  u.armR.rotation.x = sw * 0.7;
      u.stick.rotation.x = 0.15 + sw * 0.55;            // the stick plants with the stride
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
  const touch = matchMedia('(pointer: coarse)').matches;
  const odo = walk.dist < 1000 ? `${Math.round(walk.dist)} m` : `${(walk.dist / 1000).toFixed(2)} km`;
  const stats = `${airborne ? '🪂' : '🚶'} ${Math.round(g)} m · ${String(Math.round(az)).padStart(3, '0')}° ${CARD[Math.round(az / 45) % 8]}` +
    (walk.spd > 0.3 ? ` · ${Math.round(walk.spd * 3.6)} km/h` : '') +
    ` · ${t('walk.dist')} ${odo}` +                       // odometer: live proof the keys register
    (boost && moving ? ` · ${t('walk.jog')}` : '');
  // HKS-86: how-to moved to the Help drawer — keep the live stats + the functional
  // tap-controls (auto-walk toggle on touch, exit)
  const hints = (touch ? `<span data-fly="autowalk" style="cursor:pointer;text-decoration:underline">${walk.auto ? '⏸' : '▶'}</span> · ` : '') +
    `<span data-fly="exit" style="cursor:pointer;text-decoration:underline">${t('fly.exit')}</span>`;
  if (walk.helpT > 0) walk.helpT--;
  document.getElementById('flyhud').innerHTML = walk.helpT > 0
    ? `${stats}<small style="font-size:11px;line-height:1.9">${hints}</small>`
    : `${stats}<small>${hints}</small>`;
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
  applyControlLocks();
  updateWindVisuals();       // re-grades clouds/rain for the new reality (calls renderSky + setFog)
  refreshDock();
  syncUrl();
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
  applyControlLocks();
  refreshDock();
  syncUrl();
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

// ---- Stargaze mode (HKS-86 §4) -----------------------------------------------
// A planetarium anchored at the current view centre: the camera plants eye-high
// on the terrain, FIXED — look-only, no locomotion — biased up at the star layer
// (HKS-84 catalogue + constellations; hover/tap picking keeps working). Its tray
// carries a proxy for the existing sky clock (#skymode/#skytime) plus the two
// special toggles: 🧭 point-at-the-sky (device orientation) and 📍 follow-me
// (GPS anchor tracking, default OFF, experimental). World themes (Matrix/Neon)
// stay combinable. Entering dims the weather chip + radar dial (CSS,
// body.stargazing); everything restores on exit.
const stargaze = { on: false, pos: new THREE.Vector3(), yaw: 0, pitch: 0.9,
                   prevSpin: 1, prevSky: null, orient: false, followWatch: null };
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
  document.getElementById('spindir').value = '0';
  // anchor at the current view centre, eye 1.7 m over the DEM
  const b = bounds();
  const t0 = world.worldToLocal(controls.target.clone());
  stargaze.pos.set(
    Math.max(-b.halfX, Math.min(b.halfX, t0.x)), 0,
    Math.max(-b.halfZ, Math.min(b.halfZ, t0.z)));
  const fx = controls.target.x - camera.position.x, fz = controls.target.z - camera.position.z;
  stargaze.yaw = -(Math.atan2(fx, -fz) + world.rotation.y);   // keep facing the way you looked
  stargaze.pitch = 0.9;                                        // biased up at the sky
  // HKS-86 §2: GPS follow/compass engaged → plant at the fix, then disengage
  if (geo.following || geo.compass) {
    if (geoInBounds()) { const p = markerLocalPoint(); stargaze.pos.x = p.x; stargaze.pos.z = p.z; }
    gpsDisengage();
  }
  // guarantee the star layer: if the sky sim is off or it's daylight, jump the
  // clock to tonight 22:00 (custom time); the previous setting restores on exit
  updateCelestial();
  if (!starGroup.visible) {
    stargaze.prevSky = { mode: document.getElementById('skymode').value,
                        date: document.getElementById('skydate').value,
                        minutes: document.getElementById('skytime').value };
    setSkyControl('fixed', hktDateStr(new Date()), 1320);
  }
  camera.fov = 60; camera.updateProjectionMatrix();     // wide for sky sweep
  controls.enabled = false;
  document.body.classList.add('stargazing');            // dims wx chip + radar dial (CSS)
  document.getElementById('stargazebtn').blur();        // else ␣/Enter re-clicks and exits
  syncSgTray();
  refreshDock();
}
function exitStargaze() {
  if (!stargaze.on) return;
  stargaze.on = false;
  setStargazeOrient(false);
  setStargazeFollow(false);
  if (stargaze.prevSky) {                               // hand the sky clock back
    setSkyControl(stargaze.prevSky.mode, stargaze.prevSky.date, stargaze.prevSky.minutes);
    stargaze.prevSky = null;
  }
  spinDir = stargaze.prevSpin;
  document.getElementById('spindir').value = String(spinDir);
  camera.fov = 38; camera.updateProjectionMatrix();
  camera.up.set(0, 1, 0);
  controls.enabled = true;
  document.body.classList.remove('stargazing');
  frameCamera();
  refreshDock();
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
// 🧭 point-at-the-sky: device orientation aims the camera (iOS asks permission
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
function setStargazeOrient(on) {
  if (on === stargaze.orient) return;
  const arm = () => {
    stargaze.orient = true;
    addEventListener('deviceorientation', onSgOrient, true);
    syncSgToggles();
  };
  if (!on) {
    stargaze.orient = false;
    removeEventListener('deviceorientation', onSgOrient, true);
    syncSgToggles();
    return;
  }
  if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function')
    DeviceOrientationEvent.requestPermission().then(s => { if (s === 'granted') arm(); }).catch(() => {});
  else arm();
}
// 📍 follow-me (experimental, default OFF): a watch drags the anchor with you
function setStargazeFollow(on) {
  if (on === (stargaze.followWatch != null)) return;
  if (on) {
    stargaze.followWatch = navigator.geolocation.watchPosition(pos => {
      const gg = gpsToGrid(pos.coords.latitude, pos.coords.longitude);
      if (!gg || !gg.inBounds) return;
      const b = bounds();
      stargaze.pos.x = Math.max(-b.halfX, Math.min(b.halfX, (gg.col - W / 2) * cell));
      stargaze.pos.z = Math.max(-b.halfZ, Math.min(b.halfZ, (gg.row - H / 2) * cell));
    }, geoErr, { enableHighAccuracy: true, timeout: 15000, maximumAge: 2000 });
  } else {
    navigator.geolocation.clearWatch(stargaze.followWatch);
    stargaze.followWatch = null;
  }
  syncSgToggles();
}
function syncSgToggles() {
  const g = id => document.getElementById(id);
  g('sg-orient').classList.toggle('on', stargaze.orient);
  g('sg-orient').setAttribute('aria-pressed', stargaze.orient ? 'true' : 'false');
  g('sg-follow').classList.toggle('on', stargaze.followWatch != null);
  g('sg-follow').setAttribute('aria-pressed', stargaze.followWatch != null ? 'true' : 'false');
}
function syncSgTray() {   // mirror the panel's sky clock into the tray proxy
  const g = id => document.getElementById(id);
  const live = skySim.on && skySim.live;
  g('sg-live').classList.toggle('on', live);
  g('sg-custom').classList.toggle('on', !live);
  g('sg-time').disabled = live;
  g('sg-time').value = live ? hktMinutes(new Date()) : skySim.minutes;
  g('sg-timev').textContent = mmToHHMM(+g('sg-time').value);
  g('sg-orient').hidden = typeof DeviceOrientationEvent === 'undefined';
  g('sg-follow').hidden = !window.isSecureContext || !('geolocation' in navigator);
  syncSgToggles();
  const mi = moonIllumination(simDate());
  g('sg-hint').textContent = `☾ ${Math.round(mi.fraction * 100)}%`;   // how-to lives in the Help drawer (HKS-86)
}
document.getElementById('stargazebtn').addEventListener('click', () => stargaze.on ? exitStargaze() : enterStargaze());
document.getElementById('sg-live').addEventListener('click', () => { setSkyControl('live'); syncSgTray(); });
document.getElementById('sg-custom').addEventListener('click', () => {
  setSkyControl('fixed', hktDateStr(new Date()), skySim.minutes);
  syncSgTray();
});
document.getElementById('sg-time').addEventListener('input', e => {
  if (skySim.on && skySim.live) return;                 // scrub only drives custom time
  setSkyControl('fixed', null, +e.target.value);
  document.getElementById('sg-timev').textContent = mmToHHMM(+e.target.value);
  const mi = moonIllumination(simDate());
  document.getElementById('sg-hint').textContent = `☾ ${Math.round(mi.fraction * 100)}%`;   // how-to lives in the Help drawer (HKS-86)
});
document.getElementById('sg-orient').addEventListener('click', () => setStargazeOrient(!stargaze.orient));
document.getElementById('sg-follow').addEventListener('click', () => setStargazeFollow(stargaze.followWatch == null));
// panel-side sky changes keep the tray proxy honest while stargazing
document.getElementById('skymode').addEventListener('change', () => { if (stargaze.on) syncSgTray(); });
addEventListener('keydown', e => { if (stargaze.on && e.key === 'Escape') exitStargaze(); });
// drag-to-look (desktop): hold the left button; phones reuse the shared touch path
addEventListener('mousemove', e => {
  if (!stargaze.on || e.buttons !== 1) return;
  stargaze.yaw -= e.movementX * 0.003;
  stargaze.pitch = Math.max(-0.15, Math.min(1.5, stargaze.pitch - e.movementY * 0.003));
});
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
  if (flight.on) { flight.yaw = 0; return; }             // point the plane north
  if (stargaze.on) { stargaze.yaw = 0; return; }         // face north under the stars
  const t = controls.target, p = camera.position, ry = world.rotation.y;
  const d = Math.hypot(p.x - t.x, p.z - t.z);
  p.x = t.x + Math.sin(ry) * d;                          // due terrain-south of the target
  p.z = t.z + Math.cos(ry) * d;
  controls.update();
});
async function snapshot() {
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
function rfLabelSvg(ac, text, on, top) {         // straight label at the sector centre, rotated tangentially
  const [x, y] = rfPolar(RF.rt, ac);
  const rot = top ? ac : ac - 180;               // bottom labels flip so they stay upright
  return `<text class="rf-lab${on ? ' on' : ''}" x="${x.toFixed(2)}" y="${y.toFixed(2)}" transform="rotate(${rot.toFixed(1)} ${x.toFixed(2)} ${y.toFixed(2)})">${text}</text>`;
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
    modes.map(m => rfLabelSvg(m.ac, m.lab, m.on, true)).join('') + ranges.map(r => rfLabelSvg(r.ac, r.lab, r.on, false)).join('');
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
    radarBig = !radarBig; radarHudEl.classList.toggle('big', radarBig); renderWxviewControls(); return;
  }
  const p = target.closest('path[data-grp]'); if (!p) return;
  if (p.dataset.grp === 'mode') setWxMode(p.dataset.key);
  else { if (isSat()) satZoom = p.dataset.key; else radarRange = p.dataset.key; renderWxviewControls(); if (radarRunning) startRadar(); }
  syncUrl();   // write the new mode/range into the address bar (the dial lives outside #panel)
}
const rfTabsEl = document.getElementById('rf-tabs');
rfTabsEl.addEventListener('click', e => activateRfTab(e.target));
rfTabsEl.addEventListener('keydown', e => {   // keyboard access for the SVG tabs (a11y)
  if (e.key !== 'Enter' && e.key !== ' ' && e.key !== 'Spacebar') return;
  if (!e.target.closest('[data-grp],[data-size]')) return;
  e.preventDefault(); activateRfTab(e.target);
});

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
  loadSource(e.target.value).then(() => { if (liveMode) syncLiveTide(); }).catch(err => {
    document.getElementById('note').textContent = t('note.loadfail') + ': ' + err.message; console.error(err);
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
const rot = d => () => { texRot = Math.round((texRot + d) * 10) / 10; applyTexRot(); syncUrl(); };
document.getElementById('toporotL').addEventListener('click', rot(-1));
document.getElementById('toporotLf').addEventListener('click', rot(-0.2));
document.getElementById('toporotRf').addEventListener('click', rot(0.2));
document.getElementById('toporotR').addEventListener('click', rot(1));
document.getElementById('toporot0').addEventListener('click', () => { texRot = 0; applyTexRot(); syncUrl(); });
document.getElementById('water').addEventListener('change', e => { sea.visible = e.target.checked; });
document.getElementById('labels').addEventListener('change', e => { labels.forEach(l => l.div.style.display = e.target.checked ? '' : 'none'); });
document.getElementById('spindir').addEventListener('change', e => { spinDir = parseInt(e.target.value, 10); });
document.getElementById('spinspd').addEventListener('input', e => { spinSpeed = parseFloat(e.target.value); });
const panelEl = document.getElementById('panel');
document.getElementById('collapse-btn').addEventListener('click', () => panelEl.classList.add('collapsed'));
// ---- mobile drawers (HKS-16): panel is a bottom sheet, HUD a tap-to-expand chip.
// Start tucked away on phones so the map is unobstructed; tapping the map dismisses both.
const mobileMQ = matchMedia('(max-width: 640px), (pointer: coarse) and (max-height: 500px)');
const wxhudEl = document.getElementById('wxhud');
function applyMobileLayout(mobile) {
  panelEl.classList.toggle('collapsed', mobile);
  if (!mobile) wxhudEl.classList.remove('expanded');
}
applyMobileLayout(mobileMQ.matches);
mobileMQ.addEventListener('change', e => applyMobileLayout(e.matches));
document.getElementById('sheetgrip').addEventListener('click', () => panelEl.classList.add('collapsed'));
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
// ---- credits popover (floating corner chip) --------------------------------
const creditsBtn = document.getElementById('creditsbtn');
const creditsPop = document.getElementById('creditspop');
function setCredits(open) {
  creditsPop.classList.toggle('open', open);
  creditsBtn.classList.toggle('on', open);
  creditsBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
}
creditsBtn.addEventListener('click', e => { e.stopPropagation(); setCredits(!creditsPop.classList.contains('open')); });
creditsPop.addEventListener('click', e => e.stopPropagation());   // clicks inside stay open
document.addEventListener('click', () => setCredits(false));       // click anywhere else closes
document.addEventListener('keydown', e => { if (e.key === 'Escape') setCredits(false); });

// ---- weather-notices bulletin (HKS-80) --------------------------------------
// The long HKO warning + forecast texts live in a pull-up glass sheet instead of
// cluttering the weather box. Dismissal is session-only — never written to storage,
// so a fresh load re-surfaces an active warning.
const wxBulletin = document.getElementById('wxbulletin');
const wbTab = document.getElementById('wb-tab');
let bulletinDismissed = false, bulletinAutoShown = false;
const bulletinOpen = () => wxBulletin.classList.contains('open');
function setBulletin(open) {
  wxBulletin.classList.toggle('open', open);
  wbTab.setAttribute('aria-expanded', open ? 'true' : 'false');
  if (!open) bulletinDismissed = true;      // a manual close stops it auto-reopening this session
}
// fill a section with a bold label + one <div> per paragraph (textContent = no injection)
function fillWbSection(elm, label, body) {
  elm.textContent = '';
  if (!body) return;
  const b = document.createElement('b'); b.textContent = label; elm.appendChild(b);
  body.split(/\n+/).map(s => s.trim()).filter(Boolean).forEach(para => {
    const d = document.createElement('div'); d.textContent = para; elm.appendChild(d);
  });
}
wbTab.addEventListener('click', () => setBulletin(!bulletinOpen()));            // tap the tab to open / close
document.getElementById('wb-close').addEventListener('click', () => setBulletin(false));
document.getElementById('wx-warn').addEventListener('click', e => {
  e.stopPropagation();                      // don't collapse the weather chip on mobile
  if (document.getElementById('wx-warn').textContent.trim()) setBulletin(!bulletinOpen());
});
document.addEventListener('keydown', e => { if (e.key === 'Escape' && bulletinOpen()) setBulletin(false); });

// ---- adaptive Help / controls drawer (HKS-86) -------------------------------
// All navigation help centralises here: a right-edge tab below the weather tab.
// A general section (how to reach each mode) is always shown; a contextual
// section follows the active mode. Refreshed from refreshDock() + on locale
// switch. Reuses fillWbSection (bold label + one <div> per line, textContent).
const helpDrawer = document.getElementById('helpdrawer');
const hpTab = document.getElementById('hp-tab');
const helpOpen = () => helpDrawer.classList.contains('open');
function setHelp(open) { helpDrawer.classList.toggle('open', open); hpTab.setAttribute('aria-expanded', open ? 'true' : 'false'); }
function updateHelp() {
  const ctx = document.getElementById('hp-context'), gen = document.getElementById('hp-general');
  if (!ctx || !gen) return;
  const mode = flight.on ? 'fly' : walk.on ? 'walk' : stargaze.on ? 'star' : 'orbit';
  fillWbSection(ctx, t('help.' + mode + '.t'), t('help.' + mode + '.b'));
  fillWbSection(gen, t('help.gen.t'), t('help.gen.b'));
}
hpTab.addEventListener('click', () => setHelp(!helpOpen()));
document.getElementById('hp-close').addEventListener('click', () => setHelp(false));
updateHelp();
requestAnimationFrame(() => helpDrawer.classList.add('ready'));   // enable slide-in after first paint

document.getElementById('fog').addEventListener('change', e => {
  weather.fog = e.target.checked; setFog();
  if (mistGrp) mistGrp.visible = weather.fog;
});
document.getElementById('rain').addEventListener('change', e => { weather.rain = e.target.checked; if (rainPts) rainPts.visible = weather.rain; });
document.getElementById('clouds').addEventListener('change', e => { weather.clouds = e.target.checked; if (cloudGrp) cloudGrp.visible = weather.clouds; });
document.getElementById('lightning').addEventListener('change', e => {
  weather.lightning = e.target.checked;
  if (!weather.lightning) { flash = 0; boltLife = 0; disposeBolt(); if (boltLight) boltLight.intensity = 0; applyBg(bgMode); }
});
document.getElementById('waves').addEventListener('change', e => { weather.waves = e.target.checked; });
document.getElementById('snow').addEventListener('change', e => { weather.snow = e.target.checked; if (snowPts) snowPts.visible = weather.snow; });
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
sndBtn.addEventListener('click', () => setSound(!sndOn));
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
});
document.getElementById('skydate').addEventListener('change', e => { if (e.target.value) skySim.date = e.target.value; celKey = ''; updateCelestial(); });
document.getElementById('skytime').addEventListener('input', e => {
  skySim.minutes = parseInt(e.target.value, 10) || 0;
  document.getElementById('skytimev').textContent = mmToHHMM(skySim.minutes);
  celKey = ''; updateCelestial();
});
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
document.getElementById('storm').addEventListener('change', e => applyStorm(parseInt(e.target.value, 10)));
document.getElementById('wind').addEventListener('input', e => {
  windStrength = parseInt(e.target.value, 10) / 100;     // fine wind override (keeps the current signal)
  document.getElementById('windv').textContent = Math.round(windStrength * 100) + '%';
  updateWindVisuals();
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
document.getElementById('winddir').addEventListener('change', e => { setWindDir(e.target.value); updateStormBadge(); });

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

async function syncLiveWeather() {
  const el = id => document.getElementById(id);
  const chk = (id, on) => { const e = el(id); if (e.checked !== on) { e.checked = on; e.dispatchEvent(new Event('change', { bubbles: true })); } };
  try {
    const base = `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=${isZh() ? 'tc' : 'en'}&dataType=`;
    const oBase = 'https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?lang=en&rformat=json&dataType=';
    const [rh, fl, ws, lhl] = await Promise.all([
      fetch(base + 'rhrread').then(r => r.json()),
      fetch(base + 'flw').then(r => r.json()).catch(() => ({})),
      fetch(base + 'warnsum').then(r => r.json()).catch(() => ({})),
      fetch(oBase + 'LHL').then(r => r.json()).catch(() => ({})),   // past-hour lightning counts by region
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
    wxBulletin.classList.toggle('ready', !!(warn || fcast));   // reveal the pull-out tab once there's content
    wxBulletin.classList.toggle('warn', !!warn);               // amber tab + ⚠ when a warning is in force
    // keep the compact in-box chip too, as a secondary indicator that opens the drawer
    const warnChip = el('wx-warn');
    warnChip.classList.toggle('warn', !!warn);
    warnChip.textContent = warn ? `⚠ ${t('wb.chip')}` : (fcast ? t('wb.chip') : '');
    if (warn && !bulletinDismissed && !bulletinAutoShown) { bulletinAutoShown = true; setBulletin(true); }   // surface an active warning once/session
    const rainy = [53,54,62,63,64,65].includes(code) || rainMax > 0;
    chk('rain', rainy);
    // real past-hour cloud-to-ground lightning count (data.gov.hk LHL), region-aware
    const lregion = /lantau/.test(el('src').value) ? 'Lantau' : 'Hong Kong territory';
    let cg = 0; for (const row of (lhl.data || [])) if (row[1] === 'Cloud-to-ground' && row[2] === lregion) cg = +row[3] || 0;
    const stormy = cg > 0 || code === 65 || /thunderstorm|雷暴/i.test(warn);
    chk('lightning', stormy);
    setThunderRate(cg > 0 ? Math.min(1, 0.15 + cg / 150) : (stormy ? 0.4 : 0));   // strikes/hr → rate
    el('wx-warn').dataset.ltg = cg;                     // (available for a HUD readout if wanted)
    chk('clouds', rainy || [60,61,76].includes(code));
    chk('fog', [83,84,85].includes(code) || (h && +h.value >= 90));
    chk('waves', true);
    // real tropical-cyclone signal from the HKO warning summary
    const tc = stormFromWarn(ws);
    if (tc.dir) { el('winddir').value = tc.dir; setWindDir(tc.dir); }
    el('storm').value = String(tc.level);
    applyStorm(tc.level);
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
    // keep whatever live sync produced: adopt the last live tide level as the manual value
    tideManual = tideLevel; tideSeries = null;
    document.getElementById('tide').value = Math.round(tideManual * 100);
    document.getElementById('tidev').textContent = Math.round(tideManual * 100) + '%';
  }
}
document.getElementById('livebtn').addEventListener('click', () => setLiveMode(!liveMode));
document.getElementById('reset').addEventListener('click', frameCamera);
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
document.getElementById('stations').addEventListener('change', e => setStations(e.target.checked));
// HKS-7: include HKO's wind/marine-only stations (checked) vs temperature stations only
document.getElementById('stationswind').addEventListener('change', e => {
  stationsTempOnly = !e.target.checked;
  if (stationsOn && stationMarkers.length) { applyStationReadings(lastStationReadings); updateStations(); }
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
document.getElementById('aqhi').addEventListener('change', e => setAqhi(e.target.checked));
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
  updateLabels();
  updateLandmarks();
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
  p.set('ve', g('ve').value);
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
  if (p.has('sp')) setVal('spindir', p.get('sp'));
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
  restoring = false;
}

const shareUrl = () => location.origin + location.pathname + '?' + serializeState();

document.getElementById('copylink').addEventListener('click', async e => {
  const btn = e.currentTarget, label = btn.textContent;
  const url = shareUrl();
  try { await navigator.clipboard.writeText(url); btn.textContent = t('share.copied'); }
  catch (_) { history.replaceState(null, '', '?' + serializeState()); btn.textContent = 'In address bar'; }
  setTimeout(() => { btn.textContent = label; }, 1400);
});

// ---- share (HKS-26) --------------------------------------------------------
// Touch devices with the Web Share API → the native OS sheet (WhatsApp / X /
// Threads / … from installed apps). Desktop → an explicit per-network menu.
const shareMenu = document.getElementById('sharemenu');
function shareLink(target) {
  const url = shareUrl(), text = t('share.text'), e = encodeURIComponent;
  const links = {
    wa: `https://wa.me/?text=${e(text + ' ' + url)}`,
    x:  `https://twitter.com/intent/tweet?text=${e(text)}&url=${e(url)}`,
    th: `https://www.threads.net/intent/post?text=${e(text + ' ' + url)}`,
  };
  if (links[target]) window.open(links[target], '_blank', 'noopener,noreferrer');
}
document.getElementById('sharebtn').addEventListener('click', () => {
  const preferNative = navigator.share && matchMedia('(pointer: coarse)').matches;
  if (preferNative) {
    navigator.share({ title: t('share.title'), text: t('share.text'), url: shareUrl() })
      .catch(() => { shareMenu.style.display = ''; });   // cancelled / unsupported → show the menu
  } else {
    shareMenu.style.display = shareMenu.style.display === 'none' ? '' : 'none';
  }
});
document.getElementById('sh-wa').addEventListener('click', () => shareLink('wa'));
document.getElementById('sh-x').addEventListener('click', () => shareLink('x'));
document.getElementById('sh-th').addEventListener('click', () => shareLink('th'));
document.getElementById('sh-copy').addEventListener('click', async e => {
  const btn = e.currentTarget, label = btn.textContent;
  try { await navigator.clipboard.writeText(shareUrl()); btn.textContent = t('share.copied'); }
  catch (_) { history.replaceState(null, '', '?' + serializeState()); }
  setTimeout(() => { btn.textContent = label; }, 1400);
});

// ---- embed (HKS-27): copy-paste <iframe> snippet ---------------------------
// The embed URL carries the current view plus embed=1, which boots map-forward
// (control panel collapsed) so the iframe shows the scene, not the chrome.
function embedSnippet() {
  const url = shareUrl() + (shareUrl().includes('?') ? '&' : '?') + 'embed=1';
  return `<iframe src="${url}" width="800" height="600" style="border:0;border-radius:12px" `
    + `loading="lazy" allow="fullscreen" allowfullscreen title="Hong Kong Sandbox · 香港沙盒"></iframe>`;
}
document.getElementById('sh-embed').addEventListener('click', async e => {
  const btn = e.currentTarget, label = btn.textContent;
  const ta = document.getElementById('embedcode');
  ta.value = embedSnippet();
  ta.style.display = 'block';
  ta.focus(); ta.select();
  try { await navigator.clipboard.writeText(ta.value); btn.textContent = t('share.embedcopied'); }
  catch (_) { /* textarea is shown + selected for manual copy */ }
  setTimeout(() => { btn.textContent = label; }, 1600);
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
  try { localStorage.setItem('locale', locale); } catch (_) {}
  const lb = document.getElementById('langbtn'); if (lb) lb.textContent = isZh() ? 'EN' : '中';
  renderWxviewControls();   // radar/satellite labels are set in JS, refresh them for the new locale
  const md = document.getElementById('meshdensv'); if (md) md.textContent = meshStep === 1 ? t('dens.full') : '÷' + meshStep;
  if (gridW) updateNote();
  updateStormBadge(); applyControlLocks();
  const btn = document.getElementById('livebtn'); if (btn) btn.textContent = liveMode ? t('live.on') : t('live.sync');
  updateViewBtn();   // chase/cockpit label follows the locale
  updateWalkViewBtn();
  if (typeof updateHelp === 'function') updateHelp();   // Help drawer section bodies follow the locale (HKS-86)
  refreshGpsBtn();   // GPS button label/icon follows the locale + state (HKS-86)
  if (stargaze.on) syncSgTray();   // stargaze tray hint/pills follow too
  if (liveMode) { syncLiveWeather(); syncLiveTide(); }
  if (stationsOn) refreshStations();
}
function switchLocale(loc) {
  if (!LOCALES.includes(loc) || loc === locale) return;
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

resize();
applyBg('dark');
locale = detectLocale();
applyLocale(locale);
// Curated default view: a bare visit boots into this scene. Any shared/deep link
// that carries a recognised viewer-state key is honoured verbatim and wins.
// "State" is decided by the canonical key set below — NOT "any unknown key" — so a
// marketing/tracking link (?utm_source=…, ?fbclid=…), a lang-only or embed-only URL
// still lands on the curated default, with its own extra params carried through.
const DEFAULT_STATE = 's=hk-landsd-5m&surf=shaded&bg=dark&ve=2.8&d=1&ml=0&w=1&lb=0&lm=1&L=road&mc=2a4c33&sc=262626&sp=1&ss=0.2&fo=0&ra=0&cl=1&li=0&wv=1&sn=0&mx=0&nn=0&au=0&av=60&su=1&sl=1&sk=1&ti=50&tr=0&st=0&wi=0&wd=N&lv=1&ws=0&wm=0&aq=0&rdr=0&cam=-35853,34284,-26934,0,933,0,1.715';
// canonical serialized keys + the optional ones serializeState only emits sometimes
const STATE_KEYS = new Set([...new URLSearchParams(DEFAULT_STATE).keys(), 'tx', 'sd', 'sm']);
const urlParams = new URLSearchParams(location.search);
const hasState = [...urlParams.keys()].some(k => STATE_KEYS.has(k));
const startParams = hasState ? urlParams : new URLSearchParams(DEFAULT_STATE);
if (!hasState) for (const [k, v] of urlParams) startParams.set(k, v);   // carry locale/embed/utm/etc onto the default
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
  // default to live weather on (unless a shared link explicitly opted out with lv=0)
  if (startParams.has('lv') ? startParams.get('lv') === '1' : true) setLiveMode(true);
  const ld = document.getElementById('loader');           // terrain is in: fade the boot screen
  if (ld) { ld.classList.add('done'); setTimeout(() => ld.remove(), 700); }
}).catch(err => {
  document.getElementById('note').textContent = t('note.loadfail') + ': ' + err.message;
  const ld = document.getElementById('loader');
  if (ld) { ld.classList.add('err'); document.getElementById('loaderstatus').textContent = t('note.loadfail') + ': ' + err.message; }
  console.error(err);
});

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
  const show = () => bar.classList.add('show');

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
      await deferred.userChoice.catch(() => {});
      deferred = null; dismiss();
    });
  }
  addEventListener('appinstalled', dismiss);               // installed → stop nudging
})();

#!/usr/bin/env python3
"""
Extract B50K topographic vector layers from the authoritative Lands Dept GML
(iB50000GML.zip, EPSG:2326) into each DEM region's exact grid frame, so the
vectors align with the terrain by construction.

Why this exists: the legacy overlay was misregistered ~50-80m against the DEM.
The mesh georefs are proven correct (peaks match terrain within metres), so
projecting GML E/N through the same georef guarantees alignment.

GML notes:
- FME-authored GML; features <fme:LAYER>, geometry <gml:posList>.
- posList is (Northing, Easting) order (EPSG:2326 native axis order) -- verified
  against each feature's own EASTING/NORTHING attributes.
- Layer -> content:
    ELEVLINE  contours (HEIGHT attr)
    HYDRLINE  TYPE=COA -> coast ; else -> hydro (rivers/streams)
    TSPTLINE  footpath TYPEs -> trail ; else -> road
    BDRYLINE  boundaries
    TERRLINE  cliffs/relief

Output per region: normalized [u,v] polylines (viewer overlay format) plus a
matching texbb file (the grid's geographic extent), so the same data re-projects
cleanly onto any mesh that shares the region.
"""
import zipfile, re, json, os

HERE = os.path.dirname(__file__)
ZIP = os.path.join(HERE, '../../references/codex/hongkong-3d-model/data/hk-b50k-gml/iB50000GML.zip')
DATA = os.path.join(HERE, '../../3d-viewer/data')

def georef_extent(g):
    E0 = g['bE']; E1 = g['bE'] + g['aE'] * (g['W'] - 1)
    N1 = g['bN']; N0 = g['bN'] + g['aN'] * (g['H'] - 1)   # aN < 0 => N0 < N1
    return E0, E1, N0, N1

# region -> (georef dict, output vectors file, output texbb file)
lantau_g = json.load(open(os.path.join(DATA, 'lantau-georefs.json')))['hk5m']
hk_g = json.load(open(os.path.join(DATA, 'hk-georef.json')))
REGIONS = {
    'lantau': (lantau_g, 'lantau-b50k-vectors.json', 'lantau-texbb.json'),
    'hk':     (hk_g,     'hk-b50k-vectors.json',     'hk-texbb.json'),
}

EPS = 0.015
TRAIL_TYPES = {'FPI', 'FPT', 'FTP', 'FPA', 'FP', 'TRK', 'STE', 'STP', 'FTB'}
FEAT_RE = re.compile(r'<gml:featureMember>(.*?)</gml:featureMember>', re.S)
TYPE_RE = re.compile(r'<fme:TYPE>([^<]*)</fme:TYPE>')
POS_RE  = re.compile(r'<gml:posList>([-\d.\s]+)</gml:posList>')

# read each GML once, cache raw feature (type, [(E,N),...]) lists
def read_layer(entry):
    z = zipfile.ZipFile(ZIP)
    name = {n.split('\\')[-1].upper(): n for n in z.namelist()}[entry.upper()]
    text = z.read(name).decode('utf-8', 'replace')
    feats = []
    for m in FEAT_RE.finditer(text):
        block = m.group(1)
        t = TYPE_RE.search(block); typ = t.group(1) if t else ''
        for pm in POS_RE.finditer(block):
            nums = pm.group(1).split()
            pts = [(float(nums[i+1]), float(nums[i])) for i in range(0, len(nums) - 1, 2)]  # (E,N)
            feats.append((typ, pts))
    return feats

print("Reading GML layers...")
LAYERS = {f: read_layer(f + '.gml') for f in ['ELEVLINE', 'HYDRLINE', 'TSPTLINE', 'BDRYLINE', 'TERRLINE']}

def build_region(g):
    E0, E1, N0, N1 = georef_extent(g)
    def uv(E, N): return ((E - E0) / (E1 - E0), (N1 - N) / (N1 - N0))
    def clip(pts):
        out, run = [], []
        for E, N in pts:
            u, v = uv(E, N)
            if -EPS <= u <= 1 + EPS and -EPS <= v <= 1 + EPS:
                run.append([round(min(1, max(0, u)), 4), round(min(1, max(0, v)), 4)])
            else:
                if len(run) >= 2: out.append(run);
                run = []
        if len(run) >= 2: out.append(run)
        return out
    def collect(entry, splitter):
        res = {}
        for typ, pts in LAYERS[entry]:
            key = splitter(typ)
            if key is None: continue
            for seg in clip(pts):
                res.setdefault(key, []).append(seg)
        return res
    out = {}
    out.update(collect('ELEVLINE', lambda t: 'contour'))
    out.update(collect('HYDRLINE', lambda t: 'coast' if t == 'COA' else 'hydro'))
    out.update(collect('TSPTLINE', lambda t: 'trail' if t in TRAIL_TYPES else 'road'))
    out.update(collect('BDRYLINE', lambda t: 'boundary'))
    out.update(collect('TERRLINE', lambda t: 'cliff'))
    return out, (E0, E1, N0, N1)

for region, (g, vec_file, texbb_file) in REGIONS.items():
    vectors, (E0, E1, N0, N1) = build_region(g)
    json.dump(vectors, open(os.path.join(DATA, vec_file), 'w'), separators=(',', ':'))
    json.dump({'texbb': {'E0': E0, 'E1': E1, 'N0': N0, 'N1': N1}},
              open(os.path.join(DATA, texbb_file), 'w'), indent=1)
    print(f"\n[{region}] -> {vec_file} ({os.path.getsize(os.path.join(DATA, vec_file))/1024:.0f} KB), {texbb_file}")
    for k, v in vectors.items():
        print(f"    {k:9s} {len(v):5d} polylines  {sum(len(s) for s in v):7d} pts")

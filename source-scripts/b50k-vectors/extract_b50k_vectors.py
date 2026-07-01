#!/usr/bin/env python3
"""
Extract B50K topographic vector layers from the authoritative Lands Dept GML
(iB50000GML.zip, EPSG:2326) into the DEM's exact grid frame, so the vectors
align with the terrain by construction.

Why this exists: the legacy contour/coast/trail overlay was misregistered
~50-80m against the DEM. The mesh georef is proven correct (peaks match terrain
within metres), so projecting GML E/N through that same georef guarantees
alignment.

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

Output: normalized [u,v] polylines matching the viewer's overlay format,
u=(E-E0)/(E1-E0), v=(N1-N)/(N1-N0) over the exact mesh grid extent.
"""
import zipfile, re, json, sys, os

ZIP = os.path.join(os.path.dirname(__file__),
    '../../references/codex/hongkong-3d-model/data/hk-b50k-gml/iB50000GML.zip')
GEOREF = os.path.join(os.path.dirname(__file__), '../../3d-viewer/data/lantau-georefs.json')
OUT = os.path.join(os.path.dirname(__file__), '../../3d-viewer/data/lantau-b50k-vectors.json')

g = json.load(open(GEOREF))['hk5m']
E0 = g['bE']; E1 = g['bE'] + g['aE'] * (g['W'] - 1)
N1 = g['bN']; N0 = g['bN'] + g['aN'] * (g['H'] - 1)   # aN < 0, so N0 < N1
EPS = 0.015   # allow a hair outside [0,1] so coastal lines aren't over-clipped

def uv(E, N):
    return ((E - E0) / (E1 - E0), (N1 - N) / (N1 - N0))

def clip_polyline(pts):
    """Split a polyline into runs of points within the (slightly padded) mesh."""
    out, run = [], []
    for u, v in pts:
        if -EPS <= u <= 1 + EPS and -EPS <= v <= 1 + EPS:
            run.append([round(min(1, max(0, u)), 4), round(min(1, max(0, v)), 4)])
        else:
            if len(run) >= 2: out.append(run)
            run = []
    if len(run) >= 2: out.append(run)
    return out

FEAT_RE = re.compile(r'<gml:featureMember>(.*?)</gml:featureMember>', re.S)
TYPE_RE = re.compile(r'<fme:TYPE>([^<]*)</fme:TYPE>')
POS_RE  = re.compile(r'<gml:posList>([-\d.\s]+)</gml:posList>')

def features(entry):
    z = zipfile.ZipFile(ZIP)
    name = {n.split('\\')[-1].upper(): n for n in z.namelist()}[entry.upper()]
    text = z.read(name).decode('utf-8', 'replace')
    for m in FEAT_RE.finditer(text):
        block = m.group(1)
        t = TYPE_RE.search(block)
        typ = t.group(1) if t else ''
        for pm in POS_RE.finditer(block):
            nums = pm.group(1).split()
            # pairs are (N, E)
            pts = [uv(float(nums[i+1]), float(nums[i])) for i in range(0, len(nums) - 1, 2)]
            yield typ, pts

TRAIL_TYPES = {'FPI', 'FPT', 'FTP', 'FPA', 'FP', 'TRK', 'STE', 'STP', 'FTB'}

def collect(entry, splitter):
    layers, types = {}, {}
    for typ, pts in features(entry):
        types[typ] = types.get(typ, 0) + 1
        key = splitter(typ)
        if key is None: continue
        for seg in clip_polyline(pts):
            layers.setdefault(key, []).append(seg)
    return layers, types

result = {}
histos = {}

# contours
l, histos['ELEVLINE'] = collect('ELEVLINE.gml', lambda t: 'contour')
result.update(l)
# hydro + coast
l, histos['HYDRLINE'] = collect('HYDRLINE.gml', lambda t: 'coast' if t == 'COA' else 'hydro')
result.update(l)
# roads + trails
l, histos['TSPTLINE'] = collect('TSPTLINE.gml', lambda t: 'trail' if t in TRAIL_TYPES else 'road')
result.update(l)
# boundaries
l, histos['BDRYLINE'] = collect('BDRYLINE.gml', lambda t: 'boundary')
result.update(l)
# cliffs
l, histos['TERRLINE'] = collect('TERRLINE.gml', lambda t: 'cliff')
result.update(l)

json.dump(result, open(OUT, 'w'), separators=(',', ':'))

print("TYPE histograms (per source):")
for f, h in histos.items():
    top = sorted(h.items(), key=lambda x: -x[1])[:12]
    print(f"  {f}: {top}")
print("\nLayers written to", os.path.relpath(OUT))
for k, v in result.items():
    pts = sum(len(s) for s in v)
    print(f"  {k:9s} {len(v):5d} polylines  {pts:7d} pts")
print(f"\nfile size: {os.path.getsize(OUT)/1024:.0f} KB")

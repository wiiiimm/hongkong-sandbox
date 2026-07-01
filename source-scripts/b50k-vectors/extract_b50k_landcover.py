#!/usr/bin/env python3
"""
Extract B50K land-cover + water POLYGONS from the GML into each region's grid
frame, for a clean filled base map (no linework/labels). The viewer rasterises
these to a CanvasTexture, so alignment is exact by construction.

Sources:
  LANDPOLY  land cover: CLASS=VEG (WOO woodland / CUL cultivation / MAN mangrove
            / SWA swamp) and CLASS=BRL barren (SAN sand / MUD mud)
  HYDRPOLY  water bodies (reservoirs, catchwaters, etc.)

Geometry: gml:Surface > PolygonPatch > exterior > LinearRing > posList (N,E).
Output per region: { wood:[ring...], veg:[ring...], barren:[ring...], water:[ring...] }
each ring a list of normalised [u,v] points over the grid extent.
"""
import zipfile, io, re, json, os

HERE = os.path.dirname(__file__)
ZIP = os.path.join(HERE, '../../references/codex/hongkong-3d-model/data/hk-b50k-gml/iB50000GML.zip')
DATA = os.path.join(HERE, '../../3d-viewer/data')

def extent(g):
    return (g['bE'], g['bE'] + g['aE'] * (g['W'] - 1),
            g['bN'] + g['aN'] * (g['H'] - 1), g['bN'])   # E0,E1,N0,N1

lantau_g = json.load(open(os.path.join(DATA, 'lantau-georefs.json')))['hk5m']
hk_g = json.load(open(os.path.join(DATA, 'hk-georef.json')))
REGIONS = {'lantau': (lantau_g, 'lantau-b50k-landcover.json'),
           'hk':     (hk_g,     'hk-b50k-landcover.json')}

POS_RE = re.compile(r'<gml:posList>([-\d.\s]+)</gml:posList>')

def read_polys(entry):
    """Stream a *POLY gml, yielding (CLASS, TYPE, [(E,N),...]) per exterior ring."""
    z = zipfile.ZipFile(ZIP)
    name = {n.split('\\')[-1].upper(): n for n in z.namelist()}[entry.upper()]
    buf, cls, typ = [], '', ''
    with z.open(name) as f:
        for line in io.TextIOWrapper(f, 'utf-8', errors='replace'):
            if '<gml:featureMember>' in line:
                buf, cls, typ = [], '', ''
            buf.append(line)
            if '</gml:featureMember>' in line:
                block = ''.join(buf)
                mc = re.search(r'<fme:CLASS>([^<]*)', block); cls = mc.group(1) if mc else ''
                mt = re.search(r'<fme:TYPE>([^<]*)', block);  typ = mt.group(1) if mt else ''
                for pm in POS_RE.finditer(block):
                    nums = pm.group(1).split()
                    ring = [(float(nums[i+1]), float(nums[i])) for i in range(0, len(nums) - 1, 2)]  # (E,N)
                    if len(ring) >= 3:
                        yield cls, typ, ring

print("Reading LANDPOLY (208MB, streaming)...")
LAND = list(read_polys('LANDPOLY.gml'))
print(f"  {len(LAND)} land rings")
print("Reading HYDRPOLY...")
WATER = [r for _, _, r in read_polys('HYDRPOLY.gml')]
print(f"  {len(WATER)} water rings")

def category(cls, typ):
    if cls == 'VEG': return 'wood' if typ == 'WOO' else 'veg'
    if cls == 'BRL': return 'barren'
    return None

EPS = 0.0012   # min normalised spacing between kept points (~2px at 2048; sub-texel detail is wasted)

def simplify(ring):
    if len(ring) <= 4: return ring
    out = [ring[0]]
    for p in ring[1:-1]:
        dx, dy = p[0]-out[-1][0], p[1]-out[-1][1]
        if dx*dx + dy*dy >= EPS*EPS: out.append(p)
    out.append(ring[-1])
    return out

for region, (g, outfile) in REGIONS.items():
    E0, E1, N0, N1 = extent(g)
    def norm(ring):
        pts = [[round((E - E0) / (E1 - E0), 4), round((N1 - N) / (N1 - N0), 4)] for E, N in ring]
        return simplify(pts)
    def keep(ring):  # keep polygons that touch the region (canvas clips the rest)
        return any(-0.05 <= (E - E0)/(E1 - E0) <= 1.05 and -0.05 <= (N1 - N)/(N1 - N0) <= 1.05 for E, N in ring)
    out = {'wood': [], 'veg': [], 'barren': [], 'water': []}
    for cls, typ, ring in LAND:
        cat = category(cls, typ)
        if cat and keep(ring): out[cat].append(norm(ring))
    for ring in WATER:
        if keep(ring): out['water'].append(norm(ring))
    json.dump(out, open(os.path.join(DATA, outfile), 'w'), separators=(',', ':'))
    sz = os.path.getsize(os.path.join(DATA, outfile)) / 1024
    print(f"[{region}] -> {outfile} ({sz:.0f} KB): " +
          ", ".join(f"{k} {len(v)}" for k, v in out.items()))

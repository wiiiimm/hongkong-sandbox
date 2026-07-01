#!/usr/bin/env python3
"""Bake named Hong Kong mountain peaks (POI labels) for the 3D viewer.

Source: OpenStreetMap, queried via Overpass for `natural=peak` nodes in the HK
bounding box (see overpass_peaks.json — the raw response). We keep peaks with a
name and an elevation >= MIN_ELE, split English / Chinese names, project WGS84
lat/lon to the Hong Kong 1980 Grid (EPSG:2326, same datum as the terrain), and
emit 3d-viewer/data/hk-peaks.json. The viewer places each by E/N via the current
georef (so one file serves all sources) and shows name + height.

Re-query the raw data with:
  curl --data-urlencode 'data=[out:json][timeout:80];node["natural"="peak"]["name"](22.15,113.82,22.58,114.45);out;' \
       https://overpass-api.de/api/interpreter -o overpass_peaks.json
"""
import json, math, os

MIN_ELE = 200.0          # metres — notable peaks; the viewer declutters further by prominence/zoom
DEDUP_M = 120.0          # merge same-named peaks within this distance (duplicate OSM nodes)

# --- Hong Kong 1980 Grid transverse-Mercator forward (International 1924) -----
A, INV_F = 6378388.0, 297.0
F = 1.0 / INV_F; E2 = F * (2 - F)
LAT0 = math.radians(22 + 18/60 + 43.68/3600)
LON0 = math.radians(114 + 10/60 + 42.80/3600)
FE, FN, K0 = 836694.05, 819069.80, 1.0

def meridian_arc(lat):
    e2, e4, e6 = E2, E2*E2, E2*E2*E2
    return A * ((1 - e2/4 - 3*e4/64 - 5*e6/256) * lat
                - (3*e2/8 + 3*e4/32 + 45*e6/1024) * math.sin(2*lat)
                + (15*e4/256 + 45*e6/1024) * math.sin(4*lat)
                - (35*e6/3072) * math.sin(6*lat))

def to_hk1980(lat_deg, lon_deg):
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    ep2 = E2 / (1 - E2)
    sl, cl, tl = math.sin(lat), math.cos(lat), math.tan(lat)
    nu = A * K0 / math.sqrt(1 - E2 * sl*sl)
    T, C, Aa = tl*tl, ep2 * cl*cl, (lon - LON0) * cl
    M, M0 = meridian_arc(lat), meridian_arc(LAT0)
    E = FE + K0*nu*(Aa + (1-T+C)*Aa**3/6 + (5-18*T+T*T+72*C-58*ep2)*Aa**5/120)
    N = FN + K0*(M - M0 + nu*tl*(Aa*Aa/2 + (5-T+9*C+4*C*C)*Aa**4/24
                 + (61-58*T+T*T+600*C-330*ep2)*Aa**6/720))
    return E, N

def is_cjk(s): return any('一' <= ch <= '鿿' for ch in (s or ''))

here = os.path.dirname(__file__)
raw = json.load(open(os.path.join(here, 'overpass_peaks.json')))
out = []
for e in raw.get('elements', []):
    tg = e.get('tags', {})
    name = tg.get('name')
    if not name or 'lat' not in e or 'lon' not in e:
        continue
    try:
        ele = float(tg.get('ele', ''))
    except ValueError:
        continue
    if ele < MIN_ELE:
        continue
    zh = tg.get('name:zh-Hant') or tg.get('name:zh') or (name if is_cjk(name) else '')
    en = tg.get('name:en') or (name if name.isascii() else '')
    if not en and not zh:
        continue
    E, N = to_hk1980(e['lat'], e['lon'])
    out.append({"en": en.strip(), "zh": zh.strip(), "E": round(E, 1), "N": round(N, 1), "ele": round(ele)})

# dedup same-named peaks that sit within DEDUP_M (duplicate nodes) — keep the higher
out.sort(key=lambda p: -p['ele'])
kept = []
for p in out:
    dup = next((q for q in kept if (q['en'], q['zh']) == (p['en'], p['zh'])
                and math.hypot(q['E']-p['E'], q['N']-p['N']) < DEDUP_M), None)
    if not dup:
        kept.append(p)

dst = os.path.abspath(os.path.join(here, '..', '..', '3d-viewer', 'data', 'hk-peaks.json'))
json.dump({"note": "named HK peaks from OpenStreetMap (natural=peak), HK1980 grid",
           "min_ele_m": MIN_ELE, "count": len(kept), "peaks": kept},
          open(dst, 'w'), ensure_ascii=False, separators=(',', ':'))
print(f"wrote {len(kept)} peaks (>= {MIN_ELE:.0f} m) -> {dst}")
for p in kept[:8]:
    print(f"  {p['ele']:>4} m  {p['zh'] or '—':<8} {p['en']}")

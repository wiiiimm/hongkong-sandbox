#!/usr/bin/env python3
"""Bake a small curated set of Hong Kong landmarks (POI labels) for the viewer.

A hand-picked orientation layer — the tallest / most iconic hiking peaks plus the
towns people know — separate from the full named-peaks layer. WGS84 lat/lon
(approximate, public) projected to the Hong Kong 1980 Grid (EPSG:2326, same datum
as the terrain) -> 3d-viewer/data/hk-landmarks.json. The viewer places each by
E/N via the current georef, so one file serves every source.
"""
import json, math, os

# name: (lat, lon, zh, kind, ele_m|None)
LANDMARKS = {
    # iconic / popular hiking peaks (includes the tallest)
    "Tai Mo Shan":     (22.4103, 114.1244, "大帽山", "peak", 957),
    "Lantau Peak":     (22.2456, 113.9098, "鳳凰山", "peak", 934),
    "Sunset Peak":     (22.2600, 113.9440, "大東山", "peak", 869),
    "Ma On Shan":      (22.4022, 114.2497, "馬鞍山", "peak", 702),
    "Pat Sin Leng":    (22.4767, 114.2196, "八仙嶺", "peak", 639),
    "Kowloon Peak":    (22.3369, 114.2247, "飛鵝山", "peak", 602),
    "Castle Peak":     (22.3878, 113.9583, "青山",   "peak", 583),
    "Victoria Peak":   (22.2759, 114.1455, "太平山", "peak", 552),
    "Lion Rock":       (22.3520, 114.1875, "獅子山", "peak", 495),
    "Sharp Peak":      (22.4197, 114.3667, "蚺蛇尖", "peak", 468),
    "High Junk Peak":  (22.2836, 114.2681, "釣魚翁", "peak", 344),
    # towns / districts
    "Central":         (22.2819, 114.1582, "中環",   "town", None),
    "Tsim Sha Tsui":   (22.2970, 114.1722, "尖沙咀", "town", None),
    "Tai Po":          (22.4501, 114.1642, "大埔",   "town", None),
    "Fanling":         (22.4922, 114.1386, "粉嶺",   "town", None),
    "Tseung Kwan O":   (22.3076, 114.2600, "將軍澳", "town", None),
    "Yuen Long":       (22.4445, 114.0225, "元朗",   "town", None),
    "Mui Wo":          (22.2660, 113.9967, "梅窩",   "town", None),
    "Tai O":           (22.2540, 113.8620, "大澳",   "town", None),
}

# --- Hong Kong 1980 Grid transverse-Mercator forward (International 1924) -----
A = 6378388.0; F = 1.0 / 297.0; E2 = F * (2 - F)
LAT0 = math.radians(22 + 18/60 + 43.68/3600)
LON0 = math.radians(114 + 10/60 + 42.80/3600)
FE, FN, K0 = 836694.05, 819069.80, 1.0

def meridian_arc(lat):
    e2, e4, e6 = E2, E2*E2, E2*E2*E2
    return A * ((1 - e2/4 - 3*e4/64 - 5*e6/256)*lat - (3*e2/8 + 3*e4/32 + 45*e6/1024)*math.sin(2*lat)
                + (15*e4/256 + 45*e6/1024)*math.sin(4*lat) - (35*e6/3072)*math.sin(6*lat))

def to_hk1980(lat_deg, lon_deg):
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    ep2 = E2 / (1 - E2); sl, cl, tl = math.sin(lat), math.cos(lat), math.tan(lat)
    nu = A * K0 / math.sqrt(1 - E2*sl*sl); T, C, Aa = tl*tl, ep2*cl*cl, (lon - LON0)*cl
    M, M0 = meridian_arc(lat), meridian_arc(LAT0)
    E = FE + K0*nu*(Aa + (1-T+C)*Aa**3/6 + (5-18*T+T*T+72*C-58*ep2)*Aa**5/120)
    N = FN + K0*(M - M0 + nu*tl*(Aa*Aa/2 + (5-T+9*C+4*C*C)*Aa**4/24
                 + (61-58*T+T*T+600*C-330*ep2)*Aa**6/720))
    return E, N

out = []
for en, (lat, lon, zh, kind, ele) in LANDMARKS.items():
    E, N = to_hk1980(lat, lon)
    d = {"en": en, "zh": zh, "kind": kind, "E": round(E, 1), "N": round(N, 1)}
    if ele is not None:
        d["ele"] = ele
    out.append(d)

dst = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '3d-viewer', 'data', 'hk-landmarks.json'))
json.dump({"note": "curated HK landmarks (iconic peaks + towns), HK1980 grid — approximate public coordinates",
           "count": len(out), "landmarks": out}, open(dst, 'w'), ensure_ascii=False, separators=(',', ':'))
print(f"wrote {len(out)} landmarks -> {dst}")

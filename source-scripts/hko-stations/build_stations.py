#!/usr/bin/env python3
"""Bake HKO automatic-weather-station positions for the 3D viewer.

The HKO open-data feeds (rhrread JSON + the regional-weather CSVs) carry the
station *readings* but not their coordinates, and HKO serves no machine-readable
position file. So we curate WGS84 lat/lon for each station from public records
and project them to the Hong Kong 1980 Grid (EPSG:2326) — the same datum the
terrain meshes are georeferenced in — so the runtime can drop each marker with
the existing georef (col = (E-bE)/aE, row = (N-bN)/aN).

Coordinates are approximate (public place positions, ~100 m); they are meant for
plotting station markers on a ~50 km regional map, not survey use. Placement is
cross-checked visually against the coastline in the viewer.

Names match the regional-weather CSV `Automatic Weather Station` column so live
readings join by name. Output: 3d-viewer/data/hko-stations.json
"""
import json, math, os

# --- WGS84 lat/lon (approximate, public) keyed by regional-CSV station name ---
STATIONS = {
    "Central Pier":                (22.2875, 114.1600),
    "Chek Lap Kok":                (22.3090, 113.9220),
    "Cheung Chau":                 (22.2010, 114.0270),
    "Cheung Chau Beach":           (22.2100, 114.0250),
    "Clear Water Bay":             (22.2640, 114.3000),
    "Green Island":                (22.2830, 114.1110),
    "HK Observatory":              (22.3019, 114.1741),
    "HK Park":                     (22.2770, 114.1620),
    "Happy Valley":                (22.2710, 114.1830),
    "Hong Kong Sea School":        (22.2230, 114.2170),
    "Kai Tak":                     (22.3080, 114.2000),
    "Kai Tak Runway Park":         (22.3060, 114.2130),
    "Kau Sai Chau":                (22.3620, 114.3120),
    "King's Park":                 (22.3120, 114.1720),
    "Kowloon City":                (22.3280, 114.1880),
    "Kwun Tong":                   (22.3160, 114.2250),
    "Lamma Island":                (22.2100, 114.1310),
    "Lau Fau Shan":                (22.4680, 113.9840),
    "Ngong Ping":                  (22.2560, 113.9110),
    "North Point":                 (22.2910, 114.2000),
    "Pak Tam Chung":               (22.4020, 114.3260),
    "Peng Chau":                   (22.2900, 114.0430),
    "Sai Kung":                    (22.3760, 114.2740),
    "Sha Chau":                    (22.3510, 113.9010),
    "Sha Tin":                     (22.4020, 114.2100),
    "Sham Shui Po":                (22.3350, 114.1620),
    "Shau Kei Wan":                (22.2790, 114.2290),
    "Shek Kong":                   (22.4360, 114.0850),
    "Sheung Shui":                 (22.5020, 114.1130),
    "Stanley":                     (22.2180, 114.2130),
    "Star Ferry":                  (22.2940, 114.1690),
    "Ta Kwu Ling":                 (22.5280, 114.1560),
    "Tai Lung":                    (22.4900, 114.1180),
    "Tai Mei Tuk":                 (22.4750, 114.2380),
    "Tai Mo Shan":                 (22.4100, 114.1240),
    "Tai Po":                      (22.4460, 114.1740),
    "Tai Po Kau":                  (22.4300, 114.1840),
    "Tap Mun":                     (22.4710, 114.3600),
    "Tate's Cairn":                (22.3580, 114.2170),
    "The Peak":                    (22.2710, 114.1450),
    "Tseung Kwan O":               (22.3170, 114.2600),
    "Tsing Yi":                    (22.3450, 114.1100),
    "Tsuen Wan Ho Koon":           (22.3840, 114.1080),
    "Tsuen Wan Shing Mun Valley":  (22.3730, 114.1230),
    "Tuen Mun":                    (22.3900, 113.9740),
    "Waglan Island":               (22.1817, 114.3030),
    "Wetland Park":                (22.4670, 114.0070),
    "Wong Chuk Hang":              (22.2480, 114.1720),
    "Wong Tai Sin":                (22.3420, 114.1940),
    "Yuen Long Park":              (22.4450, 114.0250),
}

# --- Hong Kong 1980 Grid transverse-Mercator forward (International 1924) -----
A = 6378388.0            # semi-major axis (Hayford / International 1924)
INV_F = 297.0
F = 1.0 / INV_F
E2 = F * (2 - F)
LAT0 = math.radians(22 + 18/60 + 43.68/3600)     # 22.312133 N
LON0 = math.radians(114 + 10/60 + 42.80/3600)    # 114.178556 E
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
    sin_l, cos_l, tan_l = math.sin(lat), math.cos(lat), math.tan(lat)
    nu = A * K0 / math.sqrt(1 - E2 * sin_l*sin_l)
    T = tan_l*tan_l
    C = ep2 * cos_l*cos_l
    Aa = (lon - LON0) * cos_l
    M, M0 = meridian_arc(lat), meridian_arc(LAT0)
    E = FE + K0*nu*(Aa + (1-T+C)*Aa**3/6 + (5-18*T+T*T+72*C-58*ep2)*Aa**5/120)
    N = FN + K0*(M - M0 + nu*tan_l*(Aa*Aa/2 + (5-T+9*C+4*C*C)*Aa**4/24
                 + (61-58*T+T*T+600*C-330*ep2)*Aa**6/720))
    return E, N

# --- optional Chinese names from the public hk0weather registry --------------
ZH = {}
reg = os.path.join(os.path.dirname(__file__), 'hko_stations.json')
if os.path.exists(reg):
    for v in json.load(open(reg)).values():
        ZH[v['english_name']] = v.get('chinese_name', '')

def zh_for(name):
    if name in ZH: return ZH[name]
    alt = {'HK Observatory': 'Hong Kong Observatory', 'HK Park': 'Hong Kong Park'}.get(name)
    return ZH.get(alt, '')

out = []
for name, (lat, lon) in sorted(STATIONS.items()):
    E, N = to_hk1980(lat, lon)
    out.append({"name": name, "zh": zh_for(name), "lat": round(lat, 4),
                "lon": round(lon, 4), "E": round(E, 1), "N": round(N, 1)})

dst = os.path.join(os.path.dirname(__file__), '..', '..', '3d-viewer', 'data', 'hko-stations.json')
json.dump({"note": "approximate public station coordinates, HK1980 grid via TM projection",
           "count": len(out), "stations": out},
          open(os.path.abspath(dst), 'w'), ensure_ascii=False, indent=0)
print(f"wrote {len(out)} stations -> {os.path.abspath(dst)}")
# sanity anchors
for a in ("HK Observatory", "Chek Lap Kok", "Waglan Island", "Sha Tin"):
    E, N = to_hk1980(*STATIONS[a])
    print(f"  {a:16s} E={E:9.1f} N={N:9.1f}")

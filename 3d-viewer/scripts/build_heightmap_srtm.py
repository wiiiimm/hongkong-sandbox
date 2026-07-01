#!/usr/bin/env python3
"""
build_heightmap.py
------------------
Turn the assembled Lantau DEM (elev.npy, from assemble_dem.py) into the compact
heightmap JSON that the 3D viewer embeds.

  1. Load the metre-elevation grid.
  2. Keep ONLY the connected land component containing the highest point
     (Lantau Peak) -> isolates Lantau, drops other islands.
  3. Downsample to ~360 columns and zero the sea.
  4. Map labelled peaks/towns (lon -> grid column) for on-screen markers.
  5. Write data/heightmap.json.

Requires numpy + scipy. Run from the folder holding elev.npy + extent.txt.
"""
import numpy as np, json, os
from scipy.ndimage import zoom, gaussian_filter, label

ext = open("extent.txt").read().split()          # lonL lonR latT latB W H Z
lonL, lonR = float(ext[0]), float(ext[1]); Wfull = int(ext[4])

elev = np.load("elev.npy")
elev = np.where(elev < -50, 0, elev); elev = np.clip(elev, 0, None)

land = elev > 5.0
lab, n = label(land)
yi, xi = np.unravel_index(np.argmax(elev), elev.shape)
lantau = lab == lab[yi, xi]

rows = np.where(lantau.any(axis=1))[0]; cols = np.where(lantau.any(axis=0))[0]
r0, r1, c0, c1 = rows.min(), rows.max(), cols.min(), cols.max()
E = np.where(lantau, elev, 0.0)[r0:r1+1, c0:c1+1]
M = lantau[r0:r1+1, c0:c1+1]
E = gaussian_filter(E, 1.5)

TW = 360; f = TW / E.shape[1]
Ed = zoom(E, f, order=1); Md = zoom(M.astype(float), f, order=1) > 0.4
Ed = np.where(Md, Ed, 0.0); h, w = Ed.shape
cell = 8.8 / f                                    # metres per cell (z14 ~8.8 m/px)

def col_of(lon):
    full = (lon - lonL) / (lonR - lonL) * Wfull
    return int(round((full - c0) * f))

features = [
    ("Lantau Peak 鳳凰山", 113.9205, 934), ("Sunset Peak 大東山", 113.9535, 869),
    ("Yi Tung Shan 二東山", 113.9625, 747), ("Lin Fa Shan 蓮花山", 113.9745, 766),
    ("Lo Fu Tau 老虎頭", 114.0125, 465), ("Tai O 大澳", 113.8625, 4),
    ("Mui Wo 梅窩", 113.9985, 6), ("Discovery Bay 愉景灣", 114.0225, 12),
]
peaks = []
for nm, lon, hm in features:
    c = col_of(lon)
    if 0 <= c < w:
        win = Ed[:, max(0, c-3):c+4]; r = int(np.argmax(win.max(axis=1)))
        peaks.append({"name": nm, "col": c, "row": r, "elev": hm})

data = {"w": w, "h": h, "cell": round(cell, 2), "zmax": float(Ed.max()),
        "elev": [int(round(v)) for v in Ed.flatten().tolist()], "peaks": peaks}
os.makedirs("data", exist_ok=True)
json.dump(data, open("data/heightmap.json", "w"))
print(f"heightmap {w}x{h}  cell~{cell:.1f} m  zmax {Ed.max():.0f} m  peaks {len(peaks)}")

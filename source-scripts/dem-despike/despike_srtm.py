#!/usr/bin/env python3
"""
Remove isolated elevation spikes from AWS Terrarium (SRTM) DEM meshes.

Terrarium tiles occasionally carry a single garbage-high pixel that renders as a
needle. A real summit vertex is never far above ALL its neighbours (terrain is
gradual); a vertex that towers over its highest neighbour by > THRESH is an
artifact. Replace each such vertex with the median of its 8 neighbours.

LandsD 5m LiDAR meshes are clean and are not processed here.
"""
import json, os, statistics

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../../3d-viewer/data')
FILES = ['hk-srtm.json', 'lantau-srtm30.json']
THRESH = 40.0   # metres above the highest neighbour to count as a spike

for f in FILES:
    path = os.path.join(DATA, f)
    d = json.load(open(path)); W, H, e = d['w'], d['h'], d['elev']
    fixed = 0
    for _pass in range(3):                       # a couple of passes for any clusters
        pass_fixed = 0
        for r in range(1, H - 1):
            for c in range(1, W - 1):
                i = r * W + c; v = e[i]
                nb = [e[(r+dr)*W+(c+dc)] for dr in (-1,0,1) for dc in (-1,0,1) if not (dr == 0 and dc == 0)]
                if v - max(nb) > THRESH:
                    e[i] = statistics.median(nb); pass_fixed += 1
        fixed += pass_fixed
        if pass_fixed == 0: break
    old_max = d.get('zmax', max(e)); d['zmax'] = max(e)
    json.dump(d, open(path, 'w'), separators=(',', ':'))
    print(f"{f}: despiked {fixed} vertices; max elev {old_max:.0f} -> {d['zmax']:.0f} m")

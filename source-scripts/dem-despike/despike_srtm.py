#!/usr/bin/env python3
"""
Remove spikes AND pits from AWS Terrarium (SRTM) DEM meshes.

Terrarium tiles carry isolated garbage pixels (needles) and holes (pits, often
0 m surrounded by land), sometimes in 2-cell clusters. A median filter is robust
to both and to small clusters: replace any vertex whose value deviates from the
median of its neighbours by more than THRESH.

This does NOT flatten real summits: on a smooth slope or a broad peak the vertex
sits near its neighbours' median (small deviation); only isolated artefacts
deviate strongly. We verify named peaks are preserved after filtering.

LandsD 5m LiDAR meshes are clean and are not processed here.
"""
import json, os, statistics

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '../../3d-viewer/data')
FILES = ['hk-srtm.json', 'lantau-srtm30.json']
THRESH = 45.0     # metres deviation from neighbour median to count as an artefact
PASSES = 4

def neighbours(e, W, H, r, c):
    return [e[(r+dr)*W+(c+dc)] for dr in (-1,0,1) for dc in (-1,0,1)
            if not (dr == 0 and dc == 0) and 0 <= r+dr < H and 0 <= c+dc < W]

for f in FILES:
    path = os.path.join(DATA, f)
    d = json.load(open(path)); W, H, e = d['w'], d['h'], d['elev']
    # sample named peaks before, to prove we don't damage them
    def sample(col, row, arr):
        c0, r0 = int(col), int(row); fc, fr = col-c0, row-r0
        c1, r1 = min(c0+1, W-1), min(r0+1, H-1)
        a, b = arr[r0*W+c0], arr[r0*W+c1]; c, dd = arr[r1*W+c0], arr[r1*W+c1]
        return (a*(1-fc)+b*fc)*(1-fr) + (c*(1-fc)+dd*fc)*fr
    before = [(pk['name'], sample(pk['col'], pk['row'], e)) for pk in d.get('peaks', [])]

    total = 0
    for _ in range(PASSES):
        nxt = list(e); changed = 0
        for r in range(H):
            for c in range(W):
                nb = neighbours(e, W, H, r, c)
                if len(nb) < 3: continue
                med = statistics.median(nb)
                if abs(e[r*W+c] - med) > THRESH:
                    nxt[r*W+c] = med; changed += 1
        e = nxt; total += changed
        if changed == 0: break
    d['elev'] = e
    old_max = d.get('zmax'); d['zmax'] = max(e)
    json.dump(d, open(path, 'w'), separators=(',', ':'))

    print(f"\n{f}: filtered {total} vertices; max {old_max:.0f} -> {d['zmax']:.0f} m")
    worst = max((abs(sample(pk['col'], pk['row'], e) - b) for (nm, b), pk in zip(before, d.get('peaks', []))), default=0)
    print(f"   named-peak change: max |Δ| = {worst:.1f} m (should be ~0)")

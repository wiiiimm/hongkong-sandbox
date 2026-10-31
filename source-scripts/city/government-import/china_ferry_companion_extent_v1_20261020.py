"""Source-only diagrams and full projection measurements for two companion exceptions."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
SRC = BASE / 'government-xl-china-ferry-five-original-identity-v2-20261020'
NEIGH = BASE / 'government-xl-china-ferry-current-neighbours-v1-20261020'
PRIMARY = BASE / 'government-xl-china-ferry-six-primary-records-v1-20261020'
BATCH = 'government-xl-china-ferry-companion-extent-v1-20261020'
DOC = BASE / BATCH
assert not DOC.exists()
pins = {}
refs = [Path(__file__), HERE / 'exact_packed_world_geometry_20261009.py']
with connect() as db:
    db.execute('SET TRANSACTION READ ONLY')
    for folder in (SRC, NEIGH, PRIMARY):
        r = read(folder / 'result.json')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',
                          (r['jobId'],)).fetchone() == ('complete', r)
        refs.append(folder / 'result.json')
        for e in r['evidenceRefs']:
            assert e['path'] not in pins or pins[e['path']] == e['sha256']
            pins[e['path']] = e['sha256']
for p, h in pins.items():
    assert digest((ROOT / p).read_bytes()) == h, p
rows = read(SRC / 'selection.json.gz')['rows']
forms = {x['building']['uid']: x['building']
         for x in read(NEIGH / 'neighbour-inputs.json.gz')['rows']}
ancillary = Polygon(forms['landsd/81118:0']['rings'][0])
podium = Polygon(forms['landsd/285642:0']['rings'][0])
DOC.mkdir()
summaries = []
for uid in ['landsd/238208:0', 'landsd/252498:0']:
    row = next(r for r in rows if r['uid'] == uid)
    raw = (ROOT / row['candidate']['path']).read_bytes()
    assert digest(raw) == row['sourceSHA256']
    t = decode_original_world_triangles(raw)
    polys = shapely.polygons(t[:, :, [0, 2]])
    projection = shapely.union_all(polys)
    target = Polygon(forms[uid]['rings'][0])
    intersections = shapely.intersection(polys, ancillary)
    hits = np.flatnonzero(shapely.area(intersections) > 1e-8)
    summary = dict(
        uid=uid, sourceSHA256=row['sourceSHA256'], completeFaces=len(t),
        targetAreaM2=target.area, targetCoverage=target.intersection(projection).area/target.area,
        missingTargetAreaM2=target.difference(projection).area,
        excessAreaM2=projection.difference(target).area,
        sourceCoveredByPodiumFraction=projection.intersection(podium).area/projection.area,
        ancillaryAreaM2=ancillary.area,
        ancillaryCoverage=ancillary.intersection(projection).area/ancillary.area,
        ancillaryIntersectingFaces=hits.tolist(),
        ancillaryFaceHeightRange=[float(t[hits, :, 1].min()), float(t[hits, :, 1].max())] if len(hits) else None,
        installationApproved=False)
    save(DOC / (uid.split('/')[1] + '.json'), summary)
    fig = plt.figure(figsize=(14, 7))
    ax = fig.add_subplot(121)
    ax.add_collection(PolyCollection(t[:, :, [0, 2]], facecolors='#c4ced4',
                                    edgecolors='#65747e', linewidths=.15))
    if len(hits):
        ax.add_collection(PolyCollection(t[hits][:, :, [0, 2]],
                                        facecolors='#ee8e43', edgecolors='#a85c22', linewidths=.3))
    for poly, color, label in [(target, '#225ac0', 'Official tower footprint'),
                               (ancillary, '#cc2222', 'Official open-sided footprint')]:
        q = np.asarray(poly.exterior.coords)
        ax.plot(q[:, 0], q[:, 1], color=color, lw=1.3, label=label)
    ax.autoscale()
    ax.set_aspect('equal')
    ax.legend(fontsize=8)
    ax.set_title(forms[uid]['name'] + ': complete source projection')
    ax = fig.add_subplot(122, projection='3d')
    ax.add_collection3d(Poly3DCollection(t[:, :, [0, 2, 1]], facecolor='#bec9d1',
                                       edgecolor='#687985', linewidths=.12, alpha=.85))
    if len(hits):
        ax.add_collection3d(Poly3DCollection(t[hits][:, :, [0, 2, 1]],
                                           facecolor='#ee8e43', edgecolor='#a85c22', linewidths=.3))
    lo, hi = t.min((0, 1)), t.max((0, 1))
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[2], hi[2]); ax.set_zlim(lo[1], hi[1])
    ax.set_box_aspect((hi-lo)[[0, 2, 1]])
    ax.view_init(elev=24, azim=225)
    ax.set_title('Unchanged original; orange intersects open-sided footprint')
    ax.set_zlabel('Height (m)')
    fig.tight_layout()
    fig.savefig(DOC / (uid.split('/')[1] + '.png'), dpi=160)
    plt.close(fig)
    summaries.append(summary)
refs.extend(ROOT / p for p in pins)
module('china_extent_freeze',
       HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
           BATCH, 'original-companion-extent-and-ancillary-context',
           list(dict.fromkeys(refs)),
           dict(uids=[r['uid'] for r in summaries], rows=summaries, installationApproved=False))
print([{k:v for k,v in r.items() if k != 'ancillaryIntersectingFaces'} for r in summaries], flush=True)

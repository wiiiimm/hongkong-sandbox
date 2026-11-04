"""Locate neighbour regressions against complete unchanged source projections."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-neighbour-separation-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)]
def take(n,p):
 _,pins=authenticate(BASE/n);assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
n='government-xl-illumination-form-regression-v1-20261021';fail=take(n,BASE/n/'summary.json')['flagged']
n='government-xl-illumination-regional-scope-v2-20261021';forms={r['uid']:r for r in take(n,BASE/n/'form-obligations.json.gz')}
n='government-xl-illumination-inset-runtime-v1-20261021';runtime=take(n,HERE/'local'/n/'runtime-geometry.json.gz')
projections={}
for r in runtime['rows']:
 tri=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]
 # Includes degenerate projected faces as lines/points, rather than dropping walls.
 parts=[shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in tri]
 projections[r['uid']]=shapely.union_all(parts)
rows=[]
for failed in fail:
 b=forms[failed['uid']];poly=shapely.Polygon(b['rings'][0],b['rings'][1:])
 rows.append(dict(uid=b['uid'],name=b.get('name'),rawRegression=failed,footprintWKT=poly.wkt,sourceRelations=[dict(uid=u,distanceM=float(poly.distance(p)),intersectionAreaM2=float(poly.intersection(p).area),intersects=bool(poly.intersects(p)))for u,p in projections.items()]))
save(DOC/'separation.json',dict(rows=rows,sourceProjectionWKT={u:p.wkt for u,p in projections.items()}))
summary=dict(uids=list(projections),neighbours=len(rows),overlappingNeighbours=[r['uid']for r in rows if any(p['intersects']for p in r['sourceRelations'])],installationApproved=False,scope='Diagnostic full-source projection relation; no neighbour regression waiver or repair.')
module('illumination_separation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-and-regressed-neighbour-projections',refs,summary)
print(rows,flush=True)

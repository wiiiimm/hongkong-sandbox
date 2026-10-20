"""Measure actual overlap polygons; no approval or geometry edits."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-parent-overlap-audit-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-folkland-flatten-native-parent-v1-20261020'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256'] for e in r['evidenceRefs']};p=SRC/'unapproved-complete-parent.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 mesh=read(p)['nativeMesh'];tri=np.asarray(mesh['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];ps=shapely.polygons(tri[:,:,[0,2]]);tree=shapely.STRtree(ps);pairs=tree.query(ps,predicate='intersects');region=shapely.box(372.5,-4027.5,462.5,-3937.5);rows=[];outside=inside=cross=0
 for a,b in zip(*pairs):
  if a>=b:continue
  overlap=ps[a].intersection(ps[b])
  if overlap.area<=1e-10:continue
  local=overlap.intersection(region).area
  kind='outside' if local<=1e-10 else 'inside' if abs(local-overlap.area)<=1e-10 else 'cross-boundary'
  outside+=kind=='outside';inside+=kind=='inside';cross+=kind=='cross-boundary'
  rows.append(dict(faces=[int(a),int(b)],areaM2=overlap.area,localAreaM2=local,location=kind,bounds=list(overlap.bounds)))
 save(DOC/'overlaps.json.gz',dict(rows=rows));summary=dict(uids=['landsd/264677:0','landsd/225387:0'],overlapPairs=len(rows),outsidePairs=outside,insidePairs=inside,crossBoundaryPairs=cross,installationApproved=False,geometryChanges=0,qualification='Diagnostic only. Existing parent overlap approval does not transfer; exact output requires fresh surface evidence.')
 save(DOC/'summary.json',summary);module('folkland_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-parent-overlap-classification',[Path(__file__),SRC/'result.json',p],summary);print(summary,flush=True)
if __name__=='__main__':main()

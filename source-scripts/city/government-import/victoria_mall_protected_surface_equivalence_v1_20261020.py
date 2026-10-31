"""Prove trimming preserves every terrain facet touching complete source/fallback bounds."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-protected-surface-equivalence-v1-20261020';DOC=BASE/BATCH
TRIM=BASE/'government-xl-victoria-mall-trim-unused-margin-v2-20261020';FINAL=BASE/'government-xl-victoria-mall-trimmed-overlap-validation-v1-20261020';BASIC=BASE/'government-xl-victoria-mall-tower-support-v1-20261020';FOUND=BASE/'government-xl-victoria-mall-render-mode-foundations-v1-20261020'
assert not DOC.exists();refs=[Path(__file__),HERE/'native_patch_resolution.py'];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [TRIM,FINAL,BASIC,FOUND]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
def consume(folder,p):
 assert digest(p.read_bytes())==pins[folder.name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
trim=consume(TRIM,TRIM/'summary.json');oldpath=HERE/'local/government-xl-victoria-mall-candidate-terrain-v2-20261020/candidate-terrain.json';old=repair._faces(consume(TRIM,oldpath));new=repair._faces(consume(FINAL,FINAL/'candidate-terrain.json'));bounds=[]
for r in trim['sourceBounds']:
 for i,(lo,hi)in enumerate(r['completeFourWorldBounds']):bounds.append(dict(uid=r['uid'],representation='original-or-render-'+str(i),bounds=[lo,hi]))
for r in consume(BASIC,BASIC/'basic-geometry.json')['rows']:
 p=np.asarray(r['position']).reshape(-1,3);bounds.append(dict(uid=r['uid'],representation='actual-basic-fallback',bounds=[p.min(0).tolist(),p.max(0).tolist()]))
oldpolys=shapely.polygons(old[:,:,[0,2]]);newpolys=shapely.polygons(new[:,:,[0,2]]);oldtree=shapely.STRtree(oldpolys);newtree=shapely.STRtree(newpolys);rows=[]
for b in bounds:
 lo,hi=b['bounds'];assert hi[2]<trim['bounds'][3];region=shapely.box(lo[0],lo[2],hi[0],hi[2]);oi=sorted(map(int,oldtree.query(region,predicate='intersects')));ni=sorted(map(int,newtree.query(region,predicate='intersects')))
 a=sorted(tuple(t.reshape(-1))for t in old[oi]);c=sorted(tuple(t.reshape(-1))for t in new[ni]);assert a==c,('Protected drawn facets differ',b['uid'],b['representation'])
 rows.append(dict(**b,oldFaceIds=oi,newFaceIds=ni,identicalDrawnFacets=len(a),surfaceExactlyUnchanged=True))
f=consume(FOUND,FOUND/'summary.json');assert len(f['rows'])==12 and all(r['passed']and r['buried']==0 for r in f['rows'])
save(DOC/'equivalence.json',dict(rows=rows,allProtectedSurfacesIdentical=True,priorCompleteRenderFoundations=FOUND.name,sourceGeometryChanges=0,installationApproved=False,scope='Every drawn Float32 terrain triangle whose projection intersects the complete source bounding box in four modes, plus each actual BASIC fallback bounding box, is byte-identical. No claim about other actors or the trimmed exterior.'))
module('victoria_surface_equal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-protected-original-and-fallback-ground-equivalence',list(dict.fromkeys(refs)),dict(uids=sorted({r['uid']for r in rows}),representations=len(rows),allProtectedSurfacesIdentical=True,installationApproved=False));print(dict(representations=len(rows),allProtectedSurfacesIdentical=True),flush=True)

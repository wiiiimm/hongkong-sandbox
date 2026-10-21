"""Locate complete original source-ground failures without changing assets."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-buried-face-context-v1-20261021';DOC=BASE/BATCH
SRC=BASE/'government-xl-grandiose-podium-current-terrain-v1-20261021';GROUND=BASE/'government-xl-grandiose-adjoining-ground-v1-20261021'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'china_ferry_current_foundations_v1_20261020.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SRC,GROUND]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 rows=[r for r in take(SRC,SRC/'selection.json.gz')['rows']if r['uid']in ['landsd/246824:0']];assert len(rows)==1
 final=module('two_source_foundation',HERE/'xl-final-script-pass.py');summary=[]
 for row in rows:
  uid=row['uid'];short=uid.split('/')[1];path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path)
  tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==row['source']['building'];refs.append(tile)
  tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles']
  ground=np.asarray(take(GROUND,HERE/'local'/GROUND.name/(short+'-ground.json.gz'))['completeAdjoiningTerrain'])
  prior=take(GROUND,GROUND/(short+'.json'))['foundation'];detail=face_diagnostics(final,tri,ground)
  assert len(detail['buriedFaces'])==prior['fullyBuriedTriangles'] and sum(f['upward']for f in detail['buriedFaces'])==prior['fullyBuriedUpwardTriangles']
  save(DOC/(short+'.json.gz'),dict(uid=uid,sourceSHA256=row['sourceSHA256'],**detail,installationApproved=False))
  flagged=np.asarray([f['vertices']for f in detail['buriedFaces']]);up=np.asarray([f['vertices']for f in detail['buriedFaces']if f['upward']])
  fig,axes=plt.subplots(1,3,figsize=(18,6))
  for ax,coords,label in zip(axes,[(0,2),(0,1),(2,1)],['Plan X/Z','Elevation X/Y','Elevation Z/Y']):
   ax.add_collection(PolyCollection(tri[:,:,coords],facecolors='#cbd5e1',edgecolors='none',alpha=.45))
   ax.add_collection(PolyCollection(flagged[:,:,coords],facecolors='#ef4444',edgecolors='#ef4444',linewidths=.3))
   ax.add_collection(PolyCollection(up[:,:,coords],facecolors='#7e22ce',edgecolors='#7e22ce',linewidths=.5))
   ax.autoscale_view();ax.set_aspect('equal');ax.set_title(label);ax.ticklabel_format(useOffset=False)
  fig.suptitle(uid+' — full original grey; flagged red; upward flagged purple (diagnostic)');fig.tight_layout();fig.savefig(DOC/(short+'.png'),dpi=160);plt.close(fig)
  item=dict(uid=uid,faces=len(tri),buriedFaces=len(flagged),upwardBuriedFaces=len(up),flaggedBounds=[flagged.min((0,1)).tolist(),flagged.max((0,1)).tolist()],upwardBounds=[up.min((0,1)).tolist(),up.max((0,1)).tolist()]);summary.append(item);print(item,flush=True)
 save(DOC/'summary.json',dict(rows=summary,installationApproved=False))
 module('two_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-originals-complete-buried-face-context',refs,dict(uids=[r['uid']for r in rows],rows=summary,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()

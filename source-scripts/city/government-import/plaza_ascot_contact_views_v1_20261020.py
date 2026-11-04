"""Complete flagged contact-face context; diagnostic exports, no approval."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-contact-views-v1-20261020';DOC=BASE/BATCH
CAP=BASE/'government-xl-plaza-ascot-candidate-ground-v2-20261020';SEG=BASE/'government-xl-plaza-ascot-contact-segments-v1-20261020'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,SEG]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 row=take(CAP,HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows'][0];t=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)];ground=np.asarray(row['drawnGroundGeometry']).reshape(-1,3,3);segments=take(SEG,SEG/'segments.json.gz')['rows'];ids=np.array(sorted({r['sourceFace'] for r in segments}));centres=t[ids].mean(1);_,_,axes=np.linalg.svd(centres[:,[0,2]]-centres[:,[0,2]].mean(0),full_matrices=False);order=np.argsort(centres[:,[0,2]]@axes[0]);groups=np.array_split(ids[order],8);DOC.mkdir(parents=True);records=[]
 for n,selected in enumerate(groups,1):
  lo=t[selected].min((0,1))-2;hi=t[selected].max((0,1))+2;origin=lo[[0,2,1]]
  def near(mesh):return np.all(mesh.max(1)>=lo,axis=1)&np.all(mesh.min(1)<=hi,axis=1)
  fig=plt.figure(figsize=(16,8))
  for j,az in enumerate([35,215],1):
   ax=fig.add_subplot(1,2,j,projection='3d')
   for mesh,color,alpha in [(ground[near(ground)],'#6b9e62',.65),(t[near(t)],'#8594a8',.12),(t[selected],'#db472f',.95)]:
    ax.add_collection3d(Poly3DCollection(mesh[:,:,[0,2,1]]-origin,facecolor=color,edgecolor=color,alpha=alpha,linewidth=.15))
   extent=(hi-lo)[[0,2,1]];ax.set_xlim(0,extent[0]);ax.set_ylim(0,extent[1]);ax.set_zlim(0,extent[2]);ax.set_box_aspect(extent);ax.view_init(25,az);ax.set_xlabel('X offset m');ax.set_ylabel('Z offset m');ax.set_zlabel('height offset m')
  fig.suptitle(f'Plaza Ascot contact region {n}: {len(selected)} original faces\nRed: flagged original walls. Green: actual candidate terrain. Grey: original context. Diagnostic only.');fig.tight_layout();fig.savefig(DOC/f'region-{n}.png',dpi=130);plt.close(fig);records.append(dict(region=n,sourceFaceIds=selected.tolist(),bounds=[lo.tolist(),hi.tolist()]));print('rendered',n,flush=True)
 assert sorted(i for r in records for i in r['sourceFaceIds'])==ids.tolist();summary=dict(uids=[row['uid']],contactWitnesses=len(segments),uniqueFaces=len(ids),regions=records,installationApproved=False,allFlaggedFacesAccounted=True);save(DOC/'regions.json',summary);module('ascot_contact_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-flagged-original-contact-face-context',refs,summary)
if __name__=='__main__':main()

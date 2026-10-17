"""Render saved original failure loci; no geometry edits or new acceptance."""
from pathlib import Path
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-buried-context-v1-20261015';DOC=BASE/BATCH
SOURCE=BASE/'government-xl-china-merchants264206-saved-face-attribution-v1-20261013'
def main():
 assert not DOC.exists();r=read(SOURCE/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 resolved=[];historical={};pointer='docs/astra-city/model-integration-20260909/current-source-review.json';want='1ad04f1e75c9d476269000d50921438fb7c119b24e34118419d7ae6a71081914'
 commits=subprocess.check_output(['git','rev-list','--all','--',pointer],cwd=ROOT,text=True).splitlines()
 for commit in commits:
  raw=subprocess.check_output(['git','show',commit+':'+pointer],cwd=ROOT)
  if digest(raw)==want:historical[pointer]=(raw,commit);break
 assert pointer in historical,'Exact historical review pointer not found'
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];raw=p.read_bytes()
  if digest(raw)!=q['sha256']:
   if q['path']==pointer:raw=historical[pointer][0]
   else:
    assert q['path']=='3d-viewer/city/data/manifest.json';raw=(BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013/captured-manifest.json').read_bytes()
   assert digest(raw)==q['sha256'];historical[q['path']]=(raw,historical.get(q['path'],(None,None))[1])
  else:resolved.append(p)
 DOC.mkdir();bindings=[]
 for path,(raw,commit)in historical.items():
  out=DOC/'historical-inputs'/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw);resolved.append(out);bindings.append(dict(originalPath=path,sha256=digest(raw),historicalPath=str(out.relative_to(ROOT)),gitCommit=commit))
 x=read(SOURCE/'source-face-attribution.json.gz');tri=np.asarray(x['completeOriginalSourceFaceVerticesInOrdinalOrder']);assert tri.shape==(19551,3,3)
 runtime=read(HERE/'local/government-xl-retained-group-central-wrapper-20261009-264206-0/runtime-geometry.json.gz')['rows'][0];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3)
 groups=x['failureGroupsInCanonicalDelegateOrder'];rows=[]
 for g in groups:
  ids=g['sourceFaceIndices'];v=tri[ids];rows.append(dict(group=g['delegateOrdinal'],faces=len(ids),upwardFaces=len(g['buriedUpwardSourceFaceIndices']),bounds=[v.min(axis=(0,1)).tolist(),v.max(axis=(0,1)).tolist()],bodies=[a['bodyId']for a in g['intersectionsWithEverySavedDiagnosticComponent']if a['failureGroupSourceFaceIndices']]))
 for angle in [35,215]:
  fig=plt.figure(figsize=(16,12));fig.suptitle('China Merchants: saved original source / historical terrain\nRed = buried faces, orange = upward buried faces; grey = source context; green = terrain. No role inferred.')
  for i,g in enumerate(groups):
   ax=fig.add_subplot(2,3,i+1,projection='3d');ids=g['sourceFaceIndices'];v=tri[ids];lo=v.min(axis=(0,1))-3;hi=v.max(axis=(0,1))+3
   def subset(t):return t[np.all(t.max(axis=1)>=lo,axis=1)&np.all(t.min(axis=1)<=hi,axis=1)]
   for t,color,alpha in [(subset(ground),'#9fbc96',.13),(subset(tri),'#9da4ab',.12),(v,'#d43f3a',.8),(tri[g['buriedUpwardSourceFaceIndices']],'#ffad25',1)]:
    if len(t):ax.add_collection3d(Poly3DCollection(t[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.15,alpha=alpha))
   ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]);ax.view_init(elev=24,azim=angle);ax.set_title(f"Group {i}: {len(ids)} faces / {len(g['buriedUpwardSourceFaceIndices'])} upward");ax.set_xlabel('world X');ax.set_ylabel('world Z');ax.set_zlabel('HKPD Y')
  fig.tight_layout();fig.savefig(DOC/f'failure-context-azimuth-{angle}.png',dpi=130);plt.close(fig)
 save(DOC/'summary.json',dict(uid=x['uid'],sourceSHA256=x['sourceSHA256'],completedSourceAttributionJob=r['jobId'],historicalBindings=bindings,groups=rows,sourceGeometryChanges=0,contextClippedToEachGroupBoundsPlus3Metres=True,imagesAreHistoricalSourceContextOnly=True,physicalAccepted=False,sourceRoleApproved=False))
 paths=resolved+[SOURCE/'result.json',Path(__file__)]
 module('china_context_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'saved-buried-source-loci-visual-context-v1',paths,dict(uids=[x['uid']],fullAcceptance=False,sourceRoleApproved=False,currentAcceptance=False));print('Saved six-group source context, no acceptance',flush=True)
if __name__=='__main__':main()

"""Classify every frozen authored interface exactly; crossing is not a solid proof."""
import importlib.util,json
from collections import Counter
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_finite_contact_crossing_classification_20261011 import classify
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-vancor-two-complete-original-interfaces-v1-20261011'
IDENTITY=BASE/'government-xl-vancor-90824-current-original-identity-v1-20261011'
BATCH='government-xl-vancor-two-original-crossing-classification-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];prior=read(PRIOR/'diagnostic.json.gz');world=[]
 for folder in [PRIOR,IDENTITY]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for p in folder.iterdir():
   if p.is_file():refs.append(p)
 for a in prior['actors']:
  p=ROOT/a['source']['path'];assert ref(p)==a['source'];w=decode_original_world_triangles(p.read_bytes());assert digest(w.tobytes())==a['completeWorldSHA256'];world.append(w);refs.append(p)
 contacts=prior['completeExactAuthoredSourceInterfaces']['contacts'];rows=[]
 for c in contacts:rows.append(dict(sourceFaceA=c['sourceFaceA'],sourceFaceB=c['sourceFaceB'],dimension=c['dimension'],**classify(world[0][c['sourceFaceA']],world[1][c['sourceFaceB']],c)))
 counts=dict(Counter(r['classification']for r in rows));assert len(rows)==894
 raw=read(IDENTITY/'indexed-diagnostic.json')['identity']['freshCurrentIdentity']
 save(DOC/'diagnostic.json.gz',dict(uids=[a['uid']for a in prior['actors']],actors=prior['actors'],allContacts=rows,classificationCounts=counts,
  completeContactCount=len(rows),foreignSourceExcessRaw=raw,sourceGeometryChanges=0,
  priorFieldNameErratum='positiveAreaFacetInterfaceCount counted positive DIMENSIONAL real-facet interfaces, including lines; not positive area alone.',
  strictProperCrossingsRetained=True,volumetricCollisionProved=False,commonNameParentPermitNotOwnershipOrCollisionCredit=True,currentAcceptance=False,installationApproved=False))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,9));ax=fig.add_subplot(projection='3d')
 for w,color in zip(world,['#3478cf','#e5a13f']):ax.add_collection3d(Poly3DCollection(w[:,:,[0,2,1]],facecolors=color,edgecolors='none',alpha=.35))
 proper=[contacts[i]for i,r in enumerate(rows)if r['properTriangleInteriorCrossing']]
 for c in proper:
  p=np.array([[float(__import__('fractions').Fraction(x))for x in q]for q in c['exactPoints']]);ax.plot(p[:,0],p[:,2],p[:,1],color='#b32634',linewidth=.5)
 w=np.concatenate(world);lo=w.min((0,1));hi=w.max((0,1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=22,azim=-130)
 ax.set_xlabel('Viewer east (m)');ax.set_ylabel('Viewer south (m)');ax.set_zlabel('HKPD (m)');ax.set_title('Untouched Vancor originals: blue147956 / gold90824 / red proper facet crossings')
 fig.savefig(DOC/'complete-original-pair-crossings-2400x1800.png',dpi=200);plt.close(fig)
 refs +=[HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_finite_contact_crossing_classification_20261011.py','test_exact_finite_contact_crossing_classification_20261011.py']]
 s=importlib.util.spec_from_file_location('vancor_crossing_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-two-original-exact-relative-interior-contact-classification-source-diagnostic-only',refs,dict(uids=[a['uid']for a in prior['actors']],classificationCounts=counts,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(counts),flush=True)
if __name__=='__main__':main()

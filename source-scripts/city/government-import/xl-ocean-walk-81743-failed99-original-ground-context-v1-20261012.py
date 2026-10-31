"""UNEXECUTED annotated context/record closure only; no new finite proof or role.
Complete original source and captured ground remain unchanged. Provider-original
plots are labelled; all four modes remain in the complete context JSON.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';CAPTURE=BASE/'government-xl-ocean-walk-current-actual-ground-capture-v1-20261012';GRADE=BASE/'government-xl-ocean-walk-complete-four-stream-current-grade-paths-v1-20261012';DRAFT=BASE/'government-xl-ocean-walk-failure-context-draft-v1-20261012'
BATCH='government-xl-ocean-walk-failed99-original-ground-context-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/81743:0';MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
def preflight():
 assert not DOC.exists();receipts=[read(folder/'result.json')for folder in [CAPTURE,GRADE]];assert [r['jobId']for r in receipts]==['736c7affd6c59099c7b7ef45515094d1319959dcb065db613a776f5bce1b3e65','4f3a1119bc56218d3e629f49928f6a80f22134e64ad0006ed643a15049567455']
 refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'all99-source-id-failure-breakdown.json']+[folder/'result.json'for folder in [CAPTURE,GRADE]]
 for r in receipts:
  for pin in r['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 records=read(GRADE/'diagnostic.json.gz');source=read(CAPTURE/'complete-four-stream-ground-inputs.json.gz');breakdown=read(DRAFT/'all99-source-id-failure-breakdown.json');assert breakdown['sourceDiagnosticSHA256']==digest((GRADE/'diagnostic.json.gz').read_bytes())and len(records['rows'])==len(breakdown['rows'])==4
 for row,b in zip(records['rows'],breakdown['rows']):
  assert row['arithmetic']==b['arithmetic']and row['completeWorldSHA256']==b['completeWorldSHA256']and len(row['all15484FiniteRecords'])==15484 and [f['originalSourceFace']for f in b['all99OriginalFailureRecords']]==row['allRawFailedFaces']
  actual_grade={c['sourceFaceA']for c in row['completeFailedSteepGradeContactInventory']['contacts']if c['dimension']>0};assert b['failedSteepWithGenuinePositiveGradeOriginalFaceIDs']==sorted(actual_grade)
  assert all(f['hasGenuinePositiveGradeContacts']==(f['originalSourceFace']in actual_grade)for f in b['all99OriginalFailureRecords'])
  paths={p['sourceFace']:p for p in row['wholeOriginalSharedEdgeAndCapExposure']};component={i:j for j,ids in enumerate(row['completeOriginalTopology']['sharedEdgeConnectedComponents'])for i in ids}
  for f in b['all99OriginalFailureRecords']:
   i=f['originalSourceFace'];p=paths.get(i);assert f['component']==component[i]and f['rawFiniteProofVerbatim']==row['all15484FiniteRecords'][i]['currentDrawnGroundComparison']and f['originalSharedEdgeExposureRecordVerbatim']==p
   assert f['nonemptyOriginalSharedEdgePath']==bool(p and p['interfaces'])and f['everyWholePathInterfaceHasAnExposedEdge']==bool(p and p['interfaces']and p['allPathInterfacesHaveWholeExposedSharedEdge'])
  vacuous=sorted(i for i,p in paths.items()if not p['interfaces']and p['allPathInterfacesHaveWholeExposedSharedEdge']);complete=sorted(i for i,p in paths.items()if p['interfaces']and p['terminalCapWholeFiniteStrictlyClear']and p['allPathInterfacesHaveWholeExposedSharedEdge'])
  assert b['failedNonsteepExcludedOriginalFaceIDs']==[6034,6035]and b['emptyPathVacuousExposureFlagOriginalFaceIDs']==vacuous and len(vacuous)==14 and b['strictTerminalCapAndEveryWholeExposedEdgeOriginalFaceIDs']==complete and len(complete)==15
 return receipts,refs,records,source,breakdown,read(CAPTURE/'capture-inputs.json.gz')['canonicalResources']
def main():
 state=preflight()
 if '--owned'not in sys.argv:
  assert not LOCAL.exists();claim=reservations.claim('ocean-failed99-context-'+str(uuid.uuid4()),state[-1],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True);return
 receipts,refs,records,source,breakdown,resources=state;lease=read(LEASE);assert lease['resources']==resources and reservations.owns(lease);pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 row=next(r for r in records['rows']if r['arithmetic']=='providerOriginal');world=np.asarray(source['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8');ground=np.asarray(source['completeDrawnGround'],dtype='<f8');assert digest(world.tobytes())==row['completeWorldSHA256']and digest(ground.tobytes())==row['completeGroundSHA256'];parts=row['completeOriginalTopology']['sharedEdgeConnectedComponents'];failed=row['allRawFailedFaces'];nonsteep=[6034,6035]
 def panel(ax,ids,title,limits=None):
  # Complete unchanged triangles; limits affect only this explanatory camera.
  t=world[ids];ax.add_collection3d(Poly3DCollection(t,facecolor='#b5c8d9',edgecolor='none',alpha=.5));ax.add_collection3d(Poly3DCollection(ground,facecolor='#b8b19b',edgecolor='#847963',linewidth=.3,alpha=.22))
  wall=[i for i in ids if i in failed and i not in nonsteep];other=[i for i in ids if i in nonsteep]
  if wall:ax.add_collection3d(Poly3DCollection(world[wall],facecolor='#cc432f',edgecolor='#802112',linewidth=.5,alpha=1))
  if other:ax.add_collection3d(Poly3DCollection(world[other],facecolor='#b020b8',edgecolor='#630766',linewidth=1,alpha=1))
  low=t.reshape(-1,3).min(axis=0);high=t.reshape(-1,3).max(axis=0)
  if limits is not None:low,high=limits
  span=np.maximum(high-low,.1);pad=np.maximum(span*.035,.15);lo=low-pad;hi=high+pad;ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(elev=28,azim=-58,vertical_axis='y');ax.set_xlabel('original X / m');ax.set_ylabel('HKPD Y / m');ax.set_zlabel('original Z / m');ax.set_title(title,fontsize=10)
 def finish(fig,name):
  fig.suptitle('Ocean Walk unchanged provider-original source + captured current ground; source context only\nRed: raw steep failures; purple: excluded non-steep6034/6035. No role/root/acceptance.',fontsize=12);fig.tight_layout(rect=[0,0,1,.95]);p=DOC/name;fig.savefig(p,dpi=100);plt.close(fig);return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),width=2400,height=1800,arithmetic='providerOriginal',completeSourceTrianglesUnmodified=True)
 DOC.mkdir();images=[];fig=plt.figure(figsize=(24,18));panel(fig.add_subplot(111,projection='3d'),list(range(15484)),'Complete15484 source facets and all30 captured drawn terrain facets');images.append(finish(fig,'whole-original15484-ground30-2400x1800.png'))
 components=sorted({c for c,ids in enumerate(parts)if set(ids)&set(failed)});assert components==[0,117,227,228,268,269];fig=plt.figure(figsize=(24,18))
 for j,c in enumerate(components):panel(fig.add_subplot(2,3,j+1,projection='3d'),parts[c],f'Complete source component{c}: {len(parts[c])} facets; {len(set(parts[c])&set(failed))} raw failures')
 images.append(finish(fig,'complete-six-affected-source-components-2400x1800.png'))
 low=world[nonsteep].reshape(-1,3).min(axis=0)-2;high=world[nonsteep].reshape(-1,3).max(axis=0)+2;near=[i for i,t in enumerate(world)if np.all(t.max(axis=0)>=low)and np.all(t.min(axis=0)<=high)];fig=plt.figure(figsize=(24,18));panel(fig.add_subplot(121,projection='3d'),parts[0],'Complete10425-facet source component0');ax=fig.add_subplot(122,projection='3d');panel(ax,near,f'Explicit local explanatory crop: all {len(near)} source facets whose closed3D AABB touches ±2m zone',limits=(low,high))
 for i in nonsteep:
  centre=world[i].mean(axis=0);ax.text(*centre,str(i),color='#630766',fontsize=12)
 images.append(finish(fig,'excluded-two-nonsteep-facets-complete-mainbody-and-local-context-2400x1800.png'))
 save(DOC/'context.json.gz',dict(uids=[UID],completedInputJobs=[r['jobId']for r in receipts],fourStreamCompleteFailureBreakdownVerbatim=breakdown,sourceFaceCoordinatesAllFourStreams={mode:{str(i):s['completeWorldTriangles'][i]for i in failed}for mode,s in source['completeWorldStreams'].items()},all6BasicRegressionsRetainedVerbatim=records['sixPriorBasicRegressionsRetainedVerbatim'],all11UnresolvedInterfacesRetainedVerbatim=records['elevenPriorUnresolvedInterfacesRetainedVerbatim'],actualPNGExports=images,renderToolVersion=matplotlib.__version__,sourceRoleInterpretationProposed=False,newFiniteProofComputed=False,currentAcceptance=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in DOC.iterdir()if p.is_file());s=importlib.util.spec_from_file_location('ocean_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original99-failure-context-no-new-role-proof',refs,dict(uids=[UID],all99OriginalFailedFacesRetained=True,rawEmptyPathsUncredited=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
if __name__=='__main__':main()

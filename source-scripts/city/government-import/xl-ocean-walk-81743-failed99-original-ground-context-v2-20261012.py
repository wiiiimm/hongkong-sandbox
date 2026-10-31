"""UNEXECUTED annotated context/record closure only; no new finite proof or role.
Complete original source and captured ground remain unchanged. Provider-original
plots are labelled; all four modes remain in the complete context JSON.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';CAPTURE=BASE/'government-xl-ocean-walk-current-actual-ground-capture-v1-20261012';GRADE=BASE/'government-xl-ocean-walk-complete-four-stream-current-grade-paths-v1-20261012';DRAFT=BASE/'government-xl-ocean-walk-failure-context-draft-v1-20261012';PRIOR=BASE/'government-xl-ocean-walk-failed99-original-ground-context-v1-20261012';METHOD=BASE/'government-xl-ocean-walk-alternate-context-draft-v2-20261012'/'METHOD.md'
BATCH='government-xl-ocean-walk-failed99-original-ground-context-v2-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/81743:0';MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
def preflight():
 assert not DOC.exists();receipts=[read(folder/'result.json')for folder in [CAPTURE,GRADE,PRIOR]];assert [r['jobId']for r in receipts]==['736c7affd6c59099c7b7ef45515094d1319959dcb065db613a776f5bce1b3e65','4f3a1119bc56218d3e629f49928f6a80f22134e64ad0006ed643a15049567455','c875bfcea701dd4c31cb343e4c2f411521a005fb94a7b2c039537080612e0701']
 refs=[Path(__file__),METHOD,DRAFT/'METHOD.md',DRAFT/'all99-source-id-failure-breakdown.json']+[folder/'result.json'for folder in [CAPTURE,GRADE,PRIOR]]
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
 assert read(PRIOR/'context.json.gz')['fourStreamCompleteFailureBreakdownVerbatim']==breakdown
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
 def finish(fig,name):
  fig.suptitle('Ocean Walk provider-original diagnostic source overlays — not visibility/GPU screenshots\n6034/6035: recorded downward-or-sloping nonsteep; unchanged raw failures, no source role/root credit.',fontsize=14)
  fig.tight_layout(rect=[0,0,1,.94]);p=DOC/name;fig.savefig(p,dpi=100);plt.close(fig)
  return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),width=2400,height=1800,arithmetic='providerOriginal',completeSourceTrianglesUnmodified=True,diagnosticOverlayNotVisibilityProof=True)
 low=world[nonsteep].reshape(-1,3).min(axis=0)-2;high=world[nonsteep].reshape(-1,3).max(axis=0)+2
 near=[i for i,t in enumerate(world)if np.all(t.max(axis=0)>=low)and np.all(t.min(axis=0)<=high)];assert len(near)==105 and set(nonsteep)<=set(near)
 target_records={str(f['originalSourceFace']):f for f in breakdown['rows'][0]['all99OriginalFailureRecords']if f['originalSourceFace']in nonsteep}
 exact={str(i):{'orientationDiagnosticVerbatim':target_records[str(i)]['exactOrientationDiagnosticVerbatim'],'verticesXYZDecimalRoundTrip':world[i].tolist(),'verticesXYZExactDyadic':[[str(int(n))+'/'+str(int(d))for n,d in [float(x).as_integer_ratio()for x in v]]for v in world[i]]}for i in nonsteep}
 assert all(v['orientationDiagnosticVerbatim']=='downward-or-sloping-nonsteep'for v in exact.values())
 DOC.mkdir();images=[];fig=plt.figure(figsize=(24,18))
 for j,i in enumerate(nonsteep):
  ax=fig.add_subplot(2,2,j+1,projection='3d');t=world[i];ax.add_collection3d(Poly3DCollection([t],facecolor='#d000bd',edgecolor='#650066',linewidth=2,alpha=.8))
  lo=t.min(axis=0)-.15;hi=t.max(axis=0)+.15;ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(hi-lo);ax.view_init(elev=28,azim=-58,vertical_axis='y');ax.set_xlabel('original X / m');ax.set_ylabel('HKPD Y / m');ax.set_zlabel('original Z / m');ax.set_title(f'Original face {i} alone; recorded downward-or-sloping nonsteep',fontsize=13)
  for k,v in enumerate(t):ax.text(*v,f'{i}:v{k}',fontsize=13,color='#650066')
  tx=fig.add_subplot(2,2,j+3);tx.axis('off');lines=[f'Original face {i}; untouched vertex order X,Y,Z','Recorded orientation: downward-or-sloping-nonsteep','Exact dyadic coordinates (also complete in JSON):']+[f'v{k}: '+', '.join(v)for k,v in enumerate(exact[str(i)]['verticesXYZExactDyadic'])];tx.text(.02,.95,'\n\n'.join(lines),va='top',fontsize=12,family='monospace',wrap=True)
 images.append(finish(fig,'two-original-nonsteep-facets-alone-and-exact-coordinates-2400x1800.png'))
 from matplotlib.collections import PolyCollection
 axes=[(0,1,'XY'),(0,2,'XZ'),(1,2,'YZ')]
 def orthographic(ax,a,b,label,context):
  ids=near if context else nonsteep;t=world[ids][:,:,[a,b]]
  if context:ax.add_collection(PolyCollection(t,facecolors='#cbd5df',edgecolors='#7d8995',linewidths=.35,alpha=.45,zorder=1))
  for i in nonsteep:
   p=world[i][:,[a,b]];ax.add_collection(PolyCollection([p],facecolors='#ff00cf',edgecolors='#600060',linewidths=2.5,alpha=.72,zorder=20));ax.plot(*np.vstack([p,p[0]]).T,color='#600060',linewidth=2,zorder=21)
   centre=p.mean(axis=0);ax.annotate(f'Face {i}',centre,xytext=(15,30 if i==6034 else -35),textcoords='offset points',color='#600060',fontsize=14,fontweight='bold',arrowprops=dict(arrowstyle='->',color='#600060'),zorder=30)
   for k,v in enumerate(p):ax.annotate(f'{i}:v{k}',v,xytext=(5,8 if i==6034 else -14),textcoords='offset points',fontsize=9,color='#600060',zorder=30)
  lo=t.reshape(-1,2).min(axis=0);hi=t.reshape(-1,2).max(axis=0);pad=np.maximum((hi-lo)*.15,.1);ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_aspect('equal',adjustable='box');ax.ticklabel_format(useOffset=False,style='plain');ax.grid(alpha=.3);names=['original X / m','HKPD Y / m','original Z / m'];ax.set_xlabel(names[a]);ax.set_ylabel(names[b]);ax.set_title(f'{label}: '+('complete 105 original local facets + magenta overlay'if context else'6034/6035 alone; magenta source projection'),fontsize=13)
 for context,name in [(False,'two-original-nonsteep-facets-orthographic-XY-XZ-YZ-2400x1800.png'),(True,'complete105-local-source-orthographic-magenta-overlays-2400x1800.png')]:
  fig=plt.figure(figsize=(24,18))
  for j,(a,b,label)in enumerate(axes):orthographic(fig.add_subplot(3,1,j+1),a,b,label,context)
  images.append(finish(fig,name))
 save(DOC/'context.json.gz',dict(uids=[UID],completedInputJobs=[r['jobId']for r in receipts],fourStreamCompleteFailureBreakdownVerbatim=breakdown,sourceFaceCoordinatesAllFourStreams={mode:{str(i):s['completeWorldTriangles'][i]for i in failed}for mode,s in source['completeWorldStreams'].items()},all6BasicRegressionsRetainedVerbatim=records['sixPriorBasicRegressionsRetainedVerbatim'],all11UnresolvedInterfacesRetainedVerbatim=records['elevenPriorUnresolvedInterfacesRetainedVerbatim'],complete105LocalOriginalFaceIDs=near,twoNonsteepExactCoordinatesAndOrientation=exact,diagnosticOverlaysNotVisibilityOrGPUScreenshots=True,actualPNGExports=images,renderToolVersion=matplotlib.__version__,sourceRoleInterpretationProposed=False,newFiniteProofComputed=False,currentAcceptance=False,sourceGeometryChanges=0,terrainGeometryChanges=0))
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.extend(p for p in DOC.iterdir()if p.is_file());s=importlib.util.spec_from_file_location('ocean_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original99-failure-context-no-new-role-proof',refs,dict(uids=[UID],all99OriginalFailedFacesRetained=True,rawEmptyPathsUncredited=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
if __name__=='__main__':main()

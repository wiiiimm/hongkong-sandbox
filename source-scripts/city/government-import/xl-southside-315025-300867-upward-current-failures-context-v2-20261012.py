"""Draft actual-source diagrams and record closure, no new clearance predicates."""
import importlib.util,json,subprocess,sys,uuid,types
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from PIL import Image
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
GRADE=BASE/'government-xl-southside-315025-300867-current-grade-source-context-v1-20261012'
DRAFT=BASE/'government-xl-southside-upward-current-failures-context-draft-v2-20261012'
BATCH='government-xl-southside-315025-300867-upward-current-failures-context-v2-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UIDS=['landsd/315025:0','landsd/300867:0'];COUNTS={UIDS[0]:11699,UIDS[1]:1191};UPCOUNTS={UIDS[0]:100,UIDS[1]:38}
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
HISTORICAL_TIN=BASE/'government-xl-southside-station-original-pair-source-tin-context-20261010'
def local_imports(*extras):
 queue=list(sys.modules.values())+list(extras);seen=set();files=set()
 while queue:
  m=queue.pop()
  if not isinstance(m,types.ModuleType)or id(m)in seen:continue
  seen.add(id(m));name=getattr(m,'__file__',None)
  if not name:continue
  p=Path(name).resolve()
  if ROOT not in p.parents or not p.is_file():continue
  files.add(p);queue.extend(v for v in vars(m).values()if isinstance(v,types.ModuleType))
 return sorted(files)
def preflight():
 assert not DOC.exists();refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'no-worker-schema-validation.json',DRAFT/'v1-to-v2-directory-prerequisite.diff']+[p for p in (DRAFT/'preserved-v1-output-directory-failure').iterdir()if p.is_file()]+[HISTORICAL_TIN/'diagnostic.json.gz',HERE/'xl-southside-station-original-pair-source-tin-context-20261010.py'];receipts=[]
 for folder,job in [(INPUT,'3aa11a60f740759f78677d151fa2f9c34f494d935b7a208958164e23273f84d9'),(GRADE,'7269234ae78ade5d10223502841ee35aba9e9d844d72c59d186ae56ee45cda71')]:
  receipt=read(folder/'result.json');assert receipt['jobId']==job and not receipt['currentAcceptance'];receipts.append(receipt);refs.append(folder/'result.json')
  for pin in receipt['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 capture=read(INPUT/'capture-inputs.json.gz');assert capture['manifestSHA256']==MANIFEST;forms=capture['completeCurrentForms'];assert len(forms)==46 and len({f['uid']for f in forms})==46
 resources=sorted(set(['building:'+u for u in UIDS]+[('building:'+f['uid'])if f['uid'].startswith('landsd/')else('source-form:'+f['uid'])for f in forms]+['terrain-patch:'+u for u in UIDS]));assert capture['canonicalResources']==resources and len(resources)==48
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 worlds=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];diag=read(GRADE/'diagnostic.json.gz');rows={(q['uid'],q['arithmetic']):q for q in diag['rows']};assert len(rows)==8 and set(rows)=={(u,m)for u in UIDS for m in MODES}
 for uid in UIDS:
  item=worlds[uid];ground=np.asarray(item['completeDrawnGround'],dtype='<f8');assert digest(ground.tobytes())==item['completeDrawnGroundSHA256']
  for mode in MODES:
   row=rows[uid,mode];world=np.asarray(item['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');assert world.shape==(COUNTS[uid],3,3)and digest(world.tobytes())==row['completeWorldSHA256']and digest(ground.tobytes())==row['completeGroundSHA256']
   ids=[r['sourceFace']for r in row['allCompleteOriginalFiniteRecords']if r['sourceFace']in row['allRawFailedFaces']and r['exactOrientationDiagnostic']=='upward-nonsteep'];assert len(ids)==UPCOUNTS[uid]
   assert set(ids)<=set(row['failedNonsteepFacesUncredited']);assert not row['foundationInterpretationAccepted'] and not row['currentAcceptance']
 s=importlib.util.spec_from_file_location('southside_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);refs.extend(local_imports(f));validation=read(DRAFT/'no-worker-schema-validation.json');assert validation['callerSHA256']==digest(Path(__file__).read_bytes())and validation['methodSHA256']==digest((DRAFT/'METHOD.md').read_bytes())
 return receipts,refs,{str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs},capture,worlds,rows,f

def plot(uid,world,ground,upward,components):
 pairs=[(0,1,'X / Y'),(0,2,'X / Z'),(2,1,'Z / Y')];affected=[(i,g)for i,g in enumerate(components)if set(g)&set(upward)];context=sorted({f for _,g in affected for f in g})
 fig,axes=plt.subplots(2,3,figsize=(16,12),dpi=150)
 for column,(a,b,label)in enumerate(pairs):
  for r,scope in [(0,world),(1,world[context])]:
   ax=axes[r,column];ax.add_collection(PolyCollection(ground[:,:,[a,b]],facecolors='#b6d3df',edgecolors='#8aaebd',linewidths=.15,alpha=.28));ax.add_collection(PolyCollection(scope[:,:,[a,b]],facecolors='#dedede',edgecolors='#b0b0b0',linewidths=.12,alpha=.55));ax.add_collection(PolyCollection(world[upward][:,:,[a,b]],facecolors='#ca008f',edgecolors='#790057',linewidths=.5,alpha=.9,zorder=5))
   lo=scope.min(axis=(0,1));hi=scope.max(axis=(0,1));ax.set_xlim(lo[a]-1,hi[a]+1);ax.set_ylim(lo[b]-1,hi[b]+1);ax.set_aspect('equal',adjustable='box');ax.set_xlabel(label.split(' / ')[0]+' (m)');ax.set_ylabel(label.split(' / ')[1]+' (m)');ax.grid(alpha=.2);ax.set_title(('Whole source'if r==0 else'Complete affected components')+' — '+label)
   if r==1:
    for component,g in affected:
     ids=sorted(set(g)&set(upward));centre=world[ids].mean(axis=(0,1));ax.annotate('C'+str(component)+' / '+str(len(ids)),(centre[a],centre[b]),xytext=(3,3),textcoords='offset points',fontsize=5.5,color='#790057')
 fig.suptitle(uid+' — '+str(len(upward))+' saved upward nonsteep failures; magenta diagnostic overlays\nOriginal source / current drawn ground only; no visibility, architectural role or acceptance inference',fontsize=12);fig.tight_layout(rect=[0,0,.99,.94]);p=DOC/(uid.split('/')[1].replace(':','-')+'-upward-source-ground-2400x1800.png');fig.savefig(p,dpi=150);plt.close(fig)
 with Image.open(p)as im:assert im.size==(2400,1800)
 return p,context

def owned(state):
 receipts,refs,pins,capture,worlds,rows,freezer=state;lease=read(LEASE);assert reservations.owns(lease)and lease['resources']==capture['canonicalResources'];before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 DOC.mkdir(parents=True,exist_ok=False)
 records=[];plots=[]
 for uid in UIDS:
  item=worlds[uid];world=np.asarray(item['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8');ground=np.asarray(item['completeDrawnGround'],dtype='<f8');provider=rows[uid,'providerOriginal'];upward=[r['sourceFace']for r in provider['allCompleteOriginalFiniteRecords']if r['sourceFace']in provider['allRawFailedFaces']and r['exactOrientationDiagnostic']=='upward-nonsteep'];groups=provider['completeOriginalTopology']['sharedEdgeConnectedComponents'];p,context=plot(uid,world,ground,upward,groups);plots.append(str(p.relative_to(ROOT)));refs.append(p)
  modes=[]
  for mode in MODES:
   row=rows[uid,mode];w=np.asarray(item['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');groups=row['completeOriginalTopology']['sharedEdgeConnectedComponents'];mapping={f:i for i,g in enumerate(groups)for f in g};failed=set(row['allRawFailedFaces']);modes.append(dict(arithmetic=mode,worldSHA256=row['completeWorldSHA256'],groundSHA256=row['completeGroundSHA256'],allRawFailedFaceRecords=[dict(r,completeSourceTriangle=w[r['sourceFace']].tolist(),exactNonzeroEdgeComponent=mapping.get(r['sourceFace']),classificationIsDescriptiveOnly=True)for r in row['allCompleteOriginalFiniteRecords']if r['sourceFace']in failed],wholeSourceComponents=groups,allZeroFaceIdsUncredited=row['allZeroFacesUncredited'],failedNonsteepIdsUncredited=row['failedNonsteepFacesUncredited'],allGradePathRecordsRetainedVerbatim=row['wholeOriginalSharedEdgeAndCapExposure'],noNewPredicates=True))
  records.append(dict(uid=uid,sourceSHA256=item['sourceSHA256'],completeSourceFaces=COUNTS[uid],providerUpwardFailureIds=upward,completeProviderAffectedComponentSourceIds=context,allFourModes=modes))
 save(DOC/'diagnostic.json.gz',dict(uids=UIDS,records=records,plots=plots,completeHistoricalObligationsVerbatim=read(INPUT/'historical-obligations-verbatim.json'),all46CurrentFormsRetainedVerbatim=capture['completeCurrentForms'],historicalTinSummaryVerbatim=read(HISTORICAL_TIN/'diagnostic.json.gz')['summary'],historicalTinFiltersExplicit=dict(closedWholeBoundsMarginM=1,projectedAreaRequiredGreaterThan=1e-10,floatingIntersectionArithmetic=True,notUnfilteredWholeSheetCertificate=True),noNewClearanceContactGradeTopologyOrRootPredicate=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,physicalAccepted=False,installationApproved=False,plotRuntimeVersions=dict(numpy=np.__version__,matplotlib=matplotlib.__version__)))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(DOC/'diagnostic.json.gz');out=freezer.freeze(BATCH,'southside-upward-failure-source-context-diagrams-only-no-role-credit',refs,dict(uids=UIDS,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=out['jobId'],plots=plots)),flush=True)
def main():
 state=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noWorker=True,noDB=True,noLease=True,noNewPredicates=True,upwardCounts=UPCOUNTS,resources=state[3]['canonicalResources'],currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('southside-upward-context-'+str(uuid.uuid4()),state[3]['canonicalResources'],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

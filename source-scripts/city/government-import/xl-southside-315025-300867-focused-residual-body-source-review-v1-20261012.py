"""Unexecuted source-coordinate exports and saved obligation mapping only."""
import importlib.util,json,subprocess,sys,uuid,types
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
AUTH=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012'
GRADE=BASE/'government-xl-southside-315025-300867-authenticated-original-ground-grade-v2-20261012'
OLD=BASE/'government-xl-southside-station-original-pair-exact-slab-terrain-20261010/complete-original-podium-footing-inputs.json.gz'
DETACHED=BASE/'government-xl-southside-unattached-original-components-20261010/diagnostic.json.gz'
VISUALS=BASE/'government-xl-southside-unattached-original-visuals-20261010/visuals.json'
DRAFT=BASE/'government-xl-southside-focused-residual-body-source-review-draft-v1-20261012'
BATCH='government-xl-southside-315025-300867-focused-residual-body-source-review-v1-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UIDS=['landsd/315025:0','landsd/300867:0'];MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
TARGETS=[1044,1045,2718,2719,2720,2721,5294,5295,5296,5297,5320,11034,3009]
MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
EXPECTED_JOBS=['3aa11a60f740759f78677d151fa2f9c34f494d935b7a208958164e23273f84d9','a3b5b315b784f978ab22d511b638106abb15ec334dc1aeabf428e80ccf83675c','53845e3a5064414008f95ea813e8307fe305e0caa7874a968213274573b3ae26']
def local_modules(*extras):
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
 assert not DOC.exists()
 refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'input-contract.json',DRAFT/'no-worker-schema-validation.json',OLD,DETACHED,VISUALS]
 receipts=[read(p/'result.json')for p in [INPUT,AUTH,GRADE]];assert[q['jobId']for q in receipts]==EXPECTED_JOBS
 for folder,receipt in zip([INPUT,AUTH,GRADE],receipts):
  refs.append(folder/'result.json');assert receipt['currentAcceptance']is False
  for pin in receipt['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 contract=read(DRAFT/'input-contract.json')
 for pin in contract['filePins']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 inputs=read(INPUT/'capture-inputs.json.gz');assert inputs['manifestSHA256']==MANIFEST and len(inputs['completeCurrentForms'])==46 and len(inputs['canonicalResources'])==48
 expected=sorted(set(['building:'+u for u in UIDS]+[('building:'+f['uid'])if f['uid'].startswith('landsd/')else('source-form:'+f['uid'])for f in inputs['completeCurrentForms']]+['terrain-patch:'+u for u in UIDS]));assert inputs['canonicalResources']==expected
 data=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];diag=read(GRADE/'diagnostic.json.gz');rows={(q['uid'],q['arithmetic']):q for q in diag['rows']};assert set(rows)=={(u,m)for u in UIDS for m in MODES}
 for uid in UIDS:
  assert data[uid]['sourceSHA256']==contract['sources'][uid]
  for mode in MODES:
   q=rows[uid,mode];world=np.asarray(data[uid]['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8')
   assert digest(world.tobytes())==q['completeWorldSHA256'] and q['sourceSHA256']==contract['sources'][uid]
   assert np.isfinite(world).all() and len(q['allCompleteOriginalFiniteRecords'])==len(world)
   for i,record in enumerate(q['allCompleteOriginalFiniteRecords']):assert record['sourceFace']==i and digest(world[i].tobytes())==record['completeOriginalFacetSHA256']
   assert all(b['rootCredit']is b['fullBodyRootProved']is False for b in q['completeBodyObligationAccount'])
   assert len([p for p in q['wholeOriginalSharedEdgeAndCapExposure']if p['diagnosticAccountVerbatim']['diagnosticGradeToWholeClearCapAndExposedEdges']])==(106 if uid==UIDS[0]else 50)
   if uid==UIDS[0]:assert q['failedNonsteepFacesUncredited']==TARGETS[:-1] and [f for f in q['gradeSourceFaceIds']if f not in {a['sourceFaceA']for a in q['completeFailedSteepGradeContactInventory']['contacts']if a['dimension']>0}]==[3009]
 old=read(OLD);detached=read(DETACHED);assert len(detached['unattachedComponents'])==19
 for row in old['rows']:
  world=np.asarray(data[row['uid']]['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8')
  assert digest(world.tobytes())==row['worldTriangleSHA256'] and row['sourceSHA256']==contract['sources'][row['uid']]
  for part in row['parts']:
   xyz=np.asarray(part['position'],dtype='<f8').reshape(-1,3);ix=np.asarray(part['index'],dtype=np.int64).reshape(-1,3);ids=part['originalFaceIds']
   assert np.array_equal(xyz[ix],world[ids]) and len(ids)==len(set(ids))
 visuals=read(VISUALS);assert visuals['all19PartsAccounted']is True
 for plot in visuals['plots']:
  p=ROOT/plot['path'];assert digest(p.read_bytes())==plot['sha256'];refs.append(p)
 spec=importlib.util.spec_from_file_location('southside_context_freezer_preflight',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);refs.extend(local_modules(m))
 v=read(DRAFT/'no-worker-schema-validation.json');assert v['callerSHA256']==digest(Path(__file__).read_bytes())and v['methodSHA256']==digest((DRAFT/'METHOD.md').read_bytes())
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 return receipts,refs,pins,inputs,data,rows,old,detached,visuals

def framed(ax,triangles,axes):
 points=triangles.reshape(-1,3);a,b=axes;lo=points.min(0);hi=points.max(0)
 span=np.maximum(hi-lo,0.02);ax.set_xlim(lo[a]-span[a]*.15,hi[a]+span[a]*.15);ax.set_ylim(lo[b]-span[b]*.15,hi[b]+span[b]*.15)
 ax.set_aspect('equal',adjustable='box');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=7)
 labels=['source world X (m)','HKPD Y (m)','source world Z (m)'];ax.set_xlabel(labels[a],fontsize=8);ax.set_ylabel(labels[b],fontsize=8)
def owned(state):
 receipts,refs,pins,inputs,data,rows,old,detached,visuals=state;lease=read(LEASE);assert lease['resources']==inputs['canonicalResources']and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from PIL import Image
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();worlds={u:np.asarray(data[u]['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8')for u in UIDS};review=[];obligations=[]
 for uid in UIDS:
  for mode in MODES:
   row=rows[uid,mode];paths=row['wholeOriginalSharedEdgeAndCapExposure'];mapping={f:b['originalComponent']for b in row['completeBodyObligationAccount']for f in b['completeOriginalFaceIds']}
   for body in row['completeBodyObligationAccount']:
    ids=set(body['completeOriginalFaceIds']);relevant=[p for p in paths if p['sourceFace']in ids]
    assert all(set(p['completeSourceFacePath'])<=ids and p['sourceOriginalComponent']==body['originalComponent']for p in relevant)
    obligations.append(dict(uid=uid,arithmetic=mode,sourceSHA256=row['sourceSHA256'],completeWorldSHA256=row['completeWorldSHA256'],completeAuthenticGroundSHA256=row['completeGroundSHA256'],bodyVerbatim=body,diagnosticPathsVerbatim=relevant,unqualifiedSteepResidualIds=[p['sourceFace']for p in relevant if not p['diagnosticAccountVerbatim']['diagnosticGradeToWholeClearCapAndExposedEdges']],sourceRoleAccepted=False,rootCredit=False))
   if uid==UIDS[0]:
    for i in TARGETS:
     review.append(dict(uid=uid,arithmetic=mode,sourceFace=i,originalComponent=mapping[i],actualCompleteTriangle=data[uid]['completeWorldStreams'][mode]['completeWorldTriangles'][i],savedFiniteRecordVerbatim=row['allCompleteOriginalFiniteRecords'][i],savedPathVerbatim=[p for p in paths if p['sourceFace']==i],sourceRoleUnknown=True))
 historical=[]
 for item in detached['unattachedComponents']:
  uid=item['uid'];oldrow=next(q for q in old['rows']if q['uid']==uid);part=next(p for p in oldrow['parts']if p['component']==item['originalComponent']);assert part['originalFaceIds']==item['allOriginalFaceIds']
  ids=set(part['originalFaceIds']);matched=[]
  for body in rows[uid,'providerOriginal']['completeBodyObligationAccount']:
   overlap=ids&set(body['completeOriginalFaceIds'])
   if overlap:matched.append(dict(currentOriginalComponent=body['originalComponent'],matchedFaceIds=sorted(overlap),wholeBodyExactlySameFaceSet=ids==set(body['completeOriginalFaceIds'])))
  zeros=ids&set(rows[uid,'providerOriginal']['allZeroFacesUncredited']);assert set(f for q in matched for f in q['matchedFaceIds'])==ids-zeros
  historical.append(dict(historicalObligationVerbatim=item,originalCoordinatesCorrespondExactly=True,actualCurrentBodyMapping=matched,originalZeroFaceIdsUncredited=sorted(zeros),oldGroundOrRoleApprovalTransferred=False,roleStillUnreviewed=True))
 assert len(obligations)==208*4 and len(historical)==19 and len(review)==13*4
 images=[]
 def record(name,fig,width,height):
  p=DOC/name;fig.savefig(p,dpi=150);plt.close(fig)
  with Image.open(p)as im:assert im.size==(width,height)
  images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),width=width,height=height,sourceCoordinateDiagnosticOverlay=True,GPUScreenshot=False))
 DOC.mkdir(parents=True,exist_ok=False)
 fig,axs=plt.subplots(1,2,figsize=(16,12),dpi=150)
 for ax,axes in zip(axs,[(0,2),(2,1)]):
  for uid in UIDS:
   world=worlds[uid];ax.add_collection(PolyCollection(world[:,:,list(axes)],facecolors='none',edgecolors='#6d7e8f',linewidths=.15,alpha=.3))
  ax.add_collection(PolyCollection(worlds[UIDS[0]][TARGETS][:,:,list(axes)],facecolors='#d600ad',edgecolors='#680057',linewidths=1))
  framed(ax,np.concatenate(list(worlds.values())),axes);ax.set_title('Complete unchanged original pair / 13 diagnostic targets',fontsize=12)
 fig.suptitle('Source-coordinate diagrams only: no visibility, root or role conclusion',fontsize=14);fig.tight_layout();record('whole-pair-target-context-2400x1800.png',fig,2400,1800)
 families=[[1044,1045],[2718,2719,2720,2721],[5294,5295,5296,5297],[5320],[11034],[3009]];fig,axs=plt.subplots(6,3,figsize=(16,24),dpi=150);world=worlds[UIDS[0]]
 for axesrow,ids in zip(axs,families):
  target=world[ids];lo=target.reshape(-1,3).min(0)-3;hi=target.reshape(-1,3).max(0)+3;mask=(world.min(1)<=hi).all(1)&(world.max(1)>=lo).all(1);near=world[mask]
  for ax,axes in zip(axesrow,[(0,1),(0,2),(2,1)]):
   ax.add_collection(PolyCollection(near[:,:,list(axes)],facecolors='#dbe1e7',edgecolors='#788796',linewidths=.25,alpha=.45));ax.add_collection(PolyCollection(target[:,:,list(axes)],facecolors='#d600ad',edgecolors='#57004a',linewidths=1.4))
   framed(ax,target,axes);ax.set_title('Original face IDs '+','.join(map(str,ids))+' / diagnostic overlay',fontsize=10)
 fig.suptitle('Complete target facets; nearby source context may be cropped; equal aspect, no fitting',fontsize=14);fig.tight_layout();record('complete-target-orthographic-families-2400x3600.png',fig,2400,3600)
 fig,axs=plt.subplots(4,5,figsize=(16,20),dpi=150)
 for ax,item in zip(axs.flat,detached['unattachedComponents']):
  uid=item['uid'];target=worlds[uid][item['allOriginalFaceIds']];axes=(0,2);ax.add_collection(PolyCollection(target[:,:,list(axes)],facecolors='#cc6c25',edgecolors='#552500',linewidths=.6));framed(ax,target,axes);points=target.reshape(-1,3);ax.set_title(uid+' / historical component '+str(item['originalComponent'])+'\ncomplete '+str(len(target))+' facets; Y '+format(points[:,1].min(),'.3f')+'..'+format(points[:,1].max(),'.3f'),fontsize=9)
 axs.flat[-1].axis('off');fig.suptitle('All19 complete historical parts, original plan projections only; role unresolved',fontsize=13);fig.tight_layout();record('all19-complete-historical-parts-plan-2400x3000.png',fig,2400,3000)
 save(DOC/'source-review.json.gz',dict(uids=UIDS,targetFacetRecords=review,completeBodyObligationMapping=obligations,completeZeroFaceInventoriesVerbatim=[dict(uid=q['uid'],arithmetic=q['arithmetic'],allZeroFacesUncredited=q['allZeroFacesUncredited'])for q in rows.values()],all19HistoricalObligationsVerbatim=historical,existingOriginal19SourceExportsReusedVerbatim=visuals,allHistoricalSourceObligationsVerbatim=read(INPUT/'historical-obligations-verbatim.json'),all46CurrentProtectiveFormsVerbatim=inputs['completeCurrentForms'],sourceIdentityEvidenceReceipt='fed92957487a3da510ea33fa392594489f6534953aa820d520b2c18bc57d96f5',saved51560FiniteProofsNotRepeated=True,groundContactOrPathPredicatesRun=False,authenticTINNotCurrentRenderer=True,currentNativeDomainObligationsRetained=6649,sourceGeometryChanges=0,terrainGeometryChanges=0,sourceRoleAccepted=False,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 save(DOC/'images.json',dict(plots=images,existingSourceExports=visuals,architecturalInterpretationPendingROOTActualImageReview=True))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 refs.extend(p for p in DOC.rglob('*')if p.is_file());refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 spec=importlib.util.spec_from_file_location('southside_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);refs.extend(local_modules(m));out=m.freeze(BATCH,'southside-focused-original-source-architectural-review-no-role-root-credit',refs,dict(uids=UIDS,targetFacets=13,completeBodyModeAccounts=832,historicalPartsRetained=19,plots=3,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
def main():
 state=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noWorker=True,noDB=True,noLease=True,completeBodyModeAccounts=832,targetFacetModeRecords=52,historicalParts=19,resources=state[3]['canonicalResources'],sourceRoleAccepted=False)),flush=True);return
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('southside-focused-source-review-'+str(uuid.uuid4()),state[3]['canonicalResources'],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

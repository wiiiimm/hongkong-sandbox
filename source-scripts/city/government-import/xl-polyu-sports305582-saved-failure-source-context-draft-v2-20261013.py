"""UNEXECUTED saved-proof classification/source diagrams; no geometry predicates."""
import importlib.util,json,subprocess,sys,uuid
from fractions import Fraction as F
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';DRAFT=BASE/'government-xl-polyu-sports305582-saved-failure-source-context-draft-v2-20261013'
CAPTURE=BASE/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013';FINITE=BASE/'government-xl-polyu-sports305582-current-finite-grade-v1-20261013'
BATCH='government-xl-polyu-sports305582-saved-failure-source-context-v2-20261013';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/305582:0';SOURCE='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
def preflight():
 assert not DOC.exists();contract=read(DRAFT/'input-contract.json');refs=[Path(__file__),DRAFT/'METHOD.md',DRAFT/'input-contract.json'];pins={}
 for pin in contract['filePins']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'],pin['path'];refs.append(p);pins[pin['path']]=pin['sha256']
 before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();assert digest(before)==CURRENT and before==(CAPTURE/'captured-manifest.json').read_bytes()
 receipts=[read(p/'result.json')for p in [CAPTURE,FINITE]];assert [q['jobId']for q in receipts]==['74fc230cb2ea65e352f2d47ec20440f455bc6ae428158ba68472ab528a37bf5e','1c3dd3740d3c812b90214de76073cdf51e9e178591a2401b3c3c46f60127b229']
 data=read(CAPTURE/'complete-sports-four-stream-current-ground-inputs.json.gz');finite=read(FINITE/'diagnostic.json.gz');inputs=read(CAPTURE/'capture-inputs.json.gz');assert data['sourceSHA256']==SOURCE and finite['fullSourceSlots']==42144 and len(finite['rows'])==4
 assert inputs['installedPodiumDependency']['entry']['publicationApproved']is False;forms=inputs['completeCurrentForms'];assert len(forms)==12
 resources=sorted(set([('building:'if f['uid'].startswith('landsd/')else'source-form:')+f['uid']for f in forms]+['terrain-patch:'+UID]));assert len(resources)==13
 ground=np.asarray(data['completeDrawnGround'],dtype='<f8');assert ground.shape==(12,3,3)and digest(ground.tobytes())==data['completeDrawnGroundSHA256']
 for row in finite['rows']:
  w=np.asarray(data['completeWorldStreams'][row['arithmetic']]['completeWorldTriangles'],dtype='<f8');assert w.shape==(10536,3,3)and digest(w.tobytes())==row['completeWholeWorldSHA256']and digest(ground.tobytes())==row['completeCurrentGroundSHA256']
  records=row['completeOriginalFaceComparisons'];assert [r['sourceFace']for r in records]==list(range(10536));assert row['failedFacesRetained']==[r['sourceFace']for r in records if not r['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']]
  failed=[records[i]for i in row['failedFacesRetained']];assert len(failed)==752 and Counter(r['exactOrientationDiagnostic']for r in failed)=={'steep-wall':678,'upward-nonsteep':74}
  assert len(row['completeOriginalTopology']['sharedEdgeConnectedComponents'])==21 and len(row['allZeroFacesUncredited'])==4
  for r in records:assert digest(w[r['sourceFace']].tobytes())==r['completeOriginalFacetSHA256']
 for p in refs:pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
 assert(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
 return dict(refs=refs,pins=pins,before=before,receipts=receipts,data=data,finite=finite,inputs=inputs,resources=resources,ground=ground)
def saved_disposition(record):
 proof=record['currentDrawnGroundComparison'];assert proof['completeFiniteOrdinaryBoundProved']is False and proof['paired']is not None
 pair=proof['paired'];assert pair['contract']=='exact-original-source-prism-paired-finite-clearance-v1';actual=[];collapsed=[]
 for piece in pair['allExactFiniteSourceGroundPieces']:
  j=piece['originalGroundFace'];assert 0<=j<12
  if 'allExactSourcePrismIntersectionVertices'in piece:
   for v in piece['allExactSourcePrismIntersectionVertices']:
    assert len(v['exactOriginalSourcePoint'])==3 and F(v['exactOriginalSourcePoint'][1])-F(v['exactFiniteGroundHeightM'])==F(v['exactGapM'])
    if F(v['exactGapM'])<F(-1,2):actual.append(dict(originalGroundFace=j,savedExactWitnessVerbatim=v))
  elif piece.get('collapsedProjectionConservative')is True:
   collapsed.append(piece)
  else:assert piece['closedProjectionDisjoint']is True
 return dict(sourceFace=record['sourceFace'],orientationLabelVerbatim=record['exactOrientationDiagnostic'],savedFullFiniteRecordVerbatim=record,hasActualSavedPairedOrdinaryGapViolation=bool(actual),allSavedPairedGapViolationWitnesses=actual,coverageFailure=not pair['groundProjectionCovered'],collapsedProjectionConservativeRecords=collapsed,hasOnlyConservativeNegativeWithoutActualPairedWitness=bool(not actual and F(pair['exactCertifiedLowerClearanceM'])<F(-1,2)),noNewSourceGroundPredicate=True,rootOrRoleAccepted=False)
def exports(s):
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 w=np.asarray(s['data']['completeWorldStreams']['providerOriginal']['completeWorldTriangles'],dtype='<f8');row=s['finite']['rows'][0];assert row['arithmetic']=='providerOriginal';records=row['completeOriginalFaceComparisons'];failed=row['failedFacesRetained'];up=[i for i in failed if records[i]['exactOrientationDiagnostic']=='upward-nonsteep'];steep=[i for i in failed if i not in up];top=row['completeOriginalTopology'];outputs=[]
 for name,bodyids,target in [('whole-source-and-all-failures',list(range(10536)),failed),('upward74-with-complete-parent0',top['sharedEdgeConnectedComponents'][0],up),('complete-body9-and-failed25',top['sharedEdgeConnectedComponents'][9],[i for i in failed if i in top['sharedEdgeConnectedComponents'][9]])]:
  fig=plt.figure(figsize=(12,9),dpi=200);ax=fig.add_subplot(111,projection='3d');perm=[0,2,1]
  ax.add_collection3d(Poly3DCollection(w[bodyids][:,:,perm],facecolors='#bbbbbb',edgecolors='#777777',linewidths=.12,alpha=.22))
  ax.add_collection3d(Poly3DCollection(s['ground'][:,:,perm],facecolors='#9bb782',edgecolors='#527043',linewidths=.4,alpha=.13))
  for ids,color in [([i for i in target if i in up],'#c000be'),([i for i in target if i in steep],'#c33127')]:
   if ids:ax.add_collection3d(Poly3DCollection(w[ids][:,:,perm],facecolors=color,edgecolors=color,linewidths=.5,alpha=.9))
  focus=w[target].reshape(-1,3)if name!='whole-source-and-all-failures'else w.reshape(-1,3);lo=focus.min(0);hi=focus.max(0);span=np.maximum(hi-lo,1.);pad=span*.12
  ax.set_xlim(lo[0]-pad[0],hi[0]+pad[0]);ax.set_ylim(lo[2]-pad[2],hi[2]+pad[2]);ax.set_zlim(lo[1]-pad[1],hi[1]+pad[1]);ax.set_box_aspect(span[perm]);ax.view_init(elev=28,azim=-58)
  ax.set_xlabel('original-world X (m)');ax.set_ylabel('original-world Z (m)');ax.set_zlabel('original-world Y (m)');ax.set_title(name+' | magenta=upward orientation; red=steep orientation')
  fig.text(.04,.025,'Source-coordinate diagnostic overlay, not GPU visibility or architectural function.\nAll complete parent/source arrays retained; local axes crop display only. Ground shown translucent.',fontsize=9);fig.tight_layout(rect=(0,.06,1,1));p=DOC/(name+'-2400x1800.png');fig.savefig(p,dpi=200);plt.close(fig)
  with Image.open(p)as im:assert im.size==(2400,1800)
  outputs.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),dimensions=[2400,1800],completeSourceContextFaceIds=bodyids,highlightedSourceFaceIds=target,groundFacetsRetained=list(range(12)),displayAxesMayCropCompleteArrays=name!='whole-source-and-all-failures',notGPUVisibility=True))
 return outputs
def owned(s):
 lease=read(LEASE);assert lease['resources']==s['resources']and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in s['receipts']:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 DOC.mkdir();rows=[]
 for row in s['finite']['rows']:
  mapping={i:p for p,ids in enumerate(row['completeOriginalTopology']['sharedEdgeConnectedComponents'])for i in ids};records=row['completeOriginalFaceComparisons'];failures=[dict(**saved_disposition(records[i]),originalComponent=mapping[i])for i in row['failedFacesRetained']]
  rows.append(dict(arithmetic=row['arithmetic'],completeWorldSHA256=row['completeWholeWorldSHA256'],completeGroundSHA256=row['completeCurrentGroundSHA256'],all752FullSavedFailures=failures,all21BodyAnd4ZeroTopologyVerbatim=row['completeOriginalTopology'],fullCompleteFiniteRecordsVerbatim=records,summary=dict(actualPairedWitnessFailures=sum(q['hasActualSavedPairedOrdinaryGapViolation']for q in failures),coverageFailures=sum(q['coverageFailure']for q in failures),conservativeOnlyFailures=sum(q['hasOnlyConservativeNegativeWithoutActualPairedWitness']for q in failures)),noGroundOrContactOrTopologyRecalculation=True))
 images=exports(s);save(DOC/'saved-failure-source-context.json.gz',dict(uids=[UID],rows=rows,images=images,sourceSHA256=SOURCE,captureJob=s['receipts'][0]['jobId'],finiteGradeJob=s['receipts'][1]['jobId'],completeSourceWorldBindings=s['data']['completeWorldStreams'],completeCurrentGround=s['data']['completeDrawnGround'],installedPodiumDependencyVerbatim=s['inputs']['installedPodiumDependency'],all12CurrentFormsVerbatim=s['inputs']['completeCurrentForms'],sourceOrientationDoesNotIdentifyFunction=True,noHiddenStatusOrFoundationOrSupportInterpretation=True,noHistoricalOtherPolyUPairProofTransfer=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==s['before']
 for p,h in s['pins'].items():assert digest((ROOT/p).read_bytes())==h,p
 refs=s['refs']+[p for p in DOC.rglob('*')if p.is_file()];spec=importlib.util.spec_from_file_location('polyu_saved_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);r=m.freeze(BATCH,'sports-saved-paired-failure-classification-and-source-diagrams-only',refs,dict(uids=[UID],currentAcceptance=False,physicalAccepted=False,noFiniteContactCensusRerun=True));print(json.dumps(dict(jobId=r['jobId'],images=images,currentAcceptance=False)),flush=True)
def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noDB=True,noLease=True,noSavedClassificationOrRenderExecuted=True,sourceSlots=42144,failedRecords=3008,upwardPerMode=74,steepPerMode=678,originalBodies=21,originalZeros=4,groundFacets=12,resources=s['resources'])),flush=True);return
 if '--owned'in sys.argv:return owned(s)
 assert not LOCAL.exists();q=reservations.claim('polyu-sports-saved-context-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert q['ok'];save(LEASE,json.loads(json.dumps(q['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

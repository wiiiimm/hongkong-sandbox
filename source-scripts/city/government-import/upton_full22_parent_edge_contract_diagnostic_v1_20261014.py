"""ROOT-only bounded saved860 seam contract diagnostic; no terrain nomination."""
from pathlib import Path
import json,sys,time,uuid,subprocess
import numpy as np
import upton_full22_current_plane_actual_production_capture_v1_20261014 as capture
from upton_parent_edge_validator_sample_v1_20261014 import parent_grid_sampler
from run import ROOT,HERE,read,save,connect,reservations
ref,check=capture.ref,capture.check
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-full22-parent-edge-contract-diagnostic-v1-20261014'
DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
RUNTIME=HERE/'upton_full22_parent_edge_sampler_context_v1_20261014.mjs'
JOB='0ec576bb958d4d1e468f5511afe355546486cc54ea48a6477e6054902a64d401'
TEST='test_upton_parent_edge_validator_sample_v1_20261014'

def load():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__)) and pins['runtime']==ref(RUNTIME)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 receipt=read(capture.DOC/'result.json');assert receipt['jobId']==JOB
 verified=read(capture.DOC/'ROOT-VERIFIED.json');assert verified['jobId']==JOB and verified['exactNeonReadback'] and verified['allEvidenceHashesVerified'] and verified['leaseReleased']
 _,_,nom,raw,pv,inp,whole=capture.load()
 patch=read(capture.DOC/'private-native-terrain-candidate.json.gz');measured=read(capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];edges=measured['parentEdgeVertices']
 assert measured['candidateGeometryCanonicalSHA256']=='b3f03468d65dadd630f3f52a4c385598c433db32db38908e86132e0510516b22' and len(edges)==860 and measured['parentEdgeExistingLimitM']==.01
 parent=read(check(inp['retainedParent']));base=read(ROOT/'3d-viewer/city/data/terrain.json');assert parent['w']==parent['h']==29 and parent['meta']['georef']['aE']==5 and base['w']==910 and base['h']==685 and base['meta']['georef']['aE']==70
 pos=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);idx=np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3);indexed=pos[idx]
 assert indexed.shape==(11606,3,3) and len(pos)==34818 and sorted(idx.reshape(-1).tolist())==list(range(len(pos)))
 for r in edges:
  i,c=r['face'],r['corner'];assert indexed[i,c].tobytes()==np.asarray([r['x'],r['y'],r['z']],dtype='<f8').tobytes()
 failures=[r for r in edges if r['absoluteGap']>=.01];assert len(failures)==13 and len({(r['x'],r['y'],r['z'])for r in failures})==5
 assert {(pv[r['face']]['kind'],pv[r['face']]['region'])for r in failures}=={('capturedCurrentRing','currentExteriorRing')}
 assert {pv[r['face']]['originalFace']for r in failures}=={12,13,18,19}
 for r in failures:assert pv[r['face']]['completeCurrentSourceAttribution']['assignedMultisetOccurrence']['sourcePath']=='3d-viewer/city/data/terrain.json'
 assert nom['all68ProtectedLiteralTripletsUnchanged'] and nom['allPriorFiniteAndFullScopeNegativesVerbatim']==whole['latestFullFiniteNegativesVerbatim']
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT
 return pins,receipt,nom,pv,inp,whole,patch,measured,parent,base,pos,idx

def schema_only():
 pins,receipt,nom,pv,inp,whole,patch,m,parent,base,pos,idx=load()
 return dict(passed=True,caller=ref(Path(__file__)),savedMeasuredEdgeOccurrences=860,completeValidatorPositionVerticesIncludingUnused=len(pos),allPositionsUsedExactlyOnceThus860MatchesRawValidatorEdgeInventory=True,savedOldParentGridFailedOccurrences=13,savedFailedUniqueXYZ=5,allFailedAncestorsAreCurrentBaseFaces=[12,13,18,19],measuredRetainedParentShape=[29,29,5],actualValidatorParentShape=[910,685,70],sourceGeometryChanges=0,noParentHeightSamplerOrPredicateCalculationDBLeaseWorker=True)

def owned():
 lease=read(LEASE);assert reservations.owns(lease) and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok'] and reservations.owns(lease);last=time.monotonic()
 pins,receipt,nom,pv,inp,whole,patch,m,parent,base,pos,idx=load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__)) and prep['runtime']==ref(RUNTIME) and prep['literalValidatorSampleASTExactlyUnchanged']
 refs=pins['codeRefs']+pins['inputRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'METHOD.md'),ref(PROPOSAL/'actual-readonly-preparation.json')]+prep['evidenceRefs']+receipt['evidenceRefs']
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==capture.legacy.CURRENT and reservations.owns(lease)
 fence();DOC.mkdir();canonical=parent_grid_sampler(base);rows=[];boundaries=inp['domain']
 # Full POSITION inventory, not a highest-layer-only or sampled mask substitute.
 incidents={}
 for face,ids in enumerate(idx):
  for corner,k in enumerate(ids):incidents.setdefault(int(k),[]).append(dict(candidateFace=face,corner=corner,completeProvenance=pv[face]))
 by_position={int(idx[r['face'],r['corner']]):r for r in m['parentEdgeVertices']}
 for k,(x,y,z)in enumerate(pos):
  if min(abs(x-boundaries[0]),abs(x-boundaries[2]),abs(z-boundaries[1]),abs(z-boundaries[3]))>=.002:continue
  old=by_position[k];height=canonical(float(x),float(z));gap=abs(float(y)-height)
  rows.append(dict(positionVertex=k,actualPackedXYZ=[float(x),float(y),float(z)],completeCandidateFaceIncidents=incidents[k],savedMeasuredEdgeVerbatim=old,canonicalUnchangedValidatorParent=ref(ROOT/'3d-viewer/city/data/terrain.json'),canonicalParentHeight=height,canonicalAbsoluteGap=gap,canonicalExistingStrictPointZeroOnePass=gap<.01,sourceVertexYNotComparedToNativeMaximum=True,legacyRetainedGridParentMismatchContextOnly=True));pulse()
 assert len(rows)==860
 save(DOC/'complete860-canonical-parent-edge-vertex-guard.json.gz',dict(rows=rows,completeValidatorPositionInventory=True,parentRectangle=inp['domain'],allParentGridAndSourceGeometryUnchanged=True,existingStrictLimitM=.01,allPassed=all(r['canonicalExistingStrictPointZeroOnePass']for r in rows),maximumGap=max(r['canonicalAbsoluteGap']for r in rows),old860MeasuredRowsAnd3mFailureVerbatim=m['parentEdgeVertices'],oldMeasurementParent=inp['retainedParent'],actualCanonicalValidator=ref(capture.VALIDATOR),exactLiteralExistingSeamSamplerBodyUnchanged=True,notContinuousBoundaryOrPhysicalAcceptance=True,physicalAccepted=False,installationApproved=False))
 save(DOC/'sampler-input.json.gz',dict(schema='upton-full22-saved-parent-edge-sampler-context-v1',rows=[dict(savedMeasuredEdgeVerbatim=r,candidateVertexProvenance=pv[r['face']])for r in m['parentEdgeVertices']],candidate=ref(capture.DOC/'private-native-terrain-candidate.json.gz'),retainedParent=inp['retainedParent'],currentManifestSHA256=capture.legacy.CURRENT,allCurrentInputRefs=inp['allCurrentInputRefs'],noTerrainOrModelChanges=True))
 command=['node',str(RUNTIME),str(DOC.relative_to(ROOT))]
 with (DOC/'bounded860-sampler-context.log').open('xb')as log:run_result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-sampler-command.json',dict(command=command,exitCode=run_result.returncode,noRendererGeometryOrSourceDecode=True))
 if run_result.returncode==0:
  context=read(DOC/'all860-actual-production-sampler-context.json.gz');assert len(context['rows'])==860 and context['startEndAllInputsVerified']
  refs+=[dict(path=k,sha256=v)for k,v in context['inputHashes'].items()]
 save(DOC/'diagnostic.json.gz',dict(currentCanonicalGeometrySHA256=m['candidateGeometryCanonicalSHA256'],all860CanonicalPointGuards=ref(DOC/'complete860-canonical-parent-edge-vertex-guard.json.gz'),actualSamplerExitCode=run_result.returncode,legacy3mVsPointZeroOneDiagnosticRetained=True,measurementParentWasOld29x29NativeGridRatherThanCanonical910x685Base=True,all68LiteralsWholeSourceRolesCurrentGridsAndFullFiniteNegativesRetained=True,all6650Actor1911Basic52FourWorldZeroCrossingRootSupportObligations=ref(capture.DOC/'diagnostic.json.gz'),noGeometryProposalUntilCorrectContractEvidence=True,noBoundaryThresholdWaiverOrGlobalWatertightnessRequirement=True,notOverlapMAXFiniteRootRuntimeBrowserApproval=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 fence();refs+=[ref(p)for p in DOC.iterdir()if p.is_file()]
 capture.legacy.module(capture.legacy.FREEZER,'upton_full22_parent_edge_contract_freezer').freeze(BATCH,'bounded860-saved-edge-canonical-parent-and-production-surface-contract-context-only',[check(q)for q in refs],dict(uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-saved860-parent-edge-contract-only'in sys.argv and not DOC.exists() and not LOCAL.exists()
 load();prep=read(PROPOSAL/'actual-readonly-preparation.json');assert prep['passed'] and prep['caller']==ref(Path(__file__))
 uids=capture.legacy.OWNED+[capture.legacy.SECONDARY,capture.legacy.NATIVE,capture.legacy.FOREIGN];resources=['building:'+u for u in uids]+['terrain-patch:'+u for u in uids]+['immutable-source-proof:'+BATCH]
 claim=reservations.claim('upton-full22-parent-edge-contract-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

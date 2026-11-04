"""UNEXECUTED: two completed-input routes; no candidate edits or approvals."""
from pathlib import Path
from fractions import Fraction as F
import ast,json,time,uuid,sys,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from upton_inherited_overlap_boundary_v1_20261012 import sha,projection,intersection,overlap_pair,complete_max_difference,source_attribution,segment_to_facets
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface,verify_drawn_multiset
from upton_original_tin_current_ring_join_nomination_v1_20261012 import packed
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-upton-inherited-ring-overlap-finite-boundary-v1-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json'
AUD=BASE/'government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012'
NOM=BASE/'government-xl-upton-original-tin-current-ring-join-nomination-v2-20261012'
CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012'
HELPER=HERE/'upton_inherited_overlap_boundary_v1_20261012.py';TEST=HERE/'test_upton_inherited_overlap_boundary_v1_20261012.py';FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/338946:0','landsd/12728:0','landsd/12662:0','landsd/79882:0'];FOREIGN='landsd/254809:0'
RECEIPTS=[(AUD,'fbee12e07218f022deb4af6244a2487c6ce751da40fc5fe326c38c6bcef88a5e','75b9bf7514c3f4811824061a2a754aa134458bba498a677a3fa6d75a89284fcc'),(NOM,'0514c963b8c79bae794a1bcd2683730f2af78788245e05434ce1a38f66d72427','d3ef62c5a2534b0381cdbf05c883f6300e536ba2083a86f11dc489f89cf58219'),(CAP,'69916bb92558c08c4c5c1838f7c34f963f0e888b7ef14cb489d995ab9bc36727','91d90929b7a8f3694239ba7d5ec97ab5bc1018d52e8d205c08542a820735f120')]
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=digest(p.read_bytes()))
def check(q):
 p=ROOT/q['path'];assert ref(p)=={k:q[k]for k in ['path','sha256']},q
 if 'bytes'in q:assert p.stat().st_size==q['bytes']
 return p
def module(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];seen=set();todo=[Path(__file__),HELPER,TEST,FREEZER]
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def schema_only():
 """No kernels, decoding, DB, claim, renderer or numerical recheck."""
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['helper']==ref(HELPER)and pins['test']==ref(TEST)
 for q in pins['inputRefs']:check(q)
 nom=read(NOM/'complete-nominations-before-guards.json.gz');a=read(AUD/'measured-projection-and-parent-edge.json.gz');r=read(CAP/'whole-domain-actual-parent-attribution.json.gz')['rows'];b=read(AUD/'complete-core-boundary-fixed-band-findings.json.gz')
 pairs=[q for q in a['allProjectedIntersectingPairs']if q['projectedDimension']=='area'];assert len(pairs)==1260 and all(q['leftProvenance']['kind']==q['rightProvenance']['kind']=='capturedCurrentRing'for q in pairs)
 assert len(nom['candidateFaceProvenance'])==10742 and len(nom['allCurrentTriplets'])==9214 and len(nom['completeCoreBoundaryNominations'])==b['completeSegments']==556
 assert sum(not q['actualCandidateGroundProof']['verifiedCompleteOriginalEdgeContactBand']for q in b['rows'])==433
 assert len(r)==1 and r[0]['completeAttributionMultisetMatchedActual']and len(r[0]['completeActualDrawnTriplets'])==9214
 assert sum(len(s['allSelectedMeshFaceIDs'])for s in r[0]['completeAttributedSources'])==9214
 assert [s['sourcePath']for s in r[0]['completeAttributedSources']]==['3d-viewer/city/data/terrain.json','3d-viewer/city/data/government-native-79882-0.json']
 sampler=(ROOT/'3d-viewer/city/native-terrain.js').read_text();assert 'result=Math.max(result,u*position[t.a+1]+v*position[t.b+1]+w*position[t.c+1])'in sampler and 'if(Math.abs(determinant)<1e-10)continue;'in sampler and 'withinFiniteTriangleProjection'in sampler
 for q in nom['completeCoreBoundaryNominations']:
  assert len(q['packedSourceEdge'])==2 and q['sourceCandidateFaces']
  for j in q['completeUpperEnvelopeNomination']['joinNominations']:
   assert j['currentFace']in range(9214)and len(j['exactParameterInterval'])==2
   for key in ['exactOriginalNewEndpoints','exactOriginalOldEndpoints']:assert len(j['ruled'][key])==2 and all(len(p)==3 for p in j['ruled'][key])
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),inputRefs=pins['inputRefs'],completeAreaPairs=1260,completeBoundaryRows=556,noNumericKernelExecuted=True,noDBOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 v=read(PROPOSAL/'helper-validation.json');assert v['passedTests']==21 and v['failedTests']==0 and v['exitCode']==0 and v['helper']==ref(HELPER)and v['test']==ref(TEST);check(v['log'])
 pre=read(PROPOSAL/'schema-preflight.json');assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['noNumericKernelExecuted']
 refs=[ref(p)for p in code_paths()]+[ref(PROPOSAL/p)for p in ['METHOD.md','draft-pins.json','helper-validation.json','schema-preflight.json']]+[v['log']]
 for folder,jid,h in RECEIPTS:
  receipt=read(folder/'result.json');assert receipt['jobId']==jid and ref(folder/'result.json')['sha256']==h
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 pins=read(PROPOSAL/'draft-pins.json')
 for q in pins['inputRefs']:check(q);refs.append(q)
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();schema_only();nom=read(NOM/'complete-nominations-before-guards.json.gz');patch=read(NOM/'private-native-terrain-candidate.json.gz');replay=read(NOM/'actual-production-replay.json.gz');capture=read(CAP/'whole-domain-actual-parent-attribution.json.gz')['rows'][0];measurement=read(AUD/'measured-projection-and-parent-edge.json.gz');bands=read(AUD/'complete-core-boundary-fixed-band-findings.json.gz')
 old=np.asarray(capture['completeActualDrawnTriplets'],dtype='<f8').reshape(9214,3,3);assert sha(old)==sha(np.asarray(nom['allCurrentTriplets']).reshape(9214,3,3))==sha(np.asarray(replay['before']['closedDomainDrawnTriplets']).reshape(9214,3,3))
 actual=candidate_surface(patch,nom['candidateFaceProvenance']);drawn=np.asarray(replay['after']['closedDomainDrawnTriplets']).reshape(10770,3,3);multiset=verify_drawn_multiset(actual,drawn)
 lineage=source_attribution(old,capture['completeAttributedSources']);provenance=nom['candidateFaceProvenance'];raw=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8').reshape(10742,3,3)
 for i,p in enumerate(provenance):assert p['candidateFace']==i and p['rawNominationFaceSHA256']==sha(raw[i])
 # Only already measured area nominations are assessed; measured line/point rows
 # remain verbatim in the completed input and cannot receive area inheritance.
 pairs=[q for q in measurement['allProjectedIntersectingPairs']if q['projectedDimension']=='area'];assert len(pairs)==1260
 parent_records=[]
 for s in capture['completeAttributedSources']:
  parent_records.append(dict(sourceFile=ref(ROOT/s['sourcePath']),savedAttributionFile=ref(CAP/'whole-domain-actual-parent-attribution.json.gz'),sourceMetadata={k:s[k]for k in ['sourcePath','lineage','rawCoarseCells','rawPatchExclusions','rawCoveredChildCells','rawGeoref','rawGridDimensions','actualMatrixWorldFloat64','completeMeshFaces']},completeSelectedMeshFaceIDs=s['allSelectedMeshFaceIDs']))
 DOC.mkdir(parents=True);save(DOC/'complete-current-source-attribution.json.gz',dict(rows=lineage,completeCurrentFaces=9214,allActualParentMetadata=parent_records,ambiguousIdenticalGeometryNeverInventsUniqueIdentity=True,preJSONSignedZeroRecoveryNotClaimed=True))
 overlaps=[]
 def box_ids(world,poly):
  lo=np.nextafter(np.array([float(min(p[k]for p in poly))for k in range(2)]),-np.inf);hi=np.nextafter(np.array([float(max(p[k]for p in poly))for k in range(2)]),np.inf);xz=world[:,:,[0,2]]
  return np.flatnonzero(((xz.max(1)>=lo)&(xz.min(1)<=hi)).all(1)).tolist()
 for row in pairs:
  li,ri=row['leftFace'],row['rightFace'];lp,rp=provenance[li],provenance[ri];assert lp==row['leftProvenance']and rp==row['rightProvenance']and lp['kind']==rp['kind']=='capturedCurrentRing';oi,oj=lp['originalFace'],rp['originalFace']
  q=overlap_pair(actual[li],actual[ri],old[oi],old[oj]);poly=intersection(projection(actual[li]),projection(actual[ri]));maxproof=None
  if q['exactCandidateProjectionDimension']=='area':
   ci,di=box_ids(actual,poly),box_ids(old,poly);maxproof=dict(candidateActualFaceIDs=ci,oldActualFaceIDs=di,proof=complete_max_difference(poly,actual[ci],old[di]))
  overlaps.append(dict(savedMeasuredRow=row,leftCurrentFaceLineage=lineage[oi],rightCurrentFaceLineage=lineage[oj],exactInheritance=q,completeDrawnUnionIdealAffineMax=maxproof,runtimeBranchAndJSRoundingEqualityNotGranted=True,anyBaseParentBranchRequiresSeparateSamplerContract=any(x['assignedMultisetOccurrence']['sourcePath']=='3d-viewer/city/data/terrain.json'for x in [lineage[oi],lineage[oj]])));pulse()
  if len(overlaps)%32==0:save(LOCAL/'overlap-progress.json.gz',dict(complete=False,expected=1260,rows=overlaps));print(json.dumps(dict(overlapPairs=len(overlaps),expected=1260)),flush=True)
 save(DOC/'complete-ring-overlap-inheritance.json.gz',dict(rows=overlaps,completePairs=1260,allSavedPointLineRowsRemainUncredited=True,rawValidatorFailure=ref(AUD/'real-validator-outcome.json'),unchangedMaxSampler=next(q for q in refs if q['path']=='3d-viewer/city/native-terrain.js'),continuousIdealAffineNotBitwiseJSEvaluation=True,noApprovalWritten=True))
 # Join triangles are nominated by exact plane points plus exact source/current
 # IDs. Match all stored generated faces; do not substitute a neighbouring face.
 def exactkey(face):return tuple(sorted(tuple(str(F(x))for x in p)for p in face))
 joinmap={}
 for i,p in enumerate(provenance):
  if p['kind']=='computedVerticalRuledJoin':joinmap.setdefault((p['currentSurfaceFace'],tuple(p['sourceCandidateFaces']),exactkey(p['exactOriginalPlanePoints'])),[]).append(i)
 ringmap={}
 for i,p in enumerate(provenance):
  if p['kind']=='capturedCurrentRing':ringmap.setdefault(p['originalFace'],[]).append(i)
 boundaries=[]
 def association(segment,ids):
  numeric=np.array([[float(x)for x in p]for p in segment]);assert np.isfinite(numeric).all();ids=sorted(set(ids))
  if all(segment[0][k]==segment[1][k]for k in range(3)):return dict(collapsedNominationRetainedUncredited=True,actualCandidateFaceIDs=ids)
  return dict(actualCandidateFaceIDs=ids,exactZeroDistance=segment_to_facets(segment,actual[ids],F(0)),distance01MSeparateDiagnostic=segment_to_facets(segment,actual[ids],F(.01)),existingAssociation1M=segment_to_facets(segment,actual[ids],F(.1)),limitsAreSeparateDiagnosticsNotNewAcceptanceGate=True)
 for i,row in enumerate(nom['completeCoreBoundaryNominations']):
  source=[tuple(F(x)for x in p)for p in row['packedSourceEdge']];sourceids=row['sourceCandidateFaces'];segments=[]
  for j in row['completeUpperEnvelopeNomination']['joinNominations']:
   ruling=j['ruled'];oldface=j['currentFace'];joinids=[]
   for face in ruling['allPositiveGeneratedJoinFaces']:
    key=(oldface,tuple(sourceids),exactkey(face));ids=joinmap.get(key,[]);assert ids,('Missing exact ruled triangle',i,key)
    for k in ids:assert np.array_equal(packed([[F(x)for x in p]for p in face]),raw[k])
    joinids+=ids
   ringids=ringmap.get(oldface,[]);new=[tuple(F(x)for x in p)for p in ruling['exactOriginalNewEndpoints']];oldseg=[tuple(F(x)for x in p)for p in ruling['exactOriginalOldEndpoints']]
   for t,p in zip(map(F,j['exactParameterInterval']),new):assert tuple(source[0][k]+t*(source[1][k]-source[0][k])for k in range(3))==p
   segments.append(dict(exactSavedParameterInterval=j['exactParameterInterval'],currentFaceLineage=lineage[oldface],completePositiveRuledCandidateFaces=sorted(set(joinids)),completeDegenerateRuledNomineesRetained=ruling['allExactDegenerateGeneratedNominees'],sourceSide=association(new,sourceids),sourceToJoinOrIdenticalRing=association(new,joinids or ringids),oldToActualCapturedRing=association(oldseg,ringids),oldToJoinOrIdenticalRing=association(oldseg,joinids or ringids),bothFullVerticalEndConnectors=[association([new[k],oldseg[k]],joinids)for k in range(2)]))
  intervals=sorted((F(j['exactParameterInterval'][0]),F(j['exactParameterInterval'][1]))for j in row['completeUpperEnvelopeNomination']['joinNominations']);cursor=F(0)
  for lo,hi in intervals:assert 0<=lo<=hi<=1 and lo<=cursor;cursor=max(cursor,hi)
  assert cursor==1,'Incomplete saved nomination intervals'
  boundaries.append(dict(savedBoundary=i,wholeSourceEdge=row['packedSourceEdge'],sourceCandidateFaces=sourceids,completeParameterIntervalsPreserved=True,allSavedRuledSegments=segments,rawPriorFixedUpperHeightBandVerbatim=bands['rows'][i],notGlobalWatertightnessOrPhysicalApproval=True));pulse()
  if len(boundaries)%16==0:save(LOCAL/'boundary-progress.json.gz',dict(complete=False,expected=556,rows=boundaries));print(json.dumps(dict(boundaryRows=len(boundaries),expected=556)),flush=True)
 assert bands['completeSegments']==556 and len(bands['rows'])==556
 save(DOC/'complete-finite-3d-boundary-correspondence.json.gz',dict(rows=boundaries,completeRows=556,all433RawPriorBandNegativesRetained=True,noCandidateEdits=True,noSeamOrApprovalTransfer=True))
 save(DOC/'diagnostic.json.gz',dict(overlaps=ref(DOC/'complete-ring-overlap-inheritance.json.gz'),boundary=ref(DOC/'complete-finite-3d-boundary-correspondence.json.gz'),lineage=ref(DOC/'complete-current-source-attribution.json.gz'),candidate=ref(NOM/'private-native-terrain-candidate.json.gz'),actualCandidateMultiset=multiset,priorWholeActorsFiniteProof=ref(AUD/'complete-candidate-clearance.json.gz'),priorWholeBeforeAfterActorsNotRerun=True,prior433BandNegativesRetained=True,unchangedRealValidatorFailure=ref(AUD/'real-validator-outcome.json'),sourceDecodeCalls=0,actorOrRayReruns=0,noApprovalWritten=True))
 refs+=[ref(p)for p in DOC.iterdir()if p.is_file()];fence();module(FREEZER,'upton_inherited_boundary_freezer').freeze(BATCH,'private-inherited-overlap-and-finite-boundary-diagnostic',[check(q)for q in{(r['path'],r['sha256']):r for r in refs}.values()],dict(uids=UIDS,currentManifestSHA256=CURRENT,completePairs=1260,completeBoundaryRows=556,sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--check-inherited-overlap-boundary-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-inherited-boundary-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

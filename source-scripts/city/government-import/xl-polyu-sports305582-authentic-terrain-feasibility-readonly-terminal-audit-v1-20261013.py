"""Read-only actual saved-schema audit; no project imports, decode or predicates."""
from pathlib import Path
import hashlib,json,gzip,struct
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import';D=BASE/'government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';RESULT=D/'calculation-v1/feasibility.json.gz'
EXPECTED={RESULT:'ae1a457b2fa085377671232034f7cdb52c2588e88ed6b2b6a6bf5b74037a5a52',D/'actual-readonly-preparation-v1/validation.json':'980ae40818f142fd33101de817c43a0c03acbecbe26c755af685f1dea1ce2cea',D/'execution-logs-feasibility-v1/terminal.json':'5761888488e833b69e0c705e71a047b83d370e749293027fe6c3d7e2280cdd87',D/'execution-logs-feasibility-v1/actual-end-input-pins.json':'05427b3afcd04c32e90bcea20aa86de06a3fb06389b86bcf59bcf74215e7ed42'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
def audit():
 for p,h in EXPECTED.items():assert sha(p)==h,p
 v=read(D/'actual-readonly-preparation-v1/validation.json');t=read(D/'execution-logs-feasibility-v1/terminal.json');end=read(D/'execution-logs-feasibility-v1/actual-end-input-pins.json');x=read(RESULT)
 assert v['allPassed']and v['noDB']and v['noLease']and v['noTerrainDecode']and v['noNumericalPredicates']and len(v['beforeEndLiteralPins'])==7555 and len(v['transitiveImportedCodePins'])==31
 assert t['exitCode']==0 and t['allLiteralPinsUnchanged']and t['beforeEndPinCount']==7555 and t['noDB']and t['noLease']and t['producerAbsent']
 assert (t['wrapperPID'],t['producerPID'])==(2150129,2150352)and not Path('/proc/2150129').exists()and not Path('/proc/2150352').exists()
 assert isinstance(end,list)and len(end)==7555
 expected={p['path']:p['sha256']for p in v['beforeEndLiteralPins']+v['transitiveImportedCodePins']};assert len(expected)==7555
 assert len({p['path']for p in end})==len(end)
 for p in end:assert p['unchanged']is True and p['expectedSHA256']==p['actualSHA256']==expected[p['path']]==sha(ROOT/p['path']),p['path']
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==t['currentManifestSHA256']==CURRENT
 assert sha(ROOT/t['log']['path'])==t['log']['sha256']=='51d1b4272ab25c9a770f8502d9eb774101d8e92b56396b148351c22eab6263c1'
 context=read(BASE/'government-xl-polyu-sports305582-saved-failure-source-context-v2-20261013/saved-failure-source-context.json.gz');by={r['arithmetic']:r for r in context['rows']};assert len(by)==len(x['rows'])==4
 assert x['uid']=='landsd/305582:0'and x['allSourceSlopesVerticalsAndZerosRetainedWithoutHeightLayerDeletion']and len(x['allNominatedAuthenticTerrainFacets'])==len(x['conservativeClosedNominationOriginalTerrainIds'])==7690
 assert len(set(x['conservativeClosedNominationOriginalTerrainIds']))==7690 and sum(p['completeFacets']for p in x['completeTerrainSourceLineage'])==181089
 for p in x['completeTerrainSourceLineage']:assert sha(ROOT/p['sourcePath'])==p['sourceSHA256']
 assert x['allSource181089FacetsSHA256']=='a14e3e94062d480a27d28d7f4b9037a668ab0368d28dea8b58f8cef426f01326'
 # Only stored-array byte identity, not a fresh projection/height predicate.
 groundbytes=b''.join(struct.pack('<d',a)for tri in x['allNominatedAuthenticTerrainFacets']for vertex in tri for a in vertex);gsha=hashlib.sha256(groundbytes).hexdigest();points=set();rows=[]
 for row in x['rows']:
  old=by[row['arithmetic']];assert row['all752FailureRecordsVerbatim']==old['all752FullSavedFailures']and len(old['all752FullSavedFailures'])==752
  original=[dict(sourceFace=f['sourceFace'],originalComponent=f['originalComponent'],orientationDescriptiveOnly=f['orientationLabelVerbatim'],actualCurrentViolationVerbatim=z)for f in old['all752FullSavedFailures']for z in f['allSavedPairedGapViolationWitnesses']];actual=row['allSavedViolationWitnessAuthenticContexts'];assert len(original)==len(actual)==1410
  for o,z in zip(original,actual):
   for k,val in o.items():assert z[k]==val
   q=z['authenticSourcePointContext'];assert q['exactSavedPointRetained']==o['actualCurrentViolationVerbatim']['savedExactWitnessVerbatim']['exactOriginalSourcePoint']and q['queryUsesNearestFloat64NotRationalUniversalCertificate']is True and q['existingPointOrdinaryBoundProved']is True and z['noWholeFacetOrPhysicalAcceptance']is True
   c=q['coarse'];assert c['completeCurrentGroundSHA256']==gsha and c['sourceFaceSHA256']==q['pointDoubleQuerySHA256']and c['fullAcceptance']is False and c['installationApproved']is False
   assert c['existingOrdinaryClearanceBoundProved']or(q['paired']is not None and q['paired']['existingOrdinaryClearanceBoundProved']);points.add(tuple(q['exactSavedPointRetained']))
  rows.append(dict(arithmetic=row['arithmetic'],rawFailureFacetsRetained=752,nearestFloat64SavedPointContexts=1410,allPointBoundPositive=True,noWholeFacetAcceptance=True))
 assert len(points)==611 and len(x['fullCurrentProtectedForms'])==25 and len({p['form']['uid']for p in x['fullCurrentProtectedForms']})==25
 assert x['complete6650NativeBoundsAccounted']and x['nativeStrictlyDisjoint']==6649 and len(x['nativeOverlaps'])==1 and x['nativeOverlaps'][0]['uid']=='landsd/305793:0'and x['nativeOverlaps'][0]['arithmeticViews']==[0,1,2,3]
 assert x['installedPodiumDependencyVerbatim']['entry']['publicationApproved']is False
 assert x['noPatchGenerated']and x['noSourceGeometryChange']and x['noDB']and x['noLease']and x['noCurrentFiniteContactCensusReplay']and x['currentAcceptance']is False and x['physicalAccepted']is False and x['sourceRoleInterpretationAccepted']is False
 refs=[*EXPECTED,D/'execution-logs-feasibility-v1/execution.log',D/'execution-logs-feasibility-v1/launch.json',D/'execution-logs-feasibility-v1/execution-wrapper.py',D/'actual-readonly-preparation-v1/import.log',D/'actual-readonly-preparation-v1/preflight.log',Path(__file__).resolve()]+[ROOT/p for p in expected]
 return dict(result=ref(RESULT),terminal=ref(D/'execution-logs-feasibility-v1/terminal.json'),all7555CurrentInputHashesUnchanged=True,all31ImportedClosurePinsRetained=True,actualExitCode=0,currentManifestSHA256=CURRENT,completeOriginalTerrainFacets=181089,fullDecodedWorldHashIsSavedProducerLineageNotRedecoded=True,completeSelectedOriginalFacets=7690,uniquePointContexts=611,rows=rows,conservativeForms=25,currentNativeActorsAccounted=6650,nativeOverlapUIDs=['landsd/305793:0'],nativeStrictExclusions=6649,podiumPublicationApprovedFalse=True,wrapperAndProducerAbsent=True,noDB=True,noLease=True,noPredicatesOrReplay=True,noPatch=True,currentAcceptance=False,physicalAccepted=False),sorted(set(refs))
if __name__=='__main__':
 summary,refs=audit();print(json.dumps(dict(summary=summary,evidenceRefs=[ref(p)for p in refs]),sort_keys=True))

"""UNEXECUTED receipt-only saved core/collar/distance evidence freeze.
No numerical replay, source decode, terrain proposal or acceptance.
"""
import importlib.util,json,sys
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
P=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/selective13-parent-restoration-draft-v1'
BATCH='government-xl-southside-core-collar-distance-receipt-only-v1-20261013'
CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
RESULT=P/'all-saved-negative-region-exact-core-distance-v1/diagnostic.json.gz'
TERMINAL=P/'immutable-exact-distance-execution-v1/terminal.json'
AUDIT=P/'readonly-exact-distance-result-audit-v1.json'
PREP=P/'immutable-exact-distance-import-preflight-v1/validation.json'
METHOD=P/'CORE-COLLAR-DISTANCE-RECEIPT-ONLY-FREEZER-DRAFT-METHOD.md'
EXPECTED={RESULT:'ceac65ffb0e573c6d70bd024740a7d223d508c0894455c345da84f709cf3cc77',TERMINAL:'17d55fba8936a1fe3fa63dadc4938d4aae520d45e10cb35e77bfa8ea966b0bf9',AUDIT:'26949d1f768e44b6c639f8f1f2ee79e7f20a3f1ea29a669b2c7663f5fa3c2bc5',PREP:'17ec5c2190e17a3f77b677a6a1b81086f1c59b1d8a1b5c19d820a96c9a5087f4'}
sha=lambda p:digest(p.read_bytes())
def preflight():
 assert not(BASE/BATCH).exists()
 for p,h in EXPECTED.items():assert sha(p)==h
 t,a,v=read(TERMINAL),read(AUDIT),read(PREP)
 assert t['actualExitCode']==0 and t['all58PreparationPinsUnchanged'] and t['resultSHA256']==EXPECTED[RESULT]
 assert a['negativeRegions']==4784 and a['unresolved']==0 and a['originalCoreLineageRecords']==3653 and a['allPriorCollarNegativesRetained']==3484
 assert a['producerProcessesAbsent'] and not Path('/proc/271220').exists() and not Path('/proc/271227').exists()
 assert a['currentAcceptance']is False and a['noDistanceReplay'] and a['narrowerWidthNotSelectedOrQualified']
 assert v['allPassed'] and len(v['completePinnedInputs'])==58 and len(v['codePins'])==3
 refs=[Path(__file__),METHOD,*EXPECTED,P/'immutable-exact-distance-execution-v1/execution.log']
 assert sha(refs[-1])==t['logSHA256']
 for pins in [v['completePinnedInputs'],a['allInputHashes']]:
  for path,h in pins.items():p=ROOT/path;assert sha(p)==h;refs.append(p)
 receipts=[]
 for batch in ['government-xl-southside-saved-piece-whole-form-compatibility-receipt-only-v1-20261012','government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012','government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012']:
  p=BASE/batch/'result.json';receipts.append(read(p));refs.append(p)
 refs.extend([HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'popcorn_original_ancillary_identity_20261009.py',HERE/'run.py',HERE.parent/'shared-modelling/db.py',HERE.parent/'shared-modelling/jobs.py',HERE.parent/'shared-modelling/reservations.py'])
 # These are already completed historical receipts. Their old runtime pins are
 # preserved in their original bytes; this caller neither aliases nor renews them.
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 return a,receipts,sorted(set(refs))
def main():
 a,receipts,refs=preflight()
 if '--preflight-only'in sys.argv:
  print(json.dumps(dict(savedNegativeRegions=4784,priorCollarNegatives=3484,unresolved=0,evidencePaths=len(refs),noDB=True,noLease=True,noNumericalReplay=True,currentAcceptance=False)));return
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for old in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 spec=importlib.util.spec_from_file_location('reviewed_saved_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 pins={str(p.relative_to(ROOT)):sha(p)for p in refs}
 result=m.freeze(BATCH,'completed-original-core-collar-distance-receipt-only-no-replay',refs,dict(uids=['landsd/315025:0','landsd/300867:0'],completedDistanceArtifact=dict(path=str(RESULT.relative_to(ROOT)),sha256=EXPECTED[RESULT]),completedAuditArtifact=dict(path=str(AUDIT.relative_to(ROOT)),sha256=EXPECTED[AUDIT]),savedNegativeRegions=4784,priorFiveMetreCollarNegativeRecords=3484,priorFiveMetreNoImprovedClippedRegionLost=False,unresolved=0,exactGlobalDistanceInfimumM=a['exactGlobalDistanceInfimumM'],completePreparedCorePrimitiveCount=831,completeOriginalCoreLineageRecords=3653,historicalSourceEvidenceOnly=True,diagnosticOnly=True,noNumericalReplay=True,noSourceDecode=True,noNewTerrain=True,narrowerWidthNotSelectedOrQualified=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 for path,h in pins.items():assert sha(ROOT/path)==h
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 print(json.dumps(dict(jobId=result['jobId'],receiptOnly=True,evidenceRefs=len(result['evidenceRefs']),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()

"""Receipt-only freeze of completed saved compatibility; no numerical replay."""
import importlib.util,json,sys
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
BASE=ROOT/'docs/astra-city/government-import';D=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012';C=D/'neighbour-regression-cause-draft-v1'
BATCH='government-xl-southside-saved-piece-whole-form-compatibility-receipt-only-v1-20261012';CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
RESULT=C/'saved-piece-whole-form-compatibility-v2/diagnostic.json';TERMINAL=C/'saved-piece-v2-terminal-receipt.json';AUDIT=C/'saved-piece-v2-independent-result-audit.json'
def preflight():
 assert not(BASE/BATCH).exists();q=read(RESULT);t=read(TERMINAL);a=read(AUDIT)
 assert digest(RESULT.read_bytes())=='2ea74a53ea190b2f163a252b20ccc984cf4a8f8b23aaa604d4fa4e975f896188'
 assert digest(TERMINAL.read_bytes())=='9b24861f8d3e452952a856be68011669a77d3c79fbe6e245ba9184809ed2226c'
 assert digest(AUDIT.read_bytes())=='d827075d50d81ede8597f89dccfa9b1b372bad3430c677cb76a70f1e295242c2'
 assert t['exitCode']==0 and a['producerProcessesAbsent']and not q['noImprovedClippedRegionLost']and len(q['baselineFalseAuthenticTrueRestrictionFailures'])==1560 and not q['unresolvedRestrictions']
 assert len(q['rows'])==8 and all(q[k]is False for k in ['currentAcceptance','physicalAccepted','installationApproved'])
 refs=[Path(__file__),RESULT,TERMINAL,AUDIT,ROOT/t['stdout'],ROOT/t['actualPreparation']];refs.extend(p for p in(C/'immutable-saved-piece-scheduling-v2-preparation').rglob('*')if p.is_file());refs.extend(p for p in(C/'immutable-saved-piece-import-preflight-v1').rglob('*')if p.is_file())
 for pins in [q['inputHashes'],t['codeAndMethodHashes']]:
  for path,sha in pins.items():p=ROOT/path;assert digest(p.read_bytes())==sha;refs.append(p)
 refs.extend([C/'readonly-saved-piece-scheduling-cost-measurement-v1.py',C/'SAVED-PIECE-COMPATIBILITY-METHOD-v2.md',C/'saved-piece-v1-v2-scheduling-only.diff',C/'saved-sampler-failure-attribution.json',C/'complete16-neighbour-source-context.json',C/'saved-baseline-authentic-body-restoration-join.json',C/'saved-exact-negative-witness-form-context.json'])
 receipts=[]
 for batch in ['government-xl-southside-source-local-v4-private-ground-capture-v1-20261012','government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012','government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012','government-xl-southside-315025-300867-authenticated-original-ground-grade-v2-20261012']:
  p=BASE/batch/'result.json';old=read(p);receipts.append(old);refs.append(p)
  for pin in old['evidenceRefs']:p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 refs.extend([HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'popcorn_original_ancillary_identity_20261009.py',HERE/'run.py',HERE.parent/'shared-modelling/db.py',HERE.parent/'shared-modelling/jobs.py',HERE.parent/'shared-modelling/reservations.py',D/'independent-source-local-v4-private-ground-capture-audit-v1.json'])
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 return q,receipts,sorted(set(refs))
def main():
 q,receipts,refs=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(completeSavedModeRows=8,negativeRecords=1560,unresolved=0,evidencePaths=len(refs),noNumericalReplay=True,noDB=True,noLease=True,currentAcceptance=False)));return
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for old in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 spec=importlib.util.spec_from_file_location('southside_saved_piece_existing_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 result=m.freeze(BATCH,'completed-saved-original-piece-whole-form-compatibility-no-replay',refs,dict(uids=['landsd/315025:0','landsd/300867:0'],completedSavedCompatibilityArtifact=dict(path=str(RESULT.relative_to(ROOT)),sha256=digest(RESULT.read_bytes())),completeSavedModeRows=8,completeSavedSourceSlots=51560,completeIndependentForms=16,negativeRestrictionRecords=1560,unresolvedRestrictions=0,noImprovedClippedRegionLost=False,diagnosticOnly=True,noNumericalReplay=True,noNewTerrain=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
 print(json.dumps(dict(jobId=result['jobId'],receiptOnly=True,evidenceRefs=len(result['evidenceRefs']),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()

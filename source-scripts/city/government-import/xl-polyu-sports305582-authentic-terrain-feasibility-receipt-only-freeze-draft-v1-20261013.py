"""UNEXECUTED receipt-only source feasibility freeze. No decode or numerical replay."""
import importlib.util,json,sys
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
BASE=ROOT/'docs/astra-city/government-import';D=BASE/'government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013';F=D/'receipt-only-freezer-draft-v1'
BATCH='government-xl-polyu-sports305582-authentic-terrain-feasibility-source-context-v1-20261013';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
AUDITOR=HERE/'xl-polyu-sports305582-authentic-terrain-feasibility-readonly-terminal-audit-v1-20261013.py'
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return digest(p.read_bytes())
def preflight():
 assert not(BASE/BATCH).exists();pins=read(F/'review-file-pins.json')['filePins']
 for pin in pins:assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
 a,refs=module('reviewed_polyu_saved_terminal_auditor',AUDITOR).audit();priors=[]
 for name,jid in [('government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013','74fc230cb2ea65e352f2d47ec20440f455bc6ae428158ba68472ab528a37bf5e'),('government-xl-polyu-sports305582-current-finite-grade-v1-20261013','1c3dd3740d3c812b90214de76073cdf51e9e178591a2401b3c3c46f60127b229'),('government-xl-polyu-sports305582-saved-failure-source-context-v2-20261013','d451ab471dc1f74419a8cf2ab44f6b9261911eb51b3cbe5b3a69d74d4de8b774')]:
  p=BASE/name/'result.json';q=read(p);assert q['jobId']==jid;priors.append(q);refs.append(p)
  for pin in q['evidenceRefs']:assert sha(ROOT/pin['path'])==pin['sha256'];refs.append(ROOT/pin['path'])
 refs.extend([Path(__file__).resolve(),F/'METHOD.md',F/'review-file-pins.json',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'popcorn_original_ancillary_identity_20261009.py',HERE/'run.py',HERE.parent/'shared-modelling/db.py',HERE.parent/'shared-modelling/jobs.py',HERE.parent/'shared-modelling/reservations.py'])
 refs.extend(ROOT/pin['path']for pin in pins);assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 return a,priors,sorted(set(refs))
def main():
 a,priors,refs=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(summary=a,evidencePaths=len(refs),noDB=True,noLease=True,noNumericalReplay=True)));return
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for q in priors:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 pins={str(p.relative_to(ROOT)):sha(p)for p in refs};m=module('reviewed_polyu_receipt_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 q=m.freeze(BATCH,'original-authentic-terrain-saved-witness-feasibility-receipt-only',refs,dict(uids=['landsd/305582:0','landsd/305793:0'],sourceSHA256='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15',completedFeasibilityArtifact=a['result'],completeOriginalTerrainFacets=181089,selectedOriginalFacets=7690,rawNegativeFacetsPerArithmetic=752,nearestFloat64WitnessContextsPerArithmetic=1410,distinctPointQueries=611,pointContextIsNotWholeFacetRootOrTerrainApproval=True,protectedSourceForms=25,explicitNativeDependency='landsd/305793:0',nativePublicationApprovedFalse=True,completedTerminalSummary=a,noNumericalReplay=True,noNewSourceDecode=True,noNewTerrain=True,currentAcceptance=False,physicalAccepted=False,identityAccepted=False,sourceRoleAccepted=False))
 for path,h in pins.items():assert sha(ROOT/path)==h,path
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT;print(json.dumps(dict(jobId=q['jobId'],evidenceRefs=len(q['evidenceRefs']),receiptOnly=True,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()

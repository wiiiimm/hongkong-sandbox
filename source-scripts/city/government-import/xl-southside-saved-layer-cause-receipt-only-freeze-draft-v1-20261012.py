"""UNEXECUTED receipt-only freeze of completed saved-facet causes; no replay."""
import importlib.util,json,sys
from pathlib import Path
from run import ROOT,HERE,read,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012'
PRIOR=BASE/'government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012'
BATCH='government-xl-southside-saved-layer-cause-receipt-only-freeze-v1-20261012'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
PINS=[('saved-layer-locality-cause-diagnostic-v1.json.gz','f2b8c0d835b0427c11dd0df271a5b2a46f5d0beecf849cc2850898f7a830ac5e'),('independent-saved-layer-diagnostic-audit-v1.json','50766140a82589137c567f8b3f12e1e86e9e776ce62756e38c84593a1b3ab647'),('immutable-saved-layer-validation-v1/validation.json','695f408c040bdd9771a56961ca72dd390466bfbd6ed2b7232b0ddbe9320000fd'),('immutable-saved-layer-validation-v1/tests.log','a5d4ff45e38c020f75e22520e5d7b43e2c27e9259388229243439da0b9579627'),('execution-logs/saved-layer-locality-diagnostic-v1.log','6c41c542686916f06f2eef5f669514ba0a88cb6213b4aa26328aacba13da2116'),('independent-terminal-audit-v3.json','debcfe281ecc9d57198464cb9a6262aeef7c0c5d2eb304c42c370487040df366')]
def preflight():
 assert not(BASE/BATCH).exists()and not(HERE/'local'/BATCH).exists()
 refs=[Path(__file__)];source=read(DRAFT/PINS[0][0]);audit=read(DRAFT/PINS[1][0]);prior=read(PRIOR/'result.json')
 assert prior['jobId']=='1be4acb6a5e52787ecc57dd7806df25dc4d5281fa6e94b6858a5ea2c14b2cfae'and prior['currentAcceptance']is False
 for name,sha in PINS:
  p=DRAFT/name;assert digest(p.read_bytes())==sha;refs.append(p)
 assert audit['positiveOriginalFragmentPairs']==6239 and audit['packingOnlyPairs']==12 and len(source['positiveProjectedPairRecords'])==6251
 assert audit['exactEvidenceReferenceVersions']==8089 and audit['allReferenceHashesVerified']is True
 for pin in source['evidenceRefs']+prior['evidenceRefs']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 refs.extend([PRIOR/'result.json',DRAFT/'independent-terminal-audit-v3.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py',HERE/'run.py',HERE.parent/'shared-modelling/db.py',HERE.parent/'shared-modelling/jobs.py'])
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 assert all(not Path('/proc',str(p)).exists()for p in [119538,119531,4139705,4146273,4146343])
 return source,audit,prior,sorted(set(refs))
def main():
 source,audit,prior,refs=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(exactCompletedSavedPairs=6251,originalPairs=6239,packingOnlyPairs=12,noNumericalReplay=True,noDB=True,noLease=True)));return
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
  group=c.execute('SELECT released_at,resources FROM astra_modelling.reservation_groups WHERE token=%s',('b0b13f7b-914b-4690-a923-3c7b6f84956c',)).fetchone();assert group[0]is not None and len(group[1])==124
 spec=importlib.util.spec_from_file_location('southside_completed_causes_existing_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 before={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 result=m.freeze(BATCH,'completed-saved-original-layer-causes-receipt-only-no-replay',refs,dict(uids=['landsd/315025:0','landsd/300867:0'],completedSavedCauseArtifact=dict(path=str((DRAFT/PINS[0][0]).relative_to(ROOT)),sha256=PINS[0][1]),positivePackedPairs=6251,positiveOriginalPairs=6239,packingOnlyPairs=12,priorReleasedResources=124,noNumericalReplay=True,noSourceDecode=True,noNewTerrain=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0))
 for path,sha in before.items():assert digest((ROOT/path).read_bytes())==sha
 print(json.dumps(dict(jobId=result['jobId'],receiptOnly=True,currentAcceptance=False,physicalAccepted=False)),flush=True)
if __name__=='__main__':main()

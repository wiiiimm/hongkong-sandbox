"""Leased read-only whole-domain BASIC and terrain capture."""
from pathlib import Path
import importlib.util,subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-primrose-join-runtime-capture-v5-20261015';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-primrose-current-native-parent-scope-v1-20261015';PHYSICAL=BASE/'government-xl-primrose-private-terrain-floor-v5-20261015'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 scope=read(PRIOR/'scope.json.gz');assert not scope['touchingNativeUids'];candidate=read(PHYSICAL/'terrain-candidates.json')[0]
 claim=reservations.claim('primrose-basic-ground-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'input.json.gz',dict(currentManifestSHA256=scope['currentManifestSHA256'],domain=scope['parentDomain'],cells=scope['parentCoarseCells'],candidate=candidate))
  tool=HERE/'primrose_join_runtime_capture_v1_20261015.mjs'
  with (DOC/'capture.log').open('w')as log:p=subprocess.run(['node','--max-old-space-size=8192',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  save(DOC/'command.json',dict(exitCode=p.returncode));assert p.returncode==0
  report=read(DOC/'capture-report.json.gz');assert report['startEndAllInputsVerified']and report['strictExteriorUnchanged'];assert reservations.heartbeat(lease)['ok']
  for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
  paths=[PHYSICAL/'result.json',Path(__file__),tool,PRIOR/'result.json',PRIOR/'scope.json.gz',PHYSICAL/'terrain-candidates.json']+[ROOT/p for p in report['inputHashes']]
  spec=importlib.util.spec_from_file_location('primrose_basic_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'actual-full-basic-geometry-and-before-after-terrain-capture-v1',paths,dict(uids=['landsd/74569:0','landsd/74570:0','landsd/74573:0'],basicActors=report['basicActors'],strictExteriorUnchanged=True,fullFiniteRegressionStillRequired=True,fullAcceptance=False));print('Captured BASIC actors:',report['basicActors'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

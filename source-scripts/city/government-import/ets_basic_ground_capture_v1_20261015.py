"""Read-only actual complete BASIC census and parent-domain terrain capture."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-basic-ground-capture-v1-20261015';DOC=BASE/BATCH
PREV=BASE/'government-xl-ets-bounded-gap-infill-v4-20261015'
def main():
 assert not DOC.exists();r=read(PREV/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 candidatepath=PREV/'private-patch.json.gz';patch=read(candidatepath);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);uids=[e['uid']for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']];assert len(uids)==len(set(uids));resolution=module('stanford_capture_resolution',HERE/'resolve-pass.py');domain=resolution.extent(patch['coarseCells'],read(ROOT/'3d-viewer'/patch['meta']['parentTerrain']))
 claim=reservations.claim('ets-basic-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'input.json.gz',{'currentManifestSHA256':digest(manifestpath.read_bytes()),'currentNativeCount':len(uids),'ownUids':['landsd/323703:0'],'parentURL':patch['meta']['parentTerrain'],'domain':domain,'cells':patch['coarseCells'],'candidate':{'path':str(candidatepath.relative_to(ROOT)),'sha256':digest(candidatepath.read_bytes())}})
  tool=HERE/'ets_basic_ground_capture_v1_20261015.mjs'
  with (DOC/'capture.log').open('w')as log:p=subprocess.run(['node','--max-old-space-size=8192',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  save(DOC/'command.json',{'exitCode':p.returncode});assert p.returncode==0
  report=read(DOC/'capture-report.json.gz');assert report['startEndAllInputsVerified']and report['strictExteriorUnchanged'];assert reservations.heartbeat(lease)['ok']
  paths=[Path(__file__),tool,PREV/'result.json',candidatepath,HERE/'primrose_basic_ground_capture_v1_20261015.mjs']+[ROOT/p for p in report['inputHashes']]
  module('freeze_stanford_basic',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-basic-census-and-actual-ground-before-after-v1',paths,{'uids':['landsd/323703:0'],'basicActors':report['basicActors'],'strictExteriorUnchanged':True,'nativeActorNominationStillRequired':True,'fullAcceptance':False});print({'basicActors':report['basicActors'],'fullAcceptance':False},flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

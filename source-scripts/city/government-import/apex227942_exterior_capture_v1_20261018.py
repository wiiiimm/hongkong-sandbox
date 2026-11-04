"""Whole production terrain exterior fence around the private Apex nested change."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-apex227942-exterior-capture-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];scopefolder=BASE/'government-xl-apex227942-current-native-scope-v1-20261018';cap=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018'
 for folder in [scopefolder,cap]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 scope=read(scopefolder/'scope.json');candidate=read(cap/'terrain-candidates.json')[0];manifest=ROOT/'3d-viewer/city/data/manifest.json';save(DOC/'input.json.gz',dict(currentManifestSHA256=digest(manifest.read_bytes()),currentNativeCount=scope['currentNativeActors'],ownUids=['landsd/227942:0'],domain=candidate['bounds'],candidate=candidate,cells=read(ROOT/candidate['path'])['coarseCells'],parentURL=candidate['replaces']['url'],additionalWholeActorBounds=[b for r in scope['wholeParentTouching']for b in r['completeFourWorldBounds']]))
 tool=HERE/'apex_nested_ground_capture_v1_20261018.mjs'
 with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 report=read(DOC/'capture-report.json.gz');assert report['strictExteriorUnchanged']and report['startEndAllInputsVerified']
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([tool,scopefolder/'scope.json']);out=module('apex_exterior_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-current-production-whole-exterior-exact-comparison-v1',list(set(refs)),dict(uids=['landsd/227942:0'],strictExteriorUnchanged=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()

"""Private four-original assembly and fallback test against current map inputs."""
from pathlib import Path
import os,subprocess,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-primrose-current-assembly-browser-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
VALID='government-xl-primrose-current-loader-validation-v2-20261015'
def main():
 assert not DOC.exists()and not LOCAL.exists()
 v=read(BASE/VALID/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==4 and v['exceptions']==0
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 source=BASE/'government-xl-primrose-remaining-original-components-v2-20261015';rows=read(source/'selection.json.gz')['rows'];uids=[r['uid']for r in rows]
 claim=reservations.claim('primrose-assembly-browser-'+str(uuid.uuid4()),['building:'+u for u in uids]+['building:landsd/74566:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();shutil.copytree(HERE/'local'/VALID,LOCAL);save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);cat=read(LOCAL/'catalogue.json')
  bounds=[[min(e['worldBounds'][0][i]for e in cat['models'])for i in range(3)],[max(e['worldBounds'][1][i]for e in cat['models'])for i in range(3)]]
  c=[(a+b)/2 for a,b in zip(*bounds)];expanded=[[c[i]+(p[i]-c[i])*1.15 for i in range(3)]for p in bounds]
  candidate=read(BASE/'government-xl-primrose-private-terrain-floor-v5-20261015/terrain-candidates.json')[0]
  config=dict(stage=str(LOCAL.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=candidate['path'],destination='city/data/'+BATCH+'-terrain.json',sha256=candidate['sha256'],resolution=read(ROOT/candidate['path'])['cell'],area='Primrose private original assembly')],browserUids=[e['uid']for e in cat['models']],failureTestUids=['landsd/74573:0'],jointUids=[e['uid']for e in cat['models']],fitBox=True,captureBoundsByModel={u:expanded for u in uids})
  save(LOCAL/'browser-config.json',config);tool=HERE/'primrose_assembly_acceptance_browser_v1_20261015.mjs';cmd=['node',str(tool),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False))
  for path,h in v['hashes'].items():assert digest((ROOT/path).read_bytes())==h,path
  paths=[ROOT/p for p in v['hashes']]+[BASE/VALID/'validation.json',Path(__file__),tool]+[p for p in LOCAL.rglob('*')if p.is_file()]
  module('assembly_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-private-four-source-assembly-browser-v1',paths,dict(uids=uids,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False))
  assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

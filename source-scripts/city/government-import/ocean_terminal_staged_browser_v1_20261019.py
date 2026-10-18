"""Private original Ocean Terminal mobile/desktop acceptance; no publication."""
from pathlib import Path
import os,subprocess,shutil,uuid,argparse
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';VALID='government-xl-ocean-terminal-ordinary-validation-v2-20261019';UID='landsd/205767:0'
def main(width):
 batch='government-xl-ocean-terminal-staged-browser-'+str(width)+'-v1-20261019';doc=BASE/batch;local=HERE/'local'/batch
 assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['source-relationship-review-v1','identity-review-v1','current-neighbours-v1','retained-parent-equivalence-v1','retained-sampler-v1']:
   p=BASE/('government-xl-ocean-terminal-'+name+'-20261019')/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 v=read(BASE/VALID/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==1 and v['exceptions']==0
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 source=BASE/'government-xl-ocean-terminal-private-ground-v2-20261018';row=read(source/'selection.json.gz')['rows'][0];assert row['uid']==UID
 claim=reservations.claim('ocean-terminal-private-browser-'+str(uuid.uuid4()),['building:'+UID],batch=batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  doc.mkdir();shutil.copytree(HERE/'local'/VALID,local);save(local/'source-forms.json',[row['source']['building']]);cat=read(local/'catalogue.json');assert len(cat['models'])==1
  e=cat['models'][0];assert e['sha256']==row['sourceSHA256'];e.update(priority='landmark',label='Ocean Terminal',proceduralWindows=False);save(local/'catalogue.json',cat)
  bounds=e['worldBounds'];c=[(a+b)/2 for a,b in zip(*bounds)];expanded=[[c[i]+(p[i]-c[i])*1.15 for i in range(3)]for p in bounds]
  candidate=read(BASE/VALID/'terrain-candidates.json')[0];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256']
  terrain=dict(source=candidate['path'],destination='city/data/'+batch+'-terrain.json',sha256=candidate['sha256'],resolution=read(ROOT/candidate['path'])['cell'],area='Ocean Terminal unchanged original source terrain',replaces=candidate['replaces'])
  cfg=dict(viewportWidths=[width],stage=str(local.relative_to(ROOT))+'/',doc=str(doc.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+batch+'/catalogue.json',terrain=[terrain],browserUids=[UID],failureTestUids=[UID],nativeSupportUidsByModel={},jointUids=[UID],fitBox=True,captureDirectionByModel={UID:[.25,.85,1]},captureBoundsByModel={UID:expanded})
  save(local/'browser-config.json',cfg);tool=HERE/'pacifica_assembly_acceptance_browser_v1_20261019.mjs';cmd=['node',str(tool),'staged',str((local/'browser-config.json').relative_to(ROOT))]
  with(doc/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(doc/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False));refs.extend([tool,BASE/VALID/'validation.json',source/'selection.json.gz']);refs.extend(p for p in local.rglob('*')if p.is_file())
  for path,h in {**pins,**v['hashes']}.items():assert digest((ROOT/path).read_bytes())==h,path
  module('ocean_staged_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'ocean-terminal-current-private-browser',list(dict.fromkeys(refs)),dict(uids=[UID],width=width,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False,publication=False));assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--width',type=int,choices=[390,1280]);a=p.parse_args()
 for width in ([a.width]if a.width else[390,1280]):main(width)

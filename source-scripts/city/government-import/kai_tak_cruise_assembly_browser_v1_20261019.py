"""Private desktop/mobile original assembly browser checks; no publication."""
from pathlib import Path
import os,subprocess,shutil,uuid,argparse
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';VALID='government-xl-kai-tak-cruise-assembly-validation-v1-20261019';POD='landsd/263423:0'
def main(width):
 batch='government-xl-kai-tak-cruise-assembly-browser-'+str(width)+'-v1-20261019';doc=BASE/batch;local=HERE/'local'/batch
 assert not doc.exists()and not local.exists();refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [BASE/VALID,BASE/'government-xl-kai-tak-cruise-component-interface-review-v1-20261019']:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 v=read(BASE/VALID/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==14 and v['exceptions']==0
 rows=read(BASE/VALID/'selection.json.gz')['rows'];uids=[r['uid']for r in rows]
 claim=reservations.claim(batch+'-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=batch,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  doc.mkdir();shutil.copytree(HERE/'local'/VALID,local);save(local/'source-forms.json',[r['source']['building']for r in rows]);cat=read(local/'catalogue.json');assert len(cat['models'])==14
  for e in cat['models']:
   e.update(priority='landmark',proceduralWindows=False)
   if e['uid']!=POD:e['nativeSupportUids']=[POD]
  save(local/'catalogue.json',cat)
  candidate=read(BASE/VALID/'terrain-candidates.json')[0];assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256'];terrain=dict(source=candidate['path'],destination='city/data/'+batch+'-terrain.json',sha256=candidate['sha256'],resolution=read(ROOT/candidate['path'])['cell'],area='Kai Tak unchanged original-source terrain',replaces=candidate['replaces'])
  cfg=dict(viewportWidths=[width],stage=str(local.relative_to(ROOT))+'/',doc=str(doc.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+batch+'/catalogue.json',terrain=[terrain],browserUids=uids,failureTestUids=[POD],nativeSupportUidsByModel={POD:['landsd/299814:0']},jointUids=[POD],fitBox=True,captureDirectionByModel={POD:[.25,.85,1]})
  save(local/'browser-config.json',cfg);tool=HERE/'pacifica_assembly_acceptance_browser_v1_20261019.mjs';cmd=['node',str(tool),'staged',str((local/'browser-config.json').relative_to(ROOT))]
  with(doc/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1800)
  save(doc/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False));refs.append(tool);refs.extend(p for p in local.rglob('*')if p.is_file())
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
  module('kai_assembly_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'kai-tak-cruise-fourteen-original-private-browser',list(dict.fromkeys(refs)),dict(uids=uids,width=width,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False,publication=False));assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--width',type=int,choices=[390,1280],required=True);a=p.parse_args();main(a.width)

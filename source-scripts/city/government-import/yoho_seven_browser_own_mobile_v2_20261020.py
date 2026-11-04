"""Private seven-part YOHO browser and fallback checks."""
from pathlib import Path
import os,subprocess,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-browser-own-mobile-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
VALID='government-xl-yoho-seven-loader-v1-20261020'
def main():
 assert not DOC.exists()and not LOCAL.exists()
 receipt=read(BASE/VALID/'result.json')
 functional=read(BASE/'government-xl-yoho-seven-physical-review-v1-20261020/result.json')
 with connect()as connection:
  connection.execute('SET TRANSACTION READ ONLY')
  assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(functional['jobId'],)).fetchone()==('complete',functional)
 for evidence in receipt['evidenceRefs']+functional['evidenceRefs']:assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256'],evidence['path']
 v=read(BASE/VALID/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==7 and v['exceptions']==0
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 source=BASE/'government-xl-yoho-seven-private-terrain-v1-20261020';rows=[r for r in read(source/'selection.json.gz')['rows']];uids=[r['uid']for r in rows]
 claim=reservations.claim('ifc-assembly-browser-'+str(uuid.uuid4()),['building:'+u for u in uids]+['terrain-patch:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();shutil.copytree(HERE/'local'/VALID,LOCAL,ignore=shutil.ignore_patterns('reservation.json'));save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);cat=read(LOCAL/'catalogue.json')
  cat['models'].sort(key=lambda e:(e['uid']!='landsd/301636:0',e['uid']))
  for entry in cat['models']:
   entry['priority']='landmark'
   entry['label']=next(r['source']['building'].get('name') or ('Original podium' if r['uid']=='landsd/301636:0' else 'Tower 1') for r in rows if r['uid']==entry['uid'])
   entry['proceduralWindows']=False
   assert bool(entry['supportDependencies'])==(entry['uid']!='landsd/301636:0')
  save(LOCAL/'catalogue.json',cat)
  save(DOC/'catalogue-metadata.json',dict(landmarkPriorityReason='Seven-part YOHO original assembly; private visibility diagnostic only.',dependencyReason='Each elevated component requires candidate original podium; test both asset download failures independently.',geometryChanges=0,publication=False))
  bounds=[[min(e['worldBounds'][0][i]for e in cat['models'])for i in range(3)],[max(e['worldBounds'][1][i]for e in cat['models'])for i in range(3)]]
  c=[(a+b)/2 for a,b in zip(*bounds)];expanded=[[c[i]+(p[i]-c[i])*1.15 for i in range(3)]for p in bounds]
  candidate=read(BASE/'government-xl-yoho300857-pair-terrain-candidate-v1-20261020'/'terrain-candidates.json')[0];dest=LOCAL/Path(candidate['path']).name;shutil.copyfile(ROOT/candidate['path'],dest);assert digest(dest.read_bytes())==candidate['sha256']
  terrain=[dict(source=str(dest.relative_to(ROOT)),destination='city/data/government-native-yoho-seven-podium301636-v1-20261020.json',sha256=candidate['sha256'],resolution=read(dest)['cell'],area='Seven-part YOHO original assembly')]
  captureBounds={}
  for e in cat['models']:
   lo,hi=e['worldBounds'];c=[(a+b)/2 for a,b in zip(lo,hi)];captureBounds[e['uid']]=[[c[i]+(q[i]-c[i])*1.2 for i in range(3)] for q in [lo,hi]]

  config=dict(viewportWidths=[390],stage=str(LOCAL.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=terrain,browserUids=[e['uid']for e in cat['models']],failureTestUids=uids,nativeSupportUidsByModel={u:['landsd/301636:0']for u in uids if u!='landsd/301636:0'},jointUidsByModel={u:([u] if u=='landsd/301636:0' else [u,'landsd/301636:0'])for u in uids},fitBox=True,captureDirectionByModel={u:[0,.8,-1]for u in uids},captureBoundsByModel=captureBounds)
  save(LOCAL/'browser-config.json',config);tool=HERE/'yoho_seven_acceptance_browser_v1_20261020.mjs';cmd=['node',str(tool),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False))
  for path,h in v['hashes'].items():assert digest((ROOT/path).read_bytes())==h,path
  paths=[ROOT/e['path']for e in receipt['evidenceRefs']+functional['evidenceRefs']]+[BASE/'government-xl-yoho-seven-physical-review-v1-20261020/result.json']+[BASE/VALID/'result.json']+[ROOT/p for p in v['hashes']]+[BASE/VALID/'validation.json',source/'selection.json.gz',Path(__file__),tool]+[p for p in LOCAL.rglob('*')if p.is_file()]
  module('assembly_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-private-yoho-seven-desktop-mobile-browser-v1',paths,dict(uids=uids,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False))
  assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Private five-original assembly and fallback test against current map inputs."""
from pathlib import Path
import os,subprocess,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-assembly-browser-desktop-v5-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
VALID='government-xl-pacifica-ordinary-validation-v2-20261019'
def main():
 assert not DOC.exists()and not LOCAL.exists()
 receipt=read(BASE/VALID/'result.json')
 with connect()as connection:
  connection.execute('SET TRANSACTION READ ONLY')
  assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for evidence in receipt['evidenceRefs']:assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256'],evidence['path']
 v=read(BASE/VALID/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==5 and v['exceptions']==0
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 source=BASE/'government-xl-pacifica-original-assembly-v1-20261019';rows=read(source/'selection.json.gz')['rows'];uids=[r['uid']for r in rows]
 claim=reservations.claim('pacifica-assembly-browser-'+str(uuid.uuid4()),['building:'+u for u in uids]+['building:landsd/265478:0','building:landsd/283034:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();shutil.copytree(HERE/'local'/VALID,LOCAL);save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);cat=read(LOCAL/'catalogue.json')
  for entry in cat['models']:
   entry['priority']='landmark'
   entry['label']=next(r['source']['building']['name'] for r in rows if r['uid']==entry['uid'])
   entry['proceduralWindows']=False
   entry['supportDependencies']=[]if entry['uid']=='landsd/283036:0'else [dict(uid='landsd/283036:0',state='candidate',csuid=cat['models'][0]['buildingCSUID'],sha256=cat['models'][0]['sha256'])]
  save(LOCAL/'catalogue.json',cat)
  save(DOC/'catalogue-metadata.json',dict(landmarkPriorityReason='Recognisable named mall and four-tower assembly; use existing landmark range for complete long original source. No runtime limit change.',dependencyReason='Tower requires the unchanged original Pacifica podium.',geometryChanges=0,publication=False))
  bounds=[[min(e['worldBounds'][0][i]for e in cat['models'])for i in range(3)],[max(e['worldBounds'][1][i]for e in cat['models'])for i in range(3)]]
  c=[(a+b)/2 for a,b in zip(*bounds)];expanded=[[c[i]+(p[i]-c[i])*1.15 for i in range(3)]for p in bounds]
  candidate=read(BASE/'government-xl-pacifica-ordinary-validation-v2-20261019/terrain-candidates.json')[0]
  replacement=candidate['replaces'];assert digest((ROOT/'3d-viewer'/replacement['url']).read_bytes())==replacement['sha256']
  config=dict(viewportWidths=[1280],stage=str(LOCAL.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=candidate['path'],destination='city/data/'+BATCH+'-terrain.json',sha256=candidate['sha256'],replaces=candidate['replaces'],resolution=read(ROOT/candidate['path'])['cell'],area='Pacifica private original assembly')],browserUids=[e['uid']for e in cat['models']],failureTestUids=['landsd/283036:0'],nativeSupportUidsByModel={u:candidate['replaces']['retainedUids'] for u in uids},jointUids=[e['uid']for e in cat['models']],fitBox=True,captureDirectionByModel={u:[-.1,.7,-1]for u in uids},captureBoundsByModel={u:expanded for u in uids})
  save(LOCAL/'browser-config.json',config);tool=HERE/'pacifica_assembly_acceptance_browser_v1_20261019.mjs';cmd=['node',str(tool),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False))
  for path,h in v['hashes'].items():assert digest((ROOT/path).read_bytes())==h,path
  paths=[ROOT/'3d-viewer'/replacement['url'],Path(__file__).with_name('pacifica_assembly_browser_v1_20261019.py'),BASE/'government-xl-pacifica-assembly-browser-v1-20261019/result.json']+[ROOT/e['path']for e in receipt['evidenceRefs']]+[BASE/VALID/'result.json']+[ROOT/p for p in v['hashes']]+[BASE/VALID/'validation.json',source/'selection.json.gz',Path(__file__),tool]+[p for p in LOCAL.rglob('*')if p.is_file()]
  module('assembly_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-private-five-source-desktop-browser-v5',paths,dict(uids=uids,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False))
  assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

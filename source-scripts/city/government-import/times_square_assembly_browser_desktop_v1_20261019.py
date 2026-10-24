"""Private three-original assembly and fallback test against current map inputs."""
from pathlib import Path
import os,subprocess,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-times-square-assembly-browser-desktop-v1-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
VALID='government-xl-times-square-ordinary-validation-v2-20261019'
def main():
 assert not DOC.exists()and not LOCAL.exists()
 receipt=read(BASE/VALID/'result.json')
 functional=read(BASE/'government-xl-times-square-functional-applicability-v1-20261019/result.json')
 with connect()as connection:
  connection.execute('SET TRANSACTION READ ONLY')
  assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(functional['jobId'],)).fetchone()==('complete',functional)
 for evidence in receipt['evidenceRefs']+functional['evidenceRefs']:assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256'],evidence['path']
 v=read(BASE/VALID/'validation.json');assert v['models']==v['loaderAccepted']==v['checksPassed']==3 and v['exceptions']==0
 for p,h in v['hashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 source=BASE/'government-xl-times-square-original-assembly-v1-20261018';rows=read(source/'selection.json.gz')['rows'];uids=[r['uid']for r in rows]
 claim=reservations.claim('times-square-assembly-browser-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();shutil.copytree(HERE/'local'/VALID,LOCAL);save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);cat=read(LOCAL/'catalogue.json')
  for entry in cat['models']:
   entry['priority']='landmark'
   entry['label']=next(r['source']['building']['name'] for r in rows if r['uid']==entry['uid'])
   entry['proceduralWindows']=False
   entry['supportDependencies']=[]if entry['uid']=='landsd/233901:0'else [dict(uid='landsd/233901:0',state='candidate',csuid=cat['models'][0]['buildingCSUID'],sha256=cat['models'][0]['sha256'])]
  save(LOCAL/'catalogue.json',cat)
  save(DOC/'catalogue-metadata.json',dict(landmarkPriorityReason='Recognisable named mall and two-tower assembly; use existing landmark range for complete long original source. No runtime limit change.',dependencyReason='Tower requires the unchanged original Times Square podium.',geometryChanges=0,publication=False))
  bounds=[[min(e['worldBounds'][0][i]for e in cat['models'])for i in range(3)],[max(e['worldBounds'][1][i]for e in cat['models'])for i in range(3)]]
  c=[(a+b)/2 for a,b in zip(*bounds)];expanded=[[c[i]+(p[i]-c[i])*1.15 for i in range(3)]for p in bounds]
  candidate=read(BASE/'government-xl-times-square-ordinary-validation-v2-20261019/terrain-candidates.json')[0]
  config=dict(viewportWidths=[1280],stage=str(LOCAL.relative_to(ROOT))+'/',doc=str(DOC.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=candidate['path'],destination='city/data/'+BATCH+'-terrain.json',sha256=candidate['sha256'],resolution=read(ROOT/candidate['path'])['cell'],area='Times Square private original assembly')],browserUids=[e['uid']for e in cat['models']],failureTestUids=['landsd/233901:0'],nativeSupportUidsByModel={},jointUids=[e['uid']for e in cat['models']],fitBox=True,captureDirectionByModel={u:[-.1,.7,-1]for u in uids},captureBoundsByModel={u:expanded for u in uids})
  save(LOCAL/'browser-config.json',config);tool=HERE/'pacifica_assembly_acceptance_browser_v1_20261019.mjs';cmd=['node',str(tool),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False))
  for path,h in v['hashes'].items():assert digest((ROOT/path).read_bytes())==h,path
  paths=[ROOT/e['path']for e in receipt['evidenceRefs']+functional['evidenceRefs']]+[BASE/'government-xl-times-square-functional-applicability-v1-20261019/result.json']+[BASE/VALID/'result.json']+[ROOT/p for p in v['hashes']]+[BASE/VALID/'validation.json',source/'selection.json.gz',Path(__file__),tool]+[p for p in LOCAL.rglob('*')if p.is_file()]
  module('assembly_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-private-three-source-desktop-browser-v1',paths,dict(uids=uids,browserExitCode=p.returncode,fullAcceptance=False,visualAcceptance=False))
  assert p.returncode==0
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Private browser views of four unchanged Oi Sin originals; not publication."""
from pathlib import Path
import os,subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-oi-sin-qualified-terrain-pair-v2-20261017';OLD=BASE/'government-xl-oi-sin-four-originals-physical-v1-20261017';BATCH='government-xl-oi-sin-four-originals-browser-v3-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;P='landsd/91128:0'
def main():
 assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYS,OLD]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    if folder==OLD and e['path']!=str((OLD/'selection.json.gz').relative_to(ROOT)):continue
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=read(PHYS/'selection.json.gz')['rows']+[r for r in read(OLD/'selection.json.gz')['rows']if r['uid']in ['landsd/254867:0','landsd/256457:0']];assert len(rows)==4;podium=next(r['candidate']['entry']for r in rows if r['uid']==P);models=[]
 for row in rows:
  e=dict(row['candidate']['entry'],priority='landmark',proceduralWindows=False)
  if row['uid']!=P:e['supportDependencies']=[dict(uid=P,state='candidate',csuid=podium['buildingCSUID'],sha256=podium['sha256'])]
  src=ROOT/row['candidate']['path'];assert digest(src.read_bytes())==row['sourceSHA256']==e['sha256'];dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);models.append(e);refs.append(src)
 order=['landsd/256457:0','landsd/254867:0','landsd/256280:0','landsd/91128:0'];models.sort(key=lambda e:order.index(e['uid']));assert models[0]['uid']=='landsd/256457:0'
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],counts=dict(packedModels=4),models=models));save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);candidate=read(PHYS/'terrain-candidates.json')[0];source=ROOT/candidate['path'];assert digest(source.read_bytes())==candidate['sha256'];dest=LOCAL/'terrain.json';shutil.copyfile(source,dest);rel=lambda p:str(p.relative_to(ROOT))
 config=dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=rel(dest),destination='city/data/'+BATCH+'-terrain.json',sha256=candidate['sha256'],resolution=5,area='Private Oi Sin source terrain')],browserUids=['landsd/256457:0','landsd/254867:0','landsd/256280:0','landsd/91128:0'],captureDirectionByModel={'landsd/256457:0':[-.7,.6,-.4],'landsd/254867:0':[-.7,.6,-.4]},failureTestUids=['landsd/256457:0'],jointUids=[r['uid']for r in rows],fitBox=True)
 save(LOCAL/'browser-config.json',config);DOC.mkdir();tool=HERE/'primrose_assembly_acceptance_browser_v1_20261015.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False));refs.extend([tool,*[p for p in LOCAL.rglob('*')if p.is_file()]])
 out=module('oi_four_browser_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-four-originals-private-browser-v3',list(set(refs)),dict(uids=[r['uid']for r in rows],browserExitCode=p.returncode,fullAcceptance=False,publicationApproved=False,nextStep='Inspect original carpark/podium junctions and retain all unresolved numeric/source-role gates; private browser passing is not installation approval.'));print(dict(jobId=out['jobId'],exitCode=p.returncode),flush=True)
if __name__=='__main__':main()

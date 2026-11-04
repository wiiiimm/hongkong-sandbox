"""Private original Orchards assembly browser checks, no live publication."""
from pathlib import Path
import os,subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-orchards-assembly-terrain-candidate-v1-20261017';BATCH='government-xl-orchards-assembly-private-browser-v2-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__),BASE/'government-xl-orchards-assembly-private-browser-v1-20261017/result.json'];pins={}
 for name in ['assembly-terrain-candidate','assembly-neighbours','assembly-four-foundations']:
  d=BASE/('government-xl-orchards-'+name+'-v1-20261017');r=read(d/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  refs.append(d/'result.json')
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 rows=[r for r in read(PHYS/'selection.json.gz')['rows']if r['uid']!='landsd/254621:0'];assert len(rows)==3;models=[];pod=next(r['candidate']['entry']for r in rows if r['uid']=='landsd/233002:0')
 for r in rows:
  e=dict(r['candidate']['entry'],priority='landmark',proceduralWindows=False)
  if r['uid']=='landsd/254629:0':e['supportDependencies']=[dict(uid=pod['uid'],state='candidate',csuid=pod['buildingCSUID'],sha256=pod['sha256'])]
  src=ROOT/r['candidate']['path'];assert digest(src.read_bytes())==r['sourceSHA256'];dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);models.append(e)
 save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],counts=dict(packedModels=3),models=models));save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);tr=read(PHYS/'terrain-candidates.json')[0];assert digest((ROOT/tr['path']).read_bytes())==tr['sha256'];uids=[r['uid']for r in rows];rel=lambda p:str(p.relative_to(ROOT))
 config=dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=tr['path'],destination='city/data/'+BATCH+'-terrain.json',sha256=tr['sha256'],resolution=5,area='Private Orchards original assembly terrain',replaces=tr['replaces'])],browserUids=uids,failureTestUids=['landsd/254629:0'],jointUids=uids+['landsd/254621:0'],nativeSupportUidsByModel={u:['landsd/254621:0']for u in uids},fitBox=True)
 save(LOCAL/'browser-config.json',config);DOC.mkdir();tool=HERE/'primrose_assembly_acceptance_browser_v1_20261015.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with(DOC/'browser.log').open('w')as log:out=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=out.returncode,publication=False,retainedActorFixtureOnly='nativeSupportUidsByModel forces retained Tower 1 rendering for regression; it grants no structural dependency or support credit.'))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([tool,*[p for p in LOCAL.rglob('*')if p.is_file()]]);r=module('orchards_private_browser_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-three-new-originals-and-retained-tower-browser-v1',list(set(refs)),dict(uids=uids+['landsd/254621:0'],browserExitCode=out.returncode,fullAcceptance=False,publicationApproved=False));print(dict(jobId=r['jobId'],exitCode=out.returncode),flush=True)
if __name__=='__main__':main()

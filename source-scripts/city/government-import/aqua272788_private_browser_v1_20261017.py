"""Unpublished original Tai Kwei browser diagnostic with exact private terrain replacement."""
from pathlib import Path
import subprocess,os,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-aqua272788-private-browser-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PHYS=BASE/'government-xl-aqua272788-current-physical-v3-20261017'
def main():
 assert not DOC.exists()and not LOCAL.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PHYS]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(PHYS/'selection.json.gz')['rows'][0];e=row['candidate']['entry'];e.update(priority='landmark',proceduralWindows=False,supportDependencies=[dict(uid='landsd/193086:0',state='installed',csuid=next(x for x in read(PHYS/'support-inputs.json')['sources']if x['uid']=='landsd/193086:0')['candidate']['entry']['buildingCSUID'],sha256='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91')]);cat=dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],counts=dict(packedModels=1),models=[e]);dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(ROOT/row['candidate']['path'],dest);assert digest(dest.read_bytes())==e['sha256']
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',[row['source']['building']])
 rel=lambda p:str(p.relative_to(ROOT));config=dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],browserUids=[e['uid']],failureTestUids=[e['uid']],fitBox=True)
 save(LOCAL/'browser-config.json',config);DOC.mkdir();tool=HERE/'primrose_assembly_acceptance_browser_v1_20261015.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False));refs +=[tool,*[p for p in LOCAL.rglob('*')if p.is_file()]]+[ROOT/p for p in pins]
 out=module('tai_kwei_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-aqua272788-desktop-mobile-browser-v1',list(set(refs)),dict(uids=[e['uid']],browserExitCode=p.returncode,fullAcceptance=False,qualification='Private intercepted catalogue only. Current installed original podium retained. No live publication; numerical gates independent.'));print(dict(jobId=out['jobId'],exitCode=p.returncode),flush=True)
if __name__=='__main__':main()

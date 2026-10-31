"""Run unchanged production candidate validator for the exact private Tai Kwei source."""
from pathlib import Path
import subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tai-kwei-loader-validation-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PHYS=BASE/'government-xl-tai-kwei-candidate-physical-v2-20261017'
def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(PHYS/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(PHYS/'selection.json.gz')['rows'][0];e={**row['candidate']['entry'],'proceduralWindows':False};cat=dict(schemaVersion=1,kind='staged-official-model-catalogue',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],counts=dict(packedModels=1),models=[e]);dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(ROOT/row['candidate']['path'],dest);assert digest(dest.read_bytes())==e['sha256']
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{row['uid']:row['source']});save(DOC/'terrain-candidates.json',read(PHYS/'terrain-candidates.json'))
 tool=HERE.parent/'building-batch/validate_candidates.mjs';rel=lambda p:str(p.relative_to(ROOT));cmd=['node',str(tool),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')]
 with(DOC/'validation.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode));report=read(DOC/'validation.json');refs=[Path(__file__),tool,PHYS/'result.json',PHYS/'selection.json.gz',*[ROOT/p for p in pins],*[p for p in LOCAL.rglob('*')if p.is_file()]]
 for f,h in pins.items():assert digest((ROOT/f).read_bytes())==h,f
 out=module('tai_kwei_loader_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-exact-original-current-loader-validation-v1',refs,dict(uids=[row['uid']],exitCode=p.returncode,validation=report,fullAcceptance=False));print(dict(jobId=out['jobId'],exitCode=p.returncode,results=report.get('results')),flush=True)
if __name__=='__main__':main()

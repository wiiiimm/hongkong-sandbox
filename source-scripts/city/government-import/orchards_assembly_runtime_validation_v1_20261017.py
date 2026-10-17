"""Run unchanged production candidate validator on the staged three-original catalogue."""
from pathlib import Path
import subprocess,shutil
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-assembly-runtime-validation-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()and not LOCAL.exists();phys=BASE/'government-xl-orchards-assembly-terrain-candidate-v1-20261017';source=HERE/'local/government-xl-orchards-assembly-private-browser-v3-20261017';rows=[r for r in read(phys/'selection.json.gz')['rows']if r['uid']!='landsd/254621:0'];cat=read(source/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}=={r['uid']:r['sourceSHA256']for r in rows};refs=[Path(__file__),source/'catalogue.json',phys/'selection.json.gz',phys/'terrain-candidates.json']
 for e in cat['models']:
  src=source/e['asset'];assert digest(src.read_bytes())==e['sha256'];p=LOCAL/e['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p);refs.extend([src,p])
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=3,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows});DOC.mkdir();tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((phys/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'validation.log').open('w')as log:out=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'command.json',dict(command=cmd,exitCode=out.returncode,publication=False));refs.extend([tool,*[p for p in LOCAL.rglob('*')if p.is_file()]]);r=module('orchards_runtime_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-original-production-candidate-validation-v1',list(set(refs)),dict(uids=[r['uid']for r in rows],exitCode=out.returncode,fullAcceptance=False));print(dict(jobId=r['jobId'],exitCode=out.returncode),flush=True)
if __name__=='__main__':main()

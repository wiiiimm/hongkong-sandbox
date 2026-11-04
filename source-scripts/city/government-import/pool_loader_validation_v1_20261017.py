"""Current production loader/collision/picking validation for the unchanged pool pair."""
from pathlib import Path
import subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-loader-validation-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-sham-shui-po-pool-original-group-v1-20261016'
def main():
 assert not DOC.exists() and not LOCAL.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 source=HERE/'local'/PRIOR.name;cat=read(source/'catalogue.json');DOC.mkdir();LOCAL.mkdir()
 for e in cat['models']:
  src=source/e['asset'];dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);assert digest(src.read_bytes())==e['sha256'];shutil.copyfile(src,dest)
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',read(source/'source-forms.json'))
 tool=HERE.parent/'building-batch/validate_candidates.mjs';terrain=BASE/'government-xl-sham-shui-po-pool-preserved-neighbours-v1-20261016/terrain-candidates.json';rel=lambda p:str(p.relative_to(ROOT));cmd=['node',str(tool),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(terrain),'--out',rel(DOC/'validation.json')]
 with (DOC/'worker.log').open('w') as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode));report=read(DOC/'validation.json');refs += [tool,terrain]+[p for p in LOCAL.rglob('*') if p.is_file()]
 for path,h in report.get('hashes',{}).items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 out=module('pool_loader_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-pool-production-loader-check-v1',list(dict.fromkeys(refs)),dict(uids=[e['uid'] for e in cat['models']],exitCode=p.returncode,validation=report,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],exitCode=p.returncode,results=report.get('results')),flush=True)
if __name__=='__main__':main()

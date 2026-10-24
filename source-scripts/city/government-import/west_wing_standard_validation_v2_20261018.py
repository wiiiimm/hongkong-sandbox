"""Unmodified standard viewer validator on a private original assembly catalogue."""
import subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-standard-validation-v2-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-west-wing-runtime-checks-v3-20261018'
def main():
 assert not DOC.exists();receipt=read(CAP/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),CAP/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(CAP/'selection.json.gz')['rows'];entries=[];forms={}
 for r in rows:
  e={**r['candidate']['entry'],'proceduralWindows':False};source=ROOT/r['candidate']['path'];assert digest(source.read_bytes())==e['sha256'];dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes());entries.append(e);forms[r['uid']]={**r['source'],'tileSHA256':digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes())};refs.append(dest)
 cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');cat.update(area=BATCH,models=entries,counts=dict(packedModels=4));save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=len(entries),catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',forms);DOC.mkdir()
 tool=HERE.parent/'building-batch/validate_candidates_multi_retained.mjs';cmd=['node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((CAP/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
 with(DOC/'worker.log').open('w')as log:r=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode in [0,1]and(DOC/'validation.json').exists();save(DOC/'command.json',dict(command=cmd,exitCode=r.returncode,publication=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([tool,*[p for p in LOCAL.rglob('*')if p.is_file()]])
 out=module('west_standard_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-unmodified-standard-validator-v2',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],exitCode=r.returncode,installationApproved=False,publication=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()

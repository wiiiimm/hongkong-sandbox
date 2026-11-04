"""Validate a private catalogue of the two unchanged Illumination originals."""
from pathlib import Path
import copy,subprocess
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-loader-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__)]
n='government-xl-mongkok-inset-pair-runtime-v1-20261021';_,pins=authenticate(BASE/n);p=BASE/n/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=read(p)['rows'];refs.extend([BASE/n/'result.json',p]);entries=[]
for row in rows:
 e=copy.deepcopy(row['candidate']['entry'])
 if row['uid']=='landsd/240332:0':e['proceduralWindows']=False
 ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap)
 if row.get('native'):
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');r=db.execute('SELECT i.sheet,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE i.cache_key=%s',(row['native']['cacheKey'],)).fetchone()
  assert r and r[1]==row['native']['resultSha'];e['sourceTile']=r[0]
 else:assert row['uid']=='landsd/240527:0' and e.get('sourceTile')
 dst=LOCAL/e['asset'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(ap.read_bytes());entries.append(e)
 tp=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tp.read_bytes())==row['source']['tileSHA256'];refs.append(tp)
save(LOCAL/'catalogue.json',dict(schemaVersion=1,kind='staged-official-model-catalogue',datasetId='landsd_rcd_1742809441342_98380',crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',rootTranslation=[-834500,0,816500],models=entries,counts=dict(packedModels=2)))
save(LOCAL/'catalogue-index.json',dict(models=2,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{r['uid']:r['source']for r in rows});DOC.mkdir(parents=True)
tool=HERE.parent/'building-batch/validate_candidates.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))]
with(DOC/'worker.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
save(DOC/'command.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode in [0,1];v=read(DOC/'validation.json')
for p,h in {**v.get('inputHashes',{}),**v.get('hashes',{})}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
summary=dict(uids=[r['uid']for r in rows],models=v['models'],loaderAccepted=v['loaderAccepted'],checksPassed=v['checksPassed'],exceptions=v['exceptions'],concerns=[dict(uid=r['uid'],concerns=r.get('concerns',[]))for r in v['results']],installationApproved=False)
save(DOC/'summary.json',summary);refs.extend([tool,*[p for p in LOCAL.rglob('*')if p.is_file()]])
module('illumination_loader_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pair-loader-validation',list(dict.fromkeys(refs)),summary);print(summary,flush=True)

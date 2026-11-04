"""Current exact three-source assembly diagnostic; no installation approval."""
from pathlib import Path
import copy,shutil,subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-original-group-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CURRENT=BASE/'government-xl-opus-current-identity-v1-20261017';OLD=BASE/'government-xl-opus-source-support-review-v1-20261017'
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__)];current=read(CURRENT/'result.json');old=read(OLD/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [current,old]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for r in [current,old]:
  for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 refs += [CURRENT/'result.json',OLD/'result.json'];rows=copy.deepcopy(read(CURRENT/'selection.json.gz')['rows']);assert len(rows)==3
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);installed={e['uid'] for url in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']};assert not installed.intersection(r['uid'] for r in rows)
 DOC.mkdir();LOCAL.mkdir();forms={}
 for r in rows:
  p=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(p)['buildings'] if b['uid']==r['uid'])==r['source']['building'];r['source']['tileSHA256']=digest(p.read_bytes());forms[r['uid']]=r['source'];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];dest=LOCAL/r['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest);refs.extend([p,asset])
 neigh=BASE/'government-xl-opus-three-part-neighbours-v1-20261017';nr=read(neigh/'result.json');
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(nr['jobId'],)).fetchone()==('complete',nr)
 np=neigh/'neighbour-inputs.json.gz';assert digest(np.read_bytes())==next(x['sha256'] for x in nr['evidenceRefs'] if x['path']==str(np.relative_to(ROOT)));refs += [neigh/'result.json',np];save(DOC/'terrain-candidates.json',read(np)['patches'])
 save(LOCAL/'source-forms.json',forms);save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest(manifestpath.read_bytes())));terrain=DOC/'terrain-candidates.json';tool=HERE/'acceptance-metrics-retained-group-parent.mjs';rel=lambda p:str(p.relative_to(ROOT))
 with (DOC/'worker.log').open('w') as log:subprocess.run(['node',str(tool),'--candidates',rel(LOCAL),'--selection',rel(DOC/'selection.json.gz'),'--terrain-candidates',rel(terrain),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
 metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==3 and not any(r.get('error') for r in metrics['rows'])
 for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 template=read(HERE/'local/government-xl-science-museum-loader-validation-v1-20261016/catalogue.json');template.update(area=BATCH,models=[r['candidate']['entry'] for r in rows],counts=dict(packedModels=3));save(LOCAL/'catalogue.json',template)
 summary=dict(uids=[r['uid'] for r in rows],metrics=metrics['rows'],originalGeometryChanges=0,sourceIdentityAndAssemblyReviewPending=False,fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 refs += [tool,terrain,manifestpath,LOCAL/'runtime-geometry.json.gz',*[p for p in LOCAL.rglob('*') if p.is_file()]]
 result=module('fu_group_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-unchanged-opus-original-source-current-renderer-diagnostic-v1',list(dict.fromkeys(refs)),dict(uids=summary['uids'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],metrics=metrics['rows']),flush=True)
if __name__=='__main__':main()

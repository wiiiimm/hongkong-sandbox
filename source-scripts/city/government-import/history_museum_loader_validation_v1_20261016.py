"""Private unchanged museum loader, collision and picking check; no publication."""
from pathlib import Path
import subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-history-museum-loader-validation-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/4759:0'
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for suffix in ['identity-review-v1','canopy-foundation-review-v5','preserved-neighbours-v1']:
   folder=BASE/('government-xl-history-museum-'+suffix+'-20261016');r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 selection=BASE/'government-xl-history-museum-current-ground-v1-20261016/selection.json.gz';row=read(selection)['rows'][0];entry=row['candidate']['entry'];assert entry['uid']==UID
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==entry['sha256'];source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert next(b for b in read(tile)['buildings'] if b['uid']==UID)==source['building']
 template=HERE/'local/government-xl-ets-current-loader-validation-v1-20261015/catalogue.json';cat=read(template);cat.update(area=BATCH,models=[entry],counts={'packedModels':1})
 DOC.mkdir();LOCAL.mkdir();dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(asset,dest)
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:dict(tile=source['tile'],tileSHA256=digest(tile.read_bytes()),building=source['building'])})
 terrain=BASE/'government-xl-history-museum-preserved-neighbours-v1-20261016/terrain-candidates.json';tool=HERE.parent/'building-batch/validate_candidates.mjs';rel=lambda p:str(p.relative_to(ROOT))
 cmd=['node',str(tool),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(terrain),'--out',rel(DOC/'validation.json')]
 with (DOC/'worker.log').open('w') as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode));report=read(DOC/'validation.json') if (DOC/'validation.json').exists() else dict(error='validator did not write report')
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
 refs += [selection,asset,tile,template,terrain,tool,*[p for p in LOCAL.rglob('*') if p.is_file()]]
 result=module('museum_loader_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-museum-current-production-loader-v1',list(dict.fromkeys(refs)),dict(uids=[UID],exitCode=p.returncode,validation=report,fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=result['jobId'],exitCode=p.returncode,results=report.get('results'),fullAcceptance=False),flush=True)
if __name__=='__main__':main()

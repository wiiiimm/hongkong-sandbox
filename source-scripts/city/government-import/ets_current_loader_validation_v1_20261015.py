"""Validate one unchanged combined Grand station source against private v5 terrain."""
import subprocess,shutil
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-ets-current-loader-validation-v1-20261015'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists() and not LOCAL.exists()
 prior=HERE/'local/government-xl-unmapped-runtime-diagnostic-v1-20261015'
 cat=read(prior/'candidates/catalogue.json');entry=next(e for e in cat['models'] if e['uid']=='landsd/323703:0')
 source=prior/'candidates'/entry['asset'];assert digest(source.read_bytes())==entry['sha256']
 forms=read(prior/'source-forms.json');form=forms[entry['uid']]
 tile=ROOT/'3d-viewer'/form['tile'];assert digest(tile.read_bytes())==form['tileSHA256'];assert form['building'] in read(tile)['buildings']
 patch=ROOT/'docs/astra-city/government-import/government-xl-ets-bounded-gap-infill-v4-20261015/private-patch.json.gz'
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [source,tile,patch,ROOT/'3d-viewer/city/data/manifest.json']}
 DOC.mkdir();LOCAL.mkdir();dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(source,dest)
 cat['models']=[entry];cat['counts']={'packedModels':1};save(LOCAL/'catalogue.json',cat);save(LOCAL/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']});save(LOCAL/'source-forms.json',{entry['uid']:form})
 terrain=LOCAL/'private-terrain.json';child=read(patch);parentURL=child['meta']['parentTerrain'];parentpath=ROOT/'3d-viewer'/parentURL;parent=read(parentpath);replacement={**parent,'patches':parent['patches']+[child]};save(terrain,replacement);assert read(terrain)['patches'][:-1]==parent['patches'];pins[str(parentpath.relative_to(ROOT))]=digest(parentpath.read_bytes());manifest=read(ROOT/'3d-viewer/city/data/manifest.json');retained=[e['uid']for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
 rel=lambda p:str(p.relative_to(ROOT))
 save(DOC/'terrain-candidates.json',[{'path':rel(terrain),'sha256':digest(terrain.read_bytes()),'uids':[entry['uid']],'bounds':[-1707.5,-1087.5,1652.5,1642.5],'replaces':{'url':parentURL,'sha256':digest(parentpath.read_bytes()),'retainedUids':retained}}])
 cmd=['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')]
 save(DOC/'inputs.json',{'pins':pins,'publication':False,'sourceCount':1,'identityApproval':False})
 with (DOC/'validation.log').open('w') as log: p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',{'command':cmd,'exitCode':p.returncode})
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
 report=read(DOC/'validation.json') if (DOC/'validation.json').exists() else {'error':'No validator report; see log'}
 refs=[parentpath,__import__('pathlib').Path(__file__),source,tile,patch,*LOCAL.rglob('*')];refs=[p for p in refs if p.is_file()]
 module('freeze_ets_loader',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-loader-private-v5',refs,{'uids':[entry['uid']],'exitCode':p.returncode,'validation':report,'fullAcceptance':False,'installed':False})
 print({'exitCode':p.returncode,'checksPassed':report.get('checksPassed'),'exceptions':report.get('exceptions'),'results':report.get('results')},flush=True)
if __name__=='__main__':main()

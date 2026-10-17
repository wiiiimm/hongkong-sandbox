"""Desktop/mobile inspection of unchanged original with all neighbouring forms retained."""
from pathlib import Path
import os,subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-namcheong244683-current-capture-v1-20261017';VALID=BASE/'government-xl-namcheong244683-current-identity-runtime-v1-20261017';BATCH='government-xl-namcheong244683-private-browser-v2-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;UID='landsd/244683:0'
def main():
 assert not DOC.exists() and not LOCAL.exists();pins={};refs=[Path(__file__)]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CAP,VALID,BASE/'government-xl-namcheong244683-current-foundation-v1-20261017']:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 old=HERE/'local'/VALID.name;cat=read(old/'catalogue.json');cat['models'][0].update(priority='landmark',proceduralWindows=False);entry=cat['models'][0];asset=LOCAL/entry['asset'];asset.parent.mkdir(parents=True);shutil.copyfile(old/entry['asset'],asset);assert digest(asset.read_bytes())==entry['sha256']
 row=read(CAP/'selection.json.gz')['rows'][0];save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',[row['source']['building']]);current=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid'] for url in current['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};neighbours={r['uid']for r in read(VALID/'identity-context.json')['intersectingForms']} - {UID};basic=sorted(neighbours-installed);native=sorted(neighbours&installed)
 rel=lambda p:str(p.relative_to(ROOT));save(LOCAL/'browser-config.json',dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[],browserUids=[UID],failureTestUids=[UID],fitBox=True,retainedBuildingUidsByModel={UID:basic},nativeSupportUidsByModel={UID:native}))
 DOC.mkdir();tool=HERE/'namcheong244683_base_context_browser_v1_20261017.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False));
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
 refs.extend([tool,*[ROOT/p for p in pins],*[p for p in LOCAL.rglob('*')if p.is_file()]])
 out=module('yoho_browser_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong244683-private-desktop-mobile-base-context-browser-v2',refs,dict(uids=[UID],browserExitCode=p.returncode,retainedBasicUids=basic,retainedNativeUids=native,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()

"""Private desktop/mobile original assembly review with current neighbours."""
from pathlib import Path
import os,subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-olympian-two-three-podium-terrain-v2-20261018';BATCH='government-xl-olympian-two-thirteen-private-browser-v2-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NAMES=['government-xl-olympian-two-thirteen-foundations-v2-20261018','government-xl-olympian-two-park-interface-review-v1-20261018','government-xl-olympian-two-original-interface-review-v1-20261018',CAP.name]
def main():
 assert not DOC.exists()and not LOCAL.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   d=BASE/name;r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[r for name in ['government-xl-olympian-two-current-identity-runtime-v1-20261018','government-xl-olympian-two-park-current-identity-runtime-v1-20261018']for r in read(BASE/name/'selection.json.gz')['rows']];uids=[r['uid']for r in rows];assert len(set(uids))==len(rows)==13
 cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entries=[]
 for r in rows:
  entry={**r['candidate']['entry'],'priority':'landmark','proceduralWindows':False,'publicationApproved':False,'placementReviewed':False};raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==entry['sha256'];dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);entries.append(entry)
 cat.update(area=BATCH,models=entries,counts=dict(packedModels=len(entries)));save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);current=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid']for url in current['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};neighbours={r['building']['uid']for r in read(CAP/'neighbour-inputs.json.gz')['rows']}-set(uids);basic=sorted(neighbours-installed);native=sorted(neighbours&installed)
 patch=read(CAP/'terrain-candidates.json')[0];bounds=[[min(e['worldBounds'][0][i]for e in entries)for i in range(3)],[max(e['worldBounds'][1][i]for e in entries)for i in range(3)]];centre=[(a+b)/2 for a,b in zip(*bounds)];padded=[[centre[i]+(b[i]-centre[i])*1.15 for i in range(3)]for b in bounds];rel=lambda p:str(p.relative_to(ROOT))
 save(LOCAL/'browser-config.json',dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=patch['path'],destination='city/data/'+BATCH+'.json',replacesMany=patch['replacesMany'],resolution=5,area='Private Olympian/Park Avenue original assembly')],browserUids=uids,failureTestUids=uids,jointUids=uids,fitBox=True,captureBoundsByModel={u:padded for u in uids},retainedBuildingUidsByModel={u:basic for u in uids},nativeSupportUidsByModel={u:native for u in uids}))
 DOC.mkdir();tool=HERE/'olympian_thirteen_assembly_browser_v2_20261018.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with(DOC/'browser.log').open('w')as log:browser_process=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=browser_process.returncode,publication=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([tool,*[ROOT/p for p in pins],*[p for p in LOCAL.rglob('*')if p.is_file()]])
 out=module('olympian_browser_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-thirteen-private-browser-v1',refs,dict(uids=uids,browserExitCode=browser_process.returncode,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()

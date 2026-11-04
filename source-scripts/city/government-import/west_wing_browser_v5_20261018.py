"""Private desktop/mobile original assembly review with current neighbours."""
from pathlib import Path
import os,subprocess,shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-west-wing-runtime-checks-v3-20261018';WIDTH=int(sys.argv[1]);assert WIDTH in (390,1280);BATCH=f'government-xl-west-wing-browser-{WIDTH}-v5-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NAMES=[CAP.name,'government-xl-west-wing-native-scope-v2-20261018']
def main():
 assert not DOC.exists()and not LOCAL.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   d=BASE/name;r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(CAP/'selection.json.gz')['rows'];uids=[r['uid']for r in rows];assert len(set(uids))==len(rows)==4
 dependencies={'landsd/322270:0':['landsd/26195:0']};sources={r['uid']:r['candidate']['entry'] for r in rows}
 cat=read(HERE/'accepted/government-xxl-20260911/catalogue.json');entries=[]
 for r in rows:
  entry={**r['candidate']['entry'],'priority':'landmark','proceduralWindows':False,'publicationApproved':False,'placementReviewed':False};entry['supportDependencies']=[dict(uid=u,state='candidate',sha256=sources[u]['sha256'],csuid=sources[u]['buildingCSUID']) for u in dependencies.get(r['uid'],[])];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==entry['sha256'];dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);entries.append(entry)
 cat.update(area=BATCH,models=entries,rootTranslation=rows[0]['candidate']['entry']['rootTranslation'],coordinatePolicy=rows[0]['candidate']['entry'].get('coordinatePolicy'),counts=dict(packedModels=len(entries)));save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',[r['source']['building']for r in rows]);current=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid']for url in current['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};neighbours={r['building']['uid']for r in read(CAP/'neighbour-inputs.json.gz')['rows']}-set(uids);basic=sorted(neighbours-installed);native=read(BASE/'government-xl-west-wing-native-scope-v2-20261018/scope.json')['touchingNativeUids'];native=[u for u in native if u not in uids]
 replacements=[];removals=[]
 for url in current['officialModelCatalogues']:
  old=read(ROOT/'3d-viewer'/url)
  if any(e['uid']in uids for e in old['models']):
   old['models']=[e for e in old['models']if e['uid']not in uids];old['counts']={**old.get('counts',{}),'packedModels':len(old['models'])}
   if not old['models']:removals.append(url);continue
   dest=LOCAL/'catalogue-replacements'/(digest(url.encode())+'.json');save(dest,old);replacements.append(dict(url=url,source=str(dest.relative_to(ROOT))))
 patch=read(CAP/'terrain-candidates.json')[0];bounds=[[min(e['worldBounds'][0][i]for e in entries)for i in range(3)],[max(e['worldBounds'][1][i]for e in entries)for i in range(3)]];centre=[(a+b)/2 for a,b in zip(*bounds)];padded=[[centre[i]+(b[i]-centre[i])*1.15 for i in range(3)]for b in bounds];rel=lambda p:str(p.relative_to(ROOT))
 save(LOCAL/'browser-config.json',dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',catalogueReplacements=replacements,catalogueRemovals=removals,terrain=[dict(source=patch['path'],destination='city/data/'+BATCH+'.json',resolution=5,replaces=patch['replaces'],area='Private West Wing original assembly')],browserUids=uids,viewportWidths=[WIDTH],failureTestUids=[],jointUids=uids,fitBox=True,captureBoundsByModel={u:padded for u in uids},retainedBuildingUidsByModel={u:basic for u in uids},nativeSupportUidsByModel={u:native for u in uids}))
 js="import{readFileSync}from'node:fs';import{prepareModelCatalogue}from'./3d-viewer/city/official-model-assets.js';for(const p of process.argv.slice(1)){const data=JSON.parse(readFileSync(p));prepareModelCatalogue(data,new URL(p,'http://localhost/').href);}console.log('All private catalogues pass production parser');"
 subprocess.run(['node','--input-type=module','-e',js,str((LOCAL/'catalogue.json').relative_to(ROOT)),*[r['source']for r in replacements]],cwd=ROOT,check=True)
 DOC.mkdir();tool=HERE/'west_wing_assembly_browser_v2_20261018.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with(DOC/'browser.log').open('w')as log:browser_process=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=2400)
 save(DOC/'command.json',dict(command=cmd,exitCode=browser_process.returncode,publication=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend([tool,*[ROOT/p for p in pins],*[p for p in LOCAL.rglob('*')if p.is_file()]])
 out=module('olympian_browser_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-four-originals-dependency-browser-v5',refs,dict(uids=uids,browserExitCode=browser_process.returncode,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()

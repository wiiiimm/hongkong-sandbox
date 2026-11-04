"""Private museum and retained illustrative-canopy staging; no live file changes."""
from pathlib import Path
import os,subprocess,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-science-museum-private-browser-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=HERE/'local/government-xl-science-museum-loader-validation-v1-20261016'
def main():
 assert not DOC.exists() and not LOCAL.exists();refs=[Path(__file__)];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in ['loader-validation-v1','canopy-foundation-review-v1']:
   p=BASE/('government-xl-science-museum-'+name+'-20261016')/'result.json';r=read(p);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 DOC.mkdir();LOCAL.mkdir();rel=lambda p:str(p.relative_to(ROOT));cat=read(PRIOR/'catalogue.json');e=cat['models'][0];e['priority']='landmark';dest=LOCAL/e['asset'];dest.parent.mkdir(parents=True);shutil.copyfile(PRIOR/e['asset'],dest);assert digest(dest.read_bytes())==e['sha256'];save(LOCAL/'catalogue.json',cat);forms=read(PRIOR/'source-forms.json');save(LOCAL/'source-forms.json',[forms[e['uid']]['building']])
 posts=BASE/'government-xl-science-museum-canopy-posts-v1-20261016';old=read(posts/'input.json')['building'];proposed={**old,'foundationBase':read(posts/'proposal.json')['foundationBase'],'foundationPolicy':'terrain-derived-illustrative-posts'}
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');matches=[]
 for t in manifest['tiles']:
  p=ROOT/'3d-viewer'/t['url'];data=read(p)
  if any(b['uid']==old['uid'] for b in data['buildings']):matches.append((t,p,data))
 assert len(matches)==1;t,p,data=matches[0];assert next(b for b in data['buildings'] if b['uid']==old['uid'])==old
 data['buildings']=[proposed if b['uid']==old['uid'] else b for b in data['buildings']];tile=LOCAL/'canopy-tile.json';save(tile,data);refs.append(p)
 terrainref=read(BASE/'government-xl-science-history-preserved-neighbours-v3-20261016/terrain-candidates.json')[0];terrain=LOCAL/'terrain.json';shutil.copyfile(ROOT/terrainref['path'],terrain);assert digest(terrain.read_bytes())==terrainref['sha256']
 config=dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=rel(terrain),destination='city/data/'+BATCH+'-terrain.json',sha256=digest(terrain.read_bytes()),resolution=5,area='Private museum original terrain',replaces=terrainref['replaces'])],tileReplacements=[dict(url=t['url'],source=rel(tile),originalSHA256=digest(p.read_bytes()),sha256=digest(tile.read_bytes()))],foundationForms=[proposed],browserUids=[e['uid']],failureTestUids=[e['uid']],retainedBuildingUids=['landsd/4760:0','landsd/83471:0','landsd/211447:0'],nativeSupportUidsByModel={e['uid']:['landsd/4759:0','landsd/305793:0']},fitBox=True,captureDirectionByModel={e['uid']:[.2,1,.15]})
 save(LOCAL/'browser-config.json',config);tool=HERE/'history_museum_private_browser_v1_20261016.mjs';cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
 with (DOC/'browser.log').open('w') as log:out=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
 save(DOC/'command.json',dict(command=cmd,exitCode=out.returncode,publication=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs += [tool,*[p for p in LOCAL.rglob('*') if p.is_file()]]
 r=module('museum_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-museum-retained-canopy-browser-v1',list(dict.fromkeys(refs)),dict(uids=[e['uid'],'landsd/83471:0'],browserExitCode=out.returncode,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=r['jobId'],exitCode=out.returncode),flush=True)
if __name__=='__main__':main()

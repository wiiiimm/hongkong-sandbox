"""Private native podium with all seven companion details unavailable. No publication."""
from pathlib import Path
import json,subprocess,sys,uuid,os,copy
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-basic-fallback-browser-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OLD=BASE/'government-xl-mount-sterling-private-browser-v3-20261020';OLDLOCAL=HERE/'local'/OLD.name
POD='landsd/289787:0';TOWERS=['landsd/'+u+':0' for u in ['273905','103465','239797','163899','272927','258775','272554']]
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();r=read(OLD/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),OLD/'result.json'];current={}
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def bind(p):current[str(p.relative_to(ROOT))]=digest(p.read_bytes());refs.append(p)
 cat=consume(OLDLOCAL/'catalogue.json');forms=consume(OLDLOCAL/'source-forms.json');config=consume(OLDLOCAL/'browser-config-390.json')
 for m in cat['models']:
  src=OLDLOCAL/m['asset'];assert digest(src.read_bytes())==m['sha256'];refs.append(src);dest=LOCAL/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes())
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',forms)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';bind(manifest);blocked=[];installed=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;catalogue=read(path)
  matches=[m for m in catalogue['models']if m['uid']in TOWERS]
  if matches:
   bind(path);installed.extend(m['uid']for m in matches)
   for m in matches:blocked.append(str(Path(url).parent/m['asset']))
 assert installed==[], installed
 for m in cat['models']:
  if m['uid']in TOWERS:blocked.append(str(Path(config['catalogueURL']).parent/m['asset']))
 config.update(stage=str(LOCAL.relative_to(ROOT))+'/',browserUids=[POD],failureTestUids=[],jointUids=[],jointUidsByModel={},nativeSupportUidsByModel={},retainedBuildingUids=TOWERS,basicFallbackUids=TOWERS,blockedAssetPaths=blocked,catalogueReplacements=[])
 config.pop('joinCloseups',None)
 for t in config['terrain']:consume(ROOT/t['source'])
 # Bind the current runtime and form bytes without re-running completed geometry.
 for p in (ROOT/'3d-viewer/city').glob('*.js'):bind(p)
 bind(ROOT/'3d-viewer/city/data/tiles/-2_-3.json')
 save(DOC/'scope.json',dict(sourceOnlyPrivateBrowser=True,currentInputHashes=current,publication=False,wholeCurrentTerrainReacceptance=False))
 tool=HERE/'mount_sterling_basic_fallback_browser_v2_20261020.mjs';refs.append(tool)
 for width in [390,1280]:
  cfg={**config,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'};path=LOCAL/f'config-{width}.json';save(path,cfg)
  cmd=['node',str(tool),'staged',str(path.relative_to(ROOT))]
  with(DOC/f'browser-{width}.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/f'command-{width}.json',dict(command=cmd,exitCode=proc.returncode));assert proc.returncode==0
  report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and len(report['basicFallbackViews'])==2
 for p,h in current.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
 module('victoria_fallback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-original-mall-with-seven-basic-companion-fallbacks',list(dict.fromkeys(refs)),dict(uids=[POD,*TOWERS],installationApproved=False,visualAcceptance=False))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in [POD,*TOWERS]],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

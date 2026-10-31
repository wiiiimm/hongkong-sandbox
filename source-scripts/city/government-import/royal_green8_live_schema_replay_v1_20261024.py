"""Fresh live evidence from a producer with an explicit retained-native list.

No published report, asset, receipt or readback guard is edited.
"""
import os,sys,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from royal_green8_five_physical_review_v1_20261024 import SOURCES
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-royal-green8-five-live-schema-replay-v1-20261024'
INSTALL='government-xl-royal-green8-five-original-original-installed-v1-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();receipt,pins=authenticate(BASE/INSTALL);assert receipt['sourceSHA256ByUid']==SOURCES and receipt['completeCurrentCatalogueModels']==6907
 refs=[Path(__file__),BASE/INSTALL/'result.json'];old=HERE/'ronsdale_three_live_browser_v9_20261024.mjs';new=HERE/'ronsdale_three_live_browser_v10_20261024.mjs'
 assert old.read_text().replace('mode,views:[],errors:[]','mode,views:[],retainedNativeOwnViews:[],errors:[]',1)==new.read_text();refs.extend([old,new])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==receipt['manifest']['sha256'];refs.append(manifest)
 for w in [390,1280]:
  cfgpath=HERE/'local'/INSTALL/('browser-config-'+str(w)+'.json');assert digest(cfgpath.read_bytes())==pins[str(cfgpath.relative_to(ROOT))];refs.append(cfgpath);cfg=read(cfgpath);assert not cfg.get('retainedNativeUids',[]) and set(cfg['browserUids'])==set(SOURCES)
  cfg['doc']=str((out/('viewport-'+str(w))).relative_to(ROOT))+'/';dest=out/('config-'+str(w)+'.json');save(dest,cfg)
  with (out/('browser-'+str(w)+'.log')).open('w')as log:
   p=subprocess.run(['node',str(new),'live',str(dest.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
  assert p.returncode==0;report=read(out/('viewport-'+str(w))/'live-browser.json');assert report['passed']and not report['errors']and report['retainedNativeOwnViews']==[]
  assert all({m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
  print(dict(width=w,passed=True,explicitRetainedNativeViews=report['retainedNativeOwnViews']),flush=True)
 assert digest(manifest.read_bytes())==receipt['manifest']['sha256'];refs.extend(p for p in out.rglob('*')if p.is_file())
 result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,installedJobId=receipt['jobId'],currentManifestSHA256=digest(manifest.read_bytes()),schemaProducerOnlyChange=True,sourceGeometryChanges=0,installationApproved=False,publication=False)
 module('live_schema_replay_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-live-browser-evidence-with-required-retained-native-schema',refs,result)
if __name__=='__main__':main()

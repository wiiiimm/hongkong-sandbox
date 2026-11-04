"""Isolated original-source failed-download/retry checks. No asset or runtime edits."""
import json,os,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-private-browser-v5-20261018';STAGE=HERE/'local'/PRIOR.name
BATCH='government-xl-wave-verdant-dependency-failures-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 report=read(PRIOR/'staged-browser.json');assert report['passed']and not report['errors']and len(report['views'])==36
 template=HERE/'wave_verdant_private_browser_v5_20261018.mjs';tool=HERE/'wave_verdant_dependency_failures_v1_20261018.mjs';assert not tool.exists();text=template.read_text().replace('for(const width of [1280,390])','for(const width of [390])')
 needle="const restored={};for(const uid of model.suppressesBuildingUids||[])"
 assert text.count(needle)==1
 witness="""const ownFallbackFaces=await page.evaluate(uid=>{const r=window.__port;let count=0;for(const e of r.stream.cache.entries.values())for(const mesh of e.buildings.group.children){if(!e.buildings.group.visible||!mesh.visible)continue;const f=mesh.geometry.attributes.feature,idx=mesh.geometry.index;if(!f)continue;for(let i=0;i<(idx?.count??f.count);i+=3){const v=idx?idx.getX(i):i;if(e.data.buildings[Math.round(f.getX(v))]?.uid===uid)count++;}}return count;},model.uid);assert(ownFallbackFaces>0,'Failed original must retain actual visible BASIC triangle faces');"""
 text=text.replace(needle,witness+needle).replace("phase:'failed-download',fallbackRetained:true","phase:'failed-download',ownFallbackFaces,fallbackRetained:true")
 route="async r=>width===390&&(!config.failureTestUids||config.failureTestUids.includes(model.uid))&&!allowed.has(model.uid)?"
 assert text.count(route)==1;text=text.replace(route,"async r=>width===390&&config.blockedAssetUids.includes(model.uid)&&!allowed.has(model.uid)?")
 wait="await page.waitForFunction(uid=>window.__port.officialModels.cache.errors.has(uid),model.uid,{timeout:60000});"
 assert text.count(wait)==1;text=text.replace(wait,"await page.waitForFunction(uid=>window.__port.officialModels.cache.errors.has(uid),config.failedSupportUid,{timeout:60000});")
 assert text.count('allowed.add(model.uid)')==1;text=text.replace('allowed.add(model.uid)','allowed.add(config.failedSupportUid)')
 text=text.replace("phase:'failed-download',ownFallbackFaces","phase:'failed-download',blockedSupportUid:config.failedSupportUid,ownFallbackFaces")
 tool.write_text(text);refs.extend([template,tool]);config=read(STAGE/'browser-config.json');supports={'landsd/275510:0':'landsd/301560:0','landsd/195000:0':'landsd/304885:0'};uids=list(supports);out=[]
 for uid in uids:
  assert reservations.owns(lease)
  case=DOC/uid.replace('/','-').replace(':','-');configpath=case/'browser-config.json';local={**config,'doc':str(case.relative_to(ROOT))+'/','browserUids':[uid],'failureTestUids':[uid],'blockedAssetUids':[supports[uid]],'failedSupportUid':supports[uid],'jointUids':[]};save(configpath,local)
  cmd=['node',str(tool),'staged',str(configpath.relative_to(ROOT))]
  with(case/'browser.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  result=read(case/'staged-browser.json');failures=[v for v in result['views']if v.get('phase')=='failed-download'];success=[v for v in result['views']if 'time'in v]
  ok=proc.returncode==0 and result.get('passed')and not result['errors']and len(failures)==1 and failures[0]['ownFallbackFaces']>0 and len(success)==2
  out.append(dict(uid=uid,passed=bool(ok),exitCode=proc.returncode,failedDownloadViews=failures,recoveredViews=len(success),errors=result['errors']));save(DOC/'progress.json',dict(rows=out));print(out[-1],flush=True)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  if not ok:break
 summary=dict(rows=out,planned=len(uids),completed=len(out),passed=len(out)==len(uids)and all(x['passed']for x in out),fullAcceptance=False,dependencyFailurePropagationTested=True)
 save(DOC/'summary.json',summary);refs.extend(ROOT/p for p in pins)
 result=module('wave_failed_download_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-support-failure-dependent-basic-fallback-retry-v1',list(set(refs)),dict(uids=uids,summary=summary,fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)

def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['private-wave-full-ground-capture'],batch=BATCH,ttl=1800);assert claim['ok'],claim
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

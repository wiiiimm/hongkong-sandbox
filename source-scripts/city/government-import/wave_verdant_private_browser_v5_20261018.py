"""Private joint original-source browser diagnostic; no publication or acceptance credit."""
from pathlib import Path
import os,subprocess,shutil,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from wave_verdant_assembly_four_worlds_v1_20261017 import UIDS as PREVIOUS_UIDS
UIDS=PREVIOUS_UIDS+['landsd/194544:0']
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-private-browser-v5-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NAMES=['government-xl-wave-verdant-current-ground-equivalence-v5-20261018','government-xl-verdant194544-seam-review-v1-20261018','government-xl-verdant195000-seam-review-v1-20261018','government-xl-wave-towers-interface-review-v1-20261018']
def main():
 assert not DOC.exists() and not LOCAL.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in NAMES:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 print('Verified completed receipts and',len(pins),'distinct evidence pins',flush=True)
 sources={r['uid']:r for r in read(BASE/'government-xl-wave-all-original-support-distance-v1-20261017/support-inputs.json')['sources']};sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-podium-support-v1-20261017/support-inputs.json')['sources']});sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-block2-original-recovery-v1-20261017/selection.json.gz')['rows']})
 sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-194544-original-recovery-v1-20261017/selection.json.gz')['rows']})
 cat=read(HERE/'local/government-xl-namcheong244683-private-browser-v2-20261017/catalogue.json');cat['models']=[];cat['counts']={'packedModels':len(UIDS)};forms=[]
 for uid in UIDS:
  r=sources[uid];e=dict(r['candidate']['entry']);e.update(priority='landmark',proceduralWindows=False,placementReviewed=False,publicationApproved=False);dep='landsd/301560:0' if uid in ['landsd/275510:0','landsd/275511:0','landsd/301558:0','landsd/301562:0'] else 'landsd/304885:0' if uid in ['landsd/195000:0','landsd/194520:0','landsd/194544:0'] else None
  e['supportDependencies']=[] if dep is None else [dict(uid=dep,state='candidate',csuid=sources[dep]['candidate']['entry']['buildingCSUID'],sha256=sources[dep]['sourceSHA256'])]
  asset=LOCAL/e['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/r['candidate']['path'],asset);assert digest(asset.read_bytes())==e['sha256'];cat['models'].append(e);forms.append(r['source']['building'])
 save(LOCAL/'catalogue.json',cat);save(LOCAL/'source-forms.json',forms);rel=lambda p:str(p.relative_to(ROOT))
 updates={r['uid']:r for r in read(BASE/'government-xl-wave-multicore-private-basic-estimates-v4-20261017/geometry.json.gz')['rows']};manifest=read(ROOT/'3d-viewer/city/data/manifest.json');replacements=[];found=set()
 for tile in manifest['tiles']:
  if not any(tile['bounds'][0]<=r['sourceBefore']['centre'][0]<=tile['bounds'][2] and tile['bounds'][1]<=r['sourceBefore']['centre'][1]<=tile['bounds'][3]for r in updates.values()):continue
  p=ROOT/'3d-viewer'/tile['url'];data=read(p);changed=False
  for i,b in enumerate(data['buildings']):
   if b['uid'] in updates:
    r=updates[b['uid']];assert b==r['sourceBefore'];data['buildings'][i]=r['privateAfter'];found.add(b['uid']);changed=True
  if changed:
   target=LOCAL/'tiles'/p.name;save(target,data);replacements.append(dict(url=tile['url'],source=rel(target)));refs.append(p)
 assert found==set(updates)
 patch=read(BASE/'government-xl-wave-verdant-current-terrain-rebind-v5-20261018/terrain-candidates.json')[0];assert digest((ROOT/patch['path']).read_bytes())==patch['sha256']
 retained=sorted({r['uid']for r in read(BASE/'government-xl-wave-verdant-current-ground-capture-v5-20261018/basic-actors.json.gz')['rows']}-set(UIDS));views=list(UIDS);bounds=[[min(e['worldBounds'][0][i]for e in cat['models'])for i in range(3)],[max(e['worldBounds'][1][i]for e in cat['models'])for i in range(3)]]
 save(LOCAL/'browser-config.json',dict(stage=rel(LOCAL)+'/',doc=rel(DOC)+'/',catalogueURL='city/data/official-models/'+BATCH+'/catalogue.json',terrain=[dict(source=patch['path'],destination='city/data/'+BATCH+'.json',resolution=1,area='Private Wave/Verdant source terrain')],catalogueReplacements=replacements,browserUids=views,jointUids=[],failureTestUids=[],fitBox=True,retainedBuildingUidsByModel={u:retained for u in views}))
 tool=HERE/'wave_verdant_private_browser_v5_20261018.mjs';original=HERE/'namcheong244683_base_context_browser_v1_20261017.mjs';text=original.read_text();anchor='const retained={};';assert anchor in text;text=text.replace(anchor,'const dependencies=catalogue.models.find(e=>e.uid===model.uid).supportDependencies||[];for(const dep of dependencies){const support=await page.evaluate(uid=>{const d=window.__port.stream.detailedModels.get(uid);return {uid,active:!!d?.active,visible:!!d?.group.visible,...(d?.active?window.__portSolidWitness(uid):{})};},dep.uid);assert(support.active&&support.visible,"Selected source requires active visible original support");assert.equal(support.sourceSHA256,dep.sha256);assert.equal(support.fallbackFaces,0);report.dependencyViews??=[];report.dependencyViews.push({selectedUid:model.uid,width,...support});}const retained={};');needle='for(const uid of config.jointUids){await page.evaluate';assert needle in text;text=text.replace(needle,'for(const uid of config.jointUids){console.log("joint activating",uid);await page.evaluate');needle='},uid,{timeout:60000});}\n   const joint=';assert needle in text;text=text.replace(needle,'},uid,{timeout:60000}).catch(async error=>{report.jointFailure=await page.evaluate(uid=>{const r=window.__port,d=r.stream.detailedModels.get(uid);return {uid,active:!!d?.active,visible:!!d?.group.visible,stats:r.officialModels.stats,wanted:r.officialModels.cache.wanted,drawWanted:[...r.officialModels.drawWanted],cacheError:r.officialModels.cache.errors.get(uid)?.message,loadingPaused:r.officialModels.cache.paused};},uid);console.log(JSON.stringify(report.jointFailure));throw error;});}\n   const joint=');old='`base-context-${label}.png`';assert text.count(old)==1;tool.write_text(text.replace(old,'`base-context-${model.uid.replaceAll("/","-").replaceAll(":","-")}-${label}.png`'));refs.extend([original,tool])
 claim=reservations.claim('wave-joint-browser-'+str(uuid.uuid4()),['private-wave-full-ground-capture'],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();cmd=['node',str(tool),'staged',rel(LOCAL/'browser-config.json')]
  with(DOC/'browser.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'})
  save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode,publication=False,failureRecoveryTested=False))
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
  refs.extend([ROOT/p for p in pins]);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());out=module('wave_joint_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-joint-original-desktop-mobile-diagnostic-v1',list(set(refs)),dict(uids=UIDS,browserExitCode=p.returncode,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

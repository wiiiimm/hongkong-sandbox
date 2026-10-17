"""Whole nine-original staged desktop/mobile view under production selection budgets."""
from pathlib import Path
import os,subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave301562-reviewed-underside-v1-20261018';STAGE=HERE/'local/government-xl-wave-verdant-private-browser-v5-20261018';BATCH='government-xl-wave-verdant-joint-scene-v3-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['private-wave-full-ground-capture'],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  cat=read(STAGE/'catalogue.json');models=cat['models'];uids=[m['uid']for m in models];assert len(uids)==9;bounds=[[min(m['worldBounds'][0][i]for m in models)for i in range(3)],[max(m['worldBounds'][1][i]for m in models)for i in range(3)]];selected='landsd/275510:0';config=read(STAGE/'browser-config.json');config.update(doc=str(DOC.relative_to(ROOT))+'/',browserUids=[selected],jointUids=[],failureTestUids=[],captureBoundsByModel={selected:bounds});save(DOC/'browser-config.json',config)
  template=HERE/'wave_verdant_private_browser_v5_20261018.mjs';tool=HERE/'wave_verdant_joint_scene_v3_20261018.mjs';assert not tool.exists();text=template.read_text();a=text.index('  if(config.jointUids?.length){');z=text.index('  const suppressed={};',a)
  check=r"""  await page.waitForFunction(()=>window.__port.officialModels.stats.pending===0,null,{timeout:60000});
  await page.waitForTimeout(3000);
  await page.evaluate(uid=>{const r=window.__port;r.officialModels.plan(r.camera,{viewportHeight:innerHeight,selectedUid:uid,allowNewLoads:true,force:true});},model.uid);
  await page.waitForTimeout(3000);
  const sceneState=await page.evaluate(async uids=>{
   const r=window.__port,{projectedBounds}=await import('/city/model-spatial-index.js'),matrix=new r.THREE.Matrix4().multiplyMatrices(r.camera.projectionMatrix,r.camera.matrixWorldInverse),frustum=new r.THREE.Frustum().setFromProjectionMatrix(matrix);
   return uids.map(uid=>{const m=r.officialModels.models.get(uid),d=r.stream.detailedModels.get(uid),box=new r.THREE.Box3(new r.THREE.Vector3(...m.worldBounds[0]),new r.THREE.Vector3(...m.worldBounds[1]));let fallbackFaces=0;
    for(const e of r.stream.cache.entries.values())for(const mesh of e.buildings.group.children){if(!e.buildings.group.visible||!mesh.visible)continue;const f=mesh.geometry.attributes.feature,idx=mesh.geometry.index;if(!f)continue;for(let i=0;i<(idx?.count??f.count);i+=3){const v=idx?idx.getX(i):i;if(e.data.buildings[Math.round(f.getX(v))]?.uid===uid)fallbackFaces++;}}
    return {uid,baseLoaded:!!r.stream.getLoadedBuilding(uid),supportAvailable:r.officialModels.supportAvailable(uid,'native'),active:!!d?.active,visible:!!d?.group.visible,wanted:r.officialModels.cache.wanted.includes(uid),drawWanted:r.officialModels.drawWanted.has(uid),frustumEligible:frustum.intersectsBox(box),pixels:projectedBounds(box,matrix,innerWidth,innerHeight).pixels,minPixels:r.officialModels.limits.minPixels,fallbackFaces,sourceSHA256:m.sha256,originalTriangles:d?.active?d.record.modelGeometry.index.length/3:null};});
  },catalogue.models.map(m=>m.uid));
  report.sceneDiagnostics??=[];report.sceneDiagnostics.push({width,models:sceneState});console.log(JSON.stringify({width,models:sceneState}));
  for(const witness of sceneState){const expected=catalogue.models.find(m=>m.uid===witness.uid);assert.equal(witness.sourceSHA256,expected.sha256);assert(witness.frustumEligible,'Shared view must frame every source');if(witness.active){assert(witness.visible);assert.equal(witness.originalTriangles,expected.triangles);assert.equal(witness.fallbackFaces,0);}else{assert(!witness.wanted&&!witness.drawWanted);assert(witness.pixels<witness.minPixels,'Inactive source must be below production detail pixel threshold');assert(witness.fallbackFaces>0,'Inactive detail must retain visible BASIC faces');}}
  report.jointViews??=[];report.jointViews.push({selectedUid:model.uid,width,models:sceneState,productionEligibilityVerified:true});
"""
  text=text[:a]+check+text[z:];tool.write_text(text);refs.extend([template,tool]);cmd=['node',str(tool),'staged',str((DOC/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=proc.returncode,fullAcceptance=False));report=read(DOC/'staged-browser.json');summary=dict(passed=proc.returncode==0 and report.get('passed')is True,errors=report['errors'],jointViews=len(report.get('jointViews',[])),fullAcceptance=False,productionBudgetsUnchanged=True);save(DOC/'summary.json',summary)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  refs.extend(ROOT/p for p in pins);out=module('wave_joint_scene_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-joint-scene-production-eligibility-v2',list(set(refs)),dict(uids=uids,summary=summary,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

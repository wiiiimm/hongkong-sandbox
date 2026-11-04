"""Private focused source views; report camera collision/terrain without granting acceptance."""
import os,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-private-browser-v5-20261018';STAGE=HERE/'local'/PRIOR.name
BATCH='government-xl-wave301562-focused-context-v3-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['private-wave-full-ground-capture'],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  config=read(STAGE/'browser-config.json');config.update(doc=str(DOC.relative_to(ROOT))+'/',browserUids=['landsd/301562:0'],failureTestUids=[],captureDirectionByModel={'landsd/301562:0':[.8,.5,-.6]});save(DOC/'browser-config.json',config)
  template=HERE/'wave_verdant_private_browser_v5_20261018.mjs';tool=HERE/'wave301562_focused_context_v3_20261018.mjs';assert not tool.exists();text=template.read_text().replace('for(const width of [1280,390])','for(const width of [1280])')
  old="[['east',[65,25,0]],['west',[-65,25,0]],['north',[0,25,-65]],['south',[0,25,65]]]";new="[['northeast-close',[8,4,-8]],['ramp-low',[-2,-1.8,-6]],['outer-low',[8,-1,-3]],['north-close',[0,3,-10]]]";assert old in text;text=text.replace(old,new)
  old='c=[(a[0]+b[0])/2,10,(a[2]+b[2])/2]';assert text.count(old)==1;text=text.replace(old,'c=[-18322.7314453125,15.2826665,-10190.749349]')
  old='target:window.__port.controls.target.toArray()';assert text.count(old)==1;text=text.replace(old,old+',cameraGroundSampler:window.__port.sampler.height(window.__port.camera.position.x,window.__port.camera.position.z),cameraCollisionUid:window.__port.stream.collision(window.__port.camera.position.x,window.__port.camera.position.z,window.__port.camera.position.y-.1,window.__port.camera.position.y+.1,.1)?.uid??null')
  clamp='r.controls.enableDamping=false;r.controls.target.fromArray(c);r.camera.position.fromArray(c).add(new r.THREE.Vector3(...offset));';assert text.count(clamp)==1;text=text.replace(clamp,'r.controls.enableDamping=false;r.controls.minDistance=0;r.controls.maxPolarAngle=Math.PI;r.controls.target.fromArray(c);r.camera.position.fromArray(c).add(new r.THREE.Vector3(...offset));')
  diagnostic=r"""const extra=await page.evaluate(async()=>{
    const r=window.__port,p=r.camera.position,bottom=p.y-.1,top=p.y+.1,radius=.1;
    const {collisionVolumes}=await import('/city/building-geometry.js');
    const {modelSurfaceCollision,modelRoofHeight}=await import('/city/model-collision.js');
    const {inPolygon}=await import('/city/geo.js');
    const volumes=[];
    for(const d of r.stream.detailedModels.values())if(d.active)for(const v of collisionVolumes(d.record)){
      const [x0,z0,x1,z1]=v.bounds;
      if(top<=v.bottom||bottom>=v.top||p.x+radius<x0||p.x-radius>x1||p.z+radius<z0||p.z-radius>z1)continue;
      const roof=v.model?modelRoofHeight(v.model,p.x,p.z):null;
      const hit=v.kind==='model-surface'?modelSurfaceCollision(v.model,p.x,p.z,bottom,top,radius):v.kind==='model-interior'?inPolygon(p.x,p.z,v.rings)&&roof!==null&&bottom<roof:null;
      volumes.push({uid:d.record.uid,kind:v.kind,hit,roof});
    }
    const direction=r.controls.target.clone().sub(p),distance=direction.length();
    const ray=new r.THREE.Raycaster(p,direction.normalize(),0,distance+.05);
    const hits=ray.intersectObjects(r.stream.pickMeshes(ray.ray),false);
    const describe=hit=>{if(!hit)return null;const a=hit.object.geometry.attributes.position;return {uid:r.stream.featureAt(hit)?.uid??null,distance:hit.distance,point:hit.point.toArray(),faceIndex:hit.faceIndex,triangle:[hit.face.a,hit.face.b,hit.face.c].map(i=>new r.THREE.Vector3().fromBufferAttribute(a,i).applyMatrix4(hit.object.matrixWorld).toArray())};};
    const terrainHit=ray.intersectObject(r.terrain,true)[0];
    return {collisionVolumes:volumes,viewRay:{distance,firstBuilding:describe(hits[0]),firstTerrain:terrainHit?{distance:terrainHit.distance,point:terrainHit.point.toArray(),faceIndex:terrainHit.faceIndex}:null}};
  });Object.assign(witness,extra);"""
  marker='assert.equal(witness.sourceSHA256,model.sha256);';assert text.count(marker)==1;text=text.replace(marker,diagnostic+marker)
  tool.write_text(text);refs.extend([template,tool]);cmd=['node',str(tool),'staged',str((DOC/'browser-config.json').relative_to(ROOT))]
  with(DOC/'browser.log').open('w')as log:proc=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=900)
  save(DOC/'command.json',dict(command=cmd,exitCode=proc.returncode,diagnosticOnly=True,fullAcceptance=False))
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  refs.extend(ROOT/p for p in pins);out=module('wave_focused_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-original-service-source-unclamped-collision-kind-and-ray-v3',list(set(refs)),dict(uids=['landsd/301562:0'],browserExitCode=proc.returncode,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

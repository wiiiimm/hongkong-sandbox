"""Nominate a diagnostic camera from authenticated terrain or complete model scope."""
import argparse,itertools,re
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','scope','inventory','uid']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not doc.exists()
 refs=[Path(__file__)];pins={}
 for name in [a.runtime,a.scope,a.inventory]:
  _,p=authenticate(base/name);pins.update(p);refs.append(base/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selected=take(base/a.runtime/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 staged=take(HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows'];g=next(r for r in staged if r['uid']==a.uid)
 vertices=np.asarray(g['position']).reshape(-1,3);lo,hi=vertices.min(0),vertices.max(0);centre=(lo+hi)/2;corners=np.asarray(list(itertools.product(*zip(lo,hi))))-centre
 samples=np.unique(vertices,axis=0);samples=samples[np.linspace(0,len(samples)-1,min(600,len(samples)),dtype=int)]
 inventory=take(base/a.inventory/'complete-bounds.json.gz');native={r['uid']:r for r in inventory['rows']};boxes=[];stageduids={r['uid']for r in staged}
 for other in staged:
  if other['uid']==a.uid:continue
  pts=np.asarray(other['position']).reshape(-1,3);boxes.append([pts.min(0).tolist(),pts.max(0).tolist()])
 for uid,r in native.items():
  if uid in stageduids:continue
  bounds=np.asarray(r['completeFourWorldBounds']);assert bounds.shape==(4,2,3)
  boxes.append([bounds[:,0].min(0),bounds[:,1].max(0)])
 scope=take(base/a.scope/'summary.json')
 assert scope.get('currentManifestSHA256',selected['manifestSHA256'])==selected['manifestSHA256']
 if (base/a.scope/'form-obligations.json.gz').exists():
  forms=take(base/a.scope/'form-obligations.json.gz')
 else:
  assert a.uid in scope['uids'] and scope['status']=='model-only-current-collision-scope'
  forms=[r['building']for r in take(base/a.scope/(a.uid.split('/')[1]+'-forms.json.gz'))]
  assert len(forms)==next(r for r in scope['rows']if r['uid']==a.uid)['currentFormsWithinTwoMetreRegion']
 for f in forms:
  if f['uid']in stageduids or f['uid']in native:continue
  xz=np.asarray([p for ring in f['rings']for p in ring]);low,high=xz.min(0),xz.max(0);y=f.get('base',0)
  boxes.append([[low[0],y,low[1]],[high[0],y+f['height'],high[1]]])
 boxes=np.asarray(boxes);app=ROOT/'3d-viewer/city/app.js';appsha=digest(app.read_bytes());refs.append(app)
 fov=float(re.search(r'PerspectiveCamera\((\d+(?:\.\d+)?),',app.read_text()).group(1));tanv=np.tan(np.deg2rad(fov/2));rows=[]
 for elevation in [.7,1.2,1.8]:
  for angle in np.arange(8)*np.pi/4:
   direction=np.asarray([np.cos(angle),elevation,np.sin(angle)]);direction=np.round(direction,6);direction/=np.linalg.norm(direction)
   right=np.cross([0,1,0],direction);right/=np.linalg.norm(right);up=np.cross(direction,right);profiles=[]
   for width in [390,1280]:
    tanh=tanv*width/900;distance=max(np.max(corners@direction+np.abs(corners@right)/tanh),np.max(corners@direction+np.abs(corners@up)/tanv))*1.04;camera=centre+direction*distance
    low=np.minimum(camera,lo);high=np.maximum(camera,hi);active=boxes[np.all(boxes[:,1]>=low,axis=1)&np.all(boxes[:,0]<=high,axis=1)]
    blocked=np.zeros(len(samples),dtype=bool);ray=samples-camera
    for box in active:
     parallel=np.abs(ray)<1e-14;inside=(camera>=box[0])&(camera<=box[1]);valid=np.all(~parallel|inside,axis=1)
     with np.errstate(divide='ignore',invalid='ignore'):
      t0=(box[0]-camera)/ray;t1=(box[1]-camera)/ray
     enter=np.where(parallel,-np.inf,np.minimum(t0,t1)).max(1);leave=np.where(parallel,np.inf,np.maximum(t0,t1)).min(1)
     blocked|=valid&(leave>=np.maximum(enter,0))&(enter<.99999)&(leave>0)
    profiles.append(dict(width=width,unblockedSampleFraction=float((~blocked).mean()),candidateBoxes=len(active),camera=camera.tolist()))
   rows.append(dict(direction=np.round([np.cos(angle),elevation,np.sin(angle)],6).tolist(),profiles=profiles,minimumUnblockedFraction=min(p['unblockedSampleFraction']for p in profiles),elevation=elevation))
 chosen=max(rows,key=lambda r:(r['minimumUnblockedFraction'],-abs(r['elevation']-1.2)))
 assert digest(app.read_bytes())==appsha and digest(manifest.read_bytes())==selected['manifestSHA256']
 report=dict(uids=[a.uid],sourceSHA256=g['sourceSHA256'],currentManifestSHA256=selected['manifestSHA256'],sourceWorldVertexSHA256=digest(vertices.tobytes()),sampledSourceVertices=len(samples),cameraFieldOfViewDegrees=fov,viewportHeight=900,cameraDirection=chosen['direction'],chosen=chosen,candidates=rows,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,qualification='Camera nomination only. Union of four-world native bounds and approximate current basic-form boxes estimates foreign-actor obstruction in both viewports. All other actual staged-source bounds are included alongside native/basic context. No terrain/self-occlusion or visual approval claim; actual browser exports must still be inspected.')
 save(doc/'summary.json',report)
 module('capture_direction_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-original-diagnostic-camera-nomination',refs,report)
 print(dict(direction=report['cameraDirection'],minimumUnblockedFraction=chosen['minimumUnblockedFraction']),flush=True)
if __name__=='__main__':main()

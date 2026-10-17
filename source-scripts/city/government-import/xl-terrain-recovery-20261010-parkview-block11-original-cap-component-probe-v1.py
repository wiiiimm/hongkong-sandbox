"""Complete untouched source partitions around Parkview11's exact native cap.

Source-only causal checkpoint; no current terrain, physical or native approval.
Every source face is partitioned; complete cap-component attachments are measured
with exact rational original triangle intersections, without geometry welding.
"""
import json,importlib.util,uuid,time
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='xl-terrain-recovery-20261010-parkview-block11-original-cap-component-probe-v1';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
SCOUT=BASE/'xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1'
UID='landsd/255647:0';NATIVE='landsd/254491:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def partition(t):
 parent=list(range(len(t)));edges={}
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,face in enumerate(t):
  v=[tuple(p)for p in face]
  for a,b in zip(v,v[1:]+v[:1]):
   e=tuple(sorted((a,b)))
   if e in edges:parent[find(i)]=find(edges[e])
   else:edges[e]=i
 groups={}
 for i in range(len(t)):groups.setdefault(find(i),[]).append(i)
 return [dict(originalFaces=f,bounds=[t[f].min(axis=(0,1)).tolist(),t[f].max(axis=(0,1)).tolist()])for f in sorted(groups.values(),key=lambda f:min(f))]
def main():
 assert not DOC.exists();r=next(r for r in read(SCOUT/'diagnostic.json.gz')['rows']if r['uid']==UID);assert len(r['completeCandidateNativeInventory'])==1;n=r['completeCandidateNativeInventory'][0];assert n['uid']==NATIVE
 claim=reservations.claim('parkview11-original-cap-'+str(uuid.uuid4()),['building:'+UID,'building:'+NATIVE],batch=BATCH,ttl=3600);assert claim['ok'];lease=json.loads(json.dumps(claim['reservation'],default=str));save(HERE/'local'/BATCH/'reservation.json',lease)
 try:
  asset=ROOT/r['cachedSource']['path'];na=ROOT/n['asset']['path'];raw=asset.read_bytes();nr=na.read_bytes();assert digest(raw)==r['sourceSHA256'] and digest(nr)==n['sourceSHA256'];a=decode_original_world_triangles(raw);b=decode_original_world_triangles(nr);assert len(a)==10679 and len(b)==63133
  ac=partition(a);bc=partition(b);cap=r['exactOriginalNativeCapContacts'][0];assert cap['nativeOriginalUpwardCapFace']==57951 and cap['ownedOriginalFace']==0
  own=next(i for i,c in enumerate(ac)if 0 in c['originalFaces']);carrier=next(i for i,c in enumerate(bc)if 57951 in c['originalFaces']);print(dict(ownedParts=len(ac),nativeParts=len(bc),ownedMainPart=own,nativeCarrierPart=carrier,nativeCarrierFaces=len(bc[carrier]['originalFaces'])),flush=True)
  bf=np.asarray(bc[carrier]['originalFaces'],int);tree=shapely.STRtree(shapely.box(b[bf,:,0].min(1),b[bf,:,2].min(1),b[bf,:,0].max(1),b[bf,:,2].max(1)));contacts=[];tested=0;cached={};heartbeat=time.monotonic()
  def face(actor,i):
   key=(actor,i)
   if key not in cached:cached[key]=rational_face((a if actor=='own'else b)[i])
   return cached[key]
  for ci,c in enumerate(ac):
   if np.any(np.maximum(c['bounds'][0],bc[carrier]['bounds'][0])>np.minimum(c['bounds'][1],bc[carrier]['bounds'][1])):continue
   witness=None
   for i in c['originalFaces']:
    t=a[i]
    if not np.any(np.cross(t[1]-t[0],t[2]-t[0])):continue
    for k in tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())):
     j=int(bf[k]);u=b[j]
     if t[:,1].max()<u[:,1].min()or u[:,1].max()<t[:,1].min():continue
     if not np.any(np.cross(u[1]-u[0],u[2]-u[0])):continue
     tested+=1;points=intersection_points(face('own',i),face('native',j))
     if len(points)>=2:witness=dict(ownedComponent=ci,ownedFace=i,nativeCarrierComponent=carrier,nativeFace=j,exactPositiveContactVertices=[[str(x)for x in p]for p in points]);break
    if witness:break
   if witness:contacts.append(witness)
   if time.monotonic()-heartbeat>=20:assert reservations.heartbeat(lease)['ok'];heartbeat=time.monotonic();print(dict(component=ci,completeOwnParts=len(ac),positiveCarrierContacts=len(contacts),exactPairs=tested),flush=True)
  result=dict(uids=[UID,NATIVE],sourceOnly=True,fullAcceptance=False,nativeReacceptance=False,newlyInstalled=0,ownedSource=ref(asset),retainedNativeSource=ref(na),ownedSourceStreamBinding=source_stream_binding(raw),nativeSourceStreamBinding=source_stream_binding(nr),ownedOriginalWorldSHA256=digest(a.tobytes()),nativeOriginalWorldSHA256=digest(b.tobytes()),completeOriginalOwnedFaces=len(a),completeOriginalNativeFaces=len(b),ownedComponents=ac,nativeComponents=bc,qualifiedCapSourceDiagnosticOnly=cap,ownedMainComponent=own,nativeCarrierComponent=carrier,ownedToCarrierExactContacts=contacts,exactTrianglePairsTested=tested,sourceGeometryChanges=0,qualification='Complete untouched original partitions and exact positive-dimensional carrier attachments only. No ground/cap clearance, component root, current identity/foreign/runtime/native reacceptance or installation credit. Every detached owned and native source part remains in the complete inventory for subsequent full checks.')
  save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('parkview_original_cap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-parkview11-carrier-component-causal-probe-v1',[Path(__file__),asset,na,SCOUT/'diagnostic.json.gz',ROOT/r['cachedSelection']['path'],ROOT/n['catalogue']['path'],HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl_source_stream_binding_20261009.py'],result)
  print(dict(sourceOnly=True,ownedParts=len(ac),nativeParts=len(bc),positiveCarrierContacts=len(contacts),fullAcceptance=False),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Source-only exact positive-dimensional graph of both complete Langham originals.

Nonzero shared-edge bodies replace vertex gluing. One recomputed exact witness
per contacting body pair proves geometry only, never load bearing/root/native
acceptance. Exact zero-area faces stay enumerated and cannot bridge bodies.
"""
import importlib.util,json,time,uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-langham-upper-current-native-original-interfaces-v2';UIDS=['landsd/79318:0','landsd/224399:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();prior=read(PRIOR/'diagnostic.json.gz');receipt=read(PRIOR/'result.json')
 with connect()as con:con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assets=[];worlds=[];inventories=[];components=[];offset=0
 for uid in UIDS:
  asset=next(ROOT/r['path']for r in prior['evidenceRefs']if r['sha256']==prior['completeSourceSHA256'][uid]);assert digest(asset.read_bytes())==prior['completeSourceSHA256'][uid]
  world=decode_original_world_triangles(asset.read_bytes());assert digest(world.tobytes())==prior['completeOriginalWorldSHA256'][uid]
  inv=census(world,list(range(len(world))));inventories.append(inv);assets.append(asset);worlds.append(world)
  for local in inv['sharedEdgeConnectedComponents']:
   faces=[offset+i for i in local];part=world[local];components.append(dict(actorUID=uid,globalOriginalFaces=faces,bounds=[part.min(axis=(0,1)).tolist(),part.max(axis=(0,1)).tolist()]))
  offset+=len(world)
 tri=np.concatenate(worlds);members={f:i for i,c in enumerate(components)for f in c['globalOriginalFaces']};zero=[i for i in range(len(tri))if i not in members];assert len(members)+len(zero)==len(tri)
 binding=dict(completeOriginalWorldSHA256=digest(tri.tobytes()),completeComponentsSHA256=canonical(components),priorDiagnostic=ref(PRIOR/'diagnostic.json.gz'),priorReceipt=ref(PRIOR/'result.json'),producer=ref(Path(__file__)))
 helper_paths=[HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']];helper_refs=[ref(p)for p in helper_paths];binding['helpers']=helper_refs
 initial_refs=[binding['producer'],ref(PRIOR/'diagnostic.json.gz'),ref(PRIOR/'result.json'),*map(ref,assets),*helper_refs]
 progress_path=HERE/'local'/BATCH/'compute-progress.json.gz';contacts={};tested=0;next_component=0
 if progress_path.exists():
  progress=read(progress_path);assert progress['binding']==binding;contacts={tuple(p['components']):p for p in progress['contacts']};tested=progress['exactPairsTested'];next_component=progress['nextComponent'];assert type(next_component)is int and 0<=next_component<=len(components)
 else:
  boundary=len(worlds[0])
  for record in prior['completeEveryRenderableOriginalFacePairContactInventory']['contacts']:
   assert record['dimension']>0
   a,b=int(record['sourceFaceA']),boundary+int(record['sourceFaceB']);ca,cb=members[a],members[b];key=tuple(sorted([ca,cb]));contacts.setdefault(key,dict(components=list(key),globalOriginalFaces=[a,b],reusedCompleteCrossActorContactInventory=True))
 claim=reservations.claim('langham-source-edge-graph-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last_pulse=time.monotonic();last_output=last_pulse;rational={}
 def pulse(force=False):
  nonlocal last_pulse
  if force or time.monotonic()-last_pulse>=20:assert reservations.heartbeat(lease)['ok'];last_pulse=time.monotonic()
 def exact(i):
  if i not in rational:rational[i]=rational_face(tri[i])
  return rational[i]
 try:
  lower=np.asarray([c['bounds'][0]for c in components]);upper=np.asarray([c['bounds'][1]for c in components]);trees={}
  for a in range(next_component,len(components)):
   ca=components[a];hits=np.flatnonzero(np.all(upper>=lower[a],axis=1)&np.all(lower<=upper[a],axis=1))
   for b in hits:
    b=int(b)
    if b<=a or (a,b)in contacts or ca['actorUID']!=components[b]['actorUID']:continue
    af=ca['globalOriginalFaces'];bf=components[b]['globalOriginalFaces'];small,large=(af,bf)if len(af)<=len(bf)else(bf,af);large_key=a if large is af else b
    if large_key not in trees:
     ids=np.asarray(large,int);t=tri[ids];trees[large_key]=(ids,shapely.STRtree(shapely.box(t[:,:,0].min(axis=1),t[:,:,2].min(axis=1),t[:,:,0].max(axis=1),t[:,:,2].max(axis=1))))
    ids,tree=trees[large_key];witness=None
    for i in small:
     t=tri[i]
     for k in tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())):
      j=int(ids[k]);u=tri[j]
      if np.any(t.min(axis=0)>u.max(axis=0))or np.any(u.min(axis=0)>t.max(axis=0)):continue
      tested+=1
      if tested%250==0:pulse()
      pts=intersection_points(exact(i),exact(j))
      if len(pts)>=2:witness=[i,j]if members[i]==a else[j,i];break
     if witness:break
    if witness:contacts[(a,b)]=dict(components=[a,b],globalOriginalFaces=witness,reusedCompleteCrossActorContactInventory=False)
   if (a+1)%8==0 or a+1==len(components):save(progress_path,dict(binding=binding,nextComponent=a+1,contacts=list(contacts.values()),exactPairsTested=tested,completeProof=False,currentAcceptance=False))
   pulse()
   if time.monotonic()-last_output>=20:print(dict(component=a+1,total=len(components),contactPairs=len(contacts),exactPairsTested=tested),flush=True);last_output=time.monotonic()
  pulse(True);adj={i:set()for i in range(len(components))};verified=[]
  for key,p in sorted(contacts.items()):
   a,b=p['globalOriginalFaces'];assert [members[a],members[b]]==p['components'];pts=intersection_points(exact(a),exact(b));assert len(pts)>=2
   measure=contact_measure(pts);assert measure['dimension']>0;verified.append(dict(**p,exactContact=measure));x,y=key;adj[x].add(y);adj[y].add(x);pulse()
  native={i for i,c in enumerate(components)if c['actorUID']==UIDS[1]};reached=set(native);stack=list(native)
  while stack:
   a=stack.pop()
   for b in adj[a]-reached:reached.add(b);stack.append(b)
  by_uid={uid:dict(edgeBodies=sum(c['actorUID']==uid for c in components),geometricPathToSomeNativeBody=sum(c['actorUID']==uid and i in reached for i,c in enumerate(components)),unresolvedBodyFaces=sum(len(c['globalOriginalFaces'])for i,c in enumerate(components)if c['actorUID']==uid and i not in reached))for uid in UIDS}
  refs=[*initial_refs,ref(progress_path)];assert all(ref(ROOT/r['path'])==r for r in refs);pulse(True)
  result=dict(uids=UIDS,binding=binding,completeOriginalFaces=len(tri),completeEdgeCensus=inventories,components=components,exactNonrenderingGlobalFacesRetained=zero,completeRenderableComponentsAccounted=True,oneExactPositiveWitnessPerContactingBodyPair=verified,completeComponentPairDiscovery=True,exactPairsTested=tested,summary=by_uid,geometricReachabilitySeedsOnly='Every original native body, including unqualified bodies; not roots or acceptance',allNativeNegativesPreserved=True,nativeReacceptance=False,rootOrStructuralContactCredit=False,sourceOnly=True,noFreshCurrentCapture=True,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('langham_edge_graph_freeze',helper_paths[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-langham-original-nonzero-edge-positive-contact-graph-source-only-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,completeOriginalFaces=len(tri),completeEdgeBodies=len(components),positiveBodyContactPairs=len(verified),summary=by_uid,newlyInstalled=0));print(dict(summary=by_uid,positiveBodyContactPairs=len(verified)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

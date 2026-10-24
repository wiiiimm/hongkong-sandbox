"""Complete owned-involving original edge-body contacts for Elements towers.

All four original sources remain complete. Native/native body pairs are outside
this contact scope and no native body is a root seed. Positive intersections
prove only geometry, never exposure, structural support or current acceptance.
"""
from pathlib import Path
import importlib.util,json,time,uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011';ATTRIBUTES=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
OWN=['landsd/204145:0','landsd/204143:0'];NATIVE=['landsd/273061:0','landsd/204144:0'];UIDS=OWN+NATIVE;COUNTS=[12129,11680,203738,11166]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(x):return digest(json.dumps(x,sort_keys=True,separators=(',',':')).encode())
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [PHYSICAL,ATTRIBUTES]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 physical_receipt=read(PHYSICAL/'result.json');bound={r['path']:r for r in physical_receipt['evidenceRefs']}
 for path in [PHYSICAL/'selection.json.gz',PHYSICAL/'current-source-terrain-preflight.json',PHYSICAL/'historical-current-manifest.json',PHYSICAL/'native-neighbour-checks.json']:
  assert bound[str(path.relative_to(ROOT))]==ref(path);refs.append(ref(path))
 rows=read(PHYSICAL/'selection.json.gz')['rows'];assert[r['uid']for r in rows]==OWN
 retained=read(PHYSICAL/'current-source-terrain-preflight.json')['completeRetainedNativeEntries'];assert[r['uid']for r in retained]==NATIVE
 inputs=[dict(uid=r['uid'],asset=ref(ROOT/r['candidate']['path']),sourceSHA256=r['sourceSHA256'])for r in rows]
 inputs.extend(dict(uid=r['uid'],asset=r['source'],sourceSHA256=r['entry']['sha256'],rawCurrentNativeEntry=r['entry'])for r in retained)
 worlds=[];inventories=[];components=[];offset=0
 for source,count in zip(inputs,COUNTS):
  asset=ROOT/source['asset']['path'];assert ref(asset)==source['asset']and source['asset']['sha256']==source['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());assert len(world)==count
  inventory=census(world,list(range(count)));inventories.append(dict(uid=source['uid'],census=inventory));worlds.append(world);refs.append(ref(asset))
  for local in inventory['sharedEdgeConnectedComponents']:
   part=world[local];components.append(dict(actorUID=source['uid'],globalOriginalFaces=[offset+i for i in local],bounds=[part.min(axis=(0,1)).tolist(),part.max(axis=(0,1)).tolist()]))
  offset+=count
 assert [len(r['census']['sharedEdgeConnectedComponents'])for r in inventories[:2]]==[655,343]
 assert [len(r['census']['exactNonrenderingOriginalFaces'])for r in inventories[:2]]==[15,32]
 assert [len(r['census']['sharedEdgeConnectedComponents'])for r in inventories[2:]]==[300,447]
 assert [len(r['census']['exactNonrenderingOriginalFaces'])for r in inventories[2:]]==[74,29]
 tri=np.concatenate(worlds);assert len(tri)==238713;members={f:i for i,c in enumerate(components)for f in c['globalOriginalFaces']};zero=[i for i in range(len(tri))if i not in members];assert len(members)+len(zero)==len(tri)
 helpers=[HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']];refs.extend(ref(p)for p in helpers)
 binding=dict(completeOriginalWorldSHA256=digest(tri.tobytes()),completeComponentsSHA256=canonical(components),completeSourceInputs=inputs,physicalReceipt=ref(PHYSICAL/'result.json'),attributeReceipt=ref(ATTRIBUTES/'result.json'),helpers=[ref(p)for p in helpers],producer=ref(Path(__file__)),scope='Every distinct body pair involving at least one owned actor; native-native pairs excluded.')
 progress_path=HERE/'local'/BATCH/'compute-progress.json.gz';contacts={};tested=0;next_component=0
 if progress_path.exists():
  progress=read(progress_path);assert progress['binding']==binding;contacts={tuple(p['components']):p for p in progress['contacts']};tested=progress['exactPairsTested'];next_component=progress['nextComponent'];assert type(next_component)is int and 0<=next_component<=len(components)
 claim=reservations.claim('elements-owned-original-contacts-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last_pulse=time.monotonic();last_output=last_pulse;rational={}
 def pulse(force=False):
  nonlocal last_pulse
  if force or time.monotonic()-last_pulse>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last_pulse=time.monotonic()
 def exact(i):
  if i not in rational:rational[i]=rational_face(tri[i])
  return rational[i]
 try:
  lower=np.asarray([c['bounds'][0]for c in components]);upper=np.asarray([c['bounds'][1]for c in components]);trees={};candidate_pairs=[]
  for a,component in enumerate(components):
   if component['actorUID']not in OWN:continue
   candidate_pairs.extend([a,int(b)]for b in np.flatnonzero(np.all(upper>=lower[a],axis=1)&np.all(lower<=upper[a],axis=1))if b>a)
  eligible_pairs=998*997//2+998*747
  for a in range(next_component,len(components)):
   ca=components[a];hits=np.flatnonzero(np.all(upper>=lower[a],axis=1)&np.all(lower<=upper[a],axis=1))
   for b in hits:
    b=int(b)
    if b<=a or (a,b)in contacts or not({ca['actorUID'],components[b]['actorUID']}&set(OWN)):continue
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
      points=intersection_points(exact(i),exact(j))
      if len(points)>=2:witness=[i,j]if members[i]==a else[j,i];break
     if witness:break
    if witness:contacts[(a,b)]=dict(components=[a,b],globalOriginalFaces=witness)
   if (a+1)%8==0 or a+1==len(components):save(progress_path,dict(binding=binding,nextComponent=a+1,contacts=list(contacts.values()),exactPairsTested=tested,completeProof=False,currentAcceptance=False))
   pulse()
   if time.monotonic()-last_output>=20:print(dict(component=a+1,total=len(components),contactPairs=len(contacts),exactPairsTested=tested),flush=True);last_output=time.monotonic()
  verified=[]
  for key,p in sorted(contacts.items()):
   a,b=p['globalOriginalFaces'];assert[members[a],members[b]]==p['components'];measure=contact_measure(intersection_points(exact(a),exact(b)));assert measure['dimension']>0;verified.append(dict(**p,exactContact=measure));pulse()
  summary={uid:dict(completeOriginalFaces=count,nonzeroEdgeBodies=len(inv['census']['sharedEdgeConnectedComponents']),exactZeroFaces=len(inv['census']['exactNonrenderingOriginalFaces']))for uid,count,inv in zip(UIDS,COUNTS,inventories)}
  pulse(True);refs.append(ref(progress_path));assert all(ref(ROOT/r['path'])==r for r in refs)
  result=dict(uids=UIDS,binding=binding,completeOriginalFaces=len(tri),completeOwnedOriginalFaces=23809,completeEdgeCensus=inventories,components=components,exactNonrenderingGlobalFacesRetained=zero,completeRenderableComponentsAccounted=True,exactInclusiveBodyBoundsCandidatePairs=candidate_pairs,eligibleOwnedInvolvingBodyPairs=eligible_pairs,strictlyAABBDisjointOwnedInvolvingBodyPairs=eligible_pairs-len(candidate_pairs),broadphase='Complete original binary-coordinate body/face min/max bounds; closed inclusive comparisons and STRtree envelope candidates; touching and collapsed projections retained.',oneExactPositiveWitnessPerOwnedInvolvingBodyPair=verified,completeOwnedInvolvingComponentPairDiscovery=True,nativeNativeComponentPairsExamined=False,exactPairsTested=tested,summary=summary,nativeBodiesReceiveNoRootSeed=True,nonrenderingFacesReceiveNoSupportOrBridgeCredit=True,allNativeNegativesPreserved=True,nativeReacceptance=False,rootOrStructuralContactCredit=False,sourceOnly=True,frozenBaselineManifest=ref(PHYSICAL/'historical-current-manifest.json'),noFreshCurrentCapture=True,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('elements_owned_contact_freeze',helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-elements-owned-original-edge-body-contact-discovery-source-only-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,completeOriginalFaces=len(tri),completeOwnedOriginalFaces=23809,completeOwnedBodies=998,positiveOwnedInvolvingBodyPairs=len(verified),summary=summary,nativeReacceptance=False,newlyInstalled=0));print(dict(summary=summary,positiveOwnedInvolvingBodyPairs=len(verified)),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

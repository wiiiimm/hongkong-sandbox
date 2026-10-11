"""Replay original nonzero edge-body interfaces in four frozen representations.

Only the genuine main podium body is the conditional graph seed. All207 tower
details and both unqualified podium details are forbidden bridges. This remains
source-only geometry: exposed grade/cap, mounting and all current gates must be
composed separately. No epsilon, vertex glue or changed original source mesh.
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
BASE=ROOT/'docs/astra-city/government-import'; BATCH='xl-terrain-recovery-20261011-mount-verdant-four-stream-restricted-source-contacts-v1'; DOC=BASE/BATCH; LOCAL=HERE/'local'/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-mount-verdant-complete-original-edge-contact-graph-v1'; CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'; BACKS=BASE/'xl-terrain-recovery-20261011-mount-verdant-207-original-complete-back-associations-v1'; GRADE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-four-stream-authentic-grade-cap-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists(); refs=[ref(Path(__file__))]; receipts={}
 for folder in [GRAPH,CAPTURE,BACKS,GRADE]:
  r=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY'); assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r; refs.append(ref(folder/'result.json'))
 def bound(folder,name):
  p=folder/name; assert ref(p) in receipts[folder.name]['evidenceRefs']; refs.append(ref(p)); return read(p)
 graph=bound(GRAPH,'diagnostic.json.gz'); source=bound(CAPTURE,'literal-source-inputs.json.gz'); actual=bound(CAPTURE,'actual-render-attributes.json.gz'); backs=bound(BACKS,'diagnostic.json.gz'); grade=bound(GRADE,'diagnostic.json.gz'); worlds=[[],[],[],[]]; uids=['landsd/261717:0','landsd/75782:0']; assert [r['uid'] for r in source['rows']]==[r['uid'] for r in actual['rows']]==uids
 for row,record,count in zip(source['rows'],actual['rows'],[14938,641]):
  p=ROOT/row['path']; assert digest(p.read_bytes())==row['entry']['sha256']==record['sourceSHA256']; refs.append(ref(p)); tri=decode_original_world_triangles(p.read_bytes()); index=np.asarray(record['completeOriginalIndex'],np.uint32).reshape(-1,3); assert tri.shape==(count,3,3) and len(index)==count; worlds[0].append(tri)
  for k,key in enumerate(['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition'],1): worlds[k].append(np.asarray(record[key],float).reshape(-1,3)[index])
 worlds=[np.concatenate(w) for w in worlds]; assert all(w.shape==(15579,3,3) and np.isfinite(w).all() for w in worlds); assert digest(worlds[0].tobytes())==graph['binding']['completeOriginalWorldSHA256']; components=graph['components']; assert len(components)==973
 excluded=sorted([r['originalBody'] for r in backs['all207Bodies2682Faces']]+[967,972]); assert len(excluded)==209; assert components[966]['globalOriginalFaces']==[14938+i for i in grade['rows'][0]['complete576MainBodyFaces']]; assert len(components[967]['globalOriginalFaces'])==10 and len(components[972]['globalOriginalFaces'])==12
 allowed=sorted(set(range(973))-set(excluded)); assert len(allowed)==764; allowedset=set(allowed); originals=graph['oneExactPositiveWitnessPerContactingBodyPair']; selected=[r for r in originals if set(r['components'])<=allowedset]; assert all(len(r['globalOriginalFaces'])==2 for r in selected)
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py']; refs.extend(ref(HERE/n) for n in helpers)
 claim=reservations.claim('mount-restricted-source-contacts-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600); assert claim['ok']; lease=claim['reservation']; last=time.monotonic(); rows=[]; names=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20: assert reservations.heartbeat(lease)['ok']; last=time.monotonic(); print(json.dumps(dict(completedStreams=len(rows))),flush=True)
 try:
  for mode,world in zip(names,worlds):
   inventories=[census(world[:14938],list(range(14938))),census(world[14938:],list(range(641)))]; reconstructed=[]; zero=[]
   for offset,inv in zip([0,14938],inventories): reconstructed.extend([[offset+i for i in ids] for ids in inv['sharedEdgeConnectedComponents']]); zero.extend(offset+i for i in inv['exactNonrenderingOriginalFaces'])
   assert reconstructed==[c['globalOriginalFaces'] for c in components] and zero==graph['exactNonrenderingGlobalFacesRetained']; wsha=digest(world.tobytes()); rational={}; trees={}; records=[]
   def exact(i):
    if i not in rational:rational[i]=rational_face(world[i])
    return rational[i]
   def contact(a,b):
    pts=intersection_points(exact(a),exact(b)); measure=contact_measure(pts) if pts else None; return measure if measure and measure['dimension']>0 else None
   prior=next((r for r in rows if r['complete15579WorldSHA256']==wsha),None)
   if prior is not None: records=prior['completeRestrictedOriginalInterfaceReplays']
   else:
    for r in selected:
     a,b=r['globalOriginalFaces']; c,d=r['components']; assert a in components[c]['globalOriginalFaces'] and b in components[d]['globalOriginalFaces']; measure=contact(a,b); originalnegative=measure is None; witness=[a,b]; tested=0
     if measure is None:
      af=components[c]['globalOriginalFaces']; bf=components[d]['globalOriginalFaces']; small,large=(af,bf) if len(af)<=len(bf) else (bf,af); key=tuple(large)
      if key not in trees:
       ids=np.asarray(large,int); t=world[ids]; trees[key]=(ids,shapely.STRtree(shapely.box(t[:,:,0].min(1),t[:,:,2].min(1),t[:,:,0].max(1),t[:,:,2].max(1))))
      ids,tree=trees[key]; found=False
      for i in small:
       t=world[i]
       for k in tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())):
        j=int(ids[k]); u=world[j]
        if np.any(t.min(0)>u.max(0)) or np.any(u.min(0)>t.max(0)):continue
        tested+=1; m=contact(i,j); pulse()
        if m is not None:measure=m; witness=[i,j] if i in af else [j,i]; found=True; break
       if found:break
     records.append(dict(components=[c,d],originalWitnessGlobalFaces=[a,b],originalWitnessExactNegativePreserved=originalnegative,selectedCurrentRepresentationWitnessGlobalFaces=witness if measure is not None else None,selectedCurrentRepresentationExactContact=measure,alternateExactFacePairsTested=tested,positiveDimensionalInterface=measure is not None)); pulse()
   adjacency={k:set() for k in allowed}
   for r in records:
    if r['positiveDimensionalInterface']:
     c,d=r['components']; assert c in allowedset and d in allowedset; adjacency[c].add(d); adjacency[d].add(c)
   reached={966}; parents={966:None}; todo=[966]
   while todo:
    a=todo.pop()
    for b in sorted(adjacency[a]):
     if b not in reached:reached.add(b);parents[b]=a;todo.append(b)
   rows.append(dict(mode=mode,complete15579WorldSHA256=wsha,completeActorNonzeroEdgeCensuses=inventories,completeRestrictedOriginalInterfaceReplays=records,conditionalSeedOnlyGenuineMainPodium966=True,nonvisualAllowedComponents=allowed,forbiddenVisualAndPendingFootingBridges=excluded,conditionalReachedComponents=sorted(reached),conditionalParents=parents,unresolvedNonvisualComponents=sorted(allowedset-reached),rawFailedOriginalWitnesses=[r for r in records if r['originalWitnessExactNegativePreserved']],completeOriginalSourceZerosUncredited=zero,sourceOnly=True,structuralRootCredit=False,wholeSourceAcceptance=False)); pulse(True); print(json.dumps(dict(mode=mode,reached=len(reached),unresolved=rows[-1]['unresolvedNonvisualComponents'],failedOriginalWitnesses=len(rows[-1]['rawFailedOriginalWitnesses']))),flush=True)
  assert all(ref(ROOT/r['path'])==r for r in refs); out=dict(uids=uids,completeOriginalFaces=15579,completeOriginalNonzeroBodies=973,completeAllBodies=components,rows=rows,allOriginalExcludedBodyAndSampleFailuresPreserved=True,frozenCapturedManifest=source['currentManifest'],sourceOnly=True,conditionalMainPodiumGroundAndCapMustBeComposedIndependently=True,visualOnlyRootOrBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs); save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); m.freeze(BATCH,'mount-complete-four-stream-restricted-nonvisual-original-positive-contact-diagnostic-v1',[ROOT/r['path'] for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=uids,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

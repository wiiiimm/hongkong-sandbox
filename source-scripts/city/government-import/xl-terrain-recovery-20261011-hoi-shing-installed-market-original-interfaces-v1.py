"""Complete original Hoi Shing to two installed Market actors, source-only.

Every authored face is retained; native catalogue availability is not new
support/native approval. Exact original contacts are geometric leads only.
"""
from pathlib import Path
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering,census
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-installed-market-original-interfaces-v1';DOC=BASE/BATCH;SHORT=BASE/'xl-terrain-recovery-20261011-held-terrain-native-carrier-shortlist-v1';INV=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5';UIDS=['landsd/318801:0','landsd/313033:0','landsd/313116:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [SHORT,INV]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 own=next(r for r in read(SHORT/'diagnostic.json.gz')['rows']if r['uid']==UIDS[0]);native={r['uid']:r for r in read(INV/'inventory.json.gz')['rows']if r['uid']in UIDS[1:]};assert set(native)==set(UIDS[1:]);rows=[own,*[native[u]for u in UIDS[1:]]];assets=[ROOT/r['source']['path']for r in rows];worlds=[];partitions=[]
 for r,p in zip(rows,assets):
  assert ref(p)==r['source']and ref(p)['sha256']==r['sourceSHA256'];world=decode_original_world_triangles(p.read_bytes());bounds=packed_world_bounds(p.read_bytes());assert bounds==r['completeOriginalPOSITIONProof'];zero=[i for i,f in enumerate(world)if exact_nonrendering(f)];render=sorted(set(range(len(world)))-set(zero));topology=census(world,render);worlds.append(world);partitions.append(dict(uid=r['uid'],source=ref(p),completeSourceSHA256=r['sourceSHA256'],completeOriginalPOSITIONBounds=bounds,completeProviderStreams=source_stream_binding(p.read_bytes()),completeOriginalWorldSHA256=digest(world.tobytes()),exactNonrenderingOriginalFacesRetained=zero,completeRenderableOriginalFaceIds=render,completeNonzeroSharedEdgeCensus=topology,noNativeReacceptance=True))
 claim=reservations.claim('hoi-shing-original-interfaces-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 try:
  pairs=[]
  for i,j in [(0,1),(0,2),(1,2)]:
   assert reservations.heartbeat(lease)['ok'];contact=exact_component_contacts(worlds[i],partitions[i]['completeRenderableOriginalFaceIds'],worlds[j],partitions[j]['completeRenderableOriginalFaceIds']);assert contact['allPairsExamined']is True;assert reservations.heartbeat(lease)['ok'];pairs.append(dict(actorUIDs=[UIDS[i],UIDS[j]],completeExactRenderableSourcePairContacts=contact));print(dict(actorUIDs=[UIDS[i],UIDS[j]],positiveContacts=sum(p['dimension']>0 for p in contact['contacts']),pointOnlyContacts=sum(p['dimension']==0 for p in contact['contacts'])),flush=True)
  refs.extend(ref(p)for p in [*assets,SHORT/'diagnostic.json.gz',INV/'inventory.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']);assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=UIDS,completeOriginalSources=partitions,completeCrossActorPairs=pairs,allOriginalFacesPartitioned=True,allOriginalZeroAreaFacesNoBridge=True,frozenBaselineManifest=read(INV/'inventory.json.gz')['currentManifest'],historicalOwnReasons=own['historicalReasons'],sourceOnly=True,noFreshCurrentCapture=True,currentAcceptance=False,rootOrStructuralCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze_hoi_shing_original',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-three-original-hoi-shing-installed-market-native-original-interfaces-source-only-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,completeOriginalFaces=sum(len(w)for w in worlds),sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

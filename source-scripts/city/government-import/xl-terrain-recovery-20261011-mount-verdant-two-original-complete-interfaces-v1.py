"""Complete untouched Mount Verdant tower/podium source interfaces.

Changed method: full nonzero edge bodies and all exact source triangle contacts,
not the old 66 unresolved rim samples. Old failures stay immutable. This grants
no identity/terrain/support/current approval or installation credit.
"""
from pathlib import Path
import importlib.util, uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-mount-verdant-two-original-complete-interfaces-v1';DOC=BASE/BATCH
OLD=BASE/'government-xl-full-cell-aqua-mount-support-recovered-20261006'
UIDS=['landsd/261717:0','landsd/75782:0']
EXPECTED={UIDS[0]:('c8e54f42cd1f52ce94d1112a5c51bd58674fdbe38d8af6ac0de2b9498fbddec1',14938,'4396418746T20190903','B439641874601063C0'),UIDS[1]:('4d3d6e5e5b08c6f33b1ce710161edc3554998f7afc7ee15ce29577f9e4c2f781',641,'4396818745P20190903','B439681874502063C0')}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 bound={r['path']:r for r in receipt['evidenceRefs']}
 for name in('selection.json.gz','support-checks.json.gz','recovery.json'):
  p=OLD/name;assert bound[str(p.relative_to(ROOT))]==ref(p)
 old=read(OLD/'selection.json.gz');rows=[next(r for r in old['rows']if r['uid']==uid)for uid in UIDS]
 refs=[ref(Path(__file__)),ref(OLD/'result.json')]+[ref(OLD/name)for name in('selection.json.gz','support-checks.json.gz','recovery.json')]
 worlds=[];censuses=[];sources=[]
 for uid,row in zip(UIDS,rows):
  sha,count,csuid,modelid=EXPECTED[uid];asset=ROOT/row['candidate']['path'];native=row['native']
  assert digest(asset.read_bytes())==row['sourceSHA256']==native['model']['asset']['sha256']==sha
  assert row['uid']==row['source']['building']['uid']==uid and row['source']['building']['buildingCSUID']==csuid and row['modelId']==modelid
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');cached=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,native['cacheKey'])).fetchone()
  assert cached and cached[0]==native['resultSha'];matches=[m for m in cached[1]['models']if m['modelId']==modelid];assert len(matches)==1 and matches[0]==native['model']
  world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(count,3,3)and np.isfinite(world).all();inv=census(world,list(range(count)))
  worlds.append(world);censuses.append(inv);sources.append(dict(uid=uid,source=ref(asset),sourceSHA256=sha,sourceCSUID=csuid,modelId=modelid,completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=count,completeOriginalPOSITIONBounds=packed_world_bounds(asset.read_bytes()),completeProviderSourceStreams=source_stream_binding(asset.read_bytes()),completeEdgeCensus=inv,nativeRun=NATIVE_RUN,nativeCacheKey=native['cacheKey'],nativeResultSHA256=native['resultSha'],historicalSourceSelection=ref(OLD/'selection.json.gz')));refs.append(ref(asset))
 helpers=('exact_packed_world_geometry_20261009.py','exact_packed_world_bounds_v3_20261010.py','xl_source_stream_binding_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(ref(HERE/name)for name in helpers)
 claim=reservations.claim('mount-verdant-source-interfaces-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  assert reservations.heartbeat(lease)['ok'];contacts=exact_component_contacts(worlds[0],censuses[0]['completeRenderableFaceIds'],worlds[1],censuses[1]['completeRenderableFaceIds']);assert contacts['allPairsExamined']is True;assert reservations.heartbeat(lease)['ok']
  assert all(ref(ROOT/r['path'])==r for r in refs)
  result=dict(uids=UIDS,completeSources=sources,completeSourceSHA256={r['uid']:r['sourceSHA256']for r in sources},completeOriginalWorldSHA256={r['uid']:r['completeOriginalWorldSHA256']for r in sources},completeSourceFaces={r['uid']:r['completeOriginalFaces']for r in sources},completeEveryRenderableOriginalFacePairContactInventory=contacts,allOriginalFacesPartitioned=True,exactNonrenderingOriginalFacesRetained={u:inv['exactNonrenderingOriginalFaces']for u,inv in zip(UIDS,censuses)},positiveDimensionalOriginalInterfaces=sum(p['dimension']>0 for p in contacts['contacts']),pointOnlyOriginalContactsRetained=sum(p['dimension']==0 for p in contacts['contacts']),rawHistoricalSupportSampleFailuresRemain=ref(OLD/'support-checks.json.gz'),rawHistoricalManifestSHA256=old['manifestSHA256'],sourceOnly=True,noFreshCurrentCapture=True,currentAcceptance=False,rootOrStructuralContactCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'complete-mount-verdant-two-unchanged-original-nonzero-edge-and-exact-pair-interface-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,currentAcceptance=False,completeOriginalFaces=sum(result['completeSourceFaces'].values()),completeOriginalBodyCounts={u:len(inv['sharedEdgeConnectedComponents'])for u,inv in zip(UIDS,censuses)},positiveDimensionalOriginalInterfaces=result['positiveDimensionalOriginalInterfaces'],pointOnlyOriginalContactsRetained=result['pointOnlyOriginalContactsRetained'],newlyInstalled=0));print(dict(completeOriginalBodyCounts={u:len(inv['sharedEdgeConnectedComponents'])for u,inv in zip(UIDS,censuses)},positiveInterfaces=result['positiveDimensionalOriginalInterfaces'],pointOnly=result['pointOnlyOriginalContactsRetained']),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

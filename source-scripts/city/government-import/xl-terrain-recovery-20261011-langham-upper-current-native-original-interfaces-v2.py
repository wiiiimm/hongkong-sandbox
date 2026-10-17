"""Complete original Langham upper79318↔existing mall224399 interfaces.

Pinned saved source inputs only, never current terrain/root/identity approval.
Every original face, including explicit exact nonrendering triangles and point-only contacts,
is retained. Any positive intersection is only a causal lead, not structural
support or ownership; raw failed old samples remain unchanged.
"""
from pathlib import Path
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-upper-current-native-original-interfaces-v2';DOC=BASE/BATCH
SHORT=BASE/'xl-terrain-recovery-20261011-held-terrain-native-carrier-shortlist-v1';INV=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5';OLD=BASE/'government-xl-langham-retained-grid-recovered-20261008';UID='landsd/79318:0';NATIVE='landsd/224399:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [SHORT,INV,OLD]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
 own=next(r for r in read(SHORT/'diagnostic.json.gz')['rows']if r['uid']==UID);native=next(r for r in read(INV/'inventory.json.gz')['rows']if r['uid']==NATIVE);assets=[ROOT/r['source']['path']for r in [own,native]]
 for r,p in zip([own,native],assets):assert ref(p)==r['source']and ref(p)['sha256']==r['sourceSHA256']
 worlds=[decode_original_world_triangles(p.read_bytes())for p in assets];bounds=[packed_world_bounds(p.read_bytes())for p in assets];streams=[source_stream_binding(p.read_bytes())for p in assets];assert native['completeOriginalPOSITIONProof']==bounds[1];assert len(worlds[1])==native['rawCurrentEntry']['triangles']==20260
 claim=reservations.claim('langham-original-interfaces-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  zero=[[i for i,t in enumerate(w)if exact_nonrendering(t)]for w in worlds];render=[sorted(set(range(len(w)))-set(z))for w,z in zip(worlds,zero)]
  assert all(sorted(ids+z)==list(range(len(w)))and not set(ids)&set(z)for w,z,ids in zip(worlds,zero,render))
  contacts=exact_component_contacts(worlds[0],render[0],worlds[1],render[1]);assert contacts['allPairsExamined']is True;assert reservations.heartbeat(lease)['ok']
  DOC.mkdir(exist_ok=True);(DOC/'previous-raw-degenerate-helper-failure.log').write_bytes(Path('/tmp/langham-upper-current-native-original-interfaces-v1-20261011.log').read_bytes())
  refs.extend(ref(p)for p in [*assets,SHORT/'diagnostic.json.gz',INV/'inventory.json.gz',OLD/'metrics.json',OLD/'foundation.json',OLD/'native-neighbour-checks.json',OLD/'neighbour-checks.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'xl-terrain-recovery-20261011-langham-upper-current-native-original-interfaces-v1.py',DOC/'previous-raw-degenerate-helper-failure.log'])
  result=dict(uids=[UID,NATIVE],completeSourceFaces={UID:len(worlds[0]),NATIVE:len(worlds[1])},completeSourceSHA256={UID:own['sourceSHA256'],NATIVE:native['sourceSHA256']},completeOriginalWorldSHA256={u:digest(w.tobytes())for u,w in zip([UID,NATIVE],worlds)},completeOriginalPOSITIONBounds={u:b for u,b in zip([UID,NATIVE],bounds)},completeProviderSourceStreams={u:s for u,s in zip([UID,NATIVE],streams)},completeEveryRenderableOriginalFacePairContactInventory=contacts,exactNonrenderingOriginalFacesRetained={u:[dict(sourceFace=i,completeOriginalVertices=w[i].tolist(),providesNoStructuralContactOrBridge=True)for i in z]for u,w,z in zip([UID,NATIVE],worlds,zero)},allOriginalFacesPartitioned=True,positiveDimensionalOriginalInterfaces=sum(p['dimension']>0 for p in contacts['contacts']),pointOnlyOriginalContactsRetained=sum(p['dimension']==0 for p in contacts['contacts']),rawHistoricalPhysicalReceipt=ref(OLD/'result.json'),rawHistoricalSupportSampleFailuresRemain=True,sourceOnly=True,frozenBaselineManifest=read(INV/'inventory.json.gz')['currentManifest'],noFreshCurrentCapture=True,currentAcceptance=False,rootOrStructuralContactCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
  for r in refs:assert ref(ROOT/r['path'])==r
  s=importlib.util.spec_from_file_location('langham_interfaces_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-unchanged-langham-upper-to-existing-mall-original-positive-dimensional-interface-diagnostic-v2',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,currentAcceptance=False,completeOriginalFaces=sum(result['completeSourceFaces'].values()),positiveDimensionalOriginalInterfaces=result['positiveDimensionalOriginalInterfaces'],pointOnlyContacts=result['pointOnlyOriginalContactsRetained'],newlyInstalled=0));print(dict(completeSourceFaces=result['completeSourceFaces'],positiveContacts=result['positiveDimensionalOriginalInterfaces'],pointContacts=result['pointOnlyOriginalContactsRetained']),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

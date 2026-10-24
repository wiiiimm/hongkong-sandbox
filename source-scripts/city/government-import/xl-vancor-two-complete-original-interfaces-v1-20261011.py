"""Complete byte-authored669/646 original mutual interface diagnostic only.
Names/parent/permit are context, no ownership/grouping/support/collision credit.
All exact0D/1D/2D faces retained; no zero-area structural bridge.
"""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,primitive_census
BASE=ROOT/'docs/astra-city/government-import';OWN=BASE/'government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v2-20261011';OTHER=BASE/'government-xl-vancor-90824-untouched-original-recovery-v1-20261011'
BATCH='government-xl-vancor-two-complete-original-interfaces-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);refs=[Path(__file__),manifest];rows=[read(OWN/'check-selection.json.gz')['rows'][0],read(OTHER/'selection.json.gz')['rows'][0]];assert [r['uid']for r in rows]==['landsd/147956:0','landsd/90824:0'];worlds=[];actors=[]
 for folder in [OWN,OTHER]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(folder/'result.json')
 for row,count in zip(rows,[669,646]):
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];world=decode_original_world_triangles(raw);assert len(world)==row['candidate']['entry']['triangles']==count;worlds.append(world);refs.append(asset);actors.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],source=ref(asset),modelId=row['modelId'],completeWorldSHA256=digest(world.tobytes()),completeFaces=count,completeNonzeroSharedEdgeCensus=census(world,list(range(count))),completeFinitePrimitiveCensus=primitive_census(world),currentFormContextOnly=row['source']['building']))
 contacts=exact_finite_contacts(worlds[0],list(range(669)),worlds[1],list(range(646)));assert contacts['allPairsExamined']and not contacts['sourceFacesOmitted'];positive=[r for r in contacts['contacts']if r['dimension']>0 and r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2]
 save(DOC/'diagnostic.json.gz',dict(currentManifest=start,actors=actors,completeExactAuthoredSourceInterfaces=contacts,positiveAreaFacetInterfaceCount=len(positive),sameNameParentPermitContextNotOwnershipOrCollisionExemption=True,sourceGeometryChanges=0,structuralSupportAccepted=False,currentAcceptance=False,installationApproved=False));assert ref(manifest)==start
 refs += [OWN/'check-selection.json.gz',OTHER/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']
 s=importlib.util.spec_from_file_location('vancor_two_complete_interface_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'two-complete-unchanged-original669-plus646-finite-interface-and-body-census-diagnostic-only',refs,dict(uids=[r['uid']for r in rows],positiveAreaFacetInterfaceCount=len(positive),sourceGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(completeAuthoredContacts=len(contacts['contacts']),positiveAreaFacetInterfaces=len(positive),originalBodyCounts={a['uid']:len(a['completeNonzeroSharedEdgeCensus']['sharedEdgeConnectedComponents'])for a in actors})),flush=True)
if __name__=='__main__':main()

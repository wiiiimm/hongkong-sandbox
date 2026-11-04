"""Complete cached original12164 x764 finite contact inventory; no support/root acceptance."""
import json,importlib.util
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011';DOC=B/BATCH
CENSUS=B/'government-xl-fixed295-simple-source-support-nomination-census-v1-20261011';PODIUM=B/'government-xl-elm-tree-podium-physical-20261007'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();tower=next(r for r in read(CENSUS/'diagnostic.json.gz')['rows']if r['uid']=='landsd/253874:0');podium=next(r for r in read(PODIUM/'selection.json.gz')['rows']if r['uid']=='landsd/258892:0');a=ROOT/tower['sourceAsset']['path'];b=ROOT/podium['candidate']['path'];assert ref(a)==tower['sourceAsset']and digest(b.read_bytes())==podium['sourceSHA256'];ta=decode_original_world_triangles(a.read_bytes());tb=decode_original_world_triangles(b.read_bytes());assert ta.shape==(12164,3,3)and tb.shape==(764,3,3)
 ca=tower['completeExactOriginalBodyCensus'];cb=census(tb,list(range(len(tb))));ma={f:i for i,c in enumerate(ca['sharedEdgeConnectedComponents'])for f in c};mb={f:i for i,c in enumerate(cb['sharedEdgeConnectedComponents'])for f in c}
 contacts=exact_finite_contacts(ta,list(range(len(ta))),tb,list(range(len(tb))));positive=[p for p in contacts['contacts']if p['dimension']>0];pairs=Counter((ma[p['sourceFaceA']],mb[p['sourceFaceB']])for p in positive)
 refs=[ref(p)for p in [Path(__file__),a,b,CENSUS/'diagnostic.json.gz',CENSUS/'result.json',PODIUM/'selection.json.gz',PODIUM/'result.json']]+[ref(HERE/(n+'.py'))for n in ['exact_packed_world_geometry_20261009','exact_original_shared_edge_component_census_v2_20261011','test_exact_original_shared_edge_component_census_v2_20261011','exact_original_finite_triangle_contacts_20261010','exact_original_shell_intersections_20261009','exact_original_component_contacts_20261009']]
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=['landsd/253874:0','landsd/258892:0'],sourceOnly=True,currentAcceptance=False,installationApproved=False,rootCredit=False,structuralRoleCredit=False,nativeReapproval=False,sourceGeometryChanges=0,terrainGeometryChanges=0,noMutableCapture=True,wholeOriginalTowerFaces=len(ta),wholeOriginalPodiumFaces=len(tb),completeTowerWorldSHA256=digest(ta.tobytes()),completePodiumWorldSHA256=digest(tb.tobytes()),completeTowerNonzeroBodyCensus=ca,completePodiumNonzeroBodyCensus=cb,completeFiniteContacts=contacts,positiveDimensionalBodyPairs=[dict(towerBody=k[0],podiumBody=k[1],positiveInterfaces=v)for k,v in sorted(pairs.items())],directlyContactingTowerBodies=sorted({k[0]for k in pairs}),towerBodiesWithoutDirectPodiumContact=sorted(set(ma.values())-{k[0]for k in pairs}),historicalPodiumReasonsPreserved=read(PODIUM/'result.json')['reasons'],qualification='Complete exact original-source positive-dimensional finite contacts only. Shared-edge bodies are not solids. Tower internal support paths, all details, podium grade/root and whole finite/current terrain/identity/foreign/native/runtime gates remain unqualified. Historical podium burial and regressions stay blockers. No fabricated support, source shift, changed terrain or acceptance.',evidenceRefs=refs)
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(towerBodies=len(ca['sharedEdgeConnectedComponents']),podiumBodies=len(cb['sharedEdgeConnectedComponents']),positiveInterfaces=len(positive),directTowerBodies=result['directlyContactingTowerBodies'],pairCounts=result['positiveDimensionalBodyPairs'])),flush=True)
if __name__=='__main__':main()

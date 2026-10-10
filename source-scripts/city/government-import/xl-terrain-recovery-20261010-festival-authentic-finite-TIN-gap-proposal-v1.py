"""New bounded authentic finite TIN terrain proposal; no source building edits."""
import importlib.util,json,copy
from fractions import Fraction as F
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_original_facet_outward_float32_gap_hull_20261010 import propose
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-authentic-finite-TIN-gap-proposal-v1';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
GAPS=BASE/'xl-terrain-recovery-20261010-festival-exact-gap-regions-v1';PHYS=BASE/'government-xl-terrain-recovery-festival-pair-original-terrain-current-v1-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 assert not DOC.exists();gaps=read(GAPS/'diagnostic.json.gz');receipt=read(GAPS/'result.json')
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 old=read(PHYS/'terrain-candidates.json')[0];old_path=ROOT/old['path'];assert digest(old_path.read_bytes())==old['sha256'];patch=read(old_path);terrain=read(PHYS/'terrain.json');second=module('festival_authentic_terrain_decode','xl-second-pass.py');pieces=[];bindings=[];refs=[]
 paths={f['path']:f['sha256'] for source in patch['meta']['source']['nativeSources'] for f in source['sourceFiles'] if f['path'].endswith(('.bin','.gltf'))}
 for path,sha in paths.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ref(ROOT/path))
 for path in paths:
  if not path.endswith('.gltf'):continue
  tri=second.terrain_triangles(ROOT/path);start=len(pieces);pieces.extend(tri);bindings.extend(dict(sourceGltf=ref(ROOT/path),completeDecodedSourceTrianglesSHA256=digest(tri.tobytes()),originalSourceTerrainFace=i) for i in range(len(tri)))
 native=np.asarray(pieces);polygons=shapely.polygons(native[:,:,[0,2]]);tree=shapely.STRtree(polygons);proposals=[];fail=[];unique={};region_inventory=[]
 for r in gaps['rows']:
  for j,region in enumerate(r['gap']['allExactUncoveredRegions']):
   key=digest(json.dumps(sorted(region),separators=(',',':')).encode());region_inventory.append(dict(uid=r['uid'],kind=r['kind'],sourceFace=r['sourceFace'],region=j,canonicalUnorderedRegionKey=key))
   if key in unique:continue
   xy=np.array([[float(F(v)) for v in p] for p in region]);bounds=[*xy.min(0),*xy.max(0)];choices=[]
   for k in tree.query(shapely.box(*bounds)):
    try:p=propose(region,native[k])
    except AssertionError:continue
    choices.append((sum(v[1] for v in p['proposedVertices'])/len(p['proposedVertices']),int(k),p))
   if not choices:fail.append(dict(canonicalUnorderedRegionKey=key,completeExactGapRegion=region,reason='no-complete-outward-hull-contained-in-one-authentic-finite-TIN-facet'));unique[key]=None;continue
   _,k,p=max(choices,key=lambda q:q[0]);entry=dict(canonicalUnorderedRegionKey=key,sourceFacetBinding=bindings[k],proof=p);proposals.append(entry);unique[key]=entry
  print(json.dumps(dict(uid=r['uid'],kind=r['kind'],face=r['sourceFace'],uniqueRegions=len(unique),proposed=len(proposals),unresolved=len(fail))),flush=True)
 additions=np.asarray([f for r in proposals for f in r['proof']['proposedFaces']],float);original_position=copy.deepcopy(patch['nativeMesh']['position']);original_index=copy.deepcopy(patch['nativeMesh']['index']);offset=len(original_position)//3;patch['nativeMesh']['position'].extend(additions.reshape(-1).tolist());patch['nativeMesh']['index'].extend(range(offset,offset+len(additions)*3));assert patch['nativeMesh']['position'][:len(original_position)]==original_position and patch['nativeMesh']['index'][:len(original_index)]==original_index
 patch['nativeMesh']['source']['authenticFiniteTINOutwardGapRestoration']=dict(policy='New minimal outward Float32-cell hulls inside complete authentic finite original TIN facets, source-plane interpolated Y explicitly quantized. Existing complete patch vertices/indices unchanged; building original bytes/root pose unchanged. Full new proposal checks mandatory.',diagnosticPath=str((DOC/'diagnostic.json.gz').relative_to(ROOT)),completeGapRegionInventory=len(region_inventory),uniqueExactRegions=len(unique),proposedHulls=len(proposals),unresolvedRegions=len(fail),addedTriangles=len(additions),sumProposedProjectedAreaM2=sum(float(F(r['proof']['fullProposedProjectedAreaM2'])) for r in proposals),terrainProposalGeometryChanged=True,buildingGeometryChanges=0)
 LOCAL.mkdir(parents=True);proposal_path=LOCAL/'government-native-91827-and-104302-authentic-gap-proposal.json';save(proposal_path,patch);proposal={**old,'path':str(proposal_path.relative_to(ROOT)),'sha256':digest(proposal_path.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[proposal]);save(DOC/'terrain.json',{**terrain,'patch':proposal,'terrainGeometryChanged':True,'previousProposal':old,'exactSourceBuildingGeometryChanged':False})
 refs.extend(ref(p) for p in [Path(__file__),GAPS/'diagnostic.json.gz',GAPS/'result.json',PHYS/'terrain-candidates.json',PHYS/'terrain.json',old_path,HERE/'exact_original_projected_uncovered_regions_20261010.py',HERE/'exact_original_facet_outward_float32_gap_hull_20261010.py',HERE/'test_exact_original_facet_outward_float32_gap_hull_20261010.py',proposal_path]);save(DOC/'diagnostic.json.gz',dict(uids=gaps['uids'],completeGapRegionInventory=region_inventory,uniqueExactRegions=len(unique),authenticFiniteTINProposals=proposals,unresolvedRegions=fail,priorCompleteNativePositionSHA256=digest(np.asarray(original_position,float).tobytes()),priorCompleteNativeIndexSHA256=digest(np.asarray(original_index,np.uint32).tobytes()),priorVerticesAndIndicesExactlyPreserved=True,terrainProposalGeometryChanged=True,addedTerrainTriangles=len(additions),buildingGeometryChanges=0,sourcePlaneExtrapolation=False,fullAcceptance=False,installationApproved=False,evidenceRefs=refs));freeze=module('festivalauthenticfreeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'bounded-authentic-finite-TIN-gap-terrain-proposal-v1',[ROOT/r['path'] for r in refs],dict(uids=gaps['uids'],uniqueExactGapRegions=len(unique),proposedHulls=len(proposals),unresolvedRegions=len(fail),addedTerrainTriangles=len(additions),terrainProposalGeometryChanged=True,buildingGeometryChanges=0,fullAcceptance=False));print(dict(proposed=len(proposals),unresolved=len(fail),triangles=len(additions)),flush=True)
if __name__=='__main__':main()

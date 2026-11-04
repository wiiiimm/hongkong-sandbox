"""Explicit bounded original-native/current-parent terrain additions; no acceptance."""
import importlib.util,copy,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_original_facet_outward_float32_gap_hull_20261010 import propose
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-mixed-authentic-parent-gap-proposal-v3';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261010-festival-authentic-finite-TIN-gap-proposal-v2';PARENT=HERE/'local/xl-terrain-recovery-20261010-festival-current-parent-facets-v1/drawn-current-terrain.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();old=read(PRIOR/'diagnostic.json.gz');receipt=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 parent=read(PARENT)
 for p,h in parent['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 assert parent['actualCurrentRenderer'] and not parent['terrainProposalChanged'];tri=np.asarray(parent['faces'],float);tree=shapely.STRtree(shapely.polygons(tri[:,:,[0,2]]));rows=[];failed=[]
 for r in old['unresolvedRegions']:
  region=r['completeExactGapRegion'];xy=np.asarray([[float(F(v)) for v in p] for p in region]);choices=[]
  for k in tree.query(shapely.box(*xy.min(0),*xy.max(0))):
   try:proof=propose(region,tri[k])
   except AssertionError:continue
   choices.append((sum(p[1] for p in proof['proposedVertices'])/len(proof['proposedVertices']),int(k),proof))
  if not choices:failed.append(r);continue
  _,k,proof=max(choices,key=lambda v:v[0]);assert parent['meshes'][0]['meshName']=='Lands Department · 70 m terrain' and len(parent['meshes'])==1
  rows.append(dict(canonicalUnorderedRegionKey=r['canonicalUnorderedRegionKey'],currentDrawnParentFacet=k,originalDrawnMeshFace=parent['meshes'][0]['selectedFaces'][k]['originalDrawnMeshFace'],completeCurrentParentExport=ref(PARENT),proof=proof,proposalRole='Explicit new minimal outward hull on the literal current rendered parent plane, not the historical native floor and not an identical-surface claim.'))
 assert len(rows)==26 and not failed;old_candidate=read(PRIOR/'terrain-candidates.json')[0];assert ref(ROOT/old_candidate['path'])['sha256']==old_candidate['sha256'];patch=read(ROOT/old_candidate['path']);old_position=copy.deepcopy(patch['nativeMesh']['position']);old_index=copy.deepcopy(patch['nativeMesh']['index']);add=np.asarray([face for r in rows for face in r['proof']['proposedFaces']]);offset=len(old_position)//3;patch['nativeMesh']['position'].extend(add.reshape(-1).tolist());patch['nativeMesh']['index'].extend(range(offset,offset+len(add)*3));assert patch['nativeMesh']['position'][:len(old_position)]==old_position and patch['nativeMesh']['index'][:len(old_index)]==old_index
 patch['nativeMesh']['source']['currentRenderedParentFiniteGapRestoration']=dict(policy='Explicit new Float32 hulls, wholly inside actual current renderer parent finite triangles; full source building geometry unchanged. Fresh whole-facet/current/foreign/foundation/sampler/browser gates mandatory.',diagnosticPath=str((DOC/'diagnostic.json.gz').relative_to(ROOT)),completeCurrentParentExport=ref(PARENT),currentManifestSHA256=parent['inputHashes']['3d-viewer/city/data/manifest.json'],proposedHulls=len(rows),addedTriangles=len(add),terrainProposalGeometryChanged=True,exactSameSurfaceClaim=False,buildingGeometryChanges=0)
 # The historical overlap receipt does not bind new geometry. Generate a new full proposal audit.
 patch['nativeMesh'].pop('sourceOverlap',None);LOCAL.mkdir(parents=True);asset=LOCAL/'government-native-91827-and-104302-mixed-authentic-parent-gap-proposal.json';save(asset,patch);resolution=module('festival_mixed_gap_overlap','native_patch_resolution.py');evidence=DOC/'new-proposal-highest-surface-overlap.json';source_files=[ref(PARENT),ref(PRIOR/'diagnostic.json.gz'),ref(ROOT/old_candidate['path'])];resolution.approve_original_overlap(patch,asset,evidence,source_files);audit=read(evidence);audit['policy']='Explicit bounded original-native/current-rendered-parent additions; highest proposed drawn surface. Audit is numerical diagnostic, not source-original-only or full acceptance.';save(evidence,audit);resolution.finalize_overlap_evidence(patch,evidence);save(asset,patch)
 candidate={**old_candidate,'path':str(asset.relative_to(ROOT)),'sha256':digest(asset.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[candidate]);terrain=read(PRIOR/'terrain.json');save(DOC/'terrain.json',{**terrain,'patch':candidate,'previousProposal':old_candidate,'terrainProposalGeometryChanged':True,'terrainGeometryChanged':True,'buildingGeometryChanges':0})
 refs=[ref(p) for p in [Path(__file__),PRIOR/'diagnostic.json.gz',PRIOR/'result.json',PRIOR/'terrain-candidates.json',PRIOR/'terrain.json',ROOT/old_candidate['path'],PARENT,HERE/'xl-terrain-recovery-20261010-festival-current-parent-facets-v1.mjs',HERE/'exact_original_facet_outward_float32_gap_hull_20261010.py',HERE/'test_exact_original_facet_outward_float32_gap_hull_20261010.py',HERE/'xl-second-pass.py',HERE/'native_patch_resolution.py',asset,evidence]]
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/91827:0','landsd/104302:0'],parentProposals=rows,priorAuthenticNativeProposals=25,completeUniqueRegions=51,unresolvedRegions=failed,allPriorNativeVerticesAndIndicesExactlyPreserved=True,addedParentTriangles=len(add),terrainProposalGeometryChanged=True,buildingGeometryChanges=0,sourcePlaneExtrapolation=False,exactSameSurfaceClaim=False,fullAcceptance=False,installationApproved=False,currentRendererInputHashes=parent['inputHashes'],evidenceRefs=refs));freeze=module('festival_mixed_gap_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'explicit-current-parent-and-authentic-native-finite-gap-proposal-v3',[ROOT/r['path'] for r in refs],dict(uids=['landsd/91827:0','landsd/104302:0'],proposedHulls=51,remainingGapRegions=0,addedParentTriangles=len(add),terrainProposalGeometryChanged=True,buildingGeometryChanges=0,fullAcceptance=False));print(dict(parentHulls=len(rows),parentTriangles=len(add),completeProposalTriangles=candidate['triangles']),flush=True)
if __name__=='__main__':main()

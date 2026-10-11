"""Restore complete authenticated finite native facets across real clipped seams.

No extrapolated native heights: every added triangle is an unchanged literal
Float32 renderer version of a complete original native TIN facet. Full extent
is real proposal geometry, measured and fresh-gated separately.
"""
import importlib.util,copy
from pathlib import Path
from fractions import Fraction as F
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_original_projection_coverage_v2_20261010 import exact_coverage,clip,signed_area,point
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-festival-authentic-multi-facet-gap-proposal-v4';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261010-festival-authentic-finite-TIN-gap-proposal-v2';PARENT=BASE/'xl-terrain-recovery-20261010-festival-mixed-authentic-parent-gap-proposal-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists()
 for folder in [PRIOR,PARENT]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 prior=read(PRIOR/'terrain-candidates.json')[0];patch=read(ROOT/prior['path']);assert ref(ROOT/prior['path'])['sha256']==prior['sha256'];paths={f['path']:f['sha256'] for source in patch['meta']['source']['nativeSources'] for f in source['sourceFiles'] if f['path'].endswith(('.gltf','.bin'))};rawrefs=[];tri=[];bindings=[];decode=module('festival_complete_facet_decode','xl-second-pass.py')
 for p,h in paths.items():assert ref(ROOT/p)['sha256']==h;rawrefs.append(ref(ROOT/p))
 for p in paths:
  if not p.endswith('.gltf'):continue
  raw=decode.terrain_triangles(ROOT/p);rendered=raw.astype(np.float32).astype(float);worldhash=digest(raw.tobytes());renderhash=digest(rendered.tobytes());tri.extend(rendered);bindings.extend(dict(sourceGltf=ref(ROOT/p),completeDecodedOriginalNativeTrianglesSHA256=worldhash,completeRenderedFloat32NativeTrianglesSHA256=renderhash,originalSourceFace=i,rawOriginalFace=raw[i].tolist()) for i in range(len(raw)))
 tri=np.asarray(tri);polygons=shapely.polygons(tri[:,:,[0,2]]);tree=shapely.STRtree(polygons);parent=read(PARENT/'diagnostic.json.gz');rows=[];selected=set()
 for r in parent['parentProposals']:
  hull=[tuple(F(v) for v in p) for p in r['proof']['exactConvexOutwardHullXZ']];xz=np.asarray([[float(v) for v in p] for p in hull]);ids=[]
  for k in tree.query(shapely.box(*xz.min(0),*xz.max(0))):
   original=[point(p) for p in tri[k][:,[0,2]]];area=signed_area(original)
   if not area:continue
   if area<0:original.reverse()
   intersection=hull
   for a,b in zip(original,original[1:]+original[:1]):intersection=clip(intersection,a,b,True)
   if intersection:ids.append(int(k))
  ids=sorted(ids);assert ids;proofs=[exact_coverage(np.asarray(face),tri[ids]) for face in r['proof']['proposedFaces']];assert all(p['exactProjectionCovered'] for p in proofs),'No tiny uncovered hull tolerated';selected.update(ids);rows.append(dict(canonicalUnorderedRegionKey=r['canonicalUnorderedRegionKey'],completeExactGapRegion=r['proof']['completeExactGapRegion'],completeBoundedOutwardHullXZ=r['proof']['exactConvexOutwardHullXZ'],selectedCompleteNativeFacetIndices=ids,completeExactFiniteUnionCoverage=proofs,actualParentPlaneNotAdded=True))
 selected=sorted(selected);addition=tri[selected];bounds=prior['bounds'];assert np.all(addition[:,:,0]>=bounds[0]) and np.all(addition[:,:,0]<=bounds[2]) and np.all(addition[:,:,2]>=bounds[1]) and np.all(addition[:,:,2]<=bounds[3]);oldposition=copy.deepcopy(patch['nativeMesh']['position']);oldindex=copy.deepcopy(patch['nativeMesh']['index']);offset=len(oldposition)//3;patch['nativeMesh']['position'].extend(addition.reshape(-1).tolist());patch['nativeMesh']['index'].extend(range(offset,offset+len(addition)*3));assert patch['nativeMesh']['position'][:len(oldposition)]==oldposition and patch['nativeMesh']['index'][:len(oldindex)]==oldindex
 actual_bounds=[float(addition[:,:,0].min()),float(addition[:,:,2].min()),float(addition[:,:,0].max()),float(addition[:,:,2].max())];projected_area=sum(abs(float(signed_area([point(p) for p in face[:,[0,2]]]))) for face in addition)
 patch['nativeMesh']['source']['completeAuthenticFiniteNativeFacetRestoration']=dict(policy='Every added face is a complete literal Float32-rendered authenticated original TIN triangle. Exact complete finite union covers all26 remaining outward hulls. Added full projected extent is real new proposal geometry; no extrapolated height, parent-plane addition, tiny-hole waiver or source building edit.',diagnosticPath=str((DOC/'diagnostic.json.gz').relative_to(ROOT)),restoredOriginalFacets=len(selected),fullRestoredFacetBoundsXZ=actual_bounds,sumRestoredProjectedFacetAreaM2=projected_area,terrainProposalGeometryChanged=True,buildingGeometryChanges=0)
 patch['nativeMesh'].pop('sourceOverlap',None);LOCAL.mkdir(parents=True);asset=LOCAL/'government-native-91827-and-104302-complete-authentic-finite-gap-proposal.json';save(asset,patch);resolution=module('festival_complete_facet_overlap','native_patch_resolution.py');evidence=DOC/'new-proposal-highest-surface-overlap.json';resolution.approve_original_overlap(patch,asset,evidence,rawrefs);audit=read(evidence);audit['policy']='Complete unchanged authentic native TIN facets explicitly restored as new terrain proposal geometry; highest proposed drawn surface. Numerical audit only, all independent gates mandatory.';save(evidence,audit);resolution.finalize_overlap_evidence(patch,evidence);save(asset,patch);candidate={**prior,'path':str(asset.relative_to(ROOT)),'sha256':digest(asset.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3};save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'terrain.json',{**read(PRIOR/'terrain.json'),'patch':candidate,'previousProposal':prior,'terrainProposalGeometryChanged':True,'terrainGeometryChanged':True,'buildingGeometryChanges':0})
 refs=rawrefs+[ref(p) for p in [Path(__file__),PRIOR/'result.json',PRIOR/'diagnostic.json.gz',PRIOR/'terrain-candidates.json',PRIOR/'terrain.json',ROOT/prior['path'],PARENT/'result.json',PARENT/'diagnostic.json.gz',HERE/'xl-second-pass.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'native_patch_resolution.py',asset,evidence]];save(DOC/'diagnostic.json.gz',dict(uids=['landsd/91827:0','landsd/104302:0'],rows=rows,selectedCompleteOriginalFacets=[dict(completeNativeIndex=i,sourceBinding=bindings[i],completeAddedActualFloat32Face=tri[i].tolist()) for i in selected],restoredOriginalFacets=len(selected),fullRestoredFacetBoundsXZ=actual_bounds,sumRestoredProjectedFacetAreaM2=projected_area,priorNativeVerticesAndIndicesExactlyPreserved=True,terrainProposalGeometryChanged=True,buildingGeometryChanges=0,sourcePlaneExtrapolation=False,actualParentPlaneNotAdded=True,fullAcceptance=False,installationApproved=False,evidenceRefs=refs));freeze=module('festival_complete_facet_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'complete-authentic-native-finite-union-gap-restoration-proposal-v4',[ROOT/r['path'] for r in refs],dict(uids=['landsd/91827:0','landsd/104302:0'],completeUniqueGapRegions=51,restoredOriginalFacets=len(selected),fullRestoredFacetBoundsXZ=actual_bounds,sumRestoredProjectedFacetAreaM2=projected_area,terrainProposalGeometryChanged=True,buildingGeometryChanges=0,fullAcceptance=False));print(dict(facets=len(selected),area=projected_area,triangles=candidate['triangles']),flush=True)
if __name__=='__main__':main()

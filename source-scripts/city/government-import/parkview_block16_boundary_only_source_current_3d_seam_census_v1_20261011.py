"""DRAFT existing bounded zero-area pairs: exact3D boundary seams plus locus network."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_shared_3d_segment_intervals_v1_20261011 import overlap,point
from exact_finite_3d_segment_network_v1_20261011 import network
from exact_source_planar_domain_recovery_seams_v1_20261011 import projected
from exact_original_projection_coverage_v2_20261010 import signed_area
B=ROOT/'docs/astra-city/government-import';AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';OLD=B/'government-xl-parkview-block16-two-parent-facet-source-planar-proposal-v1-20261011';LOCUS=B/'government-xl-parkview-block16-finite-source-current-height-locus-census-v1-20261011';DOC=B/'government-xl-parkview-block16-boundary-only-source-current-3D-seam-census-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [strings(v)for v in x]
 return x

def main():
 assert not DOC.exists();oldproof=read(OLD/'diagnostic.json.gz');locus=read(LOCUS/'diagnostic.json.gz');assert read(LOCUS/'result.json')['currentAcceptance']is False
 refs=[ref(p)for p in [Path(__file__),INSTALLED,OLD/'diagnostic.json.gz',OLD/'result.json',LOCUS/'diagnostic.json.gz',LOCUS/'result.json',AUTH/'diagnostic.json.gz',AUTH/'result.json',HERE/'pending-context.py',HERE/'native_patch_resolution.py',HERE/'exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'test_exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'exact_finite_3d_segment_network_v1_20261011.py',HERE/'test_exact_finite_3d_segment_network_v1_20261011.py',HERE/'exact_source_planar_domain_recovery_seams_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];current=_faces(read(INSTALLED));assert len(current)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];assert digest(terrain.tobytes())=='740580e8f1bd38cddc48b956f5ca161de7fcebac2852d887d02ad60c1178cff5'
 sid=oldproof['completeSourceCandidateOriginalTINIds'];rid=oldproof['completeRetainedCandidateInstalledFacetIds'];assert len(sid)==150 and len(rid)==191 and len(set(sid))==150 and len(set(rid))==191
 domains=current[[94641,94645]];lo,hi=domains[:,:,[0,2]].min((0,1)),domains[:,:,[0,2]].max((0,1))
 def candidates(faces):
  xz=faces[:,:,[0,2]];return np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)).tolist()
 assert candidates(terrain)==sid
 assert [i for i in candidates(current)if i not in [94641,94645]]==rid
 assert locus['completeSourceCandidateOriginalTINIds']==sid and locus['completeRetainedCandidateInstalledFacetIds']==rid
 rows=[];boundary=[];segments=[];attribution=[];completeEdgePairs=0
 for li,r in enumerate(locus['rows']):
  fid,nid=r['originalTINFacet'],r['currentNativeFacet'];assert digest(terrain[fid].tobytes())==r['originalFacetSHA256']and digest(current[nid].tobytes())==r['currentFacetSHA256']
  classification=r['proof']['classification']
  if classification=='finite-positive-3D-equal-height-segment':segments.append(r['proof']['exactSegment']);attribution.append(dict(locusRow=li,role='positive-area-overlay-equality-context'))
  if classification!='no-positive-area-overlay':continue
  assert signed_area(projected(terrain[fid]))!=0 and signed_area(projected(current[nid]))!=0,'Vertical/degenerate host cannot get boundary seam credit'
  hits=[]
  for si in range(3):
   a,b=map(point,[terrain[fid,si],terrain[fid,(si+1)%3]])
   for ni in range(3):
    completeEdgePairs+=1;iv=overlap(a,b,current[nid,ni],current[nid,(ni+1)%3])
    if iv is None:continue
    pts=[tuple(a[k]+t*(b[k]-a[k])for k in range(3))for t in iv];hits.append(dict(sourceLocalEdge=si,currentLocalEdge=ni,exactSourceInterval=iv,exactSegment=pts));segments.append(pts);attribution.append(dict(locusRow=li,sourceLocalEdge=si,currentLocalEdge=ni,role='boundary-only-positive-3D-equality-context'))
  rows.append(dict(locusRow=li,originalTINFacet=fid,currentNativeFacet=nid,allPositive3DBoundaryEdgeOverlaps=hits))
  boundary.extend(hits)
 assert len(rows)==2504 and completeEdgePairs==22536
 proof=network(segments)if len(segments)<=256 else None
 # Necessary condition only: a closed equality cycle enclosing any positive-area
 # seed interior needs its X extent beyond seed minimum. No cycle=domain credit.
 cyclebounds=[];seedMinX=F(float(domains[:,:,0].min()))
 if proof is not None:
  for ci,c in enumerate(proof['components']):
   if c['cycleRank']==0:continue
   vertices=c['vertices'];bounds=dict(minX=min(p[0]for p in vertices),maxX=max(p[0]for p in vertices),minZ=min(p[2]for p in vertices),maxZ=max(p[2]for p in vertices))
   cyclebounds.append(dict(component=ci,cycleRank=c['cycleRank'],bounds=bounds,canIntersectPositiveAreaSeedInteriorX=bounds['maxX']>seedMinX))
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,terrainProposalWritten=False,sourceGeometryChanges=0,terrainChanges=0,completeExistingBoundaryOnlyFacetPairs=2504,completeOriginalCurrentEdgePairs=22536,rows=strings(rows),combinedEqualitySegmentAttributions=attribution,combinedEqualitySegmentCount=len(segments),boundaryOnlySegmentCount=len(boundary),exactCombinedNetwork=strings(proof),fixed256SegmentArrangementBudgetExceeded=proof is None,cycleComponentBounds=strings(cyclebounds),seedOriginalInstalledFacets=[94641,94645],exactSeedMinimumX=str(seedMinX),evidenceRefs=refs,qualification='Completes boundary-only segment context on existing2504 zero-area projected pairs; no source/current domain inventory expansion. Combines all174 prior equality segments with genuine exact3D positive boundary overlaps; no point or nearplane equality earns a segment. All original pair incidences preserved. Cycle bounds give a necessary condition only, never sourcepiece/domain/frontier approval. No actualF32/internalmesh/provenance/outside-side/root/support/affected17/native/foreign discharge or terrain candidate. If fixed arrangement budget exceeded raw segment inventory remains complete and topology remains unresolved, never truncated.'))
 print(json.dumps(dict(boundaryFacetPairs=2504,completeEdgePairs=22536,boundaryOnlySegments=len(boundary),combinedSegments=len(segments),arrangementBudgetExceeded=proof is None,cycleRank=proof['cycleRank']if proof else None,cycleComponentsAbleToIntersectSeedInteriorX=sum(c['canIntersectPositiveAreaSeedInteriorX']for c in cyclebounds),terrainProposalWritten=False,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()

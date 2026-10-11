"""DRAFT exact original TIN comparison for four current-implicated source facets.
No proposed terrain, retention discharge, full-source guarantee or approval.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage
B=ROOT/'docs/astra-city/government-import';AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';PHYSICAL=B/'government-xl-parkview-block16-fresh-current-physical-capture-v1-20261011';PRIOR=B/'government-xl-parkview-block16-sampled-foundation-faces-exact-attribution-v1-20261011';CAP=B/'government-xl-parkview-block16-original-cap-primary-tin-comparison-v1-20261011';DOC=B/'government-xl-parkview-block16-four-implicated-original-facets-primary-TIN-comparison-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(p)for p in [Path(__file__),AUTH/'diagnostic.json.gz',AUTH/'result.json',PRIOR/'diagnostic.json.gz',PRIOR/'result.json',CAP/'diagnostic.json.gz',CAP/'result.json',PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',HERE/'pending-context.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];old=read(PRIOR/'diagnostic.json.gz');ids=old['sampledFoundationFailureSourceFaceIDs'];assert ids==[3798,11277,11281,11282];row=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];source=decode_original_world_triangles(asset.read_bytes());refs.append(ref(asset))
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];assert digest(terrain.tobytes())==read(CAP/'diagnostic.json.gz')['completeOriginalTINWorldSHA256'];rows=[];total=0
 for fid in ids:
  face=source[fid];previous=next(r for r in old['rows']if r['originalSourceFace']==fid);assert digest(face.tobytes())==previous['originalSourceFacetSHA256'];xz=terrain[:,:,[0,2]];fxz=face[:,[0,2]];candidates=np.flatnonzero(np.all(xz.max(1)>=fxz.min(0),axis=1)&np.all(xz.min(1)<=fxz.max(0),axis=1)).tolist();total+=len(candidates);assert total<=512,'Bounded complete pair census; no truncation';proofs=[dict(originalTINFacet=j,proof=verify(face,terrain[j]))for j in candidates];gaps=[F(p['proof']['exactMinimumFiniteColumnGapM'])for p in proofs if p['proof']['exactClosedHorizontalProjectionsMeet']];coverage=exact_coverage(face,terrain[candidates]);low=min(gaps)if gaps else None
  rows.append(dict(originalSourceFace=fid,originalSourceFacetSHA256=digest(face.tobytes()),completeClosedAABBCandidateTINIds=candidates,completeExactFinitePairProofs=proofs,completeProjectionCoverage=coverage,exactMinimumOriginalTINClearanceM=str(low)if low is not None else None,originalTINStrictClear=bool(low is not None and low>0 and coverage['exactProjectionCovered']),actualRenderedNegativeVerbatim=previous))
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,nativeReacceptance=False,retentionRemovalApproved=False,originalTINFacets=len(terrain),completeOriginalTINWorldSHA256=digest(terrain.tobytes()),completeSourceFacetIDs=ids,actualCompletePairCount=total,rows=rows,evidenceRefs=refs,comparisonIsOriginalTINNotCurrentRenderedTerrain=True,qualification='Only4 original source facets compared; existing rendered negatives remain. No whole11351-source guarantee, retained/native/foreign obligation discharge, source grade-cap route or terrain proposal.'))
 print(json.dumps(dict(completePairs=total,sourceFacetIds=ids,strictOriginalTINResults=[r['originalTINStrictClear']for r in rows],exactMinimumOriginalTINClearances=[r['exactMinimumOriginalTINClearanceM']for r in rows],currentAcceptance=False)),flush=True)
if __name__=='__main__':main()

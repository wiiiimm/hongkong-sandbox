"""DRAFT: compare unchanged cap45867 to exact original two-sheet TIN.

No terrain proposal, retention removal, modelling, current acceptance or install.
Even a positive original-TIN result leaves retained foreign/basic/native gates,
complete source roles and fresh literal/F32 actual terrain/runtime checks open.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify
from exact_original_projection_coverage_v2_20261010 import exact_coverage,point,clip,signed_area
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-parkview-block16-original-cap-primary-tin-comparison-v1-20261011'
CAP=B/'government-xl-parkview-next-three-exact-cap-refinement-v1-20261011';AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';GRAPH=B/'government-xl-parkview-block16-complete-original-support-graph-v1-20261011';V4=B/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4'
PROBE=B/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def rectangle_area(face,bounds):
 x0,z0,x1,z1=map(F,bounds);rect=[(x0,z0),(x1,z0),(x1,z1),(x0,z1)];poly=[point(p)for p in face[:,[0,2]]]
 for a,b in zip(rect,rect[1:]+rect[:1]):poly=clip(poly,a,b,True)
 return abs(signed_area(poly))
def main():
 assert not DOC.exists();refs=[ref(p)for p in [Path(__file__),CAP/'diagnostic.json.gz',CAP/'result.json',AUTH/'diagnostic.json.gz',AUTH/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',V4/'terrain.json',V4/'result.json',PROBE/'selection.json.gz',HERE/'pending-context.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]
 for d in [CAP,AUTH,GRAPH,V4]:
  receipt=read(d/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 neg=next(r for r in read(CAP/'diagnostic.json.gz')['rows']if r['uid']=='landsd/256319:0');assert neg['cap']==45867 and neg['wholeFiniteCapStrictClear']is False and F(neg['exactCertifiedLowerClearanceM'])<0
 row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']=='landsd/254491:0');source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256'];native=decode_original_world_triangles(source.read_bytes());assert digest(native.tobytes())==read(CAP/'diagnostic.json.gz')['completeOriginalNativeWorldSHA256'];face=native[45867];assert digest(face.tobytes())==neg['sourceFacetSHA256'];refs.append(ref(source))
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];xz=terrain[:,:,[0,2]];fxz=face[:,[0,2]];ids=np.flatnonzero(np.all(xz.max(1)>=fxz.min(0),axis=1)&np.all(xz.min(1)<=fxz.max(0),axis=1)).tolist();assert len(ids)<=256,'Bounded complete cap pair census; no truncation';proofs=[dict(originalWholeTerrainFacet=j,proof=verify(face,terrain[j]))for j in ids];gaps=[F(p['proof']['exactMinimumFiniteColumnGapM'])for p in proofs if p['proof']['exactClosedHorizontalProjectionsMeet']];coverage=exact_coverage(face,terrain[ids]);low=min(gaps)if gaps else None
 preservation=read(V4/'terrain.json');overlaps=[dict(uid=f['uid'],exactCapRetainedRectangleOverlapAreaM2=str(rectangle_area(face,f['outwardDyadicRectangleBounds'])),ordinaryForm=f['fullCurrentForm'],priorNegativePreserved=f['rawBeforeAfterFinding'])for f in preservation['preservedOrdinaryForms']if rectangle_area(face,f['outwardDyadicRectangleBounds'])>0]
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',cap=45867,originalSourceCapSHA256=neg['sourceFacetSHA256'],completeOriginalTINWorldSHA256=digest(terrain.tobytes()),completeOriginalTINFacets=len(terrain),completeClosedAABBCandidateTINIds=ids,completeFiniteColumnPairProofs=proofs,completeProjectionCoverage=coverage,exactMinimumOriginalTINClearanceM=str(low)if low is not None else None,originalTINStrictCapClear=bool(low is not None and low>0 and coverage['exactProjectionCovered']),existingRetainedParentNegativeVerbatim=neg,recordedOrdinaryPreservationRectanglePositiveAreaOverlaps=overlaps,comparisonIsOriginalTINNotCurrentRenderedTerrain=True,comparisonOnly=True,wholeCurrentGroundNotChanged=True,retentionRemovalApproved=False,wholeSourceRolesRemainOpen=True,fullFreshCurrentIdentityForeignNativeFoundationRuntimeAndActualFloat32Required=True,sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,terrainChanges=0,newlyInstalled=0,evidenceRefs=refs));print(json.dumps(dict(pairCandidates=len(ids),minimum=str(low),projectionCovered=coverage['exactProjectionCovered'],ordinaryRectangleOverlaps=[r['uid']for r in overlaps],sourceOnly=True)),flush=True)
if __name__=='__main__':main()

"""Source-only exposed-grade paths to one strict clear cap; no root credit.

All failed nonwalls and unqualified walls remain explicit original geometry.
Only independently ordinary-clear faces or exact exposed grade witnesses may
participate in this diagnostic graph; no point or zero-area bridge is added.
"""
from collections import defaultdict,deque
from fractions import Fraction as F
from pathlib import Path
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-bounded-authentic-grade-clear-cap-paths-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010';FLOOR=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-carrier-floor-cap-v1';EDGE=BASE/'xl-terrain-recovery-20261011-parkview-authentic-carrier-edge-census-v1';GRADE=BASE/'xl-terrain-recovery-20261011-parkview-authentic-whole-carrier-vertical-grade-walls-v2';FINITE=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__)),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'exact_original_shared_edge_component_census_v2_20261011.py')]
 for p in [FLOOR,EDGE,GRADE,FINITE]:
  r=read(p/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert ref(p/'diagnostic.json.gz')in r['evidenceRefs'];refs.extend([ref(p/'result.json'),ref(p/'diagnostic.json.gz')])
 fd=read(FLOOR/'diagnostic.json.gz');edge=read(EDGE/'diagnostic.json.gz');grade=read(GRADE/'diagnostic.json.gz');finite=next(r for r in read(FINITE/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert finite['completeOriginalFaces']==63133 and finite['authenticWholeSourceTerrainSHA256']==fd['completeWholeTINWorldSHA256']==grade['completeAuthenticTINWorldSHA256']
 selected=read(PROBE/'selection.json.gz')['rows'];r=next(r for r in selected if r['uid']=='landsd/254491:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];original=decode_original_world_triangles(asset.read_bytes());runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(r for r in read(runtimepath)['rows']if r['uid']=='landsd/254491:0');literal=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];refs.extend([ref(asset),ref(runtimepath),ref(PROBE/'selection.json.gz')]);rows=[]
 assert [r['sourceFace']for r in finite['allFaces']]==list(range(63133))
 for mode,key,t,er,gr,fm in zip(['providerOriginal','capturedActualLiteral'],['completeOriginal','actualRendered'],[original,literal],edge['rows'],grade['rows'],fd['modes']):
  assert digest(t.tobytes())==er['completeSourceWorldSHA256']==finite['completeOriginalWorldSHA256'if key=='completeOriginal'else'completeActualRenderedWorldSHA256'];body=er['capNonzeroEdgeBodyFaces'];assert len(body)==20370 and set(body)==set(er['sharedEdgeProof']['completeRenderableFaceIds']);witnesses={r['globalOriginalFace']:r for r in gr['allExactlyVerticalWallsWithActualGradeInterfaces']if r['positiveExposedGradeLead']};assert len(witnesses)==219
  accounted=[];eligible=set();strict=set();negative_nonwalls=[];unqualified_walls=[]
  for i in body:
   proof=finite['allFaces'][i][key];assert proof['sourceFaceSHA256']==digest(t[i].tobytes())and proof['completeCurrentGroundSHA256']==finite['completeGroundSHA256']and proof['groundProjectionCovered']is True
   clear=proof['existingOrdinaryClearanceBoundProved']is True and F(proof['exactCertifiedLowerClearanceM'])>=F(-1,2);n=np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]);assert not exact_nonrendering(t[i]);wall=abs(n[1])/np.linalg.norm(n)<=.25;qualified_grade=i in witnesses
   if qualified_grade:
    w=witnesses[i];assert w['exactRationalVerticalWall']and w['exactUpperGroundPositiveInterfaces']and F(w['completeFiniteVertexExposure']['exactExposureLowerBoundM'])>0
   if clear or qualified_grade:eligible.add(i)
   if clear:strict.add(i)
   if not clear and not wall:negative_nonwalls.append(i)
   if not clear and wall and not qualified_grade:unqualified_walls.append(i)
   accounted.append(dict(globalOriginalFace=i,strictWholeFiniteOrdinaryClear=clear,exactExposedGradeWitness=qualified_grade,eligibleForDiagnosticConnectivity=clear or qualified_grade,structuralOrRootCredit=False))
  cap=next(p['finite']for p in fm['lowestAndCreditedCapFiniteProofs']if p['face']==57951);assert cap['groundProjectionCovered']and F(cap['exactCertifiedLowerClearanceM'])>0 and cap['sourceFaceSHA256']==digest(t[57951].tobytes());assert 57951 in strict
  incidence=defaultdict(set)
  for i in sorted(eligible):
   for j in range(3):
    a,b=tuple(t[i,j]),tuple(t[i,(j+1)%3]);assert a!=b;incidence[tuple(sorted((a,b)))].add(i)
  adjacency={i:set()for i in eligible}
  for members in incidence.values():
   for i in members:adjacency[i].update(members-{i})
  parent={57951:None};todo=deque([57951])
  while todo:
   i=todo.popleft()
   for j in sorted(adjacency[i]):
    if j not in parent:parent[j]=i;todo.append(j)
  paths=[]
  for i in sorted(witnesses):
   path=[i]
   while path[-1]in parent and parent[path[-1]]is not None:path.append(parent[path[-1]])
   paths.append(dict(globalOriginalGradeWallFace=i,wholeOriginalFacePath=path,hasExactEligibleSharedEdgePathToStrictCap=path[-1]==57951,allNonwallPathFacesKeepStrictWholeFiniteClearance=all(j in strict for j in path if j not in witnesses),rootCredit=False))
  rows.append(dict(mode=mode,completeCarrierFaces=20370,completeOriginalFaceAccounting=accounted,strictClearCapFace=57951,strictClearCapFiniteProof=cap,everyGradeWallPath=paths,all219GradeWallPathsReachStrictCap=all(p['hasExactEligibleSharedEdgePathToStrictCap']for p in paths),excludedFailedNonwallsRetained=negative_nonwalls,excludedUnqualifiedWallsRetained=unqualified_walls,allRawWholeNativeUnprovedFaces=finite['unprovedOriginalFaceBounds'if key=='completeOriginal'else'unprovedActualRenderedFaceBounds'],wholeNativeReaccepted=False));print(dict(mode=mode,gradeWalls=219,reached=sum(p['hasExactEligibleSharedEdgePathToStrictCap']for p in paths),failedNonwallsRetained=len(negative_nonwalls),unqualifiedWallsRetained=len(unqualified_walls)),flush=True)
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=['landsd/254491:0','landsd/255647:0'],rows=rows,evidenceRefs=refs,sourceOnly=True,notCurrentDrawnGround=True,terrainProposalRequired=True,addedGroundRoots=[],sourceGeometryChanges=0,nativeReacceptance=False,installationApproved=False,fullAcceptance=False);save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'bounded-authentic-parkview-complete-grade-walls-strict-cap-exact-shared-edge-path-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0))
if __name__=='__main__':main()

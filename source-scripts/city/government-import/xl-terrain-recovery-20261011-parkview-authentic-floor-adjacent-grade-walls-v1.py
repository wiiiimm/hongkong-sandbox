"""Exact original floor-adjacent wall grade leads, diagnostic not root credit."""
import importlib.util
from collections import defaultdict
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
from exact_original_paired_finite_clearance_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-authentic-floor-adjacent-grade-walls-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010';FLOOR=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-carrier-floor-cap-v1';EDGE=BASE/'xl-terrain-recovery-20261011-parkview-authentic-carrier-edge-census-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();fd=read(FLOOR/'diagnostic.json.gz');edge=read(EDGE/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz')['rows'];r=next(r for r in selected if r['uid']=='landsd/254491:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];original=decode_original_world_triangles(asset.read_bytes());runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(r for r in read(runtimepath)['rows']if r['uid']=='landsd/254491:0');literal=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)]
 refs=[ref(p)for p in [Path(__file__),asset,runtimepath,PROBE/'selection.json.gz',FLOOR/'result.json',FLOOR/'diagnostic.json.gz',EDGE/'result.json',EDGE/'diagnostic.json.gz',HERE/'pending-context.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'original_bound_facet_wall_context_v3_20261010.py',HERE/'original_bound_facet_wall_context_v2_20261010.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']]
 terrain=module('authentic_parkview_terrain',HERE/'pending-context.py');pieces=[]
 for sheet,model in [('11-SE-21B','T38250126000106E10'),('11-SE-16D','T38250132000106E10')]:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;download=read(folder/'original/download.json');pins=[p for p in download['entries']if p['name'].startswith('TERRAIN(TB)/'+model+'/')];assert len(pins)==2 and download['terrainGeometryIncluded']
  for pin in pins:
   p=folder/'terrain'/pin['name'];assert digest(p.read_bytes())==pin['sha256']and len(p.read_bytes())==pin['bytes'];refs.append(ref(p))
  pieces.append(terrain.triangles(folder/'terrain/TERRAIN(TB)'/model/(model+'.gltf')));refs.append(ref(folder/'original/download.json'))
 ground=np.concatenate(pieces);assert digest(ground.tobytes())==fd['completeWholeTINWorldSHA256'];rows=[]
 for mode,t,er,fm in zip(['providerOriginal','capturedActualLiteral'],[original,literal],edge['rows'],fd['modes']):
  assert digest(t.tobytes())==er['completeSourceWorldSHA256'];body=er['capNonzeroEdgeBodyFaces'];floors=fm['everyExactLowestOriginalFace'];incidence=defaultdict(set)
  for i in body:
   for j in range(3):
    a,b=tuple(t[i,j]),tuple(t[i,(j+1)%3]);assert a!=b;incidence[tuple(sorted((a,b)))].add(i)
  near=set()
  for i in floors:
   for j in range(3):near.update(incidence[tuple(sorted((tuple(t[i,j]),tuple(t[i,(j+1)%3]))))])
  walls=[]
  for i in sorted(near-set(floors)):
   normal=np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0])
   if normal[1]!=0:continue
   assert normal[0]!=0 or normal[2]!=0;interfaces=exact_upper_ground_interfaces(t,[i],ground);exposure=best_original_vertex_exposure(t[i],ground);finite=verify(t[i],ground);walls.append(dict(globalOriginalFace=i,authoredFloorAdjacentExactSharedEdge=True,completeFiniteRawClearance=finite,completeFiniteVertexExposure=exposure,exactUpperGroundPositiveInterfaces=interfaces,positiveExposedGradeLead=bool(interfaces)and F(exposure['exactExposureLowerBoundM'])>0,genuineRootCredit=False))
  rows.append(dict(mode=mode,completeNativeCarrierFaces=len(body),everyExactLowestOriginalFace=floors,allExactFloorAdjacentOriginalFaces=sorted(near-set(floors)),allExactlyVerticalFloorAdjacentWalls=walls,wholeOriginalCapFace=57951,independentCapFiniteProof=verify(t[57951],ground),noNativeReacceptance=True));print(dict(mode=mode,adjacentFaces=len(near-set(floors)),verticalWalls=len(walls),positiveGradeLeads=sum(w['positiveExposedGradeLead']for w in walls)),flush=True)
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=['landsd/254491:0','landsd/255647:0'],rows=rows,completeAuthenticTINWorldSHA256=digest(ground.tobytes()),sourceOnly=True,freshCurrentAcceptance=False,terrainProposalRequired=True,allLegacyNativeClearanceNegativesPreserved=True,addedGroundRoots=[],nativeReacceptance=False,sourceGeometryChanges=0,fullAcceptance=False,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);module('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-only-authentic-parkview-original-floor-adjacent-wall-grade-feasibility-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0))
if __name__=='__main__':main()

"""Bounded exact authentic terrain floor/cap feasibility, never current acceptance."""
import importlib.util,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from exact_original_paired_finite_clearance_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-parkview-authentic-two-TIN-carrier-floor-cap-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');selected=read(PROBE/'selection.json.gz');r=next(r for r in selected['rows']if r['uid']=='landsd/254491:0');asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']=='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77';tri=decode_original_world_triangles(raw)
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(r for r in read(runtimepath)['rows']if r['uid']=='landsd/254491:0');literal=np.asarray(rt['position'],float).reshape(-1,3)[np.asarray(rt['index'],np.uint32).reshape(-1,3)];assert tri.shape==literal.shape==(63133,3,3);body=g['components'][170]['globalOriginalFaces'];assert len(body)==20370 and 57951 in body
 refs=[ref(p)for p in [Path(__file__),asset,runtimepath,PROBE/'selection.json.gz',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'pending-context.py',HERE.parent/'citywide-native/convert.py',ROOT/'docs/astra-city/mui-wo-buildings/review/prepare_model_sample.py',ROOT/'docs/astra-city/mui-wo-buildings/review/bake_model_geometry.py']];pieces=[]
 spec=importlib.util.spec_from_file_location('auth',HERE/'pending-context.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 for sheet,model in [('11-SE-21B','T38250126000106E10'),('11-SE-16D','T38250132000106E10')]:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;download=read(folder/'original/download.json');pins=[p for p in download['entries']if p['name'].startswith('TERRAIN(TB)/'+model+'/')];assert len(pins)==2 and download['terrainGeometryIncluded']is True
  for pin in pins:
   path=folder/'terrain'/pin['name'];assert digest(path.read_bytes())==pin['sha256'] and len(path.read_bytes())==pin['bytes'];refs.append(ref(path))
  gltf=folder/'terrain/TERRAIN(TB)'/model/(model+'.gltf');pieces.append(m.triangles(gltf));refs.extend(ref(p)for p in [folder/'original/download.json',folder/'recovery.json',folder/'directory/result.json'])
 ground=np.concatenate(pieces);lo=np.minimum(tri[body].min(axis=(0,1)),literal[body].min(axis=(0,1)))[[0,2]];hi=np.maximum(tri[body].max(axis=(0,1)),literal[body].max(axis=(0,1)))[[0,2]];terrain_ids=np.flatnonzero(np.all(ground[:,:,[0,2]].max(axis=1)>=lo,axis=1)&np.all(ground[:,:,[0,2]].min(axis=1)<=hi,axis=1));selected_ground=ground[terrain_ids];modes=[]
 for mode,t in [('provider-original',tri),('captured-actual-literal',literal)]:
  bottom=float(t[body,:,1].min());floor=[i for i in body if t[i,:,1].min()==bottom];interfaces=exact_upper_ground_interfaces(t,floor,selected_ground);proofs=[dict(face=i,finite=verify(t[i],selected_ground))for i in floor+[57951]];modes.append(dict(mode=mode,completeCarrierOriginalFaces=body,carrierBottomHKPD=bottom,everyExactLowestOriginalFace=floor,completeLowestFaceUpperGroundInterfaces=interfaces,lowestAndCreditedCapFiniteProofs=proofs,sourceOnlyGradeWitnesses=len(interfaces),structuralRootCredit=False));print(dict(mode=mode,lowestFaces=len(floor),gradeWitnesses=len(interfaces),completeFaces=len(body)),flush=True)
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=['landsd/254491:0','landsd/255647:0'],modes=modes,wholeAuthenticTINFacets=len(ground),completeWholeTINWorldSHA256=digest(ground.tobytes()),selectedWholeTerrainFacetIds=terrain_ids.tolist(),sourceOnlyAuthenticatedTerrainComparison=True,notCurrentDrawnGround=True,terrainProposalPublished=False,nativeReacceptance=False,sourceGeometryChanges=0,installationApproved=False,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);f.freeze(BATCH,'bounded-complete-carrier-lowest-floor-and-cap-two-authentic-TIN-feasibility-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnlyDiagnostic=True,sourceGeometryChanges=0,nativeReacceptance=False))
if __name__=='__main__':main()

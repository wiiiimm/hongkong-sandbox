"""Source-only exact nonzero carrier connectivity, no ground-root credit."""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_original_shared_edge_component_census_v2_20261011 import census,exact_nonrendering
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-authentic-carrier-edge-census-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-parkview-block11-complete-original-current-probe-v1-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-parkview-block11-complete-original-support-v1';FLOOR=BASE/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-carrier-floor-cap-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();fr=read(FLOOR/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(fr['jobId'],)).fetchone()==('complete',fr)
 assert ref(FLOOR/'diagnostic.json.gz')in fr['evidenceRefs'];fd=read(FLOOR/'diagnostic.json.gz');g=read(GRAPH/'diagnostic.json.gz');faces=g['components'][170]['globalOriginalFaces'];assert len(faces)==20370 and 57951 in faces
 selected=read(PROBE/'selection.json.gz')['rows'];r=next(r for r in selected if r['uid']=='landsd/254491:0');asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']=='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77';original=decode_original_world_triangles(asset.read_bytes())
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';rt=next(r for r in read(runtimepath)['rows']if r['uid']=='landsd/254491:0');literal=np.asarray(rt['position']).reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];assert original.shape==literal.shape==(63133,3,3);rows=[]
 for mode,t,fm in zip(['providerOriginal','capturedActualLiteral'],[original,literal],fd['modes']):
  proof=census(t,faces);groups=proof['sharedEdgeConnectedComponents'];capgroup=next(group for group in groups if 57951 in group);floorids=fm['everyExactLowestOriginalFace'];zero=proof['exactNonrenderingOriginalFaces'];assert all(exact_nonrendering(original[i])and exact_nonrendering(literal[i])and exact_nonrendering(literal[i].astype(np.float32).astype(float))for i in zero)
  rows.append(dict(mode=mode,completeCarrierFaces=20370,sharedEdgeProof=proof,capFace=57951,capNonzeroEdgeBodyFaces=capgroup,exactLowestFloorFaces=floorids,lowestFloorFacesInCapEdgeBody=[i for i in floorids if i in set(capgroup)],allNonrenderingFacesSourceLiteralFloat32Zero=True,completeSourceWorldSHA256=digest(t.tobytes()),authenticTINWholeSHA256=fd['completeWholeTINWorldSHA256'],genuineGradeRootCredit=False,wholeLegacyNativeReaccepted=False));print(dict(mode=mode,nonzeroBodies=len(groups),capBodyFaces=len(capgroup),zeroFaces=len(zero),floorFaces=len(floorids),floorInCapBody=sum(i in set(capgroup)for i in floorids)),flush=True)
 refs=[ref(p)for p in [Path(__file__),asset,runtimepath,PROBE/'selection.json.gz',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',FLOOR/'diagnostic.json.gz',FLOOR/'result.json',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'test_exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_packed_world_geometry_20261009.py']]
 result=dict(uids=['landsd/254491:0','landsd/255647:0'],rows=rows,evidenceRefs=refs,sourceOnly=True,frozenAuthenticTINComparisonOnly=True,freshCurrentAcceptance=False,sourceGeometryChanges=0,nativeReacceptance=False,addedGroundRoots=[],fullAcceptance=False,installationApproved=False);save(DOC/'diagnostic.json.gz',result)
 s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'source-only-parkview-authentic-carrier-exact-nonzero-edge-connectivity-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,sourceGeometryChanges=0,nativeReacceptance=False,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()

"""Complete49 root51 source/literal facets under unchanged ordinary-.5 clearance."""
import importlib.util,numpy as np
from fractions import Fraction as F
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-cullinan-west-root51-complete-finite-v1';DOC=BASE/BATCH;PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v2-20261010';GRAPH=BASE/'xl-terrain-recovery-20261010-cullinan-west-three-current-original-complete-support-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']=='landsd/262871:0');p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];tri=decode_original_world_triangles(p.read_bytes());rtpath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';runtime=next(r for r in read(rtpath)['rows']if r['uid']=='landsd/262871:0');actual=np.asarray(runtime['position']).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);g=read(GRAPH/'diagnostic.json.gz');faces=g['components'][51]['globalOriginalFaces'];assert len(faces)==49;rows=[]
 for name,t in [('providerOriginal',tri),('actualLiteral',actual)]:
  proofs=[]
  for i in faces:
   proof=verify(t[i],ground);proofs.append(dict(globalOriginalFace=i,proof=proof));print(dict(mode=name,face=i,completeFiniteCovered=proof['groundProjectionCovered'],ordinaryClearance=proof['existingOrdinaryClearanceBoundProved']),flush=True)
  rows.append(dict(mode=name,completeOriginalRootFaces=faces,completeWorldSHA256=digest(t.tobytes()),completeGroundSHA256=digest(ground.tobytes()),all49FacetProofs=proofs,allCompleteFiniteOrdinaryClearanceProved=all(p['proof']['existingOrdinaryClearanceBoundProved']for p in proofs),exactWholeComponentMinimumGapM=str(min(F(p['proof']['exactCertifiedLowerClearanceM'])for p in proofs))))
 refs=[ref(p)for p in [Path(__file__),p,rtpath,PROBE/'selection.json.gz',PROBE/'result.json',GRAPH/'diagnostic.json.gz',GRAPH/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_original_closed_projection_intersection_20261010.py']]
 for folder in [PROBE,GRAPH]:
  result=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 d=dict(uids=['landsd/262871:0','landsd/161931:0','landsd/120158:0'],component=51,rows=rows,nativeReacceptance=False,noSampledClearanceSubstitution=True,ordinaryMinimumLimitM=-.5,fullAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',d);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete49-current-native-root51-original-literal-paired-finite-ordinary-clearance-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=d['uids'],completeRootFaces=49,allCompleteOriginalLiteralFacetsClear=all(r['allCompleteFiniteOrdinaryClearanceProved']for r in rows),nativeReacceptance=False,fullAcceptance=False))
if __name__=='__main__':main()

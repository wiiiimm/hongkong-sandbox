"""Complete current role continuation; full fenced numerical source facts preserved."""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest
from complete_disjoint_source_role_replay_v2_20261010 import recheck as replay
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-terrain-recovery-hkdi-block-b-post-atomic-complete-current-role-v2-20261010';DOC=BASE/BATCH
CURRENT='afe71ffa851d82ab2d1350834b5a6cd1484f28e481bd6bf866ca7a6f73e05d0b'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck():
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 result=replay(physical=BASE/'government-xl-terrain-recovery-hkdi-block-b-unchanged-current-terrain-physical-v2-20261010',context_path=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-hkdi-block-b-unchanged-current-terrain-physical-v2-20261010/context.json.gz',old_role_folder=BASE/'government-xl-terrain-recovery-hkdi-block-b-current-qualified-native-role-v3-20261010',old_role_sha='51644ac581fa29470bd621bb04053b801d1cc0fdc507192dc0641d4d1ed43b89',rebind_folder=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-post-atomic-disjoint-rebind-v3',owned_sources={'landsd/89613:0': '447d5391c1e8f0044ac5b86b6597d11392ea861cac3389fe2b3e81413ebbdc34'},retained_sources={'landsd/22089:0': '5cd70cb3bdb879ca96528fd1ff6ce29cc3b61c054b70456ec169fc9cf4831c40'})
 result['evidenceRefs']=sorted({r['path']:r for r in result['evidenceRefs']+[ref(Path(__file__))]}.values(),key=lambda r:r['path'])
 return result
def main():
 assert not DOC.exists();result=recheck();save(DOC/'typed-role.json.gz',result)
 s=importlib.util.spec_from_file_location('current_region_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-source-bound-disjoint-current-role-continuation-v1',[ROOT/r['path']for r in result['evidenceRefs']],dict(uids=result['uids'],currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,newNumericalAcceptanceCredit=False,completeOriginalFaces=result['completeOriginalFaces'],completeOriginalComponents=result['completeOriginalComponents'],typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0))
 print(dict(currentTypedPhysicalAccepted=True,completeOriginalFaces=result['completeOriginalFaces'],completeOriginalComponents=result['completeOriginalComponents'],currentManifest=result['currentManifest']),flush=True)
if __name__=='__main__':main()

"""Complete current role continuation; full fenced numerical source facts preserved."""
from pathlib import Path
import importlib.util
from run import ROOT,HERE,read,save,digest
from complete_disjoint_source_role_replay_v2_20261010 import recheck as replay
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-terrain-recovery-park-haven-post-atomic-complete-current-role-v2-20261010';DOC=BASE/BATCH
CURRENT='afe71ffa851d82ab2d1350834b5a6cd1484f28e481bd6bf866ca7a6f73e05d0b'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck():
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 result=replay(physical=BASE/'government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010',context_path=ROOT/'source-scripts/city/government-import/local/government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010/frozen-inputs/context.json.gz',old_role_folder=BASE/'government-xl-terrain-recovery-park-haven-current-complete-ordinary-role-v3-20261010',old_role_sha='25fc7e4190b8a248193f901f832a76580e2135e54fe4aefd447e70ef064b3df2',rebind_folder=BASE/'xl-terrain-recovery-20261010-park-haven-post-atomic-disjoint-rebind-v3',owned_sources={'landsd/246467:0': 'de104bedd64810cec4253142280fa27e4c91d4d98807667852ec1073419c840d', 'landsd/320705:0': '53e7601fae7d72d2dcc4ee5d32002628c927769095cd6d9d07f5c2fa7afc95e9'},retained_sources={'landsd/246270:0': 'd5284c8d1c3bbe5e6d950660b77ba10e3b4b5e9672df7472137cf201a8de0394'})
 result['evidenceRefs']=sorted({r['path']:r for r in result['evidenceRefs']+[ref(Path(__file__))]}.values(),key=lambda r:r['path'])
 return result
def main():
 assert not DOC.exists();result=recheck();save(DOC/'typed-role.json.gz',result)
 s=importlib.util.spec_from_file_location('current_region_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-source-bound-disjoint-current-role-continuation-v1',[ROOT/r['path']for r in result['evidenceRefs']],dict(uids=result['uids'],currentTypedPhysicalAccepted=True,reasons=[],sourceGeometryChanges=0,newNumericalAcceptanceCredit=False,completeOriginalFaces=result['completeOriginalFaces'],completeOriginalComponents=result['completeOriginalComponents'],typedRole=ref(DOC/'typed-role.json.gz'),browserRequired=True,publication=False,newlyInstalled=0))
 print(dict(currentTypedPhysicalAccepted=True,completeOriginalFaces=result['completeOriginalFaces'],completeOriginalComponents=result['completeOriginalComponents'],currentManifest=result['currentManifest']),flush=True)
if __name__=='__main__':main()

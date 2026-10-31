"""Bind complete current Man Oi acceptance to staged original-source loading."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
DOC=BASE/'xl-terrain-recovery-20261010-man-oi-plain-stage-config-v1'
ROLE=BASE/'xl-terrain-recovery-20261010-man-oi-current-complete-support-v2'
PHYSICAL=BASE/'government-xl-man-oi-complete-original-physical-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();typed=read(ROLE/'typed-role.json.gz')
 assert typed['independentPhysicalChecksPassed'] is True and typed['unresolvedIndependentPhysicalReasons']==[] and typed['manifestSHA256']==ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']
 cfg=dict(schema='plain-single-source-original-stage-v1',batch='government-xl-man-oi-plain-typed-stage-v1-20261010',sources={'landsd/75697:0':'6c7de45ebc146c7be0eeef151d5f217ae0c0cd72525eb74d46077bbd66c0b80d'},completeOriginalFaces=2160,completeOriginalComponents=4,plainNewTerrain=True,retainedNativeUIDs=[],supportDependencies=[],physicalReceipt=ref(PHYSICAL/'result.json'),currentRoleReceipt=ref(ROLE/'result.json'),currentTypedRole=ref(ROLE/'typed-role.json.gz'),currentRoleRunner=ref(HERE/'xl-terrain-recovery-20261010-man-oi-current-complete-support-v2.py'),plainStageRunner=ref(HERE/'xl-terrain-recovery-20261010-plain-single-source-stage-v1.py'),plainLiveRunner=ref(HERE/'xl-terrain-recovery-20261010-plain-single-source-live-v1.py'),area='Man Oi House complete unchanged government original',captureDirection=[-.65,.65,-.5],placementReview='Complete original Man Oi House tower: all2160 original and actual rendered faces satisfy the existing whole-facet -.5m limit. Allfour original components reach one genuine ground root through independently replayed positive-dimensional source contacts. Fresh current identity, whole foundation,13 neighbouring forms, complete native world bounds, terrain routing, sampler and runtime gates pass without resolving or waiving any physical reason. Original compressed government source, root pose, streams, elevations and every component are retained. No procedural window skin, no model simplification, no AI geometry modelling. Man Oi is an auxiliary source outside the fixed521 XL inventory; its installation earns no XL completion credit.',producer=ref(Path(__file__)))
 save(DOC/'config.json',cfg);print(str((DOC/'config.json').relative_to(ROOT)),flush=True)
if __name__=='__main__':main()

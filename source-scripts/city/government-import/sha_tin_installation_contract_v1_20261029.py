"""Exact Sha Tin original-only installation constants; no publication at import."""
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-sha-tin-'
BATCH=P+'seven-original-qualified-stage-v1-20261029'
DOC=BASE/BATCH
STAGE=HERE/'local'/BATCH
QUALIFICATION=BASE/(P+'seven-original-qualification-v1-20261029')/'ROOT-SOURCE-REVIEW.json'
UIDS=['landsd/231013:0','landsd/23220:0','landsd/23759:0','landsd/23761:0','landsd/238142:0','landsd/271344:0','landsd/92881:0']
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))

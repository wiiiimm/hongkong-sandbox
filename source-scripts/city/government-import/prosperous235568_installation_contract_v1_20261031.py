"""Exact six-original Prosperous Garden installation constants; no side effects."""
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-prosperous235568-';BATCH=P+'qualified-stage-v1-20261031';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
QUALIFICATION=BASE/(P+'original-qualification-v1-20261031')/'ROOT-SOURCE-REVIEW.json'
UIDS=['landsd/234691:0','landsd/235119:0','landsd/235568:0','landsd/235888:0','landsd/236076:0','landsd/237129:0']
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))

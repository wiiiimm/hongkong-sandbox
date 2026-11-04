"""Exact five-original Kai Tak installation constants; no side effects."""
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-arena275446-after-palazzo-';BATCH=P+'five-qualified-stage-v1-20261101';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
QUALIFICATION=BASE/(P+'five-original-qualification-v2-20261101')/'ROOT-SOURCE-REVIEW.json'
UIDS=['landsd/275446:0','landsd/318697:0','landsd/318701:0','landsd/318704:0','landsd/318722:0']
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))

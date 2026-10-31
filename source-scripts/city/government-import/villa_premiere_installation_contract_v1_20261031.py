"""Exact five-original Villa Premiere installation constants; no side effects."""
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-villa-premiere89917-';BATCH=P+'qualified-stage-v3-20261031';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
QUALIFICATION=BASE/(P+'original-qualification-v2-20261031')/'ROOT-SOURCE-REVIEW.json'
UIDS=['landsd/121309:0','landsd/148052:0','landsd/58497:0','landsd/63823:0','landsd/89917:0']
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))

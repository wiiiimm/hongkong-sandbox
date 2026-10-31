"""Exact twenty-original Palazzo installation constants; no side effects."""
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'twenty-qualified-stage-v2-20261101';DOC=BASE/BATCH;STAGE=HERE/'accepted'/BATCH
QUALIFICATION=BASE/(P+'twenty-original-qualification-v2-20261101')/'ROOT-SOURCE-REVIEW.json'
UIDS=['landsd/10198:0', 'landsd/252555:0', 'landsd/252556:0', 'landsd/252558:0', 'landsd/252774:0', 'landsd/304541:0', 'landsd/340334:0', 'landsd/68540:0', 'landsd/71042:0', 'landsd/71045:0', 'landsd/71688:0', 'landsd/71703:0', 'landsd/71709:0', 'landsd/71886:0', 'landsd/72626:0', 'landsd/76610:0', 'landsd/88303:0', 'landsd/88780:0', 'landsd/88899:0', 'landsd/89150:0']
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))

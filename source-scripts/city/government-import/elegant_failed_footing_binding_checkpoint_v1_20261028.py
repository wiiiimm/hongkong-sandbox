"""Mark the first private qualified-fragment preparation as rejected, not approved."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'

def main():
 batch=PREFIX+'qualified-footing-fragment-v1-20261028';out=BASE/batch;assert not(out/'result.json').exists()
 review=read(out/'qualified-footing-review.json');update=read(out/'plan-fragment.json')['basicPodiumFootings'][0]
 tile=ROOT/'3d-viewer'/update['tile'];b=next(b for b in read(tile)['buildings']if b['uid']==update['uid'])
 podium=module('failed_footing_binding_guard',HERE.parent/'island-detail-integration/basic_podium_footings.py')
 assert digest(tile.read_bytes())==review['tileSHA256']==update['tileSHA256']and b==update['before']
 assert podium.value_sha(b)!=review['sourceFormSHA256']
 result=dict(uids=[b['uid']],status='rejected-prepared-source-form-canonical-hash-mismatch',qualifiedFootingReview=False,realFootingStagerPassed=False,preparedReviewMustNotBeUsed=True,visualReviewApproved=False,installationApproved=False,publication=False,sourceGeometryChanges=0,
  actualSourceFormSHA256=podium.value_sha(b),preparedSourceFormSHA256=review['sourceFormSHA256'],
  reason='The live tile uses terrainAudit.resolutions:[70.0] while prepared input used[70]. Python value equality allowed the draft before-form assertion but the unchanged strict source-form hash gate correctly rejected it. This preparation never passed the stager and must not be used as qualified evidence. V2creates a fresh exact-live-form review after independently proving JavaScript value equality and exact production geometry attribute equality. No source tile, guard or earlier draft was changed.')
 save(out/'rejected-preparation.json',result)
 module('failed_footing_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'rejected-private-footing-preparation-source-form-hash-binding',
  [Path(__file__),HERE/'elegant_qualified_footing_fragment_v1_20261028.py',HERE.parent/'island-detail-integration/basic_podium_footings.py',tile],result)

if __name__=='__main__':main()

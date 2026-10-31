"""Record the exact five inspected BASIC junction views and unresolved next action."""
from pathlib import Path
import uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'retained-five-view-review-v1-20261101'
def main():
    keys=['68540','88780','252555','252556','252558'];uids=['landsd/'+k+':0'for k in keys]
    c=reservations.claim('palazzo-five-bounded-review-'+str(uuid.uuid4()),['building:'+u for u in ['landsd/76610:0',*uids]],batch=BATCH,ttl=1800);assert c['ok'],c;lease=c['reservation']
    try:
        refs=[Path(__file__)];images=[];assert not(BASE/BATCH).exists()
        for key in keys:
            batch=P+key+'-retained-interface-views-v1-20261101';_,pins=authenticate(BASE/batch);refs.append(BASE/batch/'result.json');p=BASE/batch/'full-height.png';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),basicUid='landsd/'+key+':0'))
        rebind=P+'owner64-foreign-current-rebind-v1-20261101';authenticate(BASE/rebind);refs.append(BASE/rebind/'result.json')
        result=dict(uids=['landsd/76610:0',*uids],imagesActuallyInspected=images,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelAndEffort='Unknown from tool-visible metadata; not inferred',sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,completeNeighbourInterpretationAccepted=False,installationApproved=False,publication=False,status='in-process-local-source-role-investigation',observation='Five exact full-height plots inspected individually, each with two opposite directions. Existing original deck/lower-wall details run within and around retained coarse BASIC bodies. The three larger forms252555/252556/252558 have substantial overlapping body context; plot presence and unchanged support warnings alone do not establish valid coexistence or permit counterpart suppression.',nextAction='Determine exact source-part coverage for the five retained forms from primary source membership and finite original/BASIC interfaces; use current close browser views as needed. Keep original sources and retained BASIC geometry unchanged pending bounded whole-scene review. No human decision or AI geometry modelling is currently required.',qualification=__doc__+' Original-height alternate exports were generated but are not claimed visually inspected. Existing raw contacts, strict diagnostics and publication guards remain unchanged.')
        assert reservations.owns(lease);save(BASE/BATCH/'ROOT-RETAINED-JUNCTION-REVIEW.json',result)
        module('palazzo_retained_five_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-retained-five-junction-inspection-no-approval',refs,result)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

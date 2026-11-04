"""Persist completed physical review and the separate automatic-approval hold."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-university-hall-93417-';batch=prefix+'pending-standalone-approval-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];evidence={}
    for name,file in [(prefix+'physical-review-v2-20261024','ROOT-PHYSICAL-REVIEW.json'),(prefix+'source-current-wall-comparison-v1-20261024','summary.json'),(prefix+'wall-source-views-v3-20261024','summary.json')]:
        receipt,pins=authenticate(base/name);path=base/name/file;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([base/name/'result.json',path]);evidence[name]=receipt['jobId']
    result=dict(uids=['landsd/93417:0'],status='held-for-automatic-review-standalone-path-approval',heldForHumanDecision=True,heldForCompute=False,aiGeometryModellingRequired=False,permanentRejection=False,installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,evidence=evidence,
        completed='Bounded physical/identity/current-neighbour review is complete for exact original mesh and unchanged current terrain. Fourteen lower vertical wall intersections accepted under source-specific exposed-wall interpretation; raw numerical failures remain. Both corrected two-angle wall exports inspected.',
        correction='Prior current-progressv1/HANDOFF incorrectly said before-BASIC foreign contacts were zero. Actual frozen report has14positive BASIC boundary contacts/zeroarea; the original haszero contacts/zeroarea in every4world. No report bytes or historical receipt changed. Source/current authenticTIN comparison reproduces2of14wall penetrations;12are specific to coarse current ground, not called provider-authored.',
        automaticReviewRejections=[
            'Creation of standalone staging/publishing/installation adapters was rejected as potential weakening of retained-support acceptance checks. That command did not execute.',
            'Executing proposed standalone staged-browser path was then rejected as potential bypass of the prior guard decision. That command did not execute.'
        ],requestedApproval='Narrow approval pending for a standalone University Hall path requiring zero source support dependencies, preserving existing publisher retained-support checks across all current models, requiring desktop/mobile source/picking/collision/fallback checks before installation.',
        currentEvidence='Current source entry has no supportDependencies or retainedBasicSupportDependencies.6468of6863currently installed entries also have no supportDependencies. Existing island-detail-integration/publish.py invokes stage_retained_basic_support globally; it remains unchanged. No staged/public catalogue or installed model changed.',
        nextActions=['Do not bypass the automatic-approval rejection. Await the explicit narrow approval before creating/running the rejected adapter path.','Continue other original XL geometry/source work independently; this is not a source corruption or permanent placement rejection.'],scriptExternalAICalls=0,aiGeometryModelling=False)
    save(out/'summary.json',result);module('university_approval_hold_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'university-hall-completed-physical-review-and-separate-automatic-approval-hold',refs,result)

if __name__=='__main__':main()

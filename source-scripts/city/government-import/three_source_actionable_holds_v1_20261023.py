"""Save exact actionable repair holds, never treating constructor failure as corruption."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-three-actionable-holds-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)]
    names=['government-xl-next-repairs-yoho-mall-ii-273672-retained-followthrough-v1-20261023','government-xl-next-repairs-yoho-mall-ii-273672-source-ground-comparison-v1-20261023','government-xl-next-repairs-hanford-plaza-276187-bounded-followthrough-v1-20261023','government-xl-next-repairs-hanford-plaza-276187-bounded-coastal-nonregression-v2-20261023','government-xl-next-repairs-hanford-original-family-discovery-v2-20261023','government-xl-next-repairs-hanford-missing-original-files-v1-20261023','government-xl-next-repairs-hanford-six-basic-towers-original-support-v1-20261023','government-xl-next-repairs-two-original-terrain-domain-diagnostics-v1-20261023','government-xl-next-repairs-hanford-plaza-276187-domain-caps-v1-20261023','government-xl-next-repairs-west-kowloon-bus-255415-source-ground-comparison-v1-20261023']
    jobs=[]
    for name in names:
        receipt,pins=authenticate(base/name);path=base/name/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.extend([base/name/'result.json',path]);jobs.append(dict(batch=name,jobId=receipt['jobId']))
    rows=[dict(uid='landsd/273672:0',name='Yoho Mall II',status='held-for-compute-and-source-reference-review',reasonCodes=['two-basic-neighbour-ground-gap-regressions','authored-source-subgrade-geometry','unchanged-legacy-native-support-failures'],nextActions=['Protect current forms3006/3007 in the bounded terrain return.','Preserve and independently qualify unchanged native294858/300857 support failures; no new burial was measured.','Review complete original-source/reference-terrain conformance for145 exact below-grade faces before any source-specific interpretation. Minima alone grant no nonregression or basement approval.']),
          dict(uid='landsd/276187:0',name='Hanford Plaza',status='held-for-source-access-and-compute',reasonCodes=['seven-exact-original-family-assets-not-local','six-basic-tower-assembly-mismatches','float32-coastal-return-depth-regressions','authored-source-subgrade-geometry'],nextActions=['Recover the seven hash-pinned originals from the existing source object store. Three of ten family originals are currently local.','Use the complete eight-tower/two-podium family; all24 current-basic-on-podium interfaces failed, so shared parent is not acceptance.','Correct and re-prove nine final Float32 coastal-face depth differences, at most roughly55micrometres; do not label the failed proof passed.','Retain the original new-land1.2m floor and all source/identity/current-neighbour/runtime/browser gates.']),
          dict(uid='landsd/255415:0',name='West Kowloon Station Bus Terminus',status='held-for-compute',reasonCodes=['authentic-tin-domain-coverage-gap-outside-building','authentic-coastal-terrain-below-land-floor','one-authored-source-wall-below-ordinary-clearance'],nextActions=['Building projection is covered by original TIN; build a bounded terrain return retaining actual coastal parent instead of requiring a full unrelated original-TIN rectangle.','Keep the original land-height floor for new source land and prove inherited coastal depth nonregression.','Preserve source face14760 exact original gap-0.5173883602853782m; do not waive the0.5m rule or alter source geometry to force credit.'])]
    for row in rows:row.update(installationApproved=False,permanentRejection=False,aiGeometryModellingRequired=False,sourceGeometryChanges=0)
    result=dict(uids=[r['uid']for r in rows],rows=rows,evidenceJobs=jobs,wholeFixedXLCounts=dict(total=521,installedVerified=339,remaining=182),newlyInstalled=0,publication=False,sourceGeometryChanges=0,scriptExternalAICalls=0)
    save(out/'summary.json',result);module('three_actionable_holds_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'original-source-actionable-repair-holds-and-next-steps',refs,result)


if __name__=='__main__':main()

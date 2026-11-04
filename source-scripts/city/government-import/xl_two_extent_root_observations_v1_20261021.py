"""Record ROOT's inspected source views without granting identity acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-two-extent-root-observations-v1-20261021';DOC=BASE/BATCH

def main():
    assert not DOC.exists();source=BASE/'government-xl-two-extent-context-v1-20261021';_,pins=authenticate(source);summary=source/'summary.json';assert digest(summary.read_bytes())==pins[str(summary.relative_to(ROOT))];refs=[Path(__file__),source/'result.json',summary];images=[]
    for row in read(summary)['rows']:
        p=ROOT/row['image'];h=digest(p.read_bytes());assert h==pins[row['image']];images.append(dict(path=row['image'],sha256=h));refs.append(p)
    result=dict(uids=['landsd/240332:0','landsd/17633:0'],reviewer='ROOT',imagesActuallyViewed=images,observations=[dict(uid='landsd/240332:0',observation='Exact source image shows a spectator-stand-like structure with repeated canopy lobes and end extensions outside the recorded footprint. Raw maximum extent is12.871m with no unrelated form overlap. Canopy interpretation is a visual hypothesis, not external identity confirmation.',nextCheck='Confirm which stadium stand this exact CSUID denotes and bind authoritative structure/roof evidence before scoped identity review.'),dict(uid='landsd/17633:0',observation='The cross-shaped tower largely follows the recorded footprint. The largest projection extension appears near ground level as a narrow rectangular apron; orange facade edges also extend slightly beyond the footprint. Raw maximum extent16.348m remains.',nextCheck='Locate and classify the farthest original faces and compare with authoritative site evidence; do not approve from whole-source image alone.')],researchLeads=[dict(url='https://www.info.gov.hk/gia/general/201307/17/P201307170283.htm',status='Search returned stadium stand/covers discussion; full-page fetch timed out. No acceptance credit.'),dict(url='https://hos.housingauthority.gov.hk/50A/TreasureHunt/en/chingho.html',status='Official estate context page opened, but does not establish this exact building apron. No acceptance credit.')],identityReviewApproved=False,installationApproved=False,rawFailuresPreserved=True,sourceGeometryChanges=0)
    save(DOC/'ROOT-OBSERVATIONS.json',result);module('root_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'inspected-original-extent-observations',refs,result)

if __name__=='__main__':main()

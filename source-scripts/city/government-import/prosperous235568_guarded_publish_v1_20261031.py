"""Exact-source lease-fenced canonical publication; no threshold or global guard edits."""
import argparse,copy,sys
from contextlib import contextmanager
from pathlib import Path
import prosperous235568_installation_contract_v1_20261031 as stage
from run import ROOT,HERE,read,save,digest,connect,reservations,dict_row
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from fuying_five_member_terrain_stage_v1_20261029 import complete_boundary_validators
from original_supported_catalogue_scope_v1_20261024 import verify
BATCH=stage.P+'six-original-installed-v1-20261031'
APPROVAL_KEYS={'sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved','sourceIdentityReview','sourceFunctionalApplicability','placementReview','aiGeometryModelling','sourceEvidenceInterpretationUsedAI'}

def evidence():
    result,pins=authenticate(stage.DOC);assert result['canonicalFullPublisherDryRunPassed']and result['qualifiedForLiveVerification']and result['qualifiedExactStage']and result['uids']==stage.UIDS
    refs={}
    def bind(folder):
        receipt,values=authenticate(folder)
        for p,h in values.items():assert p not in refs or refs[p]==h;refs[p]=h
        return receipt,values
    bind(stage.DOC);_,qpins=bind(stage.QUALIFICATION.parent);assert digest(stage.QUALIFICATION.read_bytes())==qpins[str(stage.QUALIFICATION.relative_to(ROOT))];q=read(stage.QUALIFICATION)
    assert all(q[k]is True for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance','completeFourWorldFoundations','qualifiedForLiveVerification'])
    assert q['uids']==stage.UIDS and q['sourceGeometryChanges']==q['sourcePoseChanges']==0 and not q['publication'];assert stage.ref(ROOT/'3d-viewer/city/data/manifest.json')==q['currentManifest']
    oldbatch=stage.P+'six-original-atomic-retry-v2-20261031';_,oldpins=bind(stage.BASE/oldbatch);oldpath=HERE/'local'/oldbatch/'catalogue.json';assert digest(oldpath.read_bytes())==oldpins[str(oldpath.relative_to(ROOT))];original=read(oldpath)['models'];models=read(stage.STAGE/'catalogue.json')['models'];assert len(original)==len(models)==6
    assert verify(models,q['sourceSHA256ByUid'],q['supportByUid'])
    for old,new in zip(original,models):
        assert {k:v for k,v in old.items()if k not in APPROVAL_KEYS}=={k:v for k,v in new.items()if k not in APPROVAL_KEYS}
        assert new['uid']==old['uid']and new['sha256']==q['sourceSHA256ByUid'][new['uid']]
        assert new['activationGroup']==stage.UIDS and new['rootTranslation']==[-834500,0,816500]and new.get('verticalPlacementOffsetHKPD',0)==0
        assert all(new[k]is True for k in ['sourceIdentityReviewed','identityReviewApproved','placementReviewed','publicationApproved'])and new['aiGeometryModelling']is False
        assert new['sourceIdentityReview']==new['sourceFunctionalApplicability']==stage.ref(stage.QUALIFICATION)
        assert stage.ref(stage.STAGE/new['asset'])['sha256']==new['sha256']
    plan=read(stage.STAGE/'plan.json');assert set(plan)=={'areas','topLevelTerrainPatches'};assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1
    area=plan['areas'][0];assert area['catalogue']==str((stage.STAGE/'catalogue.json').relative_to(ROOT))and area['destination']=='city/data/official-models/'+stage.BATCH+'/catalogue.json'
    terrain=plan['topLevelTerrainPatches'][0];assert terrain['destination']=='city/data/government-native-prosperous-garden-six-original-v1-20261031.json'and terrain['sha256']=='88524c63747d154b1184688afed7951034f07c84da8688ad98ff418a6965c410'and stage.ref(ROOT/terrain['source'])['sha256']==terrain['sha256']
    browser=stage.BASE/(stage.P+'qualified-stage-lifecycle-v1-20261031');life,lpins=bind(browser);assert life['browserPassed']and life['cases']==life['expectedCases']==7 and life['qualifiedExactStage']and life['exactCanonicalCatalogueEncodingVerified']and life['sourceMetadataDiffLimitedToApprovalKeys']
    report=read(browser/'browser/report.json');assert report['passed']and not report['pageErrors']and len(report['cases'])==7
    expected={(1280,None)}|{(390,u)for u in stage.UIDS};assert {(r['width'],r['failedUid'])for r in report['cases']}==expected
    for row in report['cases']:
        assert row['completeGroupEvicted']and row['baseOnlyRestoredCompleteGroup']and not row['audit']['violations']
        assert {r['uid']:r['sha256']for r in row['sources']}==q['sourceSHA256ByUid']and all(r['active']for r in row['sources'])
        if row['failedUid']:assert row['failureKeptAllBasics']
    for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
    q={**q,'finalStageLifecycle':stage.ref(browser/'result.json')};resources=set(q['leaseResources'])|{'server:127.0.0.1:4177'};assert len(resources)==len(set(resources));return resources,q

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare-only',action='store_true');p.add_argument('--receipt');p.add_argument('--apply',action='store_true');a=p.parse_args();assert not(a.prepare_only and a.apply);resources,q=evidence()
    if a.prepare_only:
        assert not a.receipt;save(stage.BASE/(stage.P+'guarded-publisher-preflight-v1-20261031')/'summary.json',dict(uids=q['uids'],passed=True,resources=sorted(resources),stageReceipt=stage.ref(stage.DOC/'result.json'),publisher=stage.ref(Path(__file__)),publication=False));return
    assert a.receipt;lease=read(Path(a.receipt))
    @contextmanager
    def fence():
        with connect()as db:
            db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));live=reservations._current(db,lease);assert live and resources<=set(live['resources']);assert stage.ref(ROOT/'3d-viewer/city/data/manifest.json')==q['currentManifest'];yield
    with fence():pass
    pub=module('prosperous_exact_live_canonical_publisher',HERE.parent/'island-detail-integration/publish.py');pub.PUBLICATION_GUARD=fence;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/BATCH;sys.argv=['publish.py',str((stage.STAGE/'plan.json').relative_to(ROOT))]+(['--apply']if a.apply else[])
    with complete_boundary_validators():pub.main()

if __name__=='__main__':main()

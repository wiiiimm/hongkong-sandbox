"""Independent exact H234/75 identity review; preserve the failed boundary certificate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fung-yip-independent-permit-identity-review-v1-20261025'
SOURCES={'landsd/254815:0':'501cc0df37031950a05a7725d0b918c2b28e8daa5fc0e02f1b78c0b2e9723c42','landsd/79883:0':'f6034a6d28e0f7d82bc2094e9817ea253fe700695d3d228825ea794c5375b6d5'}
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    current=take('government-xl-fung-yip-after-inone-current-selection-v1-20261025','selection.json.gz')
    historical=take('government-xl-fung-yip-full-native-domain-runtime-v1-20261024','selection.json.gz');old={r['uid']:r for r in historical['rows']}
    assert {r['uid']:r['sourceSHA256']for r in current['rows']}==SOURCES
    identities={};forms={}
    for row in current['rows']:
        uid=row['uid'];f=forms[uid]=row['source']['building'];assert f==old[uid]['source']['building']
        path=ROOT/'3d-viewer'/row['source']['tile'];assert next(r for r in read(path)['buildings']if r['uid']==uid)==f;refs.append(path)
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset)
        x=identities[uid]=take('government-xl-fung-yip-after-inone-current-identity-v1-20261025',uid.split('/')[1]+'/identity.json')
        assert x['sourceSHA256']==SOURCES[uid] and x['originalOwnership']['sourceGraphVerified']
        assert x['originalOwnership']['originalRootName']==row['modelId'] and x['freshCurrentIdentity']['exactObjectAndCSUID']
        assert x['exactCurrentComponentRoute']['qualified'] and x['exactWholeCellCoverage']['covered']
        assert x['freshCurrentIdentity']['targetCoveredBySourceProjection']>=.95 and x['freshCurrentIdentity']['sourceExcessMaximumDistanceFromTargetM']<10
    tower=identities['landsd/254815:0'];pod=identities['landsd/79883:0'];assert tower['passed']and not tower['reasons']
    assert set(pod['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
    assert 1.15<pod['freshCurrentIdentity']['sourceExcessCoveredByUnrelatedFormsM2']<1.16
    permit=take('government-xl-fung-yip-after-inone-complete-permit-v1-20261025')
    assert permit['permits']==['H234/75'] and permit['allRequestedPermitRecordsReturned']and permit['completePermitStructures']==2
    assert set(permit['completePermitCSUIDs'])=={f['buildingCSUID']for f in forms.values()}
    primary=take('government-xl-fung-yip-after-inone-primary-records-v1-20261025','footprints.json');official={r['attributes']['BuildingCSUID']:r['attributes']for r in primary['features']}
    for f in forms.values():
        a=official[f['buildingCSUID']];assert a['Status']=='Active'and a['BuildingBlockType']==f['structureType']
        assert a['BaseHeight']==f['baseHeightHKPD']and a['TopHeight']==f['topHeightHKPD']
    adverse=take('government-xl-fung-yip-full-native-domain-exact-boundary-counterexample-v3-20261024')
    assert adverse['sourceSHA256']==SOURCES['landsd/79883:0'] and adverse['allFiniteSegmentsStrictlyOutsideExistingGuard']
    assert adverse['existingGuardM']==.0041 and adverse['diagnosticDistanceM']>.0049
    assert adverse['sourceFormSHA256']==pod['sourceFormSHA256']
    figures=[];views='government-xl-fung-yip-full-native-domain-podium-identity-views-v1-20261024';take(views)
    for name in ['whole-source-plan.png','whole-source-perspectives.png']:
        p=BASE/views/name;assert digest(p.read_bytes())==pins[views][str(p.relative_to(ROOT))];refs.append(p);figures.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),actuallyViewed=True))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==current['manifestSHA256'];refs.append(manifest)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),reviewer='ROOT',identityAccepted=True,identityProof=proof,identityProofByUid={u:proof for u in SOURCES},independentIdentityBasis='Complete exact H234/75 two-structure family, owned source graphs, exact current object/CSUID routes, whole GeoRef cells and inspected complete source architecture.',rawIdentityProofs=identities,rawOtherFormOverlapFailureRetained=True,failedBoundaryCertificateRetained=adverse,boundaryCertificateAccepted=False,genericIdentityPolicyChanges=False,figuresActuallyViewed=figures,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,visualRuntimeAcceptance=False,installationApproved=False,observations=[
      'Accept numeric identity only for these two unchanged Fung Yip sources. The current official H234/75 family consists exactly of their tower/podium structures. Both original graphs are owned by their exact prepared roots, uniquely routed current object/CSUIDs, and complete original GeoRef cells. Both cover over95percent of their own current targets and remain inside the existing10mextent gate.',
      'ROOT inspected the complete398face podium plan/perspectives. The original body, perimeter returns and lower rear strip correspond to the same building footprint; its maximum extension is2.4201m. Preserve raw1.15139265m2 unrelated projected overlap and the distinct neighbouring identities/permits. Source identity follows the independent exact official family/owned-root/whole-source evidence; do not reassign or suppress neighbouring actors.',
      'The prior proposed4.1mmboundary certificate remains FALSE at its exact4.927408mm counterexample. This review neither retries nor approves it and changes no numerical boundary, overlap or source geometry policy. It records a separate bounded source-identity interpretation for two exact hashes, not a generic overlap waiver.',
      'Physical original/retained-neighbour interfaces, support, drawn-ground coverage/clearance, unobstructed fresh retained/mobile views and guarded publication/readback remain independent. No installation credit or engineering/zero-interpenetration exemption is granted.'
    ])
    save(out/'ROOT-IDENTITY-REVIEW.json',result)
    module('fung_yip_independent_identity',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'independent-official-permit-owned-original-fung-yip-identity-review',refs,{k:v for k,v in result.items()if k!='rawIdentityProofs'})
if __name__=='__main__':main()

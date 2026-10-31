"""Bounded identity review of five immutable originals at Ho Man Tin Station."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-inone-five-bounded-identity-review-v1-20261025'
RUNTIME='government-xl-inone-five-required-earth-runtime-v6-20261025'
IDENTITY='government-xl-inone-five-current-identity-v1-20261025'
POD='landsd/277890:0'
def main():
    out=BASE/BATCH;assert not out.exists()
    pins,refs={},[Path(__file__)]
    def take(batch,name='summary.json'):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(RUNTIME,'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==5
    raw={};forms={}
    expected={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
    for row in selection['rows']:
        u=row['uid'];f=forms[u]=row['source']['building'];asset=ROOT/row['candidate']['path']
        assert digest(asset.read_bytes())==sources[u];refs.append(asset)
        p=ROOT/'3d-viewer'/row['source']['tile'];assert next(x for x in read(p)['buildings']if x['uid']==u)==f;refs.append(p)
        x=raw[u]=take(IDENTITY,u.split('/')[1]+'/identity.json')
        assert x['sourceSHA256']==sources[u] and x['originalOwnership']['sourceGraphVerified']
        assert x['freshCurrentIdentity']['exactObjectAndCSUID'] and x['exactCurrentComponentRoute']['qualified']
        assert x['exactWholeCellCoverage']['covered']
        assert set(x['reasons'])==(expected if u==POD else set())
        if u!=POD:assert x['passed']
    assert sources[POD]=='31e137e5024c6caf78d0c0b2b258d8107d9868c6bab65cc0e7876d57f60a5fbb'
    assert raw[POD]['originalOwnership']['originalRootName']=='B368711898502063C0'
    permit=take('government-xl-inone-five-complete-permit-families-v1-20261025')
    assert permit['allRequestedPermitRecordsReturned']
    assert set(permit['completePermitCSUIDs'])=={f['buildingCSUID']for f in forms.values()}
    assert set(permit['permits'])=={'PR11/2024/OP','PR1/2025/OP'}
    x=raw[POD]['freshCurrentIdentity'];assert x['targetCoveredBySourceProjection']>.998 and 32.8<x['sourceExcessMaximumDistanceFromTargetM']<32.82
    context='government-xl-after-royal-277890-original-context-v1-20261024';take(context)
    images=[]
    for name in ['whole-source-plan.png','whole-source-perspectives.png']:
        p=BASE/context/name;assert digest(p.read_bytes())==pins[context][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),actuallyViewed=True))
    local=HERE/'local/government-xl-inone-primary-plans-v1-20261025';provenance=[]
    for name in ['phaseII-pdmc.pdf','mtr-in-one.jpeg']:
        p=local/name;request=read(local/(name+'.request.json'));assert request['sha256']==digest(p.read_bytes());refs.extend([p,local/(name+'.request.json')]);provenance.append(request)
    for page in [154,155,156]:
        p=local/('plan-page-%d.png'%page);refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),actuallyViewed=True,pdfPage=page))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),reviewer='ROOT',identityAccepted=True,identityProof=proof,identityProofByUid={u:proof for u in sources},rawIdentityProofs=raw,rawExtentAndOtherFormFailuresRetained=True,genericIdentityPolicyChanges=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,figuresActuallyViewed=images,primaryProvenance=provenance,observations=[
      'Accept the exact five numeric government identities as the original podium/four-tower assembly. All current object/CSUID/component routes, owned original roots and whole GeoRef cells are verified. The four towers pass the generic identity checks. The two complete permit families associate these exact structures; they do not establish one shared legal ownership or approve adjacent structures.',
      'The podium covers99.8234percent of its own recorded target. Its original authored platforms/access arms extend32.8103m beyond that narrower GIS outline; the1447.1312m2 excess and843.5645m2 other-form overlap remain raw failures. ROOT inspected the whole-source plan/perspectives and MTR operator photograph showing the four towers above an articulated common podium. The official site plans show station/SiteA/SiteB boundaries and retaining/platform context at32.20mPD. These corroborate site identity and multi-level architecture; they are not precise georeferencing or permission to suppress neighbouring forms.',
      'Identity approval is confined to these five unchanged hashes/current forms and the owned original root. Keep every source face, fixed1x placement, generic extent/overlap policy and all neighbouring actors. No source clipping, footprint buffer, target reassignment, blanket station exemption or photorealistic material claim.',
      'Physical contact roles, support paths, terrain clearance, actual browser/export acceptance and guarded publication are separate. Adjacent platform/club-house interfaces still require original-source context; this identity review grants no installation credit.'
    ])
    save(out/'ROOT-IDENTITY-REVIEW.json',result)
    module('inone_identity_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-five-original-inone-identity-review',refs,{k:v for k,v in result.items()if k!='rawIdentityProofs'})
if __name__=='__main__':main()

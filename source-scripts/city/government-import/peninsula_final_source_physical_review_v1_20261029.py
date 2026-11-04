"""Compose ROOT's reviewed exact-original pair acceptance; publication remains separate.

Run only after ROOT has actually inspected all eight current private exports.
"""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from peninsula_private_group_roof_contract_v1_20261029 import OWNER,TOWER,ROOF,SOURCES,form_sha
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-final-source-physical-review-v1-20261029';BROWSER='government-xl-peninsula-pair-group-roof-private-browser-v4-20261029'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(n,p):
        if n not in pins:
            receipt,pins[n]=authenticate(BASE/n);jobs[n]=receipt['jobId'];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def summary(n):return take(n,BASE/n/'summary.json')
    identity=summary('government-xl-peninsula-exact-source-association-review-v1-20261029');assert identity['exactSourceAssociationAccepted']and identity['sourceSHA256ByUid']==SOURCES
    role=summary('government-xl-peninsula-authored-assembly-role-review-v1-20261029');assert role['authoredAssemblyRoleInterpretationAccepted']and role['sourceSHA256ByUid']==SOURCES and not role['strictStructuralSupportApproved']
    corrected=summary('government-xl-peninsula-three-buried-facet-context-v1-20261029');assert corrected['sourceSHA256']==SOURCES[OWNER]
    assert all(len(r['buriedFacets'])==3 and all(f['signedNormalYRatio']==0 for f in r['buriedFacets'])for r in corrected['rows'])
    lifecycle=summary('government-xl-peninsula-group-roof-lifecycle-v1-20261029');assert lifecycle['completeAtomicPairAndRoofLifecycleVerified']and lifecycle['passed']and lifecycle['sourceSHA256ByUid']==SOURCES
    roof=summary('government-xl-peninsula-private-group-roof-review-v1-20261029');assert roof['privateExperimentApproved']and roof['sourceSHA256ByUid']==SOURCES
    scope=summary('government-xl-peninsula-pair-current-v1-20261029-model-scope');assert not any(r['nearbyNativeActors']for r in scope['rows'])
    forms={r['building']['uid']:r['building']for r in take('government-xl-peninsula-pair-current-v1-20261029-model-scope',BASE/'government-xl-peninsula-pair-current-v1-20261029-model-scope/270876:0-forms.json.gz')};assert set(forms)=={OWNER,TOWER,ROOF};assert form_sha(forms[ROOF])==roof['roofFormSHA256']
    rawname='government-xl-peninsula-pair-current-v1-20261029-identity';raw=[]
    for uid in [OWNER,TOWER]:
        record=take(rawname,BASE/rawname/(uid.split('/')[1])/'identity.json');f=record['freshCurrentIdentity'];assert f['exactObjectAndCSUID']and f['targetCoveredBySourceProjection']>=.95 and f['sourceExcessMaximumDistanceFromTargetM']<=10
        unrelated=[r for r in f['intersectingForms']if not r['sameParent']and not r['sharedOsmReference']and r['uid']!=uid];assert all(r['uid']==ROOF for r in unrelated)
        assert record['sourceSHA256']==SOURCES[uid]and record['originalOwnership']['sourceGraphVerified'];raw.append(dict(uid=uid,reasons=record['reasons'],freshCurrentIdentity=f))
    foreign=summary('government-xl-peninsula-pair-current-foreign-contacts-v1-20261029');assert {(r['uid'],r['foreignUid'])for r in foreign['rows']}=={(OWNER,ROOF),(OWNER,TOWER),(TOWER,OWNER)}
    receipt,pins[BROWSER]=authenticate(BASE/BROWSER);jobs[BROWSER]=receipt['jobId'];refs.append(BASE/BROWSER/'result.json');assert receipt['previewOnly']and not receipt['installationApproved']and receipt['independentFailureTestsDeferredToAtomicLifecycle']
    images=[]
    for width in [1280,390]:
        report=take(BROWSER,BASE/BROWSER/str(width)/'staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if 'time'in v];assert len(views)==4
        for v in views:
            uid=v['uid'];assert uid==v['pick']==v['collision']and v['sourceSHA256']==SOURCES[uid]and v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']
            p=BASE/BROWSER/str(width)/v['file'];assert digest(p.read_bytes())==pins[BROWSER][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    cat=take(BROWSER,HERE/'local'/BROWSER/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==SOURCES
    for m in cat['models']:
        assert m['activationGroup']==sorted(SOURCES)and m['proceduralWindows']is False and all(m[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
        path=HERE/'local'/BROWSER/m['asset'];assert digest(path.read_bytes())==m['sha256'];refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==identity['currentManifest']['sha256']==scope['currentManifestSHA256'];refs.append(manifest)
    resources=['building:'+OWNER,'building:'+TOWER,'source-form:'+ROOF,'building:'+ROOF,'terrain:city/data/terrain.json','server:127.0.0.1:4177']
    decision=dict(uids=[OWNER,TOWER],sourceSHA256ByUid=SOURCES,currentManifest=identity['currentManifest'],reviewer='Codex ROOT',identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,rawStrictSupportPassed=False,strictStructuralSupportApproved=False,authoredOriginalAssemblyJointAccepted=True,supportByUid={TOWER:OWNER},activationGroup=sorted(SOURCES),retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],retainedNativeUids=[],leaseResources=resources,conditionalOsmRoofReplacement=dict(sourceUid=OWNER,basicUid=ROOF,sourceSHA256=SOURCES[OWNER],sourceFormSHA256=form_sha(forms[OWNER]),basicFormSHA256=form_sha(forms[ROOF]),onlyWhileExactOwnerActive=True,approved=True),evidence=jobs,imagesActuallyViewed=images,rawIdentityWarningsVerbatim=raw,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,installationApproved=False,publication=False,
        interpretation='ROOT reviewed all eight fresh current-code desktop/mobile day/night exports. The unchanged lower hotel, upper tower, twin rooftop pads, courtyard and source entrance canopy align as one original government assembly. The old one-storey OSM roof box duplicates the detailed original canopy and is replaced only while the exact original owner is active; its complete source form is checked at runtime. Both originals activate/retire atomically, with all3desktop/mobile per-peer-failure/Base/Auto/eviction cases independently passed. All raw164tower rim warnings remain preserved; original source paths and the28near-vertical lower-facade witnesses establish an authored joint, not strict structural footing certification. Three buried hotel facets are exactly vertical lower boundary walls (5580/5931/5932), correcting the earlier unproven downward-closure label; the established zero-upward-burial/area policy and all189whole-source clear-cap paths remain passed. The two stable primary IDs and whole1m cells establish source association, with the exact named native02/current2D Tower difference documented rather than coercing the generic type checker. The only foreign form is the exact reviewed roof part; co-import peer contacts are source-authored, with no source-pair area intersections and no overlapping installed-native candidates. This accepts this exact source revision and current scene only. Global retained-support checks, lease/preflight/atomic rollback, final live browser and installed-ledger readback remain mandatory; this is not publication.')
    save(out/'ROOT-PHYSICAL-REVIEW.json',decision);save(out/'ROOT-SOURCE-REVIEW.json',decision);save(out/'summary.json',decision);module('peninsula_final_physical_source_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-Peninsula-pair-final-current-source-physical-and-ROOT-visual-review',refs,decision)
if __name__=='__main__':main()

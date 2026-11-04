"""Bounded exact-source identity and interface interpretation; no visual/publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
PREFIX='government-xl-podium323546-after-beverly-d-'
SOURCES={'landsd/323546:0':'f0805e04e4bee49024520e79055c05991bffe6fdf268ffad5b1a8ce1bc199f03','landsd/210501:0':'028dcca0f84062f4502ff9bcdac20ee628158f7f35d5a61ff8ef467a12e27830','landsd/210742:0':'a10fd697713657c483840a1705c21b0f6cf3ffb43b06c82005665500eb06a2d6'}


def main():
    base=ROOT/'docs/astra-city/government-import';batch=PREFIX+'three-original-identity-role-review-v1-20261026';out=base/batch
    assert not out.exists();refs=[Path(__file__)];pins={}
    def take(label,file='summary.json'):
        name=PREFIX+label+'-20261026'
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        if file=='result.json':return authenticate(base/name)[0]
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take('three-original-hierarchical-runtime-v1','selection.json.gz')
    assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    raw=take('three-original-identity-v1');assert {r['uid']for r in raw['rows']}==set(SOURCES)
    identities=[]
    for row in raw['rows']:
        uid=row['uid'];p=take('three-original-identity-v1',uid.split('/')[1]+'/identity.json')
        assert p['sourceSHA256']==SOURCES[uid] and p['originalOwnership']['sourceGraphVerified']
        assert p['exactCurrentComponentRoute']['qualified'] and p['exactWholeCellCoverage']['covered']
        assert p['freshCurrentIdentity']['exactObjectAndCSUID']
        if uid=='landsd/323546:0':
            assert row['passed']is False and row['reasons']==['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
            assert p['originalOwnership']['originalRootName']=='B361601749602063C0'
            assert p['freshCurrentIdentity']['targetCoveredBySourceProjection']>.99
            assert p['freshCurrentIdentity']['sourceExcessCoveredByUnrelatedFormsM2']==0
        else:assert row['passed'] and row['reasons']==[]
        identities.append(dict(uid=uid,sourceSHA256=SOURCES[uid],rawPassed=row['passed'],rawReasons=row['reasons'],originalRoot=p['originalOwnership']['originalRootName'],rawFreshCurrentSpatialEvidence=p['freshCurrentIdentity']))
    primary=take('three-original-primary-v1','result.json');assert primary['footprints']==3 and primary['missingRequestedCSUIDs']==[] and primary['relations']==0
    roles=take('three-original-contact-roles-v1');assert roles['sourceSHA256ByUid']==SOURCES and roles['allRawContactsClassified']
    for row in roles['rows']:
        expected=31 if row['uid']=='landsd/210501:0' and row['peerUid']=='landsd/323546:0'else 72 if row['uid']=='landsd/210742:0' and row['peerUid']=='landsd/323546:0'else 0
        assert row['contactCount']==expected
        if expected:assert row['roles']=={'transverse-surface-crossing':expected}
        else:assert row['strictBoundsSeparated']
    foreign=take('three-current-foreign-contacts-v1');assert len(foreign['rows'])==8
    external=[r for r in foreign['rows']if r['foreignUid']not in SOURCES]
    assert len(external)==4 and all(m['positiveContactPairs']==0 and m['allFiniteContactPairs']==0 for r in external for m in r['modes'])
    scope=take('three-current-neighbours-v1');assert all(r['currentNativeActorsChecked']==6959 and not r['nearbyNativeActors']for r in scope['rows'])
    for label in ['hierarchical-foundation-context-v2','three-210501-foundation-context-v1','three-210742-foundation-context-v1']:
        assert take(label)['establishedFoundationPolicyPassed']
    for label in ['three-podium-cap-paths-v1','three-210501-cap-paths-v1']:assert take(label)['allFourCompleteGroundClearCapPaths']
    degenerate=take('three-210742-exact-degenerate-partition-v1');assert degenerate['rawAllFourCompleteGroundClearCapPaths']is False
    assert all(r['negativeNonWallDimensions']=={'311':1,'312':1}and r['renderingNegativeFacesWithExistingCapPaths']==15 and r['noDegenerateCapPathBridge']for r in degenerate['rows'])
    coverage=take('exact-remaining-coverage-v2');rebind=take('three-podium-identical-numerics-v1')
    assert coverage['completeProjectionCoverageProved'] and coverage['remainingExactlyUncoveredFaces']==[]
    assert coverage['sourceSHA256']==SOURCES['landsd/323546:0'] and coverage['wholeOriginalFacesAccounted']==10612
    assert rebind['allFourWorldSourceAttributesIdentical'] and rebind['allActualLiteralSourceAndDrawnGroundInputsIdentical']
    # These exact images were opened by ROOT in this and the prior continuation.
    viewed=[]
    for label,names in [('three-original-contact-views-v1',['210501:0--323546:0.png','210742:0--323546:0.png']),('three-original-official-basemap-v1',['official-map-comparison.png']),('three-original-source-views-v1',['complete-original-assembly.png','base-only-diagnostic.png'])]:
        for name in names:
            take(label,'summary.json') if (base/(PREFIX+label+'-20261026')/'summary.json').exists() else take(label,'result.json')
            folder=PREFIX+label+'-20261026';path=base/folder/name
            assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);viewed.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    review=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),identityAccepted=True,identityReviewScope='Faithful import of these three exact anonymous official components; no named landmark or property identity assertion.',identityRows=identities,identityInterpretation='The uniquely routed original B361601749602063C0 and its complete GeoRef cell match the current podium CSUID, cover99.1745percent of its footprint and occupy the same triangular deck/ramp extent in the inspected official basemap. The complete source owns the southern ramp/edge extensions causing14.658229m maximum excess; no unrelated form is covered by this excess. Preserve both raw extent failures. Both independently identified adjoining originals pass strict identity. Fresh provider OBJECTIDs differ from immutable viewer IDs; matching CSUID/BuildingID does not justify changing IDs or inferring common ownership. Basemap dates are unconfirmed and its transformation is metre-scale context, not centimetre placement proof.',originalInterfaceInterpretation='The inspected source close views locate all31/72 transverse surface crossings on the cuboid side-façade/deck-wall interfaces. Retain these original crossings as a faithful source-port interface; do not call them collision-free, coplanar or structural support. Current BASIC fallback interfaces are also measured and retained, including8/53 companion-to-BASIC-podium contacts and26/30 original-podium-to-BASIC-companion contacts. The three external ordinary forms have no finite contacts in any measured source stream. No support or availability dependency is inferred from contact alone.',sourceSpecificPhysicalInterpretationAccepted=True,physicalReviewScope='Bounded original wall/deck source-role interpretation and existing foundation policy, for private review only. Not whole-site structural or collision certification.',rawWarningsPreserved=dict(podiumWholeBuriedWallFaces=7,podiumBuriedAreaFraction=0.0006444657767,upwardBuriedFaces=0,rawCompanion210742CapContractPassed=False,nonrenderingFaces=[311,312],originalTransverseContactsPerMode=103),completeNeighbourInterpretationAccepted=True,retainedCurrentBasicSupportUids=[],supportByUid={},inspectedSourceImages=viewed,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,visualAcceptance=False,installationApproved=False,publication=False,qualification='Bounded interpretation for exact unchanged original source imports. Actual desktop/mobile day/night source and fallback views, hierarchical replacement non-effect admission, canonical publisher guards, production browser/readback and installed ledger remain mandatory. Raw failures/contacts/negative flags remain unmodified. No photographic completeness, engineering safety or common ownership is claimed.')
    save(out/'ROOT-IDENTITY-AND-ROLE-REVIEW.json',review)
    module('podium_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-anonymous-original-source-identity-wall-interface-review',refs,review)
    print(dict(identityAccepted=True,privateRoleReview=True,visualAcceptance=False,installed=0),flush=True)

if __name__=='__main__':main()

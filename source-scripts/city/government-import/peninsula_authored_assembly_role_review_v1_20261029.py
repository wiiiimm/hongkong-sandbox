"""Review exact original facade/roof joint roles; preserve raw numerical failures."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-authored-assembly-role-review-v1-20261029'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};jobs={}
    def take(n,p):
        if n not in pins:
            receipt,pins[n]=authenticate(BASE/n);jobs[n]=receipt['jobId'];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def summary(n):return take(n,BASE/n/'summary.json')
    association=summary('government-xl-peninsula-exact-source-association-review-v1-20261029');sources=association['sourceSHA256ByUid'];assert association['exactSourceAssociationAccepted']
    physical=summary('government-xl-peninsula-pair-four-world-support-v1-20261029');assert physical['sourceSHA256ByUid']==sources and not physical['allFourModesPassed']
    assert physical['supportUid']=='landsd/270876:0'and physical['supportedUid']=='landsd/266543:0'
    for row in physical['rows']:
        assert row['support']['samples']==305 and row['support']['strictContacts']==141 and len(row['support']['unresolved'])==164
        f=row['compoundFoundation'];assert f['triangles']==f['completeTerrainTriangles']==2872 and f['fullyBuriedTriangles']==f['fullyBuriedUpwardTriangles']==0 and f['minimumGapM']>=-.5
    paths=summary('government-xl-peninsula-office-finite-self-attachment-v2-20261029');assert paths['sourceSHA256ByUid']==sources
    assert all(r['finiteAttachmentPaths']==r['witnesses']==164 and r['disconnected']==0 and r['pathsWithinEndpointHeight']==136 for r in paths['rows'])
    views=summary('government-xl-peninsula-office-28-junction-views-v1-20261029');assert views['allResidualsShownExactlyOnce']and views['completeResidualWitnesses']==28
    normals=[f['signedNormalYRatio']for w in views['witnesses']for f in w['incidentFaceContext']];assert max(abs(v)for v in normals)<.006
    assert all(48.39924<=w['witness']['position'][1]<=48.39926 and w['riseAboveEndpointsM']<=.215951 for w in views['witnesses'])
    caps=summary('government-xl-peninsula270876-complete-ground-cap-paths-v1-20261029');assert caps['allFourCompleteGroundClearCapPaths']and caps['sourceSHA256']==sources['landsd/270876:0']
    foundation=summary('government-xl-peninsula-pair-current-v1-20261029-foundation-270876-0');assert foundation['establishedFoundationPolicyPassed']
    for row in foundation['rows']:assert row['triangles']==row['completeTerrainTriangles']==15114 and row['fullyBuriedTriangles']==3 and row['fullyBuriedUpwardTriangles']==0 and row['fullyBuriedAreaFraction']<=.001
    contacts=summary('government-xl-peninsula-pair-finite-contacts-v1-20261029');assert contacts['sourceSHA256ByUid']==sources and all(r['allPairsExamined']and r['sourceFacesOmitted']==0 and r['areaContactPairs']==0 for r in contacts['rows'])
    scope=summary('government-xl-peninsula-pair-current-v1-20261029-model-scope');assert not any(r['nearbyNativeActors']for r in scope['rows'])
    roof=summary('government-xl-peninsula-private-group-roof-review-v1-20261029');assert roof['sourceSHA256ByUid']==sources and roof['privateExperimentApproved']and not roof['physicalAcceptance']
    lifecycle=summary('government-xl-peninsula-group-roof-lifecycle-v1-20261029');assert lifecycle['passed']and lifecycle['completeAtomicPairAndRoofLifecycleVerified']and lifecycle['sourceSHA256ByUid']==sources
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==association['currentManifest']['sha256']==scope['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=list(sources),sourceSHA256ByUid=sources,currentManifest=association['currentManifest'],reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=False,authoredAssemblyRoleInterpretationAccepted=True,strictStructuralSupportApproved=False,rawStrictSupportPassed=False,rawWarningsPreserved=True,sourceSpecificWholePhysicalAcceptance=False,identityAccepted=False,visualAcceptance=False,installationApproved=False,publication=False,evidence=jobs,
        roleDecision='The upper original begins at48.399m because it is the upper portion of the same authored hotel/tower assembly, not an independent ground building. Complete unchanged source facets meet the lower original at positive finite edge contacts in all4coordinate streams. All164 raw low-rim warnings have finite original self-join paths to that peer. The28 endpoint-ceiling failures are lower facade skirts at the same source cut plane; every incident facet is near vertical, with maximum absolute normalY below0.006, and the longest excess is0.215950m. ROOT inspected all28 labelled two-angle witnesses, full/base-cut original assembly and exact canopy correspondence. They are accepted as source-authored facade/junction context for this exact co-rendered pair, not promoted to strict footing samples or structural roots. Do not add a per-facade engineering monotonic-path requirement. Both originals must activate/fail/retire together.',
        unchangedPhysicalObligations='Lower original passes the existing complete-ground/zero-upward-burial/buried-area policy in every representation; three downward basal closures and all189 low wall facets remain recorded. All189 have complete strict-clear cap paths. Upper source on the complete lower-source/current-ground compound has zero buried/upward-buried facets and minimum gap above-0.5m; its43m ground-only clearance is not an independent grounding approval. Original-pair contacts have no area intersections. Scope contains no overlapping installed-native candidate. Only the exactly reviewed OSM entrance roof may be conditionally replaced, with all raw42source/roof contacts retained. Complete current desktop/mobile visual/picking/collision, final identity/foreign-role composition and guarded publisher/global-support/live readback remain mandatory.',
        nextStep='Complete current-code full private exports and ROOT visual review, then compose final exact-source physical/identity acceptance and qualified publication. Reuse this bounded original-role decision without rerunning the finished engineering diagnostics. This alone is not installation approval.')
    save(out/'ROOT-SOURCE-ROLE-REVIEW.json',result);save(out/'summary.json',result);module('peninsula_authored_role_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-original-Peninsula-facade-junction-and-coavailability-role-review',refs,result)
if __name__=='__main__':main()

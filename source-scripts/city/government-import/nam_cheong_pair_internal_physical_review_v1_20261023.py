"""Bounded ROOT interpretation of the exact pair's internal source interfaces.

Foreign bridge/roof contacts and complete source identity remain unapproved.
"""
from fractions import Fraction
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-nam-cheong-pair-internal-physical-review-v1-20261023'
NAMES=dict(capture='government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime',membership='government-xl-nam-cheong-primary-pair-membership-review-v1-20261023',support='government-xl-nam-cheong-fu-yun-four-world-support-v1-20261023',attribution='government-xl-nam-cheong-fu-yun-compound-envelope-attribution-v1-20261023',contacts='government-xl-nam-cheong-pair-four-world-contacts-v1-20261023',representation='government-xl-nam-cheong-contact-representation-readback-v1-20261023',views='government-xl-nam-cheong-pair-body-contact-views-v1-20261023')


def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH
    assert not doc.exists()
    refs,pins=[Path(__file__)],{}
    for name in NAMES.values():
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(key,filename):
        name=NAMES[key];path=base/name/filename
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take('capture','selection.json.gz');sources={r['uid']:r['sourceSHA256'] for r in selection['rows']}
    membership=take('membership','summary.json');assert membership['samePropertyMembershipAccepted'] and membership['sourceSHA256ByUid']==sources
    support=take('support','summary.json');assert support['sourceSHA256ByUid']==sources and len(support['rows'])==4
    for r in support['rows']:
        assert r['support']['passed'] and r['support']['samples']==r['support']['strictContacts']==526 and not r['support']['unresolved']
        assert r['compoundFoundation']['fullyBuriedTriangles']==r['compoundFoundation']['fullyBuriedUpwardTriangles']==0
        assert r['compoundFoundation']['minimumGapM']<-.5 and not r['passed']
    attribution=take('attribution','summary.json');assert attribution['sourceSHA256ByUid']==sources and len(attribution['rows'])==4
    for r in attribution['rows']:
        assert r['unchangedSavedFoundationReproduced'] and r['negativeSamples']==18
        assert r['highestProviderKinds']=={'support-original':18}
        assert r['conservativeActualTerrainWholeSourceYGapM']>9
        assert {p['face'] for p in r['providerFaceCounts']}=={8452,9732,9740,9797}
        assert r['minimumWitness']['highestProviders'][0]['face']==9732
        assert r['minimumWitness']['highestProviders'][0]['normalYRatio']==1
    contacts=take('contacts','summary.json');assert contacts['sourceSHA256ByUid']==sources and contacts['allFourRepresentationsAccounted']
    for row in contacts['rows']:
        expected=111 if row['mode']=='literal' else 22
        assert row['allPairsExamined'] and row['roles']['transverse-surface-crossing']==expected
    representation=take('representation','summary.json');assert representation['sourceSHA256ByUid']==sources
    assert representation['newUnmatchedContactPairs']==0 and representation['originalCrossingsNeedingPhysicalReview']==22 and representation['changedPointOrEdgeClassifications']==89
    views=take('views','summary.json');assert views['sourceSHA256ByUid']==sources
    pairs=views['rows'];assert len(pairs)==22 and {r['sourceFaceA'] for r in pairs}=={8440,8538,10131}
    maximum=max(Fraction(r['minimumBidirectionalMinorPlaneExtentSquaredM2']) for r in pairs)
    # This binds the measured descriptor, not a new generic acceptance limit.
    assert maximum<Fraction(19,1000)**2
    images=[]
    assert len(views['views'])==4
    for image in views['views']:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==pins[NAMES['views']][str(path.relative_to(ROOT))];refs.append(path)
        images.append(dict(path=image['path'],sha256=image['sha256']))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==attribution['currentManifestSHA256']==contacts['currentManifestSHA256']==views['currentManifestSHA256'];refs.append(manifest)
    review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,currentManifestSHA256=selection['manifestSHA256'],reviewer='Codex ROOT',imagesActuallyViewed=images,
                pairInternalSourceVisualAssemblyInterpretationAccepted=True,pairStrictSupportWitnessesAccepted=True,sourceEvidenceInterpretationUsedAI=True,
                interpretation='These exact original Nam Cheong Place/Fu Yun meshes form a primary-owner-documented ancillary assembly. All526strict low-rim contacts pass in all four coordinate representations. Eighteen compound-envelope negative samples per representation are caused by four Nam source caps, not actual terrain; the global-4.515m value measures a low FuYun detail beneath Nam cap9732 at23.304mHKPD. No complete FuYun triangle or upward triangle is buried; the entire FuYun source clears actual captured terrain by a conservative9.104m. The22original pair crossings are localised at two shallow sloping cap/base-wall joins and one small lower detail/vertical-wall interface. ROOT inspected the four source-context exports and accepts these unchanged contacts as internal visual assembly joins, not a displaced independent building or source corruption. Literal89extra crossing classifications arise at the same original point/edge pairs under exactly bounded coordinate arithmetic; all111rawliteral contacts remain retained.',
                exactMaximumObservedMinorPlaneExtentSquaredM2=str(maximum),strictSupportContactsPerRepresentation=526,
                rawCompoundEnvelopePassed=False,rawCompoundMinimumGapM=-4.5149993896484375,rawOriginalTransverseCrossings=22,rawLiteralTransverseCrossings=111,
                rawCanonicalFailuresPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,
                limits=['Named internal assembly interpretation only; no generic support, collision, burial, coverage or extent threshold changes.', 'Every original source face, degenerate primitive and raw contact retained. No structural engineering or closed-solid certificate.', 'Nam Cheong long source extensions/fullidentity,72VWalk and40FuCheongforeign crossings remain unapproved.', 'Onewallrole10ee6b5d56b702a551ae4906c17b54116078934c4acc91307021912ab0920213 remains a separate bounded review; no wholeNam clearance or root exemption.', 'Full source physical integration/current neighbours/staged andlive desktop/mobile/picking/collision/failure-retry/guarded publication remain mandatory.'],
                completePhysicalAccepted=False,sourceIdentityAccepted=False,publicationApproved=False,installationApproved=False)
    save(doc/'ROOT-INTERNAL-PAIR-REVIEW.json',review)
    module('nam_pair_internal_physical_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-pair-internal-source-visual-assembly-interpretation',refs,review)


if __name__=='__main__':main()

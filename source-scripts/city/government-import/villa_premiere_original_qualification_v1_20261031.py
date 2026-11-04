"""Compose bounded unchanged-original Villa Premiere review; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-villa-premiere89917-';BATCH=P+'original-qualification-v1-20261031'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(batch,name='summary.json'):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def part(suffix,name='summary.json'):return take(P+suffix,name)
    runtime=P+'five-ramp-current-runtime-v1-20261030';selection=take(runtime,'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==5
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    proofs={};identities=[]
    for row in selection['rows']:
        uid=row['uid'];asset=ROOT/row['candidate']['path'];assert ref(asset)['sha256']==sources[uid];refs.append(asset)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert ref(tile)['sha256']==row['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==row['source']['building'];refs.append(tile)
        identity=part('five-ramp-identity-v1-20261031',uid.split('/')[1]+'/identity.json');assert identity['sourceSHA256']==sources[uid];identities.append(identity)
        route=identity['exactCurrentComponentRoute'];assert route['qualified']and not route['reasons'];official=route['official'];b=row['source']['building'];assert official['objectId']==b['objectId']and official['buildingCSUID']==b['buildingCSUID']
        if uid!='landsd/89917:0':assert identity['passed']and not identity['reasons'];proofs[uid]=identity['proof']
        else:
            assert set(identity['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
            owned=identity['originalOwnership'];assert owned['sourceGraphVerified']and owned['originalRootName']==row['candidate']['entry']['modelId']=='B216233340102062G0'
            intersects=owned['fullProjection']['intersectingForms'];assert {x['uid']for x in intersects}==set(sources)|{'landsd/325786:0'}
            assert all(x['sharedOsmReference']for x in intersects if x['uid']in sources)
            proofs[uid]=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True,basis='Exact official ObjectID/CSUID and unique native named G0 root/GeoRef, full original graph and face accounting. Shared podium projection includes the four exact co-import tower components with shared source OSM references. The only unrelated metadata-ring overlap is325786; every actual production canopy triangle is projection-disjoint and has zero finite source contacts in all4worlds. Original source extent is retained, without asserting cadastral ownership or assigning extra geometry to a tower.')
    support=part('ramp-support-checkpoint-v1-20261031');assert support['exactStrictRootWitnessesReusable']and support['allFourPodiumCapProofsPass']and support['unrelatedPositiveSourceContacts']==0
    for uid in sources:
        if uid=='landsd/89917:0':continue
        paths=part(uid.split('/')[1].replace(':','-')+'-strict-root-paths-v1-20261030')
        for row in paths['rows']:
            proof=part(uid.split('/')[1].replace(':','-')+'-strict-root-paths-v1-20261030',row['mode']+'.json.gz')
            assert all(x['passesExistingEndpointHeight']and x['maximumResidualM']<=.001 and x['riseAboveEndpointsM']==0 and x['terminal']['kind']=='canonical-strict-vertical-support-anchor'for x in proof['rows'])
    cap=part('five-ramp-podium-caps-v1-20261030');assert cap['allFourCompleteGroundClearCapPaths']and all(not r['completeGroundClearancePartition']['negativeNonWallFaces']for r in cap['rows'])
    coverage=part('five-ramp-continuous-v1-20261031');assert len(coverage['rows'])==5
    for row in coverage['rows']:
        assert row['sourceSHA256']==sources[row['uid']]and not row['otherAffectedFaces']
        assert row['wholeSourceUncoveredFaces']==(2 if row['uid']=='landsd/89917:0'else 0)
    numerical=part('numerical-ground-context-v1-20261031');assert numerical['allFourGridFallbackClear']and numerical['declaredCoveragePolicyReproduced']and numerical['nativeGapsRemainUnfilled']
    pairs=part('five-ramp-pairs-v1-20261031');assert pairs['sourceSHA256ByUid']==sources and pairs['completeUnorderedPairs']==10 and len(pairs['rows'])==40
    for row in pairs['rows']:
        assert set(row.get('contactDimensions',{}))<={'0','1'}
        if row.get('positiveSurfaceContacts',0):assert 'landsd/89917:0'in[row['uid'],row['peerUid']]
    foreign=part('five-ramp-foreign-contacts-v1-20261030');assert len(foreign['rows'])==23
    for row in foreign['rows']:
        if row['foreignUid']not in sources:
            assert all(m['positiveContactPairs']==0 and m['projectedOverlapAreaM2']==0 for m in row['modes']if m['mode']!='before-basic')
    scope=part('ramp-return-scope-v1-20261030','scope.json');forms=part('ramp-return-scope-v1-20261030','form-obligations.json.gz');assert len(forms)==47 and scope['currentNativeActors']==7030 and not scope['touchingNativeUids']and scope['positiveAreaTerrainOverlaps']==0
    ground=part('ramp-return-forms-v1-20261030');assert {r['uid']for r in ground['flagged']}==set(sources)-{'landsd/89917:0'}|{'landsd/325786:0'}
    browser=P+'five-ramp-canopy-private-preview-v1-20261031';part('five-ramp-canopy-private-preview-v1-20261031')
    images=[]
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        for uid in sources:
            for hour in ['1500','2200']:
                name=str(width)+'/staged-'+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+hour+'-canvas.png'
                path=BASE/browser/name;assert digest(path.read_bytes())==pins[browser][str(path.relative_to(ROOT))];refs.append(path);images.append(ref(path))
    life=P+'five-atomic-canopy-lifecycle-v2-20261031';atomic=take(life);assert atomic['browserPassed']and atomic['cases']==atomic['expectedCases']==6 and atomic['collisionProbes']==8400
    collision=take(life,'collision.json');assert collision['unchangedRegionalForms']==46 and collision['allRoofPartsExactlyRetained']and collision['allPostFootprintsAndTopsExactlyRetained']
    lifecycle=take(life,'browser/report.json');assert lifecycle['passed']and not lifecycle['pageErrors']
    for case in lifecycle['cases']:
        assert not case['audit']['violations']and case['completeGroupEvicted']and case['baseOnlyRestoredCompleteGroup']
        assert {'original-active','base-only','auto-restored','evicted-return-base-only'}<={r['phase']for r in case['retainedCanopyLifecycle']}
        if case['failedUid']:assert case['failureKeptAllBasics']
    canopy=part('canopy-post-foundation-v1-20261030');assert canopy['fullPostFootprintsMeetGround']and canopy['wholeRoofClear']and canopy['completePostCount']==8
    supports={u:'landsd/89917:0'for u in sources if u!='landsd/89917:0'};resources=sorted({('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms}|{'terrain:city/data/terrain.json'})
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,supportByUid=supports,identityAccepted=True,identityProofByUid=proofs,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},rawIdentityReasonsRetained=[dict(uid=x['uid'],reasons=x['reasons'],proof=x['proof'])for x in identities],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,qualifiedForLiveVerification=True,leaseResources=resources,currentManifest=ref(manifest),currentManifestSHA256=ref(manifest)['sha256'],completeCurrentNeighbourChecks=47,images=images,inspectionMethod='All20actual day/night exports inspected at contact-sheet resolution; two desktop exported canvases additionally inspected at full size. Separate atomic software observations prove all-original activation/fallback and retained canopy render/collision at every lifecycle phase; UI-occluded atomic screenshots do not replace exported-canvas review.',sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawCanonicalFailuresPreserved=True,reviewer='ROOT',installationApproved=False,publication=False,interpretation=['Exact immutable podium and four tower source components ported as supplied; no whole-landmark reconstruction or structural certification.','Every remaining original tower rim warning reaches an independently reproduced canonical strict anchor through unchanged source edges without endpoint rise. Complete fresh compound foundations are clear; raw direct-interface failures remain recorded.','Podium below-grade authored walls retain complete four-world cap paths; source-authored upward ramp triangles now clear on bounded source-derived terrain. Two native coverage slivers remain explicit and clear existing production grid fallback by at least0.851m.','Four BASIC tower ground-gap flags do not grant standalone publication: the existing atomic group retains all five original BASIC envelopes together during any original failure/Base-only/eviction. Their original source fields and fallback podium interface remain unchanged. The sole unrelated canopy regression is resolved only by extending eight existing illustrative post bottoms; roof/top/XZ and surveyed fields unchanged.','All remaining scoped forms keep current geometry, roofs and collision volumes; no unrelated source contacts or detailed actors/terrain overlaps nominated in the complete affected domain.'])
    save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result)
    module('villa_original_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-unchanged-five-original-source-physical-and-runtime-qualification',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

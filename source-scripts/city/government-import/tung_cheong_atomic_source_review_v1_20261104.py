"""Bound ROOT's actual export inspection and exact two-original assembly review.

The canopy-like source is accepted only with its exact atomic tower companion.
Raw standalone identity failures remain; no geometry, native match or limits change.
"""
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-tung-cheong-atomic-source-review-v1-20261104'
PREP='government-xl-tung-cheong-pair-preparation-v1-20261104'
BROWSER='government-xl-tung-cheong-atomic-private-browser-v1-20261104'
IDENTITY='government-xl-tung-cheong-atomic-identity-context-v1-20261104'
INSPECT=BASE/'government-xl-tung-cheong-atomic-export-inspection-v1-20261104'
HIGH,LOW='landsd/53799:0','landsd/223636:0'


def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json'
    assert not out.exists()
    refs,pins=[Path(__file__)],{}
    def take(batch,name):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=BASE/batch/name
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))]
        refs.append(p);return read(p)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    preview=take(BROWSER,'summary.json');resources=sorted(set(preview['leaseResources'])-{'server:127.0.0.1:4177'})
    if '--owned'not in sys.argv:
        assert not lp.parent.exists()
        c=reservations.claim('tung-cheong-atomic-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    sources=preview['sourceSHA256ByUid'];assert set(sources)=={HIGH,LOW}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==preview['currentManifestSHA256'];refs.append(manifest)
    identity=take(IDENTITY,'summary.json')
    assert identity['currentManifestSHA256']==preview['currentManifestSHA256']
    assert identity['targetUnionCoveredByOriginals']>=.95 and identity['completeProjectionCoveredByTenMetreTargetBuffer']is True
    assert identity['foreignExcessOverlaps']==[]and identity['completeOriginalFaces']==12202
    assert identity['currentTilesScanned']==452 and identity['currentFormsScanned']==346115
    assert {a['uid']:a['sourceSHA256']for a in identity['accounts']}==sources
    assert all(a['completeNamedGraphVerified']and a['uniqueCurrentGeoRef']for a in identity['accounts'])
    assert all(c['targetUnionCoversWholeCell']and c['sourceUnionCellCoverage']['coversWholeCell']for c in identity['compoundGeographicCells'])
    hashes=take(IDENTITY,'complete-current-tile-hashes.json')
    for url,h in hashes.items():assert digest((ROOT/'3d-viewer'/url).read_bytes())==h
    assert identity['nativeLowViewerUid']is None and identity['nativeMatchingRowsChanged']==0
    # Existing YOHO compound route: exact roots/unique GeoRefs, complete companion
    # footprint coverage and positive source contacts; never a standalone waiver.
    refs.append(HERE/'yoho_compound_identity_review_v1_20261020.py')
    pair_batch='government-xl-tung-cheong-unmatched-four-world-context-v2-20261103'
    pair=take(pair_batch,'summary.json');assert pair['completeSourceFaces']==[12158,44]
    assert len(pair['rows'])==4
    for r in pair['rows']:
        assert r['lowFoundation']['completeTerrainTriangles']==44 and r['lowFoundation']['fullyBuriedTriangles']==r['lowFoundation']['fullyBuriedUpwardTriangles']==0
        proof=take(pair_batch,r['mode']+'-pair.json.gz')
        assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0
        assert len(proof['contacts'])==r['pairFiniteContacts']and r['pairPositiveSurfaceContacts']>0
    foundation=take('government-xl-tung-cheong53799-source-physical-v1-20261103-foundations','summary.json')
    assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
    assert all(r['establishedFoundationPolicyPassed']and r['completeTerrainTriangles']==12158 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    take('government-xl-tung-cheong53799-source-physical-v1-20261103-ground-contacts','summary.json')
    metrics=take(PREP+'-runtime','metrics.json')
    assert {r['uid']for r in metrics['rows']}==set(sources)
    mobile=metrics['profiles']['mobile']
    for r in metrics['rows']:
        assert r['sourcePreserved']and r['sourceSHA256']==sources[r['uid']]
        assert r['checks']>0 and r['lowRimChecks']>0 and r['missingTerrain']==0
        assert r['missingDrawnTerrain']['count']==r['samplerDisagreement']['count']==0
        assert r['minSurfaceGap']>=-.5 and r['minLowGap']<=.1 and r['maxLowGap']<=1 and r['maxSamplerDelta']<=.004
        assert all(r['budget'][k]<=mobile[k]for k in ['geometryBytes','residentBytes','triangles'])
    unchanged=take(PREP,'unchanged-complete-four-world-source-arrays.json');assert len(unchanged)==2 and all(r['completeSourceArraysExactlyEqual']for r in unchanged)
    scope=take(PREP+'-source-scope','summary.json');assert all(r['currentNativeActorsChecked']==7106 for r in scope['rows'])
    assert { (r['uid'],n['uid'])for r in scope['rows']for n in r['nearbyNativeActors']}=={(HIGH,'landsd/12854:0')}
    native=take('government-xl-tung-cheong53799-foreign-contacts-v1-20261103-native','summary.json')
    assert len(native['rows'])==1 and native['rows'][0]['uid']==HIGH and native['rows'][0]['nativeUid']=='landsd/12854:0'
    assert all(m['finiteContactPairs']==m['positiveSurfaceContactPairs']==m['areaContactPairs']==0 for m in native['rows'][0]['modes'])
    for row in scope['rows']:
        forms=take(PREP+'-source-scope',row['uid'].split('/')[1]+'-forms.json.gz')
        assert {f['building']['uid']for f in forms}<={HIGH,LOW,'landsd/12854:0'}
    terrain_scope=take(PREP+'-terrain-scope','scope.json')
    forms=take(PREP+'-terrain-scope','form-obligations.json.gz');assert len(forms)==40
    neighbours=take('government-xl-tung-cheong53799-full-neighbours-v1-20261103-checks','summary.json')
    assert neighbours['forms']==40 and neighbours['basicFlags']==[]
    assert set(neighbours['nativeResolved'])==set(neighbours['requiredNativeUids'])==set(terrain_scope['touchingNativeUids'])and len(neighbours['nativeRows'])==9
    assert all(r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in neighbours['nativeRows'])
    terrain=take(PREP+'-terrain','summary.json');assert terrain['candidateBytesUnchanged']and terrain['additionalExplicitCompanionUids']==[LOW]
    old=terrain['replacedNativeTerrain'][0];replacement=dict(url=old['url'],sha256=old['sha256'],retainedUids=old['targetUids'])
    candidate=ROOT/terrain['candidate']['path'];assert ref(candidate)['sha256']==terrain['candidate']['sha256'];refs.append(candidate)
    assert set(read(candidate)['meta']['targetUids'])==set(old['targetUids'])|{HIGH}
    # Every actual source/native own-view export plus the three lifecycle exports
    # was opened by ROOT in this continuation. Authenticate exact original bytes.
    sheets=[];images=[]
    for name,width in [('desktop/desktop-contact-sheets.json',1280),('mobile/mobile-contact-sheets.json',390),('lifecycle/desktop-contact-sheets.json',1280),('lifecycle/mobile-contact-sheets.json',390)]:
        p=INSPECT/name;sheet=read(p);refs.append(p)
        assert sheet['originalPixelsResized']is False and not sheet['flatSceneWarnings']
        for item in [*sheet['sheets'],*sheet['originalImages']]:
            q=ROOT/item['path'];assert ref(q)['sha256']==item['sha256'];refs.append(q)
        sheets.extend(dict(**s,actuallyViewed=True)for s in sheet['sheets']);images.extend(sheet['originalImages'])
    assert len(images)==len({i['path']for i in images})==47 and len(sheets)==14
    for width in [1280,390]:
        report=take(BROWSER,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==4
        assert {(v['uid'],v['time'])for v in views}=={(u,t)for u in sources for t in ['15:00','22:00']}
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and v['fallbackFaces']==0
            assert v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
            assert len(v['retained'])==29 and all(r['loaded']and not r['detailedActive']and not r['hidden']for r in v['retained'].values())
        assert len(report['retainedNativeOwnViews'])==18 and {v['uid']for v in report['retainedNativeOwnViews']}==set(neighbours['requiredNativeUids'])
        assert all(v['active']and v['visible']and v['fullyFramed']and v['fallbackFaces']==0 for v in report['retainedNativeOwnViews'])
        assert len(report['jointViews'])==2 and all({m['uid']for m in r['models']}==set(sources)and all(m['active']and m['visible']and m['fallbackFaces']==0 for m in r['models'])for r in report['jointViews'])
    lifecycle=take(BROWSER,'atomic-lifecycle/report.json');assert lifecycle['passed']and not lifecycle['pageErrors']and len(lifecycle['cases'])==3
    assert {c['failedUid']for c in lifecycle['cases']if c['width']==390}==set(sources)
    assert all(c['baseOnlyRestoredCompleteGroup']and c['completeGroupEvicted']and not c['audit']['violations']for c in lifecycle['cases'])
    assert all(c['failureKeptAllBasics']for c in lifecycle['cases']if c['width']==390)
    cat=HERE/'local'/BROWSER/'catalogue.json';assert digest(cat.read_bytes())==pins[BROWSER][str(cat.relative_to(ROOT))];refs.append(cat)
    assert all(m['activationGroup']==sorted(sources)and not m.get('supportDependencies')and m['proceduralWindows']is False and m['publicationApproved']is False for m in read(cat)['models'])
    observations=dict(reviewer='Codex ROOT',imagesActuallyViewed=images,sheetsActuallyViewed=sheets,visualAcceptance=True,publication=False,installationApproved=False,limitations=['Night originals are dark; foreground objects and mobile lifecycle UI partly occlude views. No all-facet visibility, as-built certification or physical-phone FPS claim.'],observations=['Both original source actors are solid and framed in actual desktop/mobile day/night own views. The low original appears as a narrow adjoining base strip/roof-wall form with the tower behind it; no procedural windows are added. All nine retained originals remain present in their own views.','All three lifecycle exports were inspected; runtime instrumentation independently verifies complete group activation and fallback, per-peer retry, Base-only and eviction.'])
    save(out/'ROOT-EXPORT-OBSERVATIONS.json',observations)
    review=dict(currentManifest=ref(manifest),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,activationGroupRequired=True,identityAccepted=True,compoundIdentityAccepted=True,standaloneLowSourceIdentityAccepted=False,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,retainedNativeUids=neighbours['requiredNativeUids'],retainedNativeRegression=neighbours,exactTerrainReplacement=replacement,terrainGroundOwnerUids=[HIGH],unchangedSurfaceCompanionUids=[LOW],supportByUid={},unresolvedExternalBasicContacts=[],rawIdentityFailures=identity['rawIndividualIdentity'],rawIntraAssemblyContacts=pair['rows'],sourceGeometryChanges=0,sourcePoseChanges=0,nativeMatchingRowsChanged=0,nativeLowViewerUid=None,installedMetadataChanges=0,genericThresholdChanges=0,leaseResources=resources,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reviewer='Codex ROOT',installationApproved=False,publication=False,basis='Accept only these two exact immutable government originals as one atomic assembly. Complete named source graphs, unique current GeoRefs/BuildingIDs and active primary records identify the parts without treating labels as proof. Fresh provider OBJECTIDs differ and are preserved. Whole combined footprint coverage is 99.7177%; both complete GeoRef cells are covered; no excess overlaps a foreign form. The low original fails standalone coverage/cell tests and cannot replace that BASIC volume alone. The exact tower supplies its recorded envelope, while positive original contacts join the real adjoining low part. All authored intra-assembly contacts remain raw source context, not an invented support or foreign-collision waiver. Both sources pass unchanged terrain/rim/mobile budgets; all four complete source foundations, unchanged array bindings, the sole nominated foreign native with zero contacts, forty BASIC regressions and nine retained natives are bound. Actual 47 exports and per-peer atomic lifecycle pass. Existing fenced publisher, global retained supports, installed browser and independent readback remain mandatory.')
    save(out/'ROOT-PHYSICAL-REVIEW.json',review);save(out/'ROOT-SOURCE-REVIEW.json',review)
    assert reservations.owns(lease)and ref(manifest)==review['currentManifest']
    module('tung_cheong_atomic_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-two-original-compound-source-physical-neighbour-export-review',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,compoundIdentityAccepted=True,standaloneLowSourceIdentityAccepted=False,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=47,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,installationApproved=False,publication=False))


if __name__=='__main__':main()

"""Bound exact tower identity and exposed original panel evidence; no installation."""
from pathlib import Path
from fractions import Fraction
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-lee-shau-kee-bounded-identity-panel-review-v1-20261025'
RT='government-xl-polyu-lee-shau-kee-current-ground-v2-20261025'
ID='government-xl-polyu-lee-shau-kee-current-identity-v2-20261025'
LOW='government-xl-polyu305600-current-complete-ground-v2-20261025'
CAP='government-xl-polyu305600-current-cap-paths-v2-20261025'
OVER='government-xl-polyu-lee-shau-kee-sports-overhang-context-v1-20261025'
PREVIEW='government-xl-polyu-lee-shau-kee-unapproved-source-preview-v2-20261025'
MAIN='landsd/305600:0';SMALL='landsd/257998:0';LIB='landsd/305793:0';SPORT='landsd/305582:0'


def main():
    out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(n,name='summary.json'):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        p=BASE/n/name;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selected=take(RT,'selection.json.gz');rows={r['uid']:r for r in selected['rows']}
    assert set(rows)=={MAIN,SMALL}
    sources={u:r['sourceSHA256']for u,r in rows.items()}
    raw={u:take(ID,u.split('/')[1]+'/identity.json')for u in rows}
    assert set(raw[MAIN]['reasons'])=={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
    assert raw[SMALL]['passed'] and not raw[SMALL]['reasons']
    primary=take('government-xl-polyu-lee-shau-kee-primary-v2-20261025','footprints.json')
    records={r['attributes']['BuildingCSUID']:r['attributes']for r in primary['features']}
    for uid,r in rows.items():
        d=raw[uid];f=r['source']['building'];asset=ROOT/r['candidate']['path']
        assert digest(asset.read_bytes())==sources[uid]==d['sourceSHA256'];refs.append(asset)
        assert d['originalOwnership']['sourceGraphVerified'] and d['exactCurrentComponentRoute']['qualified'] and d['exactWholeCellCoverage']['covered'] and d['freshCurrentIdentity']['exactObjectAndCSUID']
        rec=records[f['buildingCSUID']]
        assert rec['Status']=='Active' and rec['BuildingBlockType']==f['structureType'] and rec['BaseHeight']==f['base'] and abs(rec['TopHeight']-f['base']-f['height'])<1e-8
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==f;refs.append(tile)
    over=take(OVER);assert over['sourceSHA256']==sources[MAIN]
    assert len(over['rows'])==4 and all(r['conservativeVerticalSeparationM']>4.44 for r in over['rows'])
    continuous=take('government-xl-polyu-lee-shau-kee-current-continuous-v2-20261025')
    assert all(r['upwardContinuousMinimumGapM']>=-.5 and set(r['continuousAffectedFaces'])==set(r['affectedWallFaces'])for r in continuous['rows'])
    cov=take('government-xl-polyu-lee-shau-kee-current-exact-coverage-v2-20261025');assert all(not r['stillUncoveredFaces']for r in cov['rows'])
    caps=take(CAP);panels=[]
    for row in caps['rows']:
        mode=row['mode'];paths=row['completeGroundClearancePartition']['paths'];assert len(paths)==38
        failed=[r['sourceFace']for r in paths if not r['hasExactSharedEdgeClearCapPath']];assert failed==[4292,4293]
        low=take(LOW,mode+'.json.gz');assert low['sourceWorldSHA256']==row['sourceWorldSHA256']
        for face in failed:
            r=next(r for r in low['rows']if r['sourceFace']==face)
            assert r['absoluteNormalYRatio']==0 and r['highestVertexAboveEveryOverlappingGroundFace']
            crossing=[]
            for p in r['negativeGroundPairProofs']:
                gaps=[Fraction(v['exactGapM'])for v in p['proof']['allExactBasicFeasibleColumnVertices']]
                if gaps and min(gaps)<0<max(gaps):crossing.append(p['groundFace'])
            assert crossing
            panels.append(dict(mode=mode,sourceFace=face,exactFiniteGradeCrossingPairs=crossing,rawMinimumGapM=r['minimumFiniteGapM'],highestOriginalVertexAboveEveryOverlappingGroundFace=True))
    support=take('government-xl-polyu-lee-shau-kee-library-support-v2-20261025')
    small=[r for r in support['rows']if r['uid']==SMALL];large=[r for r in support['rows']if r['uid']==MAIN]
    assert len(small)==len(large)==4
    assert all(r['strictPassed'] and r['strictContacts']==r['samples']==34 and r['unresolved']==0 for r in small)
    assert all(r['strictContacts']==0 and r['unresolved']==5 for r in large)
    binding=take('government-xl-polyu-library-support-current-stream-binding-v1-20261025');assert binding['nativeStreamReuseVerified']
    native=take('government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025','native-input.json.gz')
    native_entries={r['uid']:r['entry']for r in native['rows']if r['uid']in {LIB,SPORT}}
    assert native_entries[LIB]['publicationApproved']is False
    assert {MAIN,SMALL}<=set(native_entries[LIB]['suppressesBuildingUids'])
    images=[]
    pins[PREVIEW]=authenticate(BASE/PREVIEW)[1];refs.append(BASE/PREVIEW/'result.json')
    for n,file in [(OVER,'original-overhang-and-native-height-context.png'),(PREVIEW,'staged-landsd-305600-0-1280-1500-canvas.png'),(PREVIEW,'staged-landsd-305600-0-1280-2200-canvas.png')]:
        p=BASE/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result=dict(uids=sorted(rows),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,reviewer='ROOT',identityAccepted=True,identityProof=proof,identityProofByUid={u:proof for u in rows},rawIdentityProofs=raw,mainExposedOriginalPanels=panels,mainOtherClearCapFaces=36,proposedCompanionSupportUid=LIB,proposedCompanionStrictContactsPerStream=34,retainedNativeEntries=native_entries,retainedLibraryPublicationHoldUnchanged=True,retainedLibrarySuppressionOfRequestedUidsUnchanged=[MAIN,SMALL],imagesActuallyViewed=images,sourceGeometryChanges=0,nativeMetadataChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,remainingReason='Complete source-specific retained-native publication/suppression/dependency review and guarded model-only preview path; no automatic external-native-support admission or prior library approval transfer.',observations=[
        'Exact current ObjectIDs/CSUIDs, unique component routes, owned original source graphs, complete GeoRef cells and current official active footprint records identify both originals. The companion passes every raw identity rule. Main target coverage and extent pass; its only raw identity failures concern16.108m2 of elevated projection over the Sports Centre record.',
        'ROOT opened the exact original-overhang diagram and both unapproved main-source desktop exports. Every contributing original face is above the entire unchanged Sports Centre by at least4.4485m in every stream; all raw excess is accounted for. The source diagram shows a small corner projection of the named tower, not another building body. Accept identity only for these exact source hashes, preserving raw unrelated-overlap flags and generic policy. No photograph-based dimensional accuracy, broad campus exemption or source crop is claimed.',
        'Thirty-six affected main walls have exact complete-ground clear-cap paths. Two remaining original vertical panel faces4292/4293 spanY9.442..15.220m and each crosses actual ground with exposed highest vertex in all4streams. Preserve missing-cap and5low-rim failures. These are positive source-role facts, not approval of a dependency on the library, whole engineering acceptance or permission to cap/edit the source.',
        'Companion147faces have34strict library contacts in every stream; the main has0strictlibrarycontacts/5embedded probes. Reverse proposed pair directions also fail. Do not invent a co-import parent to fit an old adapter. Every source face has exact currentground projection coverage, and all upward main/companion surfaces clear actualearth; terrain replacement is not indicated by these results.',
        'The library exact installed entry remains publicationApproved:false and suppresses both requested BASIC UIDs. Original Sept13 installed-acceptance and later Oct15 Sports review do not grant a new current library publication approval. This record changes neither that flag nor any suppression. Actual retained-native dependency/fallback/suppression behaviour needs a bounded reviewed adapter and complete desktop/mobile own-source+retained exports before installation. No new models are installed by this packet.'
    ])
    save(out/'ROOT-IDENTITY-PANEL-CONTEXT.json',result)
    module('polyu_identity_panel_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-exact-polyu-original-identity-and-exposed-panel-source-context',refs,{k:v for k,v in result.items()if k!='rawIdentityProofs'})


if __name__=='__main__':main()

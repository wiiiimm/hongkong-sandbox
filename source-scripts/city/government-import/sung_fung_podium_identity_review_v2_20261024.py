"""Bounded exact government podium identity review; all physical gates remain open."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-podium-identity-review-v2-20261024';out=base/batch;assert not out.exists()
    names=dict(identity='government-xl-next-repairs-sung-fung-three-current-identity-v1-20261024',runtime='government-xl-next-repairs-sung-three-retained-runtime-v1-20261024',projection='government-xl-next-repairs-sung-fung-original-pair-projection-v1-20261024',views='government-xl-next-repairs-sung-fung-three-source-context-views-v1-20261024')
    refs=[Path(__file__)];pins={}
    def take(kind,name):
        n=names[kind]
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/name;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take('runtime','selection.json.gz');source=next(r for r in selection['rows']if r['uid']=='landsd/45779:0')
    raw=take('identity','45779:0/identity.json');context=take('identity','45779:0/context.json');pair=take('projection','summary.json')
    assert raw['uid']==source['uid'] and raw['sourceSHA256']==source['sourceSHA256']=='28e868670016b935355c29b991ac1d7fc3703f1579d98b3ce79403b605716de5'
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['exactCurrentComponentRoute']['qualified'] and raw['exactWholeCellCoverage']['covered'] and raw['geographicCell']['targetCoversWholeCell']
    pr=raw['originalOwnership']['fullProjection'];assert pr['exactObjectAndCSUID'] and pr['sourceExcessCoveredByUnrelatedFormsM2']==0
    assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-maximum-extent','full-source-target-coverage'}
    assert .8395<pr['targetCoveredBySourceProjection']<.8397 and 11.492<pr['sourceExcessMaximumDistanceFromTargetM']<11.494
    assert .9970<pair['completePairTargetCoverage']<.9971 and pair['unrelatedExcessAreaM2']==0
    assert 704.64<pair['podiumMissingCoveredByOriginalTowerM2']<704.65 and 13.16<pair['podiumMissingRemainingAfterOriginalTowerM2']<13.17
    required={r['uid']:r['sourceSHA256']for r in selection['rows']};assert pair['sourceSHA256ByUid']=={uid:required[uid]for uid in pair['uids']}
    for row in selection['rows']:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256'];refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for tile,sha in context['neighbourTileHashes'].items():
        path=ROOT/'3d-viewer'/tile;assert digest(path.read_bytes())==sha;refs.append(path)
    take('views','summary.json');images=[]
    for name in ['complete-original-assembly.png','base-only-diagnostic.png']:
        path=base/names['views']/name;assert digest(path.read_bytes())==pins[names['views']][str(path.relative_to(ROOT))];refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    review=dict(uid=source['uid'],reviewer='Codex ROOT',reviewType='exact-original-podium-component-identity',sourceSHA256=source['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],modelId=source['modelId'],sourceFaces=source['triangles'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=raw,rawReasonsRetained=raw['reasons'],requiredUnchangedAssemblySources=required,currentManifestSHA256=selection['manifestSHA256'],imagesActuallyInspected=images,reviewBasis=[
        'The exact government ObjectID45779/CSUID3777116537P20060312, verified original root graph, current typed component route and complete one-metre geographic cell identify this original podium. This review does not infer identity from a shared name or parent alone.',
        'The independent podium projection covers83.9593percent of its surveyed composite target. The complete unchanged Sung Fung plus podium source projection covers99.7057percent:704.6438square metres of the717.8066square-metre shortfall are the original Sung Fung tower component.13.16275square metres remain unmatched and are preserved in the raw evidence. No geometry, buffering or gap filling was used.',
        'Prior ROOT inspection of these exact hash-bound unchanged-source images is retained: the complete three-source two-angle export and the26m display-only base clipping. The unchanged source is a stepped low podium with tower cut-outs, low terraces and projecting perimeter surfaces. The11.49294m extent warning belongs to that full original podium component; no unrelated-form excess is measured. This is source correspondence, not photographic architectural accuracy or legal ownership.',
        'Sung Fung and Lee & Man remain separately identified unchanged original sources; Nam Fung remains an independently installed actor. No actor is merged, suppressed or accepted by this identity review. The required exact assembly SHA tuples prevent reuse for different source bytes.',
        'Identity only. Preserve archived raw podium burial measurements and their subsequent exact-terrain checks, canonical strict support failures, existing Nam Fung fallback dependency, raw source contacts, all compound foundations, terrain/neighbour checks and staged/live desktop/mobile publication obligations. No physical or publication exception is granted.'
    ],sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,placementReviewed=False,publicationApproved=False,installationApproved=False)
    save(out/'45779:0-review.json',review)
    module('sung_podium_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-podium-identity-review',list(dict.fromkeys(refs)),dict(uids=[source['uid']],identityAccepted=True,installationApproved=False,sourceGeometryChanges=0))

if __name__=='__main__':main()

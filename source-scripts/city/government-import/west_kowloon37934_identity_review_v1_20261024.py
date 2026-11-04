"""Bound the exact shaft identity to its unchanged original terminus assembly."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';batch=prefix+'37934-identity-review-v1-20261024';out=base/batch;assert not out.exists();pins={};refs=[Path(__file__)]
    def take(s,f):
        n=prefix+s
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take('six-original-runtime-v2-20261024','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==6;source=next(r for r in selection['rows']if r['uid']=='landsd/37934:0');assert source['sourceSHA256']=='9f7f9f04fd7021f592a71ee88ae75e91e1f8e7863e1ab02e7609712168e47ea9'
    raw=take('six-original-identity-v1-20261024','37934:0/identity.json');context=take('six-original-identity-v1-20261024','37934:0/context.json');assert set(raw['reasons'])=={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}
    assert raw['originalOwnership']['sourceGraphVerified']and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered'];pr=raw['originalOwnership']['fullProjection'];assert pr['exactObjectAndCSUID']and pr['sourceExcessCoveredByUnrelatedFormsM2']==0 and .8555<pr['targetCoveredBySourceProjection']<.8556
    pair=take('37934-roof-pair-projection-v1-20261024','summary.json');assert pair['sourceSHA256ByUid']=={u:sources[u]for u in pair['uids']};assert 1.9586<pair['podiumTargetMissingFromPodiumSourceM2']<1.9588 and 0<pair['podiumMissingRemainingAfterOriginalTowerM2']<.000384
    contacts=take('six-new-original-pairs-v1-20261024','summary.json');joined=next(r for r in contacts['rows']if r['supportUid']=='landsd/231056:0');assert joined['contacts']==43 and joined['contactDimensions']['2']==4
    images=[]
    for name,files in [('37934-identity-plots-v1-20261024',['whole-source-plan.png','whole-source-perspectives.png']),('six-original-plots-v1-20261024',['complete-original-assembly.png','base-only-diagnostic.png'])]:
        take(name,'summary.json')
        for f in files:
            n=prefix+name;p=base/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    for row in selection['rows']:
        p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p)
    for tile,sha in context['neighbourTileHashes'].items():
        p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==sha;refs.append(p)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    review=dict(uid=source['uid'],reviewer='ROOT',sourceSHA256=source['sourceSHA256'],sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],modelId=source['modelId'],identityOnlyApproved=True,identityReviewApproved=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),rawProof=raw,rawReasonsRetained=raw['reasons'],requiredUnchangedAssemblySources=sources,currentManifestSHA256=selection['manifestSHA256'],imagesActuallyInspected=images,sourceIdentityReviewUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,placementReviewed=False,publicationApproved=False,installationApproved=False,basis=[
        'Exact ObjectID37934/CSUID3498218681T20180831 and provider Tower ModelID B349821868101063C0, unchanged root graph, typed current component route and complete geographic cell bind this source. No nearest-name or speculative placement assignment.',
        'ROOT inspected both complete-source identity exports and both six-original assembly exports. This is a narrow continuous shaft with an overhanging square cap alongside the original raised roof. Its individual projection covers85.55574percent of the current simplified footprint; the original roof231056 accounts for1.958303m2of1.958687m2missing projection.0.000383578m2remains unmatched and is retained. The pair union covers96.58228percent of both target forms; do not present that as total-assembly or shaft-only coverage.',
        'The original shaft extends down to5.558317mHKPD while its recorded basic form begins14.7mHKPD. Both facts remain unchanged; this identity review does not alter source pose, recorded height or terrain. The prepared exact source graph and rooftop component correspondence identify the complete original, not only the shorter basic extrusion.',
        'Exact original shaft/roof surface contact report retains43contacts including4shared-plane areas; this supports correspondence of these original components but grants no collision or structural support approval. The six exact source SHA tuples are required together; another mesh or partial assembly needs fresh review.',
        'Identity only. Preserve all strict support/ground warnings, actual finite source contacts, retained292042boundary intrusion, current-neighbour checks and desktop/mobile staged/live publication obligations. No model generation, source edits, suppression, physical or publication approval.'
    ])
    save(out/'37934:0-review.json',review);module('west_37934_identity_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-original-terminus-shaft-component-identity-review',refs,dict(uids=[source['uid']],identityAccepted=True,installationApproved=False,sourceGeometryChanges=0))

if __name__=='__main__':main()

"""ROOT source-specific stadium identity review; no automatic guard or publication change."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-source-identity-review-v1-20261021';DOC=BASE/BATCH

def main():
    assert not DOC.exists();refs=[Path(__file__)];bound={}
    def take(batch,relative):
        folder=BASE/batch;_,pins=authenticate(folder);p=folder/relative;k=str(p.relative_to(ROOT));h=digest(p.read_bytes());assert pins[k]==h;bound[k]=h;refs.extend([folder/'result.json',p]);return p
    current='government-xl-remaining-forty-original-identity-v2-20261021'
    identity=read(take(current,'240332:0/identity.json'))
    expected=['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
    assert sorted(identity['reasons'])==sorted(expected)
    assert identity['exactCurrentComponentRoute']['qualified'] and identity['exactWholeCellCoverage']['covered']
    spatial=identity['freshCurrentIdentity'];assert spatial['exactObjectAndCSUID'] and spatial['targetCoveredBySourceProjection']>.999999 and spatial['unrelatedIntersectingForms']==0 and spatial['sourceExcessCoveredByUnrelatedFormsM2']==0
    selection=read(take(current,'selection.json.gz'));row=next(r for r in selection['rows']if r['uid']=='landsd/240332:0')
    source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256']=='896138f962db178400870c74c41d5eae3a2ba99e0c978fad49790956c0a50bdd';refs.append(source)
    tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
    farbatch='government-xl-mongkok-far-feature-context-v1-20261021';far=read(take(farbatch,'summary.json'));assert far['historicalAttributionMatchesCurrentSourceAndFootprint'] and len(far['farFaces'])==62 and far['sourceSHA256']==row['sourceSHA256']
    assert far['maximumExtentM']==spatial['sourceExcessMaximumDistanceFromTargetM']
    imagepaths=[take(farbatch,'far-feature.png'),take('government-xl-two-extent-context-v1-20261021','240332-0.png')]
    photo='government-xl-mongkok-official-photo-context-v1-20261021';take(photo,'sources.json');imagepaths += [take(photo,f'01704{c}.jpg')for c in 'abcdefghij']
    images=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in imagepaths]
    result=dict(uids=[row['uid']],reviewer='ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceSHA256=row['sourceSHA256'],sourceFormTileSHA256=row['source']['tileSHA256'],imagesActuallyViewed=images,identityAccepted=True,sourceSpecificIdentityReviewAccepted=True,automaticIdentityCheckPassed=False,rawIdentityReasons=identity['reasons'],rawMaximumExtentM=far['maximumExtentM'],rawSourceExcessAreaM2=spatial['sourceExcessAreaM2'],wholeOriginalFaces=15456,farOriginalFaces=far['farFaces'],farBounds=far['farBounds'],observations=[
        'Exact CSUID/object/type routing and the complete geographic cell identify this unchanged source as the recorded stadium grandstand; all other current identity checks passed.',
        'The complete source view has repeated canopy bays, a continuous stepped spectator frontage and access structures. These correspond qualitatively to the north stand at image-left in official photograph01704c, facing the scoreboard end. This is source interpretation, not metric photogrammetry.',
        'All62 original faces beyond10m occur in the low west-end extension, at source heights7.394967079162598 to8.708999633789062m. The detailed source render shows paired low walls and an inclined approach connected to the stand. They are not displaced roof facets or an unrelated tower.',
        'Official photograph01704c shows the low elongated access/wall feature continuing beyond the west end of that stand. The other official views establish the repeated stair/frontage and canopy context. Photographs do not establish centimetre coordinates, slope compliance or physical support.',
        'Historical exact shared-edge attribution, now rebound to identical current bytes and footprint, connects every flagged face to target-projected source geometry. Together with exact government routing, photographs and zero unrelated-form overlap, this supports retaining the full source as one stadium model despite the footprint-only distance flags.'
    ],decision='Accept source identity for this exact original revision and current form. Preserve both automatic extent failures as raw diagnostics. This review is not a general distance exemption and does not modify the automatic checker.',remainingRequirements=['Current complete foundation and terrain checks','All affected ordinary and installed-model regressions for any terrain repair','Staged and live desktop/mobile visibility, picking, collision and recovery','Guarded publication and commit/push'],sourceGeometryChanges=0,sourcePoseChanges=0,terrainGeometryChanges=0,installationApproved=False,publicationApproved=False)
    for k,h in bound.items():assert digest((ROOT/k).read_bytes())==h
    save(DOC/'ROOT-IDENTITY-REVIEW.json',result)
    module('mongkok_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-stadium-source-identity',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

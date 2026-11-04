"""Exact-source review of the ventilation building's authored portal roof extent.

Identity only; no physical, neighbour, runtime or installation approval.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';UID='landsd/335494:0'
SHA='79e43d3e3c6d5cdb5f2b45b6f7734cb0a94a970665d7610fc0efaf7eb3e9ca1b'
BATCH='government-xl-ventilation335494-bounded-identity-review-v1-20261024'
IDENTITY='government-xl-next-four-after-hanford-identity-v1-20261024'
CAPTURE='government-xl-next-four-after-hanford-runtime-v1-20261024'
PLOTS='government-xl-next-four-after-hanford-335494-source-plots-v1-20261024'


def main():
    out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__)]
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(batch,path):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        assert ref(path)['sha256']==pins[batch][ref(path)['path']];refs.append(path);return read(path)
    selection=take(CAPTURE,BASE/CAPTURE/'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID)
    assert row['sourceSHA256']==SHA and row['triangles']==10338
    source=ROOT/row['candidate']['path'];assert ref(source)['sha256']==SHA;refs.append(source)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    source_tile=ROOT/'3d-viewer'/row['source']['tile'];assert ref(source_tile)['sha256']==row['source']['tileSHA256']and next(b for b in read(source_tile)['buildings']if b['uid']==UID)==row['source']['building'];refs.append(source_tile)
    proof=take(IDENTITY,BASE/IDENTITY/'335494:0/identity.json');context=take(IDENTITY,BASE/IDENTITY/'335494:0/context.json')
    assert proof['sourceSHA256']==SHA and proof['originalOwnership']['sourceGraphVerified']
    assert proof['originalOwnership']['originalRootName']==row['modelId']=='B344081637301063C0'
    assert set(proof['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
    route=proof['exactCurrentComponentRoute'];assert route['qualified']and route['uid']==UID and route['source']==row['source']
    assert proof['exactWholeCellCoverage']['covered']and proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==10338
    assert proof['geographicCell']['targetCoversWholeCell']and proof['geographicCell']['originalProjectionCoversWholeCell']
    spatial=context['identity'];assert spatial['exactObjectAndCSUID']and spatial['targetCoveredBySourceProjection']>.999999
    assert spatial['sourceExcessCoveredByUnrelatedFormsM2']==0 and spatial['unrelatedIntersectingForms']==0
    assert len(spatial['intersectingForms'])==1 and spatial['intersectingForms'][0]['uid']==UID
    figures=[]
    for name in ['whole-source-plan.png','whole-source-perspectives.png']:
        p=BASE/PLOTS/name
        if PLOTS not in pins:
            _,pins[PLOTS]=authenticate(BASE/PLOTS);refs.append(BASE/PLOTS/'result.json')
        assert ref(p)['sha256']==pins[PLOTS][ref(p)['path']];refs.append(p);figures.append(ref(p))
    official=BASE/'government-xl-ventilation335494-official-context-v1-20261024';provenance=read(official/'provenance.json');photo=official/'official-west-ventilation-building.jpg'
    assert ref(photo)['sha256']==provenance['imageSHA256'];refs.extend([photo,official/'provenance.json']);figures.append(ref(photo))
    observations=[
        'ROOT inspected the complete original plan, two original perspectives and the official government photo. The source contains the curved leaf roof, open portal truss canopy and tapered outer frame visible in that photo. The GIS outline is a smaller central building footprint and does not describe the complete authored portal roof. The38.9023m extent warning therefore measures retained roof/portal architecture, not an arbitrary detached building or shifted source.',
        'The Information Services Department article Cleaner air with new link, dated1January2019, explicitly describes the West Ventilation Building roof extending over the Central Tunnel Portal. This independently corroborates the observed roof/portal composition; it does not establish engineering dimensions. Article URL, image URL, short12word excerpt and exact image hash are recorded in the provenance note.',
        'Exact current ObjectID335494/CSUID3440816373T20170609, unique provider/component route, owned complete original root graph and exact whole1mGeoRefcell bind this immutable10338face source. The current target is fully covered, and the entire projected extension has zero other-form or unrelated-form overlap. Original pose/1xscale/source bytes remain unchanged.',
        'Accept identity for this exact hash and current form based on the authoritative source binding and explicitly reviewed original roof extent. Retain both raw extent failures, every source facet and the unchanged generic10m extent policy. Physical clearance/support, complete current neighbours, actual desktop/mobile exports and guarded publication remain separate; no installation or geometry edits are authorised by this record.'
    ]
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},sourceSHA256=SHA,reviewer='ROOT',identityAccepted=True,identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},requiredOriginalAssembly={UID:SHA},currentManifest=ref(manifest),rawIdentityProof=proof,rawExtentFailuresRetained=True,genericIdentityPolicyChanges=False,figuresActuallyViewed=figures,officialContext=ref(official/'provenance.json'),observations=observations,physicalAcceptance=False,visualRuntimeAcceptance=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True)
    save(out/'ROOT-IDENTITY-REVIEW.json',result)
    module('ventilation_bounded_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-ventilation-building-authored-portal-roof-identity-review',list(dict.fromkeys(refs)),{k:v for k,v in result.items()if k!='rawIdentityProof'})

if __name__=='__main__':main()

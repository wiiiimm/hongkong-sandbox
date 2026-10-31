"""Review the exact Tower VI component identity; retain source extent warnings."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

PREFIX = 'government-xl-after-dragon-next-five-'
UID = 'landsd/203730:0'
SHA = 'ef6b1eef5ee27f3c9f027d48436cc31722c8c41b4179e68f90f0d9542e03232e'


def main():
    base=ROOT/'docs/astra-city/government-import'; batch=PREFIX+'waterfront-identity-review-v1-20261026'
    out=base/batch; assert not out.exists(); refs=[Path(__file__)]; pins={}
    def take(suffix,name):
        folder=base/(PREFIX+suffix+'-20261026')
        if folder.name not in pins:
            pins[folder.name]=authenticate(folder)[1]; refs.append(folder/'result.json')
        path=folder/name; assert digest(path.read_bytes())==pins[folder.name][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection=take('ground-v1','selection.json.gz'); source=next(r for r in selection['rows']if r['uid']==UID)
    raw=take('identity-v1','203730:0/identity.json'); form=source['source']['building']
    assert source['sourceSHA256']==raw['sourceSHA256']==SHA
    assert source['modelId']==raw['originalOwnership']['originalRootName']=='B348761848101063C0'
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['exactCurrentComponentRoute']['qualified']
    assert raw['freshCurrentIdentity']['exactObjectAndCSUID'] and raw['exactWholeCellCoverage']['covered']
    assert not raw['passed'] and raw['reasons']==['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
    assert form['buildingCSUID']=='3487618481T20050430' and form['buildingId']==1108241993
    fresh=raw['freshCurrentIdentity']; assert fresh['targetCoveredBySourceProjection']>.996 and fresh['sourceExcessCoveredByUnrelatedFormsM2']==0
    assert 12.98<fresh['sourceExcessMaximumDistanceFromTargetM']<12.99
    asset=ROOT/source['candidate']['path']; assert digest(asset.read_bytes())==SHA; refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes()); assert len(tri)==10667 and digest(tri.astype('<f8').tobytes())==raw['worldTrianglesSHA256']
    footprint=next(r['attributes']for r in take('primary-v1','footprints.json')['features']if r['attributes']['BuildingCSUID']==form['buildingCSUID'])
    assert footprint['BuildingID']==form['buildingId'] and footprint['Storeys']==36 and footprint['BuildingNameEN']=='The Waterfront Tower VI'
    assert footprint['BaseHeight']==32.1 and footprint['TopHeight']==141.2
    foreign=take('foreign-v1','summary.json'); external=[r for r in foreign['rows']if r['uid']==UID]
    assert len(external)==3 and all(m['allFiniteContactPairs']==0 for r in external for m in r['modes'])
    images=[]
    for suffix,names in [('203730-source-plots-v1',['whole-source-plan.png','whole-source-perspectives.png']),('waterfront-map-v1',['official-map-comparison.png'])]:
        take(suffix,'summary.json')
        for name in names:
            path=base/(PREFIX+suffix+'-20261026')/name
            assert digest(path.read_bytes())==pins[path.parent.name][str(path.relative_to(ROOT))]
            refs.append(path); images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes())==selection['manifestSHA256']; refs.append(manifest)
    result=dict(uid=UID,uids=[UID],reviewer='Codex ROOT',modelId=source['modelId'],sourceSHA256=SHA,
        sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],completeSourceFaces=10667,
        currentManifestSHA256=digest(manifest.read_bytes()),identityOnlyApproved=True,identityReviewApproved=True,
        identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),
        rawIdentityVerbatim=raw,rawReasonsRetained=raw['reasons'],freshPrimaryFootprint=footprint,
        sourceHeightRangeHKPD=[float(tri[:,:,1].min()),float(tri[:,:,1].max())],imagesActuallyInspected=images,
        interpretation='The stable CSUID/BuildingID, uniquely routed original root and graph, complete geographic cell and fresh36-storey primary record identify the exact Tower VI source component. The inspected source plan and two perspectives contain the same branching tower footprint, facade projections and a lower apron/skirt with small detached source details. The official basemap places that complete component at the eastern Waterfront block. The lower authored source extends to23.478m HKPD while the2D Tower record begins32.1m; retain this difference and the12.9803m outer extent warning. It is not evidence for moving or scaling the source. More than99.6percent of the tower footprint is covered, no excess projects onto an unrelated BASIC form, and all three external BASIC pairs have zero finite contacts in all representations. This approves faithful component identity only: the Elements podium relationship, five strict unresolved samples, six compound-buried walls and non-wall compound clearance conflicts remain separate, unapproved physical obligations. No common property ownership or engineering support is inferred. Fresh service OBJECTID203424 does not replace immutable viewer203730.',
        sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,
        physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,
        qualification='Bounded exact-source identity interpretation, preserving the raw automatic failures and all physical/retained-source/browser obligations. No installation credit or approval transfer to Elements.')
    save(out/'ROOT-IDENTITY-REVIEW.json',result); refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('waterfront_exact_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-waterfront-vi-source-identity-only-review',refs,result)


if __name__=='__main__': main()

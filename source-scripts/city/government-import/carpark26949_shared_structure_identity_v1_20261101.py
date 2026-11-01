"""Bound exact carpark identity to explicit government shared-structure records.

No approval of related Academic geometry, terrain, collisions or publication.
"""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-academic309823-after-kai-tak-'
BATCH=P+'carpark-shared-structure-identity-v1-20261101'
UID,OTHER='landsd/26949:0','landsd/309823:0'
SHA='e4cf4099b7a1179c0c1a6ea27a7dc9036bde9ad08ba2ee900a6ac0fe3542fde8'
OTHER_SHA='7270510e89f268a8c114ba787cdf9a1d4255d55acdc0d05bb4dfd81922f0e65a'
REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned',action='store_true');args=parser.parse_args()
    lp=HERE/'local'/BATCH/'reservation.json'
    assert not (BASE/BATCH).exists()
    resources=read(BASE/(P+'carpark-current-runtime-plan-v1-20261101.json'))['resources']
    if not args.owned:
        assert not lp.parent.exists()
        claim=reservations.claim('carpark-shared-structure-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert claim['ok'],'Source scope reserved; do not bypass ownership'
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease) and set(lease['resources'])==set(resources)
    pins={};refs=[Path(__file__)]
    def take(batch,name):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(P+'current-two-originals-v1-20261101','selection.json.gz')
    rows={r['uid']:r for r in selection['rows']};assert set(rows)=={UID,OTHER}
    assert {u:r['sourceSHA256']for u,r in rows.items()}=={UID:SHA,OTHER:OTHER_SHA}
    raw=take(P+'carpark26949-identity-v1-20261101','26949:0/identity.json')
    assert raw['uid']==UID and raw['sourceSHA256']==SHA and not raw['passed'] and set(raw['reasons'])==REASONS
    assert raw['originalOwnership']['sourceGraphVerified'] and raw['originalOwnership']['originalRootName']==rows[UID]['modelId']
    assert raw['exactCurrentComponentRoute']['qualified'] and raw['exactWholeCellCoverage']['covered']
    assert raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==680
    spatial=raw['freshCurrentIdentity'];assert spatial['exactObjectAndCSUID']
    assert {f['uid']for f in spatial['intersectingForms']}=={UID,OTHER}
    assert {f['uid']for f in spatial['intersectingForms']if not f['sameParent']}=={OTHER}
    primary=P+'carpark-academic-primary-v1-20261101'
    footprints=take(primary,'footprints.json')['features'];official={f['attributes']['BuildingCSUID']:f['attributes']for f in footprints}
    assert len(official)==len(footprints)==2
    relations=take(primary,'relations.json')['features'];structures=take(primary,'structures.json')['features']
    csuids={u:r['source']['building']['buildingCSUID']for u,r in rows.items()}
    links={u:sorted({int(f['attributes']['BuildingStructureID'])for f in relations if f['attributes']['BuildingCSUID']==cs})for u,cs in csuids.items()}
    assert links[UID]==[1732120] and set(links[UID])&set(links[OTHER])=={1732120}
    shared=[f['attributes']for f in structures if f['attributes']['BuildingStructureID']==1732120]
    assert len(shared)==1 and shared[0]['OPNo']=='NT98/91' and shared[0]['Storeys']==15
    with connect()as db:
        db.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
        for uid,row in rows.items():
            form=row['source']['building'];a=official[csuids[uid]]
            assert a['Status']=='Active' and a['GeoRefNo']==csuids[uid][:10]==row['modelId'][1:11]
            assert a['BuildingBlockType']==form['structureType']
            assert a['BaseHeight']==form['baseHeightHKPD'] and a['TopHeight']==form['topHeightHKPD']
            tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']
            assert [f for f in read(tile)['buildings']if f['uid']==uid]==[form];refs.append(tile)
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
            record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()
            assert record and record[0]==row['native']['resultSha']
            assert next(m for m in record[1]['models']if m['modelId']==row['modelId'])==row['native']['model']
    route=raw['exactCurrentComponentRoute'];assert route['official']['objectId']==rows[UID]['source']['building']['objectId']==26949
    assert route['official']['buildingCSUID']==csuids[UID]=='4513822205T20050430'
    views=take(P+'carpark-academic-source-views-v1-20261101','summary.json')['views'];assert len(views)==1
    image=ROOT/views[0]['image']['path'];assert digest(image.read_bytes())==views[0]['image']['sha256'];refs.append(image)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    proof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
    result=dict(uids=[UID],uid=UID,sourceSHA256=SHA,relatedUID=OTHER,relatedSourceSHA256=OTHER_SHA,
        sourceFormSHA256=raw['sourceFormSHA256'],worldTrianglesSHA256=raw['worldTrianglesSHA256'],
        currentManifestSHA256=selection['manifestSHA256'],passed=True,identityAccepted=True,reasons=[],proof=proof,
        officialSharedStructureID=1732120,structureIDsByUid=links,currentPrimaryObjectIDs={u:official[cs]['OBJECTID']for u,cs in csuids.items()},
        viewerSnapshotObjectIDs={u:r['source']['building']['objectId']for u,r in rows.items()},
        objectIDVersionNote='Live service OBJECTIDs differ from the pinned viewer/native snapshot. Stable exact CSUID/GeoRef/type/heights bind fresh relation evidence; no claim that live OBJECTIDs equal historic snapshot IDs.',
        rawIdentityVerbatim=raw,resolvedOnlyReasons=sorted(REASONS),currentNativeVersionsReadBack=True,
        imagesActuallyViewed=[dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes()),purpose='Whole unchanged source-pair context only; no terrain/runtime appearance approval.')],
        sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,genericIdentityPolicyChanges=False,
        relatedSourceIdentityApproved=False,currentFormSuppression=False,currentCollisionExemption=False,
        currentTerrainExemption=False,physicalAcceptance=False,visualRuntimeAcceptance=False,
        installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,
        qualification='Exact unchanged carpark root/native/CSUID/GeoRef and complete original cell retained. Its sole other-form overlap is with Academic309823, explicitly linked by current government BuildingStructureID1732120/NT98/91. OSM parent inequality is not a separate government structure. This bounded numeric identity review preserves raw25.846m2overlap and all original parts; no generic overlap waiver, reassignment, suppression, support/collision/terrain exemption, related-source approval or publication. All physical, current-neighbour and real-browser checks remain independent.')
    assert reservations.owns(lease);save(BASE/BATCH/'identity.json',result)
    module('carpark_shared_structure_identity',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-government-shared-structure-bounded-carpark-identity',refs,result)

if __name__=='__main__':main()

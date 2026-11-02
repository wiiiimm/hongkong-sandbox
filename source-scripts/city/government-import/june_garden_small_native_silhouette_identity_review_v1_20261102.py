"""Source-specific joint identity review using both actual original silhouettes.

The coarse podium footprint fills its source mesh's opening. Preserve the raw
footprint-overlap rejection; measure the complete exact-original peer instead.
This decision requires that exact peer in the same installation group. It gives
no placement, collision, terrain, visual-browser or publication approval.
"""
import argparse, sys, uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_four_world_pair_context_v3_20261101 import represented
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

OWN, PEER = 'landsd/264492:0', 'landsd/227380:0'
SOURCES = {OWN:'265d11ddab4f31ffcfcbd2f1826107465335f4bbf69ee8b6544ed08ddafcfb09',
           PEER:'0ec881f882c5f52a34ba7d86f20b25a0903dcfcf8d8935ef949ab20569e99dfa'}
RUNTIME = 'government-xl-tower3-june-garden-four-originals-current-v1-20261102-runtime'
ATTRS = 'government-xl-tower3-june-garden-four-originals-current-v1-20261102-attributes'
IDENT = 'government-xl-tower3-june-garden-four-originals-current-v1-20261102-identity'
SCOPE = 'government-xl-tower3-june-garden-current-model-context-v1-20261102-scope'
VIEWS = 'government-xl-tower3-june-garden-current-model-context-v1-20261102-views'
PRIMARY = 'government-xl-tower3-june-garden-fresh-primary-records-v1-20261102'
PAIR = 'government-xl-tower3-june-garden-small-peer-context-v1-20261102-contacts'
PAIR_VIEWS = 'government-xl-tower3-june-garden-small-peer-views-v1-20261102'
RAW_REASONS = {'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',required=True); p.add_argument('--resources-plan',required=True)
    p.add_argument('--owned',action='store_true'); a = p.parse_args()
    base = ROOT/'docs/astra-city/government-import'; out = base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    pp = (ROOT/a.resources_plan).resolve(); assert pp.is_relative_to(base)
    resources = read(pp)['resources']; assert {'building:'+u for u in SOURCES} <= set(resources)
    lp = HERE/'local'/a.batch/'reservation.json'
    if not a.owned:
        assert not out.exists() and not lp.parent.exists()
        c = reservations.claim('june-garden-exact-peer-identity-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs, pins = [Path(__file__),pp], {}
    def take(batch,name):
        if batch not in pins:
            pins[batch] = authenticate(base/batch)[1]; refs.append(base/batch/'result.json')
        path = base/batch/name; assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take(RUNTIME,'selection.json.gz'); selected = {r['uid']:r for r in selection['rows']}
    attrdoc = take(ATTRS,'attributes.json.gz'); assert attrdoc['startEndAllInputsVerified']
    attrs = {r['uid']:r for r in attrdoc['rows']}; worlds = {}
    for uid, sha in SOURCES.items():
        row = selected[uid]; asset = ROOT/row['candidate']['path']
        assert digest(asset.read_bytes()) == row['sourceSHA256'] == attrs[uid]['sourceSHA256'] == sha
        refs.append(asset); worlds[uid] = represented(attrs[uid],decode_original_world_triangles(asset.read_bytes()))
        proof = take(IDENT,uid.split('/')[1]+'/identity.json')
        assert proof['sourceSHA256'] == sha and proof['originalOwnership']['sourceGraphVerified']
        assert proof['freshCurrentIdentity']['exactObjectAndCSUID'] and proof['exactCurrentComponentRoute']['qualified']
        if uid == OWN:
            raw = proof; assert proof['passed'] is False and set(proof['reasons']) == RAW_REASONS
            assert proof['freshCurrentIdentity']['targetCoveredBySourceProjection'] >= .95
        else:
            assert proof['passed'] is True and not proof['reasons']
    forms = take(SCOPE,OWN.split('/')[1]+'-forms.json.gz')
    assert {r['building']['uid'] for r in forms} == set(SOURCES)
    assert all(r['building'] == selected[r['building']['uid']]['source']['building'] for r in forms)
    scope = take(SCOPE,'summary.json')
    assert all(not r['nearbyNativeActors'] for r in scope['rows'] if r['uid'] in SOURCES)
    primary = take(PRIMARY,'summary.json'); assert not primary['missingRequestedCSUIDs']
    records = {r['attributes']['BuildingCSUID']:r['attributes'] for r in take(PRIMARY,'footprints.json')['features']}
    record_by_uid = {}
    for uid in SOURCES:
        form = selected[uid]['source']['building']; record = records[form['buildingCSUID']]
        assert record['Status'] == 'Active' and record['BuildingID'] == form['buildingId']
        assert record['GeoRefNo'] == selected[uid]['modelId'][1:11] == form['buildingCSUID'][:10]
        assert record['BuildingBlockType'] == form['structureType']
        record_by_uid[uid] = record
    assert record_by_uid[OWN]['BuildingBlockType'] == 'Tower' and record_by_uid[PEER]['BuildingBlockType'] == 'Podium'
    assert record_by_uid[OWN]['BaseHeight'] == record_by_uid[PEER]['TopHeight'] == 7.4
    pair = take(PAIR,'summary.json'); assert pair['uids'] == [PEER,OWN] and pair['sourceSHA256ByUid'] == SOURCES
    assert {r['mode'] for r in pair['rows']} == set(worlds[OWN])
    own = selected[OWN]['source']['building']; polygon = shapely.Polygon(own['rings'][0],own['rings'][1:]); measures = []
    for mode in worlds[OWN]:
        assert reservations.owns(lease)
        projections = {}
        for uid in SOURCES:
            triangles = worlds[uid][mode]; projected = shapely.polygons(triangles[:,:,[0,2]])
            projections[uid] = shapely.union_all(projected[shapely.area(projected)>0])
        capture = next(r for r in pair['rows'] if r['mode'] == mode)
        assert capture['sourceWorldSHA256ByUid'] == {u:digest(worlds[u][mode].astype('<f8').tobytes()) for u in SOURCES}
        assert capture['allPairsExamined'] and capture['sourceFacesOmitted'] == 0 and capture['positiveSurfaceContactPairs'] > 0
        intersection = projections[OWN].intersection(projections[PEER]).area
        # Keep the existing ordinary foreign-silhouette limit, without widening it.
        assert intersection <= 1 and projections[OWN].intersection(polygon).area/polygon.area >= .95
        measures.append(dict(mode=mode,sourceWorldSHA256ByUid=capture['sourceWorldSHA256ByUid'],actualOriginalPeerOverlapM2=intersection,ordinaryForeignLimitM2=1,coarsePodiumOriginalMeshInsideOwnFootprintM2=projections[PEER].intersection(polygon).area,positiveOriginalContactPairs=capture['positiveSurfaceContactPairs']))
    images = []
    views = take(VIEWS,'summary.json'); assert set(views['uids']) == set(SOURCES)
    for row in views['rows']:
        assert row['sourceSHA256'] == SOURCES[row['uid']]
        images.extend(row['images'])
    pairviews = take(PAIR_VIEWS,'summary.json'); assert set(pairviews['uids']) == set(SOURCES)
    images.extend(r['image'] for r in pairviews['exports']); assert len(images) == 7
    for image in images:
        path = ROOT/image['path']; assert digest(path.read_bytes()) == image['sha256']; refs.append(path)
    manifest = ROOT/'3d-viewer/city/data/manifest.json'; assert digest(manifest.read_bytes()) == selection['manifestSHA256']; refs.append(manifest)
    decision = dict(uids=[OWN],sourceSHA256=SOURCES[OWN],identityAccepted=True,sourceIdentityReviewUsedAI=True,sourceIdentityReviewScope='Exact joint original silhouette only',requiredOriginalPeerBindings={PEER:SOURCES[PEER]},requiresSameInstallationGroup=True,rawIdentityVerbatim=raw,rawReasonsReplacedOnly=sorted(RAW_REASONS),measures=measures,inspectedExports=images,sourceGeometryChanges=0,sourcePoseChanges=0,placementReviewed=False,collisionApproved=False,publication=False,installationApproved=False,qualification=__doc__+' Seven actual plan/oblique/contact exports inspected. The complete original podium leaves an opening occupied by the exact matching small original; coarse footprint overlap is not actual native overlap. Active dated CSUID/type/georef/BuildingID and complete four-world geometry are bound. No common legal ownership or structure/permit relation is inferred; the small component has no returned structure relation.')
    save(out/'identity-review.json',decision)
    refs.extend(HERE/n for n in ['original_assembly_four_world_pair_context_v3_20261101.py','exact_packed_world_geometry_20261009.py'])
    assert reservations.owns(lease)
    module('june_garden_native_silhouette_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'reviewed-exact-joint-original-small-component-silhouette-identity',refs,decision)


if __name__ == '__main__': main()

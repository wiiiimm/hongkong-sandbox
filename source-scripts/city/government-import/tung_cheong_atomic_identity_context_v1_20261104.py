"""Measure exact Tung Cheong assembly identity; retain individual match failures.

Diagnostic evidence only. No native UID assignment, acceptance or publication.
"""
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations, connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_ownership import document, graph_reasons
from government_owned_identity import geographic_cell
from georef_projection_coverage import whole_cell_coverage

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-tung-cheong-atomic-identity-context-v1-20261104'
PREP = 'government-xl-tung-cheong-pair-preparation-v1-20261104'
SELECT = 'government-xl-tung-cheong-paired-diagnostic-selection-v1-20261104'
UIDS = ['landsd/53799:0','landsd/223636:0']


def main():
    out = BASE/BATCH
    lp = HERE/'local'/(BATCH+'-control')/'reservation.json'
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(batch, name):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE/batch)
            refs.append(BASE/batch/'result.json')
        p = BASE/batch/name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)
    nomination = take(SELECT, 'summary.json')
    resources = sorted(set(nomination['leaseResources']) | {'native-source:a04c53795d53db1d54dd224b5d4b2b9091855f5b8525f82753a981f88bc08438/B339081144201063C0'})
    if '--owned' not in sys.argv:
        assert not lp.parent.exists()
        claim = reservations.claim('tung-cheong-atomic-context-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    selected = take(PREP+'-runtime','selection.json.gz')
    rows = selected['rows']
    assert [r['uid'] for r in rows] == UIDS
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256'] == nomination['currentManifestSHA256']
    refs.append(manifest)
    primary = take(SELECT,'active-georef-records.json')
    assert not primary.get('exceededTransferLimit') and len(primary['features']) == 2
    allforms, tilehashes = [], {}
    for tile in read(manifest)['tiles']:
        p = ROOT/'3d-viewer'/tile['url']
        tilehashes[tile['url']] = digest(p.read_bytes())
        allforms.extend(read(p)['buildings'])
    assert len(tilehashes) == len(read(manifest)['tiles'])
    raw_identity = take(PREP+'-identity','summary.json')
    assert all(r['passed'] is False for r in raw_identity['rows'])
    context_batch = 'government-xl-tung-cheong-unmatched-four-world-context-v2-20261103'
    contact_context = take(context_batch,'summary.json')
    original_contacts = take(context_batch,'original-pair.json.gz')
    assert original_contacts['allPairsExamined'] and original_contacts['sourceFacesOmitted'] == 0
    assert len(original_contacts['contacts']) == 68
    triangles, accounts, footprints = [], [], []
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for r in rows:
            form, native = r['source']['building'],r['native']
            routed = [f for f in allforms if str(f.get('buildingCSUID') or '')[:10] == r['modelId'][1:11] or f['uid'] == r['uid']]
            assert routed == [form]
            assert form['buildingCSUID'][:10] == r['modelId'][1:11]
            fresh = [f['attributes'] for f in primary['features'] if f['attributes']['GeoRefNo'] == r['modelId'][1:11]]
            assert len(fresh) == 1 and fresh[0]['Status'] == 'Active'
            assert fresh[0]['BuildingCSUID'] == form['buildingCSUID'] and fresh[0]['BuildingID'] == form['buildingId']
            sha, cached = db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone()
            assert sha == native['resultSha'] and next(m for m in cached['models'] if m['modelId']==r['modelId']) == native['model']
            candidates = native['model']['matching']['officialCandidates']
            assert len(candidates) == 1 and candidates[0]['objectId'] == form['objectId'] and candidates[0]['buildingCSUID'] == form['buildingCSUID']
            p = ROOT/r['candidate']['path']
            assert digest(p.read_bytes()) == r['sourceSHA256']
            refs.append(p)
            raw = p.read_bytes()
            assert graph_reasons(document(raw),r['modelId'],r['triangles']) == []
            tri = decode_original_world_triangles(raw)
            assert tri.shape == (r['triangles'],3,3)
            assert np.max(np.abs(np.array([tri.min((0,1)),tri.max((0,1))])-np.asarray(native['model']['worldBounds']))) < .002
            triangles.append(tri)
            footprint = shapely.Polygon(form['rings'][0],form['rings'][1:])
            assert footprint.is_valid and footprint.area > 0
            footprints.append(footprint)
            accounts.append(dict(uid=r['uid'],modelId=r['modelId'],sourceSHA256=r['sourceSHA256'],completeOriginalFaces=len(tri),worldSHA256=digest(tri.astype('<f8').tobytes()),completeNamedGraphVerified=True,uniqueCurrentGeoRef=True,currentProviderObjectId=fresh[0]['OBJECTID'],cachedViewerObjectId=form['objectId'],providerObjectIdExact=fresh[0]['OBJECTID']==form['objectId'],nativeMatching=native['model']['matching'],currentActivePrimaryRecord=fresh[0]))
        low = rows[1]
        assert db.execute('SELECT viewer_uid,source_state FROM astra_modelling.native_model_sizes WHERE cache_key=%s AND model_id=%s',(low['native']['cacheKey'],low['modelId'])).fetchall() == [(None,'source-match-held')]
    assert [a['worldSHA256'] for a in accounts] == contact_context['rows'][0]['sourceWorldSHA256s']
    complete = np.concatenate(triangles)
    projection = shapely.union_all(shapely.polygons(complete[:,:,[0,2]]))
    target = shapely.union_all(footprints)
    assert projection.is_valid and target.is_valid
    excess = projection.difference(target)
    bound = projection.bounds
    foreign = []
    for form in allforms:
        if form['uid'] in UIDS: continue
        poly = shapely.Polygon(form['rings'][0],form['rings'][1:])
        assert poly.is_valid and not poly.is_empty, form['uid']
        a,b,c,d = poly.bounds
        if a>bound[2] or c<bound[0] or b>bound[3] or d<bound[1]: continue
        area = excess.intersection(poly).area
        if area>0: foreign.append(dict(uid=form['uid'],sourceExcessOverlapM2=area))
    # Covers the source and target GeoRef cells as a whole assembly only.
    cells = []
    for r in rows:
        form = r['source']['building']
        cell = geographic_cell(r['modelId'],form['buildingCSUID'],form['structureType'])
        cells.append(dict(uid=r['uid'],bounds=list(cell.bounds),targetUnionCoversWholeCell=bool(target.covers(cell)),sourceUnionCellCoverage=whole_cell_coverage(complete,cell,projection)))
    coverage = projection.intersection(target).area/target.area
    extent = 0
    # This is a vertex diagnostic, not a continuous maximum-distance certificate.
    if not excess.is_empty:
        coords = shapely.get_coordinates(excess)
        extent = float(np.max(shapely.distance(shapely.points(coords),target)))
    result = dict(uids=UIDS,currentManifestSHA256=selected['manifestSHA256'],accounts=accounts,currentTilesScanned=len(tilehashes),currentFormsScanned=len(allforms),completeOriginalFaces=len(complete),sourceUnionProjectionAreaM2=projection.area,targetUnionAreaM2=target.area,targetUnionCoveredByOriginals=coverage,sourceUnionExcessAreaM2=excess.area,sourceUnionExcessMaximumVertexDistanceM=extent,completeProjectionCoveredByTenMetreTargetBuffer=bool(target.buffer(10).covers(projection)),foreignExcessOverlaps=foreign,compoundGeographicCells=cells,rawIndividualIdentity=raw_identity,rawFourWorldPairCounts=contact_context['rows'],completeOriginalPairFiniteContacts=68,sourceGeometryChanges=0,sourcePoseChanges=0,nativeLowViewerUid=None,nativeMatchingRowsChanged=0,sourceAssociationAccepted=False,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
    save(out/'complete-current-tile-hashes.json',tilehashes)
    save(out/'summary.json',result)
    assert reservations.owns(lease) and digest(manifest.read_bytes())==selected['manifestSHA256']
    for url,h in tilehashes.items(): assert digest((ROOT/'3d-viewer'/url).read_bytes())==h
    refs.extend(ROOT/'3d-viewer'/url for url in tilehashes if any(r['source']['tile']==url for r in rows))
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','original_source_ownership.py','government_owned_identity.py','georef_projection_coverage.py'])
    module('tung_cheong_compound_identity_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-atomic-identity-context-no-assignment',list(dict.fromkeys(refs)),result)
    print(dict(coverage=coverage,maximumExtensionM=extent,foreignOverlaps=foreign,cells=cells),flush=True)


if __name__=='__main__': main()

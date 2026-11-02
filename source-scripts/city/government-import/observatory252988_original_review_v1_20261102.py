"""Review the exact unchanged Observatory original and bounded current terrain.

Source-specific lower-wall/underside interpretation only; guarded publication,
live browser checks and independent installed readback remain mandatory.
"""
import sys, uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE = ROOT/'docs/astra-city/government-import'
P = 'government-xl-observatory252988-'; BATCH = P+'original-review-v1-20261102'
UID = 'landsd/252988:0'; SHA = '65a071eb71ff421ba33ea7dc6816887e6b1c460e75c85e606c03e8eb17f32cca'
R = P+'floor-current-checks-v1-20261102'; V = P+'private-browser-v1-20261102'
DOWN = {448,449,467,468,630,631,634,635,638,639,642,643,654,655,656,657}


def main():
    out = BASE/BATCH; lp = HERE/'local'/BATCH/'reservation.json'; assert not out.exists()
    plan = BASE/(P+'floor-checks-v1-20261102-resources.json'); resources = read(plan)['resources']
    if '--owned' not in sys.argv:
        assert not lp.parent.exists()
        c = reservations.claim('observatory-original-review-'+str(uuid.uuid4()), resources, batch=BATCH, ttl=3600); assert c['ok'], c
        return execute_reserved(c['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp); assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    refs, pins = [Path(__file__), plan], {}
    def take(batch, name='summary.json', local=False):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]; refs.append(BASE/batch/'result.json')
        path = (HERE/'local'/batch if local else BASE/batch)/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    source = take(R+'-runtime', 'selection.json.gz')['rows'][0]
    assert source['uid'] == UID and source['sourceSHA256'] == SHA and source['triangles'] == 14128
    identity = take(P+'after-yoho-current-v1-20261102-identity', '252988:0/identity.json')
    assert identity['passed'] and not identity['reasons'] and identity['sourceSHA256'] == SHA
    assert all(identity['proof'][k] for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
    metric_doc = take(R+'-runtime', 'metrics.json'); m = metric_doc['rows'][0]
    assert m['uid'] == UID and m['sourceSHA256'] == SHA and m['sourcePreserved']
    assert m['missingTerrain'] == m['missingDrawnTerrain']['count'] == m['samplerDisagreement']['count'] == 0
    assert m['maxSamplerDelta'] <= .004
    policy = module('observatory_original_policy', HERE/'acceptance-policy.py'); refs.append(HERE/'acceptance-policy.py')
    raw = {k: policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SHA,identityProof=identity['proof']), m, profile) for k, profile in metric_doc['profiles'].items()}
    assert raw and all(v == ['terrain-intersects-source-over-0.5m'] for v in raw.values()), raw
    foundation = take(R+'-foundations'); assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
    assert all(r['triangles'] == r['completeTerrainTriangles'] == 14128 and r['fullyBuriedTriangles'] == 14 and r['fullyBuriedUpwardTriangles'] == 0 for r in foundation['rows'])
    scope = take(P+'current-model-scope-v1-20261102'); assert scope['uids'] == [UID]
    scoped = scope['rows'][0]; assert scoped['sourceSHA256'] == SHA and scoped['currentNativeActorsChecked'] == 7094 and not scoped['nearbyNativeActors'] and scoped['currentFormsWithinTwoMetreRegion'] == 1
    neighbours = take(R+'-neighbours'); assert neighbours['forms'] == 53 and not neighbours['basicFlags']
    assert set(neighbours['requiredNativeUids']) == set(neighbours['nativeResolved']) == {'landsd/118475:0'} and all(r['passed'] for r in neighbours['nativeRows'])
    replacement = take(R+'-binding')['candidate']['replaces']; assert replacement['retainedUids'] == ['landsd/118475:0']
    geometry = take(R+'-runtime', 'runtime-geometry.json.gz', True)['rows'][0]
    ground = np.asarray(geometry['drawnGroundGeometry'], dtype='<f8').reshape(-1,3,3); gsha = digest(ground.tobytes())
    path_summary = take(P+'exposed-grade-paths-v1-20261102'); assert path_summary['sourceSHA256'] == SHA and all(r['allPathsPass'] for r in path_summary['rows'])
    records = []
    for mode in ['original','literal','leftF32','balancedF32']:
        context = take(P+'repaired-below-grade-v1-20261102', mode+'.json.gz')
        rim = take(P+'repaired-canonical-rims-v1-20261102', mode+'.json.gz')
        route = take(P+'exposed-grade-paths-v1-20261102', mode+'.json.gz')
        low = take(R+'-low-faces', {'leftF32':'left','balancedF32':'balanced'}.get(mode,mode)+'.json.gz')
        sha = context['sourceWorldSHA256']; assert route['sourceWorldSHA256'] == rim['sourceWorldSHA256'] == low['sourceWorldSHA256'] == sha
        assert context['completeGroundSHA256'] == route['completeGroundSHA256'] == rim['groundSHA256'] == low['groundSHA256'] == gsha
        assert low['completeSourceFaces'] == 14128
        bad = {r['sourceFace'] for r in low['rows']}; walls = set(context['negativeWallFaces'])
        assert len(walls) == 94 and bad == walls | DOWN and set(context['negativeNonWallFaces']) == DOWN
        assert not context['wallsWithoutSharedEdgeClearCapPath'] and all(r['hasExactSharedEdgeClearCapPath'] for r in context['allWallCapPaths'])
        assert {i for g in context['coplanarDownwardGroups'] for i in g['negativeDownwardFaces']} == DOWN
        assert all(r['absoluteNormalYRatio'] is not None and (r['absoluteNormalYRatio'] < .25 if r['sourceFace'] in walls else r['vertices'] is not None) for r in low['rows'])
        warning_indices = [i for i,s in enumerate(rim['completeOriginalSamples']) if s['low'] and (s['gap'] < -.5 or s['gap'] > 1)]
        assert len(warning_indices) == 124 and route['rawCanonicalWarningIndices'] == warning_indices
        assert len(route['rows']) == 124 and route['allPathsPass']
        assert all(r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight'] and r['riseAboveEndpointsM'] == 0 and r['maximumResidualM'] <= .001 for r in route['rows'])
        assert len(route['acceptedOriginalWallRoots']) == 230
        assert all(r['strictAccepted'] and -.1 <= r['gap'] <= 1 for r in route['acceptedOriginalWallRoots'])
        assert all(set(s['originalIncidentFaces']) <= bad for s in rim['completeOriginalSamples'] if s['gap'] < -.5)
        records.append(dict(mode=mode,sourceWorldSHA256=sha,completeGroundSHA256=gsha,negativeWalls=sorted(walls),negativeDownwardFaces=sorted(DOWN),canonicalWarnings=124,actualExposedWallRoots=230,allCanonicalWarningPathsPass=True,rawRimRangeM=[rim['minimumRimGapM'],rim['maximumRimGapM']]))
    obs_path = BASE/(P+'private-inspection-v1-20261102')/'ROOT-OBSERVATIONS.json'; obs = read(obs_path); refs.append(obs_path)
    assert obs['reviewer'] == 'Codex ROOT' and obs['allEightExportsActuallyOpenedInBoundSheets'] and obs['allSixLowSourcePlotsActuallyOpened']
    observed = {r['path']:r['sha256'] for r in obs['imagesActuallyViewed']}; reports, images, retained_images = [], [], []
    for width in [1280,390]:
        path = BASE/V/str(width)/'staged-browser.json'; report = take(V,str(width)+'/staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]; assert len(views) == 2 and len(report['retainedNativeOwnViews']) == 2
        for v in views:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'] and v['pick'] == v['collision'] == UID and v['sourceSHA256'] == SHA
        for v in views+report['retainedNativeOwnViews']:
            image = path.parent/v['file']; rel = str(image.relative_to(ROOT)); assert digest(image.read_bytes()) == observed[rel]; refs.append(image)
            (images if v in views else retained_images).append(dict(path=rel,sha256=observed[rel]))
        reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    for image in obs['imagesActuallyViewed']:
        path=ROOT/image['path']; assert digest(path.read_bytes()) == image['sha256']; refs.append(path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json'; mh=digest(manifest.read_bytes()); assert mh == scope['currentManifestSHA256'] == identity['exactRouteManifestSHA256']; refs.append(manifest)
    asset=ROOT/source['candidate']['path']; assert digest(asset.read_bytes()) == SHA; refs.append(asset)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},identityAccepted=True,identityProof=identity['proof'],identityProofByUid={UID:identity['proof']},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),currentManifestSHA256=mh,leaseResources=resources,exactTerrainReplacement=replacement,retainedNativeRegression=neighbours,completeCurrentNeighbourChecks=53,completeFourWorldFoundations=True,rawRuntimeMetrics=m,rawPolicyReasonsByProfile=raw,rawCanonicalFailuresPreserved=True,lowerSourceRecords=records,imagesActuallyViewed=images,retainedNativeImagesActuallyViewed=retained_images,allImagesActuallyViewed=obs['imagesActuallyViewed'],browserReports=reports,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=True,publicTerrainWritesPerformed=False,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,interpretation=[
        'Exact object252988/CSUID3601818144T20050430 original identity passes current full-source checks. Full four-world native bounds separate every other installed original; only its own BASIC form occurs within2m of the complete source. Full changed-terrain extent separately retains all53form/native regression obligations.',
        'The remaining110negative source faces comprise94grade-crossing original walls and16downward lower skins, including slight literal plane tilts preserved exactly. All six opposite-perspective diagrams were inspected. These are original perimeter/underside closures; no basement use, legal ownership, structural engineering or fabricated support is inferred. All walls retain exact source paths to ordinary-clear upper faces. All other original facets retain complete ordinary clearance.',
        'Every one of124actual canonical lowest-rim warnings reaches an independently replayed finite upper-ground interface on an exposed original wall in every represented stream, without intercomponent joins, endpoint rise or more than existing1mm incidence residual.230original wall roots per stream meet unchanged[-.1,1]m limits against every overlapping actual ground primitive. The raw negative lowest rim is preserved; actual grade interfaces supply the bounded source-specific ground-contact account, never a blanket relaxed clearance threshold.',
        'Four-world foundation policy passes with14non-upward buried underside faces,0upward and original fraction.000511; no facets removed. The two formerly embedded upward floors11997/11998 are clear after the validated bounded terrain return. All53BASIC and retained118475terrain regressions passed; retained source metadata remains unchanged.',
        'All eight bound desktop/mobile day/night exports inspected, with loading/picking/collision/failure-retry passing. Dark nighttime surfaces and partial occlusion limit facade assessment; no physical-phone FPS claim. Guarded publication, actual live exports and independent old-assets/support/521-source readback remain required.'])
    assert reservations.owns(lease)
    save(out/'ROOT-SOURCE-REVIEW.json',result); save(out/'ROOT-PHYSICAL-REVIEW.json',result); save(out/'summary.json',result)
    module('observatory_original_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-observatory-wall-underside-and-current-terrain-review',list(dict.fromkeys(refs)),result)


if __name__ == '__main__': main()

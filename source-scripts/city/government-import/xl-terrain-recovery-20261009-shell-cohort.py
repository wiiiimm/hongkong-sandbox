"""New closed-shell diagnosis of cached physical evidence, not an unchanged retry.

Historical source/terrain bindings remain explicit. No acceptance or publication
and no assertion that provider provenance authorises an underground component.
"""
import importlib.util
import json
import shutil
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from original_shell_diagnostic_20261009 import shell_context

BATCH = 'xl-terrain-recovery-20261009-shell-cohort'
DOC = ROOT/'docs/astra-city/government-import'/BATCH
SELECTION = HERE/'local/xl-terrain-recovery-20261009/selected.json'
LEASES = [Path('/tmp/xl-terrain-recovery-20261009-hoi-fu-lease.json'),
          Path('/tmp/xl-terrain-recovery-20261009-cohort-lease-v2.json')]


def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}


def main():
    assert not DOC.exists(), 'Fresh diagnostic path required'
    leases = [read(p) for p in LEASES]
    assert all(reservations.owns(r) for r in leases)
    selected = read(SELECTION)
    s = importlib.util.spec_from_file_location('shell_source_context', HERE/'xl-final-script-pass.py')
    module = importlib.util.module_from_spec(s); s.loader.exec_module(module)
    rows = []
    for selected_row in selected['rows']:
        prior = selected_row['foundationSummary']['foundation']
        row = {**selected_row, 'historicalTerrain':True, 'geometryChanges':0,
               'publication':False, 'placementAccepted':False,
               'historicalEvidenceRefs':[ref(ROOT/selected_row[k])
                                         for k in ['historicalFoundation', 'runtimeGeometry']]}
        if not prior['fullyBuriedTriangles']:
            row['classification'] = 'no-fully-buried-faces-in-this-paired-historical-geometry'
            rows.append(row)
            continue
        assert any('building:'+row['uid'] in lease['resources'] for lease in leases)
        geometry = next(r for r in read(ROOT/row['runtimeGeometry'])['rows'] if r['uid'] == row['uid'])
        assert geometry['sourceSHA256'] == row['sourceSHA256']
        position = np.asarray(geometry['position'], dtype=float).reshape(-1,3)
        index = np.asarray(geometry['index'])
        assert np.isfinite(position).all() and index.ndim == 1 and len(index)%3 == 0
        assert np.issubdtype(index.dtype, np.integer) and index.min() >= 0 and index.max() < len(position)
        tri = position[index.reshape(-1,3)]
        ground = np.asarray(geometry['drawnGroundGeometry'], dtype=float).reshape(-1,3,3)
        assert np.isfinite(ground).all() and len(tri) == prior['triangles']
        support_proof_path = (ROOT/row['historicalFoundation']).parent/'installed-support-proof.json'
        if support_proof_path.exists():
            proof = read(support_proof_path)
            assert proof['uid'] == row['uid'] and proof['sourceSHA256'] == row['sourceSHA256']
            inputs_path = support_proof_path.parent/'support-inputs.json'
            source = next(r for r in read(inputs_path)['sources'] if r['uid'] == proof['supportUid'])
            entry = source['candidate']['entry']
            asset = ROOT/source['candidate']['path']
            assert entry['sha256'] == proof['supportSHA256'] == digest(asset.read_bytes())
            decode_local = HERE/'local'/BATCH/'support-decode'/row['uid'].replace('/','-').replace(':','-')
            dest = decode_local/'assets'/(entry['sha256']+'.glb.gz')
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
            module.s.LOCAL = decode_local
            decoder_row = {**source,'modelId':entry['modelId'],'triangles':entry['triangles'],
                           'native':{'model':{'worldBounds':entry['worldBounds']}}}
            support_triangles = module.s.glb_triangles(decoder_row)
            ground = np.concatenate([ground, support_triangles])
            row['compoundOriginalSupport'] = {'uid':proof['supportUid'],
                'sourceSHA256':proof['supportSHA256'], 'triangles':len(support_triangles),
                'evidenceRefs':[ref(p) for p in [support_proof_path,inputs_path,asset]]}
        polygons = shapely.polygons(ground[:,:,[0,2]])
        valid = shapely.area(polygons) > 1e-10
        ground, polygons = ground[valid], polygons[valid]
        points = np.concatenate([tri, tri.mean(axis=1)[:,None,:]], axis=1)
        heights = module.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),
                                                   ground, shapely.STRtree(polygons)).reshape(-1,4)
        gaps = points[:,:,1]-heights
        complete = np.isfinite(heights).all(axis=1)
        buried = complete & (gaps < -.5).all(axis=1)
        cross = np.cross(tri[:,1]-tri[:,0], tri[:,2]-tri[:,0])
        upward = cross[:,1] > .25*np.linalg.norm(cross,axis=1)
        if int(buried.sum()) != prior['fullyBuriedTriangles'] or int((buried & upward).sum()) != prior['fullyBuriedUpwardTriangles']:
            row.update(classification='historical-surface-binding-not-reproduced-no-topology-credit',
                       recomputedBuriedTriangles=int(buried.sum()),
                       recomputedBuriedUpwardTriangles=int((buried & upward).sum()))
            rows.append(row);print(json.dumps({'uid':row['uid'],'bindingMismatch':True}),flush=True)
            continue
        pending = set(int(i) for i in np.flatnonzero(buried)); shells = []
        shell_faces = set()
        while pending:
            seed = min(pending)
            context = shell_context(tri, [seed])
            members = context['componentFaces']
            contained = sorted(pending.intersection(members))
            pending.difference_update(members)
            shell_faces.update(members)
            local_gaps = gaps[members]
            context.update(fullyBuriedFaces=contained,
                           fullyBuriedUpwardFaces=[i for i in contained if upward[i]],
                           completeGroundFaces=int(complete[members].sum()),
                           sourceSamplesBelowGround=int((local_gaps < 0).sum()),
                           sourceSamplesAboveGround=int((local_gaps > 0).sum()),
                           upwardFaceMinimumGapM=float(gaps[[i for i in members if upward[i]]].min())
                             if any(upward[i] for i in members) else None,
                           rawGapRangeM=[float(local_gaps.min()),float(local_gaps.max())])
            shells.append(context)
        outside = [i for i in range(len(tri)) if i not in shell_faces]
        row.update(buriedFaces=np.flatnonzero(buried).tolist(), shells=shells,
                   sourceTriangles=len(tri), completeGroundTriangles=int(complete.sum()),
                   outsideShellMinimumGapM=float(gaps[outside].min()) if outside else None,
                   allBuriedFacesInClosedOutwardShells=all(s['outwardPositiveVolume'] for s in shells),
                   anyFullyBuriedUpwardFace=bool((buried & upward).any()),
                   geometricBelowGradeShellLead=bool(complete.all() and not (buried & upward).any()
                     and all(s['outwardPositiveVolume'] and s['sourceSamplesAboveGround']
                             and s['sourceSamplesBelowGround'] for s in shells)),
                   selfIntersectionCertified=False, belowGradeAuthorisation=False)
        row['classification'] = ('closed-outward-shell-crosses-ground-no-buried-upward-faces'
             if row['geometricBelowGradeShellLead'] else 'additional-foundation-or-topology-failure')
        rows.append(row)
        print(json.dumps({'uid':row['uid'],'buried':int(buried.sum()),
                          'upward':int((buried&upward).sum()),'shells':len(shells),
                          'closedShellLead':row['geometricBelowGradeShellLead'],
                          'outsideMin':row['outsideShellMinimumGapM']}),flush=True)
    assert all(reservations.owns(r) for r in leases)
    result = {'batch':BATCH, 'sourceScope':173, 'pairedHistoricalGeometry':len(rows),
              'nonzeroBuriedGeometry':sum(bool(r['foundationSummary']['foundation']['fullyBuriedTriangles']) for r in rows),
              'geometricBelowGradeShellLeads':sum(bool(r.get('geometricBelowGradeShellLead')) for r in rows),
              'rows':rows, 'unpaired':selected['unpaired'], 'newlyInstalled':0,
              'publication':False, 'aiGeometryModelling':False, 'sourceGeometryChanges':0,
              'evidenceRefs':[ref(p) for p in [Path(__file__), SELECTION,
                HERE/'original_shell_diagnostic_20261009.py', HERE/'test_original_shell_diagnostic_20261009.py']],
              'qualification':'Fresh topology diagnosis of byte-pinned historical runtime geometry. Closed shells do not authorise below-grade acceptance. Original strict failures, every source face, source hash and terrain binding remain visible. No changed source/model review or installation credit.'}
    save(DOC/'diagnostic.json.gz',result)
    print(json.dumps({k:result[k] for k in ['sourceScope','pairedHistoricalGeometry','nonzeroBuriedGeometry','geometricBelowGradeShellLeads','newlyInstalled']}),flush=True)


if __name__ == '__main__':main()

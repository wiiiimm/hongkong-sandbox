"""Rebind the viable original group without repeating unchanged terrain/foundation math.

All old actor extents lie within the refreshed complete podium extent. Every old
drawn terrain face must be an exact member of its current complete terrain, and
the full current regional scope must have no other native or terrain overlap.
Fresh actual-loader attributes independently replay every selected source pose.
"""
import argparse
from copy import deepcopy
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
BATCH = 'government-xl-southside-viable-originals-current-rebind-v2-20261104'
OUT = BASE/BATCH
CAPTURE = BATCH+'-runtime'
ATTRIBUTES = BATCH+'-attributes'
LEASE = HERE/'local'/BATCH/'reservation.json'
CURRENT = 'government-xl-southside-source-bound-current-podium-runtime-v1-20261104'
SCOPE = 'government-xl-southside-six-partition-current-scope-v3-20261104'
OLD = 'government-xl-southside-source-bound-runtime-sequence-v1-20261028'
PODIUM = 'landsd/315025:0'
EXCLUDED = {'landsd/311759:0','landsd/311763:0','landsd/330243:0','landsd/330244:0'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    assert not OUT.exists()
    previous, _ = authenticate(BASE/OLD)
    wanted = set(previous['uids'])-EXCLUDED
    assert len(wanted)==13 and PODIUM in wanted
    if not args.owned:
        assert not LEASE.parent.exists()
        resources = {'building:'+u for u in wanted|EXCLUDED}|{'terrain:city/data/terrain.json'}
        claim = reservations.claim('southside-viable-current-rebind-'+str(uuid.uuid4()), sorted(resources), batch=BATCH, ttl=3600)
        assert claim['ok']
        return execute_reserved(claim['reservation'], LEASE, [sys.executable,__file__,'--owned'])
    lease = read(LEASE)
    assert reservations.owns(lease)
    refs, pins = [Path(__file__)], {}

    def take(batch,path):
        if batch not in pins:
            _,pins[batch] = authenticate(BASE/batch)
            refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    scope = take(SCOPE,BASE/SCOPE/'scope.json')
    forms = take(SCOPE,BASE/SCOPE/'form-obligations.json.gz')
    assert len(forms)==84 and scope['currentNativeActors']==7109
    assert not scope['touchingNativeUids'] and not scope['terrainContacts']
    current = take(CURRENT,HERE/'local'/CURRENT/'runtime-geometry.json.gz')['rows']
    selection = take(CURRENT,BASE/CURRENT/'selection.json.gz')
    metric = take(CURRENT,BASE/CURRENT/'metrics.json')
    assert len(current)==len(selection['rows'])==len(metric['rows'])==1
    current, primary, primary_metric = current[0],selection['rows'][0],metric['rows'][0]
    assert current['uid']==primary['uid']==primary_metric['uid']==PODIUM
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes())==selection['manifestSHA256']
    refs.append(manifest)
    ground = np.asarray(current['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    terrain_faces = {t.tobytes() for t in ground}
    podium_positions = np.asarray(current['position']).reshape(-1,3)[:,[0,2]]
    old_receipt = take(OLD,BASE/OLD/'summary.json')
    rows, geometry, foundations, metrics, bindings = {}, {}, {}, {}, []
    historical_manifests = set()
    module_changes = []
    for batch in old_receipt['actualRendererCohorts']:
        selected = take(batch,BASE/batch/'selection.json.gz')
        old_geometry = {r['uid']:r for r in take(batch,HERE/'local'/batch/'runtime-geometry.json.gz')['rows']}
        old_metrics = take(batch,BASE/batch/'metrics.json')
        historical_manifests.add(selected['manifestSHA256'])
        # Replay the same literal production module closure, not an old helper's
        # current source code. Historical manifest/catalogue receipts stay old.
        production = {p:h for p,h in old_metrics['inputHashes'].items() if p.startswith('3d-viewer/') and p.endswith(('.js','.mjs','.wasm'))}
        current_production = {p:h for p,h in metric['inputHashes'].items() if p.startswith('3d-viewer/') and p.endswith(('.js','.mjs','.wasm'))}
        assert production and current_production
        module_changes += [dict(priorBatch=batch,path=p,historicalSHA256=production.get(p),currentSHA256=current_production.get(p),replacementEvidence='Independent complete current actual-loader positions and indices must exactly equal every saved actor before freezing the rebound capture') for p in sorted(set(production)|set(current_production)) if production.get(p)!=current_production.get(p)]
        for p,h in current_production.items():
            assert digest((ROOT/p).read_bytes())==h
            refs.append(ROOT/p)
        for old_row in selected['rows']:
            uid = old_row['uid']
            if uid not in wanted:
                continue
            g = old_geometry[uid]
            assert g['sourceSHA256']==old_row['sourceSHA256']==old_receipt['originalSourceSHA256ByUid'][uid]
            asset = ROOT/old_row['candidate']['path']
            assert digest(asset.read_bytes())==old_row['sourceSHA256']
            refs.append(asset)
            assert [f for f in forms if f['uid']==uid]==[old_row['source']['building']]
            sourcepath = ROOT/'3d-viewer'/old_row['source']['tile']
            assert [f for f in read(sourcepath)['buildings'] if f['uid']==uid]==[old_row['source']['building']]
            refs.append(sourcepath)
            positions = np.asarray(g['position']).reshape(-1,3)[:,[0,2]]
            assert np.all(positions.min(0)>=podium_positions.min(0)) and np.all(positions.max(0)<=podium_positions.max(0))
            old_ground = np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
            assert all(t.tobytes() in terrain_faces for t in old_ground)
            if uid==PODIUM:
                assert g==current
                current_row = primary
                g = current
                m = primary_metric
                foundation = take(CURRENT,BASE/CURRENT/'315025:0.json')
            else:
                current_row = deepcopy(old_row)
                entry = current_row['candidate']['entry']
                added = {}
                for key,field in [('recordedBaseHeight','baseHeightHKPD'),('recordedTopHeight','topHeightHKPD')]:
                    value = old_row['source']['building'].get(field)
                    if key in entry:
                        assert entry[key]==value
                    else:
                        entry[key]=value
                        added[key]=value
                m = next(r for r in old_metrics['rows'] if r['uid']==uid)
                foundation = take(batch,BASE/batch/(uid.split('/')[1]+'.json'))
                bindings.append(dict(uid=uid,priorBatch=batch,oldDrawnTerrainFaces=len(old_ground),allOldDrawnFacesExactlyPresentInCurrentCompleteTerrain=True,oldWorldAndTerrainSHA256=digest(np.asarray(g['position'],dtype='<f8').tobytes()+np.asarray(g['index'],dtype='<i8').tobytes()+old_ground.tobytes()),addedMissingRecordedSourceFields=added))
            if uid in rows:
                assert rows[uid]==current_row and geometry[uid]==g and foundations[uid]==foundation and metrics[uid]==m
            else:
                rows[uid], geometry[uid], foundations[uid], metrics[uid] = current_row,g,foundation,m
    assert set(rows)==set(geometry)==set(foundations)==set(metrics)==wanted
    runtime = BASE/CAPTURE
    assert not runtime.exists() and not (HERE/'local'/CAPTURE).exists()
    save(runtime/'selection.json.gz',dict(rows=[rows[u] for u in sorted(wanted)],manifestSHA256=selection['manifestSHA256']))
    save(runtime/'terrain-candidates.json',take(CURRENT,BASE/CURRENT/'terrain-candidates.json'))
    # Terrain target metadata stays the completed single-podium proposal. Other
    # original actors are unapproved dependants, never extra ground owners.
    save(HERE/'local'/CAPTURE/'runtime-geometry.json.gz',dict(rows=[geometry[u] for u in sorted(wanted)]))
    for uid in sorted(wanted):
        save(runtime/(uid.split('/')[1]+'.json'),foundations[uid])
    save(runtime/'metrics.json',dict(rows=[metrics[u] for u in sorted(wanted)],inputHashes=metric['inputHashes'],qualification='Exact saved per-actor numeric rows rebound by complete current scene/source/loader/terrain witnesses; twelve actors are not claimed as freshly captured.'))
    save(runtime/'reuse-bindings.json',dict(rows=bindings,currentManifestSHA256=selection['manifestSHA256'],historicalManifestSHA256s=sorted(historical_manifests),currentWholeGroundSHA256=digest(ground.tobytes()),currentWholeGroundFaces=len(ground),excludedOriginalUIDs=sorted(EXCLUDED),retainedBasicApproval=False,identityApproval=False,physicalApproval=False))
    assert reservations.owns(lease)
    summary = dict(uids=sorted(wanted),rows=[dict(uid=u,status='captured',provenance='fresh-current-complete-renderer' if u==PODIUM else 'rebound-saved-complete-arrays-not-a-fresh-capture') for u in sorted(wanted)],currentManifestSHA256=selection['manifestSHA256'],currentDetailedActors=7109,currentScopeForms=84,originals=13,exactSourceGeometryPreserved=True,sourceGeometryChanges=0,installationApproved=False,qualification=__doc__+' The exact current single-podium terrain target descriptor is preserved. The other twelve originals remain unapproved dependants. Four Southland original sources are excluded from the proposed group; their BASIC fallbacks require their own reviewed evidence. No terminal original-source decision is reversed.')
    save(runtime/'summary.json',summary)
    freezer = module('southside_viable_current_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
    # Module changes disallow hash-only reuse. Replay every complete source in
    # the actual current loader and compare full position/index arrays BEFORE
    # freezing the rebound capture. No prior renderer approval transfers.
    attr_doc = BASE/ATTRIBUTES
    assert not attr_doc.exists()
    def ref(path):
        return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    save(attr_doc/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url) for url in read(manifest)['officialModelCatalogues']],evidenceRefs=[ref(runtime/'selection.json.gz')],expectedSourceByUid={u:[rows[u]['sourceSHA256'],rows[u]['triangles']] for u in wanted},rows=[dict(uid=u,entry=rows[u]['candidate']['entry'],building=rows[u]['source']['building'],path=rows[u]['candidate']['path']) for u in sorted(wanted)]))
    attrs_tool = HERE/'selected_original_render_attributes_v1.mjs'
    with (attr_doc/'worker.log').open('w') as log:
        subprocess.run(['node',str(attrs_tool),str((attr_doc/'input.json.gz').relative_to(ROOT)),str((attr_doc/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    attrs = read(attr_doc/'attributes.json.gz')
    assert attrs['startEndAllInputsVerified'] and len(attrs['rows'])==13
    for row in attrs['rows']:
        g = geometry[row['uid']]
        assert row['sourceSHA256']==g['sourceSHA256']
        assert np.array_equal(np.asarray(row['completeOriginalIndex']),np.asarray(g['index']))
        assert np.array_equal(np.asarray(row['completeLiteralWorldPosition']),np.asarray(g['position']))
    attr_refs = [Path(__file__),attrs_tool,runtime/'selection.json.gz']
    for path,sha in attrs['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha
        attr_refs.append(ROOT/path)
    save(attr_doc/'summary.json',dict(uids=sorted(wanted),completeFaces=sum(rows[u]['triangles'] for u in wanted),allCurrentLiteralArraysMatchOldCompleteArrays=True,sourceGeometryChanges=0,installationApproved=False))
    assert reservations.owns(lease)
    freezer.freeze(ATTRIBUTES,'complete-current-source-loader-attributes-independent-old-array-comparison',list(dict.fromkeys(attr_refs)),read(attr_doc/'summary.json'))
    save(runtime/'changed-module-array-replay.json',dict(changes=module_changes,all13CompleteSourcePositionsAndIndicesIndependentlyReplayed=True,oldHashOnlyReuse=False,approvalTransferred=False))
    refs.append(attr_doc/'result.json')
    freezer.freeze(CAPTURE,'current-scene-exact-saved-original-runtime-array-rebinding',list(dict.fromkeys(refs)),summary)
    OUT.mkdir()
    result = dict(uids=sorted(wanted),originals=13,freshCompleteActualLoaderPoses=13,oldCompleteLiteralPositionsAndIndicesExactlyEqual=True,newCurrentWholeGroundCapture=1,reusedSavedActorGeometry=12,excludedOriginalUIDs=sorted(EXCLUDED),installationApproved=False,physicalAccepted=False,sourceGeometryChanges=0,qualification='All13 complete actual-loader literal arrays independently match the rebound saved arrays. Fresh explicit Float32 attributes are available for new support/clearance work. No repeated foundation or terrain construction, original-source terminal reversal, identity/physical/publication approval or changed ground-owner metadata.')
    save(OUT/'summary.json',result)
    refs += [BASE/CAPTURE/'result.json',attrs_tool,attr_doc/'result.json']
    assert reservations.owns(lease)
    freezer.freeze(BATCH,'viable-original-group-exact-current-rebind-and-independent-loader-array-check',list(dict.fromkeys(refs)),result)
    print(dict(originals=13,freshCompletePosesMatched=13,reusedGeometryActors=12,newInstallations=0),flush=True)


if __name__=='__main__':
    main()

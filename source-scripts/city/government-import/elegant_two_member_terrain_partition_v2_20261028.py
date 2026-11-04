"""Private two-node terrain recovery using the unchanged existing pair contract."""
import argparse
import copy
import sys
import traceback
import uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from finite_terrain_two_way_partition_v1_20261028 import partition
from constant_colour_terrain_consolidation_v1 import colours
from float32_coverage import approve_roundoff
sys.path.insert(0, str(HERE.parent/'island-detail-integration'))
import coordinated_native_boundary as pair
from native_terrain_validation import validate_native_mesh

BASE = ROOT/'docs/astra-city/government-import'
PRIOR = BASE/'government-xl-elegant-garden-fourteen-original-expanded-export-v1-20261028'
DOMAIN = BASE/'government-xl-elegant-garden-fourteen-original-retained-domain-v1-20261028'
BATCH = 'government-xl-elegant-garden-fourteen-original-two-member-partition-v1-20261028'
DOC = BASE/BATCH
LOCAL = HERE/'local'/BATCH
LEASE = LOCAL/'reservation.json'


def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))


def owned():
    lease = read(LEASE)
    assert reservations.owns(lease) and not DOC.exists()
    receipt, pins = authenticate(PRIOR)
    domain, dp = authenticate(DOMAIN)
    refs = [Path(__file__), PRIOR/'result.json', DOMAIN/'result.json',
        HERE/'finite_terrain_two_way_partition_v1_20261028.py',
        HERE/'southside_six_strip_partition_diagnostic_v1_20261028.py',
        HERE/'constant_colour_terrain_consolidation_v1.py', HERE/'float32_coverage.py',
        Path(pair.__file__), HERE.parent/'island-detail-integration/native_terrain_validation.py',
        HERE/'coordinated_native_boundary_v1_20261023.py', HERE/'finite_native_boundary_strip_v1_20261023.py']
    for mapping in [pins, dp]:
        for path, sha in mapping.items():
            p = ROOT/path
            assert digest(p.read_bytes()) == sha, path
            refs.append(p)
    master = read(PRIOR/'unapproved-terrain.json')
    lineage = read(PRIOR/'unapproved-lineage.json.gz')
    rootpath = ROOT/'3d-viewer/city/data/terrain.json'
    root = read(rootpath)
    assert master['meta']['parentSha256'] == digest(rootpath.read_bytes())
    assert master['coarseCells'] == domain['coarseCells'] == [457, 449, 462, 452]
    assert len(master['nativeMesh']['index'])//3 == receipt['unapprovedTerrainFaces'] and receipt['reason']=='terrain-runtime-budget'
    assert len(receipt['replacedNativeTerrain']) == 2
    split_col = 460
    split_x = root['meta']['georef']['bE']+split_col*root['cell']-834500
    split_grid = (split_x-pair.bounds(master)[0])/master['cell']
    assert split_grid == int(split_grid)
    split_grid = int(split_grid)
    before_tri = pair.triangles(master)
    pieces, conservation = partition(before_tri, split_x)
    save(DOC/'conservation.json', conservation)
    nodes, members, rows = {}, {}, []
    error = None
    try:
        for name in ['west', 'east']:
            p = copy.deepcopy(master)
            p['id'] = BATCH+'-'+name
            low, high = (0, split_grid) if name == 'west' else (split_grid, master['w']-1)
            for key, value in master.items():
                if isinstance(value, list) and len(value) == master['w']*master['h']:
                    p[key] = [value[r*master['w']+c] for r in range(master['h']) for c in range(low, high+1)]
            p['w'] = high-low+1
            p['meta']['georef'].update(bE=master['meta']['georef']['bE']+low*master['cell'], W=p['w'])
            p['coarseCells'] = [457, 449, 460, 452] if name == 'west' else [460, 449, 462, 452]
            old = [r for r in receipt['replacedNativeTerrain'] if r['coarseCells'][0] == p['coarseCells'][0]]
            assert len(old) == 1
            old = old[0]
            oldpath = ROOT/old['path']
            assert digest(oldpath.read_bytes()) == old['sha256']
            p['meta']['targetUids'] = sorted(set(old['targetUids']) | set(receipt['uids']))
            data = pieces[name]
            tri = data['triangles']
            assert len(tri) <= 25000, 'Unchanged per-member runtime budget exceeded'
            p['nativeMesh']['position'] = tri.reshape(-1).tolist()
            p['nativeMesh']['index'] = list(range(tri.size//3))
            p['nativeMesh'].pop('sourceOverlap', None)
            for key in ['numericalCoverageGap', 'numericalProjectionOverlap', 'coordinatedBoundary']:
                p['nativeMesh']['source'].pop(key, None)
            parent_ids = np.asarray(data['parentFaceIndices'])
            # A cropped grid must preserve actual vertex colour lookup. A newly
            # cut mixed-colour face needs separate interpolation evidence.
            assert np.array_equal(colours(tri, p), colours(tri, master)), 'Cropped colour field changed'
            for piece, original in zip(tri, before_tri[parent_ids]):
                if not np.array_equal(piece, original):
                    original_colours = colours(original, master)
                    assert (original_colours == original_colours[0]).all(), 'Cut mixed-colour face requires separate evidence'
                    assert (colours(piece, p) == original_colours[0]).all(), 'Cut face changed colour'
            gap = shapely.union_all(shapely.polygons(tri[:, :, [0, 2]])).symmetric_difference(shapely.box(*pair.bounds(p))).area
            if gap > 0:
                save(DOC/(name+'-coverage.json'), approve_roundoff(p, pair.bounds(p)))
            unbound = DOC/(name+'-unbound.json')
            save(unbound, p)
            save(DOC/(name+'-lineage.json.gz'), dict(parent=ref(PRIOR/'unapproved-terrain.json'), parentFaceIndices=data['parentFaceIndices']))
            refs.append(unbound)
            nodes[name] = p
            members[name] = dict(before=ref(oldpath), candidate=ref(unbound), canonicalSHA256=pair.canonical_sha(p))
            rows.append(dict(member=name, terrainTriangles=len(tri), coarseCells=p['coarseCells'], targetUids=p['meta']['targetUids'], replaces=old, validatorPassed=False))
        assert set().union(*(set(p['meta']['targetUids']) for p in nodes.values())) == set(master['meta']['targetUids'])
        proofpath = DOC/'pair-proof.json'
        save(proofpath, dict(policy=pair.POLICY, parent=ref(rootpath), members=members, editRegionWKT=lineage['outerWKT']))
        refs.append(proofpath)
        overlap = module('elegant_two_member_overlap', HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py')
        refs.append(Path(overlap.__file__))
        for row in rows:
            name = row['member']
            node = nodes[name]
            node['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=pair.POLICY, proof=ref(proofpath), member=name)
            overlap.DOC = DOC/name
            overlap.overlap_proof(node, [PRIOR/'unapproved-terrain.json', proofpath, *[DOC/(n+'-unbound.json') for n in nodes]])
            validate_native_mesh(node, root)
            row['validatorPassed'] = True
            out = DOC/(name+'-terrain.json')
            save(out, node)
            row['candidate'] = ref(out)
        pair.validate_effective_coordinated_members(list(nodes.values()))
        negative = []
        mutations = dict(missing=[nodes['east']], duplicate=[nodes['west'], nodes['east'], nodes['west']])
        for name in ['geometry', 'targets', 'root', 'marker']:
            changed = copy.deepcopy(nodes['west'])
            if name == 'geometry': changed['nativeMesh']['position'][1] += 1
            if name == 'targets': changed['meta']['targetUids'] = []
            if name == 'root': changed['meta']['parentSha256'] = '0'*64
            if name == 'marker': changed['nativeMesh']['source']['coordinatedBoundary']['member'] = 'east'
            mutations[name] = [changed, nodes['east']]
        for name, values in mutations.items():
            try:
                pair.validate_effective_coordinated_members(values)
            except AssertionError:
                negative.append(name)
            else:
                raise AssertionError('Invalid effective pair accepted: '+name)
        save(DOC/'adversarial-checks.json', dict(rejected=negative))
    except Exception as exc:
        error = dict(errorType=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
        save(DOC/'failure.json', error)
    result = dict(uids=domain['uids'], members=rows, conservation=conservation, error=error,
        status='private-two-member-terrain-validator-passed' if error is None else 'two-member-terrain-investigation',
        sourceSHA256ByUid=receipt['sourceSHA256ByUid'], sourceGeometryChanges=0,
        sharedConstructionTargetsOnBothMembers=True, targetRosterQualification='New construction cohort belongs to the mandatory effective pair; old retained target rosters remain on their original spatial member. This grants no whole-model ownership or support approval.',
        newlyInstalled=0, installationApproved=False, publication=False, scriptExternalAICalls=0,
        qualification='Private spatial partition only. Existing finite pair/outer root boundary, coverage/overlap and 25000-face limits unchanged. Retains full old extents/targets and parent-face lineage. No source identity, physical, current-neighbour, browser or installation approval.')
    save(DOC/'summary.json', result)
    assert reservations.owns(lease)
    module('elegant_two_member_partition_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'private-original-terrain-two-member-partition', list(dict.fromkeys(refs)), result)
    print(dict(status=result['status'], members=[(r['member'], r['terrainTriangles'], r['validatorPassed']) for r in rows], error=error), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--owned', action='store_true')
    a = p.parse_args()
    if a.owned:
        return owned()
    assert not DOC.exists() and not LOCAL.exists()
    domain, _ = authenticate(DOMAIN)
    claim = reservations.claim('elegant-two-member-partition-'+str(uuid.uuid4()), domain['resources'], batch=BATCH, ttl=3600)
    assert claim['ok']
    execute_reserved(claim['reservation'], LEASE, [sys.executable, __file__, '--owned'])


if __name__ == '__main__':
    main()

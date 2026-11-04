"""Validate three new coastal terrain patches using frozen original-TIN faces.

No original model edits, tolerance changes, scene writes or installation.
"""
import copy
import traceback
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from unchanged_low_parent_lineage_v1_20261029 import qualify
import three_member_native_boundary_v1_20261027 as chain

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-depot120104-three-member-surface-v1-20261029'
CONSTRUCTION = 'government-xl-depot120104-land-inset-construction-v3-20261029'
PLAN = 'government-xl-depot120104-exact-land-domains-v1-20261029'
PARENT = 'government-xl-depot120104-terrain-sequence-v1-20261029-120104-0-inset'
LOW = 'government-xl-depot120104-exact-low-lineage-v1-20261029'
UID = 'landsd/120104:0'


def main():
    out, local = BASE / BATCH, HERE / 'local' / BATCH
    assert not out.exists() and not local.exists()
    refs, pins = [Path(__file__)], {}

    def ref(path):
        return dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes()))

    def take(name, path):
        if name not in pins:
            pins[name] = authenticate(BASE / name)[1]
            refs.append(BASE / name / 'result.json')
        assert digest(path.read_bytes()) == pins[name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    plan = take(PLAN, BASE / PLAN / 'summary.json')
    summary = take(CONSTRUCTION, BASE / CONSTRUCTION / 'summary.json')
    lineage = take(CONSTRUCTION, BASE / CONSTRUCTION / 'global-lineage.json.gz')
    captured = take(PARENT, HERE / 'local' / PARENT / 'parent.json')
    baseline = np.asarray(captured['triangles'])
    output = np.asarray(take(CONSTRUCTION, HERE / 'local' / CONSTRUCTION / 'global-triangles.json.gz')['triangles'])
    low = take(LOW, BASE / LOW / 'summary.json')
    assert qualify(baseline, output, lineage) == low['proof']
    assert low['exactActualLowFacetPreservationPassed'] is True
    assert plan['sourceSHA256'] == summary['sourceSHA256'] == low['sourceSHA256']
    for name, sha in captured['inputHashes'].items():
        assert digest((ROOT / name).read_bytes()) == sha
        refs.append(ROOT / name)
    rootpath = ROOT / '3d-viewer/city/data/terrain.json'
    root = read(rootpath)
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == plan['currentManifestSHA256']
    refs.extend([rootpath, manifestpath])
    # These are new root children. Never treat an existing patch as an implicit
    # replacement or cut a retained native patch through its interior.
    rectangles = [shapely.box(*m['bounds']) for m in plan['members']]
    for item in read(manifestpath).get('terrainPatches', []):
        path = ROOT / '3d-viewer' / (item['url'] if isinstance(item, dict) else item)
        node = read(path)
        if node.get('nativeMesh') and node['meta'].get('parentTerrain') == 'city/data/terrain.json':
            assert all(shapely.box(*chain.legacy.bounds(node)).intersection(p).area == 0 for p in rectangles), 'Existing native patch needs explicit retained obligations'
            refs.append(path)
    out.mkdir()
    local.mkdir(parents=True)
    builder = module('depot_coastal_template', HERE / 'validated_parent_roundoff_template_v2.py')
    members, candidates = {}, {}
    result = dict(uids=[UID], sourceSHA256ByUid={UID: summary['sourceSHA256']},
                  members=[], newTerrainMembers=True, replacedNativeTerrain=[],
                  installationApproved=False, publication=False,
                  sourceGeometryChanges=0, lowParentPreservation=ref(BASE / LOW / 'summary.json'))
    try:
        for item in plan['members']:
            i, name = item['member'], 'coast-' + str(item['member'])
            before_faces = baseline[item['parentFaceIds']]
            directory = out / (name + '-template-overlap')
            directory.mkdir()
            template = builder.make_patch(dict(cells=item['coarseCells'], uids=[UID]), root,
                before_faces, [], parent_sha256=digest(rootpath.read_bytes()),
                allow_native_below_clamp=bool((before_faces[:, :, 1].min(1) < 1.2).any()),
                declare_float32_roundoff=True, overlap_evidence_dir=directory,
                overlap_sources=[HERE / 'local' / PARENT / 'parent.json', Path(__file__)])
            template['id'] += '-' + name
            template['nativeMesh'].pop('sourceOverlap', None)
            template['nativeMesh']['source'].pop('numericalCoverageGap', None)
            template['nativeMesh']['position'] = before_faces.reshape(-1).tolist()
            template['nativeMesh']['index'] = list(range(before_faces.size // 3))
            beforepath = local / (name + '-before.json')
            # This body contains exact captured parent facets, not the template's
            # transition tessellation. Check that body under ordinary validators.
            overlap = module('depot_before_overlap_' + name, HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
            overlap.DOC = out / (name + '-before-overlap')
            overlap.DOC.mkdir()
            overlap.overlap_proof(template, [HERE / 'local' / PARENT / 'parent.json', Path(__file__)])
            builder.validate_patch(template, root)
            save(beforepath, template)
            memberrow = next(r for r in summary['members'] if r['member'] == i)
            path = ROOT / memberrow['path']
            assert digest(path.read_bytes()) == memberrow['sha256']
            part = read(path)
            refs.append(path)
            faces = np.asarray(part['triangles'])
            assert np.array_equal(faces, output[part['outputFaceIds']])
            assert len(faces) <= 25000
            candidate = copy.deepcopy(template)
            candidate['nativeMesh'].pop('sourceOverlap', None)
            candidate['nativeMesh']['position'] = faces.reshape(-1).tolist()
            candidate['nativeMesh']['index'] = list(range(faces.size // 3))
            candidate['nativeMesh']['source']['boundedOriginalInset'] = dict(
                coreWKT=lineage['coreWKT'], outerWKT=lineage['outerWKT'],
                policy='Frozen global original-TIN lower inset and affine return; partitioned by parent-face lineage without geometry refitting.')
            candidate['nativeMesh']['source']['exactLowParentPreservation'] = ref(BASE / LOW / 'summary.json')
            candidate['meta']['source']['nativeSources'] = lineage['sourceRefs']
            unbound = local / (name + '-unbound.json')
            save(unbound, candidate)
            refs.extend([beforepath, unbound])
            candidates[name] = candidate
            members[name] = dict(before=ref(beforepath), candidate=ref(unbound), canonicalSHA256=chain.legacy.canonical_sha(candidate))
        outer = shapely.from_wkt(lineage['outerWKT'])
        pairs = []
        for i, edge in enumerate(plan['sharedEdges']):
            line = shapely.from_wkt(edge['sharedEdgeWKT'])
            names = ['coast-' + str(edge[k]) for k in ['left', 'right']]
            region = outer.intersection(line.buffer(1, cap_style='flat'))
            domain = shapely.union_all([rectangles[edge[k]] for k in ['left', 'right']])
            assert region.is_valid and region.area > 0 and domain.covers(region) and region.distance(domain.boundary) > 0
            path = out / ('pair-' + str(i) + '.json')
            save(path, dict(policy=chain.legacy.POLICY, parent=ref(rootpath), members={name: members[name] for name in names}, editRegionWKT=region.wkt))
            refs.append(path)
            pairs.append(ref(path))
        proofpath = out / 'three-member-proof.json'
        save(proofpath, dict(policy=chain.POLICY, parent=ref(rootpath), members=members, pairs=pairs))
        refs.append(proofpath)
        validated = []
        with chain.private_validator():
            for name, original in candidates.items():
                node = copy.deepcopy(original)
                node['nativeMesh']['source']['coordinatedBoundary'] = dict(policy=chain.POLICY, proof=ref(proofpath), member=name)
                overlap = module('depot_final_overlap_' + name, HERE / 'sham_shui_po_pool_shared_terrain_v2_20261016.py')
                overlap.DOC = out / (name + '-overlap')
                overlap.DOC.mkdir()
                overlap.overlap_proof(node, [ROOT / members[name]['candidate']['path'], proofpath, Path(__file__)])
                assert node['nativeMesh']['position'] == original['nativeMesh']['position'] and node['nativeMesh']['index'] == original['nativeMesh']['index']
                builder.validate_patch(node, root)
                path = local / (name + '-candidate.json')
                save(path, node)
                refs.append(path)
                result['members'].append(dict(member=name, candidate=ref(path), surfaceValidated=True, newTerrainMember=True))
                validated.append(node)
                print('Validated new coastal member', name, flush=True)
            chain.validate_effective_coordinated_members(validated)
        result.update(status='private-three-member-chain-surface-validator-passed', allEffectiveMembersRequired=True, currentManifest=ref(manifestpath))
    except Exception as error:
        result.update(status='private-three-member-surface-investigation', reason=str(error), errorType=type(error).__name__)
        save(out / 'failure.json', dict(errorType=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
    assert digest(manifestpath.read_bytes()) == plan['currentManifestSHA256']
    refs.extend(HERE / name for name in ['validated_parent_roundoff_template_v2.py', 'sham_shui_po_pool_shared_terrain_v2_20261016.py', 'three_member_native_boundary_v1_20261027.py', 'unchanged_low_parent_lineage_v1_20261029.py'])
    refs.extend(chain.INTEGRATION / name for name in ['coordinated_native_boundary.py', 'native_terrain_validation.py', 'publish.py'])
    save(out / 'summary.json', result)
    module('depot_coastal_surface_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'private-new-coastal-three-member-surface-validation', refs, result)
    print(dict(status=result['status'], reason=result.get('reason')), flush=True)


if __name__ == '__main__':
    main()

"""Fresh whole-cell identity for an exact component missed by cached shape matching.

Keep raw native matches and all source/current spatial/physical guards. Only empty
shape-filtered official/viewer match lists may be replaced by the existing exact
GeoRef/type/CSUID/ObjectID route across all current forms. Nonempty conflicting or
ambiguous matches are never replaced. This is identity, not placement approval.
"""
from copy import deepcopy
from component_type_resolution import resolve
import government_georef_cell_identity as original

POLICY = 'original-government-routed-full-georef-cell-identity-v1'


def routed_proof(proof, row, sources):
    proof = deepcopy(proof)
    route = resolve(row['native']['model'], sources)
    reasons = list(proof['reasons'])
    replaced = []
    matching = row['native']['model']['matching']
    # Require one original authoritative record; never disambiguate raw records
    # here or invent a shape match. This bounded route covers empty proxy lists.
    qualified = (route['qualified'] and route['uid'] == row['uid']
                 and route['source'] == row['source']
                 and len(matching.get('officialCandidates', [])) == 1)
    if not qualified:
        reasons.append('fresh-exact-component-route-not-unique-or-differs')
    else:
        for key in ('officialMatches', 'viewerMatches'):
            reason = 'unique-' + key
            if matching.get(key) == [] and reason in reasons:
                reasons.remove(reason)
                replaced.append(reason)
    passed = not reasons
    proof.update(policy=POLICY, passed=passed, reasons=sorted(set(reasons)),
                 rawNativeIdentityReasons=deepcopy(proof['originalOwnership']['reasons']),
                 emptyCachedShapeMatchesReplaced=sorted(replaced),
                 exactCurrentComponentRoute=route,
                 proof={'exactObjectId': passed, 'exactBuildingCSUID': passed,
                        'uniqueViewerMatch': passed, 'identityAccepted': passed},
                 roofAreaRatioReplacedByPositiveIdentity=passed,
                 qualification='Identity only: exact unique original official record and fresh whole-map GeoRef/type/CSUID/ObjectID routing replace only empty cached shape matches. Raw native failures, original graph/bytes/pose, whole coordinate cell and every current coverage/extent/unrelated-form guard remain. All physical/runtime/browser/publication gates remain required.')
    return proof


def verify(raw, row, context, triangles, *, current_identity, sources):
    return routed_proof(original.verify(raw, row, context, triangles,
                        current_identity=current_identity), row, sources)


def verify_files(row, context, local):
    from run import ROOT, read, digest
    manifest_path = ROOT / '3d-viewer/city/data/manifest.json'
    manifest_sha = digest(manifest_path.read_bytes())
    sources = []
    tiles = {}
    prefix = row['modelId'][1:11]
    for tile in read(manifest_path)['tiles']:
        path = ROOT / '3d-viewer' / tile['url']
        raw = path.read_bytes()
        forms = [b for b in __import__('json').loads(raw)['buildings']
                 if str(b.get('buildingCSUID') or '')[:10] == prefix]
        if forms:
            tiles[tile['url']] = digest(raw)
            sources.extend({'building': b, 'tile': tile['url'], 'tileSHA256': digest(raw)} for b in forms)
    proof = routed_proof(original.verify_files(row, context, local), row, sources)
    assert digest(manifest_path.read_bytes()) == manifest_sha
    for tile, sha in tiles.items():
        assert digest((ROOT / '3d-viewer' / tile).read_bytes()) == sha
    proof['exactRouteTileHashes'] = tiles
    proof['exactRouteManifestSHA256'] = manifest_sha
    return proof

"""Expose unchanged Dragon podium/BASIC interfaces; diagnostics, never approval."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

PREFIX = 'government-xl-dragon-after-podium323546-'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    batch = PREFIX + 'foreign-interface-views-v1-20261026'
    out = base / batch
    assert not out.exists()
    refs = [Path(__file__)]; pins = {}

    def take(suffix, name):
        folder = base / (PREFIX + suffix + '-20261026')
        if folder.name not in pins:
            pins[folder.name] = authenticate(folder)[1]
            refs.append(folder / 'result.json')
        path = folder / name
        assert digest(path.read_bytes()) == pins[folder.name][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    selection = take('ground-v1', 'selection.json.gz')
    foreign = take('foreign-v1', 'summary.json')
    basic = take('foreign-v1', 'basic.json')
    meshes = {r['uid']: np.asarray(r['position']).reshape(-1, 3)[np.asarray(r['index']).reshape(-1, 3)] for r in basic['rows']}
    row = next(r for r in selection['rows'] if r['uid'] == 'landsd/232428:0')
    path = ROOT / row['candidate']['path']
    assert digest(path.read_bytes()) == row['sourceSHA256']
    refs.append(path); source = decode_original_world_triangles(path.read_bytes())
    assert len(source) == 316
    summary = take('private-diagnostic-v2', 'summary.json')
    assert summary['allBrowserDiagnosticsPassed'] and not summary['installationApproved']
    images = []
    for width in [1280, 390]:
        report = take('private-diagnostic-v2', str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        for uid in ['232428', '226794']:
            for time in ['1500', '2200']:
                image = base / (PREFIX + 'private-diagnostic-v2-20261026') / str(width) / f'staged-landsd-{uid}-0-{width}-{time}-canvas.png'
                assert digest(image.read_bytes()) == pins[PREFIX + 'private-diagnostic-v2-20261026'][str(image.relative_to(ROOT))]
                refs.append(image)
                images.append(dict(path=str(image.relative_to(ROOT)), sha256=digest(image.read_bytes()), actuallyOpenedByROOT=True))
    out.mkdir(); results = []
    for pair in foreign['rows']:
        if pair['uid'] != row['uid']:
            continue
        mode = next(r for r in pair['modes'] if r['mode'] == 'original')
        if not mode['positiveContactPairs']:
            continue
        other = pair['foreignUid']; target = meshes[other]
        raw = take('foreign-v1', '232428:0--' + other.split('/')[1] + '--original.json.gz')
        contacts = raw['contacts']
        positive = [c for c in contacts if c['sourcePrimitiveDimensionA'] == c['sourcePrimitiveDimensionB'] == 2 and c['dimension'] > 0]
        assert len(positive) == mode['positiveContactPairs']
        points = [np.asarray([[float(Fraction(z)) for z in p] for p in c['exactPoints']]) for c in contacts]
        joined = np.concatenate(points); lo, hi = joined.min(0), joined.max(0)
        # Whole source and whole BASIC actor: no silent triangle exclusion.
        lower = np.minimum(source.min((0, 1)), target.min((0, 1))) - 1
        upper = np.maximum(source.max((0, 1)), target.max((0, 1))) + 1
        center = (lower + upper) / 2
        def transform(t):
            return (np.asarray(t) - center)[..., [0, 2, 1]]
        bounds = transform(np.array([lower, upper]))
        fig = plt.figure(figsize=(16, 7), layout='constrained')
        for j, angle in enumerate([35, 215]):
            ax = fig.add_subplot(1, 3, j + 1, projection='3d')
            for tri, color in [(source, '#d89d43'), (target, '#93abb9')]:
                ax.add_collection3d(Poly3DCollection(transform(tri), facecolors=color, edgecolor='#52616b', linewidth=.2, alpha=.65))
            lines = [transform(p) for p in points if len(p) > 1]
            if lines:
                ax.add_collection3d(Line3DCollection(lines, colors='#ce2424', linewidths=2))
            ax.set(xlim=bounds[:, 0], ylim=bounds[:, 1], zlim=bounds[:, 2], xlabel='east offset m', ylabel='viewer Z offset m', zlabel='height offset m')
            ax.set_box_aspect(bounds[1] - bounds[0]); ax.view_init(elev=22, azim=angle)
        ax = fig.add_subplot(1, 3, 3)
        for tri, color in [(source, '#d89d43'), (target, '#93abb9')]:
            for f in transform(tri):
                ax.fill(f[:, 0], f[:, 1], color=color, alpha=.12, linewidth=.2, edgecolor='#52616b')
        for points_ in points:
            p = transform(points_); ax.plot(p[:, 0], p[:, 1], color='#ce2424', linewidth=1.5)
        ax.set(aspect='equal', xlabel='east offset m', ylabel='viewer Z offset m')
        is_fallback = other == 'landsd/226794:0'
        fig.suptitle('Original podium 232428 (gold) / BASIC ' + other + ' (blue)\nEvery exact contact red; complete meshes. ' + ('Proposed tower FALLBACK, not original-pair clearance.' if is_fallback else 'External BASIC interface; no ownership or suppression inferred.'))
        image = out / ('232428--' + other.split('/')[1].replace(':', '-') + '.png')
        fig.savefig(image, dpi=120); plt.close(fig); refs.append(image)
        roles = Counter()
        for c in positive:
            a = source[c['sourceFaceA']]; b = target[c['sourceFaceB']]
            def normal_role(t):
                n = np.cross(t[1] - t[0], t[2] - t[0]); size = np.linalg.norm(n)
                return 'degenerate' if size == 0 else ('horizontal' if abs(n[1]) / size > .999999 else 'wall-or-slope')
            roles[normal_role(a) + '/' + normal_role(b)] += 1
        results.append(dict(uid=row['uid'], foreignUid=other, proposedTowerFallbackOnly=is_fallback, completeSourceFaces=len(source), completeBasicFaces=len(target), positiveContactPairs=len(positive), allFiniteContactPairs=len(contacts), contactBounds=[lo.tolist(), hi.tolist()], geometricNormalRoles=dict(roles), allFourWorldRawModeSummaries=pair['modes'], image=str(image.relative_to(ROOT))))
    assert len(results) == 6 and sum(not r['proposedTowerFallbackOnly'] for r in results) == 5
    result = dict(uids=['landsd/226794:0', row['uid']], rows=results, browserV2ImagesActuallyOpened=images, browserDiagnosticsPassed=True, visualAcceptance=False, identityAccepted=False, physicalAcceptance=False, installationApproved=False, newlyInstalled=0, sourceGeometryChanges=0, aiGeometryModelling=False, scriptExternalAICalls=0, qualification='Complete original podium versus complete current BASIC meshes and every exact finite contact. Normal directions are geometric diagnostics, not architectural roles or ownership. Five external interfaces plus the proposed tower BASIC fallback remain explicit. Source-only diagrams must be opened separately; they do not establish original-pair clearance or approval. All eight V2 browser exports were actually opened by ROOT; podium lower interfaces remain obscured and mobile podium own views retain tower fallback during recovery. Final joint report confirms both originals active; no joint image is claimed.')
    save(out / 'summary.json', result)
    refs.append(HERE / 'exact_packed_world_geometry_20261009.py')
    module('dragon_interface_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch, 'original-podium-complete-basic-interface-views-and-browser-observations', refs, result)
    print(dict(interfaces=len(results), external=5, installationApproved=False), flush=True)


if __name__ == '__main__':
    main()

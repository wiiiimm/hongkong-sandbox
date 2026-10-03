"""Persist full-extent terrain and exact neighboring support evidence; no publication."""
from run import ROOT, HERE, read, save, digest

BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC = BASE / 'beverly-hill-pair-terrain-diagnostic-20260928'
LOCAL = HERE / 'local/government-xl-beverly-hill-pair-checks-20260928'


def run():
    old = read(BASE / 'beverly-hill-block-a-terrain-diagnostic-20260927/held.json')
    support = read(DOC / 'support-foundation.json')['foundation']
    assert support['completeTerrainTriangles'] == support['triangles'] == 4712
    probe_path = BASE / 'beverly-hill-neighbour-support-probe-20260928.json'
    probes = read(probe_path)['rows']
    assert len(probes) == 4 and all(r['within05'] == r['interfaceSamples'] for r in probes)
    for name in ('metrics.json', 'validation.json', 'neighbour-checks.json', 'native-neighbour-checks.json'):
        save(DOC / ('pair-' + name), read(LOCAL / name))
    options_path = BASE / 'beverly-hill-terrain-options-20260929.json'
    options = read(options_path)
    assert options['buriedUpwardEvenWithPointwiseLowerSurface'] == 111
    result = {**old,
        'parentTerrainMaskCannotResolveBuriedUpwardTriangles': 111,
        'detailedHold': 'full-podium-terrain-burial-and-neighbour-ground-changes-unresolved',
        'podiumTerrainTrianglesChecked': support['completeTerrainTriangles'],
        'podiumBuriedUpwardTriangles': support['fullyBuriedUpwardTriangles'],
        'podiumBuriedAreaFraction': support['fullyBuriedAreaFraction'],
        'installedNeighboursWithExactPodiumContact': [r['uid'] for r in probes],
        'installedNeighbourInterfaceVertices': sum(r['interfaceSamples'] for r in probes),
        'maximumNeighbourSupportDistanceM': max(r['maximumDistance'] for r in probes),
        'blockedNeighbourUids': read(DOC / 'checks.json')['blockedNeighbourUids'],
        'blockedNativeNeighbourUids': read(DOC / 'checks.json')['blockedNativeNeighbourUids'],
        'nativeNeighbourQualification': 'Existing validator considers installed supports only. Separate hash-verified original-mesh probe confirms all 190 lower interface vertices of the four installed towers contact the staged podium. This is diagnostic evidence, not installation acceptance.',
        'nextWork': 'Parent-terrain masking is ruled out for all 111 buried upward faces. Investigate source revisions or exact component metadata to establish whether these faces are legitimate below-ground structure; do not lower terrain or alter geometry without source evidence. Preserve neighbor contact probes for later guarded staged-support validation.',
        'evidence': old['evidence'] + [
            {'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}
            for p in [DOC / 'result.json', DOC / 'support-foundation.json', DOC / 'checks.json',
                      BASE / 'beverly-hill-pair-foundation-20260928.json', probe_path, options_path,
                      *(DOC / ('pair-' + name) for name in ('metrics.json','validation.json','neighbour-checks.json','native-neighbour-checks.json'))]]}
    save(DOC / 'held.json', result)
    print({'uid': result['uid'], 'completePodiumTriangles': support['triangles'],
           'buriedUpward': support['fullyBuriedUpwardTriangles'], 'supportedInstalledNeighbours': len(probes)})


if __name__ == '__main__':
    run()

"""Freeze final masked Citywalk 2 gates for unchanged-source browser staging."""
import subprocess
from run import ROOT, HERE, read, save

BASE = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
ORIGINAL = BASE / 'citywalk2-terrain-diagnostic-20260929'
DOC = BASE / 'citywalk2-mask-final-20260929'
LOCAL = HERE / 'local/government-xl-citywalk2-mask-20260929/citywalk2'
CANDIDATES = HERE / 'local/government-xl-citywalk2-terrain-20260929/candidates'

def run():
    masked = read(BASE / 'citywalk2-mask-eval-20260929.json')['rows'][0]
    assert not masked['remainingBlockedUids'] and masked['sourcePreserved']
    foundation = read(BASE / 'citywalk2-mask-foundation-20260929.json')['rows'][0]
    assert foundation['strictFoundationAccepted']
    for command in ([ 'node', str(HERE.parent / 'building-batch/validate_candidates.mjs'),
        '--candidates', str(CANDIDATES.relative_to(ROOT)), '--source-forms', str((CANDIDATES/'source-forms.json').relative_to(ROOT)),
        '--terrain-candidates', str((LOCAL/'terrain-candidates.json').relative_to(ROOT)), '--out', str((LOCAL/'validation.json').relative_to(ROOT))],
        ['node', str(HERE/'check-native-neighbours.mjs'), str(LOCAL.relative_to(ROOT))+'/']):
        subprocess.run(command, cwd=ROOT, check=True)
    for name in ('metrics','validation','neighbour-checks','native-neighbour-checks'):
        save(DOC/(name+'.json'),read(LOCAL/(name+'.json')))
    save(DOC/'identity-resolution.json',read(ORIGINAL/'identity-resolution.json'))
    save(DOC/'foundation.json',foundation)
    save(DOC/'result.json', {**read(ORIGINAL/'result.json'),
        'patchPath':masked['candidatePatch']['path'],'patchSHA256':masked['candidatePatch']['sha256']})
    metric=read(DOC/'metrics.json')['rows'][0]
    native=read(DOC/'native-neighbour-checks.json')
    validation=read(DOC/'validation.json')['results'][0]
    checks={'uid':'landsd/305615:0','sourcePreserved':metric['sourcePreserved'],
        'missingTerrainSamples':metric['missingTerrain'],'maxSamplerDeltaM':metric['maxSamplerDelta'],
        'blockedNeighbourUids':masked['remainingBlockedUids'],
        'blockedNativeNeighbourUids':sorted(set(native['blocked'])-set(native['resolved'])),
        'runtimeConcerns':validation.get('concerns',[]),'aiCalls':0,'modelGeometryChanges':0,'publication':False}
    save(DOC/'checks.json',checks)
    assert checks['runtimeConcerns']==[] and not checks['blockedNativeNeighbourUids']
    print(checks,flush=True)

if __name__=='__main__':run()

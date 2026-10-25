"""Verify every failed installation destination restored; no model rejection."""
from pathlib import Path
from urllib.request import urlopen
from run import ROOT, HERE, read, save, digest
from original_install_rollback_readback_v1_20261024 import verify
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    prefix = 'government-xl-dragon-after-podium323546-three-'
    old = base / (prefix + 'original-installed-v1-20261026')
    out = base / (prefix + 'install-rollback-v1-20261026'); assert not out.exists()
    failure = read(old / 'failure-recovery.json'); history = read(old / 'historical-input-context.json')
    restored = verify(ROOT, failure, history); assert len(restored) == 10
    assert not (old / 'result.json').exists() and not (old / 'installed-acceptance.json').exists()
    command = read(old / 'command-003.json')
    assert command['exitCode'] != 0 and 'Timeout 300000ms exceeded' in command['stderr']
    assert 'live 1280 landsd/232428:0 selecting' in command['stdout']
    mobile = read(old / 'viewport-390/live-browser.json'); assert mobile['passed'] and not mobile['errors']
    # Root observed connection refusal after terminal failure, then restarted
    # only the private4177 static server. This is a fresh health witness.
    with urlopen('http://127.0.0.1:4177/city/data/tiles/1_0.json', timeout=15) as response:
        raw = response.read(); assert response.status == 200
    tile = ROOT / '3d-viewer/city/data/tiles/1_0.json'; assert digest(raw) == digest(tile.read_bytes())
    refs = [Path(__file__), HERE / 'original_install_rollback_readback_v1_20261024.py', tile]
    refs.extend(p for p in old.rglob('*') if p.is_file())
    refs.extend(ROOT / r['savedHistoricalBytes']['path'] for r in history['mutableCurrentByteSnapshots'])
    refs.extend(ROOT / r['path'] for r in restored if r['restoredSHA256'] is not None)
    result = dict(uids=['landsd/226794:0','landsd/232428:0','landsd/95231:0'],
        allMutableDestinationsIndependentlyRestored=True, destinations=restored, mobileLivePassed=True,
        desktopLivePassed=False, observedFailure='Desktop BASIC-cache completion wait timed out after the private4177 HTTP server stopped. ROOT observed connection refused after terminal failure; no source-model failure is inferred.',
        privateServerRestarted=True, shared4176Restarted=False, privateTileHTTPStatus=200, privateTileSHA256=digest(raw),
        currentXLInstalled=383, currentXLUnfinished=138, currentDetailedActors=6962, newlyInstalled=0,
        sourceGeometryChanges=0, aiGeometryModelling=False, permanentRejection=False,
        retry='Separate installVersion v2, identical source qualification and browser predicates. Predecessor rollback must pass the unchanged installer guard.')
    save(out / 'summary.json', result)
    module('dragon_rollback_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name, 'uncredited-original-install-full-rollback-readback-and-private-server-recovery', refs, result)


if __name__ == '__main__':
    main()

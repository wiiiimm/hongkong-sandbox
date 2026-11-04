"""Use each authenticated private viewport's cameras with the existing installer.

Publication, leases, rollback, ledger and all old-actor guards stay in the original
installer/publisher. Only the tested per-viewport capture directions are selected.
"""
from pathlib import Path
from copy import deepcopy
import independent_model_only_live_install_v1_20261024 as impl

ORIGINAL_INSTALLER = Path(impl.__file__).resolve()
THIS = Path(__file__).resolve()
original_load = impl.load
original_browser_config = impl.browser_config


def browser_config(width, focused=False):
    config = original_browser_config(width, focused=focused)
    path = impl.stage.PREVIOUS / f'browser-config-{width}.json'
    receipt = impl.read(impl.guard.BROWSER / 'result.json')
    ref = impl.ref(path)
    assert ref in receipt['evidenceRefs']
    tested = impl.read(path)
    assert tested['viewportWidths'] == [width]
    assert tested['browserUids'] == config['browserUids']
    assert tested.get('nativeSupportUidsByModel') == config.get('nativeSupportUidsByModel')
    directions = tested['captureDirectionByModel']
    assert set(directions) == set(impl.stage.SOURCES)
    config['captureDirectionByModel'] = deepcopy(directions)
    retained_directions = tested.get('retainedCaptureDirectionByModel', {})
    assert set(retained_directions) <= set(config.get('additionalRetainedUids', []))
    config['retainedCaptureDirectionByModel'] = deepcopy(retained_directions)
    return config


def load(previous):
    values = list(original_load(previous))
    extra = [impl.ref(ORIGINAL_INSTALLER), impl.ref(THIS)]
    for width in [390, 1280]:
        extra.append(impl.ref(impl.stage.PREVIOUS / f'browser-config-{width}.json'))
    values[-1] = impl.distinct_refs([*values[-1], *extra])
    return tuple(values)


impl.browser_config = browser_config
impl.load = load
impl.BROWSER = impl.HERE / 'ronsdale_three_live_browser_v13_20261025.mjs'
impl.FOCUSED = impl.BROWSER
# The managed child must enter this same adapter. Keep the original implementation
# explicitly pinned above instead of losing its code provenance to this override.
impl.__file__ = str(THIS)

if __name__ == '__main__':
    impl.main()

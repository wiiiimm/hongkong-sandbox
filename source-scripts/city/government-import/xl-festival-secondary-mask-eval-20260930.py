"""Evaluate parent-ground preservation under the flagged neighbor footprints."""
import importlib.util
from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location('festival-secondary_mask', HERE / 'xl-shared-neighbour-mask-eval.py')
mask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mask)

if __name__ == '__main__':
    doc = mask.BASE / 'festival-secondary-terrain-diagnostic-20260930'
    result = read(doc / 'result.json')
    blocked = sorted({uid for row in read(doc / 'neighbour-checks.json')['patches'] for uid in row['blockedBy']})
    assert blocked and 'landsd/104302:0' not in blocked
    mask.LOCAL = HERE / 'local/government-xl-festival-secondary-mask-20260930'
    mask.SOURCE = mask.LOCAL / 'input.json'
    save(mask.SOURCE, {'rows': [{'uid': 'landsd/104302:0', 'site': 'festival-secondary',
        'candidatePatch': {'path': result['patchPath'], 'sha256': result['patchSHA256']},
        'sharedFootprintUids': [{'uid': uid} for uid in blocked]}]})
    mask.DIAGNOSTIC_DIRS = {'festival-secondary': doc}
    mask.SOURCE_ASSET_DIRS = {'festival-secondary': HERE / 'local/government-xl-festival-secondary-terrain-20260930/candidates'}
    mask.OUTPUT = mask.BASE / 'festival-secondary-mask-eval-20260930.json'
    mask.run()

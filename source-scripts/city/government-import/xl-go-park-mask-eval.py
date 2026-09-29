"""Evaluate parent-ground preservation under GO PARK's three same-parent towers."""
import importlib.util
from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location('go_park_mask', HERE / 'xl-shared-neighbour-mask-eval.py')
mask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mask)

if __name__ == '__main__':
    doc = mask.BASE / 'go-park-terrain-diagnostic-20260929'
    result = read(doc / 'result.json')
    blocked = sorted({uid for row in read(doc / 'neighbour-checks.json')['patches'] for uid in row['blockedBy']})
    assert blocked == ['landsd/323150:0', 'landsd/325612:0', 'landsd/325613:0']
    mask.LOCAL = HERE / 'local/government-xl-go-park-mask-20260929'
    mask.SOURCE = mask.LOCAL / 'input.json'
    save(mask.SOURCE, {'rows': [{'uid': 'landsd/318499:0', 'site': 'go-park',
        'candidatePatch': {'path': result['patchPath'], 'sha256': result['patchSHA256']},
        'sharedFootprintUids': [{'uid': uid} for uid in blocked]}]})
    mask.DIAGNOSTIC_DIRS = {'go-park': doc}
    mask.SOURCE_ASSET_DIRS = {'go-park': HERE / 'local/government-xl-go-park-terrain-20260929/candidates'}
    mask.OUTPUT = mask.BASE / 'go-park-mask-eval-20260929.json'
    mask.run()

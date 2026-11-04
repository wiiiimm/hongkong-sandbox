"""Evaluate parent-ground preservation under Harbourview Horizon's neighbor footprint."""
import importlib.util
from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location('harbourview_horizon_mask', HERE / 'xl-shared-neighbour-mask-eval.py')
mask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mask)

if __name__ == '__main__':
    doc = mask.BASE / 'harbourview-horizon-terrain-diagnostic-20260929'
    result = read(doc / 'result.json')
    blocked = sorted({uid for row in read(doc / 'neighbour-checks.json')['patches'] for uid in row['blockedBy']})
    assert blocked == ['landsd/257058:0', 'landsd/257059:0', 'landsd/259577:0']
    mask.LOCAL = HERE / 'local/government-xl-harbourview-horizon-mask-20260929'
    mask.SOURCE = mask.LOCAL / 'input.json'
    save(mask.SOURCE, {'rows': [{'uid': 'landsd/237402:0', 'site': 'harbourview-horizon',
        'candidatePatch': {'path': result['patchPath'], 'sha256': result['patchSHA256']},
        'sharedFootprintUids': [{'uid': uid} for uid in blocked]}]})
    mask.DIAGNOSTIC_DIRS = {'harbourview-horizon': doc}
    mask.SOURCE_ASSET_DIRS = {'harbourview-horizon': HERE / 'local/government-xl-harbourview-horizon-terrain-20260929/candidates'}
    mask.OUTPUT = mask.BASE / 'harbourview-horizon-mask-eval-20260929.json'
    mask.run()

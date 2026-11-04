"""Evaluate parent-ground preservation under the flagged neighbor footprints."""
import importlib.util
from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location('parkview_block9_mask', HERE / 'xl-shared-neighbour-mask-eval.py')
mask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mask)

if __name__ == '__main__':
    doc = mask.BASE / 'parkview-block9-terrain-diagnostic-20260929'
    result = read(doc / 'result.json')
    blocked = sorted({uid for row in read(doc / 'neighbour-checks.json')['patches'] for uid in row['blockedBy']})
    assert blocked and 'landsd/255439:0' not in blocked
    mask.LOCAL = HERE / 'local/government-xl-parkview-block9-mask-20260929'
    mask.SOURCE = mask.LOCAL / 'input.json'
    save(mask.SOURCE, {'rows': [{'uid': 'landsd/255439:0', 'site': 'parkview-block9',
        'candidatePatch': {'path': result['patchPath'], 'sha256': result['patchSHA256']},
        'sharedFootprintUids': [{'uid': uid} for uid in blocked]}]})
    mask.DIAGNOSTIC_DIRS = {'parkview-block9': doc}
    mask.SOURCE_ASSET_DIRS = {'parkview-block9': HERE / 'local/government-xl-parkview-block9-terrain-20260929/candidates'}
    mask.OUTPUT = mask.BASE / 'parkview-block9-mask-eval-20260929.json'
    mask.run()

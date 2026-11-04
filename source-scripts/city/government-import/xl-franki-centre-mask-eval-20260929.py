"""Evaluate parent-ground preservation under Franki Centre's neighbor footprint."""
import importlib.util
from run import ROOT, HERE, read, save

spec = importlib.util.spec_from_file_location('franki_centre_mask', HERE / 'xl-shared-neighbour-mask-eval.py')
mask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mask)

if __name__ == '__main__':
    doc = mask.BASE / 'franki-centre-terrain-diagnostic-20260929'
    result = read(doc / 'result.json')
    blocked = sorted({uid for row in read(doc / 'neighbour-checks.json')['patches'] for uid in row['blockedBy']})
    assert blocked == ['landsd/91695:0']
    mask.LOCAL = HERE / 'local/government-xl-franki-centre-mask-20260929'
    mask.SOURCE = mask.LOCAL / 'input.json'
    save(mask.SOURCE, {'rows': [{'uid': 'landsd/111822:0', 'site': 'franki-centre',
        'candidatePatch': {'path': result['patchPath'], 'sha256': result['patchSHA256']},
        'sharedFootprintUids': [{'uid': uid} for uid in blocked]}]})
    mask.DIAGNOSTIC_DIRS = {'franki-centre': doc}
    mask.SOURCE_ASSET_DIRS = {'franki-centre': HERE / 'local/government-xl-franki-centre-terrain-20260929/candidates'}
    mask.OUTPUT = mask.BASE / 'franki-centre-mask-eval-20260929.json'
    mask.run()

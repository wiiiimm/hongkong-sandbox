"""Check every original Citywalk 2 face against the neighbor-preserving candidate."""
import importlib.util
from run import HERE

spec = importlib.util.spec_from_file_location('citywalk2_mask_foundation', HERE / 'xl-masked-foundation-eval.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.SOURCE = audit.BASE / 'citywalk2-mask-eval-20260929.json'
    audit.OUT = audit.BASE / 'citywalk2-mask-foundation-20260929.json'
    audit.DIAGNOSTIC_DIRS = {'citywalk2': audit.BASE / 'citywalk2-terrain-diagnostic-20260929'}
    audit.run()

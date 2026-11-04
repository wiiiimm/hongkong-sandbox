"""Check every original Festival Walk secondary source face against the neighbor-preserving candidate."""
import importlib.util
from run import HERE

spec = importlib.util.spec_from_file_location('festival-secondary_mask_foundation', HERE / 'xl-masked-foundation-eval.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.SOURCE = audit.BASE / 'festival-secondary-mask-eval-20260930.json'
    audit.OUT = audit.BASE / 'festival-secondary-mask-foundation-20260930.json'
    audit.DIAGNOSTIC_DIRS = {'festival-secondary': audit.BASE / 'festival-secondary-terrain-diagnostic-20260930'}
    audit.run()

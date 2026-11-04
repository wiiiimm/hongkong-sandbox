"""Check every original Parkview Block 9 face against the neighbor-preserving candidate."""
import importlib.util
from run import HERE

spec = importlib.util.spec_from_file_location('parkview_block9_mask_foundation', HERE / 'xl-masked-foundation-eval.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.SOURCE = audit.BASE / 'parkview-block9-mask-eval-20260929.json'
    audit.OUT = audit.BASE / 'parkview-block9-mask-foundation-20260929.json'
    audit.DIAGNOSTIC_DIRS = {'parkview-block9': audit.BASE / 'parkview-block9-terrain-diagnostic-20260929'}
    audit.run()

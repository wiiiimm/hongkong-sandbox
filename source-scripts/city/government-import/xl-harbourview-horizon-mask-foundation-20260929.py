"""Check every original Harbourview Horizon face against the neighbor-preserving candidate."""
import importlib.util
from run import HERE

spec = importlib.util.spec_from_file_location('harbourview_horizon_mask_foundation', HERE / 'xl-masked-foundation-eval.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.SOURCE = audit.BASE / 'harbourview-horizon-mask-eval-20260929.json'
    audit.OUT = audit.BASE / 'harbourview-horizon-mask-foundation-20260929.json'
    audit.DIAGNOSTIC_DIRS = {'harbourview-horizon': audit.BASE / 'harbourview-horizon-terrain-diagnostic-20260929'}
    audit.run()

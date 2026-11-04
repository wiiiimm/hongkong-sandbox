"""Check every original GO PARK face against the neighbor-preserving candidate."""
import importlib.util
from run import HERE

spec = importlib.util.spec_from_file_location('go_park_mask_foundation', HERE / 'xl-masked-foundation-eval.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.SOURCE = audit.BASE / 'go-park-mask-eval-20260929.json'
    audit.OUT = audit.BASE / 'go-park-mask-foundation-20260929.json'
    audit.DIAGNOSTIC_DIRS = {'go-park': audit.BASE / 'go-park-terrain-diagnostic-20260929'}
    audit.run()

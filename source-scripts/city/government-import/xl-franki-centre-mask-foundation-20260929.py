"""Check every original Franki Centre face against the neighbor-preserving candidate."""
import importlib.util
from run import HERE

spec = importlib.util.spec_from_file_location('franki_centre_mask_foundation', HERE / 'xl-masked-foundation-eval.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

if __name__ == '__main__':
    audit.SOURCE = audit.BASE / 'franki-centre-mask-eval-20260929.json'
    audit.OUT = audit.BASE / 'franki-centre-mask-foundation-20260929.json'
    audit.DIAGNOSTIC_DIRS = {'franki-centre': audit.BASE / 'franki-centre-terrain-diagnostic-20260929'}
    audit.run()

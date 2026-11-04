"""Refresh GO PARK diagnostics against the current manifest without altering old evidence."""
import importlib.util
import sys
from run import ROOT, HERE, read, save, digest

spec = importlib.util.spec_from_file_location('go_park_refresh', HERE / 'xl-yoho-mall-ii-acceptance.py')
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

if __name__ == '__main__':
    base = ROOT / 'docs/astra-city/government-import/government-xl-remaining-20260923'
    old = base / 'go-park-terrain-diagnostic-20260925'
    checks.DOC = base / 'go-park-terrain-diagnostic-20260929'
    result = read(old / 'result.json')
    assert digest((ROOT / result['patchPath']).read_bytes()) == result['patchSHA256']
    save(checks.DOC / 'result.json', result)
    save(checks.DOC / 'native-overlap.json', read(old / 'native-overlap.json'))
    checks.LOCAL = HERE / 'local/government-xl-go-park-terrain-20260929'
    checks.STAGE = checks.LOCAL / 'candidates'
    sys.argv = [__file__, 'prepare']
    checks.run()

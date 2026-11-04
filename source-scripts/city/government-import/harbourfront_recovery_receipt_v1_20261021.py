"""Freeze independently verified completed interrupted-install recovery."""
from pathlib import Path
from run import ROOT,HERE,read,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-install-recovery-v1-20261021';DOC=BASE/BATCH;OLD=BASE/'government-xl-harbourfront-tower-original-installed-v1-20261021'
history=read(OLD/'historical-input-context.json');summary=read(DOC/'summary.json')
for r in history['mutableCurrentByteSnapshots']:assert digest((ROOT/r['originalPath']).read_bytes())==r['originalSHA256']
for p in summary['removedExactNewDestinations']:assert not (ROOT/p).exists()
assert summary['allPublicDestinationsRestored'] and not (OLD/'result.json').exists()
summary['uids']=['landsd/118230:0']
module('recovery_receipt',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'interrupted-publication-exact-recovery',[Path(__file__),HERE/'harbourfront_install_recovery_v1_20261021.py',OLD/'historical-input-context.json',OLD/'acceptance.json'],summary)

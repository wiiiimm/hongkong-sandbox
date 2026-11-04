"""Exact completed current Heya inputs; local immutable fixture, no DB/acceptance."""
from run import ROOT,read
BASE=ROOT/'docs/astra-city/government-import'
FOLDERS={
'actual':'government-xl-heya-aqua-184286-184285-current-actual-ground-capture-v1-20261011',
'source':'government-xl-heya-aqua-184286-installed-podium-complete-source-census-v1-20261011',
'interfaces':'government-xl-heya-aqua-184286-184285-current-four-world-interfaces-grade-v1-20261011',
'finite':'government-xl-heya-aqua-184286-184285-complete-four-stream-current-finite-v1-20261011',
'visual':'government-xl-heya-aqua-58-original-terminal-visual-placement-proposal-v1-20261011',
'account':'government-xl-heya-aqua-current-main-family-exposed-root-account-v1-20261011',
'identity':'government-xl-heya-aqua-184286-current-owned-identity-v1-20261011',
'physical':'government-xl-heya-aqua-184286-unchanged-current-ordinary-physical-v1-20261011',
'foreign':'government-xl-heya-aqua-184286-complete-current12-foreign-basic-context-v1-20261011',
'native':'government-xl-heya-aqua-complete-current6648-native-exclusions-v1-20261011',
'inventory':'government-xl-complete-current-native-actual-position-matrix-bounds-v3-20261011',
'context':'government-xl-heya-aqua-complete85-coupled-source-join-context-v1-20261011'}
def load():
 def file(key,name):return read(BASE/FOLDERS[key]/name)
 return dict(actual=file('actual','complete-two-actor-four-stream-ground-inputs.json.gz')['rows'],
 source=file('source','diagnostic.json.gz'),interfaces=file('interfaces','diagnostic.json.gz'),finite=file('finite','diagnostic.json.gz'),
 visual=file('visual','proposal.json.gz'),account=file('account','proposal.json.gz'),identity=file('identity','identity.json'),physical=file('physical','diagnostic.json.gz'),foreign=file('foreign','diagnostic.json.gz'),native=file('native','diagnostic.json.gz'),
 native_uids=[r['uid']for r in file('inventory','inventory.json.gz')['rows']],context=file('context','context.json'),
 current_forms=file('actual','capture-inputs.json.gz')['completeCurrentForms'],
 provider_sources=read(BASE/'government-xl-georef-sparkle-heya-original-supports-20261008/support-inputs.json')['sources'])

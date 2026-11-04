"""Freeze private runtime evidence, without source/publication acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import authenticate
BATCH='government-xl-ocean-four-atomic-lifecycle-browser-v1-20261027'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local/government-xl-ocean-four-atomic-lifecycle-stage-v1-20261027'
def main():
 report=read(DOC/'report.json');assert report['passed'] is True and report['pageErrors']==[]
 for flag in ['physicalAcceptance','installationApproved','publication','performanceAcceptance']:assert report[flag] is False
 uids=['landsd/156599:0','landsd/210743:0','landsd/231469:0','landsd/234188:0']
 cases=report['cases'];assert len(cases)==5 and cases[0]['width']==1280 and cases[0]['failedUid'] is None
 assert sorted(c['failedUid'] for c in cases[1:])==uids and all(c['width']==390 for c in cases[1:])
 old='government-xl-after-waterfront-ocean-four-corrected-private-diagnostic-v4-20261027'
 olddoc=ROOT/'docs/astra-city/government-import'/old;_,pins=authenticate(olddoc)
 oldlocal=HERE/'local'/old;cat=read(LOCAL/'catalogue.json');previous=read(oldlocal/'catalogue.json')
 assert digest((oldlocal/'catalogue.json').read_bytes())==pins[str((oldlocal/'catalogue.json').relative_to(ROOT))]
 assert sorted(m['uid'] for m in cat['models'])==uids
 for m in cat['models']:
  expected=next(p for p in previous['models'] if p['uid']==m['uid']);assert {k:v for k,v in m.items() if k!='activationGroup'}==expected and m['activationGroup']==uids
  asset=LOCAL/m['asset'];assert digest(asset.read_bytes())==m['sha256'] and asset.stat().st_size==m['bytes']
 assert (LOCAL/'source-forms.json').read_bytes()==(oldlocal/'source-forms.json').read_bytes()
 assert digest((oldlocal/'source-forms.json').read_bytes())==pins[str((oldlocal/'source-forms.json').relative_to(ROOT))]
 cfg=read(LOCAL/'config.json');assert cfg['diagnosticOnly'] and cfg['publication'] is False
 for terrain in cfg['terrain']:assert digest((ROOT/terrain['source']).read_bytes())==pins[terrain['source']]
 for c in cases:
  assert c['baseOnlyRestoredCompleteGroup'] and c['completeGroupEvicted'] and c['testWarmRetentionDisabledForEviction']
  if c['failedUid']:assert c['failureKeptAllBasics']
  assert c['audit']['violations']==[] and c['audit']['frames']>0
  transitions=c['audit']['transitions'];assert transitions[0]['active']==[] and transitions[-1]['active']==[]
  assert any(t['active']==uids for t in transitions) and all(t['active'] in [[],uids] for t in transitions)
  assert sorted(s['uid'] for s in c['sources'])==uids
  for s in c['sources']:
   m=next(m for m in cat['models'] if m['uid']==s['uid']);assert s['active'] and s['sha256']==m['sha256'] and s['triangles']==m['triangles']
 observation=read(DOC/'ROOT-OBSERVATIONS.json');assert observation['physicalAcceptance'] is False and observation['performanceAcceptance'] is False
 for image in observation['imagesActuallyViewed']:assert digest((ROOT/image['path']).read_bytes())==image['sha256']
 log=Path('/tmp/astra-activation-groups-tests.log').read_bytes();assert 'ℹ tests 440' in log.decode() and 'ℹ pass 440' in log.decode() and 'ℹ fail 0' in log.decode();(DOC/'city-node-tests.log').write_bytes(log)
 paths=[Path(__file__),HERE/'model_atomic_lifecycle_browser_v1_20261027.mjs',olddoc/'result.json',ROOT/'docs/astra-city/MODEL-ACTIVATION-GROUPS.md']
 paths.extend(p for p in LOCAL.rglob('*') if p.is_file());paths.extend(ROOT/t['source'] for t in cfg['terrain'])
 for name in ['model-activation-groups.js','model-group-lifecycle.js','model-support.js','official-models.js','streaming.js','app.js','official-model-assets.js','tile-cache.js','model-byte-cache.js','model-variants.js']:
  paths.append(ROOT/'3d-viewer/city'/name)
 paths.extend((ROOT/'3d-viewer/city/tests').glob('model-*group*.test.js'));paths.append(ROOT/'3d-viewer/city/tests/model-activation-transaction.test.js')
 module('atomic_lifecycle_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-source-atomic-runtime-lifecycle-diagnostic-v1',paths,dict(uids=uids,browserCases=5,nodeTestsPassed=440,physicalAcceptance=False,performanceAcceptance=False,sourceReviewApproval=False,scriptFullAcceptancePassed=False,aiCodeWork=True,nextStep='Complete source-specific grade/interface and current retained-model visual review, then guarded qualification and publication. This runtime diagnostic grants no installation approval.'))
if __name__=='__main__':main()

"""Use the unchanged coarse-bottom resolver; preserve all other actual failures."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-olympian-one-global-bottom-resolution-v1-20261018'
DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-olympian-one-pair-physical-v2-20261018'
PAIR=BASE/'government-xl-olympian-one-original-assembly-v1-20261018'
BIND=BASE/'government-xl-olympian-one-wall-binding-v1-20261018'
def main():
 assert not DOC.exists()
 pins={};refs=[Path(__file__),HERE/'terrain_diagnostic_resolution.py']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYSICAL,PAIR,BIND]:
   receipt=read(folder/'result.json')
   assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
   refs.append(folder/'result.json')
   for e in receipt['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256']
    pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 uid='landsd/72354:0'
 metric=next(r for r in read(PAIR/'metrics.json')['rows']if r['uid']==uid)
 validation=next(r for r in read(PHYSICAL/'validation.json')['results']if r['uid']==uid)
 bindings=read(BIND/'exact-source-face-bindings.json.gz')['bindings'];resolutions=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  foundation=read(PHYSICAL/f'72354:0-{mode}-foundation.json')
  binding=next(b for b in bindings if b['uid']==uid and b['mode']==mode)
  assert foundation['worldSHA256']==binding['wholeWorldSHA256']
  assert metric['sourceSHA256']==binding['sourceSHA256']
  result=resolve_global_bottom_warning(validation,metric,{**foundation,'sourceSHA256':binding['sourceSHA256']})
  assert result['resolved']==['sampled-terrain-above-model-bottom'] and not result['remaining']
  resolutions.append(dict(mode=mode,worldSHA256=foundation['worldSHA256'],**result))
 raw=read(PHYSICAL/'summary.json')['rawReasons'];removed='validation:'+uid+':sampled-terrain-above-model-bottom'
 assert removed in raw
 summary=dict(uids=[uid,'landsd/256927:0'],rawReasons=raw,resolvedByExistingGlobalBottomPolicy=[removed],remainingReasons=[r for r in raw if r!=removed],fourModeResolutions=resolutions,installationApproved=False,publicationApproved=False,sourceGeometryChanges=0)
 save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_global_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-coarse-bottom-policy-four-mode-resolution',list(dict.fromkeys(refs)),summary)
 print('Podium coarse warning resolved in four modes; three tower reasons remain.',flush=True)
if __name__=='__main__':main()

"""Record exact canonical warning outcomes; no approval or threshold changes."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from terrain_diagnostic_resolution import resolve_global_bottom_warning
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-ifc-mall-loader-warning-audit-v1-20261019'
DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 names=['loader-v1','unchanged-four-mode-foundations-v1','original-column-review-v2']
 pins={};refs=[Path(__file__),HERE/'terrain_diagnostic_resolution.py']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in names:
   path=BASE/('government-xl-ifc-mall-'+name+'-20261019')/'result.json';r=read(path)
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(path)
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256']
    pins[e['path']]=e['sha256']
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
 validation=read(BASE/'government-xl-ifc-mall-loader-v1-20261019/validation.json')
 for path,h in validation['hashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 assert validation['models']==validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0
 review=read(BASE/'government-xl-ifc-mall-original-column-review-v2-20261019/ROOT-GRADE-REVIEW.json')
 metric=review['rawNumericMetrics'];outputs=[]
 for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
  f=read(BASE/'government-xl-ifc-mall-unchanged-four-mode-foundations-v1-20261019'/('64856:0-'+mode+'.json'))
  result=resolve_global_bottom_warning(validation['results'][0],metric,f)
  assert result['resolved']==[] and result['remaining']==['sampled-terrain-above-model-bottom']
  assert f['strictFoundationAccepted'] and f['foundation']['triangles']==36305 and f['foundation']['fullyBuriedTriangles']==0
  outputs.append(dict(mode=mode,canonicalResult=result,foundation=f['foundation']))
 save(DOC/'audit.json',dict(uid=metric['uid'],sourceSHA256=metric['sourceSHA256'],modes=outputs,canonicalWarningResolved=False,sourceSpecificReviewExists=review['sourceSpecificGradeInterpretationAccepted'],explanation='Canonical resolver requires minSurfaceGap >= -0.5m; actual is -0.6992303011939107m. Preserve failure. Existing exact-column interpretation is separate from numeric acceptance. Publication qualification must explicitly account for both; this audit grants no installation approval.',publication=False,installationApproved=False))
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h,path
 refs.extend(ROOT/path for path in pins)
 module('ifc_warning_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'canonical-loader-warning-audit',refs,dict(uids=[metric['uid']],canonicalWarningResolved=False,installationApproved=False))
if __name__=='__main__':main()

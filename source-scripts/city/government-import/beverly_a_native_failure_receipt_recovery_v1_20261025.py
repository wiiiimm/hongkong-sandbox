"""Recover a completed exact browser report after receipt-only schema failure; no rerun."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-beverly-a-after-fe-native-failure-recovered-v1-20261025'
OLD='government-xl-beverly-a-after-fe-native-failure-v2-20261025'
def main():
 out=BASE/BATCH;assert not out.exists();inp=HERE/'local'/OLD/'input.json';data=read(inp);refs=[Path(__file__),inp,BASE/OLD/'summary.json',BASE/OLD/'browser.json',BASE/OLD/'worker.log']
 for r in data['evidenceRefs']:
  p=ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'];refs.append(p)
 raw=read(BASE/OLD/'browser.json');old=read(BASE/OLD/'summary.json')
 assert raw['passed']and old['passed']and old['browserExitCode']==0 and not raw['errors']
 assert raw['uid']==data['uid']==old['uid']and raw['parentUid']==data['parent']['uid']==old['parentUid']
 assert raw['sourceSHA256']==data['sourceSHA256']and raw['parentSHA256']==data['parent']['entry']['sha256']
 assert raw['deniedParentRequests']>0 and raw['successfulParentRequests']>0
 w=raw['failed'];assert w['parentFailed']and not w['active']and not w['parentActive']and w['basicLoaded']and not w['basicHidden']and not w['detailSuppressed']and w['basicGroupVisible']and w['ownFeaturePresent']
 assert w['dependencies']==[dict(uid=data['parent']['uid'],state='installed',buildingCSUID=data['parent']['entry']['buildingCSUID'],sha256=raw['parentSHA256'])]
 assert all(r['active']and r['visible']for r in raw['recovered'])
 assert [r['sourceSHA256']for r in raw['recovered']]==[raw['sourceSHA256'],raw['parentSHA256']]
 assert [r['triangles']for r in raw['recovered']]==[15248,11825]
 summary={**old,'uids':[raw['uid']],'originalReport':dict(path=str((BASE/OLD/'browser.json').relative_to(ROOT)),sha256=digest((BASE/OLD/'browser.json').read_bytes())),'receiptRecoveryOnly':True,'browserRerun':False,'qualification':old['qualification']+' Original browser completed successfully; the freezer rejected the missing uids reporting field before enqueue. Exact original producer/config/input/report bytes retained, not rewritten.'}
 save(out/'browser.json',raw);save(out/'summary.json',summary)
 module('native_failure_receipt_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'verified-complete-native-failure-browser-receipt-schema-recovery',refs,summary)
if __name__=='__main__':main()

"""Rebind all current whole-source bounds to the pool/market parent-cell extent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-sham-shui-po-pool-native-scope-v1-20261016';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-fu-tor-loy-native-parent-scope-v1-20261016';CANDIDATE=BASE/'government-xl-sham-shui-po-pool-shared-terrain-v3-20261016'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__),HERE/'heritage_saved_native_bounds_binding_v1_20261014.py']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PRIOR,CANDIDATE]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for q in r['evidenceRefs']:assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 domain=read(CANDIDATE/'summary.json')['changedParentExtent'];data=read(PRIOR/'complete-bounds.json.gz');rows=data['rows'];m=read(ROOT/'3d-viewer/city/data/manifest.json');models={e['uid']:e for url in m['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/url)['models']};assert len(rows)==len(models)==6666 and set(models)=={r['uid'] for r in rows}
 for r in rows:assert r['sourceSHA256']==models[r['uid']]['sha256'];r['disjoint']=closed_disjoint(r['completeFourWorldBounds'],domain)
 touched=sorted(r['uid'] for r in rows if not r['disjoint']);DOC.mkdir();save(DOC/'complete-bounds.json.gz',data);scope=dict(currentNativeActors=len(rows),changedParentExtent=domain,touchingNativeUids=touched,allCurrentActorsNominated=True,fullMeshRegressionStillRequired=True,fullAcceptance=False);save(DOC/'scope.json',scope)
 refs +=[PRIOR/'complete-bounds.json.gz',CANDIDATE/'summary.json'];out=module('pool_scope_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-whole-source-pool-market-parent-scope-v1',list(dict.fromkeys(refs)),dict(uids=touched,summary=scope,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],scope=scope),flush=True)
if __name__=='__main__':main()

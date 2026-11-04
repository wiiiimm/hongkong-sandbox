"""Rebind authenticated current complete actor bounds to expanded assembly extent."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from heritage_saved_native_bounds_binding_v1_20261014 import closed_disjoint
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-native-scope-v2-20261018';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-west-wing-native-scope-v1-20261018';SCOPE=BASE/'government-xl-west-wing-terrain-inputs-v3-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PRIOR,SCOPE]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 domain=read(SCOPE/'scope.json')['fullParentBounds'];data=read(PRIOR/'complete-bounds.json.gz');touch=[]
 for r in data['rows']:
  r['disjoint']=closed_disjoint(r['completeFourWorldBounds'],domain)
  if not r['disjoint']:touch.append(r['uid'])
 summary=dict(currentNativeActors=len(data['rows']),changedParentExtent=domain,touchingNativeUids=sorted(touch),allCurrentActorsNominated=True,exactCurrentCensusReused=True,fullMeshRegressionStillRequired=True,fullAcceptance=False)
 save(DOC/'scope.json',summary);save(DOC/'complete-bounds.json.gz',data);refs.extend(ROOT/p for p in pins);refs.append(HERE/'heritage_saved_native_bounds_binding_v1_20261014.py')
 out=module('west_expanded_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-full-assembly-current-native-scope-v2',list(dict.fromkeys(refs)),dict(uids=sorted(touch),summary=summary,fullAcceptance=False,publication=False));print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()

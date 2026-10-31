"""Bind the validated candidate to the exact one native terrain it replaces."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-fung-yip-full-native-domain-';BATCH=P+'replacement-binding-v1-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();names=[P+'inset-v1-20261024',P+'runtime-v1-20261024',P+'scope-v1-20261024'];rs={};pins={};refs=[Path(__file__)]
 for n in names:
  rs[n],pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
 def take(n,f):
  p=BASE/n/f;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 proposal=rs[names[0]];scope=take(names[2],'scope.json');candidates=take(names[1],'terrain-candidates.json');assert len(candidates)==1
 candidate=candidates[0];assert candidate['path']==proposal['candidate']['path']and candidate['sha256']==proposal['candidate']['sha256']
 assert len(proposal['replacedNativeTerrain'])==1;old=proposal['replacedNativeTerrain'][0];assert candidate['replaces']==dict(url=old['url'],sha256=old['sha256'],retainedUids=old['targetUids'])
 actual=ROOT/old['path'];assert digest(actual.read_bytes())==old['sha256'];refs.append(actual)
 p=ROOT/candidate['path'];assert digest(p.read_bytes())==candidate['sha256'];refs.append(p);patch=read(p)
 assert set(old['targetUids'])<=set(patch['meta']['targetUids'])and patch['coarseCells']==scope['regionalCoarseCells']==old['coarseCells']
 positive=[r for r in scope['terrainContacts']if r['coarseOverlapAreaM2']>0 or any(c['overlapAreaM2']>0 for c in r['packedContacts'])];assert len(positive)==1 and positive[0]['url']==old['url']
 assert set(scope['touchingNativeUids'])=={'landsd/79882:0','landsd/12728:0','landsd/338946:0'}and scope['currentNativeActors']==6907
 result=dict(uids=proposal['uids'],candidate=candidate,scope=scope,replacedNativeTerrain=proposal['replacedNativeTerrain'],sourceSHA256ByUid=proposal['sourceSHA256ByUid'],sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Exact candidate-to-current replacement contract only. The full old native extent and declared targets remain; all three actual touching native actors and all56forms still require regression. No old asset, metadata, source, terrain acceptance or publication approval changes.')
 save(out/'summary.json',result);module('full_native_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-private-full-native-terrain-replacement-contract',refs,result)
if __name__=='__main__':main()

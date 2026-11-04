"""Current whole-parent BASIC and complete nominated-native terrain regression."""
from pathlib import Path
import subprocess,sys,json,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-royal-green3-retained-terrain-v1-20261017';SCOPE=BASE/'government-xl-royal-green3-current-native-scope-v1-20261018';BATCH='government-xl-royal-green3-current-neighbours-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def inputs():
 scope=read(SCOPE/'scope.json');final=module('royal_all_current_forms',HERE/'xl-final-script-pass.py');forms={b['uid']:(b,t)for b,_,t in final.load_forms(scope['changedParentExtent'])};manifest=read(ROOT/'3d-viewer/city/data/manifest.json');missing=set(scope['touchingNativeUids'])-set(forms)
 for tile in manifest['tiles']:
  if not missing:break
  for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
   if b['uid']in missing:forms[b['uid']]=(b,tile['url']);missing.remove(b['uid'])
 assert not missing,missing
 return scope,forms,manifest

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PRIOR,SCOPE]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 scope,forms,manifest=inputs();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifestpath.read_bytes());patches=read(PRIOR/'terrain-candidates.json');live={e['uid']for u in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/u)['models']};assert 'landsd/11093:0'not in live
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=u in live or bool(b.get('modelGeometry')))for u,(b,t)in forms.items()],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for b,t in forms.values()},candidateIds=['landsd/11093:0'],patches=patches,requiredNativeUids=scope['touchingNativeUids']))
 for tool in ['check-neighbours-multi-retained.mjs','check-native-neighbours-multi-retained-scoped-v1.mjs']:
  with(DOC/(tool+'.log')).open('w')as log:subprocess.run(['node',str(HERE/tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  assert reservations.owns(lease);refs.append(HERE/tool)
 standard=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json');assert set(scope['touchingNativeUids'])<=set(native['blocked'])and set(scope['touchingNativeUids'])<={x['uid']for x in native['rows']}
 for report in [standard,native]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 summary=dict(forms=len(forms),requiredNativeUids=scope['touchingNativeUids'],basicFlags=[dict(uid=x['uid'],reasons=x['reasons'])for x in standard['rows']if x['reasons']and not x['existingNative']],nativeRows=native['rows'],nativeResolved=native['resolved'],fullAcceptance=False);save(DOC/'summary.json',summary);assert digest(manifestpath.read_bytes())==sha
 refs.extend([HERE/'terrain-replacements.mjs',HERE/'native-neighbour-policy.mjs']);out=module('royal_current_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'royal-green3-current-whole-parent-all-nominated-native-regression-v1',list(set(refs)),dict(uids=['landsd/11093:0']+scope['touchingNativeUids'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],forms=len(forms),basicFlags=summary['basicFlags'],resolved=native['resolved']),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope,forms,_=inputs();keys={('building:' if u.startswith('landsd/') else 'source-form:')+u for u in forms}|{'terrain:city/data/terrain.json'};keys|={'terrain:'+r['url']for p in read(PRIOR/'terrain-candidates.json')for r in p['replacesMany']};claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

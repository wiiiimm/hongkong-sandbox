"""Full current native-neighbour regression for the bounded China Merchants child."""
from pathlib import Path
import subprocess,uuid,json
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-12-15-native-regression-v2-20261021';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(name,p):
  r,ps=authenticate(BASE/name);k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([BASE/name/'result.json',p]);return read(p)
 scopeName='government-xl-parkview-13-14-regional-scope-v2-20261021';scope=take(scopeName,BASE/scopeName/'scope.json');iv='government-xl-parkview-13-14-current-inventory-v1-20261021';inventory=take(iv,BASE/iv/'complete-bounds.json.gz');native={r['uid']for r in inventory['rows']};assert len(native)==6826
 cn='government-xl-parkview-12-15-private-terrain-v2-20261021';assert take(cn,BASE/cn/'summary.json')['terrainValidationPassed'];patches=take(cn,BASE/cn/'terrain-candidates.json');assert set(patches[0]['replaces']['retainedUids'])==set(scope['touchingNativeUids'])
 rt='government-xl-parkview-12-15-shared-runtime-v2-20261021';metrics=[r for r in take(rt,BASE/rt/'metrics.json')['rows']if r['uid']in {'landsd/253980:0','landsd/255260:0','landsd/255648:0','landsd/255440:0'}];assert len(metrics)==4 and all(not r.get('error')and r['missingTerrain']==0 and r['minSurfaceGap']>=-.5 and r['maxSamplerDelta']<=.004 for r in metrics)
 manifestp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(iv,manifestp);forms={};scopeForms=take(scopeName,BASE/scopeName/'form-obligations.json.gz');needed=native|{'landsd/253980:0','landsd/255260:0','landsd/255648:0','landsd/255440:0'}|{b['uid']for b in scopeForms}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];found=[b for b in read(p)['buildings']if b['uid']in needed]
  if found:refs.append(p)
  for b in found:assert b['uid']not in forms;forms[b['uid']]=b
 assert set(forms)==needed
 inputs=dict(rows=[dict(building=b,existingNative=uid in native,patchIndexes=[0])for uid,b in forms.items()],patches=patches)
 resources=['building:'+u for u in sorted(set(scope['touchingNativeUids'])|{'landsd/253980:0','landsd/255260:0','landsd/255648:0','landsd/255440:0'})];leases=[];owner=BATCH+'-'+str(uuid.uuid4())
 try:
  for offset in range(0,len(resources),800):
   claim=reservations.claim(owner,resources[offset:offset+800],batch=BATCH+'-'+str(offset),ttl=3600);assert claim['ok'],claim;leases.append(claim['reservation'])
  save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'neighbour-checks.json',{'rows':[]});tool=HERE/'check-parkview-retained-native-v2-20261021.mjs';cmd=['/home/williamli/.nvm/versions/node/v24.18.0/bin/node',str(tool),str(DOC.relative_to(ROOT))+'/']
  with(DOC/'worker.log').open('w')as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1500)
  save(DOC/'command.json',dict(command=cmd,exitCode=p.returncode));assert p.returncode==0
  result=read(DOC/'native-neighbour-checks.json');assert set(result['blocked'])==set(scope['touchingNativeUids']);assert {r['uid']for r in result['rows']}==set(scope['touchingNativeUids'])
  for path,h in result['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
  assert all(reservations.owns(lease)for lease in leases)
  summary=dict(uids=['landsd/253980:0','landsd/255260:0','landsd/255648:0','landsd/255440:0'],nominated=len(scope['touchingNativeUids']),checked=len(result['rows']),passed=len(result['resolved']),allRetainedPassed=all(r['passed']for r in result['rows']),installationApproved=False,qualification='Complete indexed installed originals nominated from whole current parent and packed child domain. Ordinary forms, source visual/collision/browser acceptance remain separate.')
  save(DOC/'summary.json',summary);r=module('china_native_regression_freeze4',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-whole-wrapper-native-regression',list(dict.fromkeys(refs+[tool])),summary);print(dict(jobId=r['jobId'],**summary),flush=True)
 finally:
  for lease in reversed(leases):
   if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

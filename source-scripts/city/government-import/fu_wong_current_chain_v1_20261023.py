"""Serial fresh-scene original-source checks; no installation or source modelling."""
from pathlib import Path
import subprocess,sys,traceback
from run import ROOT,HERE,read,save
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
B='government-xl-fu-wong-current-chain-v1-20261023';BASE=ROOT/'docs/astra-city/government-import';D=BASE/B;UID='landsd/50662:0'
N=dict(inventory='government-xl-after-source118003-current-inventory-v1-20261023',selection='government-xl-after-source118003-fu-wong-selection-v1-20261023',capture='government-xl-after-source118003-fu-wong-capture-v1-20261023',terrain='government-xl-fu-wong-retained-current-v1-20261023',current='government-xl-fu-wong-current-checks-v1-20261023',physical='government-xl-fu-wong-prephysical-v1-20261023')
assert not D.exists()and all(not(BASE/n).exists()for n in N.values());D.mkdir();refs=[Path(__file__)];completed=[];status='script-investigation'
retained='city/data/government-native-fu-loy-original-v1-20261022.json';manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert sum(p['url']==retained for p in manifest['terrainPatches'])==1
assert {'landsd/147589:0','landsd/51275:0'}<=set(read(ROOT/'3d-viewer'/retained)['meta']['targetUids'])
steps=[
 ('inventory','refresh_original_bounds_inventory_v1.py',['--prior','government-xl-after-tung-ping-current-inventory-v1-20261022','--attributes','government-xl-source118003-after-tung-ping-prephysical-v1-20261022-attributes','--installed','government-xl-source118003-original-installed-v3-20261022']),
 ('selection','selected_original_refresh_selection_v1.py',['--capture','government-xl-next-seventeen-current-capture-v1-20261022','--uid',UID]),
 ('capture','selected_original_current_capture_v2.py',['--capture',N['selection'],'--uid',UID]),
 ('terrain','selected_original_retained_replacement_v7.py',['--capture',N['capture'],'--terrain-check','government-xl-all-200-original-terrain-batch-v2-20261022','--uid',UID,'--retain-patch',retained]),
 ('current','selected_retained_patch_followthrough_v1.py',['--patch',N['terrain'],'--capture',N['capture'],'--inventory',N['inventory'],'--uid',UID]),
 ('physical','selected_original_prephysical_suite_v2.py',['--runtime',N['current']+'-runtime','--uid',UID]),
]
try:
 for phase,script,tail in steps:
  logpath=D/(phase+'.log');refs.extend([HERE/script,logpath]);save(D/'running.json',dict(uids=[UID],phase=phase,batch=N[phase],completed=completed,installationApproved=False))
  with logpath.open('w')as log:
   code=subprocess.run([sys.executable,'-u',str(HERE/script),'--batch',N[phase],*tail],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
  assert code==0,'Child command failed: '+phase+' exit'+str(code)
  result,_=authenticate(BASE/N[phase]);refs.append(BASE/N[phase]/'result.json');completed.append(dict(phase=phase,batch=N[phase],jobId=result['jobId']));print(completed[-1],flush=True)
  if phase=='inventory':assert result['currentNativeActors']==6850
  if phase=='terrain'and result.get('status')!='private-terrain-validator-passed':status='terrain-investigation';break
  if phase=='current':
   summary=read(BASE/N[phase]/'summary.json')
   if summary.get('basicFlags')or summary.get('status')in ['script-investigation','runtime-investigation']or set(summary.get('nativeResolved',[]))!={r['uid']for r in summary.get('nativeRows',[])}or any(not r['passed']for r in summary.get('nativeRows',[])):
    status='current-regression-investigation';break
   f=summary.get('foundation',{})
   if f.get('completeTerrainTriangles')!=f.get('triangles')or f.get('fullyBuriedTriangles')!=0 or f.get('fullyBuriedUpwardTriangles')!=0:status='source-foundation-investigation';break
  if phase=='physical':status=read(BASE/N[phase]/'summary.json')['status']
except Exception as error:
 save(D/'failure.json',dict(errorType=type(error).__name__,reason=str(error),traceback=traceback.format_exc()));refs.append(D/'failure.json');print(dict(errorType=type(error).__name__,reason=str(error)),flush=True)
summary=dict(uids=[UID],status=status,batches=N,completed=completed,installationApproved=False,publication=False,newlyInstalled=0,permanentRejection=False,sourceGeometryChanges=0,scriptExternalAICalls=0)
save(D/'summary.json',summary);module('fu_wong_chain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'serial-fresh-original-source-current-evidence',refs,summary)
print(dict(status=status,completed=len(completed)),flush=True)

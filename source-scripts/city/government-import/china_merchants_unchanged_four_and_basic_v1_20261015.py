"""Prove four pre-existing support flags are outside the changed child; check all BASIC forms."""
from pathlib import Path
import subprocess,sys
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from complete_actual_native_position_bounds_separation_20261011 import NATIVE_MODES
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-unchanged-four-and-basic-v1-20261015';DOC=BASE/BATCH
CENSUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015';SCOPE=BASE/'government-xl-china-merchants-complete-current-scope-v1-20261015';NATIVE=BASE/'government-xl-china-merchants-full-native-regression-v3-20261015';WRAP=BASE/'government-xl-china-merchants-current-wrapper-v1-20261015'
def main():
 assert not DOC.exists();paths=[Path(__file__)];pins={}
 for folder in [CENSUS,SCOPE,NATIVE,WRAP]:
  r=read(folder/'result.json');paths.append(folder/'result.json')
  for q in r['evidenceRefs']:
   assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 proposal=read(WRAP/'terrain-candidates.json')[0];new=read(ROOT/proposal['path']);old=read(ROOT/'3d-viewer'/proposal['replaces']['url'])
 assert {k:v for k,v in new.items()if k!='patches'}=={k:v for k,v in old.items()if k!='patches'} and new['patches'][:-1]==old['patches']
 child=new['patches'][-1];g=child['meta']['georef'];origin=read(ROOT/'3d-viewer/city/data/terrain.json')['meta']['origin']
 domain=[g['bE']-origin[0],origin[1]-g['bN'],g['bE']-origin[0]+(child['w']-1)*g['aE'],origin[1]-g['bN']-(child['h']-1)*g['aN']]
 # Same conservative halo as terrainGridBounds, never narrower than production lookup.
 halo=max(1e-8,32*sys.float_info.epsilon*max(*map(abs,origin),abs(g['bE']),abs(g['bN']),*map(abs,domain)));domain=[domain[0]-halo,domain[1]-halo,domain[2]+halo,domain[3]+halo]
 inv={r['uid']:r for r in read(CENSUS/'inventory.json.gz')['rows']};native=read(NATIVE/'native-neighbour-checks.json');failed=[r for r in native['rows']if not r['passed']];assert len(failed)==4
 cert=[]
 for row in failed:
  checks=[]
  for key in NATIVE_MODES.values():
   b=inv[row['uid']][key];gaps=[domain[0]-b[1][0],b[0][0]-domain[2],domain[1]-b[1][2],b[0][2]-domain[3]];assert max(gaps)>0;checks.append(dict(mode=key,strictPositiveSeparationM=max(gaps)))
  assert row['terrain']['maximumBurialIncrease']==0 and row['terrain']['newlyWhollyBuried']==0
  cert.append(dict(uid=row['uid'],completeBoundsDisjointFromOnlyChangedChild=checks,rawSupportFailureRetained=row,terrainRegressionResolvedByUnchangedWholeDomain=True,originalSupportReapproved=False))
 DOC.mkdir();save(DOC/'unchanged-four.json',dict(domain=domain,currentWrapperAllOtherBytesIdentical=True,rows=cert,scope='Exact whole-source separation from only added child establishes unchanged terrain for these four. Original support approvals are not granted or rewritten. Full1199 regression was executed.',publication=False))
 census=read(CENSUS/'input.json.gz');scope=read(SCOPE/'scope.json.gz');nativeids=set(inv);inputs=read(WRAP/'neighbour-inputs.json.gz');inputs['inputHashes']={p:h for p,h in pins.items()if p.startswith('3d-viewer/')};inputs['rows']=[dict(building=b,existingNative=b['uid']in nativeids,patchIndexes=[0])for b in scope['currentIntersectingForms']];save(DOC/'neighbour-inputs.json.gz',inputs)
 tool=HERE/'check-neighbours.mjs';paths.append(tool)
 with (DOC/'worker.log').open('w')as log:p=subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
 assert p.returncode==0;d=read(DOC/'neighbour-checks.json');bad=[r for r in d['rows']if r['reasons']and not r['existingNative']and not r['candidate']]
 for p,h in d['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 paths.extend(ROOT/'3d-viewer/city'/s for s in ['geo.js','terrain-patch-index.js','rendered-patch-height.js'])
 module('china_four_basic_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-four-native-and-complete-basic-neighbour-regression-v1',paths,dict(uids=['landsd/264206:0'],unchangedNativeFlags=4,basicFormsChecked=len(d['rows']),remainingBasicFailures=bad,fullAcceptance=False))
 print(dict(forms=len(d['rows']),basicFailures=len(bad),unchangedNativeFlags=4),flush=True)
if __name__=='__main__':main()

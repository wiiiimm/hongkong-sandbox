"""Bind complete diagnostic grid arrays to the unchanged viewer grid branch."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-fung-yip-full-native-domain-';BATCH=P+'heightfield-grid-conformance-v1-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();out.mkdir();refs=[Path(__file__)];receipt,pins=authenticate(BASE/(P+'inset-v1-20261024'));refs.append(BASE/(P+'inset-v1-20261024')/'result.json');patch=ROOT/receipt['candidate']['path'];assert digest(patch.read_bytes())==receipt['candidate']['sha256'];refs.append(patch);tool=HERE/'verify_virtual_fallback_grid_contract_v1_20261024.mjs';refs.append(tool);rows=[]
 for label,uid in [('podium','landsd/79883:0'),('tower','landsd/254815:0')]:
  folder=BASE/(P+label+'-effective-heightfield-v1-20261024');r,p=authenticate(folder);refs.append(folder/'result.json');contract=folder/'heightfield-contract.json';assert digest(contract.read_bytes())==p[str(contract.relative_to(ROOT))];refs.append(contract)
  dest=out/(label+'.json');subprocess.run(['node',str(tool),str(patch),str(contract),str(dest)],cwd=ROOT,check=True);result=read(dest);assert result['passed']and result['maximumSamplerErrorM']<1e-8;rows.append(dict(uid=uid,**result));refs.append(dest)
 refs.extend(ROOT/'3d-viewer/city'/n for n in ['geo.js','native-terrain.js','exact-finite-triangle-projection.js','world.js','terrain-patch-index.js','rendered-patch-height.js'])
 result=dict(uids=[r['uid']for r in rows],rows=rows,sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,qualification='Conformance only: every diagnostic selected fallback Float64 facet hash matches the actual geo.js grid branch, with all2352grid triangles checked at vertices/centroids. Full native surface remains the first runtime choice, and the diagnostic envelope deliberately overestimates the fallback by using it everywhere. It is never claimed drawn geometry or published. No missing drawn-projection flag is removed.')
 save(out/'summary.json',result);module('grid_conformance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-diagnostic-grid-array-and-current-renderer-grid-contract',refs,result)
if __name__=='__main__':main()

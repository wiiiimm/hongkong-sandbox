"""Rebind unchanged private V4 terrain to current census, then run full neighbour checks."""
from pathlib import Path
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
OLD=BASE/'government-xl-wave-verdant-multicore-terrain-v4-20261017'
CURRENT=BASE/'government-xl-wave-verdant-current-native-scope-v2-20261018'
APEX=BASE/'government-xl-apex227942-original-installed-v1-20261018'
BATCH='government-xl-wave-verdant-current-terrain-rebind-v5-20261018';DOC=BASE/BATCH

def rebind():
 assert not DOC.exists()
 old,new,apex=[read(p/'result.json')for p in [OLD,CURRENT,APEX]]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in [old,new,apex]:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 history={(r['originalPath'],r['originalSHA256']):r['savedHistoricalBytes']for r in apex['historicalMutableByteSnapshots']}
 refs=[Path(__file__),OLD/'result.json',CURRENT/'result.json',APEX/'result.json'];resolved=[];pins={}
 for r in [old,new]:
  for e in r['evidenceRefs']:
   p=ROOT/e['path'];h=e['sha256']
   if digest(p.read_bytes())!=h:
    assert r is old
    replacement=history[(e['path'],h)];p=ROOT/replacement['path'];assert digest(p.read_bytes())==h==replacement['sha256'];resolved.append(dict(originalPath=e['path'],originalSHA256=h,savedHistoricalBytes=replacement))
   key=str(p.relative_to(ROOT));assert key not in pins or pins[key]==h;pins[key]=h
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestsha=digest(manifestpath.read_bytes())
 current=read(CURRENT/'scope.json');scope=read(OLD/'scope.json');assert current['changedParentExtent']==scope['parentExtent'];assert current['currentNativeActors']==6684 and not current['touchingNativeUids']
 scope.update(currentNativeActors=6684,touchingNativeUids=[],allCurrentActorsNominated=True)
 final=module('wave_current_forms_v5',HERE/'xl-final-script-pass.py');forms=final.load_forms(scope['parentExtent']);scope['basicAndNativeForms']=[b['uid']for b,_,_ in forms]
 patches=module('wave_current_patch_bounds_v5',HERE/'native_patch_resolution.py')
 for entry in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/entry['url'];assert box(*scope['parentExtent']).intersection(box(*patches._patch_bounds(read(p)))).area<=1e-8,entry['url'];refs.append(p)
 candidates=read(OLD/'terrain-candidates.json')
 for candidate in candidates:
  p=ROOT/candidate['path'];assert digest(p.read_bytes())==candidate['sha256'];patch=read(p);parentpath=ROOT/'3d-viewer'/patch['meta']['parentTerrain'];assert digest(parentpath.read_bytes())==patch['meta']['parentSha256'];patches_ref=HERE/'resolve-pass.py';validator=module('wave_current_parent_validation_v5',patches_ref);validator.validate_patch(patch,read(parentpath));refs.extend([p,parentpath,patches_ref])
 selection=read(OLD/'selection.json.gz');selection['manifestSHA256']=manifestsha
 save(DOC/'scope.json',scope);save(DOC/'selection.json.gz',selection);save(DOC/'terrain-candidates.json',candidates)
 save(DOC/'rebind.json',dict(currentManifestSHA256=manifestsha,unchangedTerrainCandidates=candidates,historicalInputs=resolved,currentNativeActors=6684,forms=len(forms),touchingNativeUids=[],completeParentDomain=scope['parentExtent'],fullAcceptance=False))
 refs.extend([manifestpath,HERE/'native_patch_resolution.py',HERE/'xl-final-script-pass.py',*[ROOT/'3d-viewer'/t for _,_,t in forms]])
 assert digest(manifestpath.read_bytes())==manifestsha
 module('wave_current_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-original-unchanged-terrain-current-census-rebind-v5',list(set(refs)),dict(uids=[r['uid']for r in selection['rows']],fullAcceptance=False,newlyInstalled=0))

def main():
 rebind()
 worker=module('wave_current_neighbour_worker_v5',HERE/'wave_verdant_multicore_neighbours_v4_20261017.py')
 worker.PRIOR=DOC;worker.BATCH='government-xl-wave-verdant-current-neighbours-v5-20261018';worker.DOC=BASE/worker.BATCH;worker.LOCAL=HERE/'local'/worker.BATCH
 # The existing worker's subprocess executes its own module. Use a distinct
 # copied entry point with the same explicit constants, rather than losing them.
 import subprocess,sys
 tool=HERE/'wave_verdant_current_neighbours_worker_v5_20261018.py'
 assert not tool.exists()
 text=(HERE/'wave_verdant_multicore_neighbours_v4_20261017.py').read_text().replace('government-xl-wave-verdant-multicore-terrain-v4-20261017',BATCH).replace('government-xl-wave-verdant-multicore-neighbours-v4-20261017',worker.BATCH)
 tool.write_text(text)
 subprocess.run([sys.executable,str(tool)],cwd=ROOT,check=True)
if __name__=='__main__':main()

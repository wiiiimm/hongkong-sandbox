"""Fresh complete-domain ordinary neighbour check; no exclusions for car parks."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-yoho300857-private-terrain-capture-v2-20261020';SCOPE=BASE/'government-xl-yoho300857-current-terrain-scope-v1-20261020';BATCH='government-xl-yoho300857-current-neighbours-v1-20261020';DOC=BASE/BATCH

def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYS,SCOPE]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 scope=read(SCOPE/'scope.json');assert scope['currentNativeActors']==6764 and scope['allCurrentActorsNominated']and not scope['touchingNativeUids']
 candidates=read(PHYS/'terrain-candidates.json');assert len(candidates)==1 and candidates[0]['bounds']==scope['changedParentExtent'];bounds=candidates[0]['bounds'];manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={r['uid']for url in manifest['officialModelCatalogues']for r in read(ROOT/'3d-viewer'/url)['models']}
 final=module('oi_current_neighbour_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(bounds);inputHashes={str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes())for b,_,tile in forms};rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in installed or bool(b.get('modelGeometry')))for b,_,tile in forms]
 save(DOC/'neighbour-inputs.json.gz',dict(rows=rows,inputHashes=inputHashes,patches=candidates,candidateIds=['landsd/300857:0','landsd/301636:0']))
 tool=HERE/'check-neighbours-multi-retained.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 checks=read(DOC/'neighbour-checks.json');failed=[r for r in checks['rows']if r['reasons']];save(DOC/'summary.json',dict(forms=len(rows),remainingFailures=failed,allCurrentNativeActorsDisjoint=True,fullAcceptance=False))
 for p,h in checks['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([tool,HERE/'xl-final-script-pass.py',*[ROOT/p for p in pins],*[ROOT/p for p in inputHashes]])
 out=module('oi_neighbours_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'yoho300857-current-whole-terrain-domain-neighbours-v1',list(set(refs)),dict(uids=['landsd/300857:0','landsd/301636:0'],forms=len(rows),remainingFailures=failed,fullAcceptance=False,nextStep='Resolve any real ordinary-neighbour regressions without excluding unsupported forms; then staged/live browser and guarded installation.'));print(dict(jobId=out['jobId'],failed=[r['uid']for r in failed]),flush=True)
if __name__=='__main__':main()

"""Current whole-parent basic-form regression, diagnostic only; no publication."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018';BATCH='government-xl-apex227942-current-parent-neighbours-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for folder in [PRIOR,BASE/'government-xl-apex227942-original-terrain-foundation-v1-20261018']:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 patches=read(PRIOR/'terrain-candidates.json');parent=read(ROOT/'3d-viewer'/patches[0]['replaces']['url']);g=parent['meta']['georef'];domain=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(parent['w']-1)*g['aE'],816500-g['bN']-(parent['h']-1)*g['aN']]
 final=module('apex_parent_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(domain)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);native=set()
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;native.update(e['uid']for e in read(p)['models']);refs.append(p)
 rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in native)for b,_,_ in forms]
 save(DOC/'neighbour-inputs.json.gz',dict(rows=rows,patches=patches,candidateIds=['landsd/227942:0'],inputHashes=pins))
 save(DOC/'scope.json',dict(parentExtent=domain,forms=len(rows),currentNativeCatalogueCount=len(native),nativeWholeSourceBoundsAuditPending=True,fullAcceptance=False))
 print(dict(forms=len(rows),domain=domain),flush=True)
 with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 result=read(DOC/'neighbour-checks.json')
 for p,h in result['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 flagged=[r for r in result['rows']if r['reasons']];save(DOC/'summary.json',dict(forms=len(rows),flagged=flagged,fullAcceptance=False))
 refs.extend([HERE/'check-neighbours.mjs',HERE/'xl-final-script-pass.py']);out=module('apex_parent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-current-whole-parent-basic-neighbour-regression-v1',list(set(refs)),dict(uids=['landsd/227942:0'],forms=len(rows),flagged=flagged,fullAcceptance=False,newlyInstalled=0,nextStep='Resolve actual neighbour regressions, then complete packed native scope, renderer seam, support and identity/browser acceptance.'))
 print(dict(jobId=out['jobId'],flagged=flagged),flush=True)
if __name__=='__main__':main()

"""Read-only fixed-XL source inventory. Reuse verified local bytes; never approve models.
Usage: python xl_source_cache_inventory.py --count PATH --out PATH
One rg scan and one hash per candidate file, regardless of cohort size.
"""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import subprocess
from run import ROOT,read,save,digest

def inventory(count_path,out):
 count_path=Path(count_path);count=read(count_path)
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest_path.read_bytes())
 if manifest_sha!=count['manifestSHA256']:raise ValueError('Count snapshot is stale; refresh authoritative count first')
 manifest=read(manifest_path);installed=defaultdict(set);catalogue_pins={}
 for url in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;catalogue_pins[str(p.relative_to(ROOT))]=digest(p.read_bytes())
  for m in read(p)['models']:installed[m['uid']].add(m['sha256'])
 remaining=[]
 for r in count['rows']:
  exact=bool(r.get('runtimeSourceSHA256')) and r['runtimeSourceSHA256'] in installed.get(r.get('uid'),set())
  if exact!=r['installedVerified']:raise ValueError('Catalogue/count mismatch: '+str(r.get('uid')))
  if not exact:remaining.append(r)
 wanted={r['indexedSourceSHA256']for r in remaining};found=defaultdict(list)
 names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines()
 invalid=[]
 for name in sorted(names):
  p=ROOT/name;h=p.name.removesuffix('.glb.gz')
  if h not in wanted or found[h]:continue
  if digest(p.read_bytes())==h:found[h].append(name)
  else:invalid.append(name)
 rows=[dict(r,cacheState='exact-source-local'if found[r['indexedSourceSHA256']]else'source-recovery-needed',assetPath=next(iter(found[r['indexedSourceSHA256']]),None),installationApproved=False)for r in remaining]
 result=dict(totalXL=len(count['rows']),installedXL=len(count['rows'])-len(rows),remainingXL=len(rows),counts=dict(Counter(r['cacheState']for r in rows)),rows=rows,invalidNamedCacheFiles=invalid,manifestSHA256=manifest_sha,countSnapshot=dict(path=str(count_path.relative_to(ROOT)),sha256=digest(count_path.read_bytes())),catalogueHashes=catalogue_pins,qualification='Exact source availability only. Local files are not installation, identity or physical approval. No terminal rejection inferred.',scriptExternalAICalls=0)
 assert digest(manifest_path.read_bytes())==manifest_sha
 for p,h in catalogue_pins.items():assert digest((ROOT/p).read_bytes())==h
 save(out,result);print({k:result[k]for k in ['totalXL','installedXL','remainingXL','counts']},flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--count',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();inventory(a.count.resolve(),a.out.resolve())

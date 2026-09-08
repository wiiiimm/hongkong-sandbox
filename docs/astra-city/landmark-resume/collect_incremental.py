"""Inventory explicit current-pass caches; no network, database writes or uploads."""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/landmark-resume'))
from r2_snapshot import safe_path,digest
BASE=Path(__file__).parent
ROOTS=['assembly-support-review','identity-hold-review','residential-support-review','residual-support-review','grounded-model-review','grounded-framing-review','roof-occlusion-review','model-support-review','cultural-model-review','landmark-preflight/snapshots','landmark-identity/prepared','landmark-identity/staged','landmark-acquisition','central-completion']
SKIP={'__pycache__','node_modules','.git','.vercel'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--prior-manifest',type=Path,required=True);a=p.parse_args()
 checkpoint=json.loads((BASE/'R2-CLOUD-CHECKPOINT.json').read_text())
 assert digest(a.prior_manifest)==checkpoint['manifestSHA256'],'Prior checkpoint hash mismatch'
 prior=json.loads(a.prior_manifest.read_text()); prior_hashes={r['sha256'] for r in prior['files'] if r['kind']=='file'}
 tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
 paths={r['path'] for r in prior['files']}; excluded=[]
 for rel in ROOTS:
  base=ROOT/'source-scripts/city'/rel
  for parent,dirs,files in os.walk(base,followlinks=False):
   dirs[:]=[d for d in dirs if d not in SKIP]
   for name in files+[d for d in dirs if (Path(parent)/d).is_symlink()]:
    path=Path(parent)/name;relative=path.relative_to(ROOT).as_posix()
    if path.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.mp4'} or name.startswith('.env') or path.suffix in {'.key','.pem','.pyc'}:
     excluded.append(relative);continue
    safe_path(ROOT,relative);paths.add(relative)
 rows=[];missing=[];hashes={};reused=set();new=set();closure=[]; references=[]
 for relative in sorted(paths):
  path=safe_path(ROOT,relative)
  if not path.exists():missing.append(relative);continue
  row={'path':relative,'gitTracked':relative in tracked,'profiles':['unmodified-cli-restore'],'exists':True}
  if path.is_symlink():
   row.update(kind='symlink',linkTarget=os.readlink(path),bytes=0)
   target=path.resolve().relative_to(ROOT).as_posix()
   if target not in paths and target not in tracked and path.is_file():closure.append({'path':relative,'missingTarget':target})
  elif path.is_file():
   sha=digest(path);size=path.stat().st_size;row.update(kind='file',bytes=size,sha256=sha)
   if relative.endswith('/buildings.sqlite'):
    row.update(profiles=['historical-sqlite-not-current'], historicalCheckpointRow=next(r for r in prior['files'] if r['path']==relative))
   if relative not in tracked and 'unmodified-cli-restore' in row['profiles']:
    hashes[sha]=size;(reused if sha in prior_hashes else new).add(sha)
   # Local glTF buffers and current catalogue asset references are necessary offline inputs.
   if path.suffix=='.gltf' or path.name=='catalogue.json':
    try:data=json.loads(path.read_text())
    except (UnicodeError,json.JSONDecodeError):data={}
    refs=[b.get('uri') for b in data.get('buffers',[])] if path.suffix=='.gltf' else [m.get('asset') for m in data.get('models',[])]
    for ref in refs:
     if not ref or ref.startswith(('data:','https:','http:')):continue
     target=path.parent/ref
     if not target.exists():references.append({'path':relative,'reference':ref})
  else:continue
  rows.append(row)
 # Catalogue relocation is valid when exact content-addressed asset exists in closure.
 byname={}
 for row in rows:
  if row['kind']=='file':byname.setdefault(Path(row['path']).name,[]).append(row)
 relocated=[]
 for ref in references:
  matches=byname.get(Path(ref['reference']).name,[])
  expected=Path(ref['reference']).name.split('.')[0]
  matches=[m for m in matches if m.get('sha256')==expected]
  if matches:relocated.append({**ref,'availableAt':matches[0]['path'],'sha256':expected})
  else:closure.append(ref)
 out={'issue':'HKS-216','status':'inventory-only-awaiting-final-commit','gitCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'parentCheckpoint':checkpoint,'explicitRoots':ROOTS,'relocatedContentReferences':relocated,'rows':rows,'summary':{'entries':len(rows),'uniqueWorkingObjects':len(hashes),'uniqueWorkingBytes':sum(hashes.values()),'priorObjectsReused':len(reused),'priorBytesReused':sum(hashes[h] for h in reused),'newOrChangedObjects':len(new),'newOrChangedBytes':sum(hashes[h] for h in new),'missingPaths':missing,'referenceGaps':closure,'excludedMediaOrSensitivePaths':len(excluded)},'qualification':'Local hash audit only. No upload. Refresh after final commit and all cache writers stop. Existing remote_checkpoint full transfer re-downloads all objects; use a differential transfer manifest plus full restore manifest to avoid reading old payloads again.'}
 (BASE/'current-pass-cache-inventory.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({**out['summary'],'referenceGaps':len(closure)},indent=2))
if __name__=='__main__':main()

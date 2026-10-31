"""Enumerate absent exact historical source references before bounded restore."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'xl-terrain-recovery-20261010-hkdi-missing-historical-source-inventory-v1';ARCHIVE=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1/acceptance-manifest.json'
def refs(v,pointer=''):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:yield v,pointer
  for k,x in v.items():yield from refs(x,pointer+'/'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):yield from refs(x,pointer+'/'+str(i))
assert not DOC.exists();rows=[];seen=set()
for r,pointer in refs(read(ARCHIVE)):
 if not r['path'].startswith('source-scripts/city/landmark-acquisition/batches/terrain-prerequisites/staged/'):continue
 key=(r['path'],r['sha256'])
 if key in seen:continue
 seen.add(key);p=ROOT/r['path']
 if p.is_file():assert digest(p.read_bytes())==r['sha256'];continue
 rows.append(dict(reference=r,archivePointer=pointer,sheet=r['path'].split('/staged/')[1].split('/')[0],name=p.name))
save(DOC/'missing-inputs.json',dict(archive=dict(path=str(ARCHIVE.relative_to(ROOT)),sha256=digest(ARCHIVE.read_bytes())),missing=len(rows),missingBytes=sum(r['reference'].get('bytes',0)for r in rows),rows=rows,sourceGeometryChanges=0,numericalExceptions=0))
print(dict(missing=len(rows),bytes=sum(r['reference'].get('bytes',0)for r in rows),sheets=sorted({r['sheet']for r in rows})),flush=True)

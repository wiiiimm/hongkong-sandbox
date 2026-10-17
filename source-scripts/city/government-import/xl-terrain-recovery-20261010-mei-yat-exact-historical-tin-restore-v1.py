"""Restore exact pinned historical geometry/BIN from cached original provider ZIP.
No completeness exception or geometry change. Both files require archived hashes.
"""
from pathlib import Path
import json,zipfile,zlib,importlib.util
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261010-mei-yat-exact-historical-tin-restore-v1';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
ARCHIVE=BASE/'xl-terrain-recovery-20261010-mei-yat-source-scope-declaration-v1/acceptance-manifest.json'
ZIP=HERE/'local/government-xl-50-second-20260913/sheets/11-SW-10D/original/11-SW-10D.zip'
NAMES=['T36750156000106E11.bin','T36750156000106E11-geometry.gltf']
PINS=['1233ed4af4d076cf71a26857d81034b1a923a185c332dc2a1bfe6b592628eab5','5fecad7c609d2701c389bc33f5381024f0e6611d49894e91f255b39bf722062b']
def walk(v):
 if isinstance(v,dict):
  if v.get('path','').endswith(tuple(NAMES)) and '/landmark-acquisition/' in v['path']:yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
def main():
 assert not DOC.exists();expected={Path(r['path']).name:r for r in walk(read(ARCHIVE))};assert set(expected)==set(NAMES)
 for n,s in zip(NAMES,PINS):assert expected[n]['sha256']==s
 memberproof=[];files=[]
 with zipfile.ZipFile(ZIP) as z:
  targets={ext:next(m for m in z.infolist() if '/TERRAIN(TB)/T36750156000106E11/' in '/'+m.filename and m.filename.endswith(ext)) for ext in ['.bin','.gltf']}
  decoded={}
  for ext,m in targets.items():
   raw=z.read(m);assert len(raw)==m.file_size and zlib.crc32(raw)&0xffffffff==m.CRC;decoded[ext]=raw;memberproof.append(dict(name=m.filename,decodedBytes=len(raw),crc32=m.CRC,decodedSHA256=digest(raw)))
  g=json.loads(decoded['.gltf']);g.pop('images',None);g.pop('textures',None);g.pop('samplers',None)
  for mat in g.get('materials',[]):
   mat.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
   for key in ['normalTexture','occlusionTexture','emissiveTexture']:mat.pop(key,None)
  values=[decoded['.bin'],json.dumps(g,separators=(',',':')).encode()]
  for n,raw in zip(NAMES,values):
   r=expected[n];assert digest(raw)==r['sha256'] and len(raw)==r['bytes'],'Historical exact byte SHA mismatch; restore forbidden';p=ROOT/r['path']
   if p.exists():assert p.read_bytes()==raw
   else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
   files.append(dict(**r,exactOriginalRestored=True));print(n,len(raw),'EXACT',flush=True)
 out=dict(uids=['landsd/183776:0'],files=files,sourceArchiveProvenance=dict(cachedLocalArchivePath=str(ZIP.relative_to(ROOT)),archiveSHA256=digest(ZIP.read_bytes()),sourceMembers=memberproof),modelGeometryChanges=0,terrainGeometryChanges=0,provenanceScopeWeakened=False,qualification='Restored exact archived SHA/length of historical provider TIN geometry-only glTF and unchanged BIN from original ZIP, with CRC validation. Original source references remain complete; no metadata exemption, new shape or current numerical credit.')
 save(DOC/'restored-inputs.json',out);s=importlib.util.spec_from_file_location('mei_exact_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'mei-yat-exact-historical-source-tin-restore-v1',[Path(__file__),ARCHIVE,*[ROOT/r['path'] for r in files]],out)
if __name__=='__main__':main()

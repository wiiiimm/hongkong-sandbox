"""Bounded exact cached original-TIN restore; no closure-policy exception."""
import argparse,json,zipfile,zlib,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';ARCHIVE=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1/acceptance-manifest.json'
def walk(v):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str)and v.get('sha256'):yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
def main():
 p=argparse.ArgumentParser();p.add_argument('--sheet',required=True);p.add_argument('--model',required=True);p.add_argument('--zip',required=True);p.add_argument('--batch',required=True);a=p.parse_args();assert a.sheet in {'11-SW-6D'} and a.model in {'T30750156000106E10'}
 doc=BASE/a.batch;assert not doc.exists();zpath=(ROOT/a.zip).resolve();assert zpath.is_relative_to(ROOT);names=[a.model+'.bin',a.model+'-geometry.gltf'];expected={Path(r['path']).name:r for r in walk(read(ARCHIVE))if '/landmark-acquisition/batches/terrain-prerequisites/staged/'+a.sheet+'/'in r['path']and Path(r['path']).name in names};assert set(expected)==set(names);members=[]
 with zipfile.ZipFile(zpath)as z:
  decoded={}
  for ext in ['.bin','.gltf']:
   m=next(m for m in z.infolist()if '/TERRAIN(TB)/'+a.model+'/'in '/'+m.filename and m.filename.endswith(ext));raw=z.read(m);assert len(raw)==m.file_size and zlib.crc32(raw)&0xffffffff==m.CRC;decoded[ext]=raw;members.append(dict(name=m.filename,crc32=m.CRC,decodedBytes=len(raw),decodedSHA256=digest(raw)))
 g=json.loads(decoded['.gltf']);g.pop('images',None);g.pop('textures',None);g.pop('samplers',None)
 for mat in g.get('materials',[]):
  mat.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
  for key in ['normalTexture','occlusionTexture','emissiveTexture']:mat.pop(key,None)
 files=[]
 for n,raw in zip(names,[decoded['.bin'],json.dumps(g,separators=(',',':')).encode()]):
  r=expected[n];assert len(raw)==r['bytes']and digest(raw)==r['sha256'],'Exact archived numerical bytes differ; restore forbidden';dest=ROOT/r['path']
  if dest.exists():assert dest.read_bytes()==raw
  else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  files.append(dict(**r,exactOriginalRestored=True));print(n,len(raw),'EXACT',flush=True)
 out=dict(uids=['landsd/89613:0'],files=files,cachedOriginalArchive=dict(path=str(zpath.relative_to(ROOT)),sha256=digest(zpath.read_bytes())),originalMembers=members,sourceGeometryChanges=0,terrainGeometryChanges=0,provenanceScopeWeakened=False,qualification='Original member CRC and final immutable archived SHA/bytes strictly matched before restoring missing original numerical paths. No closure or current physical exception.')
 save(doc/'restored-inputs.json',out);s=importlib.util.spec_from_file_location('hkdi_cached_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(a.batch,'hkdi-exact-cached-historical-source-tin-restore-v1',[Path(__file__),ARCHIVE,*[ROOT/r['path']for r in files]],out)
if __name__=='__main__':main()

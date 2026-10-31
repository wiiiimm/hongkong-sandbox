"""Recover exact historical TIN bytes; no metadata waiver or geometry edit."""
import importlib.util,json,struct,types,zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest
spec=importlib.util.spec_from_file_location('bounded_original_acquisition',ROOT/'source-scripts/city/landmark-acquisition/acquire.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
DOC=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-no1-garden-exact-historical-tin-restore-v1';LOCAL=HERE/'local'/DOC.name
assert not DOC.exists();DOC.mkdir();LOCAL.mkdir(parents=True,exist_ok=True)
net=a.Network(DOC/'transfer-ledger.json',cap=26000000);index=read(a.HERE/'index.json');plan=read(a.HERE/'batches/terrain-prerequisites/target-input.json')
def walk(v):
 if isinstance(v,dict):
  if 'sheet' in v and isinstance(v.get('directory'),dict) and 'members' in v['directory']:yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
parts={r['sheet']:r for r in walk(plan)};sources=read(ROOT/'3d-viewer/city/data/terrain-central-with-sun-yat-sen.json')['patches'][1]['meta']['source']['nativeSources'];proof=[]
for source in sources:
 sheet=source['sheet'];attrs=next(f['attributes'] for f in index['features'] if f['attributes']['SHEETNO']==sheet);url=attrs['Format_glTF'];members=parts[sheet]['directory']['members'];decoded={}
 for m in members:
  start=m['headerOffset'];header,h=net.get(url,30,span=f'{start}-{start+29}');fields=struct.unpack('<4s5H3L2H',header);assert fields[0]==b'PK\x03\x04';size=30+fields[-2]+fields[-1]+m['compressedBytes'];raw,headers=net.get(url,size,span=f'{start}-{start+size-1}',etag=h.get('ETag'))
  e=types.SimpleNamespace(filename=m['name'],compress_type=fields[3],compress_size=m['compressedBytes'],file_size=m['decodedBytes'],CRC=m['crc32']);value=a.unpack_member(raw,e);decoded[m['name']]=value
  dest=LOCAL/sheet/Path(m['name']).name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
 for expected in source['files']:
  p=ROOT/expected['path'];name=Path(expected['path']).name
  if name.endswith('.bin'):value=next(v for k,v in decoded.items() if k.endswith('/'+name))
  else:
   original=next(v for k,v in decoded.items() if k.endswith('.gltf'));g=json.loads(original);g.pop('images',None);g.pop('textures',None);g.pop('samplers',None)
   for material in g.get('materials',[]):
    material.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
    for key in ['normalTexture','occlusionTexture','emissiveTexture']:material.pop(key,None)
   value=json.dumps(g,separators=(',',':')).encode()
  assert digest(value)==expected['sha256'] and len(value)==expected['bytes'],'Original historical byte SHA mismatch; no restore'
  if p.exists():assert p.read_bytes()==value
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
  proof.append(dict(**expected,exactOriginalRestored=True));print(sheet,name,len(value),'EXACT',flush=True)
save(DOC/'restored-inputs.json',dict(files=proof,modelGeometryChanges=0,terrainGeometryChanges=0,provenanceScopeWeakened=False,receivedBytes=net.data['receivedBytes']))

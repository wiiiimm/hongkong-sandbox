"""Restore archived exact NW9B TIN members using pinned original range receipts.

No closure exception: compressed range SHA, decoded CRC and archived final SHA
must all match before either missing original numerical path is written.
"""
from pathlib import Path
import json,struct,zlib,urllib.request,importlib.util
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261010-hkdi-exact-historical-nw9b-tin-restore-v1';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
ARCHIVE=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1/acceptance-manifest.json'
ACQ=ROOT/'source-scripts/city/landmark-acquisition/batches/terrain-prerequisites'
MODEL='T35250222000106E11';NAMES=[MODEL+'.bin',MODEL+'-geometry.gltf'];PINS=['1da5a936e4e84c5c7e09ce1b1b50fcd41956f25e4dfd18d21cd8603f4aa9a700','7ef434db85b4a4d6fcaca75b36ec5da919b64ca27b21d00e819ba24f1aed2ea5']
def walk(v):
 if isinstance(v,dict):
  if v.get('path','').endswith(tuple(NAMES)) and '/landmark-acquisition/' in v['path']:yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
def all_dicts(v):
 if isinstance(v,dict):
  yield v
  for x in v.values():yield from all_dicts(x)
 elif isinstance(v,list):
  for x in v:yield from all_dicts(x)
def main():
 assert not DOC.exists();expected={Path(r['path']).name:r for r in walk(read(ARCHIVE))};assert set(expected)==set(NAMES)
 for n,s in zip(NAMES,PINS):assert expected[n]['sha256']==s
 target=next(r for r in all_dicts(read(ACQ/'target-input.json'))if r.get('sheet')=='11-NW-9B' and 'directory'in r);members=target['directory']['members'];assert len(members)==2
 ledger=[r for r in all_dicts(read(ACQ/'transfer-ledger.json')) if r.get('method')=='GET' and '/11-NW-9B.zip' in r.get('url','') and r.get('status')=='complete'];assert len(ledger)==2
 decoded={};proof=[];LOCAL.mkdir(parents=True,exist_ok=True)
 for member in members:
  extension=Path(member['name']).suffix;r=next(x for x in ledger if int(x['range'].split('-')[0])==member['headerOffset']);assert r['httpStatus']==206 and r['reservedBytes']==r['receivedBytes']
  cached=LOCAL/(r['sha256']+'.range.bin')
  if cached.exists():raw=cached.read_bytes()
  else:
   request=urllib.request.Request(r['url'],headers={'Range':'bytes='+r['range']})
   with urllib.request.urlopen(request,timeout=45) as response:
    assert response.status==206 and response.headers['Content-Range']==r['headers']['Content-Range'];raw=response.read(r['receivedBytes']+1)
   assert len(raw)==r['receivedBytes'] and digest(raw)==r['sha256'],'Provider range differs from archived original receipt; restore forbidden';cached.write_bytes(raw)
  assert len(raw)==r['receivedBytes'] and digest(raw)==r['sha256'];assert raw[:4]==b'PK\x03\x04'
  header=struct.unpack_from('<4s5H3I2H',raw);method=header[3];crc,compressed,uncompressed=header[6:9];name_length,extra_length=header[9:11];name=raw[30:30+name_length].decode();start=30+name_length+extra_length
  assert name==member['name'] and method==8 and crc==member['crc32'] and compressed==member['compressedBytes'] and uncompressed==member['decodedBytes'];assert start+compressed<=len(raw)
  value=zlib.decompress(raw[start:start+compressed],-15);assert len(value)==uncompressed and zlib.crc32(value)&0xffffffff==crc;decoded[extension]=value
  proof.append(dict(originalTransferReceipt=r,compressedRange=dict(path=str(cached.relative_to(ROOT)),sha256=digest(raw)),name=name,decodedBytes=len(value),crc32=crc,decodedSHA256=digest(value)))
 g=json.loads(decoded['.gltf']);g.pop('images',None);g.pop('textures',None);g.pop('samplers',None)
 for mat in g.get('materials',[]):
  mat.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
  for key in ['normalTexture','occlusionTexture','emissiveTexture']:mat.pop(key,None)
 values=[decoded['.bin'],json.dumps(g,separators=(',',':')).encode()];files=[]
 for n,raw in zip(NAMES,values):
  r=expected[n];assert digest(raw)==r['sha256'] and len(raw)==r['bytes'],'Exact archived numerical input differs; restore forbidden';p=ROOT/r['path']
  if p.exists():assert p.read_bytes()==raw
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  files.append(dict(**r,exactOriginalRestored=True));print(n,len(raw),'EXACT',flush=True)
 out=dict(uids=['landsd/89613:0'],files=files,sourceMembers=proof,modelGeometryChanges=0,terrainGeometryChanges=0,provenanceScopeWeakened=False,qualification='Exact archived provider BIN and geometry-only glTF restored only after compressed-range SHA, original member CRC/length, and final archived byte SHA/length verification. No new closure or numerical exception; these global historical provenance inputs grant no new current acceptance.')
 save(DOC/'restored-inputs.json',out);s=importlib.util.spec_from_file_location('hkdi_exact_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'hkdi-exact-historical-source-tin-nw9b-restore-v1',[Path(__file__),ARCHIVE,ACQ/'target-input.json',ACQ/'transfer-ledger.json',*[ROOT/r['path']for r in files],*[ROOT/r['compressedRange']['path']for r in proof]],out)
if __name__=='__main__':main()

"""Recover all eight enumerated missing original global TIN references exactly.

Three authenticated cached ZIP members and one pinned historical range acquisition;
all original CRC/length and immutable final SHA gates remain mandatory.
"""
import json,zipfile,zlib,struct,urllib.request,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-hkdi-batch-exact-historical-tin-restore-v2';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=BASE/'xl-terrain-recovery-20261010-hkdi-missing-historical-source-inventory-v1/missing-inputs.json';ARCHIVE=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1/acceptance-manifest.json';ACQ=ROOT/'source-scripts/city/landmark-acquisition/batches/terrain-prerequisites'
ZIPS={'11-NW-24C':'source-scripts/city/government-import/local/government-xxl-second-20260911/sheets/11-NW-24C/original/11-NW-24C.zip','11-SE-7D':'source-scripts/city/government-import/local/government-xl-full-cell-34-sequence-20261006-254621-0/sheets/11-SE-7D/original/11-SE-7D.zip','11-NE-25C':'source-scripts/city/government-import/local/government-200-20260911-pending-context-v1/terrain/11-NE-25C/original/11-NE-25C.zip'}
def all_dicts(v):
 if isinstance(v,dict):
  yield v
  for x in v.values():yield from all_dicts(x)
 elif isinstance(v,list):
  for x in v:yield from all_dicts(x)
def geometry(raw):
 g=json.loads(raw);g.pop('images',None);g.pop('textures',None);g.pop('samplers',None)
 for mat in g.get('materials',[]):
  mat.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
  for key in ['normalTexture','occlusionTexture','emissiveTexture']:mat.pop(key,None)
 return json.dumps(g,separators=(',',':')).encode()
def main():
 assert not DOC.exists();inventory=read(INPUT);assert inventory['missing']==8 and inventory['missingBytes']==105362847 and inventory['archive']['sha256']==digest(ARCHIVE.read_bytes());groups={}
 for r in inventory['rows']:groups.setdefault(r['sheet'],[]).append(r)
 assert set(groups)==set(ZIPS)|{'11-SW-20B'};files=[];provenance=[];LOCAL.mkdir(parents=True,exist_ok=True)
 for sheet,rows in sorted(groups.items()):
  assert len(rows)==2;model=rows[0]['name'].split('.')[0].replace('-geometry','');decoded={};members=[]
  if sheet in ZIPS:
   path=ROOT/ZIPS[sheet]
   with zipfile.ZipFile(path)as z:
    for ext in ['.bin','.gltf']:
     m=next(m for m in z.infolist()if '/TERRAIN(TB)/'+model+'/'in '/'+m.filename and m.filename.endswith(ext));raw=z.read(m);assert len(raw)==m.file_size and zlib.crc32(raw)&0xffffffff==m.CRC;decoded[ext]=raw;members.append(dict(name=m.filename,crc32=m.CRC,decodedBytes=len(raw),decodedSHA256=digest(raw)))
   provenance.append(dict(sheet=sheet,originalArchive=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),members=members))
  else:
   target=next(r for r in all_dicts(read(ACQ/'target-input.json'))if r.get('sheet')==sheet and 'directory'in r);ledger=[r for r in all_dicts(read(ACQ/'transfer-ledger.json'))if r.get('method')=='GET'and '/'+sheet+'.zip'in r.get('url','')and r.get('status')=='complete'];assert len(ledger)==2
   for m in target['directory']['members']:
    r=next(x for x in ledger if int(x['range'].split('-')[0])==m['headerOffset']);cached=LOCAL/(r['sha256']+'.range.bin')
    if cached.exists():raw=cached.read_bytes()
    else:
     request=urllib.request.Request(r['url'],headers={'Range':'bytes='+r['range']})
     with urllib.request.urlopen(request,timeout=45)as response:
      assert response.status==206 and response.headers['Content-Range']==r['headers']['Content-Range'];raw=response.read(r['receivedBytes']+1)
     assert len(raw)==r['receivedBytes']and digest(raw)==r['sha256'],'Compressed range changed; restore forbidden';cached.write_bytes(raw)
    assert len(raw)==r['receivedBytes']and digest(raw)==r['sha256'];h=struct.unpack_from('<4s5H3I2H',raw);assert h[0]==b'PK\x03\x04'and h[3]==8;crc,compressed,uncompressed=h[6:9];n,extra=h[9:11];name=raw[30:30+n].decode();start=30+n+extra;assert name==m['name']and crc==m['crc32']and compressed==m['compressedBytes']and uncompressed==m['decodedBytes']and start+compressed<=len(raw);value=zlib.decompress(raw[start:start+compressed],-15);assert len(value)==uncompressed and zlib.crc32(value)&0xffffffff==crc;decoded[Path(name).suffix]=value;members.append(dict(originalTransferReceipt=r,compressedRange=dict(path=str(cached.relative_to(ROOT)),sha256=digest(raw)),name=name,crc32=crc,decodedBytes=len(value),decodedSHA256=digest(value)))
   provenance.append(dict(sheet=sheet,members=members))
  decoded['-geometry.gltf']=geometry(decoded['.gltf'])
  # Validate both full original files before writing either original path.
  for row in rows:
   r=row['reference'];suffix='.bin'if row['name'].endswith('.bin')else '-geometry.gltf';raw=decoded[suffix];assert len(raw)==r['bytes']and digest(raw)==r['sha256'],'Archived exact input differs; restore forbidden'
  for row in rows:
   r=row['reference'];raw=decoded['.bin'if row['name'].endswith('.bin')else '-geometry.gltf'];dest=ROOT/r['path']
   if dest.exists():assert dest.read_bytes()==raw
   else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
   files.append(dict(**r,exactOriginalRestored=True));print(sheet,row['name'],len(raw),'EXACT',flush=True)
 out=dict(uids=['landsd/89613:0'],files=files,originalAcquisition=provenance,sourceGeometryChanges=0,terrainGeometryChanges=0,provenanceScopeWeakened=False,numericalExceptions=0,qualification='Every enumerated missing archived original BIN/geometry-glTF restored only after member CRC/length and immutable final byte SHA/length equality, with historical compressed-range equality for absent ZIP. No closure-policy exception or new current physical acceptance.')
 save(DOC/'restored-inputs.json',out);refs=[Path(__file__),INPUT,ARCHIVE,ACQ/'target-input.json',ACQ/'transfer-ledger.json',*[ROOT/r['path']for r in files],*[ROOT/m['compressedRange']['path']for p in provenance for m in p['members']if 'compressedRange'in m]];s=importlib.util.spec_from_file_location('hkdi_batch_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'hkdi-exact-eight-historical-source-tin-batch-restore-v2',refs,out)
if __name__=='__main__':main()

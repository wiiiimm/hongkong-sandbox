"""Batch exact restoration of every enumerated global original TIN path.

Final archived SHA is mandatory for all restored bytes. Sources are byte-pinned
cached original members or historical SHA-pinned HTTP ranges; no source rewrite,
closure-policy exception, approximate reconstruction or new physical credit.
"""
import json,zipfile,zlib,struct,urllib.request,subprocess,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261010-hkdi-all-prefix-exact-historical-tin-restore-v3';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
INPUT=BASE/'xl-terrain-recovery-20261010-hkdi-missing-historical-source-inventory-v2/missing-inputs.json';ARCHIVE=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1/acceptance-manifest.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def dicts(v):
 if isinstance(v,dict):
  yield v
  for x in v.values():yield from dicts(x)
 elif isinstance(v,list):
  for x in v:yield from dicts(x)
def variants(raw):
 yield raw
 g=json.loads(raw);g.pop('images',None);g.pop('textures',None);g.pop('samplers',None)
 for mat in g.get('materials',[]):
  mat.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
  for key in ['normalTexture','occlusionTexture','emissiveTexture']:mat.pop(key,None)
 yield json.dumps(g,separators=(',',':')).encode()
def main():
 assert not DOC.exists();inv=read(INPUT);assert inv['archive']==ref(ARCHIVE);groups={}
 for row in inv['rows']:groups.setdefault((row['sheet'],row['model']),[]).append(row)
 sourcefiles=[ROOT/p for p in subprocess.check_output(['rg','--files','-uuu','source-scripts/city'],cwd=ROOT,text=True).splitlines()];byname={}
 for p in sourcefiles:byname.setdefault(p.name,[]).append(p)
 ledgers=[p for p in sourcefiles if p.name.endswith('transfer-ledger.json')];receipt_index={}
 for p in ledgers:
  try:d=read(p)
  except(ValueError,OSError):continue
  for r in dicts(d):
   if r.get('method')!='GET'or r.get('status')!='complete'or r.get('httpStatus')!=206 or not isinstance(r.get('range'),str):continue
   url=r.get('url','')
   if not url.startswith('https://download.map.gov.hk/api/3d-zip/GLTF0/'):continue
   sheet=url.split('/')[-1].split('.zip')[0];receipt_index.setdefault(sheet,[]).append((p,r))
 restored=[];provenance=[];missing=[];LOCAL.mkdir(parents=True,exist_ok=True)
 for (sheet,model),rows in sorted(groups.items()):
  values={};sources={};member_pins={model+'.bin':set(),model+'.gltf':set()}
  def consider(name,raw,source):
   if name not in member_pins:return
   if name.endswith('.gltf'):candidates=list(variants(raw))
   else:candidates=[raw]
   for row in rows:
    wanted=row['name'];matches=[v for v in candidates if digest(v)==row['reference']['sha256']and(len(v)==row['reference']['bytes']if 'bytes'in row['reference']else True)]
    if matches:values[wanted]=matches[0];sources[wanted]=source
  for name in [model+'.bin',model+'.gltf',model+'-geometry.gltf']:
   for p in byname.get(name,[]):
    raw=p.read_bytes()
    if name.endswith('-geometry.gltf'):
     for row in rows:
      if row['name']==name and digest(raw)==row['reference']['sha256']:values[name]=raw;sources[name]=dict(exactExistingSource=ref(p))
    else:consider(name,raw,dict(exactExistingSource=ref(p)))
   if len(values)==len({r['name']for r in rows}):break
  if len(values)<len({r['name']for r in rows}):
   for p in byname.get(sheet+'.zip',[]):
    try:
     with zipfile.ZipFile(p)as z:
      members=[m for m in z.infolist()if '/TERRAIN(TB)/'+model+'/'in '/'+m.filename and Path(m.filename).name in member_pins]
      for m in members:
       raw=z.read(m);assert len(raw)==m.file_size and zlib.crc32(raw)&0xffffffff==m.CRC;consider(Path(m.filename).name,raw,dict(originalArchive=ref(p),member=dict(name=m.filename,crc32=m.CRC,decodedBytes=len(raw),decodedSHA256=digest(raw))))
    except zipfile.BadZipFile:continue
    if len(values)==len({r['name']for r in rows}):break
  if len(values)<len({r['name']for r in rows}):
   seen=set()
   for lp,r in receipt_index.get(sheet,[]):
    if r['sha256']in seen:continue
    seen.add(r['sha256']);assert r['receivedBytes']==r['reservedBytes'];assert 0<r['receivedBytes']<=35000000,'Historical range exceeds bounded source restoration cap';cached=LOCAL/(r['sha256']+'.range.bin')
    if cached.exists():compressed=cached.read_bytes()
    else:
     req=urllib.request.Request(r['url'],headers={'Range':'bytes='+r['range']})
     with urllib.request.urlopen(req,timeout=45)as response:
      assert response.status==206 and response.headers['Content-Range']==r['headers']['Content-Range'];compressed=response.read(r['receivedBytes']+1)
     assert len(compressed)==r['receivedBytes']and digest(compressed)==r['sha256'],'Historical compressed range changed; restoration forbidden';cached.write_bytes(compressed)
    assert len(compressed)==r['receivedBytes']and digest(compressed)==r['sha256']
    if compressed[:4]!=b'PK\x03\x04':continue
    h=struct.unpack_from('<4s5H3I2H',compressed);crc,size,uncompressed=h[6:9];n,extra=h[9:11];name=compressed[30:30+n].decode();start=30+n+extra
    if Path(name).name not in member_pins or '/TERRAIN(TB)/'+model+'/'not in '/'+name:continue
    assert h[3]==8 and size>0 and uncompressed>0 and start+size<=len(compressed);raw=zlib.decompress(compressed[start:start+size],-15);assert len(raw)==uncompressed and zlib.crc32(raw)&0xffffffff==crc
    consider(Path(name).name,raw,dict(historicalLedger=ref(lp),originalTransferReceipt=r,compressedRange=ref(cached),member=dict(name=name,crc32=crc,decodedBytes=len(raw),decodedSHA256=digest(raw))))
    if len(values)==len({r['name']for r in rows}):break
  if len(values)<len({r['name']for r in rows}):
   missing.extend(r for r in rows if r['name']not in values);print(json.dumps(dict(sheet=sheet,model=model,remaining=[r['name']for r in rows if r['name']not in values])),flush=True)
  for row in rows:
   if row['name']not in values:continue
   r=row['reference'];raw=values[row['name']];assert digest(raw)==r['sha256'];dest=ROOT/r['path'];assert dest.resolve().is_relative_to(ROOT)and str(dest.relative_to(ROOT)).startswith('source-scripts/city/')
   if dest.exists():assert dest.read_bytes()==raw
   else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
   restored.append(dict(**r,decodedBytes=len(raw),exactOriginalRestored=True));provenance.append(dict(restoredReference=r,source=sources[row['name']]));print(sheet,row['name'],len(raw),'EXACT',flush=True)
  save(DOC/'restore-progress.json',dict(restored=restored,remaining=missing,partialCheckpointOnly=True,noNumericalExceptions=True))
 out=dict(uids=['landsd/89613:0'],files=restored,originalAcquisition=provenance,remaining=missing,sourceGeometryChanges=0,terrainGeometryChanges=0,provenanceScopeWeakened=False,numericalExceptions=0,allEnumeratedOriginalFilesRestored=not missing,qualification='Each restored original path exactly matches immutable archived SHA/length; recovered from byte-pinned cached source/CRC-verified original ZIP or historical compressed-range SHA and member CRC. No approximate source, closure waiver or new physical acceptance.')
 save(DOC/'restored-inputs.json',out);assert not missing,'Unresolved exact original source acquisitions preserved; closure remains held'
 refs=[Path(__file__),INPUT,ARCHIVE,*[ROOT/r['path']for r in restored]]
 for p in provenance:
  for r in dicts(p['source']):
   if isinstance(r.get('path'),str)and isinstance(r.get('sha256'),str):refs.append(ROOT/r['path'])
 s=importlib.util.spec_from_file_location('hkdi_allprefix_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'hkdi-all-prefix-exact-original-tin-restoration-v3',list(dict.fromkeys(refs)),out)
if __name__=='__main__':main()

"""Freeze independently verified raw provider exterior provenance and exact source role."""
import importlib.util,gzip,json,struct
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='xl-terrain-recovery-20261009-222781-provider-role'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LEASE='/tmp/xl-terrain-recovery-20261009-222781-lease.json'
RAW=HERE/'local/government-xl-held-component-recovery-20261008/government-source/6-SW-1A/decoded/BUILDING/B156592961802063C0/B156592961802063C0.gltf'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();assert reservations.heartbeat(read(LEASE))['ok']
 d=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-wall-context/diagnostic.json.gz');r=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-current-inputs-v2/check-selection.json.gz')['rows'][0]
 asset=ROOT/r['candidate']['path'];rawasset=asset.read_bytes();assert digest(rawasset)==d['sourceSHA256']
 buf=gzip.decompress(rawasset);n,k=struct.unpack_from('<II',buf,12);assert k==0x4e4f534a
 glb=json.loads(buf[20:20+n]);blen,bkind=struct.unpack_from('<II',buf,20+n);assert bkind==0x004e4942;binary=buf[28+n:28+n+blen]
 original=read(RAW);originalbin=RAW.parent/original['buffers'][0]['uri'];rbin=originalbin.read_bytes()
 for key in ['nodes','scenes','materials']:assert original[key]==glb[key]
 assert len(original['meshes'])==len(glb['meshes'])==1
 assert len(original['meshes'][0]['primitives'])==len(glb['meshes'][0]['primitives'])==1
 spec=importlib.util.spec_from_file_location('original_attribute_reader',HERE/'xl-terrain-recovery-20261009-block37-authored-role.py');reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
 rp=original['meshes'][0]['primitives'][0];gp=glb['meshes'][0]['primitives'][0];ri=reader.accessor(original,rbin,rp['indices']).ravel();gi=reader.accessor(glb,binary,gp['indices']).ravel();assert len(ri)==len(gi)==11598*3
 attributes={}
 for name in ['POSITION','NORMAL','COLOR_0']:
  a=reader.accessor(original,rbin,rp['attributes'][name])[ri];b=reader.accessor(glb,binary,gp['attributes'][name])[gi];assert np.array_equal(a,b)
  attributes[name]={'expandedOriginalTriangleStreamSHA256':digest(a.tobytes()),'packedEqualsOriginal':True}
 provider=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-provider-exterior-provenance'
 receipt=read(provider/'receipt.json');pdf=provider/'government-nontextured-exterior-information-sheet.pdf';assert digest(pdf.read_bytes())==receipt['sha256']
 assert r['modelId']=='B156592961802063C0' and r['source']['building']['structureType']=='Podium'
 role={'role':'original-provider-exterior-ground-crossing-walls','uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'modelId':r['modelId'],'originalFaceCount':11598,'wallFaces':d['affectedWallFaces'],
  'providerExteriorProvenanceBinding':{'governmentExteriorProductSpecification':ref(pdf),'retrievalReceipt':ref(provider/'receipt.json'),'originalProviderGLTF':ref(RAW),'originalProviderBinary':ref(originalbin),'originalAttributes':attributes,'originalHierarchySHA256':digest(json.dumps({k:original[k] for k in ['nodes','scenes','materials']},sort_keys=True,separators=(',',':')).encode()),'exactPackedSourceStreams':source_stream_binding(rawasset),'modelSubtype':'02 podium','modelLevel':'3C LOD3','currentExactSourceIdentity':ref(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-current-inputs-v2/indexed-preflight.json')},
  'qualification':'Provider product and original source prove an exterior podium model, not basement or watertight solid certification. Exact independently frozen 14 original steep ground-crossing wall faces connect to original clear roofs; four original winding conflicts remain. Current complete foreign/ground and independent physical acceptance are separate.'}
 paths=[Path(__file__),RAW,originalbin,asset,pdf,provider/'receipt.json',ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-wall-context/diagnostic.json.gz',HERE/'xl_source_stream_binding_20261009.py',HERE/'xl-terrain-recovery-20261009-block37-authored-role.py']
 save(DOC/'expected-role.json',role);save(DOC/'original-source-provenance.json',{'uid':d['uid'],'evidenceRefs':[ref(p) for p in paths],'sourceGeometryChanges':0,'installationApproved':False,'publication':False})
 print(json.dumps({'uid':d['uid'],'originalAttributesEqualPacked':True,'wallFaces':len(role['wallFaces']),'wholeFaces':11598}),flush=True)
if __name__=='__main__':main()

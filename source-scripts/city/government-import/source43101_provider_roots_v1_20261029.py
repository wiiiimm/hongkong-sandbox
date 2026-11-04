"""Trace both packed scene roots to unchanged provider GLTF; diagnostics only."""
import copy
import gzip
import json
import struct
import zipfile
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-after-sha-tin-43101-provider-roots-v1-20261029'

def glb(doc,binary,root=None):
    value=copy.deepcopy(doc);value['buffers']=[dict(byteLength=len(binary))]
    if root is not None:value['scenes'][value.get('scene',0)]['nodes']=[root]
    data=json.dumps(value,separators=(',',':')).encode();data+=b' '*((-len(data))%4)
    binary+=b'\0'*((-len(binary))%4)
    raw=struct.pack('<III',0x46546c67,2,28+len(data)+len(binary))+struct.pack('<II',len(data),0x4e4f534a)+data+struct.pack('<II',len(binary),0x004e4942)+binary
    return gzip.compress(raw,mtime=0)

def main():
    out=BASE/BATCH;assert not out.exists()
    cap=BASE/'government-xl-after-sha-tin-four-source-fit-selection-v1-20261029';_,pins=authenticate(cap);selection=cap/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
    row=next(r for r in read(selection)['rows']if r['uid']=='landsd/43101:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    folder=HERE/'local/government-xl-held-component-recovery-20261008/government-source/8-SW-11C';archive=folder/'original/8-SW-11C.zip';record=folder/'original/download.json';download=read(record);assert archive.stat().st_size==download['bytes']and digest(archive.read_bytes())==download['sha256']
    member=row['native']['model']['sourceEntry'];sourcepath=folder/'decoded'/member
    with zipfile.ZipFile(archive)as z:
        source_bytes=z.read(member);assert sourcepath.read_bytes()==source_bytes
        source=json.loads(source_bytes);assert len(source['buffers'])==1
        buffer_name=str(Path(member).parent/source['buffers'][0]['uri']);binary=z.read(buffer_name);assert len(binary)==source['buffers'][0]['byteLength']
        source_crc=z.getinfo(member).CRC;binary_crc=z.getinfo(buffer_name).CRC
    packed_raw=gzip.decompress(asset.read_bytes());size,kind=struct.unpack_from('<II',packed_raw,12);assert kind==0x4e4f534a;packed=json.loads(packed_raw[20:20+size]);packed_binary=packed_raw[28+size:]
    roots=source['scenes'][source.get('scene',0)]['nodes'];proots=packed['scenes'][packed.get('scene',0)]['nodes'];names=[source['nodes'][i]['name']for i in roots];assert names==[packed['nodes'][i]['name']for i in proots]==['B4561111',row['modelId']]
    original=decode_original_world_triangles(glb(source,binary));converted=decode_original_world_triangles(asset.read_bytes());same=np.array_equal(original,converted);assert len(original)==len(converted)==row['triangles']
    per_root=[]
    for i,j in zip(roots,proots):
        a=decode_original_world_triangles(glb(source,binary,i));b=decode_original_world_triangles(glb(packed,packed_binary,j));equal=np.array_equal(a,b)
        per_root.append(dict(name=source['nodes'][i]['name'],completeFaces=len(a),sourceWorldBounds=[a.min((0,1)).tolist(),a.max((0,1)).tolist()],providerAndPackedWorldArraysEqual=equal,providerWorldSHA256=digest(a.astype('<f8').tobytes()),packedWorldSHA256=digest(b.astype('<f8').tobytes())))
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],originalSourceEntry=member,selectedArchiveSHA256=download['sha256'],originalGLTFSHA256=digest(source_bytes),originalBinarySHA256=digest(binary),originalMemberCRC32=source_crc,binaryMemberCRC32=binary_crc,sceneRoots=names,completeOriginalFaces=len(original),allProviderAndPackedWorldArraysEqual=same,roots=per_root,extraRootIsProviderAuthored=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,identityAccepted=False,installationApproved=False,publication=False,semanticCounterpartIdentityPending=True,qualification='Both scene roots, including B4561111, exist in the original cached provider GLTF, independently CRC-read from its checksum-verified selected ZIP. Full and per-root world-coordinate arrays are compared with the frozen packed original. This traces authorship and rules out an accidentally introduced packing root if equality holds; it does not identify the counterpart current structure, approve footprint scope, suppression, physical placement or installation.')
    save(out/'summary.json',result)
    refs=[Path(__file__),cap/'result.json',selection,asset,record,archive,sourcepath,sourcepath.parent/source['buffers'][0]['uri'],HERE/'exact_packed_world_geometry_20261009.py']
    module('provider_two_roots_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'provider-authored-two-root-original-packing-equivalence',refs,result)
    print(dict(allWorldArraysEqual=same,perRoot=[(r['name'],r['completeFaces'],r['providerAndPackedWorldArraysEqual'])for r in per_root]),flush=True)
if __name__=='__main__':main()

"""Acquire exact A0 GLTF/binary for root/geometry diagnostics; no installation.

Preserves source bytes. No texture downloads, modelling, source acceptance or
replacement of the existing C0 source. Payload transfer is capped at 1 MB.
"""
import argparse,json,struct,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from bounded_zip_directory_v1_20261103 import parse_window
from source43101_provider_roots_v1_20261029 import glb
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-source43101-individual-original-probe-v2-20261103'
DIRECTORY='government-xl-source43101-fresh-directories-v2-20261103'
UID='landsd/43101:0'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        claim=reservations.claim('source43101-individual-probe-'+str(uuid.uuid4()),['building:'+UID,'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    _,pins=authenticate(BASE/DIRECTORY);summary=BASE/DIRECTORY/'summary.json'
    assert digest(summary.read_bytes())==pins[str(summary.relative_to(ROOT))]
    d=read(summary);assert d['completeBoundedFreshSearch'] and not d['errors']
    r=next(r for r in d['rows'] if r['family']=='individualised' and r['format']=='Format_glTF')
    candidates=r['exactGeoRefNativeModels'][UID];assert len(candidates)==1
    model=candidates[0];assert model['modelId']=='B456572683001063A0' and model['geoRefNo']=='4565726830'
    directory=BASE/DIRECTORY/'directories/individualised/8-SW-11C/Format_glTF/zip-directory.bin'
    raw=directory.read_bytes();assert digest(raw)==r['directorySHA256']==pins[str(directory.relative_to(ROOT))]
    entries={e.filename:e for e in parse_window(raw,r['centralDirectoryOffset'],r['archiveBytes'],r)}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==d['currentManifestSHA256']
    net=ac.Network(out/'transfer.json',cap=1_000_000);_,head=net.get(r['sourceURL'],0,method='HEAD')
    assert head.get('ETag')==r['etag'] and int(head['Content-Length'])==r['archiveBytes']
    payloads={};refs=[Path(__file__),BASE/DIRECTORY/'result.json',summary,directory,manifest,HERE/'bounded_zip_directory_v1_20261103.py',HERE/'source43101_provider_roots_v1_20261029.py',HERE/'exact_packed_world_geometry_v2_20261103.py']
    for member in model['members']:
        entry=entries[member['name']];assert entry.CRC==member['crc32'] and entry.header_offset==member['headerOffset']
        assert entry.compress_size==member['compressedBytes'] and entry.file_size==member['decodedBytes']
        at=entry.header_offset;header,_=net.get(r['sourceURL'],30,f'{at}-{at+29}',r['etag'])
        fields=struct.unpack('<4s5H3L2H',header);assert fields[0]==b'PK\x03\x04'
        length=30+fields[-2]+fields[-1]+entry.compress_size
        packed,_=net.get(r['sourceURL'],length,f'{at}-{at+length-1}',r['etag'])
        value=ac.unpack_member(packed,entry);path=local/'provider'/Path(entry.filename).name
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value);refs.append(path);payloads[path.suffix]=(path,value)
    source=json.loads(payloads['.gltf'][1]);binary=payloads['.bin'][1]
    assert len(source['buffers'])==1 and source['buffers'][0]['uri']==payloads['.bin'][0].name
    assert source['buffers'][0]['byteLength']==len(binary)
    roots=source['scenes'][source.get('scene',0)]['nodes'];whole=decode_original_world_triangles(glb(source,binary));rows=[]
    for root in roots:
        tri=decode_original_world_triangles(glb(source,binary,root));rows.append(dict(name=source['nodes'][root].get('name'),faces=len(tri),worldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],worldSHA256=digest(tri.astype('<f8').tobytes())))
    _,after=net.get(r['sourceURL'],0,method='HEAD');assert after.get('ETag')==r['etag'] and int(after['Content-Length'])==r['archiveBytes']
    assert reservations.owns(lease) and digest(manifest.read_bytes())==mh
    result=dict(uids=[UID],modelId=model['modelId'],currentManifestSHA256=mh,sourceETag=r['etag'],sourceRevision=r['revision'],originalGLTFSHA256=digest(payloads['.gltf'][1]),originalBinarySHA256=digest(binary),sceneRoots=rows,completeFaces=len(whole),worldBounds=[whole.min((0,1)).tolist(),whole.max((0,1)).tolist()],receivedBytes=net.data['receivedBytes'],texturePayloadRequests=0,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,installationApproved=False,publication=False,permanentRejection=False,qualification=__doc__)
    save(out/'summary.json',result);refs.extend(p for p in out.rglob('*') if p.is_file())
    module('source43101_individual_original_probe_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-individualised-original-root-and-geometry-probe',refs,result)
    print(dict(sceneRoots=rows,completeFaces=len(whole),receivedBytes=net.data['receivedBytes']),flush=True)


if __name__=='__main__':main()

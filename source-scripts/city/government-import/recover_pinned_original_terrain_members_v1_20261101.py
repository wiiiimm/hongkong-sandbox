"""Recover only exact pinned government terrain members with bounded HTTP ranges.

Reuse the acquisition Network byte ledger, ZIP parser and CRC decoder. Every
output must match native-stage SHA256; current provider bytes grant no approval.
"""
import argparse, sys, uuid, struct, shutil
from pathlib import Path, PurePosixPath
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','capture','uid']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.capture])
    out=BASE/a.batch;local=HERE/'local'/a.batch;control=HERE/'local'/(a.batch+'-lease');lp=control/'reservation.json'
    assert not out.exists()and not local.exists()
    if not a.owned:
        assert not control.exists()
        c=reservations.claim('pinned-original-terrain-'+str(uuid.uuid4()),['building:'+a.uid,'immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    _,pins=authenticate(BASE/a.capture);selected=BASE/a.capture/'selection.json.gz';assert digest(selected.read_bytes())==pins[str(selected.relative_to(ROOT))]
    source=next(r for r in read(selected)['rows']if r['uid']==a.uid)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(source['native']['cacheKey'],)).fetchone()
    assert sha==source['native']['resultSha']
    records=native['terrain'];expected={}
    for record in records:
        assert record['sourceEntry']in record['sourceHashes']
        for name,h in record['sourceHashes'].items():
            q=PurePosixPath(name);assert not q.is_absolute()and'..'not in q.parts and q.parts[0].startswith('TERRAIN')and q.suffix in ['.gltf','.bin']
            assert name not in expected or expected[name]==h;expected[name]=h
    assert expected
    index=HERE.parent/'landmark-acquisition/index.json';sheet=source['candidate']['entry']['sourceTile']
    attrs=next(r['attributes']for r in read(index)['features']if r['attributes']['SHEETNO']==sheet)
    tool=HERE.parent/'landmark-acquisition/acquire.py';acquisition=module('pinned_terrain_range_acquisition',tool)
    assert shutil.disk_usage(ROOT).free>=3*1024**3
    network=acquisition.Network(local/'network.json',cap=8_000_000)
    url=attrs['Format_glTF'];_,headers=network.get(url,0,method='HEAD');etag=headers.get('ETag');assert etag
    size=int(headers['Content-Length']);tail,received=network.get(url,65536,'-65536',etag)
    end=tail.rfind(b'PK\x05\x06');assert end>=0
    fields=struct.unpack('<4s4H2LH',tail[end:end+22]);offset=fields[6];start=int(received['Content-Range'].split()[1].split('-')[0]);assert int(received['Content-Range'].split('/')[-1])==size
    if offset<start:
        prefix,_=network.get(url,start-offset,f'{offset}-{start-1}',etag);directory=prefix+tail
    else:directory=tail[offset-start:]
    infos,check=acquisition.parse_directory(directory);directorypath=local/'zip-directory.bin';directorypath.write_bytes(directory)
    byname={r.filename:(i,r)for i,r in enumerate(infos)};rows=[];refs=[Path(__file__),tool,index,BASE/a.capture/'result.json',selected,directorypath]
    for name,h in sorted(expected.items()):
        assert reservations.owns(lease)
        if name not in byname:rows.append(dict(sourceEntry=name,state='pinned-member-absent-in-current-directory',expectedSHA256=h));continue
        i,entry=byname[name];stop=(infos[i+1].header_offset if i+1<len(infos)else check['centralDirectoryOffset'])-1
        raw,_=network.get(url,stop-entry.header_offset+1,f'{entry.header_offset}-{stop}',etag)
        value=acquisition.unpack_member(raw,entry);actual=digest(value)
        if actual!=h:
            rows.append(dict(sourceEntry=name,state='current-source-revision-does-not-match-pinned-member',expectedSHA256=h,observedSHA256=actual));continue
        path=local/'decoded'/name;path.parent.mkdir(parents=True,exist_ok=True);assert not path.exists();path.write_bytes(value);refs.append(path)
        rows.append(dict(sourceEntry=name,state='exact-original-restored',sha256=h,bytes=len(value),crc32=entry.CRC,path=str(path.relative_to(ROOT))))
    assert reservations.owns(lease);refs.append(local/'network.json')
    result=dict(uids=[a.uid],sheet=sheet,sourceSHA256=source['sourceSHA256'],nativeCacheKey=source['native']['cacheKey'],nativeResultSHA256=sha,rows=rows,allExactOriginalTerrainRestored=all(r['state']=='exact-original-restored'for r in rows),downloadedBytes=network.data['receivedBytes'],capBytes=8_000_000,sourceArchiveBytes=size,fullArchiveDownloaded=False,sourceGeometryChanges=0,publicTerrainEdits=False,installationApproved=False,publication=False)
    save(out/'summary.json',result)
    module('pinned_original_terrain_range_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-native-stage-sha256-original-terrain-member-range-recovery',refs,result)
    print(dict(uid=a.uid,allExactOriginalTerrainRestored=result['allExactOriginalTerrainRestored'],downloadedBytes=result['downloadedBytes']),flush=True)
if __name__=='__main__':main()

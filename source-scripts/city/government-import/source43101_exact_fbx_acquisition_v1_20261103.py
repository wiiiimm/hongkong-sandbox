"""Acquire two exact official FBX alternatives under one 1 MB transfer ledger.

Original byte acquisition only. No texture requests, model editing, conversion,
identity acceptance or publication. Reuse the completed ETag-bound directories.
"""
import argparse, shutil, struct, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v2_20261103 import execute_reserved
from bounded_zip_directory_v1_20261103 import parse_window
sys.path.insert(0,str(HERE.parent/'citywide-source'))
from discover import ac
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-source43101-exact-fbx-acquisition-v1-20261103'
DIRECTORY='government-xl-source43101-fresh-directories-v2-20261103'
UID='landsd/43101:0'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out,local=BASE/BATCH,HERE/'local'/BATCH;lp=local/'reservation.json'
    if not a.owned:
        assert not out.exists() and not local.exists()
        claim=reservations.claim('source43101-exact-fbx-'+str(uuid.uuid4()),['building:'+UID,'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
        assert claim['ok'],claim
        return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    _,pins=authenticate(BASE/DIRECTORY);sp=BASE/DIRECTORY/'summary.json';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))]
    summary=read(sp);assert summary['completeBoundedFreshSearch'] and not summary['errors']
    refs=[Path(__file__),BASE/DIRECTORY/'result.json',sp,HERE/'bounded_zip_directory_v1_20261103.py',HERE.parent/'landmark-acquisition/acquire.py']
    targets=[]
    for family,suffix in [('package','C0'),('individualised','A0')]:
        row=next(r for r in summary['rows']if r['family']==family and r['format']=='Format_FBX')
        path=BASE/DIRECTORY/'directories'/family/'8-SW-11C/Format_FBX/zip-directory.bin'
        raw=path.read_bytes();assert digest(raw)==row['directorySHA256']==pins[str(path.relative_to(ROOT))];refs.append(path)
        model='B456572683001063'+suffix;name='BUILDING/'+model+'/'+model+'.fbx'
        assert [s for s in row['exactGeoRefMembers'][UID]if s.endswith('.fbx')]==[name]
        entries=[e for e in parse_window(raw,row['centralDirectoryOffset'],row['archiveBytes'],row)if e.filename==name];assert len(entries)==1
        targets.append((row,model,entries[0]))
    maximum=sum(30+65535*2+e.compress_size for _,_,e in targets)
    # Actual local-header lengths are checked before each bounded body request.
    assert sum(e.compress_size for _,_,e in targets)<1_000_000
    assert shutil.disk_usage(local.parent).free>2*sum(e.file_size for _,_,e in targets)+1_000_000
    net=ac.Network(out/'transfer.json',cap=1_000_000);rows=[]
    for source,model,entry in targets:
        assert reservations.owns(lease)
        _,head=net.get(source['sourceURL'],0,method='HEAD');assert head.get('ETag')==source['etag'] and int(head['Content-Length'])==source['archiveBytes']
        at=entry.header_offset;header,_=net.get(source['sourceURL'],30,f'{at}-{at+29}',source['etag'])
        fields=struct.unpack('<4s5H3L2H',header);assert fields[0]==b'PK\x03\x04'
        size=30+fields[-2]+fields[-1]+entry.compress_size
        packed,_=net.get(source['sourceURL'],size,f'{at}-{at+size-1}',source['etag'])
        raw=ac.unpack_member(packed,entry);assert len(raw)==entry.file_size
        path=local/'provider'/source['family']/(model+'.fbx');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);refs.append(path)
        _,after=net.get(source['sourceURL'],0,method='HEAD');assert after.get('ETag')==source['etag'] and int(after['Content-Length'])==source['archiveBytes']
        rows.append(dict(uid=UID,modelId=model,family=source['family'],sourcePath=str(path.relative_to(ROOT)),sourceSHA256=digest(raw),originalSourceEntry=entry.filename,originalCRC32=entry.CRC,decodedBytes=entry.file_size,compressedBytes=entry.compress_size,sourceURL=source['sourceURL'],sourceETag=source['etag'],sourceRevision=source['revision'],sourceArchiveBytes=source['archiveBytes'],sourceHeaderOffset=entry.header_offset,isBinaryFBX=raw.startswith(b'Kaydara FBX Binary'),sourceGeometryChanges=0,sourcePoseChanges=0))
    assert reservations.owns(lease)
    save(out/'untouched-current-fbx-sources.json',dict(rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0))
    result=dict(uids=[UID],rows=rows,receivedBytes=net.data['receivedBytes'],capBytes=1_000_000,texturePayloadRequests=0,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,installationApproved=False,publication=False,permanentRejection=False,qualification=__doc__,historicalDirectoryManifestSHA256=summary['currentManifestSHA256'],mapAcceptanceNotEvaluated=True)
    save(out/'summary.json',result);refs.extend(p for p in out.rglob('*')if p.is_file())
    module('source43101_exact_fbx_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-fbx-alternative-acquisition',refs,result)
    print(dict(receivedBytes=net.data['receivedBytes'],models=[r['modelId']for r in rows],sourceGeometryChanges=0),flush=True)

if __name__=='__main__':main()

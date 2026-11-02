"""Probe bounded original dated orthophoto headers; never download a full archive."""
import sys,uuid,struct,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-source43101-dated-orthophoto-header-v1-20261103';PARENT='government-xl-source43101-dated-orthophoto-index-v1-20261103'
def owned():
    local=HERE/'local'/BATCH;out=BASE/BATCH;lease=read(local/'reservation.json');assert reservations.owns(lease)and shutil.disk_usage(local.parent).free>2_000_000;_,pins=authenticate(BASE/PARENT);p=BASE/PARENT/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];parent=read(p);assert len(parent['coveringFeatures'])==1;attrs=parent['coveringFeatures'][0]['attributes'];assert attrs['SHEETNO']=='T8-SW-C'and attrs['YEAR_OF_RELEASE']==2025;url=attrs['DOWNLOAD_LINK'];assert url.startswith('https://open.hkmapservice.gov.hk/OpenData/directDownload?');refs=[Path(__file__),HERE.parent/'landmark-acquisition/acquire.py',BASE/PARENT/'result.json',p];net=ac.Network(out/'transfer.json',cap=200000)
    _,headers=net.get(url,0,method='HEAD');assert reservations.owns(lease);etag=headers.get('ETag');prefix=None;error=None
    try:prefix,prefix_headers=net.get(url,65536,span='0-65535',etag=etag)
    except Exception as e:error=dict(errorClass=type(e).__name__,httpCode=getattr(e,'code',None),boundedRangeFailed=True)
    parsed={}
    if prefix is not None:
        q=out/'original-prefix.bin';q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(prefix);refs.append(q);parsed['magicHex']=prefix[:16].hex()
        if prefix[:4]==b'PK\x03\x04':
            fields=struct.unpack('<4s5H3L2H',prefix[:30]);name=prefix[30:30+fields[-2]].decode('utf8');offset=30+fields[-2]+fields[-1];parsed.update(kind='zip-local-header',firstMemberName=name,firstMemberCompressionMethod=fields[3],firstMemberFlags=fields[2],firstMemberDataOffset=offset,firstMemberDeclaredCompressedBytes=fields[7],firstMemberDeclaredRawBytes=fields[8],firstMemberDataMagicHex=prefix[offset:offset+16].hex())
        elif prefix[:2]in [b'II',b'MM']:parsed.update(kind='tiff-family',headerVersion=int.from_bytes(prefix[2:4],'little'if prefix[:2]==b'II'else'big'))
        else:parsed['kind']='other-response'
    result=dict(uids=parent['uids'],sourceSHA256=parent['sourceSHA256'],officialIndexAttributes=attrs,downloadURL=url,headHeaders=headers,prefixParsed=parsed,rangeError=error,receivedBytes=net.data['receivedBytes'],capBytes=200000,fullArchiveDownloaded=False,modelGeometryChanges=0,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,installationApproved=False,publication=False,permanentRejection=False,qualification='HEAD and at most64KiB range from the exact official dated orthophoto index link. Header planning only; no full raster/ZIP read, no dated pixel interpretation or XYZ image-date transfer, no model acceptance.')
    save(out/'summary.json',result);refs.extend(q for q in out.iterdir()if q.is_file());assert reservations.owns(lease);module('source43101_dated_raster_header_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-official-dated-raster-header-context',list(dict.fromkeys(refs)),result);print(dict(receivedBytes=net.data['receivedBytes'],headers=headers,parsed=parsed,rangeError=error),flush=True)
if __name__=='__main__':
    if '--owned'in sys.argv:owned()
    else:
        assert not(BASE/BATCH).exists()and not(HERE/'local'/BATCH).exists();c=reservations.claim('source43101-dated-raster-header-'+str(uuid.uuid4()),['building:landsd/43101:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],'Source reservation unavailable';execute_reserved(c['reservation'],HERE/'local'/BATCH/'reservation.json',[sys.executable,__file__,'--owned'])

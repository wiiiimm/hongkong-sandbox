"""Check exact provider bytes behind a failed native parser; no model repair."""
import sys,uuid,copy,json,zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';UID='landsd/254814:0';MID='B317931646001063C0'
BATCH='government-xl-industrial254814-current-original-parser-failure-probe-v1-20261101'
PREVIOUS='government-xl-harbour-one-industrial-neighbour-originals-v1-20261101'
def main():
    out=BASE/BATCH;local=HERE/'local'/BATCH;lp=HERE/'local'/(BATCH+'-lease')/'reservation.json'
    assert not out.exists()and not local.exists()
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('industrial-source-byte-probe-'+str(uuid.uuid4()),['building:'+UID,'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    _,pins=authenticate(BASE/PREVIOUS);selectionpath=BASE/PREVIOUS/'selection.json.gz'
    assert digest(selectionpath.read_bytes())==pins[str(selectionpath.relative_to(ROOT))]
    row=next(r for r in read(selectionpath)['missing']if r['uid']==UID);form=row['currentSource'];assert form['building']['buildingCSUID'][:10]==MID[1:11]
    tile=ROOT/'3d-viewer'/form['tile'];assert digest(tile.read_bytes())==form['tileSHA256']and next(r for r in read(tile)['buildings']if r['uid']==UID)==form['building']
    folder=HERE/'local'/PREVIOUS/'sheets/11-SW-7A/directory';directorypath=folder/'result.json';rawpath=folder/'zip-directory.bin'
    for p in [directorypath,rawpath]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
    directory=read(directorypath);models=[m for m in directory['models']if m['modelId']==MID];assert len(models)==1
    directory=copy.deepcopy(directory);directory['models']=models
    helper=module('industrial_failed_source_download',HERE.parent/'citywide-native/download.py')
    receipt=helper.acquire(directory,rawpath,local/'original')
    archive=local/'original'/('11-SW-7A.zip');assert digest(archive.read_bytes())==receipt['sha256']
    rawrows=[]
    with zipfile.ZipFile(archive)as z:
        for member in models[0]['members']:
            raw=z.read(member['name']);assert len(raw)==member['decodedBytes']
            p=local/'original-members'/member['name'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            parse=None
            if member['name'].endswith('.gltf'):
                try:json.loads(raw);parse='parsed-json'
                except (ValueError,UnicodeError)as error:parse=type(error).__name__+': '+str(error)
            rawrows.append(dict(sourceEntry=member['name'],sha256=digest(raw),bytes=len(raw),zeroBytes=raw.count(0),nonWhitespaceNonzeroBytes=sum(v not in [0,9,10,13,32]for v in raw),sourceCRC32=member['crc32'],jsonParse=parse,path=str(p.relative_to(ROOT))))
    key=row['profiles'][0][0]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()
    old=next(r for r in native['models']if r['modelId']==MID);assert old['state']=='failed'
    assert reservations.owns(lease)
    result=dict(uids=[UID],modelId=MID,sourceTile='11-SW-7A',nativeCacheKey=key,nativeResultSHA256=sha,rawNativeFailure=old,rows=rawrows,downloadedBytes=receipt['newThisInvocationBytes'],providerETag=directory['etag'],rawDirectorySHA256=directory['directorySHA256'],providerFilesContainOnlyNulAndWhitespace=all(r['nonWhitespaceNonzeroBytes']==0 for r in rawrows),sourceGeometryChanges=0,repairAttempted=False,installationApproved=False,publication=False,permanentRejection=False,qualification='Current original government ZIP ranges pass provider directory CRC and length verification. Parser failure is tested on those exact original bytes; no geometry/data bytes changed. This source-only diagnostic neither rejects Harbour One nor claims all provider revisions unavailable. Keep the existing BASIC actor.')
    save(out/'summary.json',result)
    refs=[Path(__file__),BASE/PREVIOUS/'result.json',selectionpath,tile,directorypath,rawpath,HERE.parent/'citywide-native/download.py',HERE.parent/'landmark-acquisition/acquire.py',*[p for p in local.rglob('*')if p.is_file()]]
    module('industrial_provider_byte_failure_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-provider-member-parser-failure-diagnostic-no-geometry-repair',refs,result)
    print(dict(providerNulPlaceholder=result['providerFilesContainOnlyNulAndWhitespace'],downloadedBytes=result['downloadedBytes']),flush=True)
if __name__=='__main__':main()

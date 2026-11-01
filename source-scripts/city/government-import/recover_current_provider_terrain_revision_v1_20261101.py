"""Acquire a separately identified current original TIN after an old member miss.

Never relabel current bytes as the pinned historical terrain or edit old native
records. No terrain transformation, placement approval, optimisation or publish.
"""
import argparse,sys,uuid,zipfile,datetime
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','previous-recovery']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.previous_recovery])
    out=BASE/a.batch;local=HERE/'local'/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json'
    assert not out.exists()and not local.exists()
    previous,pins=authenticate(BASE/a.previous_recovery);assert len(previous['uids'])==1 and not previous['allExactOriginalTerrainRestored'];uid=previous['uids'][0]
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('current-original-terrain-revision-'+str(uuid.uuid4()),['building:'+uid,'immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    refs=[Path(__file__),BASE/a.previous_recovery/'result.json'];oldlocal=HERE/'local'/a.previous_recovery
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    old=take(BASE/a.previous_recovery/'summary.json');net=take(oldlocal/'network.json');directorypath=oldlocal/'zip-directory.bin';assert digest(directorypath.read_bytes())==pins[str(directorypath.relative_to(ROOT))];refs.append(directorypath)
    head=next(r for r in net['requests']if r['method']=='HEAD'and r['status']=='complete');sheet=old['sheet']
    index=HERE.parent/'landmark-acquisition/index.json';attrs=next(r['attributes']for r in read(index)['features']if r['attributes']['SHEETNO']==sheet);refs.append(index)
    assert head['url']==attrs['Format_glTF'];etag=head['headers']['ETag'];revision=datetime.datetime.fromtimestamp(attrs['REVISIONDATE']/1000,datetime.timezone.utc).isoformat()
    downloader=module('current_original_terrain_revision_download',HERE.parent/'citywide-native/download.py')
    infos,_=downloader.ac.parse_directory(directorypath.read_bytes());current_names={e.filename for e in infos if e.filename.startswith('TERRAIN')and e.filename.endswith(('.gltf','.bin'))};assert current_names
    old_names={r['sourceEntry']for r in old['rows']};assert current_names!=old_names,'This route records a distinct current revision, not a historical-byte restoration'
    directory=dict(sheet=sheet,sourceURL=head['url'],etag=etag,revision=revision,archiveBytes=old['sourceArchiveBytes'],directorySHA256=digest(directorypath.read_bytes()),models=[])
    download=downloader.acquire(directory,directorypath,local/'original',include_terrain=True)
    archive=local/'original'/(sheet+'.zip');assert digest(archive.read_bytes())==download['sha256'];rows=[]
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==current_names
        for name in sorted(current_names):
            raw=z.read(name);path=local/'decoded'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
            rows.append(dict(sourceEntry=name,path=str(path.relative_to(ROOT)),sha256=digest(raw),bytes=len(raw),crc32=z.getinfo(name).CRC))
    assert reservations.owns(lease)
    result=dict(uids=[uid],sheet=sheet,currentProviderOriginalTerrain=rows,sourceTerrainPaths=[r['path']for r in rows if r['sourceEntry'].endswith('.gltf')],providerETag=etag,providerDirectorySHA256=directory['directorySHA256'],providerRevision=revision,previousPinnedTerrainMembers=old['rows'],historicalNativeTerrainRestored=False,historicalNativeRecordsChanged=False,currentTerrainIsDistinctSourceIdentity=True,downloadedBytes=download['newThisInvocationBytes'],sourceBuildingSHA256=old['sourceSHA256'],sourceBuildingGeometryChanges=0,sourceBuildingPoseChanges=0,terrainGeometryTransformed=False,publicTerrainEdits=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Separately identified current provider terrain glTF/bin originals, verified using ETag-conditioned bounded ranges and original ZIP CRCs. Keep historical missing-member proof and old native terrain identities unchanged. Fresh frame, coverage, complete source/scene physical, runtime, browser and publication checks required before use. No acceptance transfer.')
    save(out/'summary.json',result);refs.extend([HERE.parent/'citywide-native/download.py',HERE.parent/'landmark-acquisition/acquire.py',*[f for f in local.rglob('*')if f.is_file()]])
    module('current_original_terrain_revision_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'separate-current-original-provider-terrain-revision-acquisition-no-acceptance',refs,result)
    print(dict(uid=uid,currentOriginalTerrainMembers=len(rows),downloadedBytes=result['downloadedBytes'],historicalNativeRecordsChanged=False),flush=True)
if __name__=='__main__':main()

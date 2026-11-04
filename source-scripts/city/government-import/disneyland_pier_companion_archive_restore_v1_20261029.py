"""Restore one exact archived original for investigation; no identity acceptance."""
import json, os, shutil, sys, tarfile, uuid, zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH='government-xl-disneyland-pier-74189-archive-restore-v1-20261029'
SELECTION='government-xl-disneyland-piers-current-selection-v1-20261029'
MODEL='B227921867901062G0'
SHA='5447be08a0649a83efc506fbc1b5e33cdeaffe60642c64f2672b66c92fc65150'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;local=HERE/'local'/BATCH
    assert not doc.exists()
    _,pins=authenticate(base/SELECTION);path=base/SELECTION/'selection.json.gz'
    assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    source=read(path)['rows'][0]
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(source['native']['cacheKey'],)).fetchone()
    assert sha==source['native']['resultSha']
    models=[m for m in native['models'] if m['modelId']==MODEL];assert len(models)==1
    model=models[0];assert model['asset']['sha256']==SHA and model['asset']['bytes']==60901 and model['triangles']==6705
    artifacts=[a for a in native['artifacts'] if a['kind']=='original-and-prepared-sheet'];assert len(artifacts)==1
    sys.path.insert(0,str(HERE.parent/'landmark-resume'));sys.path.insert(0,str(HERE.parent/'citywide-native'))
    from r2_snapshot import R2Store,verify_object
    from source_cache import validate_artifact
    from dotenv import dotenv_values
    artifact=validate_artifact(artifacts[0]);assert artifact['bytes']==3275059
    # Retain the existing acquisition free-space floor, even for this small restore.
    assert shutil.disk_usage(ROOT).free>=3*1024**3
    for key,value in dotenv_values(ROOT/'.env.modelling').items():
        if key.startswith('R2_') and value and value!='[SENSITIVE]':os.environ.setdefault(key,value)
    local.mkdir(parents=True,exist_ok=True);bundle=local/(artifact['sha256']+'.tar.gz');refs=[]
    try:store=R2Store('hk-sandbox-assets')
    except (ImportError,ValueError):store=None
    if store is not None or bundle.exists():
        if bundle.exists():
            assert bundle.stat().st_size==artifact['bytes'] and digest(bundle.read_bytes())==artifact['sha256']
        else:verify_object(store,artifact['key'],artifact['sha256'],artifact['bytes'],bundle)
        with tarfile.open(bundle,'r:gz') as archive:
            members=[m for m in archive if Path(m.name).name==SHA+'.glb.gz'];assert len(members)==1 and members[0].isfile() and members[0].size==60901
            raw=archive.extractfile(members[0]).read();assert digest(raw)==SHA
        refs.append(bundle);method='verified-native-archive'
    else:
        # Existing public-source scanner/acquirer/converter, with pinned revision
        # and exact expected packed bytes. This needs no invented viewer match.
        sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
        import shape_prepare
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            prior=db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",('10-NE-21A',)).fetchone()[0]
        save(local/'pinned-directory.json',prior)
        claim=reservations.claim('pier-original-recovery-'+str(uuid.uuid4()),['building:landsd/74189:0','native-model:'+source['native']['cacheKey']+'/'+MODEL],batch=BATCH,ttl=3600);assert claim['ok']
        lease=claim['reservation']
        try:
            save(local/'reservation.json',json.loads(json.dumps(lease,default=str)))
            directory,_=shape_prepare.scan({'SHEETNO':'10-NE-21A','Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},local/'directory')
            assert directory['etag']==prior['etag'] and directory['directorySHA256']==prior['directorySHA256']
            directory['models']=[m for m in directory['models'] if m['modelId']==MODEL];assert len(directory['models'])==1 and reservations.owns(lease)
            shape_prepare.acquire(directory,local/'directory/zip-directory.bin',local/'original')
            packed=local/'packed';packed.mkdir(exist_ok=True)
            with zipfile.ZipFile(local/'original/10-NE-21A.zip') as archive:
                converted=shape_prepare._convert_one(archive,archive.getinfo(model['sourceEntry']),local/'decoded',packed,{}, {'modelId':MODEL})
            raw=shape_prepare.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),SHA)
            assert len(raw)==60901 and reservations.owns(lease)
            method='verified-pinned-government-source';refs.extend(p for p in local.rglob('*') if p.is_file() and p.suffix!='.zip' and p.name!='reservation.json')
        finally:assert reservations.release(lease)['ok']
    asset=local/(SHA+'.glb.gz');asset.write_bytes(raw)
    tri=decode_original_world_triangles(raw);assert len(tri)==6705
    assert tri.min((0,1)).tolist()==model['worldBounds'][0] and tri.max((0,1)).tolist()==model['worldBounds'][1]
    receipt=dict(uids=['landsd/74189:0'],modelId=MODEL,sourceSHA256=SHA,sourceFaces=len(tri),worldBounds=model['worldBounds'],assetPath=str(asset.relative_to(ROOT)),nativeCacheKey=source['native']['cacheKey'],nativeResultSHA256=sha,method=method,nativeArchiveNomination=artifact,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Exact original restored for companion/roof coverage investigation only. No candidate routing, duplicate suppression, geometry, pose, terrain or runtime changes.')
    save(doc/'summary.json',receipt);save(doc/'native-model.json',model)
    module('archive_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-pinned-pier-companion-restore-no-acceptance',[Path(__file__),path,base/SELECTION/'result.json',asset,*refs],receipt)

if __name__=='__main__':main()

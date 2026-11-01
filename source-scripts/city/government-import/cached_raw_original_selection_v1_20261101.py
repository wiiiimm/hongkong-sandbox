"""Recover one exact indexed packed asset from existing local government members.

The original members remain untouched. Existing converter and canonical-byte checks
must reproduce the pinned asset exactly; no model/placement acceptance transfers.
"""
import argparse,copy,io,json,sys,uuid,zipfile
from pathlib import Path,PurePosixPath
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import canonical_bytes,_convert_one

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','lookup','raw-gltf']:p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.lookup])
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
    _,pins=authenticate(base/a.lookup);lookup_path=base/a.lookup/'lookup.json';assert digest(lookup_path.read_bytes())==pins[str(lookup_path.relative_to(ROOT))];lookup=read(lookup_path);assert len(lookup['rows'])==1
    row=lookup['rows'][0];assert len(row['matches'])==1;match=row['matches'][0];uid=row['uid'];model=match['model'];entry=copy.deepcopy(model['candidate'])
    resources=sorted({'building:'+uid,'native-model:'+match['sourceKey']})
    if not a.owned:
        assert not local.exists();c=reservations.claim('cached-raw-original-'+str(uuid.uuid4()),resources,batch=a.batch,ttl=1800);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');found=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members n USING(cache_key) WHERE n.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,match['nativeCacheKey'])).fetchone()
        assert found and found[0]==match['nativeResultSHA256']and next(m for m in found[1]['models']if m['modelId']==model['modelId'])==model
    source=row['source'];tile=ROOT/'3d-viewer'/source['tile'];assert digest(tile.read_bytes())==source['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==uid)==source['building']
    assert entry['uid']==uid and entry['objectId']==source['building']['objectId']and entry['buildingCSUID']==source['building']['buildingCSUID']and entry['publicationApproved']is False and entry['placementReviewed']is False
    raw_path=(ROOT/a.raw_gltf).resolve();assert raw_path.is_relative_to(HERE/'local')and raw_path.name==model['modelId']+'.gltf';raw=raw_path.read_bytes();gltf=json.loads(raw)
    member=PurePosixPath(model['sourceEntry']);assert not member.is_absolute()and'..'not in member.parts and member.name==raw_path.name
    members={str(member):raw};refs=[Path(__file__),base/a.lookup/'result.json',lookup_path,tile,raw_path];raw_refs=[dict(path=str(raw_path.relative_to(ROOT)),sha256=digest(raw),member=str(member))]
    for buffer in gltf.get('buffers',[]):
        uri=PurePosixPath(buffer['uri']);assert not uri.is_absolute()and'..'not in uri.parts and':'not in str(uri)
        path=(raw_path.parent/str(uri)).resolve();assert path.is_relative_to(raw_path.parent);payload=path.read_bytes();assert len(payload)==buffer['byteLength'];name=str(member.parent/uri);assert name not in members;members[name]=payload;refs.append(path);raw_refs.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(payload),member=name))
    input_bytes=sum(len(v)for v in members.values());assert 0<input_bytes<=16*1024**2,'Bounded local-member conversion only; use existing acquisition policy for larger inputs'
    envelope=io.BytesIO()
    with zipfile.ZipFile(envelope,'w',compression=zipfile.ZIP_STORED)as archive:
        for name,payload in members.items():archive.writestr(name,payload)
    envelope.seek(0);packed=local/'packed';packed.mkdir();
    with zipfile.ZipFile(envelope)as archive:converted=_convert_one(archive,archive.getinfo(str(member)),local/'decoded',packed,{},dict(modelId=model['modelId']))
    initial=packed/converted['asset']['asset'];expected=model['asset'];value=canonical_bytes(initial.read_bytes(),expected['sha256']);assert len(value)==expected['bytes']and converted['triangles']==model['triangles']and converted['worldBounds']==model['worldBounds']
    target=packed/'assets'/(expected['sha256']+'.glb.gz');target.write_bytes(value);refs.extend([target,HERE.parent/'enhancement-screening/shape_prepare.py',HERE.parent/'citywide-native/convert.py']);assert digest(target.read_bytes())==entry['sha256']==expected['sha256']
    entry.update(rootTranslation=[-834500,0,816500],proceduralWindows=False)
    selected=dict(uid=uid,source=source,modelId=model['modelId'],triangles=model['triangles'],native=dict(cacheKey=match['nativeCacheKey'],resultSha=match['nativeResultSHA256'],model=model),candidate=dict(path=str(target.relative_to(ROOT)),entry=entry),originalGeometryOnly=True,sourceSHA256=expected['sha256'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest);save(out/'selection.json.gz',dict(rows=[selected],manifestSHA256=digest(manifest.read_bytes())));save(out/'conversion.json',converted)
    result=dict(uids=[uid],sourceSHA256ByUid={uid:expected['sha256']},recovered=1,downloads=0,conversions=1,localInputBytes=input_bytes,sourceMembers=raw_refs,existingArchiveRecoveryGuardChanged=False,remoteArchiveRestoreUsed=False,localEnvelopeOnly=True,originalGeometryOnly=True,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,publication=False,qualification=__doc__+' Existing GLTF and buffer bytes passed through the unchanged citywide-native converter using an in-memory member envelope capped16MiB. Exact pinned packed SHA/byte count, complete raw world bounds and triangle count reproduced. No archive download/restoration, acquisition guard changes, simplification, source reauthoring or approval.')
    assert reservations.owns(lease);save(out/'summary.json',result);module('cached_raw_original_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-indexed-original-recovery-from-existing-local-members',refs,result)
    print(dict(recovered=1,triangles=model['triangles'],bytes=len(value),downloads=0,installationApproved=False),flush=True)
if __name__=='__main__':main()

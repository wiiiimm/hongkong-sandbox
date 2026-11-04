"""Recover the exact unmatched low original; no viewer identity assignment or approval."""
import sys, uuid, zipfile
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module
from observed_reserved_runner_v4_20261103 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-tung-cheong-low223636-exact-original-recovery-v1-20261103'
KEY='a04c53795d53db1d54dd224b5d4b2b9091855f5b8525f82753a981f88bc08438'
MID='B339081144201063C0'
SHA='b980c1f30da1c162f1e961eb8c17df7b64fde72de89de59d5add13ab24c86eda'
RESULT='b8416aba5019dd70d0c3d8c5141c2f854a27f28c707ac179dbb56eabd0a60262'

def main():
    out=ROOT/'docs/astra-city/government-import'/BATCH
    local=HERE/'local'/BATCH; lp=local/'reservation.json'
    assert not out.exists()
    if '--owned' not in sys.argv:
        assert not local.exists()
        c=reservations.claim('tung-cheong-low-original-'+str(uuid.uuid4()),['building:landsd/223636:0','immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
        assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        sha,record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(KEY,)).fetchone()
        assert sha==RESULT
        model=next(m for m in record['models']if m['modelId']==MID)
    assert model['asset']['sha256']==SHA and model['triangles']==44 and model['state']=='source-match-held'
    assert not model['matching']['viewerMatches'] and not model['matching']['officialMatches']
    assert len(model['matching']['officialCandidates'])==1 and model['matching']['officialCandidates'][0]['buildingCSUID']=='3390811442T20050430'
    archive=HERE/'local/government-xl-owned-57-sequence-20261006-12851-0/sheets/15-NW-3B/original/15-NW-3B.zip'
    assert archive.is_file(); archive_sha=digest(archive.read_bytes())
    converter=module('tung_cheong_original_converter',HERE/'xl-second-pass.py')
    folder=local/'recovered';(folder/'packed').mkdir(parents=True)
    with zipfile.ZipFile(archive)as z:
        info=z.getinfo(model['sourceEntry'])
        recovered=converter._convert_one(z,info,folder/'decoded',folder/'packed',{},dict(modelId=MID))
    generated=folder/'packed'/recovered['asset']['asset']
    raw=converter.recovery.canonical_bytes(generated.read_bytes(),SHA)
    assert digest(raw)==SHA and len(raw)==model['asset']['bytes']==1406
    target=local/(SHA+'.glb.gz');target.write_bytes(raw)
    tri=decode_original_world_triangles(raw);assert tri.shape==(44,3,3)
    tile=ROOT/'3d-viewer/city/data/tiles/-1_2.json';form=next(f for f in read(tile)['buildings']if f['uid']=='landsd/223636:0')
    assert form['buildingCSUID']=='3390811442T20050430' and form['buildingId']==1103139073
    projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));foot=shapely.Polygon(form['rings'][0],form['rings'][1:])
    result=dict(uids=['landsd/223636:0'],proposedViewerUid='landsd/223636:0',viewerIdentityAssigned=False,identityAccepted=False,nominationOnly=True,nativeCacheKey=KEY,nativeResultSHA256=RESULT,model=model,sourceSHA256=SHA,sourceAsset=dict(path=str(target.relative_to(ROOT)),sha256=SHA,bytes=len(raw)),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),completeOriginalFaces=len(tri),completeOriginalWorldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],sourceProjectionAreaM2=projection.area,currentFootprintAreaM2=foot.area,projectionIntersectionAreaM2=projection.intersection(foot).area,currentForm=form,archive=dict(path=str(archive.relative_to(ROOT)),sha256=archive_sha,member=model['sourceEntry']),sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,scriptExternalAICalls=0,qualification='Exact immutable native-stage original recovered locally. Matching remains rejected: GeoRefNo/name proximity does not override its raw footprint mismatch. Proposed low-component association, complete pair contacts, current terrain and identity/physical review remain separate.')
    assert digest(archive.read_bytes())==archive_sha and reservations.owns(lease)
    save(out/'summary.json',result)
    refs=[Path(__file__),target,tile,HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py']
    module('tung_cheong_low_recovery_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-unmatched-low-original-local-recovery-only',refs,result)
    print(dict(sourceSHA256=SHA,faces=len(tri),currentFootprintCovered=projection.intersection(foot).area/foot.area,identityAccepted=False),flush=True)
if __name__=='__main__':main()

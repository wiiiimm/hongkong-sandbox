"""Compare six elevated originals against each unchanged mall source separately."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-companion-support-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020'
def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
    receipt=read(SRC/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};refs=[Path(__file__),SRC/'result.json',HERE/'exact_packed_world_geometry_20261009.py']
    p=SRC/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
    rows=read(p)['rows'];world={}
    for row in rows:
        asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[row['assetPath']];refs.append(asset)
        world[row['modelId']]=decode_original_world_triangles(asset.read_bytes())
    elevated=[r for r in rows if world[r['modelId']][:,:,1].min()>15];assert len(elevated)==6
    summary=[]
    for podium in [r for r in rows if r['uid']=='landsd/289787:0']:
        assert reservations.owns(lease)
        folder=DOC/podium['modelId'];mesh=world[podium['modelId']]
        save(folder/'input.json.gz',dict(podium=mesh.tolist(),rows=[dict(uid=r['uid'],position=world[r['modelId']].reshape(-1).tolist(),index=list(range(len(world[r['modelId']])*3))) for r in elevated]))
        subprocess.run(['node',str(HERE/'wave_retained_basic_support_v1_20261017.mjs'),str(folder.relative_to(ROOT))],cwd=ROOT,check=True)
        result=read(folder/'support.json.gz')
        for p,h in result['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        for row in result['rows']:
            proof=row['proof'];summary.append(dict(uid=row['uid'],podiumModelId=podium['modelId'],samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved']),passed=proof['passed']))
    save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Original-coordinate support diagnostic only; no current render, identity or publication approval. Each mall source tested separately, never combined.'))
    module('mount_sterling_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'six-original-companions-two-separate-podiums',list(dict.fromkeys(refs)),dict(uids=sorted({r['uid'] for r in rows}),rows=summary,installationApproved=False))
def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists()
    claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

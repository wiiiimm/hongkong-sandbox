"""Test eight originals against a private exact-source terrain proposal."""
from pathlib import Path
import json,sys,uuid,subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-candidate-ground-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();receipt=read(CAP/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    proposal=BASE/'government-xl-mount-sterling-replacement-contract-v1-20261020';pr=read(proposal/'result.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(pr['jobId'],)).fetchone()==('complete',pr)
    for e in pr['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
    pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']};path=CAP/'input.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];source=read(path)
    assert digest((ROOT/source['currentManifest']['path']).read_bytes())==source['currentManifest']['sha256']
    rows=[dict(uid=r['uid'],sourceSHA256=r['entry']['sha256'],candidate=dict(entry=r['entry'],path=r['path']),source=dict(tile='city/data/tiles/-2_-3.json',building=r['building'])) for r in source['rows']]
    save(DOC/'selection.json.gz',dict(manifestSHA256=source['currentManifest']['sha256'],rows=rows))
    tool=HERE/'acceptance-metrics-multi-retained.mjs';subprocess.run(['node',str(tool),'--terrain-candidates',str((proposal/'terrain-candidates.json').relative_to(ROOT)),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates','source-scripts/city/government-import/local/government-xl-mount-sterling-nine-original-recovery-v1-20261020','--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
    report=read(DOC/'metrics.json');assert len(report['rows'])==8 and not any(r.get('error') for r in report['rows'])
    runtime=read(LOCAL/'runtime-geometry.json.gz');final=module('mount_sterling_current_foundations',HERE/'xl-final-script-pass.py');summaries=[]
    for r in runtime['rows']:
        assert reservations.owns(lease)
        triangles=np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];ground=np.asarray(r['drawnGroundGeometry']).reshape(-1,3,3);building=next(x['source']['building'] for x in rows if x['uid']==r['uid']);foundation=final.foundation_context(triangles,ground,Polygon(building['rings'][0],building['rings'][1:]));details=face_diagnostics(final,triangles,ground)
        save(DOC/(r['uid'].split('/')[1]+'.json.gz'),dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],foundation=foundation,**details,installationApproved=False))
        item=dict(uid=r['uid'],**{k:v for k,v in foundation.items() if k!='components'});summaries.append(item);print(item,flush=True)
    refs=[Path(__file__),proposal/'result.json',*[ROOT/e['path'] for e in pr['evidenceRefs']],CAP/'result.json',path,LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py',HERE/'china_ferry_current_foundations_v1_20261020.py']
    for r in rows:
        p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p)
    for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
    save(DOC/'summary.json',dict(uids=[r['uid'] for r in rows],rows=summaries,productionTerrainChanges=0,privateTerrainChanges=1,sourceGeometryChanges=0,installationApproved=False))
    module('mount_sterling_candidate_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-originals-private-source-terrain',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],rows=summaries,installationApproved=False,productionTerrainChanges=0,privateTerrainChanges=1))
def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

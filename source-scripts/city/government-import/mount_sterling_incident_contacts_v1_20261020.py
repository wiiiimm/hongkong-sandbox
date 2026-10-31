"""Exact finite contacts for unresolved original companion support samples."""
from pathlib import Path
import json,subprocess,sys,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-incident-contacts-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
REC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020';SUP=BASE/'government-xl-mount-sterling-companion-support-v1-20261020';POD='B323332207602063C0'
def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists();refs=[Path(__file__)];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (REC,SUP):
            receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    recovered=take(REC,REC/'recovery.json')['rows'];failures=take(SUP,SUP/POD/'support.json.gz')['rows'];world={}
    for row in recovered:
        asset=ROOT/row['assetPath'];assert digest(asset.read_bytes())==row['sourceSHA256']==pins[REC][row['assetPath']];refs.append(asset);world[row['modelId']]=decode_original_world_triangles(asset.read_bytes())
    support=world[POD];summary=[]
    for row in failures:
        assert reservations.owns(lease)
        source=next(r for r in recovered if r['uid']==row['uid']);t=world[source['modelId']];lo,hi=t.min(1),t.max(1);targets=[]
        for witness in row['proof']['unresolved']:
            point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
            ids=[int(i) for i in broad if np.linalg.norm(np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]))>0 and np.linalg.norm(closest(point,t[i])-point)<=.001]
            assert ids;targets.append(dict(rawWitness=witness,incidentFaces=ids))
        ids=sorted({f for target in targets for f in target['incidentFaces']});proof=exact_finite_contacts(t,ids,support,list(range(len(support))))
        for target in targets:
            contacts=[c for c in proof['contacts'] if c['sourceFaceA'] in target['incidentFaces'] and c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
            target.update(positiveDimensionalContact=bool(contacts),contactRows=contacts)
        save(DOC/(source['modelId']+'.json.gz'),dict(uid=row['uid'],sourceSHA256=source['sourceSHA256'],sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(support.tobytes()),targets=targets,proof=proof,installationApproved=False))
        item=dict(uid=row['uid'],targets=len(targets),withIncidentContact=sum(x['positiveDimensionalContact'] for x in targets));summary.append(item);print(item,flush=True)
    refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','pool_incident_wall_contacts_v1_20261017.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py'])
    save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0,qualification='Original source finite-contact diagnostic; does not alone prove bounded support paths or current renderer acceptance.'))
    module('mount_sterling_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-companion-incident-finite-contacts',list(dict.fromkeys(refs)),dict(uids=sorted({r['uid'] for r in recovered}),rows=summary,installationApproved=False))
def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];path=LOCAL/'reservation.json';save(path,json.loads(json.dumps(lease,default=str)))
    try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

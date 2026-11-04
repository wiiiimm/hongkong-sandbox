"""Verify finite support segments and locate the remaining noncontact sample."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-contact-segments-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-mount-sterling-incident-contacts-v1-20261020';REC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020';POD='B323332207602063C0'
def main():
    assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in (SRC,REC):
            receipt=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    sources=take(REC,REC/'recovery.json')['rows'];world={}
    for r in sources:
        p=ROOT/r['assetPath'];assert digest(p.read_bytes())==r['sourceSHA256']==pins[REC][r['assetPath']];refs.append(p);world[r['modelId']]=decode_original_world_triangles(p.read_bytes())
    results=[];remaining=[];support=world[POD]
    for r in sources:
        path=SRC/(r['modelId']+'.json.gz')
        if not path.exists():continue
        source=take(SRC,path);t=world[r['modelId']]
        for target in source['targets']:
            start=np.asarray(target['rawWitness']['position']);candidates=[]
            for contact in target['contactRows']:
                points=np.array([[float(Fraction(v)) for v in p] for p in contact['exactPoints']]);end=points.mean(0);face=t[contact['sourceFaceA']]
                residual=max(float(np.linalg.norm(closest(p,face)-p)) for p in (start,end));normal=np.cross(face[1]-face[0],face[2]-face[0]);normal/=np.linalg.norm(normal)
                candidates.append(dict(sourceFace=contact['sourceFaceA'],supportFace=contact['sourceFaceB'],end=end.tolist(),residualM=residual,lengthM=float(np.linalg.norm(end-start)),normalY=float(normal[1])))
            if candidates:
                best=min(candidates,key=lambda x:(x['residualM']>.001,x['lengthM']));results.append(dict(uid=r['uid'],start=start.tolist(),**best,finiteSameFaceSegment=best['residualM']<=.001))
            else:
                # Exact closest point on the finite triangles, no tolerance waiver.
                normal=np.cross(support[:,1]-support[:,0],support[:,2]-support[:,0]);valid=np.flatnonzero(np.linalg.norm(normal,axis=1)>0)
                nearest=sorted([(float(np.linalg.norm(closest(start,support[i])-start)),int(i)) for i in valid])[:5]
                remaining.append(dict(uid=r['uid'],rawWitness=target['rawWitness'],incidentSourceFaces=[dict(id=i,vertices=t[i].tolist()) for i in target['incidentFaces']],nearestPodiumFaces=[dict(distanceM=d,face=i,closestPoint=closest(start,support[i]).tolist(),vertices=support[i].tolist()) for d,i in nearest]))
    save(DOC/'segments.json.gz',dict(rows=results,remaining=remaining,installationApproved=False))
    summary=dict(uids=sorted({r['uid'] for r in sources}),targets=len(results)+len(remaining),finiteSameFaceSegments=sum(r['finiteSameFaceSegment'] for r in results),remaining=len(remaining),maximumResidualM=max(r['residualM'] for r in results),maximumLengthM=max(r['lengthM'] for r in results),remainingClosestDistancesM=[r['nearestPodiumFaces'][0]['distanceM'] for r in remaining],installationApproved=False,sourceGeometryChanges=0)
    save(DOC/'summary.json',summary);module('mount_sterling_segments_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'finite-original-contact-segments-and-residual',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()

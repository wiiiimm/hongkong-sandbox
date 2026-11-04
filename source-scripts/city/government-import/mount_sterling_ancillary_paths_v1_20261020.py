"""Finite paths across exact shared original edges to actual podium intersections."""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-ancillary-paths-v1-20261020'
DOC=BASE/BATCH
CAP=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
CONTACT=BASE/'government-xl-mount-sterling-ancillary-contacts-v1-20261020'
UID='landsd/163899:0';POD='landsd/289787:0'

def main():
    assert not DOC.exists()
    refs=[Path(__file__),HERE/'exact_original_finite_triangle_contacts_20261010.py',
          HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,CONTACT]:
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,p):
        assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    cap=take(CAP,CAP/'attributes.json.gz');summary=[];cached={}
    for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        world={r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in cap['rows']}
        t=world[UID];pod=world[POD];key=(digest(t.tobytes()),digest(pod.tobytes()))
        if key not in cached:cached[key]=exact_finite_contacts(t,list(range(len(t))),pod,list(range(len(pod))))
        proof=cached[key];anchors=defaultdict(list)
        for c in proof['contacts']:
            if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2:anchors[c['sourceFaceA']].append(c)
        edges=defaultdict(list)
        for i,face in enumerate(t):
            for a,b in zip(face,np.roll(face,-1,axis=0)):
                if np.array_equal(a,b):continue
                edges[tuple(sorted([tuple(a),tuple(b)]))].append(i)
        adjacent=defaultdict(list)
        for edge,ids in edges.items():
            for i in ids:
                for j in ids:
                    if i!=j:adjacent[i].append((j,edge))
        targets=take(CONTACT,CONTACT/(mode+'-targets.json.gz'))['rows'];records=[]
        for target in targets:
            if target['positiveDimensionalContact']:continue
            queue=deque((i,[],[]) for i in target['incidentFaces']);seen=set(target['incidentFaces']);found=None
            while queue:
                face,path,shared=queue.popleft()
                if face in anchors:found=(face,path+[face],shared);break
                for nextface,edge in adjacent[face]:
                    if nextface not in seen:
                        seen.add(nextface);queue.append((nextface,path+[face],shared+[edge]))
            record=dict(witness=target['rawWitness'],incidentFaces=target['incidentFaces'],connectedToPositivePodiumContact=found is not None)
            if found:
                last,path,shared=found
                start=np.asarray(target['rawWitness']['position'])
                points=[start]+[np.asarray(edge).mean(0) for edge in shared]
                options=[]
                for c in anchors[last]:
                    end=np.asarray([[float(Fraction(v)) for v in p] for p in c['exactPoints']]).mean(0)
                    options.append((float(np.linalg.norm(end-points[-1])),end,c))
                _,end,contact=min(options,key=lambda a:a[0]);points.append(end)
                residuals=[max(float(np.linalg.norm(closest(p,t[i])-p)) for p in points[k:k+2]) for k,i in enumerate(path)]
                record.update(facePath=path,sharedEdges=[[list(a),list(b)] for a,b in shared],
                              pathPoints=[p.tolist() for p in points],contact=contact,
                              maximumFiniteFaceResidualM=max(residuals),
                              finiteSurfacePath=max(residuals)<=.001,
                              pathLengthM=sum(float(np.linalg.norm(b-a)) for a,b in zip(points,points[1:])))
            records.append(record)
        save(DOC/(mode+'.json.gz'),dict(sourceWorldSHA256=key[0],supportWorldSHA256=key[1],
                                       exactContacts=proof,rows=records,installationApproved=False))
        result=dict(mode=mode,remainingWitnesses=len(records),
                    connected=sum(r['connectedToPositivePodiumContact'] for r in records),
                    finitePaths=sum(r.get('finiteSurfacePath',False) for r in records),
                    maximumPathLengthM=max((r.get('pathLengthM',0) for r in records),default=0),
                    maximumResidualM=max((r.get('maximumFiniteFaceResidualM',0) for r in records),default=0))
        summary.append(result);print(result,flush=True)
    save(DOC/'summary.json',dict(rows=summary,installationApproved=False,
                                qualification='Exact finite original surface paths only; no strict-interface waiver, structural engineering claim or physical approval.'))
    module('mount_sterling_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'ancillary-exact-shared-edge-surface-paths',refs,dict(uids=[UID],rows=summary,installationApproved=False))

if __name__=='__main__':main()

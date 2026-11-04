"""Locate unresolved ancillary contacts on unchanged finite source surfaces."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-mount-sterling-ancillary-context-v1-20261020'
DOC=BASE/BATCH
CAP=BASE/'government-xl-mount-sterling-actual-render-attributes-v1-20261020'
CONTACT=BASE/'government-xl-mount-sterling-ancillary-contacts-v1-20261020'
UID='landsd/163899:0';POD='landsd/289787:0'

def main():
    assert not DOC.exists()
    refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for folder in [CAP,CONTACT]:
            receipt=read(folder/'result.json')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
    def take(folder,path):
        assert digest(path.read_bytes())==pins[folder][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    cap=take(CAP,CAP/'attributes.json.gz')
    summary=[]
    for mode,field in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
        world={r['uid']:np.asarray(r[field]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in cap['rows']}
        t=world[UID];support=world[POD]
        targets=take(CONTACT,CONTACT/(mode+'-targets.json.gz'))['rows']
        records=[];remaining=[]
        for target in targets:
            start=np.asarray(target['rawWitness']['position']);candidates=[]
            for c in target['contactRows']:
                end=np.asarray([[float(Fraction(v)) for v in p] for p in c['exactPoints']]).mean(0)
                f=t[c['sourceFaceA']]
                residual=max(float(np.linalg.norm(closest(p,f)-p)) for p in [start,end])
                candidates.append(dict(sourceFace=c['sourceFaceA'],supportFace=c['sourceFaceB'],
                                       end=end.tolist(),residualM=residual,lengthM=float(np.linalg.norm(end-start))))
            if candidates:
                best=min(candidates,key=lambda x:(x['residualM']>.001,x['lengthM']))
                records.append(dict(start=start.tolist(),**best,finiteSameFaceSegment=best['residualM']<=.001))
            else:
                # Box lower bounds select a finite nearest-face search without
                # substituting an infinite supporting plane for actual geometry.
                lo=support.min(1);hi=support.max(1)
                lower=np.linalg.norm(np.maximum(np.maximum(lo-start,start-hi),0),axis=1)
                nearest=None
                for i in np.argsort(lower):
                    if nearest and lower[i]>nearest['distanceM']:break
                    f=support[i]
                    if np.linalg.norm(np.cross(f[1]-f[0],f[2]-f[0]))==0:continue
                    q=closest(start,f);distance=float(np.linalg.norm(q-start))
                    if nearest is None or distance<nearest['distanceM']:nearest=dict(face=int(i),distanceM=distance,point=q.tolist(),vertices=f.tolist())
                remaining.append(dict(witness=target['rawWitness'],incidentFaces=target['incidentFaces'],nearestPodiumFace=nearest))
        save(DOC/(mode+'-context.json.gz'),dict(segments=records,remaining=remaining,sourceBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],installationApproved=False))
        summary.append(dict(mode=mode,finiteSegments=sum(r['finiteSameFaceSegment'] for r in records),remaining=len(remaining),
                            remainingNearestDistancesM=[r['nearestPodiumFace']['distanceM'] for r in remaining],
                            maximumSegmentResidualM=max(r['residualM'] for r in records)))
        if mode!='literal':continue
        ids=sorted({i for r in remaining for i in r['incidentFaces']})
        lo=t.min((0,1));hi=t.max((0,1));origin=np.array([lo[0]-3,lo[2]-3,0])
        fig=plt.figure(figsize=(16,8))
        for number,az in enumerate([30,210]):
            ax=fig.add_subplot(1,2,number+1,projection='3d')
            for mesh,color,alpha in [(support,'#617d9c',.18),(t,'#35a371',.65),(t[ids],'#d63f30',.95)]:
                selected=mesh[(mesh[:,:,0].max(1)>=lo[0]-3)&(mesh[:,:,0].min(1)<=hi[0]+3)&(mesh[:,:,2].max(1)>=lo[2]-3)&(mesh[:,:,2].min(1)<=hi[2]+3)]
                ax.add_collection3d(Poly3DCollection(selected[:,:,[0,2,1]]-origin,facecolor=color,edgecolor=color,linewidth=.25,alpha=alpha))
            ax.set_xlim(0,hi[0]-lo[0]+6);ax.set_ylim(0,hi[2]-lo[2]+6);ax.set_zlim(10,24)
            ax.set_box_aspect([hi[0]-lo[0]+6,hi[2]-lo[2]+6,14]);ax.view_init(25,az)
            ax.set_xlabel('X offset m');ax.set_ylabel('Z offset m');ax.set_zlabel('HKPD m')
        fig.suptitle('Ancillary original 163899: green; unresolved incident faces red; original podium blue\nSource-only diagnostic, no placement approval or geometry edits.')
        fig.tight_layout();fig.savefig(DOC/'ancillary-context.png',dpi=140);plt.close(fig)
    save(DOC/'summary.json',dict(uids=[UID],rows=summary,installationApproved=False,sourceGeometryChanges=0))
    module('mount_sterling_ancillary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH,'ancillary-finite-contact-paths-and-unresolved-source-context',refs,
        dict(uids=[UID],rows=summary,installationApproved=False))
    print(summary,flush=True)

if __name__=='__main__':main()

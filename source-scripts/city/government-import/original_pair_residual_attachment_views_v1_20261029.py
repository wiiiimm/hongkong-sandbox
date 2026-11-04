"""Show every unresolved exact original pair attachment witness; no acceptance."""
import argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_assembly_context_plot_v3_20261023 import clipped_faces

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attachment','uid','peer']:p.add_argument('--'+key,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/'not in a.batch and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(n,path):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,base/a.runtime/'selection.json.gz');proof=take(a.attachment,base/a.attachment/'summary.json')
    assert proof['targetUid']==a.uid and set(proof['uids'])=={a.uid,a.peer}
    models={}
    for uid in [a.uid,a.peer]:
        row=next(r for r in selection['rows']if r['uid']==uid);path=ROOT/row['candidate']['path'];raw=path.read_bytes()
        assert digest(raw)==row['sourceSHA256']==proof['sourceSHA256ByUid'][uid];refs.append(path)
        models[uid]=decode_original_world_triangles(raw);assert len(models[uid])==row['triangles']
    report=take(a.attachment,base/a.attachment/'original.json.gz')
    residual=[dict(r,witnessIndex=i)for i,r in enumerate(report['rows'])if not r.get('passesExistingEndpointHeight',False)]
    assert residual and all(r['hasUnrestrictedFiniteAttachment']for r in residual)
    residual.sort(key=lambda r:tuple(r['witness']['position']))
    target=models[a.uid];peer=models[a.peer];out.mkdir();exports=[];records=[]
    for offset in range(0,len(residual),7):
        group=residual[offset:offset+7];points=np.asarray([r['witness']['position']for r in group]);lo=points.min(0)-[2,1,2];hi=points.max(0)+[2,2,2]
        ids=sorted({i for r in group for i in r['incidentFaces']});planes=[(i,float(lo[i]),True)for i in range(3)]+[(i,float(hi[i]),False)for i in range(3)]
        fig=plt.figure(figsize=(16,7),layout='constrained')
        for k,angle in enumerate([35,215],1):
            ax=fig.add_subplot(1,2,k,projection='3d')
            for tri,color,alpha in [(target,'#94a3b8',.25),(peer,'#3b82f6',.5),(target[ids],'#dc2626',.9)]:
                mask=np.all(tri.max(1)>=lo,axis=1)&np.all(tri.min(1)<=hi,axis=1);faces=clipped_faces(tri[mask],planes)
                if len(faces):ax.add_collection3d(Poly3DCollection((faces-lo)[:,:,[0,2,1]],facecolor=color,edgecolor=color,alpha=alpha,linewidth=.25))
            for r in group:
                q=np.asarray(r['witness']['position'])-lo;ax.scatter(q[0],q[2],q[1],color='black',s=14);ax.text(q[0],q[2],q[1],str(r['witnessIndex']),fontsize=7)
            size=(hi-lo)[[0,2,1]];ax.set(xlim=(0,size[0]),ylim=(0,size[1]),zlim=(0,size[2]),xlabel='east offset m',ylabel='Z offset m',zlabel='height offset m');ax.set_box_aspect(size.copy());ax.view_init(25,angle)
        fig.suptitle(f'{a.uid} original junction warnings {offset+1}–{offset+len(group)} / {len(residual)}\nRed: exact incident source facets; blue: unchanged original peer. Display crops only; no support approval.')
        path=out/f'residual-witnesses-{offset//7+1}.png';fig.savefig(path,dpi=140);plt.close(fig);refs.append(path)
        exports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),witnessIndices=[r['witnessIndex']for r in group]))
        for r in group:
            normals=np.cross(target[r['incidentFaces'],1]-target[r['incidentFaces'],0],target[r['incidentFaces'],2]-target[r['incidentFaces'],0]);length=np.linalg.norm(normals,axis=1)
            records.append(dict(r,incidentFaceContext=[dict(sourceFace=i,vertices=target[i].tolist(),signedNormalYRatio=float(normals[k,1]/length[k]))for k,i in enumerate(r['incidentFaces'])]))
    assert sorted(i for e in exports for i in e['witnessIndices'])==sorted(r['witnessIndex']for r in residual)
    result=dict(uids=[a.uid,a.peer],sourceSHA256ByUid=proof['sourceSHA256ByUid'],completeResidualWitnesses=len(residual),witnesses=records,exports=exports,allResidualsShownExactlyOnce=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='All residual original-mode witnesses shown and labelled. Exact source incident facets and full local peer surface retained in display-only crops. Other coordinate modes remain independently obligated. No architectural role, root credit, tolerance change, source modelling or placement approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_assembly_context_plot_v3_20261023.py'])
    module('original_residual_views',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-residual-original-pair-attachment-witness-views',refs,result)
    print(dict(witnesses=len(residual),exports=len(exports)))

if __name__=='__main__':main()

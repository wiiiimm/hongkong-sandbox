"""Render every detached original facade detail and representative close-ups; no role approval."""
from pathlib import Path
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-sung-fung-55-facade-source-views-v1-20261024';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    context='government-xl-next-repairs-sung-fung-55-separate-facade-groups-v1-20261024';attrs='government-xl-next-repairs-sung-fung-original-podium-current-prephysical-v1-20261024-attributes';uid='landsd/79098:0';summary=take(context,base/context/'summary.json');attr=next(r for r in take(attrs,base/attrs/'attributes.json.gz')['rows']if r['uid']==uid);tri=np.asarray(attr['completeLiteralWorldPosition']).reshape(-1,3)[np.asarray(attr['completeOriginalIndex']).reshape(-1,3)];sha=digest(tri.astype('<f8').tobytes());assert sha==next(r['completeSourceWorldSHA256']for r in summary['coordinateBindings']if r['mode']=='literal');assert summary['sourceSHA256']==attr['sourceSHA256'];prior=summary['distinctWorlds'][sha];rows=[take(context,base/context/(prior['proofMode']+'-group-'+str(r['group'])+'.json.gz'))for r in prior['groups']];assert len(rows)==55
    helper=module('source_view_crop_only',HERE/'next_two_local_surface_views_v2_20261020.py');refs.append(HERE/'next_two_local_surface_views_v2_20261020.py');out.mkdir();images=[]
    def draw(ax,row,angle):
        part=tri[row['completeOriginalFaceIds']];host=tri[row['sameSourceMainGroupHostFaceIds']];low=part.min((0,1))-np.array([.3,.2,.3]);high=part.max((0,1))+np.array([.3,.2,.3]);size=(high-low)[[0,2,1]]
        for mesh,color,alpha in [(host,'#64748b',.3),(part,'#d77b31',1.)]:
            polys=helper.clipped(mesh,low,high)
            if polys:ax.add_collection3d(Poly3DCollection(polys,facecolors=color,edgecolors=color,alpha=alpha,linewidth=.35))
        ax.set_xlim(0,size[0]);ax.set_ylim(0,size[1]);ax.set_zlim(0,size[2]);ax.set_box_aspect(size);ax.view_init(22,angle);ax.set_title('Group '+str(row['group'])+' | '+str(len(row['completeOriginalFaceIds']))+' source faces');ax.set_xlabel('X m');ax.set_ylabel('Z m');ax.set_zlabel('Y m')
    def finish(fig,path,size,groups):
        fig.tight_layout();fig.savefig(path,dpi=130);plt.close(fig)
        with Image.open(path)as im:assert im.size==size
        images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),dimensions=list(size),groups=groups));refs.append(path)
    for page in range(math.ceil(len(rows)/9)):
        subset=rows[page*9:(page+1)*9];fig=plt.figure(figsize=(14,14))
        for n,row in enumerate(subset,1):draw(fig.add_subplot(3,3,n,projection='3d'),row,35)
        fig.suptitle('All original Sung Fung exterior detail groups — orange source, grey finite same-source body\nLiteral renderer coordinates; display crops only; no source geometry edits or role approval.');finish(fig,out/('atlas-'+str(page+1)+'.png'),(1820,1820),[r['group']for r in subset])
    for gid in [1,15,16,54,55]:
        row=next(r for r in rows if r['group']==gid);fig=plt.figure(figsize=(14,6))
        for n,angle in enumerate([35,215],1):draw(fig.add_subplot(1,2,n,projection='3d'),row,angle)
        fig.suptitle('Original detail group '+str(gid)+' — orange source, grey existing finite body\nDisplay-only clipping/colouring. All actual source vertices/pose retained.');finish(fig,out/('group-'+str(gid)+'-two-angles.png'),(1820,780),[gid])
    result=dict(uids=[uid],sourceSHA256=attr['sourceSHA256'],completeLiteralWorldSHA256=sha,groupsCovered=sorted(r['group']for r in rows),images=images,sourceGeometryChanges=0,sourcePoseChanges=0,displayClippingOnly=True,imagesActuallyViewed=False,architectureReview=False,visualRoleAccepted=False,structuralRootCredit=False,physicalAcceptance=False,installationApproved=False,publication=False,rendererVersions=dict(numpy=np.__version__,matplotlib=matplotlib.__version__),qualification='Actual exported source-coordinate inspection charts covering all55separate groups plus both angles for all observed face-count/association cases. These are source-only diagnostic figures, not staged/live city browser acceptance or a model edit. ROOT still must inspect them before any source-role interpretation.')
    save(out/'summary.json',result);module('source_facade_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'all-original-separate-facade-group-source-coordinate-exports',refs,result)


if __name__=='__main__':main()

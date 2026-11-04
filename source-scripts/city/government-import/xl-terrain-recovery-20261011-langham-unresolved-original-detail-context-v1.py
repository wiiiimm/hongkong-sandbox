"""Complete unchanged source context for four unmatched facets and other details.

Neighbour surfaces are explicitly cropped visual context, not support/mount proof.
The complete selected components, all faces, windings and original bounds remain
bound. No function or semantic acceptance is inferred from a plausible picture.
"""
from pathlib import Path
import importlib.util, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-unresolved-original-detail-context-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011'
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
LOOPS=BASE/'xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1'
UID='landsd/79318:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists(); refs=[ref(Path(__file__))]
    for folder in (PROBE,GRAPH,LOOPS):
        receipt=read(folder/'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
        refs.extend(ref(folder/name)for name in ('result.json','diagnostic.json.gz')if(folder/name).is_file())
    row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(18086,3,3)
    g=read(GRAPH/'diagnostic.json.gz');loops=read(LOOPS/'diagnostic.json.gz');assert loops['completeOriginalWorldSHA256']==digest(world.tobytes())
    views=[([683],.4,'Original unmatched facet 8123'),([711],.5,'Original unmatched facet 8528; complete nearby host boundary'),([761],.4,'Original unmatched facet 9395'),([902],.4,'Original unmatched facet 11745'),([91],2.5,'Entire original 12-face box 91; roof context'),([10,20,21,29],.7,'Four original 139-face strips; complete authored parts'),([213,214,355,476,477,618,630,830],.6,'Complete nearby unresolved original cluster'),([95],.4,'Complete original 10-face thin part 95')]
    lo=world.min(1);hi=world.max(1);records=[];fig=plt.figure(figsize=(18,16),dpi=100)
    for k,(bodies,pad,title)in enumerate(views):
        ids=sorted(set(i for b in bodies for i in g['components'][b]['globalOriginalFaces']));assert all(g['components'][b]['actorUID']==UID for b in bodies);shown=world[ids];low=shown.min((0,1));high=shown.max((0,1));bounds=np.array([low-pad,high+pad]);near=[int(i)for i in np.where(np.all(hi>=bounds[0],axis=1)&np.all(lo<=bounds[1],axis=1))[0]if int(i)not in ids];center=(low+high)/2
        ax=fig.add_subplot(4,2,k+1,projection='3d');ax.add_collection3d(Poly3DCollection((world[near]-center)[:,:,[0,2,1]],facecolors='#839caa',edgecolors='#455b67',alpha=.38,linewidths=.3));ax.add_collection3d(Poly3DCollection((shown-center)[:,:,[0,2,1]],facecolors='#dd893b',edgecolors='#693813',alpha=.97,linewidths=.7));s=(bounds-center)[:,[0,2,1]];ax.set_xlim(s[0,0],s[1,0]);ax.set_ylim(s[0,1],s[1,1]);ax.set_zlim(s[0,2],s[1,2]);ax.set_box_aspect(s[1]-s[0]);ax.view_init(23,-65);ax.set_title(title,fontsize=9);ax.set_xlabel('Original X (m)');ax.set_ylabel('Original Z (m)');ax.set_zlabel('Original Y (m)')
        normals=np.cross(shown[:,1]-shown[:,0],shown[:,2]-shown[:,0]);records.append(dict(originalBodies=bodies,completeOriginalFaces=ids,completeUnchangedOriginalTriangles=shown.tolist(),completeOriginalNormals=normals.tolist(),completeOriginalAreasM2=(np.linalg.norm(normals,axis=1)/2).tolist(),completeOriginalBounds=[low.tolist(),high.tolist()],croppedOriginalNeighbourFaces=near,visualCropBounds=bounds.tolist(),cropDoesNotClaimCompleteHostOrPhysicalScope=True))
    fig.tight_layout();DOC.mkdir(parents=True);png=DOC/'original-unresolved-details-1800x1600.png';fig.savefig(png);plt.close(fig);refs.extend(ref(p)for p in(asset,png,PROBE/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py'))
    out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(world.tobytes()),completeOwnedOriginalFaces=18086,exactCompleteSelectedSourceComponents=records,completeFourUnmatchedFacetFailuresPreserved=True,box91NoMountOrSupportProved=True,equalMetricAxes=True,sourceOnly=True,noFreshCurrentCapture=True,authoredRoleAccepted=False,structuralRootCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
    s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-langham-four-unmatched-facets-box-strips-unresolved-source-context-v1',[ROOT[r['path']]for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnly=True,authoredRoleAccepted=False,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()

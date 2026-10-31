"""Exact basal-closure/recorded-base context; diagnostic, never acceptance."""
import argparse
from fractions import Fraction
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
from exact_original_triangle_pair_column_gap_20261010 import verify
from original_assembly_context_plot_v3_20261023 import clipped_faces

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','low-faces','uid']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    low=take(a.low_faces,base/a.low_faces/'summary.json');assert low['sourceSHA256']==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256']and low['uids']==[a.uid]
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k]).reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(ground)>0;recorded=Fraction(float(row['source']['building']['baseHeightHKPD']));results=[];ids=None
    for mode,tri in worlds.items():
        raw=take(a.low_faces,base/a.low_faces/(mode+'.json.gz'));assert raw['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())and raw['groundSHA256']==digest(ground.astype('<f8').tobytes())
        faces=[r['sourceFace']for r in raw['rows']if r['absoluteNormalYRatio']is not None and r['absoluteNormalYRatio']>=.25];assert faces and(ids is None or ids==faces);ids=faces;floor=[]
        for i in faces:
            f=tri[i];n=np.cross(f[1]-f[0],f[2]-f[0]);assert n[0]==n[2]==0 and n[1]<0 and np.all(f[:,1]==tri[:,:,1].min())
            assert Fraction(float(f[0,1]))<recorded;proofs=[]
            for j,t in enumerate(ground):
                proof=verify(f,t)
                if proof['exactClosedHorizontalProjectionsMeet']:
                    assert proof['allExactBasicFeasibleColumnVertices'];proofs.append(dict(groundFace=j,proof=proof))
            assert proofs;maxgrade=max(Fraction(v['exactGroundPoint'][1])for p in proofs for v in p['proof']['allExactBasicFeasibleColumnVertices']);assert maxgrade<recorded
            floor.append(dict(sourceFace=i,sourceVertices=f.tolist(),sourceGlobalMinimumY=float(f[0,1]),recordedBaseHKPD=str(recorded),maximumExactGroundUnderThisFaceHKPD=str(maxgrade),exactGradeBelowRecordedBaseM=str(recorded-maxgrade),everyActualGroundFaceTested=len(ground),allFiniteColumnProofs=proofs))
        save(out/(mode+'.json.gz'),dict(uid=a.uid,sourceSHA256=row['sourceSHA256'],sourceWorldSHA256=raw['sourceWorldSHA256'],groundSHA256=raw['groundSHA256'],rows=floor,physicalAcceptance=False,installationApproved=False));results.append(dict(mode=mode,faces=faces,allDownwardAtGlobalSourceMinimum=True,everyGroundFaceTested=len(ground),maximumGroundUnderBottomHKPD=str(max(Fraction(r['maximumExactGroundUnderThisFaceHKPD'])for r in floor)),recordedBaseHKPD=str(recorded),groundBelowRecordedBase=True))
    tri=worlds['original'];selected=tri[ids];lowbox=selected.min((0,1))-np.array([1.5,1,1.5]);highbox=selected.max((0,1))+np.array([1.5,4,1.5]);origin=(lowbox+highbox)/2;planes=[(axis,value,lower)for axis in range(3)for value,lower in [(lowbox[axis],True),(highbox[axis],False)]]
    fig=plt.figure(figsize=(16,7))
    for k,(azim,elev)in enumerate([(35,20),(-130,15)]):
        ax=fig.add_subplot(1,2,k+1,projection='3d')
        for t,color,alpha in [(tri,'grey',.25),(ground,'teal',.35),(selected,'red',.85)]:
            lo,hi=t.min(1),t.max(1);local=t[np.all(hi>=lowbox,axis=1)&np.all(lo<=highbox,axis=1)];clipped=clipped_faces(local,planes)
            if len(clipped):ax.add_collection3d(Poly3DCollection((clipped-origin)[:,:,[0,2,1]],facecolors=color,edgecolors=color,linewidths=.3,alpha=alpha))
        aa,bb=lowbox-origin,highbox-origin;ax.set_xlim(aa[0],bb[0]);ax.set_ylim(aa[2],bb[2]);ax.set_zlim(aa[1],bb[1]);ax.set_box_aspect((highbox-lowbox)[[0,2,1]].copy());ax.view_init(elev=elev,azim=azim);ax.set_xlabel('X relative (m)');ax.set_ylabel('Z relative (m)');ax.set_zlabel('Y relative (m)');ax.set_title('Original lower facade grey / actual ground teal / basal closure red')
    fig.tight_layout();fig.savefig(out/'basal-ground-context.png',dpi=150);plt.close(fig)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],rows=results,allFourWorldBottomFacesBelowRecordedBaseWithGradeBelowBase=True,rawClearanceNegativesPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,architectureReview=False,physicalAcceptance=False,installationApproved=False,qualification='Exact lower-closure context only. Each named nonwall-negative face is downward horizontal at the whole original source global minimum; every finite column against every actual ground facet stays below the government recorded base. No public walking surface, basement purpose, structural support or import acceptance is inferred automatically. Display-only clipping does not alter source/terrain assets.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_triangle_pair_column_gap_20261010.py','original_assembly_context_plot_v3_20261023.py']);module('basal_closure_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-four-world-original-basal-closure-recorded-base-context',refs,result)

if __name__=='__main__':main()

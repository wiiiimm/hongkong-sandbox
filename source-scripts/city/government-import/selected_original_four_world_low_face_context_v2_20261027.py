"""Exact finite current-ground diagnostics for every potentially low original face."""
import argparse
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_triangle_pair_column_gap_20261010 import verify


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();pins={};refs=[Path(__file__)]
    for name in [a.runtime,a.attributes]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    row=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
    ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    modes=dict(original=decode_original_world_triangles(raw),**{name:np.asarray(attr[key]).reshape(-1,3)[ix]for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(ground)>0
    gxz=ground[:,:,[0,2]];glo=gxz.min(1);ghi=gxz.max(1);maxy=Fraction(float(ground[:,:,1].max()));threshold=Fraction(-1,2);summaries=[]
    cache={}
    for name,tri in modes.items():
        assert len(tri)==row['triangles']
        key=digest(tri.tobytes())
        if key in cache:
            prior,document,summary=cache[key]
            assert tri.dtype==prior.dtype and np.array_equal(tri,prior)
            save(out/(name+'.json.gz'),deepcopy(document))
            summaries.append(dict(summary,mode=name))
            print(summaries[-1],flush=True)
            continue
        rows=[];pruned=0;checked=0
        for i,t in enumerate(tri):
            if Fraction(float(t[:,1].min()))-maxy>=threshold:pruned+=1;continue
            txz=t[:,[0,2]];ids=np.flatnonzero(np.all(ghi>=txz.min(0),axis=1)&np.all(glo<=txz.max(0),axis=1));proofs=[]
            for j in ids:
                proof=verify(t,ground[j]);checked+=1
                if proof['exactClosedHorizontalProjectionsMeet']and Fraction(proof['exactMinimumFiniteColumnGapM'])<threshold:proofs.append(dict(groundFace=int(j),proof=proof))
            if not proofs:continue
            cross=np.cross(t[1]-t[0],t[2]-t[0]);norm=float(np.linalg.norm(cross));ratio=abs(float(cross[1]))/norm if norm else None
            v=int(np.argmax(t[:,1]));point=t[v];pis=np.flatnonzero(np.all(glo<=point[[0,2]],axis=1)&np.all(ghi>=point[[0,2]],axis=1));exposed=[]
            for j in pis:
                proof=verify(np.repeat(point[None,:],3,axis=0),ground[j])
                if proof['exactClosedHorizontalProjectionsMeet']:exposed.append(dict(groundFace=int(j),proof=proof))
            rows.append(dict(sourceFace=i,vertices=t.tolist(),absoluteNormalYRatio=ratio,minimumFiniteGapM=str(min(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])for q in proofs)),negativeGroundPairProofs=proofs,highestOriginalVertex=v,highestVertexProofs=exposed,highestVertexAboveEveryOverlappingGroundFace=bool(exposed)and all(Fraction(q['proof']['exactMinimumFiniteColumnGapM'])>0 for q in exposed)))
        document=dict(sourceWorldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),rows=rows,completeSourceFaces=len(tri),globalHeightBoundPrunedFaces=pruned,finitePairsTested=checked)
        save(out/(name+'.json.gz'),document)
        summaries.append(dict(mode=name,completeSourceFaces=len(tri),globalHeightBoundPrunedFaces=pruned,finitePairsTested=checked,exactAffectedFaces=[r['sourceFace']for r in rows],allAffectedWallLike=all(r['absoluteNormalYRatio']is not None and r['absoluteNormalYRatio']<.25 for r in rows),allAffectedHaveExposedHighestVertex=all(r['highestVertexAboveEveryOverlappingGroundFace']for r in rows)))
        cache[key]=(tri.copy(),deepcopy(document),deepcopy(summaries[-1]))
        print(summaries[-1],flush=True)
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],rows=summaries,installationApproved=False,physicalAcceptance=False,architectureReview=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Every source face considered: exact global height bound prunes only definitely clear faces; remaining inclusive finite ground pairs checked exactly. Wall-like normals and exposed vertices are diagnostics, not architectural-role, coverage, support or publication approval.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_triangle_pair_column_gap_20261010.py'])
    module('exact_low_face_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-complete-source-low-face-exact-current-ground-context',refs,result)


if __name__=='__main__':main()

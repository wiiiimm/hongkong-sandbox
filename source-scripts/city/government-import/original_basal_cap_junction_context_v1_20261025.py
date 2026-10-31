"""Classify exact downward basal closures in an original support junction.

Evidence only. Keeps canonical failures and never grants a burial exemption,
identity, physical or publication approval.
"""
import argparse
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def classify(face, base):
    p,q,r=[[F.from_float(float(v))for v in point]for point in face]
    a,b=[[v[i]-p[i]for i in range(3)]for v in [q,r]]
    normal=(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    return dict(exactlyHorizontal=normal[0]==normal[2]==0,exactlyDownward=normal[1]<0,
                allVerticesAtCompleteSourceMinimum=all(point[1]==base for point in face))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','clearance','uid','support']:p.add_argument('--'+key,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs=[__file__];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected={r['uid']:r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']}
    attrs={r['uid']:r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']}
    geometry=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    worlds={};sources={}
    for uid in [a.uid,a.support]:
        r=selected[uid];g=attrs[uid];path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256']==g['sourceSHA256'];refs.append(path);sources[uid]=r['sourceSHA256'];index=np.asarray(g['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]={'original':decode_original_world_triangles(path.read_bytes()),**{mode:np.asarray(g[field]).reshape(-1,3)[index]for mode,field in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
    summary=take(a.clearance,base/a.clearance/'summary.json');assert summary['supportedUid']==a.uid and summary['supportUid']==a.support and summary['sourceSHA256']==sources[a.uid]and summary['supportSHA256']==sources[a.support]
    actual=np.asarray(geometry['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);rows=[]
    for mode,tri in worlds[a.uid].items():
        low=take(a.clearance,base/a.clearance/(mode+'.json.gz'));caps=take(a.clearance,base/a.clearance/(mode+'-cap-paths.json.gz'));ground=np.concatenate([actual,worlds[a.support][mode]])
        assert low['sourceWorldSHA256']==caps['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes())
        assert low['groundSHA256']==caps['compoundGroundSHA256']==digest(ground.astype('<f8').tobytes())
        assert caps['actualGroundSHA256']==digest(actual.tobytes())and caps['supportWorldSHA256']==digest(worlds[a.support][mode].astype('<f8').tobytes())
        proof=caps['proof'];walls={r['sourceFace']for r in low['rows']if r['absoluteNormalYRatio']is not None and r['absoluteNormalYRatio']<.25};nonwalls={r['sourceFace']for r in low['rows']} - walls
        assert set(proof['negativeNonWallFaces'])==nonwalls
        assert set(proof['negativeSourceFaces'])==walls|nonwalls
        minimum=float(tri[:,:,1].min());classified=[]
        for i in sorted(nonwalls):
            row=next(r for r in low['rows']if r['sourceFace']==i);assert np.array_equal(tri[i],np.asarray(row['vertices']))
            classified.append(dict(sourceFace=i,**classify(tri[i],minimum)))
        wallpaths=[r for r in proof['paths']if r['sourceFace']in walls];assert len(wallpaths)==len(walls)
        result=dict(mode=mode,sourceWorldSHA256=low['sourceWorldSHA256'],compoundGroundSHA256=low['groundSHA256'],completeSourceMinimumY=minimum,minimumSourceMinusAllActualGroundMaximumM=minimum-float(actual[:,:,1].max()),negativeWallFaces=len(walls),allNegativeWallsHaveClearCapPaths=all(r['hasExactSharedEdgeClearCapPath']for r in wallpaths),negativeNonWalls=classified,allNegativeNonWallsAreExactDownwardBasalClosures=bool(classified)and all(all(r[k]for k in ['exactlyHorizontal','exactlyDownward','allVerticesAtCompleteSourceMinimum'])for r in classified),rawCanonicalCapPathsPassed=proof['allAffectedHavePaths'])
        rows.append(result)
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,rows=rows,allFourContextsClassified=all(r['allNegativeNonWallsAreExactDownwardBasalClosures']and r['allNegativeWallsHaveClearCapPaths']and r['minimumSourceMinusAllActualGroundMaximumM']>=-.5 for r in rows),identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Exact classification of the complete recorded negatives. Downward closures remain original base facets; their size is not waived and canonical failures remain false. Any later bounded interpretation must independently bind exact source identity/assembly, whole-source foundations, original support paths, current neighbours and actual browser exports. This producer approves none of those.')
    save(out/'summary.json',result)
    from pathlib import Path
    refs += [HERE/'exact_packed_world_geometry_20261009.py']
    module('basal_junction_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-four-world-original-basal-closure-junction-context',[Path(r)for r in refs],result)
    print(dict(allFourContextsClassified=result['allFourContextsClassified'],rows=[dict(mode=r['mode'],wallFaces=r['negativeWallFaces'],basalFaces=len(r['negativeNonWalls']))for r in rows]),flush=True)


if __name__=='__main__':main()

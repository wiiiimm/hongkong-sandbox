"""Qualify literal clear-cap evidence only for exactly identical source/ground arrays."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','literal-paths','uid']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    source=next(r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid)
    g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']if r['uid']==a.uid)
    old=take(a.literal_paths,base/a.literal_paths/'summary.json')
    assert old['uids']==[a.uid] and old['coordinateRepresentation']=='actual-literal-only' and old['proof']['allAffectedHavePaths']
    asset=ROOT/source['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==source['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256']==old['sourceSHA256'];refs.append(asset)
    index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
    literal=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    worlds={'original':decode_original_world_triangles(raw),**{name:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]for name,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
    ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
    assert digest(literal.tobytes())==old['binding']['completeOriginalWorldTrianglesSHA256']
    assert digest(ground.tobytes())==old['binding']['currentDrawnGroundSHA256']
    rows=[]
    for mode,tri in worlds.items():
        assert tri.shape==literal.shape and np.array_equal(tri,literal),'Different coordinates require their own complete path evidence'
        assert tri.astype('<f8').tobytes()==literal.tobytes(),'Represented arrays must be byte-identical, including signed zero'
        rows.append(dict(mode=mode,completeSourceFaces=len(tri),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),groundSHA256=digest(ground.tobytes()),exactSameSourceAndGroundArrays=True))
    result=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],rows=rows,allFourExactArrayEquivalent=True,literalClearCapProof=old['proof'],allFourAffectedHaveClearCapPaths=True,sourceGeometryChanges=0,sourcePoseChanges=0,architectureReview=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete indexed source triangle arrays, their order and all represented coordinates are exactly byte-identical to the independently authenticated literal clear-cap proof; actual drawn ground is identical. Reuses mathematical paths only for identical inputs, with no tolerance or changed-source approval transfer. Architectural-role, support, collision, neighbour, runtime/browser and publication remain independent.')
    save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('exact_cap_equivalence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-four-world-coordinate-equivalence-for-existing-clear-cap-proof',refs,result)

if __name__=='__main__':main()

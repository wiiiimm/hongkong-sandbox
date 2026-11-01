"""Bind a represented contact to an exact adjacent original native plane.

Diagnostic only. Retains every new facet pair; no tolerance, contact suppression,
geometry change, source-role or installation approval.
"""
import argparse
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,sub,cross,dot
from exact_original_component_contacts_20261009 import contact_measure

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','contacts','roles','uid','native']:p.add_argument('--'+k,required=True)
    for k in ['source-face','original-native-face','represented-native-face']:p.add_argument('--'+k,type=int,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch and a.original_native_face!=a.represented_native_face
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        f=base/batch/name;assert digest(f.read_bytes())==pins[batch][str(f.relative_to(ROOT))];refs.append(f);return read(f)
    selected=take(a.runtime,'selection.json.gz');source=next(r for r in selected['rows']if r['uid']==a.uid)
    attr=next(r for r in take(a.attributes,'attributes.json.gz')['rows']if r['uid']==a.uid)
    native=next(r for r in take(a.contacts,'native-input.json.gz')['rows']if r['uid']==a.native)
    nattr=next(r for r in take(a.contacts,'native-attributes.json.gz')['rows']if r['uid']==a.native)
    role_summary=take(a.roles,'summary.json');worlds={};hashes={}
    for uid,row,path,sha in [(a.uid,attr,ROOT/source['candidate']['path'],source['sourceSHA256']),(a.native,nattr,ROOT/native['path'],native['entry']['sha256'])]:
        assert digest(path.read_bytes())==sha==row['sourceSHA256'];refs.append(path);hashes[uid]=sha;ix=np.asarray(row['completeOriginalIndex']).reshape(-1,3)
        worlds[uid]={'original':decode_original_world_triangles(path.read_bytes())}
        for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(row[key],dtype='<f8').reshape(-1,3)[ix]
    rows=[];stem=a.uid.split('/')[1]+'--'+a.native.split('/')[1]+'--'
    for mode in ['original','literal','leftF32','balancedF32']:
        tri=worlds[a.native][mode];left,right=rational_face(tri[a.original_native_face]),rational_face(tri[a.represented_native_face]);shared=set(left)&set(right);assert len(shared)==2
        normal=cross(sub(left[1],left[0]),sub(left[2],left[0]));assert any(normal)and all(dot(normal,sub(q,left[0]))==0 for q in right)
        summary=next(r for r in role_summary['rows']if r['uid']==a.uid and r['nativeUid']==a.native and r['mode']==mode)
        assert summary['sourceWorldSHA256']==digest(worlds[a.uid][mode].astype('<f8').tobytes())and summary['nativeWorldSHA256']==digest(tri.astype('<f8').tobytes())
        records=take(a.roles,stem+mode+'.json.gz');hits=[r for r in records if r['sourceFaceA']==a.source_face and r['sourceFaceB']in[a.original_native_face,a.represented_native_face]]
        assert any(r['sourceFaceB']==a.original_native_face for r in hits)
        if mode=='original':assert not any(r['sourceFaceB']==a.represented_native_face for r in hits)
        points={tuple(Fraction(v)for v in q)for r in hits for q in r['exactPoints']};assert points
        rows.append(dict(mode=mode,sourceWorldSHA256=summary['sourceWorldSHA256'],nativeWorldSHA256=summary['nativeWorldSHA256'],sharedExactVertices=[[str(v)for v in q]for q in sorted(shared)],allThreePlaneResiduals=['0','0','0'],completeOriginalNativeFaces=[tri[a.original_native_face].tolist(),tri[a.represented_native_face].tolist()],retainedRawContacts=hits,combinedFiniteContact=contact_measure(points)))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    result=dict(uids=[a.uid,a.native],sourceSHA256ByUid=hashes,sourceFace=a.source_face,adjacentNativeFaces=[a.original_native_face,a.represented_native_face],rows=rows,exactAdjacentCoplanarNativePatch=True,newPairsRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__+' The complete source/native arrays and full previously measured contact context remain bound; this is a named exact-plane/diagonal partition observation, not whole-source collision or architectural acceptance.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']);module('adjacent_native_plane_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-adjacent-native-plane-contact-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

"""Trace represented pair contacts to original facet pairs; no tolerance or acceptance."""
import argparse
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from nam_cheong_pair_body_contact_views_v1_20261023 import minor_plane_extent_squared


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','contacts','roles']:ap.add_argument('--'+key,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
    def take(n,file):
        if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
        path=base/n/file;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    finite=take(a.contacts,'summary.json');roles=take(a.roles,'summary.json');uids=finite['uids'];assert len(uids)==2 and roles['uids']==uids and roles['sourceSHA256ByUid']==finite['sourceSHA256ByUid']
    attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']};selection=take(a.runtime,'selection.json.gz');selected={r['uid']:r for r in selection['rows']};worlds={};deltas={}
    fields=dict(literal='completeLiteralWorldPosition',leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',balancedF32='completeExplicitBalancedFloat32WorldPosition')
    for uid in uids:
        r=selected[uid];attr=attrs[uid];path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['sourceSHA256']==attr['sourceSHA256']==finite['sourceSHA256ByUid'][uid];refs.append(path);original=decode_original_world_triangles(path.read_bytes());ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds[uid]={'original':original};deltas[uid]={}
        for mode,field in fields.items():
            tri=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix];assert tri.shape==original.shape and len(tri)==r['triangles'];worlds[uid][mode]=tri
            flat_o=original.reshape(-1,3);flat_t=tri.reshape(-1,3);maximum=[]
            for axis in range(3):
                maximum.append(str(max(abs(F(float(x))-F(float(y)))for x,y in zip(flat_o[:,axis],flat_t[:,axis]))))
            deltas[uid][mode]=dict(completeIndexedVerticesCompared=len(flat_o),exactMaximumAbsoluteCoordinateDeltaM=maximum)
    assert {r['mode']for r in finite['rows']}=={'original',*fields}
    for mode in finite['rows']:assert mode['sourceWorldSHA256ByUid']=={uid:digest(worlds[uid][mode['mode']].astype('<f8').tobytes())for uid in uids}
    original=take(a.roles,'original.json.gz');by={(r['sourceFaceA'],r['sourceFaceB']):r for r in original};assert len(by)==len(original);rows=[]
    for mode in ['original',*fields]:
        raw=take(a.contacts,mode+'.json.gz');classified=take(a.roles,mode+'.json.gz');assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0 and len(raw['contacts'])==len(classified)
        assert all({k:v for k,v in c.items()if k!='contactRole'}==r for c,r in zip(classified,raw['contacts']));records=[]
        for c in classified:
            if c['contactRole']!='transverse-surface-crossing':continue
            ia,ib=c['sourceFaceA'],c['sourceFaceB'];old=by.get((ia,ib));p,q=worlds[uids[0]][mode][ia],worlds[uids[1]][mode][ib];left=minor_plane_extent_squared(p,q);right=minor_plane_extent_squared(q,p)
            records.append(dict(sourceFaceA=ia,sourceFaceB=ib,representedContact=c,originalPairContact=old,originalPairRole=old['contactRole']if old else None,sourceAAgainstBPlane=left,sourceBAgainstAPlane=right,minimumBidirectionalMinorPlaneExtentSquaredM2=str(min(F(left['exactMinorPlaneSideExtentSquaredM2']),F(right['exactMinorPlaneSideExtentSquaredM2']))),physicalAcceptance=False))
        r=dict(mode=mode,transverseSegments=len(records),allRepresentedCrossingsHaveOriginalFacetPairContacts=all(c['originalPairContact']is not None for c in records),originalRoleCounts=dict(Counter(c['originalPairRole']for c in records)),rows=records);rows.append(r);save(out/(mode+'.json.gz'),r);print({k:r[k]for k in ['mode','transverseSegments','allRepresentedCrossingsHaveOriginalFacetPairContacts','originalRoleCounts']},flush=True)
    result=dict(uids=uids,sourceSHA256ByUid=finite['sourceSHA256ByUid'],allRepresentedCrossingsHaveOriginalFacetPairContacts=all(r['allRepresentedCrossingsHaveOriginalFacetPairContacts']for r in rows),completeCorrespondingVertexDeltas=deltas,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact source-face pair correspondence and exact rational coordinate deltas only. Every represented crossing is traced to its original facet-pair contact when present. Plane-side extents are diagnostic and are NOT finite penetration depths or a tolerance allowance. Original point/line contacts alone do not grant architectural, physical, collision or publication approval; all raw represented crossings remain unchanged.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','nam_cheong_pair_body_contact_views_v1_20261023.py']);module('original_pair_lineage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-represented-transverse-contact-original-facet-pair-lineage',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

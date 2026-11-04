"""Exact affine context for saved source-pair contacts in each renderer representation.

Source-only evidence: no contact/identity/physical approval or current terrain claim.
Every saved contact vertex must belong exactly to both represented source faces.
"""
import argparse,sys,uuid
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def exact_triangle(t):return [[F(float(v))for v in row]for row in t]


def barycentric(t,p):
    a,b,c=t;u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];q=[p[i]-a[i]for i in range(3)]
    for i,j in combinations(range(3),2):
        det=u[i]*v[j]-u[j]*v[i]
        if det:
            s=(q[i]*v[j]-q[j]*v[i])/det;r=(u[i]*q[j]-u[j]*q[i])/det;w=[1-s-r,s,r]
            break
    else:
        axis=next((i for i in range(3)if u[i]or v[i]),None)
        if axis is None:
            assert p==a,'Point not on zero-dimensional source face';return [F(1),F(0),F(0)]
        lo=min(range(3),key=lambda k:t[k][axis]);hi=max(range(3),key=lambda k:t[k][axis])
        s=(p[axis]-t[lo][axis])/(t[hi][axis]-t[lo][axis]);w=[F(0)]*3;w[lo]=1-s;w[hi]=s
    assert min(w)>=0 and sum(w)==1,'Contact outside represented source face'
    assert all(sum(w[k]*t[k][i]for k in range(3))==p[i]for i in range(3)),'Contact off represented source face'
    return w


def displacement_context(original,represented,point):
    w=barycentric(represented,point)
    mapped=[sum(w[k]*original[k][i]for k in range(3))for i in range(3)]
    bound=[max(abs(original[k][i]-represented[k][i])for k in range(3))for i in range(3)]
    delta=[abs(point[i]-mapped[i])for i in range(3)]
    assert all(delta[i]<=bound[i]for i in range(3))
    return delta,bound


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','contacts']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--lease');a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.attributes,a.contacts])and not out.exists()
    parent,pin=authenticate(base/a.contacts);summary=read(base/a.contacts/'summary.json');assert digest((base/a.contacts/'summary.json').read_bytes())==pin[str((base/a.contacts/'summary.json').relative_to(ROOT))]
    uids=summary['uids'];assert len(uids)==2 and len(set(uids))==2
    if not a.lease:
        assert not local.exists();c=reservations.claim('source-pair-representation-'+str(uuid.uuid4()),['building:'+u for u in uids]+['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],'Source reservation unavailable'
        return execute_reserved(c['reservation'],local/'reservation.json',[sys.executable,__file__,*sys.argv[1:],'--lease',str(local/'reservation.json')])
    lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+u for u in uids}<=set(lease['resources']);refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    summary=take(a.contacts,'summary.json');selected=take(a.runtime,'selection.json.gz');rows={r['uid']:r for r in selected['rows']};attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']};worlds={};source_shas={}
    for u in uids:
        row=rows[u];attr=attrs[u];asset=ROOT/row['candidate']['path'];refs.append(asset);source_shas[u]=digest(asset.read_bytes());assert source_shas[u]==row['sourceSHA256']==attr['sourceSHA256']==summary['sourceSHA256ByUid'][u]
        worlds[u]={'original':decode_original_world_triangles(asset.read_bytes())};index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[u][mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
        assert all(len(t)==row['triangles']for t in worlds[u].values())
    reports=[]
    for mode in ['original','literal','leftF32','balancedF32']:
        expected=next(r for r in summary['rows']if r['mode']==mode)
        assert expected['sourceWorldSHA256ByUid']=={u:digest(worlds[u][mode].tobytes())for u in uids}
        proof=take(a.contacts,mode+'.json.gz');assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0 and len(proof['contacts'])==expected['finiteContactPairs']
        cache={};pairs=[];max_delta=[F(0)]*3;max_bound=[F(0)]*3
        for contact in proof['contacts']:
            delta=[F(0)]*3;bound=[F(0)]*3
            for uid,face in zip(uids,[contact['sourceFaceA'],contact['sourceFaceB']]):
                key=(uid,face)
                if key not in cache:cache[key]=(exact_triangle(worlds[uid]['original'][face]),exact_triangle(worlds[uid][mode][face]))
                original,represented=cache[key]
                for vertex in contact['exactPoints']:
                    d,b=displacement_context(original,represented,[F(v)for v in vertex])
                    delta=[max(delta[i],d[i])for i in range(3)];bound=[max(bound[i],b[i])for i in range(3)]
            max_delta=[max(max_delta[i],delta[i])for i in range(3)];max_bound=[max(max_bound[i],bound[i])for i in range(3)]
            pairs.append(dict(sourceFaceA=contact['sourceFaceA'],sourceFaceB=contact['sourceFaceB'],dimension=contact['dimension'],vertices=len(contact['exactPoints']),maximumMappedDisplacementExact=[str(v)for v in delta],maximumSourceVertexDisplacementExact=[str(v)for v in bound]))
        report=dict(mode=mode,allSavedContactsExamined=True,allVerticesExactlyOnBothRepresentedFaces=True,allAffineDisplacementsWithinExactVertexBounds=True,contactPairs=len(pairs),areaContactPairs=sum(c['dimension']==2 for c in pairs),sourceFacesOmitted=0,maximumMappedDisplacementM=[float(v)for v in max_delta],maximumSourceVertexDisplacementM=[float(v)for v in max_bound],maximumMappedDisplacementExact=[str(v)for v in max_delta],maximumSourceVertexDisplacementExact=[str(v)for v in max_bound]);reports.append(report);save(out/(mode+'.json.gz'),dict(summary=report,pairs=pairs));assert reservations.owns(lease);print(report,flush=True)
    result=dict(uids=uids,sourceSHA256ByUid=source_shas,rows=reports,sourceGeometryChanges=0,sourcePoseChanges=0,originalContactScanNotRepeated=True,currentSceneRevalidated=False,identityAccepted=False,physicalAcceptance=False,collisionExemption=False,installationApproved=False,publication=False,qualification='Every saved exact contact vertex was proven to lie in both represented source triangles using rational barycentric coordinates. Its affine image on the unchanged original face differs by at most that face original-to-rendered vertex displacement, axis by axis, exactly. This quantifies representation effects; it does not approve original contacts, redefine collision tolerances, eliminate raw intersections, certify terrain/support, or grant identity/installation approval. Current complete scene and terrain obligations remain.')
    save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py']);assert reservations.owns(lease);module('pair_representation_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-source-pair-contact-representation-context',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

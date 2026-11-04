"""Classify represented area contacts against exact original face planes; no approval."""
import argparse,sys,uuid
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_pair_contact_representation_context_v1_20261103 import exact_triangle
from observed_reserved_runner_v2_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module


def cross(u,v):return [u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
def normal(t):return cross([t[1][i]-t[0][i]for i in range(3)],[t[2][i]-t[0][i]for i in range(3)])
def plane_context(a,b):
    na,nb=normal(a),normal(b);assert any(na)and any(nb),'Area contact must retain nondegenerate original faces'
    sa=[sum(na[i]*(p[i]-a[0][i])for i in range(3))for p in b]
    sb=[sum(nb[i]*(p[i]-b[0][i])for i in range(3))for p in a]
    parallel=not any(cross(na,nb));coplanar=parallel and not any(sa)
    def role(n):return 'horizontal'if not n[0]and not n[2]else'vertical'if not n[1]else'oblique'
    return dict(originalPlaneRelation='coplanar'if coplanar else'parallel-separated'if parallel else'non-parallel',
        originalNormalRoles=[role(na),role(nb)],
        signedPlaneNumeratorRangeA=[str(min(sa)),str(max(sa))],signedPlaneNumeratorRangeB=[str(min(sb)),str(max(sb))],
        bothOriginalTrianglesStraddleOtherPlane=min(sa)<0<max(sa)and min(sb)<0<max(sb))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','contacts','representation-context']:ap.add_argument('--'+k,required=True)
    ap.add_argument('--lease');a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.runtime,a.contacts,a.representation_context])and not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    context=take(a.representation_context,'summary.json');uids=context['uids'];assert len(uids)==2 and context['sourceGeometryChanges']==0 and context['sourcePoseChanges']==0
    if not a.lease:
        assert not local.exists();c=reservations.claim('source-pair-original-planes-'+str(uuid.uuid4()),['building:'+u for u in uids]+['immutable-source-proof:'+a.batch],batch=a.batch,ttl=3600);assert c['ok'],'Source reservation unavailable'
        return execute_reserved(c['reservation'],local/'reservation.json',[sys.executable,__file__,*sys.argv[1:],'--lease',str(local/'reservation.json')])
    lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+u for u in uids}<=set(lease['resources']);selected=take(a.runtime,'selection.json.gz');by={r['uid']:r for r in selected['rows']};source=take(a.contacts,'summary.json');assert source['uids']==uids and source['sourceSHA256ByUid']==context['sourceSHA256ByUid'];worlds={}
    for u in uids:
        row=by[u];asset=ROOT/row['candidate']['path'];refs.append(asset);assert digest(asset.read_bytes())==row['sourceSHA256']==context['sourceSHA256ByUid'][u];worlds[u]=decode_original_world_triangles(asset.read_bytes());assert len(worlds[u])==row['triangles']
    old=take(a.contacts,'original.json.gz');assert old['allPairsExamined']and old['sourceFacesOmitted']==0
    old_pairs={(c['sourceFaceA'],c['sourceFaceB']):c['dimension']for c in old['contacts']};assert len(old_pairs)==len(old['contacts']);reports=[];cache={}
    for mode in ['original','literal','leftF32','balancedF32']:
        raw=take(a.contacts,mode+'.json.gz');mapped=take(a.representation_context,mode+'.json.gz')['summary'];assert mapped['allSavedContactsExamined']and mapped['allVerticesExactlyOnBothRepresentedFaces']and mapped['allAffineDisplacementsWithinExactVertexBounds'];assert len(raw['contacts'])==mapped['contactPairs']
        rows=[]
        for c in raw['contacts']:
            if c['dimension']!=2:continue
            pair=(c['sourceFaceA'],c['sourceFaceB'])
            if pair not in cache:cache[pair]=plane_context(*[exact_triangle(worlds[u][f])for u,f in zip(uids,pair)])
            rows.append(dict(sourceFaceA=pair[0],sourceFaceB=pair[1],originalContactDimension=old_pairs.get(pair),**cache[pair]))
        assert len(rows)==mapped['areaContactPairs'];save(out/(mode+'.json.gz'),dict(rows=rows))
        reports.append(dict(mode=mode,areaContactPairs=len(rows),originalPlaneRelations=dict(Counter(r['originalPlaneRelation']for r in rows)),originalNormalRolePairs=dict(Counter('/'.join(r['originalNormalRoles'])for r in rows)),originalContactDimensions=dict(Counter(str(r['originalContactDimension'])for r in rows)),bothOriginalTrianglesStraddleOtherPlane=sum(r['bothOriginalTrianglesStraddleOtherPlane']for r in rows)))
        assert reservations.owns(lease)
    result=dict(uids=uids,sourceSHA256ByUid=context['sourceSHA256ByUid'],rows=reports,originalFacesUnchanged=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceOnlyEvidence=True,currentSceneRevalidated=False,physicalAcceptance=False,identityAccepted=False,collisionExemption=False,installationApproved=False,publication=False,qualification='Exact rational original plane relations for every saved positive-area represented contact. Signed plane numerators are unnormalised algebraic quantities, not distances or tolerance changes. Prior affine source-displacement bounds and all raw contact records remain. Nonparallel planes, coplanarity or tiny representation displacement alone do not approve source roles, interpenetration, support, terrain, collision or publication.')
    save(out/'summary.json',result);refs.extend([HERE/'original_pair_contact_representation_context_v1_20261103.py',HERE/'exact_packed_world_geometry_20261009.py']);assert reservations.owns(lease);module('area_original_plane_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-face-planes-for-represented-area-contacts',list(dict.fromkeys(refs)),result);print(result,flush=True)

if __name__=='__main__':main()

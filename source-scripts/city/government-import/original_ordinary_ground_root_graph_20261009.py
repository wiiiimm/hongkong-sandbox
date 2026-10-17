"""Source-only exact contact graph with separately typed ordinary ground roots.

Existing strict graph remains immutable. Every new ordinary root replays all
original indexed component samples against complete actual drawn ground, with
-.5 clearance/1m rim ceiling and genuine ±.1m anchors. No wall role or detached
component omission. All full-facet/foundation/foreign/current gates stay separate.
"""
import hashlib,json
from fractions import Fraction
import numpy as np,shapely
from original_multi_actor_support_graph_20261009 import verify as strict_graph
from original_ordinary_rim_accounting_20261009 import verify as ordinary_rim
from original_wall_rim_accounting_20261009 import original_samples

def sha(value):return hashlib.sha256(value).hexdigest()

def verify(triangles,actors,components,contacts,indexed_sources,drawn_ground,*,expected_binding,current_binding):
    tri=np.asarray(triangles,float);ground=np.asarray(drawn_ground,float)
    assert ground.ndim==3 and ground.shape[1:]==(3,3) and len(ground) and np.isfinite(ground).all()
    assert expected_binding==current_binding and current_binding['currentDrawnGroundSHA256']==sha(ground.tobytes())
    assert current_binding['originalIndexedSourcesSHA256']==sha(json.dumps(indexed_sources,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    interfaces=[{'passed':False} for _ in components]
    binding={**current_binding,'groundInterfacesSHA256':sha(json.dumps(interfaces,sort_keys=True,separators=(',',':')).encode())}
    strict=strict_graph(tri,actors,components,interfaces,contacts,expected_binding=binding,current_binding=binding)
    sources={s['uid']:s for s in indexed_sources};assert set(sources)=={a['uid'] for a in actors} and len(sources)==len(indexed_sources)
    by_uid={a['uid']:a for a in actors};decoded={}
    for uid,s in sources.items():
        p=np.asarray(s['position'],float).reshape(-1,3);idx=np.asarray(s['index'])
        assert np.isfinite(p).all() and np.issubdtype(idx.dtype,np.integer);idx=idx.reshape(-1,3)
        assert (idx>=0).all() and (idx<len(p)).all()
        a=by_uid[uid];start,end=a['globalFaceRange'];assert np.array_equal(p[idx],tri[start:end]),'Original indexed source differs'
        assert s['sourceSHA256']==a['sourceSHA256'];decoded[uid]=(p,idx,start)
    polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>0
    faces=ground[valid];polys=polys[valid];assert len(faces);tree=shapely.STRtree(polys);rational={}
    def height(x,z):
        qx,qz=Fraction(float(x)),Fraction(float(z));values=[]
        for k in tree.query(shapely.Point(x,z)):
            k=int(k)
            if k not in rational:rational[k]=[[Fraction(float(v)) for v in p] for p in faces[k]]
            a,b,c=rational[k];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
            if not den:continue
            u=((b[2]-c[2])*(qx-c[0])+(c[0]-b[0])*(qz-c[2]))/den
            v=((c[2]-a[2])*(qx-c[0])+(a[0]-c[0])*(qz-c[2]))/den;w=1-u-v
            if min(u,v,w)>=0:values.append(u*a[1]+v*b[1]+w*c[1])
        assert values,'Missing exact drawn ground at original component sample'
        return float(max(values))
    roots=[];proofs=[]
    for k,c in enumerate(components):
        p,idx,start=decoded[c['actorUID']];local=np.asarray(c['globalOriginalFaces'])-start
        vertex_ids=sorted(set(idx[local].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(vertex_ids)}
        cp=p[vertex_ids];ci=np.asarray([[mapping[int(v)] for v in f] for f in idx[local]],dtype=np.uint32);bottom=float(cp[:,1].min())
        samples=original_samples(cp,ci,bottom);missing=False
        try:
            for r in samples:
                g=height(r['point'][0],r['point'][2]);r.update(ground=g,gap=r['point'][1]-g)
            low=[r for r in samples if r['point'][1]<=bottom+.35]
            metric={'checks':len(samples),'lowRimChecks':len(low),'minSurfaceGap':min(r['gap'] for r in samples),'minLowGap':min(r['gap'] for r in low),'maxLowGap':max(r['gap'] for r in low)}
            result=ordinary_rim(cp,ci,bottom,samples,expected_metric=metric);roots.append(k)
            proof={'accepted':True,'ordinaryRim':result,'metric':metric}
        except AssertionError as error:proof={'accepted':False,'reason':str(error)}
        proofs.append({**proof,'component':k,'actorUID':c['actorUID'],'completeOriginalFaces':c['globalOriginalFaces'],'originalRuntimeVertexIds':vertex_ids,'sampleInventorySHA256':sha(json.dumps(samples,sort_keys=True,separators=(',',':'),allow_nan=False).encode())})
    adjacency={i:set() for i in range(len(components))}
    for contact in strict['exactOriginalContacts']:
        a,b=contact['components'];adjacency[a].add(b);adjacency[b].add(a)
    reached=set(roots);todo=list(roots);parents={i:None for i in roots}
    while todo:
        a=todo.pop()
        for b in sorted(adjacency[a]):
            if b not in reached:reached.add(b);parents[b]=a;todo.append(b)
    reasons=[] if roots else ['no-genuine-ordinary-original-ground-root']
    reasons+=['unresolved-original-component:'+str(i) for i in sorted(set(adjacency)-reached)]
    return {'contract':'unchanged-original-ordinary-ground-root-contact-graph-v1','supportInterfaceAccepted':not reasons,'reasons':reasons,'completeOriginalFaces':len(tri),'completeOriginalComponentCount':len(components),'ordinaryGroundRootComponents':roots,'ordinaryRootProofs':proofs,'exactOriginalContacts':strict['exactOriginalContacts'],'resolvedOriginalComponents':sorted(reached),'groundRootedComponentParents':parents,'strictOriginalGraphWithoutNewRoots':strict,'sourceGeometryChanges':0,'wallRoleCredit':False,'fullAcceptance':False,'publication':False}

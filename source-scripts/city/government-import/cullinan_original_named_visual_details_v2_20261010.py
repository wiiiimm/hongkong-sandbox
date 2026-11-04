"""Source-only named Cullinan facade ribbons/double-sided detail proposal.

No structural roots/bridges, carrier reacceptance or current import acceptance.
The source adapter must independently verify provider/streams/current inputs,
root receipts and complete all-facet physical/native/foreign gates before any
promotion. Every authored duplicate and free edge remains untouched.
"""
import hashlib,json,collections
from fractions import Fraction as F
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as edge_band
WORLD='5c42e8ace044f7037789054d378c27fbdfc4692bceb16666daae5e5110987509'
PARTS={270:dict(uid='landsd/161931:0',body=264,faces=[134521,134522,134523,134580,134581,134582],sha='bb1cd95f7c935ef1bfcd40cdfb430888f0701561d5381e71a92e8a6fb99079c5',anchor=[(134521,0),(134521,1)],back=None,role='original-double-sided-folded-facade-detail'),294:dict(uid='landsd/120158:0',body=279,faces=[153546,153547,153548],sha='477473a61b781b5ed5ee5cb92cbc08d5b72c94cbd200077ccd99546291c8e344',anchor=[(153546,0),(153548,2)],back=[(153546,0),(153546,2),(153548,2)],role='original-tapered-facade-ribbon'),295:dict(uid='landsd/120158:0',body=279,faces=[153582,153583,153584],sha='dd334fc88c38ee77e5ae73d06dd81ad7ce99ff4d163c5a9ef35b7ad35f537018',anchor=[(153582,0),(153584,0)],back=[(153582,0),(153582,1),(153584,0)],role='original-tapered-facade-ribbon')}
def sha(x):return hashlib.sha256(np.asarray(x,float).tobytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def verify(original,literal,float32_world,graph,*,frozen_context,expected_binding,current_binding):
 modes=[('provider-original',np.asarray(original,float)),('captured-runtime-literal',np.asarray(literal,float)),('literal-world-float32-projection',np.asarray(float32_world,float))]
 assert all(t.shape==(154603,3,3) and np.isfinite(t).all()for _,t in modes)
 assert expected_binding==current_binding and current_binding
 assert sha(modes[0][1])==WORLD==current_binding['originalWorldSHA256']
 assert sha(modes[1][1])==current_binding['literalWorldSHA256'] and sha(modes[2][1])==current_binding['float32WorldSHA256']
 assert np.array_equal(modes[2][1],modes[1][1].astype(np.float32).astype(float)),'Bind literal-world Float32 projection without claiming shader pixel certification'
 assert np.max(np.abs(modes[0][1]-modes[1][1]))<=1e-9
 assert canonical(graph)==current_binding['strictGraphSHA256'] and canonical(frozen_context)==current_binding['frozenContextSHA256']
 assert graph['binding']['completeOriginalWorldTrianglesSHA256']==WORLD and len(graph['components'])==296
 assert sorted(f for c in graph['components']for f in c['globalOriginalFaces'])==list(range(154603))
 assert graph['ordinaryGroundRootComponents']==[11,51] and not graph['supportInterfaceAccepted']
 assert frozen_context['independentLiteralOrdinaryNativeRoots']==[11,51]
 assert all(p['ordinaryLiteralSampleRootVerified'] and p['nativeReacceptance']is False for p in frozen_context['literalRootProofs'])
 assert {p['component']for p in frozen_context['literalRootProofs']}=={11,51}
 rooted=set(graph['resolvedOriginalComponents']);visual=set(PARTS)
 assert all(i in rooted for i,c in enumerate(graph['components'])if c['actorUID']!='landsd/262871:0'and i not in visual)
 assert not rooted&visual
 assert all(not(set(c['components'])&visual)for c in graph['contactWitnesses']), 'Visual details must supply no structural graph edges'
 assert all(p not in visual for p in graph['groundRootedComponentParents'].values())
 for k,p in PARTS.items():
  assert graph['components'][k]['actorUID']==p['uid'] and graph['components'][k]['globalOriginalFaces']==p['faces']
  assert sha(modes[0][1][p['faces']])==p['sha'] and p['body']in rooted and graph['components'][p['body']]['actorUID']==p['uid']
 results=[]
 for mode,t in modes:
  for k,p in PARTS.items():
   detail=t[p['faces']];bodyids=np.array(graph['components'][p['body']]['globalOriginalFaces']);lo=np.nextafter(detail.min(axis=(0,1))-.1,-np.inf);hi=np.nextafter(detail.max(axis=(0,1))+.1,np.inf)
   near=bodyids[np.all(t[bodyids].max(axis=1)>=lo,axis=1)&np.all(t[bodyids].min(axis=1)<=hi,axis=1)];assert len(near)
   anchorpoints=[tuple(t[i,j])for i,j in p['anchor']];assert len(set(anchorpoints))==2 and anchorpoints[0][1]<anchorpoints[1][1]
   if p['back'] is None:assert anchorpoints[0][1]==detail[:,:,1].min() and anchorpoints[1][1]==detail[:,:,1].max()
   anchors=[]
   for i in p['faces']:
    for j in near:
     if np.any(t[j].max(axis=0)<t[i].min(axis=0))or np.any(t[j].min(axis=0)>t[i].max(axis=0)):continue
     ps=intersection_points(rational_face(t[i]),rational_face(t[j]));assert len(ps)<=1,'A positive-dimensional interface belongs to structural diagnosis, not this role'
     for x in ps:
      for n,a in enumerate(anchorpoints):
       if x==tuple(F(float(v))for v in a):anchors.append(dict(endpoint=n,faces=[i,int(j)],exactPoint=[str(v)for v in x]))
   assert {a['endpoint']for a in anchors}=={0,1},'Two exact original endpoints required in each bound representation'
   incidences=collections.defaultdict(list)
   for i in p['faces']:
    v=list(map(tuple,t[i]));
    for a,b in zip(v,v[1:]+v[:1]):incidences[tuple(sorted((a,b)))].append(i)
   back=[]
   if p['back']:
    points=[t[i,j]for i,j in p['back']];assert points[0][1]<points[1][1]<points[2][1]
    assert tuple(points[0])==anchorpoints[0] and tuple(points[-1])==anchorpoints[-1], 'Use actual mounted back-chain endpoints, never whole ribbon extremes from a free slanted front edge'
    for a,b in zip(points,points[1:]):
     assert len(incidences[tuple(sorted((tuple(a),tuple(b))))])==1,'Every prescribed back edge must remain original boundary'
     proof=edge_band(np.asarray([a,b]),t[near]);assert proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'],'Entire original back edge must fit unchanged finite .1m band';back.append(proof)
    assert len([e for e,v in incidences.items()if len(v)==1])==5
   else:
    groups=collections.Counter(tuple(sorted(map(tuple,f)))for f in detail);assert len(groups)==3 and set(groups.values())=={2},'Preserve exact original two-sided duplicates'
    normals=np.cross(detail[:,1]-detail[:,0],detail[:,2]-detail[:,0]);assert np.all(np.linalg.norm(normals,axis=1)>0)
    for key in groups:
     normals_for=[n for f,n in zip(detail,normals)if tuple(sorted(map(tuple,f)))==key];assert np.array_equal(normals_for[0],-normals_for[1])
   results.append(dict(component=k,mode=mode,role=p['role'],completeFaces=p['faces'],completeOriginalHostFaces=near.tolist(),exactEndpointAttachments=anchors,completeBackEdgeProofs=back,originalEdgeIncidences=[dict(edge=e,faces=v)for e,v in sorted(incidences.items())],wholeFacetPositiveCredit=False))
 return dict(contract='source-only-cullinan-original-named-visual-detail-proposal-v2',proposalVerified=True,rows=results,rawStrictGraphReasons=graph['reasons'],nativeReacceptance=False,wholeNativeNegativesPreserved=True,addedGroundRoots=[],addedLoadBearingEdges=[],visualDetailsCanSupportOthers=False,fullAcceptance=False,currentPromotionRequiresCompleteIndependentCarrierPhysicalForeignRuntimeChecks=True,sourceGeometryChanges=0,installationApproved=False,bindings=current_binding)

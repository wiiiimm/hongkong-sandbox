"""Named, unchanged Parkview roof appendage; never structural support.

Only the complete authored six-edge bottom mounting loop gets finite-band
accounting. Two upper openings and two triple incidences remain explicitly
recorded. This is not generic equipment/closed-solid/root certification.
The source-specific current adapter must independently replay all host roots,
provider streams, all current foreign/terrain/physical and runtime guards.
"""
from collections import defaultdict
import hashlib,json
from fractions import Fraction
import numpy as np
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
SOURCE='c2a4c7342c9edfed5abdd1851fda88a9860d04e2b9b34236faf96e98e828b943'
FACES=[63507,63508,63509,63510,*range(67610,67669),*range(73283,73292)]
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(x):return hashlib.sha256(np.asarray(x,float).tobytes()).hexdigest()
def verify(triangles,component_faces,contexts,host_faces,independent_host_support,template,*,expected_binding,current_binding):
 t=np.asarray(triangles,float);assert t.shape==(73812,3,3)and np.isfinite(t).all()
 assert current_binding==expected_binding and current_binding['ownedSourceSHA256']==SOURCE
 inputs=dict(completeWorldSHA256=sha(t),completeComponentFacesSHA256=canonical(component_faces),completeFacetContextsSHA256=canonical(contexts),completeHostFacesSHA256=canonical(host_faces),independentHostSupportSHA256=canonical(independent_host_support),sourceRoleTemplateSHA256=canonical(template))
 for k,v in inputs.items():assert current_binding[k]==v,'Changed named source/context/support input '+k
 assert component_faces==FACES and template['component']==324 and template['hostComponent']==285
 assert template['kind']=='parkview-original-mounted-roof-appendage-324'
 assert independent_host_support['hostComponent']==285 and independent_host_support['hostGroundedIndependentlyOfUnit324']is True
 assert 324 not in independent_host_support['creditedRootOrBridgeComponents']
 assert host_faces==sorted(set(host_faces))and host_faces and not set(host_faces)&set(FACES)
 assert len(contexts)==len(t)and [r['sourceFace']for r in contexts]==list(range(len(t)))
 for i in FACES+host_faces:
  c=contexts[i];assert c['sourceFaceSHA256']==sha(t[i])
  assert c['groundProjectionCovered']is True and c['existingOrdinaryClearanceBoundProved']is True
  v=c['exactCertifiedLowerClearanceM'];assert isinstance(v,(str,int,float))and not isinstance(v,bool)
  if isinstance(v,float):assert np.isfinite(v)
  assert Fraction(v)>=Fraction(-1,2)
 normals=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normals,axis=1)
 assert all(length[i]>0 for i in FACES)
 roofs=[i for i in host_faces if normals[i,1]/length[i]>.25];assert roofs
 edges=defaultdict(list);adj={i:set()for i in FACES}
 for i in FACES:
  for a,b in zip(t[i],np.roll(t[i],-1,axis=0)):
   assert tuple(a)!=tuple(b);edges[tuple(sorted([tuple(a),tuple(b)]))].append(i)
 for members in edges.values():
  for i in members:adj[i].update(set(members)-{i})
 seen={FACES[0]};todo=list(seen)
 while todo:
  for i in adj[todo.pop()]:
   if i not in seen:seen.add(i);todo.append(i)
 assert seen==set(FACES),'Detached named original face'
 boundary=sorted(e for e,m in edges.items()if len(m)==1);minimum=float(t[FACES,:,1].min())
 lower=[e for e in boundary if e[0][1]==e[1][1]==minimum];upper=[e for e in boundary if e not in lower]
 triples=[dict(originalEdge=[list(v)for v in e],completeOriginalIncidentFaces=m)for e,m in edges.items()if len(m)>2]
 assert len(boundary)==8 and len(lower)==6 and len(upper)==2 and len(triples)==2
 assert all(len(r['completeOriginalIncidentFaces'])==3 for r in triples)
 assert template['completeEveryOriginalBoundary']==[[list(v)for v in e]for e in boundary]
 assert template['completeOriginalTripleIncidences']==triples
 a=defaultdict(set)
 for p,q in lower:a[p].add(q);a[q].add(p)
 assert all(len(v)==2 for v in a.values());seen={min(a)};todo=list(seen)
 while todo:
  for i in a[todo.pop()]:
   if i not in seen:seen.add(i);todo.append(i)
 assert seen==set(a),'Incomplete or disconnected authored mounting loop'
 bands=[]
 for e in boundary:
  p=verify_contact_segment(np.asarray(e),t[roofs]);is_lower=e in lower
  assert p['verifiedCompleteOriginalEdgeContactBand']is is_lower,'Changed lower mount or original upper-opening failure'
  p['completeOriginalSurfacePieces']=[{**r,'originalSourceFace':roofs[r['originalSurfaceFace']]}for r in p['completeOriginalSurfacePieces']]
  bands.append(dict(originalBoundaryEdge=[list(v)for v in e],isLowerMountingBoundary=is_lower,finiteBandProof=p))
 return dict(contract='parkview-original-roof-unit324-named-visual-accounting-v1',component=324,completeOriginalFaces=FACES,completeEveryOriginalBoundaryProof=bands,completeOriginalTripleIncidences=triples,completeOriginalLowerLoopEdges=6,upperOpeningsOutsideBandPreserved=2,strictContactBandM=.1,nonmanifoldSourcePreserved=True,independentlySupportedHostComponent=285,contactQualification='within existing finite contact band; not exact source contact',closedSolidCertified=False,addedRootOrBridgeCredit=False,structuralSupportCredit=False,sourceGeometryChanges=0,currentAcceptance=False,fullAcceptance=False,installationApproved=False)

"""Original finite interface versus two literal affine images, diagnostic only.

An exact original line/area interface can have two different production-world
images after floating arithmetic. This preserves their separation and certifies
only fixed .1m complete affine association; it never calls them actual contact,
adds a structural edge, welds geometry or infers universal GPU arithmetic.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points,cross,sub
from exact_original_component_contacts_20261009 import contact_measure
LIMIT=F(.1)

def array(v):
 a=np.asarray(v,float);assert a.shape==(3,3)and np.isfinite(a).all()
 assert any(cross(sub(rational_face(a)[1],rational_face(a)[0]),sub(rational_face(a)[2],rational_face(a)[0])))
 return a
def barycentric(face,p):
 n=cross(sub(face[1],face[0]),sub(face[2],face[0]));assert any(n)
 assert sum(n[i]*(p[i]-face[0][i])for i in range(3))==0
 k=max(range(3),key=lambda i:abs(n[i]));a,b=[i for i in range(3)if i!=k]
 v=sub(face[1],face[0]);w=sub(face[2],face[0]);q=sub(p,face[0]);det=v[a]*w[b]-v[b]*w[a];assert det
 t=(q[a]*w[b]-q[b]*w[a])/det;u=(v[a]*q[b]-v[b]*q[a])/det
 weights=(1-t-u,t,u);assert all(x>=0 for x in weights)and sum(weights)==1
 assert tuple(sum(weights[j]*face[j][i]for j in range(3))for i in range(3))==p
 return weights
def affine(weights,face):return tuple(sum(weights[j]*face[j][i]for j in range(3))for i in range(3))

def verify(original_a,original_b,literal_a,literal_b,*,expected_binding):
 raw=[array(v)for v in [original_a,original_b,literal_a,literal_b]]
 binding={name:hashlib.sha256(a.tobytes()).hexdigest()for name,a in zip(
  ['originalFaceASHA256','originalFaceBSHA256','actualLiteralFaceASHA256','actualLiteralFaceBSHA256'],raw)}
 assert binding==expected_binding,'Original/literal full face binding changed'
 a,b,la,lb=map(rational_face,raw);original=intersection_points(a,b)
 assert original,'A genuine exact original interface is required'
 measure=contact_measure(original);assert measure['dimension']>0,'Point-only original contact cannot be associated as a structural interface'
 points=[]
 for p in sorted(original):
  wa=barycentric(a,p);wb=barycentric(b,p);pa=affine(wa,la);pb=affine(wb,lb)
  distance=sum((pa[i]-pb[i])**2 for i in range(3))
  points.append(dict(exactOriginalInterfaceVertex=list(map(str,p)),
   exactOriginalFaceABarycentric=list(map(str,wa)),exactOriginalFaceBBarycentric=list(map(str,wb)),
   separateLiteralFaceAImage=list(map(str,pa)),separateLiteralFaceBImage=list(map(str,pb)),
   exactSquaredImageSeparationM2=str(distance),withinExistingFixedBand=distance<=LIMIT*LIMIT))
 actual=intersection_points(la,lb)
 actual_measure=contact_measure(actual)if actual else dict(dimension=-1,maximumSpanM=0,exactPoints=[],bounds=None)
 return dict(contract='complete-original-interface-separate-literal-affine-image-association-diagnostic-v1',
  binding=binding,completeOriginalExactInterface=measure,completeSeparateAffineInterfaceVertices=points,
  wholeConvexOriginalInterfaceAssociationProved=all(p['withinExistingFixedBand']for p in points),
  exactFixedBandM=str(LIMIT),maxExactSquaredAffineSeparationM2=str(max(F(p['exactSquaredImageSeparationM2'])for p in points)),
  actualLiteralExactContact=actual_measure,actualLiteralPositiveDimensionalContact=actual_measure['dimension']>0,
  actualLiteralNegativesPreserved=True,wholeInterfaceConvexAffineDifferenceBound=True,
  originalToLiteralArithmeticCauseNotCertified=True,structuralRootCredit=False,structuralBridgeCredit=False,
  geometryWeldingPerformed=False,sourceGeometryChanges=0,visualRoleAccepted=False,fullAcceptance=False)

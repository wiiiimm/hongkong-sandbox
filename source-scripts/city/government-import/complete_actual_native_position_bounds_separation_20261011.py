"""Exact positive X/Z separation of whole actual POSITION/matrix bounds.
Caller must independently bind current source/catalogue/viewer/loader hashes.
Bounds include unused vertices; strict dyadic comparison, no geographic buffer.
"""
from fractions import Fraction as F
import hashlib,json,math
OWNED_MODES={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
NATIVE_MODES={'actualLiteral':'completeLiteralBounds','explicitLeftAssociatedF32ModelMatrix':'completeLeftAssociatedF32Bounds','explicitBalancedF32ModelMatrix':'completeBalancedF32Bounds'}
def box(value):
 assert len(value)==2 and all(len(v)==3 for v in value)
 assert all(type(v) in [int,float] and math.isfinite(v) for row in value for v in row)
 out=[[F(v) for v in row] for row in value];assert all(out[0][k]<=out[1][k] for k in range(3));return out

def strict_planar_separation(a,b):
 a,b=box(a),box(b)
 for k in [0,2]:
  if a[1][k]<b[0][k]:return dict(axis=k,ownedBeforeForeign=True,exactPositiveGapM=str(b[0][k]-a[1][k]))
  if b[1][k]<a[0][k]:return dict(axis=k,ownedBeforeForeign=False,exactPositiveGapM=str(a[0][k]-b[1][k]))
 raise AssertionError('Whole actual POSITION bounds overlap or touch; complete finite actor context required')

def verify(owned_bounds,actors):
 assert set(owned_bounds)==OWNED_MODES and actors and len({a['uid'] for a in actors})==len(actors)
 for value in owned_bounds.values():box(value)
 result=[]
 for a in actors:
  assert a['sourceFacesOmitted']==0 and a['wholeUnusedPositionVerticesIncluded'] is True
  meshes=a['actualRenderMeshes'];assert meshes and all(m['wholePositionVerticesIncludingUnused'] is True for m in meshes)
  assert sum(m['completePositionVertices'] for m in meshes)==a['completePositionVertices']
  assert sum(m['completeIndexedFaces'] for m in meshes)==a['completeFaces']
  for field in NATIVE_MODES.values():
   boxes=[box(m[field]) for m in meshes]
   union=[[min(v[0][k] for v in boxes) for k in range(3)],[max(v[1][k] for v in boxes) for k in range(3)]]
   assert box(a[field])==union
  proofs=[]
  for owned_mode,own in owned_bounds.items():
   for foreign_mode,field in NATIVE_MODES.items():proofs.append(dict(ownedMode=owned_mode,foreignMode=foreign_mode,**strict_planar_separation(own,a[field])))
  result.append(dict(uid=a['uid'],sourceSHA256=a['sourceSHA256'],completeActualPositionRowSHA256=hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest(),completePositionVertices=a['completePositionVertices'],wholeUnusedPositionVerticesIncluded=True,completePairProofs=proofs))
 return dict(completeForeignNativeActors=len(actors),allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint=True,rows=result,noToleranceOrGeographicBufferCredit=True,cameraOrGPUFMAUniversalClaim=False,physicalAccepted=False,installationApproved=False)

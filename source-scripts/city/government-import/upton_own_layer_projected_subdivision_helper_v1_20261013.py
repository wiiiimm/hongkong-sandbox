"""Own-edge Y interpolation; projected neighbours are context, never height donors."""
from fractions import Fraction as F
import numpy as np
from upton_source_family_exact_subdivision_v1_20261013 import subdivide_source_triangle
from upton_saved_cut_node_ancestor_correspondence_draft_v1_20261013 import plane_residual

def own_layer_subdivision(triangle,raw_triangle,edge,aliases,packed_aliases,ancestor,saved_parameter,protected_target=False,protected_points=()):
 t=tuple(tuple(F(v)for v in p)for p in triangle);old=np.asarray(raw_triangle,dtype='<f8');assert old.shape==(3,3)and np.isfinite(old).all()
 assert len(aliases)==len(packed_aliases)==3
 alias=[tuple(F(v)for v in p)for p in aliases];packed=[tuple(F(v)for v in p)for p in packed_aliases]
 assert len({(p[0],p[2])for p in alias})==1,'Aliases must share one exact projected node'
 assert len({(p[0],p[2])for p in packed})==1,'Aliases must share one unchanged packed projected node'
 a,b=t[edge],t[(edge+1)%3];xz=(alias[0][0],alias[0][2]);axis=0 if a[0]!=b[0]else 2
 assert a[axis]!=b[axis],'Projected edge is collapsed'
 parameter=(xz[0 if axis==0 else 1]-a[axis])/(b[axis]-a[axis])
 assert parameter==F(saved_parameter)and 0<parameter<1,'Not the saved strict finite projected parameter'
 node=tuple(a[k]+parameter*(b[k]-a[k])for k in range(3))
 assert (node[0],node[2])==xz,'No exact projected collinearity; snapping forbidden'
 whole=tuple(tuple(F(v)for v in p)for p in ancestor)
 for point in [*t,node]:
  residual=plane_residual(point,whole);assert not residual['exactDegenerate']and residual['exactSignedPlaneResidual']==0,'Target/node must retain exact complete original ancestor plane'
 protected_node=node in {tuple(F(v)for v in p)for p in protected_points}
 proof=subdivide_source_triangle(t,node,edge,protected_target=protected_target,protected_node_incident=protected_node)
 own_packed=np.asarray([float(v)for v in node],dtype='<f4').astype('<f8');assert np.isfinite(own_packed).all()
 assert (F(float(own_packed[0])),F(float(own_packed[2])))==(packed[0][0],packed[0][2]),'Nearest Float32 XZ does not match unchanged common node; no snap/waiver'
 pieces=[]
 for piece in proof['exactPiecesXYZ']:
  value=np.asarray([[float(v)for v in p]for p in piece],dtype='<f4').astype('<f8')
  for k,point in enumerate(piece):
   if point in t:value[k]=old[t.index(point)]
   if point==node:assert value[k].tobytes()==own_packed.tobytes()
  assert np.isfinite(value).all();pieces.append(value.tolist())
 return dict(exactOwnLayerNodeXYZ=node,exactProjectedParameter=parameter,unchangedOtherLayerXYZ=alias,unchangedOtherLayerPackedXYZ=packed,ownYInterpolatedOnlyFromTargetEdge=True,neverCopiedOtherLayerY=True,exactWholeOriginalAncestorXYZ=whole,exactPartitionProof=proof,packedOwnLayerNodeXYZ=own_packed.tolist(),packedPieceTriplets=pieces,packedXZMatchesAllUnchangedAliases=True,allOriginalEndpointRawBytesRetained=True,noOtherLayerVerticesMoved=True,noPackedCoverageHeightOrAcceptanceClaim=True)

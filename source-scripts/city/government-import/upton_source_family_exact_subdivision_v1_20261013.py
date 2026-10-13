"""UNEXECUTED exact single source-triangle subdivision, not packed coverage."""
from fractions import Fraction as F
from upton_saved_uncovered_packed_ancestor_boundary_attribution_draft_v1_20261013 import segment_parameter,xz,cross
from upton_saved_cut_node_ancestor_correspondence_draft_v1_20261013 import plane_residual
def subdivide_source_triangle(triangle,node,edge,protected_target=False,protected_node_incident=False):
 t=tuple(tuple(F(v)for v in p)for p in triangle);p=tuple(F(v)for v in node)
 assert len(t)==3 and all(len(q)==3 for q in t)and len(p)==3 and type(edge)is int and 0<=edge<3
 assert not protected_target and not protected_node_incident,'Protected literal-current incidence is unavailable for subdivision'
 normal=plane_residual(p,t);assert not normal['exactDegenerate']and normal['exactSignedPlaneResidual']==0
 a,b=t[edge],t[(edge+1)%3];opposite=t[(edge+2)%3];parameter=segment_parameter(p,a,b)
 assert parameter is not None and 0<parameter<1,'Node must be a strict finite full-XYZ edge interior'
 pieces=((opposite,a,p),(opposite,p,b));area=cross(*map(xz,t));piece_areas=[cross(*map(xz,q))for q in pieces]
 assert area!=0 and all(v*area>0 for v in piece_areas)and sum(piece_areas)==area
 assert all(plane_residual(v,t)['exactSignedPlaneResidual']==0 for q in pieces for v in q)
 # All opposite-side fan points stay inside the original convex triangle;
 # the two interiors have disjoint finite edge parameters [0,t] and [t,1].
 return dict(exactOriginalXYZ=t,exactNodeXYZ=p,exactFiniteParameter=parameter,exactPiecesXYZ=pieces,exactOriginalProjectedArea2=area,exactPieceProjectedAreas2=piece_areas,completeIdealTrianglePreserved=True,idealPiecesShareOnlyFiniteOppositeToNodeBoundary=True,noPackedCoverageHeightOrAcceptanceClaim=True)

"""DRAFT exact positive projected overlap plane attribution, no consolidation."""
from fractions import Fraction as F
from exact_compute_transition_mesh_v1_20261011 import project,height
from exact_source_core_ten_metre_transition_domain_v1_20261011 import intersection
from exact_original_projection_coverage_v2_20261010 import signed_area

def classify(a,b):
 a=[tuple(F(v)for v in p)for p in a];b=[tuple(F(v)for v in p)for p in b];assert len(a)==len(b)==3 and all(len(p)==3 for p in a+b)
 pa,pb=project(a),project(b);poly=intersection(pa,pb);area=signed_area(poly);assert area>0,'No positive finite projected overlap'
 gaps=[height(a,p)-height(b,p)for p in poly];same=all(g==0 for g in gaps);duplicate=set(a)==set(b)
 assert not duplicate or same
 return dict(exactPositiveProjectedOverlapPolygon=poly,exactPositiveProjectedAreaM2=area,allExactOverlapVertexHeightDifferencesM=gaps,exactHeightDifferenceLowerM=min(gaps),exactHeightDifferenceUpperM=max(gaps),exactClosedOverlapPlanesIdentical=same,exactDuplicateUnordered3DVertices=duplicate,distinctPlaneHeightsCrossWithinOverlap=min(gaps)<0<max(gaps),qualification='Affine height difference extrema at all exact finite overlap polygon vertices. Same plane on this positive domain is exact coplanarity, not role/root/native acceptance or deletion authorization.')

"""Unexecuted representation adapter; no terrain construction or approvals."""
import math
from collections import defaultdict
def actual_complete_edge_incidents(patch,account):
 positions=patch['nativeMesh']['position'];index=patch['nativeMesh']['index'];lineage=account['completeOutputFacetLineage'];count=account['outputFacets']
 assert count==3214 and len(positions)==count*9 and index==list(range(count*3)) and len(lineage)==count
 assert all(type(v)in [int,float]and math.isfinite(v)for v in positions)
 triangles=[[positions[i*9+j*3:i*9+j*3+3]for j in range(3)]for i in range(count)];edges=defaultdict(list)
 for i,(triangle,row)in enumerate(zip(triangles,lineage)):
  assert row['outputFacet']==i and triangle==row['actualPackedPoints']
  assert row['classification']in ['original-source-core','changed-five-metre-collar','retained-captured-parent-exterior']
  assert row['packed3DCollapse']is False and row['noHeightLayerDeleted']is True
  for local,(a,b)in enumerate(zip(triangle,triangle[1:]+triangle[:1])):
   incident=dict(kind=row['classification'],outputFacet=i,localOriginalEdge=local,globalOriginalTerrainFacet=row['globalOriginalTerrainFacet'],capturedParentFacet=row['capturedParentFacet'],completeOutputFacetLineageVerbatim=row)
   edges[tuple(sorted((tuple(a),tuple(b))))].append(incident)
 result=[dict(actualPackedEdge=[list(a),list(b)],allIncidentRecords=edges[(a,b)])for a,b in sorted(edges)]
 assert sum(len(r['allIncidentRecords'])for r in result)==3*count
 assert all(r['allIncidentRecords']and r['actualPackedEdge'][0]!=r['actualPackedEdge'][1]for r in result)
 return dict(completeActualTriangles=triangles,completeActualPackedEdgeInventory=result,completeOutputFacetCount=count,completeIncidentCount=3*count,everyOriginalFacetLocalEdgeAccounted=True,incidentKindsAreSavedClassificationVerbatim=True,noApprovalOrSyntheticKind=True,noGeometryOrIndexModification=True)

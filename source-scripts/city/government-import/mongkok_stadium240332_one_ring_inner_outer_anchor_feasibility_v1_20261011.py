"""DRAFT finite one-ring apron necessary anchor constraints, no generated mesh.
Exact rational frozen source pieces only; ROOT full-read before execution.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
import json
from run import ROOT,HERE,read,save,digest,connect
from exact_original_projection_coverage_v2_20261010 import cross,signed_area
B=ROOT/'docs/astra-city/government-import'
ATOMIC=B/'government-xl-mongkok-stadium240332-atomic-domain-one-ring-inventory-v1-20261011'
OLD=B/'government-xl-mongkok-stadium240332-causal55-original-tin-domain-seam-diagnostic-v1-20261011'
DOC=B/'government-xl-mongkok-stadium240332-one-ring-inner-outer-anchor-feasibility-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def closed_height(points,p):
 points=[tuple(F(v)for v in q)for q in points];poly=[(q[0],q[2])for q in points]
 assert len(points)>=3 and signed_area(poly)>0
 if any(cross(a,b,p)<0 for a,b in zip(poly,poly[1:]+poly[:1])):return None
 a=points[0];b,c=next((points[i],points[i+1])for i in range(1,len(points)-1)if cross((a[0],a[2]),(points[i][0],points[i][2]),(points[i+1][0],points[i+1][2]))!=0)
 x=[(q[0],q[2])for q in [a,b,c]];y=[q[1]for q in [a,b,c]];den=cross(*x)
 return (cross(x[1],x[2],p)*y[0]+cross(x[2],x[0],p)*y[1]+cross(x[0],x[1],p)*y[2])/den
def boundary_nodes(boundary):
 nodes=defaultdict(list)
 for bi,r in enumerate(boundary['allBoundaryAtomicEdges']):
  assert len(r['allOriginalIncidences'])==1;e=r['allOriginalIncidences'][0]
  for k in [0,1]:nodes[tuple(F(v)for v in e['start'if k==0 else'end'])].append(dict(boundaryAtom=bi,face=e['face'],height=F(e['exactEndpointY'][k])))
 return nodes
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [strings(v)for v in x]
 return x
def main():
 assert not DOC.exists();refs=[ref(Path(__file__)),ref(HERE/'exact_original_projection_coverage_v2_20261010.py'),ref(HERE/'test_mongkok_stadium_one_ring_anchor_height_v1_20261011.py')]
 for folder in [ATOMIC,OLD]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 a=read(ATOMIC/'diagnostic.json.gz');d=read(OLD/'diagnostic.json.gz');inner=boundary_nodes(a['exactAtomicDomainAndOneRingInventory']['domainAtomicBoundary']);outer=boundary_nodes(a['exactWholeDomainAndOneRingUnionBoundary']);assert len(inner)==29 and len(outer)==137
 pieces=d['exactSourcePlanarSeamProof']['exactSourcePlanarPieces'];assert pieces and all(F(r['exactUncoveredAreaM2'])==0 for r in d['exactSourcePlanarSeamProof']['domainCoverage'])
 all_rows=[]
 for p in sorted(inner):
  source=[]
  for pi,piece in enumerate(pieces):
   height=closed_height(piece['exactPoints'],p)
   if height is not None:source.append(dict(piece=pi,domain=piece['domain'],sourceFacet=piece['source'],height=height))
  sh={r['height']for r in source};current=outer.get(p,[]);oh={r['height']for r in current}
  all_rows.append(dict(point=p,innerIncidences=inner[p],allClosedSourcePieceHeightIncidences=source,sourceSingleValued=len(sh)==1,immutableOuterIncidences=current,coincidentInnerOuterPoint=bool(current),immutableOuterSingleValued=len(oh)==1 if current else None,allExactSourceMinusOuterHeightGaps=[s-o for s in sorted(sh)for o in sorted(oh)],coincidentAnchorCompatible=bool(len(sh)==1 and len(oh)==1 and sh==oh)if current else None))
 outer_conflicts=[dict(point=p,incidences=r)for p,r in sorted(outer.items())if len({v['height']for v in r})!=1]
 shared=[r for r in all_rows if r['coincidentInnerOuterPoint']];bad=[r for r in shared if not r['coincidentAnchorCompatible']]
 save(DOC/'diagnostic.json.gz',strings(dict(uid='landsd/240332:0',sourceOnly=True,currentAcceptance=False,terrainProposalCreated=False,apronTriangulationCreated=False,sourceGeometryChanges=0,terrainGeometryChanges=0,completeOriginalFrozenCoreFaces=55,completeOneProjectedEdgeRingFaces=96,completeInnerBoundaryNodes=29,completeOuterBoundaryNodes=137,completeCoincidentInnerOuterNodes=len(shared),allInnerBoundarySourceHeightIncidences=all_rows,allOuterBoundaryHeightConflicts=outer_conflicts,allCoincidentAnchorIncompatibilities=bad,necessaryOneRingAnchorConstraintSatisfied=not bad and not outer_conflicts and all(r['sourceSingleValued']for r in all_rows),allOuterRetainedEdgeNeighboursStillRequireExactCapture=True,allSourcePieceInternalIncidencesAndFloat32StillUnqualified=True,evidenceRefs=refs,qualification='Necessary constraints for the specifically selected96-facet compute renderer apron, not a sourceTIN/ground/support/identity proof. Complete frozen authentic planar pieces are queried as closed finite polygons with exact rational heights; all piece incidences/multiple heights preserved. Where genuine inner/outer boundaries share an XY node, authentic inner-source and immutable outer-current constraints must agree exactly; conflicting values reject this narrow ring rather than snapping heights, manufacturing walls, or expanding the domain arbitrarily. Existing current internal layer cracks are not blanket repair obligations. Passing this necessary test cannot qualify a mesh; complete source-piece overlap/incidence, retained outer-edge/F32 seams and affected-actor protection remain required.')))
 assert all(ref(ROOT/e['path'])==e for e in refs)
 print(json.dumps(dict(innerNodes=29,outerNodes=137,coincidentNodes=len(shared),outerHeightConflicts=len(outer_conflicts),incompatibleCoincidentAnchors=len(bad),candidateCreated=False)))
if __name__=='__main__':main()

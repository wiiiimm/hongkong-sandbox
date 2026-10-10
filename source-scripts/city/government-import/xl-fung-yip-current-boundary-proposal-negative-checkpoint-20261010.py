"""Persist unaccepted finite-boundary proposal; never retry a wider allowance."""
import importlib.util
import json
import traceback
from pathlib import Path
import numpy as np
import shapely
from fractions import Fraction
from run import ROOT,HERE,read,save,digest
from test_fung_yip_original_distinct_party_edge_identity_20261010 import fixture
from fung_yip_original_distinct_party_edge_identity_20261010 import named_proof,UID,FOREIGN,BOUNDARY_GUARDS
from no1_garden_original_overhead_roof_edge_identity_20261010 import polygon,primary_polygon

BATCH='government-xl-fung-yip-current-boundary-proposal-negative-checkpoint-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH

def chord_squared(q,a,b):
 q,a,b=[tuple(Fraction(float(v))for v in p)for p in [q,a,b]]
 d=tuple(b[i]-a[i]for i in range(2));length=sum(v*v for v in d);assert length>0
 t=sum((q[i]-a[i])*d[i]for i in range(2))/length;t=max(Fraction(0),min(Fraction(1),t))
 return sum((q[i]-a[i]-t*d[i])**2 for i in range(2))

def main():
 assert not DOC.exists();DOC.mkdir(parents=True)
 assert BOUNDARY_GUARDS[FOREIGN[1]]==.0041,'Rejected allowance must remain unchanged'
 args=fixture();previous,row,worlds,forms,primary,relations,structures=args
 failure=None
 try:
  named_proof(*args)
 except AssertionError as e:failure=dict(error=str(e),traceback=traceback.format_exc())
 assert failure,'Do not infer acceptance from a changed diagnostic'
 source=DOC.parent/'government-xl-fung-yip-distinct-original-shared-boundary-diagnostic-v2-20261010';context=read(source/'diagnostic.json.gz');providers=context['primary'];fs={b['uid']:b for b in forms};rows=[]
 for r in context['rows']:
  u=r['foreignUID']
  for label,a,b in [('current',polygon(fs[UID]['rings']),polygon(fs[u]['rings'])),('primary',primary_polygon(providers[UID]),primary_polygon(providers[u]))]:
   shared=shapely.line_merge(a.boundary.intersection(b.boundary));pieces=list(shared.geoms)if hasattr(shared,'geoms')else[shared];face_rows=[]
   for face in r['checks'][label]['allExcessFaces']:
    coords=shapely.get_coordinates(shapely.from_geojson(face['projectedExcessGeometry']));bounds=[]
    for edge in pieces:
     if edge.geom_type!='LineString':continue
     chain=np.asarray(edge.coords);aa,bb=chain[0],chain[-1]
     delta=max(chord_squared(q,aa,bb)for q in chain);distance=max(chord_squared(q,aa,bb)for q in coords)
     bounds.append(dict(literalChain=chain.tolist(),exactMaximumChainChordDistanceSquared=str(delta),exactMaximumPortionChordDistanceSquared=str(distance),diagnosticConservativeDistanceUpperM=float(delta)**.5+float(distance)**.5))
    face_rows.append(dict(originalFace=face['face'],rawMaximumVertexNearestBoundaryDistanceM=face['maximumExcessVertexDistanceFromExactSharedBoundaryM'],completeChordBounds=bounds))
   rows.append(dict(foreignUID=u,scope=label,allOriginalExcessFaces=face_rows))
 out=dict(uids=[UID,*FOREIGN],strictActualProposalFailure=failure,unchangedSourceSpecificGuards=BOUNDARY_GUARDS,allRawForeignOverlapReasonsRetained=previous['reasons'],completeFiniteChordDiagnostic=rows,automaticApprovalReviewRejection=dict(action='Raise proposed source-specific boundary guard from4.1mm to6mm',reason='Threshold increase after failing tests conflicts with active restrictions',commandRan=False,filesChanged=False,retried=False),identityAccepted=False,physicalAccepted=False,installationApproved=False,structuralSupportAccepted=False,sourceGeometryChanges=0,qualification='All original source/current/provider actors remain intact. A5.271mm conservative bound does not certify4.1mm, and raw4.004mm vertex distances are not complete finite coverage. The proposal remains unaccepted; this is missing sufficient continuous evidence, not proof of corrupt government geometry. No wider allowance or acceptance is attempted. All other numeric, source, foreign and physical gates remain unchanged.')
 save(DOC/'diagnostic.json.gz',out)
 spec=importlib.util.spec_from_file_location('fung_negative_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 refs=[Path(__file__),HERE/'fung_yip_original_distinct_party_edge_identity_20261010.py',HERE/'test_fung_yip_original_distinct_party_edge_identity_20261010.py',HERE/'exact_original_polygon_triangle_partition_20261010.py',source/'diagnostic.json.gz',source/'result.json']
 refs += [ROOT/r['path']for r in context['evidenceRefs']]
 result=m.freeze(BATCH,'strict-existing-boundary-guard-unaccepted-proposal-v1',refs,out)
 print(json.dumps(dict(jobId=result['jobId'],identityAccepted=False,reason=failure['error'],thresholdUnchanged=True)),flush=True)

if __name__=='__main__':main()

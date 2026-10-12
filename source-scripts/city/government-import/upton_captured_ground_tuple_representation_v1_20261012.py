"""Strict saved Nx9 JSON tuple adapter only; no geometric arithmetic or credit."""
from collections import Counter
import hashlib,math,re
import numpy as np

def _flat_rows(value,count):
 assert isinstance(value,list) and len(value)==count,'Wrong complete flat-nine row count'
 for row in value:
  assert isinstance(row,list) and len(row)==9,'Expected exactly nine scalars per captured triplet'
  assert all(type(x) in (int,float) and math.isfinite(x) for x in row),'Non-number/nonfinite captured scalar'
 a=np.asarray(value,dtype='<f8');assert a.shape==(count,9) and np.isfinite(a).all()
 return a

def adapt_captured_ground(row,*,expected_faces,expected_ground_sha,expected_source_counts):
 assert type(expected_faces) is int and expected_faces>0
 assert re.fullmatch('[0-9a-f]{64}',expected_ground_sha)
 assert row['uid']=='whole-parent-domain' and row['completeClosedWholeDomainCapture'] is True
 assert row['completeAttributionMultisetMatchedActual'] is True and row['allActualFacesIncludingDegeneraciesRetained'] is True
 assert type(row['completeCurrentDrawnDomainFacets']) is int and row['completeCurrentDrawnDomainFacets']==expected_faces
 raw=_flat_rows(row['completeActualDrawnTriplets'],expected_faces)
 raw_bytes=raw.tobytes(order='C');assert hashlib.sha256(raw_bytes).hexdigest()==expected_ground_sha,'Captured order/XYZ bytes changed'
 sources=row['completeAttributedSources'];assert isinstance(sources,list) and len(sources)==len(expected_source_counts)
 attributed=[];summary=[]
 for source,(path,count) in zip(sources,expected_source_counts):
  assert source['sourcePath']==path and type(count) is int and count>0
  a=_flat_rows(source['completeSelectedDrawnTriplets'],count)
  ids=source['allSelectedMeshFaceIDs'];assert isinstance(ids,list) and len(ids)==count and all(type(i) is int and i>=0 for i in ids) and len(set(ids))==count
  attributed.extend(a[i].tobytes() for i in range(count));summary.append(dict(sourcePath=path,completeSelectedFacets=count,orderedFloat64SHA256=hashlib.sha256(a.tobytes()).hexdigest()))
 assert len(attributed)==expected_faces
 assert Counter(raw[i].tobytes() for i in range(expected_faces))==Counter(attributed),'Complete attribution binary64 tuple multiset mismatch'
 triangles=raw.reshape(expected_faces,3,3)
 assert triangles.dtype.str=='<f8' and triangles.tobytes(order='C')==raw_bytes,'Reshape changed scalar order/bytes'
 return triangles,dict(inputShape=[expected_faces,9],outputShape=[expected_faces,3,3],dtype='<f8',orderedBinary64SHA256=expected_ground_sha,completeAttributionBinary64MultisetMatched=True,sourceCounts=summary,windingMultiplicitySignedZeroAndDegeneraciesPreserved=True,representationOnly=True,geometryArithmeticPerformed=False)

"""Validate contiguous immutable, Neon-fenced paired-clearance chunk accounting.

Receipt/file hashes must be independently verified by caller before replay.
No root credit: each numerical proof binds exact source/runtime/ground streams.
"""
import hashlib
import numpy as np

def sha(a):return hashlib.sha256(np.asarray(a,float).tobytes()).hexdigest()
def verify_chunk(report,binding,original,rendered,ground,cached,first,last):
 assert report['binding']==binding and report['first']==first and report['endExclusive']==last
 assert 0<=first<last<=len(original)==len(rendered)==len(cached)
 assert len(report['faces'])==last-first and report['fullAcceptance']is False and report['installationApproved']is False
 groundsha=sha(ground)
 for i,r in zip(range(first,last),report['faces']):
  assert r['sourceFace']==i and r['priorCoarseBoundProofVerbatim']==cached[i]
  for face,old,result,flag in [(original[i],cached[i]['completeOriginal'],r['pairedExactOriginalFiniteBound'],r['completeOriginalBoundProved']),(rendered[i],cached[i]['actualRendered'],r['pairedExactActualRenderedFiniteBound'],r['completeActualRenderedBoundProved'])]:
   assert old['sourceFaceSHA256']==sha(face) and old['completeCurrentGroundSHA256']==groundsha
   assert type(old['existingOrdinaryClearanceBoundProved'])is bool and type(flag)is bool
   if old['existingOrdinaryClearanceBoundProved']:
    assert result is None and flag is True
   else:
    assert result is not None and result['sourceFaceSHA256']==sha(face) and result['completeCurrentGroundSHA256']==groundsha
    assert result['contract']=='exact-original-source-prism-paired-finite-clearance-v1'
    assert type(result['existingOrdinaryClearanceBoundProved'])is bool
    assert flag==result['existingOrdinaryClearanceBoundProved']
    assert result['rawPriorDiagnosticChanged']is False and result['sourceGeometryChanges']==0 and result['rootOrContactCredit']is False and result['fullAcceptance']is False and result['installationApproved']is False
 return report['faces']

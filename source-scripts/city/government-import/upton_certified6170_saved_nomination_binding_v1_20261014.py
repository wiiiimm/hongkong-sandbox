"""Byte/map authentication of saved certified6170 nominee; no geometry kernels."""
import numpy as np
from upton_append_current_plane_nomination_binding_v1_20261014 import digest

def validate_binding(nom,previous,patch,records,enclosures):
 old=np.asarray(previous['candidateRawPositionTriplets'],dtype='<f8');raw=np.asarray(nom['candidateRawPositionTriplets'],dtype='<f8');n=len(old)
 assert raw.ndim==3 and raw.shape[1:]==(3,3) and len(raw)>n and np.isfinite(raw).all()
 pv=nom['candidateFaceProvenance'];assert len(pv)==len(raw) and pv[:n]==previous['candidateFaceProvenance'] and raw[:n].tobytes()==old.tobytes()
 mapping=nom['completePreviousCandidateMapping'];assert len(mapping)==n
 for i,r in enumerate(mapping):assert r==dict(oldCandidateFace=i,newCandidateFaces=[i],allOldRawProvenanceBytesUnchanged=True)
 assert nom['protectedWholeCurrentTripletsUnchanged']==previous['protectedWholeCurrentTripletsUnchanged']
 for r in nom['protectedWholeCurrentTripletsUnchanged']:assert digest(raw[r['newCandidate']])==r['rawTripletSHA256']
 mesh=nom['newNativeMesh'];oldmesh=patch['nativeMesh'];pos=np.asarray(mesh['position'],dtype='<f8');idx=np.asarray(mesh['index'],dtype=np.int64)
 assert pos.ndim==1 and len(pos)%3==0 and np.isfinite(pos).all() and idx.ndim==1 and len(idx)==len(raw)*3
 assert all(type(i)is int for i in mesh['index']) and idx.min()>=0 and idx.max()<len(pos)//3
 assert np.asarray(mesh['position'][:len(oldmesh['position'])],dtype='<f8').tobytes()==np.asarray(oldmesh['position'],dtype='<f8').tobytes()
 assert mesh['index'][:len(oldmesh['index'])]==oldmesh['index'] and pos.reshape(-1,3)[idx.reshape(-1,3)].tobytes()==raw.tobytes()
 assert raw.tobytes()==raw.astype('<f4').astype('<f8').tobytes()
 recordmap={r['originalCurrentFace']:r for r in records};assigned=[]
 assert nom['wholeCurrentSafeIDs']==[6141,6159,6168] and nom['onlyCertifiedEnclosureParentID']==6170
 for row in nom['completeWholeCurrentRestorationMapping']:
  face=row['originalCurrentFace'];assert face in nom['wholeCurrentSafeIDs'];r=recordmap[face];assert row['completeWholeCurrentCounterpartVerbatim']==r
  j=row['newCandidateFace'];assert type(j)is int and n<=j<len(raw);assigned.append(j);p=pv[j]
  assert digest(raw[j])==r['wholeOriginalCurrentTripletSHA256'] and raw[j].tobytes()==np.asarray(r['wholeOriginalCurrentTriplet'],dtype='<f8').tobytes()
  assert p['candidateFace']==j and p['kind']=='capturedCurrentRing' and p['originalFace']==face and p['completeCurrentSourceAttribution']==r['completeCurrentAttribution']
  assert not p['computedFragment'] and p['savedInputByteExact'] and p['rawNominationFaceSHA256']==digest(raw[j])
 assert sorted(r['originalCurrentFace']for r in nom['completeWholeCurrentRestorationMapping'])==nom['wholeCurrentSafeIDs']
 certified={r['maskVerbatim']['mask']:r for r in enclosures['enclosures']};expected=[]
 for e in enclosures['enclosures']:
  cert=e['completeFloat32EnclosureCertificate'];assert cert['actualHeightIndexedWholeClosedMaskCoverage']['wholeClosedResidualCovered']
  for q in cert['actualPackedFacetRecords']:expected.append((e['maskVerbatim']['mask'],q['localFacet']))
 seen=[]
 for row in nom['completeCurrent6170EnclosureMapping']:
  j=row['newCandidateFace'];assert type(j)is int and n<=j<len(raw);assigned.append(j);q=row['completePackedFaceCertificate'];mask=row['mask'];assert mask==q['mask'];e=certified[mask];cert=e['completeFloat32EnclosureCertificate'];f=q['completePackingFacetCertificate'];i=f['localFacet'];seen.append((mask,i));assert f==cert['actualPackedFacetRecords'][i]
  assert np.asarray(q['actualPackedTriplet'],dtype='<f8').tobytes()==raw[j].tobytes() and q['actualPackedTriplet']==f['actualPackedTriplet']
  assert q['completeClosedResidualCertificate']==cert['actualHeightIndexedWholeClosedMaskCoverage']
  nodes=cert['completeOwnPlanePackedNodeCertificates'];assert q['exactOwnPlanePoints']==[nodes[k]['exactOwnPlanePoint']for k in [0,i+1,i+2]]
  p=pv[j];assert p['candidateFace']==j and p['kind']=='capturedCurrentRing' and p['originalFace']==6170 and p['completeCurrentSourceAttribution']==recordmap[6170]['completeCurrentAttribution']
  assert p['computedFragment'] and not p['savedInputByteExact'] and p['rawNominationFaceSHA256']==digest(raw[j]) and p['exactOriginalPlanePoints']==q['exactOwnPlanePoints']
  lineage=p['currentResidualEnclosure'];assert lineage['mask']==mask and lineage['completeFreshMaskLineage']==e['maskVerbatim'] and lineage['completePackingFacetCertificate']==f and lineage['allXZAlreadyExactFloat32OwnPlaneYCertified'] and lineage['noOtherLayerYUsed']
 assert sorted(seen)==sorted(expected) and len(set(seen))==len(seen)
 assert sorted(assigned)==list(range(n,len(raw))), 'every appended facet has exactly one saved authenticated parent/certificate'
 assert nom['completeNewCandidateFacets']==len(raw) and nom['completeNewRawSHA256']==digest(raw)
 assert nom['allOldMapsCountsPartitionProofsHistoricalOnly'] and nom['certified6170OwnPlaneInterpolationAndFloat32YPackingDeclared'] and not nom['noNewPackingOrSourcePlaneInterpolation']
 assert nom['safeThreeAppendOperationContextVerbatim']==dict(noNewPackingOrSourcePlaneInterpolation=True,onlyWholeCurrentIDs=[6141,6159,6168],operationBeforeCertified6170Fragments=True)
 return raw

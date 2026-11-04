import unittest
from copy import deepcopy
from upton_append_four_saved_current_triangles_v1_20261014 import append_saved_current,digest
from upton_certified_float32_parent_enclosure_v1_20261014 import enclose
from upton_certified6170_saved_nomination_binding_v1_20261014 import validate_binding
class Binding(unittest.TestCase):
 def setUp(self):
  raw=[[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]]];pv=[{'literal':True}];mesh={'position':[v for p in raw[0]for v in p]+[9.,8.,7.],'index':[0,1,2]};protected=[dict(newCandidate=0,rawTripletSHA256=digest(raw[0]))]
  self.previous=dict(candidateRawPositionTriplets=raw,candidateFaceProvenance=pv,protectedWholeCurrentTripletsUnchanged=protected);self.patch=dict(nativeMesh=mesh)
  tri=[[-2345.,2.,1.],[-2344.,2.,1.],[-2345.,2.,2.]]
  self.records=[dict(originalCurrentFace=i,wholeOriginalCurrentTriplet=deepcopy(tri),wholeOriginalCurrentTripletSHA256=digest(tri),completeCurrentAttribution=dict(globalCurrentFace=i,globalOrderedSavedFaceSHA256=digest(tri)))for i in [6141,6159,6168,6170]]
  self.nom=append_saved_current(raw,pv,mesh,self.records[:3],protected)
  c=enclose([['-7034/3','4/3'],['-9379/4','4/3'],['-7034/3','7/5']],tri)
  lineage=dict(mask=0,sourceFace=228,mode='synthetic');self.enclosures=dict(enclosures=[dict(maskVerbatim=lineage,completeFloat32EnclosureCertificate=c)])
  mapping=[]
  for f in c['actualPackedFacetRecords']:
   i=f['localFacet'];nodes=c['completeOwnPlanePackedNodeCertificates'];face=f['actualPackedTriplet'];q=dict(actualPackedTriplet=face,exactOwnPlanePoints=[nodes[k]['exactOwnPlanePoint']for k in [0,i+1,i+2]],mask=0,completePackingFacetCertificate=f,completeClosedResidualCertificate=c['actualHeightIndexedWholeClosedMaskCoverage']);j=len(self.nom['candidateRawPositionTriplets']);k=len(self.nom['newNativeMesh']['position'])//3
   self.nom['candidateRawPositionTriplets'].append(face);self.nom['newNativeMesh']['position'].extend(v for p in face for v in p);self.nom['newNativeMesh']['index'].extend(range(k,k+3));self.nom['candidateFaceProvenance'].append(dict(candidateFace=j,kind='capturedCurrentRing',originalFace=6170,completeCurrentSourceAttribution=self.records[-1]['completeCurrentAttribution'],computedFragment=True,savedInputByteExact=False,rawNominationFaceSHA256=digest(face),exactOriginalPlanePoints=q['exactOwnPlanePoints'],currentResidualEnclosure=dict(mask=0,completeFreshMaskLineage=lineage,completePackingFacetCertificate=f,allXZAlreadyExactFloat32OwnPlaneYCertified=True,noOtherLayerYUsed=True)));mapping.append(dict(newCandidateFace=j,mask=0,completePackedFaceCertificate=q))
  self.nom.update(completeCurrent6170EnclosureMapping=mapping,wholeCurrentSafeIDs=[6141,6159,6168],onlyCertifiedEnclosureParentID=6170,completeNewCandidateFacets=len(self.nom['candidateRawPositionTriplets']),completeNewRawSHA256=digest(self.nom['candidateRawPositionTriplets']),allOldMapsCountsPartitionProofsHistoricalOnly=True,certified6170OwnPlaneInterpolationAndFloat32YPackingDeclared=True,noNewPackingOrSourcePlaneInterpolation=False,safeThreeAppendOperationContextVerbatim=dict(noNewPackingOrSourcePlaneInterpolation=True,onlyWholeCurrentIDs=[6141,6159,6168],operationBeforeCertified6170Fragments=True))
 def call(self):return validate_binding(self.nom,self.previous,self.patch,self.records,self.enclosures)
 def test_complete_binding_and_unused_prefix(self):self.assertEqual(len(self.call()),self.nom['completeNewCandidateFacets']);self.assertEqual(self.nom['newNativeMesh']['position'][9:12],[9.,8.,7.])
 def reject(self,change):change();self.assertRaises(AssertionError,self.call)
 def test_changed_literal_rejected(self):self.reject(lambda:self.nom['candidateRawPositionTriplets'][0][0].__setitem__(1,3.))
 def test_changed_unused_vertex_rejected(self):self.reject(lambda:self.nom['newNativeMesh']['position'].__setitem__(9,10.))
 def test_missing_certificate_mapping_rejected(self):self.reject(lambda:self.nom['completeCurrent6170EnclosureMapping'].pop())
 def test_duplicate_certificate_mapping_rejected(self):self.reject(lambda:self.nom['completeCurrent6170EnclosureMapping'].append(deepcopy(self.nom['completeCurrent6170EnclosureMapping'][0])))
 def test_wrong_parent_rejected(self):self.reject(lambda:self.nom['candidateFaceProvenance'][-1].__setitem__('originalFace',6168))
 def test_false_no_interpolation_declaration_rejected(self):self.reject(lambda:self.nom.__setitem__('noNewPackingOrSourcePlaneInterpolation',True))
 def test_wrong_exact_plane_lineage_rejected(self):self.reject(lambda:self.nom['candidateFaceProvenance'][-1].__setitem__('exactOriginalPlanePoints',[['0']*3]*3))
if __name__=='__main__':unittest.main()

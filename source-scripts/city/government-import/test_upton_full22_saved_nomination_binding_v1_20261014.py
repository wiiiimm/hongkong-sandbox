import unittest
from copy import deepcopy
from upton_append_current_plane_nomination_binding_v1_20261014 import append_bound_pieces,digest
from upton_full22_saved_nomination_binding_v1_20261014 import validate_binding
class Binding(unittest.TestCase):
 def setUp(self):
  face=[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]];new=[[0.,1.,0.],[1.,1.,0.],[0.,1.,1.]]
  self.prev={'candidateRawPositionTriplets':[face],'candidateFaceProvenance':[{'old':True}],'completeOldNewIndexMapping':[{'oldCandidateFace':0,'newCandidateFaces':[0]}],'protectedWholeCurrentTripletsUnchanged':[{'newCandidate':0,'rawTripletSHA256':digest(face)}]}
  self.patch={'nativeMesh':{'position':[v for p in face for v in p]+[10.,11.,12.],'index':[0,1,2]}}
  hit={'mask':2,'polygon':[['0','1','0'],['1','1','0'],['0','1','1']]};parent={'originalCurrentFace':7,'completeCurrentAttribution':{'current':7},'wholeOriginalCurrentTripletSHA256':digest(new),'completeOwnCurrentPlaneMaskPartition':{'inside':[hit]}}
  self.parents=[parent];p={'candidateFace':1,'kind':'capturedCurrentRing','originalFace':7,'completeCurrentSourceAttribution':parent['completeCurrentAttribution'],'rawNominationFaceSHA256':digest(new),'computedFragment':True,'savedInputByteExact':False,'currentRestoration':{'noOtherLayerYUsed':True,'originalCurrentTripletSHA256':digest(new),'ownPlaneInsidePolygonOrdinal':0,'exactSavedInsidePolygonVerbatim':hit,'savedCompiledMaskOrdinal':2}}
  self.nom=append_bound_pieces([face],self.prev['candidateFaceProvenance'],self.patch['nativeMesh'],[{'packedPieceTriplet':new,'provenance':p}],self.prev['protectedWholeCurrentTripletsUnchanged'],self.prev['completeOldNewIndexMapping']);self.nom.update(completeRestoredCurrentCounterpartMapping=[{'originalCurrentFace':7,'completeCurrentCounterpartVerbatim':parent,'addedCandidateFaces':[1]}],completeNewCandidateFacets=2,completeNewRawCandidateSHA256=digest([face,new]))
 def test_complete_saved_binding(self):self.assertEqual(len(validate_binding(self.nom,self.prev,self.patch,self.parents)),2)
 def test_raw_prefix_change_rejected(self):
  self.nom['candidateRawPositionTriplets'][0][0][1]=3.
  with self.assertRaises(AssertionError):validate_binding(self.nom,self.prev,self.patch,self.parents)
 def test_unused_prefix_change_rejected(self):
  self.nom['newNativeMesh']['position'][9]=99.
  with self.assertRaises(AssertionError):validate_binding(self.nom,self.prev,self.patch,self.parents)
 def test_duplicate_current_ancestor_rejected(self):
  self.nom['completeRestoredCurrentCounterpartMapping'][0]['addedCandidateFaces']=[1,1]
  with self.assertRaises(AssertionError):validate_binding(self.nom,self.prev,self.patch,self.parents)
 def test_wrong_saved_mask_rejected(self):
  self.nom['candidateFaceProvenance'][1]['currentRestoration']['savedCompiledMaskOrdinal']=9
  with self.assertRaises(AssertionError):validate_binding(self.nom,self.prev,self.patch,self.parents)
 def test_wrong_historical_mapping_rejected(self):
  self.nom['completeOriginalCandidateMappingHistoricalOldPrefixVerbatim'][0]['newCandidateFaces']=[]
  with self.assertRaises(AssertionError):validate_binding(self.nom,self.prev,self.patch,self.parents)
if __name__=='__main__':unittest.main()

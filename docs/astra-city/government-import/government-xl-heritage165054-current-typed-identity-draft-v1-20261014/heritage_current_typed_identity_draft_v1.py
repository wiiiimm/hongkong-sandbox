"""Narrow Museum identity account only. Every physical actor/guard survives."""
from copy import deepcopy
import hashlib,json

UID='landsd/165054:0';SOURCE='1a978cdc751afa70933802e2faf090b2435250967e63b68f348ed232aeb1837f'
WORLD='258ac5cbe505d4f78f8cd334e1b6bbd3e3a56bcd6ef4e1854865f1dade75e8c7'
MODEL='B371252646701063C0';CSUID='3712526467T20050430';ASSOCIATED='landsd/104467:0';FOREIGN='landsd/57455:0'
SMALL=[835,836,839,841,842,1148,1149,1153,1154,1155]
EXTENT={'full-source-maximum-extent','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM'}
OVERLAP={'full-source-unrelated-overlap','fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2'}
POLICY='heritage-museum-original462-exterior-scope-104467-entry-association-current-identity-only-v1'
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def validate_scope(context,interpretation,*,expected_context_hash,expected_interpretation_hash):
 assert canonical(context)==expected_context_hash and canonical(interpretation)==expected_interpretation_hash
 assert context['uid']==UID and context['sourceSHA256']==SOURCE and context['worldTrianglesSHA256']==WORLD
 assert context['completeOriginalFaces']==15140 and context['componentCensusPerformed']is False
 assert all(context[k]is False for k in ['sourceRoleAccepted','identityAccepted','physicalAccepted','currentAcceptance','installationApproved'])
 assert context['sourceGeometryChanges']==context['sourcePoseChanges']==0
 groups=interpretation['viewInventoryOnlyNotComponents'];assert len(groups)==2
 assert groups[0]['farFaceIds']==SMALL and groups[0]['count']==10
 far=context['attribution']['farOriginalFaceIds'];assert len(far)==462 and far==sorted(set(far))
 assert groups[1]['count']==452 and groups[1]['farFaceIds']==[f for f in far if f not in SMALL]
 assert sorted(groups[0]['farFaceIds']+groups[1]['farFaceIds'])==far
 overlaps=context['attribution']['overlaps'];assert {r['uid']:len(r['completeAttributedOriginalFaceIds'])for r in overlaps}=={ASSOCIATED:1106,FOREIGN:2}
 assert interpretation['independent104467Association']['completeMuseumSourceNominatedFaceIds']==next(r for r in overlaps if r['uid']==ASSOCIATED)['completeAttributedOriginalFaceIds']
 assert interpretation['StarMartIndependentForeign']['sourceFacetIds']==[12346,12347]
 ordinary=sorted(set(range(15140))-set(far));assert len(ordinary)==14678 and sorted(ordinary+far)==list(range(15140))
 return far,ordinary

def compose(previous,row,world,forms,source_context,interpretation,*,expected_context_hash,expected_interpretation_hash):
 import numpy as np
 import shapely
 from shapely.geometry import Polygon
 far,ordinary=validate_scope(source_context,interpretation,expected_context_hash=expected_context_hash,expected_interpretation_hash=expected_interpretation_hash)
 tri=np.asarray(world,dtype='<f8');assert tri.shape==(15140,3,3)and np.isfinite(tri).all()
 assert hashlib.sha256(tri.tobytes()).hexdigest()==WORLD==previous['worldTrianglesSHA256']
 assert(row['uid'],row['modelId'],row['sourceSHA256'],row['triangles'])==(UID,MODEL,SOURCE,15140)
 assert previous['uid']==UID and previous['sourceSHA256']==SOURCE
 assert row['candidate']['entry']['rootTranslation']==[-834500,0,816500]
 assert row['candidate']['entry']['sha256']==SOURCE and row['native']['model']['asset']['sha256']==SOURCE
 assert len(forms)==len({b['uid']for b in forms});by_uid={b['uid']:b for b in forms}
 for uid,saved in source_context['currentThreeFormsVerbatim'].items():
  assert uid in by_uid and by_uid[uid]==saved
 own=by_uid[UID];assert own==row['source']['building']
 assert(own['objectId'],own['buildingCSUID'],own['structureType'])==(165054,CSUID,'Tower')
 assert(by_uid[ASSOCIATED]['buildingCSUID'],by_uid[ASSOCIATED]['structureType'])==('3717026380T20071207','Open-sided Structure')
 assert(by_uid[FOREIGN]['buildingCSUID'],by_uid[FOREIGN]['name'])==('3708726507T20050430','Star Mart')
 historical=source_context['historicalRoleRecordVerbatim']['variants']['direct-shared-OSM']
 assert own['rings']==historical['groupForms'][0]['rings']
 target=Polygon(own['rings'][0],own['rings'][1:]);assert target.is_valid and len(own['rings'])==2
 # Complete same-world/same-target legacy far proof is reused, not resampled.
 # It enumerated every original vertex and its strict >10 predicate. Other
 # source faces, zeros and target holes are retained in all whole-source tests.
 projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
 independent=[b for b in forms if b['uid']not in [UID,ASSOCIATED]]
 polygons=[Polygon(b['rings'][0],b['rings'][1:])for b in independent]
 assert all(p.is_valid and p.area>0 for p in polygons)
 foreign=shapely.union_all(polygons)
 residual=float(projection.difference(target).intersection(foreign).area)
 old_reasons=deepcopy(previous['reasons']);assert len(old_reasons)==len(set(old_reasons))
 reasons=list(old_reasons);replaced=[]
 cell=previous['geographicCell'];exact=previous['exactWholeCellCoverage']
 positive_base=(previous['originalOwnership']['sourceGraphVerified']and
  previous['originalOwnership']['originalRootName']==MODEL and
  exact['covered']and exact['wholeOriginalFacesAccounted']==15140 and
  cell['targetCoversWholeCell']and previous['freshCurrentIdentity']['exactObjectAndCSUID'])
 if positive_base:
  for reason in sorted(EXTENT & set(reasons)):reasons.remove(reason);replaced.append(reason)
  if 0<=residual<=1:
   for reason in sorted(OVERLAP & set(reasons)):reasons.remove(reason);replaced.append(reason)
 if not positive_base:reasons.append('heritage-positive-whole-source-cell-base-not-proved')
 if not 0<=residual<=1:reasons.append('heritage-independent-foreign-identity-area-bound')
 passed=not reasons;out=deepcopy(previous)
 out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),
  proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},
  rawCurrentIdentityRetained=deepcopy(previous),rawReasonsRetained=old_reasons,
  narrowlyAccountedReasonKeys=sorted(replaced),completeOriginalFaceCount=15140,
  namedLowEastOriginalExtentFaceIds=SMALL,namedLowPerimeterOriginalExtentFaceIds=[f for f in far if f not in SMALL],
  ordinaryExtentFaceIds=ordinary,complete15140FacePartition=True,
  unchangedCompleteFarProofBinding={'sourceContextSemanticSHA256':expected_context_hash,'sameCompleteWorldSHA256':WORLD,'sameLiteralOriginalTargetRings':True,'historicalVertexDistanceThresholdM':10,'far462Retained':True,'noNewComponentOrWholeArchitecturalPartClaim':True},
  associatedIdentityActor={'uid':ASSOCIATED,'CSUID':'3717026380T20071207','role':'registered Museum main-entrance-side roof-and-column canopy association only','completeProjectedNominationsRetained':1106,'all1106ClassifiedAsCanopy':False,'legalOwnershipClaim':False,'physicalCollisionExemption':False},
  allCurrentFormsRetained=deepcopy(forms),independentForeignUIDs=sorted(b['uid']for b in independent),
  independentForeignIdentityOverlapM2=residual,StarMartForeignPreserved=True,
  sourceInterpretationSemanticSHA256=expected_interpretation_hash,sourceEvidenceInterpretationUsedAI=True,
  sourceRoleProvidesStructuralRoot=False,terminalVisualSupportAccepted=False,
  physicalAccepted=False,structuralSupportAccepted=False,physicalSupportExemption=False,runtimeExemption=False,
  currentActorRemoval=False,installationApproved=False,currentAcceptance=False,modelGeometryChanges=0,aiGeometryModelling=False,
  qualification='Current identity only. Exact original462 low exterior/site facets and a named104467 main-entrance identity association account for only the explicit extent/unrelated-area reason families. Cached proxies remain raw under the unchanged existing whole-GeoRef-cell policy. No blanket1106canopy facet role, primary registration, property/engineering/root/support or foreign collision exemption. All15140 source primitives, StarMart and every current physical/native/runtime/browser installation obligation remain.')
 return out

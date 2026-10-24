"""Exact Man Fuk source-envelope relationship; identity only.

HA's independently named Blocks A and K corroborate the adjacent source envelopes.
It is not a legal ownership, OP, surveyed vertical, or support certification.
"""
from copy import deepcopy
import numpy as np,shapely
from run import digest
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
UID='landsd/266062:0';RELATED='landsd/75697:0'
POLICY='man-fuk-exact-original-ha-block-a-k-envelope-identity-v3'
SOURCE_SHA='22b458321ca483c53324ee152cb27c382e5ac4dfd745974f169b1c551ac8a6c1'
RELATED_SHA='6c7de45ebc146c7be0eeef151d5f217ae0c0cd72525eb74d46077bbd66c0b80d'
WORLD_SHA='2042ad56fe266775639d4d50ecf94c2ac379f44dbcc2c5dac66fb0b58b3eaebe'
RELATED_WORLD_SHA='dff958c56ed4788a95964315b6a9fc162c613c4111c8a2982f5dc43d7e6781b8'
EXACT={UID:('3644619608P20050726',1108246586,'Podium',1122336000000),RELATED:('3647219454T20050430',1108238305,'Tower',1114819200000)}
REPLACE={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def ring_poly(rings,*,primary=False):
 out=shapely.Polygon()
 for ring in rings:
  points=[(x-834500,816500-y) for x,y in ring] if primary else ring
  out=out.symmetric_difference(shapely.Polygon(points))
 assert out.is_valid and out.area>0
 return out
def named_proof(previous,row,own_triangles,related_triangles,forms,evidence):
 assert row['uid']==previous['uid']==UID and row['modelId']=='B364461960802063C0'
 assert row['sourceSHA256']==previous['sourceSHA256']==SOURCE_SHA
 t,p=np.asarray(own_triangles,float),np.asarray(related_triangles,float)
 assert t.shape==(10661,3,3) and p.shape==(2160,3,3) and np.isfinite(t).all() and np.isfinite(p).all()
 assert digest(t.astype('<f8').tobytes())==WORLD_SHA and digest(p.astype('<f8').tobytes())==RELATED_WORLD_SHA
 assert previous['originalOwnership']['sourceGraphVerified'] is True
 assert previous['geographicCell']['targetCoversWholeCell'] is True and previous['geographicCell']['originalProjectionCoversWholeCell'] is True
 assert len(forms)==len({b['uid'] for b in forms})
 own=next(b for b in forms if b['uid']==UID);related=next(b for b in forms if b['uid']==RELATED)
 assert own==row['source']['building'],'Current own form differs'
 assert own['buildingCSUID']==EXACT[UID][0] and own['buildingId']==EXACT[UID][1] and own['structureType']=='Podium'
 assert related['buildingCSUID']==EXACT[RELATED][0] and related['buildingId']==EXACT[RELATED][1] and related['structureType']=='Tower'
 records=evidence['primaryRecords'];assert len(records)==2
 primary={}
 for uid,(csuid,bid,kind,date) in EXACT.items():
  matches=[r for r in records if r['attributes']['BuildingCSUID']==csuid];assert len(matches)==1
  attrs=matches[0]['attributes'];assert attrs['Status']=='Active' and attrs['BuildingID']==bid and attrs['BuildingBlockType']==kind and attrs['DateCreate']==date and attrs['GeoRefNo']==csuid[:10]
  primary[uid]=matches[0]
 assert evidence['exactRelations']==[] and evidence['exactStructures']==[], 'No OP relationship was established'
 assert evidence['primaryPlanSHA256']=='d2dbcef160489ec1acd81e1ffad11f3d3574a3dec9bcb268311d713bc623ec74'
 assert evidence['primaryFloorPlanSHA256']=='36ff4cfe483a7aa05ab6b689f1ba817e994764e5366d055de0a4544d94fb8bc2'
 assert evidence['primaryBlockAPlanSHA256']=='a1f798e420eae3bc123a4225f3bc26cedbae471dc7ede07bdb1ea326f72c10be'
 assert evidence['primaryNamedRelationship']=={'platformName':'MAN FUK HOUSE (BLK A)','namedBlock':'A','adjacentStructure':'Man Oi House / Block K','relationship':'adjacent connected source envelopes','legalOwnershipClaim':False,'surveyPrecisionClaim':False,'supportClaim':False}
 assert evidence['rows'][0]['model']['asset']['sha256']==SOURCE_SHA and evidence['rows'][1]['model']['asset']['sha256']==RELATED_SHA
 assert evidence['rows'][0]['sourceKey']=='d5c2873925a517c3fcfee4a1bfb005df6d4e32f688ab69722ae2f61266cb8917/B364461960802063C0'
 assert evidence['rows'][1]['sourceKey']=='d5c2873925a517c3fcfee4a1bfb005df6d4e32f688ab69722ae2f61266cb8917/B364721945401063C0'
 parts=components(t)['components'];assert len(parts)==93
 main=next(c for c in parts if len(c['faceIndices'])==8676);assert not main['closedConsistentlyWound'],'Unexpected source body topology'
 contacts=exact_component_contacts(t,main['faceIndices'],p,list(range(len(p))),maximum_pairs=1000000)
 positive=[r for r in contacts['contacts'] if r['dimension']>0];assert len(positive)==12 and all(r['dimension']==1 for r in positive)
 target=ring_poly(own['rings']);pp=ring_poly(primary[UID]['geometry']['rings'],primary=True);rp=ring_poly(related['rings']);provider_related=ring_poly(primary[RELATED]['geometry']['rings'],primary=True)
 projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));raw_overlaps=[];spatial=[]
 related_projection=shapely.union_all(shapely.polygons(p[:,:,[0,2]]));related_spatial=[]
 for name,q in [('current-related',rp),('primary-related',provider_related)]:
  covered=related_projection.intersection(q).area/q.area;extent=float(shapely.distance(shapely.points(p[:,:,[0,2]].reshape(-1,2)),q).max());assert covered>=.95 and extent<=10,'Exact complete related source/current/provider bounds differ'
  related_spatial.append({'basis':name,'wholeTargetCoverage':covered,'maximumFullSourceExtentM':extent})
 others=[b for b in forms if b['uid'] not in [UID,RELATED]];foreign=shapely.union_all([ring_poly(b['rings']) for b in others]) if others else shapely.Polygon()
 for name,q in [('current',target),('primary',pp)]:
  coverage=projection.intersection(q).area/q.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),q).max());unrelated=projection.difference(q).intersection(foreign).area
  assert coverage>=.95 and extent<=10 and unrelated<=1, f'Complete {name} source/foreign bounds fail'
  spatial.append({'basis':name,'wholeTargetCoverage':coverage,'maximumFullSourceExtentM':extent,'unrelatedExcessM2':unrelated})
  raw_overlaps.append({'basis':name,'relatedActorExcessM2':projection.difference(q).intersection(rp if name=='current' else provider_related).area})
 overlap_ids=[i for i,face in enumerate(t) if shapely.Polygon(face[:,[0,2]]).intersection(projection.difference(target).intersection(rp)).area>0]
 plate=parts[63];assert len(plate['faceIndices'])==108 and digest(__import__('json').dumps(plate['faceIndices'],separators=(',',':')).encode())=='b02ce24843fff0dcdd5859340c99888a796dd07cb5181337fbb4495db1610bed'
 plate_contacts=exact_component_contacts(t,plate['faceIndices'],t,main['faceIndices'],maximum_pairs=1000000)
 assert len([q for q in plate_contacts['contacts'] if q['dimension']>0])==134,'Complete attached original plate interfaces differ'
 assert overlap_ids==evidence['completeOverlapFaceIds'] and len(overlap_ids)==23 and set(overlap_ids)<=set(main['faceIndices'])|set(plate['faceIndices'])
 assert sorted(set(overlap_ids)&set(plate['faceIndices']))==[5537,5538,5581,5582,5583]
 assert digest(__import__('json').dumps(main['faceIndices'],separators=(',',':')).encode())=='4cddcb74dcd62dab545a887dddb5bf7a76ee3daede7953af4230f7448870cd0e'
 reasons=[r for r in previous['reasons'] if r not in REPLACE];passed=not reasons
 return {**deepcopy(previous),'policy':POLICY,'passed':passed,'reasons':reasons,'rawIdentityReasonsRetained':deepcopy(previous['reasons']),'onlyNamedRelatedReasonsReplaced':sorted(set(previous['reasons'])&REPLACE),'explicitRelatedUID':RELATED,'occupationPermitRelationEstablished':False,'wholeCurrentAndPrimarySpatial':spatial,'wholeRelatedCurrentAndPrimarySpatial':related_spatial,'rawRelatedActorOverlapsRetained':raw_overlaps,'completeRawOverlapFaceIdsRetained':overlap_ids,'exactOriginalMainBodyToWholeRelatedActorContacts':contacts,'completeOriginalFaceCount':10661,'completeOriginalComponentsRetained':93,'originalMainBodyFaceCount':8676,'completeSourceAttachedPlateFaceCount':108,'exactWholeOriginalPlateToMainBodyContacts':plate_contacts,'allOtherCurrentFormsRetained':deepcopy(forms),'currentRelatedActorCollisionExemption':False,'currentRelatedActorTerrainExemption':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'proof':{'exactObjectId':passed,'exactBuildingCSUID':passed,'uniqueViewerMatch':passed,'identityAccepted':passed},'qualification':'One named unchanged Man Fuk Block A complete source envelope and one exact adjacent Man Oi Block K original. Primary active stable identifiers, the independently authored HA named estate/key plans and12 exact original interfaces corroborate this bounded adjacent-envelope interpretation. All23 excess faces are in the complete8676-face source mainbody or its complete108-face original attached plate. The five plate excess faces are explicitly retained; all93 components and raw overlap remain. No OP/legal ownership, surveyed precision, support, collision, terrain or installation claim; every other actor stays foreign.'}

"""Exact named MTR mall-station source-envelope relationship; identity only."""
from copy import deepcopy
import numpy as np,shapely
from run import digest
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
UID='landsd/315025:0';RELATED='landsd/300867:0'
POLICY='southside-exact-original-mtr-station-envelope-identity-v1'
SOURCE_SHA='85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c'
PODIUM_SHA='2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1'
WORLD_SHA='526f47c28d13afe312c79009d94bafd3c35647b01ea0f3e9608f1a251d4020b1'
PODIUM_WORLD_SHA='613de54aee262b8f80c7b2dc3df9ccc1f90f24a1f1a488d662ae1e949ded3bbe'
EXACT={UID:('3533312006P20240709',1910235866,'Podium',1720483200000),RELATED:('3536012138T20160607',1810151919,'Tower',1465257600000)}
REPLACE={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def ring_poly(rings,*,primary=False):
 out=shapely.Polygon()
 for ring in rings:
  points=[(x-834500,816500-y) for x,y in ring] if primary else ring
  out=out.symmetric_difference(shapely.Polygon(points))
 assert out.is_valid and out.area>0
 return out
def named_proof(previous,row,tower,podium,forms,evidence):
 assert row['uid']==previous['uid']==UID and row['modelId']=='B353331200602063C0'
 assert row['sourceSHA256']==previous['sourceSHA256']==SOURCE_SHA
 t,p=np.asarray(tower,float),np.asarray(podium,float)
 assert t.shape==(11699,3,3) and p.shape==(1191,3,3) and np.isfinite(t).all() and np.isfinite(p).all()
 assert digest(t.astype('<f8').tobytes())==WORLD_SHA and digest(p.astype('<f8').tobytes())==PODIUM_WORLD_SHA
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
 assert len(evidence['exactRelations'])==1
 relation=evidence['exactRelations'][0]['attributes'];assert relation['BuildingCSUID']=='3533312006P20240709' and relation['BuildingStructureID']==6095667, 'Only mall OP was found; no station OP may be invented'
 attrs=evidence['exactStructures'];assert len(attrs)==1
 a=attrs[0]['attributes'];assert a['BuildingStructureID']==6095667 and a['OPNo']=='PR8/2023/OP' and a['OPBlockType']=='Podium' and a['OPBuildingType']=='Commercial (phase 1)'
 assert evidence['primaryMTRPageSHA256']=='987ab96e553591395bbb5d1ee0171e54d90c441ad65a96b9c01101ea7c26ff67'
 assert evidence['primaryOwnerPageSHA256']=='3dc3dbed1583721f5819f0177e5b31f0ae6c236d17da36b8b26dd9fc3c777c66'
 assert evidence['primaryStationPlanSHA256']=='3a494ad5933e014be859951c18341f435b7dcba05caeb5e52fe3094972c887f3'
 assert evidence['primaryNamedRelationship']=={'mallName':'The Southside','stationName':'Wong Chuk Hang Station','relationship':'documented direct connection / unchanged intersecting source envelopes','legalOwnershipClaim':False,'commonOPClaim':False,'allFacesL1Claim':False,'surveyPrecisionClaim':False,'supportClaim':False}
 assert evidence['rows'][0]['model']['asset']['sha256']==SOURCE_SHA and evidence['rows'][1]['model']['asset']['sha256']==PODIUM_SHA
 assert evidence['rows'][0]['sourceKey']=='3823f924cd3de2e96656b14a0733dfa6df00341df154f8076db5d18d627f542d/B353331200602063C0'
 assert evidence['rows'][1]['sourceKey']=='3823f924cd3de2e96656b14a0733dfa6df00341df154f8076db5d18d627f542d/B353601213801063C1'
 parts=components(t)['components'];assert len(parts)==157
 main=next(c for c in parts if len(c['faceIndices'])==7663);assert not main['closedConsistentlyWound'],'Unexpected source body topology'
 contacts=exact_component_contacts(t,main['faceIndices'],p,list(range(len(p))),maximum_pairs=1000000)
 positive=[r for r in contacts['contacts'] if r['dimension']>0];assert len(positive)==74 and all(r['dimension']==1 for r in positive)
 ancillary=parts[121];assert len(ancillary['faceIndices'])==12
 ancillary_station=exact_component_contacts(t,ancillary['faceIndices'],p,list(range(len(p))),maximum_pairs=1000000)
 ancillary_main=exact_component_contacts(t,ancillary['faceIndices'],t,main['faceIndices'],maximum_pairs=1000000)
 assert sum(q['dimension']>0 for q in ancillary_station['contacts'])==7 and sum(q['dimension']>0 for q in ancillary_main['contacts'])==6
 target=ring_poly(own['rings']);pp=ring_poly(primary[UID]['geometry']['rings'],primary=True);rp=ring_poly(related['rings']);provider_podium=ring_poly(primary[RELATED]['geometry']['rings'],primary=True)
 projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));raw_overlaps=[];spatial=[]
 others=[b for b in forms if b['uid'] not in [UID,RELATED]];foreign=shapely.union_all([ring_poly(b['rings']) for b in others]) if others else shapely.Polygon()
 for name,q in [('current',target),('primary',pp)]:
  coverage=projection.intersection(q).area/q.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),q).max());unrelated=projection.difference(q).intersection(foreign).area
  assert coverage>=.95 and extent<=10 and unrelated<=1, f'Complete {name} source/foreign bounds fail'
  spatial.append({'basis':name,'wholeTargetCoverage':coverage,'maximumFullSourceExtentM':extent,'unrelatedExcessM2':unrelated})
  raw_overlaps.append({'basis':name,'relatedPodiumExcessM2':projection.difference(q).intersection(rp if name=='current' else provider_podium).area})
 overlap_ids=[i for i,face in enumerate(t) if shapely.Polygon(face[:,[0,2]]).intersection(projection.difference(target).intersection(rp)).area>0]
 assert overlap_ids==evidence['completeOverlapFaceIds'] and len(overlap_ids)==34 and set(overlap_ids)<=set(main['faceIndices'])|set(ancillary['faceIndices'])
 assert len(set(overlap_ids)&set(main['faceIndices']))==31 and len(set(overlap_ids)&set(ancillary['faceIndices']))==3
 reasons=[r for r in previous['reasons'] if r not in REPLACE];passed=not reasons
 return {**deepcopy(previous),'policy':POLICY,'passed':passed,'reasons':reasons,'rawIdentityReasonsRetained':deepcopy(previous['reasons']),'onlyNamedRelatedReasonsReplaced':sorted(set(previous['reasons'])&REPLACE),'explicitRelatedUID':RELATED,'occupationPermitRelationEstablished':False,'wholeCurrentAndPrimarySpatial':spatial,'rawRelatedPodiumOverlapsRetained':raw_overlaps,'completeRawOverlapFaceIdsRetained':overlap_ids,'exactOriginalMainBodyToWholeStationContacts':contacts,'exactAncillaryToStationContacts':ancillary_station,'exactAncillaryToMainbodyContacts':ancillary_main,'completeOriginalFaceCount':11699,'completeOriginalComponentsRetained':157,'originalMainBodyFaceCount':7663,'allOtherCurrentFormsRetained':deepcopy(forms),'currentPodiumCollisionExemption':False,'currentPodiumTerrainExemption':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'proof':{'exactObjectId':passed,'exactBuildingCSUID':passed,'uniqueViewerMatch':passed,'identityAccepted':passed},'qualification':'One named unchanged full Southside mall and one exact station original. MTR and owner independently document their direct connection; complete 7663-face mainbody and12-face ancillary component account for every34 raw excess face with74/7 exact station interfaces and6 ancillary-mainbody interfaces. All157 mall components and full current/primary foreign checks remain. No common OP, legal ownership, L1 attribution for each face, surveyed height, support, collision, terrain or installation claim.'}

"""Exact Tung Sing source-envelope relationship; identity only.

HA's named Block E layout corroborates the adjacent commercial structure.
It is not a legal ownership, OP, surveyed vertical, or support certification.
"""
from copy import deepcopy
import numpy as np,shapely
from run import digest
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
UID='landsd/53800:0';RELATED='landsd/126434:0'
POLICY='tung-sing-exact-original-ha-adjacent-envelope-identity-v1'
SOURCE_SHA='01b2b8a50351975e57fa036e8c358f72b93209c684a29194b5bcfeebaa2de60c'
PODIUM_SHA='368ec3bcb2b011f8db942a2e294f500043762b15851e55113c95443a48ff5f15'
WORLD_SHA='eb60a508924631729decbce9d436d21afd9f3222886b4b17c4fa44355a9969ef'
PODIUM_WORLD_SHA='4ba251e37ac08ac9ae11ab967871f420fc8c7a97d8d577d5d7148740170ded6a'
EXACT={UID:('3417311416T20050430',1103139074,'Tower',1114819200000),RELATED:('3417111358P20060312',1103119420,'Podium',1142121600000)}
REPLACE={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def ring_poly(rings,*,primary=False):
 out=shapely.Polygon()
 for ring in rings:
  points=[(x-834500,816500-y) for x,y in ring] if primary else ring
  out=out.symmetric_difference(shapely.Polygon(points))
 assert out.is_valid and out.area>0
 return out
def named_proof(previous,row,tower,podium,forms,evidence):
 assert row['uid']==previous['uid']==UID and row['modelId']=='B341731141601063C0'
 assert row['sourceSHA256']==previous['sourceSHA256']==SOURCE_SHA
 t,p=np.asarray(tower,float),np.asarray(podium,float)
 assert t.shape==(11445,3,3) and p.shape==(432,3,3) and np.isfinite(t).all() and np.isfinite(p).all()
 assert digest(t.astype('<f8').tobytes())==WORLD_SHA and digest(p.astype('<f8').tobytes())==PODIUM_WORLD_SHA
 assert previous['originalOwnership']['sourceGraphVerified'] is True
 assert previous['geographicCell']['targetCoversWholeCell'] is True and previous['geographicCell']['originalProjectionCoversWholeCell'] is True
 assert len(forms)==len({b['uid'] for b in forms})
 own=next(b for b in forms if b['uid']==UID);related=next(b for b in forms if b['uid']==RELATED)
 assert own==row['source']['building'],'Current own form differs'
 assert own['buildingCSUID']==EXACT[UID][0] and own['buildingId']==EXACT[UID][1] and own['structureType']=='Tower'
 assert related['buildingCSUID']==EXACT[RELATED][0] and related['buildingId']==EXACT[RELATED][1] and related['structureType']=='Podium'
 records=evidence['primaryRecords'];assert len(records)==2
 primary={}
 for uid,(csuid,bid,kind,date) in EXACT.items():
  matches=[r for r in records if r['attributes']['BuildingCSUID']==csuid];assert len(matches)==1
  attrs=matches[0]['attributes'];assert attrs['Status']=='Active' and attrs['BuildingID']==bid and attrs['BuildingBlockType']==kind and attrs['DateCreate']==date and attrs['GeoRefNo']==csuid[:10]
  primary[uid]=matches[0]
 assert evidence['exactRelations']==[] and evidence['exactStructures']==[], 'No OP relationship was established'
 assert evidence['primaryPlanSHA256']=='987fa89914d12b13774b85800cfb34b9e142a36ab58d7bc3ec2dec42cf9584dd'
 assert evidence['primaryFloorPlanSHA256']=='feb702526201e4a77485b65a0e9468486fdd83bb2ab37fc1ec8f460052984d17'
 assert evidence['primaryNamedRelationship']=={'towerName':'Tung Sing House','towerBlock':'E','adjacentStructure':'Commercial Complex (Carpark Under)','relationship':'adjacent connected source envelopes','legalOwnershipClaim':False,'surveyPrecisionClaim':False,'supportClaim':False}
 assert evidence['rows'][0]['model']['asset']['sha256']==SOURCE_SHA and evidence['rows'][1]['model']['asset']['sha256']==PODIUM_SHA
 assert evidence['rows'][0]['sourceKey']=='a04c53795d53db1d54dd224b5d4b2b9091855f5b8525f82753a981f88bc08438/B341731141601063C0'
 assert evidence['rows'][1]['sourceKey']=='00a245ba806076847f0f248289259b7ea9cd1676f37c4c35e4ace87dfc3f7a99/B341711135802063C0'
 parts=components(t)['components'];assert len(parts)==365
 main=next(c for c in parts if len(c['faceIndices'])==3878);assert not main['closedConsistentlyWound'],'Unexpected source body topology'
 contacts=exact_component_contacts(t,main['faceIndices'],p,list(range(len(p))),maximum_pairs=1000000)
 positive=[r for r in contacts['contacts'] if r['dimension']>0];assert len(positive)==21 and all(r['dimension']==1 for r in positive)
 target=ring_poly(own['rings']);pp=ring_poly(primary[UID]['geometry']['rings'],primary=True);rp=ring_poly(related['rings']);provider_podium=ring_poly(primary[RELATED]['geometry']['rings'],primary=True)
 projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));raw_overlaps=[];spatial=[]
 others=[b for b in forms if b['uid'] not in [UID,RELATED]];foreign=shapely.union_all([ring_poly(b['rings']) for b in others]) if others else shapely.Polygon()
 for name,q in [('current',target),('primary',pp)]:
  coverage=projection.intersection(q).area/q.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),q).max());unrelated=projection.difference(q).intersection(foreign).area
  assert coverage>=.95 and extent<=10 and unrelated<=1, f'Complete {name} source/foreign bounds fail'
  spatial.append({'basis':name,'wholeTargetCoverage':coverage,'maximumFullSourceExtentM':extent,'unrelatedExcessM2':unrelated})
  raw_overlaps.append({'basis':name,'relatedPodiumExcessM2':projection.difference(q).intersection(rp if name=='current' else provider_podium).area})
 overlap_ids=[i for i,face in enumerate(t) if shapely.Polygon(face[:,[0,2]]).intersection(projection.difference(target).intersection(rp)).area>0]
 assert overlap_ids==evidence['completeOverlapFaceIds'] and len(overlap_ids)==65 and set(overlap_ids)<=set(main['faceIndices'])
 assert digest(__import__('json').dumps(main['faceIndices'],separators=(',',':')).encode())=='3ab0bf3b9d9be64f90a8cc703b34a1c33e86d7c1aff2159d03959a3b155700dc'
 reasons=[r for r in previous['reasons'] if r not in REPLACE];passed=not reasons
 return {**deepcopy(previous),'policy':POLICY,'passed':passed,'reasons':reasons,'rawIdentityReasonsRetained':deepcopy(previous['reasons']),'onlyNamedRelatedReasonsReplaced':sorted(set(previous['reasons'])&REPLACE),'explicitRelatedUID':RELATED,'occupationPermitRelationEstablished':False,'wholeCurrentAndPrimarySpatial':spatial,'rawRelatedPodiumOverlapsRetained':raw_overlaps,'completeRawOverlapFaceIdsRetained':overlap_ids,'exactOriginalMainBodyToWholePodiumContacts':contacts,'completeOriginalFaceCount':11445,'completeOriginalComponentsRetained':365,'originalMainBodyFaceCount':3878,'allOtherCurrentFormsRetained':deepcopy(forms),'currentPodiumCollisionExemption':False,'currentPodiumTerrainExemption':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'proof':{'exactObjectId':passed,'exactBuildingCSUID':passed,'uniqueViewerMatch':passed,'identityAccepted':passed},'qualification':'One named unchanged Tung Sing Block E complete source envelope and one exact adjacent Lei Tung commercial original. Primary active stable identifiers, the independently authored HA named estate/key plans and21 exact original interfaces corroborate this bounded adjacent-envelope interpretation. All65 excess faces are in the complete3878-face source mainbody;365 complete components and raw overlap remain. No OP/legal ownership, surveyed precision, support, collision, terrain or installation claim; every other actor stays foreign.'}

"""One exact original Tower8, one proved original podium; identity only.

Distinct official OP structures remain distinct. The carved podium hole is not
filled; complete raw geometry and every current primitive remain unchanged.
"""
from copy import deepcopy
import numpy as np,shapely
from run import digest
from source_closed_components import components
from exact_original_component_contacts_20261009 import exact_component_contacts
UID='landsd/146396:0';RELATED='landsd/231756:0'
POLICY='yoho-town-eight-exact-original-primary-op-podium-identity-v1'
SOURCE_SHA='fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08'
PODIUM_SHA='d716e1d0d761cbd1268798db53d5367b630c837a72fa94ec64fddfaabcf30167'
WORLD_SHA='eb7ac3175b1a89c220c460e6d661fba1a9feb8b4d639abe8b9148d18ed73a9ae'
PODIUM_WORLD_SHA='6a159823a04a2d8a0c0d25de42bdf41449991c0884d3bc1dab94cd6a95328020'
EXACT={UID:('2179133649T20050430',1105737045,'Tower',1114819200000,5285253),RELATED:('2187833636P20050609',1105779514,'Podium',1118275200000,5285219)}
REPLACE={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def ring_poly(rings,*,primary=False):
 out=shapely.Polygon()
 for ring in rings:
  points=[(x-834500,816500-y) for x,y in ring] if primary else ring
  out=out.symmetric_difference(shapely.Polygon(points))
 assert out.is_valid and out.area>0
 return out
def named_proof(previous,row,tower,podium,forms,evidence):
 assert row['uid']==previous['uid']==UID and row['modelId']=='B217913364901063C0'
 assert row['sourceSHA256']==previous['sourceSHA256']==SOURCE_SHA
 t,p=np.asarray(tower,float),np.asarray(podium,float)
 assert t.shape==(14792,3,3) and p.shape==(7731,3,3) and np.isfinite(t).all() and np.isfinite(p).all()
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
 for uid,(csuid,bid,kind,date,structure) in EXACT.items():
  matches=[r for r in records if r['attributes']['BuildingCSUID']==csuid];assert len(matches)==1
  attrs=matches[0]['attributes'];assert attrs['Status']=='Active' and attrs['BuildingID']==bid and attrs['BuildingBlockType']==kind and attrs['DateCreate']==date and attrs['GeoRefNo']==csuid[:10]
  primary[uid]=matches[0]
  relation=[r for r in evidence['exactRelations'] if r['attributes']['BuildingCSUID']==csuid];assert len(relation)==1 and relation[0]['attributes']['BuildingStructureID']==structure
  detail=[r for r in evidence['exactStructures'] if r['attributes']['BuildingStructureID']==structure];assert len(detail)==1 and detail[0]['attributes']['OPNo']=='NT21/2004(OP)' and detail[0]['attributes']['OPBlockType']==kind
 assert len(evidence['exactRelations'])==len(evidence['exactStructures'])==2
 assert evidence['rows'][0]['model']['asset']['sha256']==SOURCE_SHA and evidence['rows'][1]['model']['asset']['sha256']==PODIUM_SHA
 assert evidence['rows'][0]['sourceKey']=='d8dd631ac65de2790f694981e8402bafd0f0f33e1a65bbce74d03db17e307d4b/B217913364901063C0'
 assert evidence['rows'][1]['sourceKey']=='cba1912c7d337d8d9734d95e031adbe5c4d0ca3e71d52f23a7913d93d48c9642/B218783363602062G0'
 parts=components(t)['components'];assert len(parts)==953
 main=next(c for c in parts if len(c['faceIndices'])==2084);assert not main['closedConsistentlyWound'],'Unexpected source body topology'
 contacts=exact_component_contacts(t,main['faceIndices'],p,list(range(len(p))),maximum_pairs=1000000)
 positive=[r for r in contacts['contacts'] if r['dimension']>0];assert len(positive)==42 and all(r['dimension']==1 for r in positive)
 target=ring_poly(own['rings']);pp=ring_poly(primary[UID]['geometry']['rings'],primary=True);rp=ring_poly(related['rings']);provider_podium=ring_poly(primary[RELATED]['geometry']['rings'],primary=True)
 projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));raw_overlaps=[];spatial=[]
 others=[b for b in forms if b['uid'] not in [UID,RELATED]];foreign=shapely.union_all([ring_poly(b['rings']) for b in others]) if others else shapely.Polygon()
 for name,q in [('current',target),('primary',pp)]:
  coverage=projection.intersection(q).area/q.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),q).max());unrelated=projection.difference(q).intersection(foreign).area
  assert coverage>=.95 and extent<=10 and unrelated<=1, f'Complete {name} source/foreign bounds fail'
  spatial.append({'basis':name,'wholeTargetCoverage':coverage,'maximumFullSourceExtentM':extent,'unrelatedExcessM2':unrelated})
  raw_overlaps.append({'basis':name,'relatedPodiumExcessM2':projection.difference(q).intersection(rp if name=='current' else provider_podium).area})
 child_base=primary[UID]['attributes']['BaseHeight'];pa=primary[RELATED]['attributes'];assert pa['BaseHeight']<=child_base<=pa['TopHeight']
 reasons=[r for r in previous['reasons'] if r not in REPLACE];passed=not reasons
 return {**deepcopy(previous),'policy':POLICY,'passed':passed,'reasons':reasons,'rawIdentityReasonsRetained':deepcopy(previous['reasons']),'onlyNamedRelatedReasonsReplaced':sorted(set(previous['reasons'])&REPLACE),'explicitRelatedUID':RELATED,'distinctOPStructuresRetained':[5285253,5285219],'wholeCurrentAndPrimarySpatial':spatial,'rawRelatedPodiumOverlapsRetained':raw_overlaps,'primaryChildOutsideCarvedPodiumM2':pp.difference(provider_podium).area,'exactOriginalMainBodyToWholePodiumContacts':contacts,'completeOriginalFaceCount':14792,'completeOriginalComponentsRetained':953,'knownOriginalUnattachedComponentsRetained':143,'allOtherCurrentFormsRetained':deepcopy(forms),'currentPodiumCollisionExemption':False,'currentPodiumTerrainExemption':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'proof':{'exactObjectId':passed,'exactBuildingCSUID':passed,'uniqueViewerMatch':passed,'identityAccepted':passed},'qualification':'One named complete original Tower8 and one exact original podium with unique active primary identities and distinct Tower/Podium structures under the exact original occupation permit;42 exact authored interfaces corroborate their physical source relationship. Carved hole and full raw overlap retained. Every other actor remains foreign including same-name/permit actors. No absent-source support, closed-solid, mounting, current primitive collision/terrain/runtime exemption, suppression, or installation credit.'}

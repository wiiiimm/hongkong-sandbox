"""One named hospital source relationship; identity only, no podium import credit.

Independent official site context and exact original interfaces distinguish
these two hospital actors. Every other actor remains foreign. The incomplete
podium source is corroborating evidence only; it is not certified for import.
"""
from copy import deepcopy
import numpy as np,shapely
from run import digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_ownership import document,graph_reasons
from exact_mesh_components import face_components
from exact_original_component_contacts_20261009 import exact_component_contacts
UID='landsd/191896:0';RELATED='landsd/280350:0'
POLICY='tuen-mun-special-exact-original-owner-site-relationship-v1'
SPEC={UID:('B156632989901063C0',18759,'0e40084c921eda267370e464ce055098fab70c4aa2f29013f94918f78e17f23b','f557ffaa79efba86ee5d053b206da3aa3168223f5d594a8c1d85aa336de24181','1566329899T20080513',1108522327,'Tower',1210636800000),RELATED:('B156122977802063C0',13121,'851ae2f02fe2499f10c8514b08be8bb9e2e73afa243488c5dc0e0c6ea7acb261','d45756433a78633dbb05f32094d9353fb8f5f23921ccefe5704ebbb6bd4c02a3','1561229778P20210726',1108531684,'Podium',1627257600000)}
OWNER={'official-site-plan-20150518.pdf':'2e116361db0aedfd829811f6d4978b5b9f6d4196957f23c8318012e3fa8d3fe7','official-hospital-about.html':'781a5a371ff67695977a8d44061834ed1268aa743b629363907522e66ebb3f52'}
REPLACE={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def polygon(rings,primary=False):
 p=shapely.Polygon()
 for ring in rings:p=p.symmetric_difference(shapely.Polygon([(x-834500,816500-z) for x,z in ring] if primary else ring))
 assert p.is_valid and p.area>0
 return p
def verify(previous,row,source_bytes,forms,primary_records,owner_bytes):
 assert previous['uid']==row['uid']==UID and previous['sourceSHA256']==row['sourceSHA256']==SPEC[UID][2]
 assert row['modelId']==SPEC[UID][0]
 assert previous['originalOwnership']['sourceGraphVerified'] is True
 assert previous['geographicCell']['targetCoversWholeCell'] is True and previous['geographicCell']['originalProjectionCoversWholeCell'] is True
 assert set(source_bytes)==set(SPEC) and set(owner_bytes)==set(OWNER)
 assert {k:digest(v) for k,v in owner_bytes.items()}==OWNER,'Independent official owner sources differ'
 assert len(forms)==len({f['uid'] for f in forms}) and len(primary_records)==2
 meshes={};providers={};current={}
 for uid,(model,faces,sha,world,csuid,bid,kind,date) in SPEC.items():
  raw=source_bytes[uid];assert digest(raw)==sha and not graph_reasons(document(raw),model,faces)
  t=decode_original_world_triangles(raw);assert t.shape==(faces,3,3) and digest(t.astype('<f8').tobytes())==world
  meshes[uid]=t
  current[uid]=next(f for f in forms if f['uid']==uid)
  assert (current[uid]['buildingCSUID'],current[uid]['buildingId'],current[uid]['structureType'])==(csuid,bid,kind)
  matches=[f for f in primary_records if f['attributes']['BuildingCSUID']==csuid];assert len(matches)==1
  f=matches[0];a=f['attributes'];assert (a['Status'],a['BuildingID'],a['BuildingBlockType'],a['DateCreate'],a['GeoRefNo'])==('Active',bid,kind,date,csuid[:10])
  providers[uid]=f
 assert current[UID]==row['source']['building']
 assert providers[UID]['attributes']['BuildingNameEN']=='Tuen Mun Hospital Special Block'
 assert current[RELATED]['name']=='Main Block' and current[RELATED]['kind']=='hospital'
 t,p=meshes[UID],meshes[RELATED];proj=shapely.union_all(shapely.polygons(t[:,:,[0,2]]))
 target=polygon(current[UID]['rings']);provider=polygon(providers[UID]['geometry']['rings'],True);related=polygon(current[RELATED]['rings'])
 foreign=shapely.union_all([polygon(f['rings']) for f in forms if f['uid'] not in SPEC])
 bounds=[]
 for basis,q in [('current',target),('primary',provider)]:
  coverage=proj.intersection(q).area/q.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),q).max());other=proj.difference(q).intersection(foreign).area
  assert coverage>=.95 and extent<=10 and other<=1,'Ordinary whole source/current/provider/other-actor bounds fail'
  bounds.append(dict(basis=basis,coverage=coverage,maximumExtentM=extent,otherForeignExcessM2=other,namedRelatedExcessM2=proj.difference(q).intersection(related).area))
 raw_excess=proj.difference(provider).intersection(related)
 ids=[i for i,f in enumerate(t) if shapely.Polygon(f[:,[0,2]]).area and shapely.Polygon(f[:,[0,2]]).intersection(raw_excess).area>0]
 assert len(ids)==174 and abs(raw_excess.area-11.625801872489985)<1e-9
 contacts=exact_component_contacts(t,ids,p,list(range(len(p))),maximum_pairs=1000000)
 positive=[r for r in contacts['contacts'] if r['dimension']>0];assert len(positive)==80
 parts=face_components(t);assert len(parts)==130 and sum(map(len,parts))==18759
 pa=providers[RELATED]['attributes'];assert pa['BaseHeight']<=providers[UID]['attributes']['BaseHeight']<=pa['TopHeight']
 podium_projection=shapely.union_all(shapely.polygons(p[:,:,[0,2]]));podium_primary=polygon(providers[RELATED]['geometry']['rings'],True)
 podium_coverage=podium_projection.intersection(podium_primary).area/podium_primary.area
 reasons=[r for r in previous['reasons'] if r not in REPLACE];passed=not reasons
 return {**deepcopy(previous),'policy':POLICY,'passed':passed,'reasons':reasons,'rawIdentityReasonsRetained':deepcopy(previous['reasons']),'onlyNamedRelatedReasonsReplaced':sorted(set(previous['reasons'])&REPLACE),'explicitRelatedUID':RELATED,'wholeCurrentAndPrimarySpatial':bounds,'exactCompleteOriginalExcessInterfaces':contacts,'completeOriginalTowerFacesRetained':18759,'completeOriginalTowerComponentsRetained':130,'completeOriginalPodiumFacesRetained':13121,'allCurrentFormsRetained':deepcopy(forms),'independentOfficialOwnerSourceHashes':OWNER,'supportingPodiumPrimaryCoverage':podium_coverage,'supportingPodiumIdentityAccepted':False,'supportingPodiumInstallationApproved':False,'wholePodiumContainmentClaimed':False,'commonOccupationPermitClaimed':False,'currentPodiumCollisionExemption':False,'currentPodiumTerrainExemption':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'proof':{'exactObjectId':passed,'exactBuildingCSUID':passed,'uniqueViewerMatch':passed,'identityAccepted':passed},'qualification':'One exact original Special Block and one exact original Main Block podium, corroborated by reviewed first-party hospital introduction/site-boundary plan and80recomputed positive-dimensional authored source interfaces. All174excess faces retained. Not-to-scale owner plan supplies no coordinates or support. The podium source covers only75percent of its primary footprint and receives no independent import/quality/support certification. Every other actor remains foreign; current physics, runtime, browser and publication remain independent.'}

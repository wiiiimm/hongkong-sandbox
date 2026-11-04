"""Source-bound podium footprint attribution; no physical or publication approval."""
from copy import deepcopy
import numpy as np,shapely
from shapely.geometry import Polygon
from run import digest
P='landsd/233002:0';C='landsd/256434:0'
PINS={P:('26d2392b7510242922721dfbaef49f1fb0db447fa017317f7b4a2de37beabd2e','B400991605802063C0',1557),C:('7904c4759be630f393ba5aa51771e936327aa4adb45317f3672a7eafdb5502dd','B400971609701063C0',849)}
RAW=['fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage']
POLICY='orchards-original-podium-community-footprint-identity-v1'
def interpret(rows,proofs,meshes,forms,providers):
 assert set(rows)==set(proofs)==set(meshes)==set(providers)=={P,C}
 projections={};targets={};vertices=[]
 for uid,(sha,model,count)in PINS.items():
  r=rows[uid];proof=proofs[uid];b=r['source']['building'];tri=np.asarray(meshes[uid],dtype='<f8')
  assert r['uid']==b['uid']==proof['uid']==uid and r['sourceSHA256']==proof['sourceSHA256']==sha
  assert r['modelId']==model and tri.shape==(count,3,3)and np.isfinite(tri).all()
  assert digest(tri.tobytes())==proof['worldTrianglesSHA256']
  assert proof['originalOwnership']['sourceGraphVerified']and proof['originalOwnership']['originalRootName']==model
  assert proof['exactWholeCellCoverage']['covered']and proof['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==count
  assert proof['geographicCell']['targetCoversWholeCell']and proof['geographicCell']['originalProjectionCoversWholeCell']
  assert forms[uid]==b
  provider=providers[uid];assert not provider.get('exceededTransferLimit')and len(provider['features'])==1
  assert provider['spatialReference'].get('latestWkid',provider['spatialReference'].get('wkid'))==2326
  f=provider['features'][0];a=f['attributes'];assert a['BuildingCSUID']==b['buildingCSUID']and a['BuildingID']==b['buildingId']and a['BuildingBlockType']==b['structureType']and a['Status']=='Active'
  rings=[[(x-834500,816500-y)for x,y in ring]for ring in f['geometry']['rings']];official=Polygon(rings[0],rings[1:]);target=Polygon(b['rings'][0],b['rings'][1:]);assert official.is_valid and target.is_valid and official.hausdorff_distance(target)<.002
  projections[uid]=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));targets[uid]=target;vertices.append(tri[:,:,[0,2]].reshape(-1,2))
 assert proofs[P]['reasons']==RAW and not proofs[P]['passed'];assert proofs[C]['passed']and not proofs[C]['reasons']
 assert forms[P]['structureType']=='Podium'and forms[C]['structureType']=='Tower'
 assert forms[C]['parent']=='way/296724534'and forms[C]['parent']in forms[P]['osmRefs']and forms[P]['parent']=='way/100512374'
 assert forms[P]['base']==forms[C]['base']==18.3 and forms[C]['topHeightHKPD']==29 and forms[P]['topHeightHKPD']==45.3
 target=shapely.union_all(list(targets.values()));source=shapely.union_all(list(projections.values()));remaining=targets[P].difference(targets[C]);assert remaining.area>0
 parents={forms[P]['parent'],forms[C]['parent']};others=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:])for u,b in forms.items()if u not in PINS and b.get('parent')not in parents])
 measures=dict(combinedCoverage=source.intersection(target).area/target.area,podiumCoverageExcludingVerifiedCommunity=projections[P].intersection(remaining).area/remaining.area,maximumExtentM=float(shapely.distance(shapely.points(np.concatenate(vertices)),target).max()),unrelatedExcessM2=source.difference(target).intersection(others).area)
 assert measures['combinedCoverage']>=.95 and measures['podiumCoverageExcludingVerifiedCommunity']>=.95 and measures['maximumExtentM']<=10 and measures['unrelatedExcessM2']<=1
 out=deepcopy(proofs[P]);out.update(policy=POLICY,rawPodiumIdentity=deepcopy(proofs[P]),requiredOriginalCommunityIdentity=deepcopy(proofs[C]),rawCoverageReasonsRetained=RAW,measures=measures,passed=True,reasons=[],proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},requiredCompanionUid=C,requiredCompanionSHA256=PINS[C][0],physicalAccepted=False,installationApproved=False,sourceInterpretationUsedAI=True,qualification='Identity only, conditional on the exact original community component being present. Separate official component occupies the northern portion included in the official podium footprint. Both unique original roots/whole GeoRef cells and primary current records remain mandatory. Independently measured remaining podium and combined coverage retain the 95 percent limit; extent and unrelated overlap limits remain unchanged. Different map parents and raw singleton failures retained. No support, source crossing, terrain, collision or publication approval.')
 return out

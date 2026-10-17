"""Three exact No1 Garden authored horizontal roof-edge faces over a distinct body.

Identity interpretation only: complete current/provider/source streams are caller
bound. The foreign structure remains an independent collision/terrain actor.
"""
from copy import deepcopy
from datetime import datetime,timezone
import numpy as np,shapely
from run import digest
from source_closed_components import components
UID='landsd/304714:0';FOREIGN='landsd/213929:0'
SOURCE_SHA='f06178309a08955ef93e0d5424e864075632670d3bb2902d3c7d9aaee933beca'
FOREIGN_SHA='ff493e5dd805466dc1021dce603c4ea7fa77d15fdc6983ffd905301a2d3df83b'
WORLD_SHA='b40f2ddbc25d38435ff7c7a2c3eee2a79d331a5bbadd1ce7bd62b634e859395c'
FOREIGN_WORLD_SHA='b73014ff749fa852006f122bf11b368fa23bdfce73f711a29979f6afefe216f2'
EXPECTED={UID:('3396115261P20060312',1103118328,'Podium'),FOREIGN:('3395315297P20060312',1109348222,'Podium')}
ROLE_FACES={642,643,644}
RAW_REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
POLICY='exact-no1-garden-source-authored-overhead-roof-edge-identity-v1'
def polygon(rings):
 p=shapely.GeometryCollection()
 for r in rings:p=p.symmetric_difference(shapely.Polygon(r))
 assert p.is_valid and p.area>0
 return p

def primary_polygon(f):return polygon([[(x-834500,816500-y) for x,y in r] for r in f['geometry']['rings']])

def named_proof(previous,row,own,foreign,current_forms,primary):
 assert row['uid']==UID and row['modelId']=='B339611526102063C0' and row['sourceSHA256']==SOURCE_SHA
 assert previous['uid']==UID and previous['sourceSHA256']==SOURCE_SHA and previous['originalOwnership']['sourceGraphVerified']
 own=np.asarray(own,float);foreign=np.asarray(foreign,float)
 assert own.shape==(821,3,3) and foreign.shape==(546,3,3) and np.isfinite(own).all() and np.isfinite(foreign).all()
 assert digest(own.astype('<f8').tobytes())==WORLD_SHA and digest(foreign.astype('<f8').tobytes())==FOREIGN_WORLD_SHA,'Complete original world/pose differs'
 forms={b['uid']:b for b in current_forms};assert len(forms)==len(current_forms) and UID in forms and FOREIGN in forms
 assert forms[UID]==row['source']['building'] and forms[UID]['name']=='NO.1 GARDEN TERRACE'
 assert len(primary)==2;providers={}
 for uid,(csuid,bid,kind) in EXPECTED.items():
  b=forms[uid];assert (b['buildingCSUID'],b['buildingId'],b['structureType'])==(csuid,bid,kind)
  matches=[f for f in primary if f['attributes']['BuildingCSUID']==csuid];assert len(matches)==1;p=matches[0];v=p['attributes'];providers[uid]=p
  assert (v['Status'],v['BuildingID'],v['BuildingBlockType'],str(v['GeoRefNo']))==('Active',bid,kind,csuid[:10])
  assert datetime.fromtimestamp(v['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:]
  assert v['BaseHeight']==b['baseHeightHKPD'] and v['TopHeight']==b['topHeightHKPD']
 parts=components(own)['components'];assert len(parts)==3;main=parts[0]['faceIndices'];assert len(main)==779 and ROLE_FACES<=set(main)
 role=own[sorted(ROLE_FACES)];assert (role[:,:,1]==133.25698852539062).all()
 assert (np.cross(role[:,1]-role[:,0],role[:,2]-role[:,0])[:,1]>0).all(),'Every named face must remain an original positive-area upward horizontal roof surface'
 low=float(role[:,:,1].min());assert low>foreign[:,:,1].max() and low>forms[FOREIGN]['topHeightHKPD'] and low>providers[FOREIGN]['attributes']['TopHeight']
 projection=shapely.union_all(shapely.polygons(own[:,:,[0,2]]));others=[b for b in current_forms if b['uid'] not in {UID,FOREIGN}];other_shapes=shapely.union_all([polygon(b['rings']) for b in others]);reasons=[r for r in previous['reasons'] if r not in RAW_REASONS];checks={}
 for label,target,foreign_target in [('current',polygon(forms[UID]['rings']),polygon(forms[FOREIGN]['rings'])),('primary',primary_polygon(providers[UID]),primary_polygon(providers[FOREIGN]))]:
  extra=projection.difference(target);overlap=extra.intersection(foreign_target);ids={i for i,t in enumerate(own) if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area>0};assert ids and ids<=ROLE_FACES,'Every actual foreign projected excess face must be one of the three exact roof edges'
  m={'targetCoverage':projection.intersection(target).area/target.area,'maximumSourceExtentM':float(shapely.distance(shapely.points(own[:,:,[0,2]].reshape(-1,2)),target).max()),'allOtherForeignExcessM2':extra.intersection(other_shapes).area,'rawNamedForeignRoofEdgeExcessM2':overlap.area,'completeNamedForeignExcessFaceIds':sorted(ids)};checks[label]=m
  if not(.95<=m['targetCoverage']<=1.000000001 and m['maximumSourceExtentM']<=10 and m['allOtherForeignExcessM2']<=1):reasons.append('complete-source-'+label+'-spatial-bound')
 raw=sorted(set(previous['reasons'])&RAW_REASONS);assert raw
 out=deepcopy(previous);passed=not reasons;out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawUnrelatedOverlapReasonsRetained=raw,explicitOverheadForeignUID=FOREIGN,completeOriginalMainBodyFaceIds=main,allRawNamedOverlapFaceIds=sorted(ROLE_FACES),completeOriginalWorldSHA256=WORLD_SHA,completeForeignOriginalWorldSHA256=FOREIGN_WORLD_SHA,roofEdgeMinimumYHKPD=low,completeForeignOriginalMaximumYHKPD=float(foreign[:,:,1].max()),independentFullSourceSpatialChecks=checks,completeCurrentForeignActorsRetained=current_forms,allOtherActorsStillForeignUIDs=sorted(b['uid'] for b in others),noCommonOwnershipOrSupportClaim=True,foreignRemoval=False,foreignCollisionExemption=False,foreignTerrainExemption=False,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Only three byte-bound source-authored positive-area upward horizontal roof-edge faces are above the complete distinct original/current/primary Hollywood Heights body. Whole779-face own body is NOT claimed overhead or noncolliding. Distinct OP/property structures and all actual physical actors remain independent; no support/collision/terrain exemption.')
 return out

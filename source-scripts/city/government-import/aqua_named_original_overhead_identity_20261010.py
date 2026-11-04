"""One exact Aqua Marine authored overhead plate; no foreign ownership credit.

The caller must independently bind complete current forms, primary requests,
native original streams/root and raw full-cell proof. This kernel grants only
the named two-dimensional source-envelope identity interpretation.
"""
from copy import deepcopy
from datetime import datetime,timezone
import numpy as np,shapely
from run import digest
from source_closed_components import components
UID='landsd/193086:0';FOREIGN='landsd/138449:0'
SOURCE_SHA='d24d090ed2711744be1b4cd326da724a2a17baa5368720c8ac12e7bd42823b91'
FOREIGN_SHA='7afefdfbd5ca92f7019bb2c944b4459beea827d0637e06d1bc755ab85c7d3474'
WORLD_SHA='5ea5b37944d5c941be6589fa469c8c5a671fd9e2e86ebc2e8c2092d451dfbc10'
FOREIGN_WORLD_SHA='4b6d0cc82c2a83715effc2487fba1fcf7d16323dcfe4688104d579a4a77ba6e8'
EXPECTED={UID:('3333921515P20060311',1108245634,'Podium'),FOREIGN:('3336221561T20060914',1108225422,'Tower')}
ROLE_FACES={4767,4768,4769,4770,4771,6282,6283,6284,7353,7354,7355,7389,7390,7393,7394,7395,13612,13613,13614,13615,13616,13617}
RAW_REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
POLICY='exact-aqua-marine-source-authored-overhead-plate-identity-v1'
def polygon(rings):
 result=shapely.GeometryCollection()
 for ring in rings:result=result.symmetric_difference(shapely.Polygon(ring))
 return result
def primary_polygon(feature):return polygon([[(x-834500,816500-y) for x,y in r] for r in feature['geometry']['rings']])
def named_proof(previous,row,own,foreign,current_forms,primary):
 assert row['uid']==UID and row['modelId']=='B333392151502063C0' and row['sourceSHA256']==SOURCE_SHA
 assert previous['uid']==UID and previous['sourceSHA256']==SOURCE_SHA and previous['originalOwnership']['sourceGraphVerified']
 own=np.asarray(own,float);foreign=np.asarray(foreign,float)
 assert own.shape==(22735,3,3) and foreign.shape==(116,3,3) and np.isfinite(own).all() and np.isfinite(foreign).all()
 assert digest(own.astype('<f8').tobytes())==WORLD_SHA and digest(foreign.astype('<f8').tobytes())==FOREIGN_WORLD_SHA,'Complete original world or pose differs'
 forms={b['uid']:b for b in current_forms};assert len(forms)==len(current_forms) and UID in forms and FOREIGN in forms
 assert forms[UID]==row['source']['building'] and forms[UID]['name']=='AquaMarine'
 assert len(primary)==2;providers={}
 for uid,(csuid,bid,kind) in EXPECTED.items():
  b=forms[uid];assert (b['buildingCSUID'],b['buildingId'],b['structureType'])==(csuid,bid,kind)
  matches=[p for p in primary if p['attributes']['BuildingCSUID']==csuid];assert len(matches)==1;p=matches[0];a=p['attributes'];providers[uid]=p
  assert (a['Status'],a['BuildingID'],a['BuildingBlockType'],str(a['GeoRefNo']))==('Active',bid,kind,csuid[:10])
  assert datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:]
  assert a['BaseHeight']==b['baseHeightHKPD'] and a['TopHeight']==b['topHeightHKPD'],'Current/provider vertical metadata differs'
 parts=components(own)['components'];assert len(parts)==46;plate=parts[12];ids=plate['faceIndices'];assert len(ids)==656 and ROLE_FACES<=set(ids)
 low=float(own[ids,:,1].min());assert low>foreign[:,:,1].max() and low>forms[FOREIGN]['topHeightHKPD'] and low>providers[FOREIGN]['attributes']['TopHeight'],'Whole source-owned plate must remain above the complete separate body'
 source_projection=shapely.union_all(shapely.polygons(own[:,:,[0,2]]));foreign_shape=polygon(forms[FOREIGN]['rings']);all_other=[b for b in current_forms if b['uid'] not in {UID,FOREIGN}];other_shape=shapely.union_all([polygon(b['rings']) for b in all_other]);reasons=[r for r in previous['reasons'] if r not in RAW_REASONS];checks={}
 for label,target in [('current',polygon(forms[UID]['rings'])),('primary',primary_polygon(providers[UID]))]:
  extra=source_projection.difference(target);overlap=extra.intersection(foreign_shape if label=='current' else primary_polygon(providers[FOREIGN]));face_ids={i for i,t in enumerate(own) if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area>0}
  assert face_ids and face_ids<=ROLE_FACES,'Every exact foreign projected-overlap face must be an identified original overhead face'
  metrics={'targetCoverage':source_projection.intersection(target).area/target.area,'maximumSourceExtentM':float(shapely.distance(shapely.points(own[:,:,[0,2]].reshape(-1,2)),target).max()),'allOtherForeignExcessM2':extra.intersection(other_shape).area,'rawNamedForeignOverheadExcessM2':overlap.area,'completeNamedForeignExcessFaceIds':sorted(face_ids)};checks[label]=metrics
  if not(.95<=metrics['targetCoverage']<=1.000000001 and metrics['maximumSourceExtentM']<=10 and metrics['allOtherForeignExcessM2']<=1):reasons.append('complete-source-'+label+'-spatial-bound')
 raw=sorted(set(previous['reasons'])&RAW_REASONS);assert raw,'Named raw projected overlap must be retained';out=deepcopy(previous);passed=not reasons
 out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawUnrelatedOverlapReasonsRetained=raw,explicitOverheadForeignUID=FOREIGN,completeOriginalOverheadComponent=12,completeOriginalOverheadFaceIds=ids,allRawNamedOverlapFaceIds=sorted(ROLE_FACES),completeOriginalWorldSHA256=WORLD_SHA,completeForeignOriginalWorldSHA256=FOREIGN_WORLD_SHA,wholePlateMinimumYHKPD=low,completeForeignOriginalMaximumYHKPD=float(foreign[:,:,1].max()),independentFullSourceSpatialChecks=checks,completeCurrentForeignActorsRetained=current_forms,allOtherActorsStillForeignUIDs=sorted(b['uid'] for b in all_other),noCommonOwnershipOrSupportClaim=True,foreignRemoval=False,foreignCollisionExemption=False,foreignTerrainExemption=False,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact unchanged Aqua Marine root owns the complete656-face shallow overhead plate. Every named foreign projected excess face is one of22 source-authored overhead faces, strictly above the independently identified whole116-face original/current/primary body. All raw projected overlap remains; every other actor remains foreign. No legal ownership, surveyed-height, architectural function, grounding, collision, terrain or physical exemption is granted.')
 return out

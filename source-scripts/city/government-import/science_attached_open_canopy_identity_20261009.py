"""One named government museum/attached open-sided structure identity relation.

Retains all raw overlap and every current actor. No floorplan/property boundary,
true canopy elevation, collision, physical or runtime exemption is inferred.
"""
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as original_verify
UID='landsd/80343:0';RELATED='landsd/83471:0'
EXPECTED={UID:('3634918016T20050430',1108243181,'Tower'),RELATED:('3631518015T20071227',1108243261,'Open-sided Structure')}
DOC=ROOT/'docs/astra-city/government-import/government-xl-science-museum-open-structure-primary-20261009'
JOB='3fbf8b38597353c543a30dcfa01a08d4e6b2e1a7e56e2dc94015176d030c4e81'
POLICY='one-exact-government-science-museum-attached-open-sided-canopy-identity-v1'
SOURCE_SHA='df4eeb38ea777cf3016a497db81c0c2a36ea880da7a3cb5b27a426e8768dbe28'
SOURCE_MODEL='B363491801601063C0'
REASONS={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','full-source-unrelated-overlap'}
def polygon(rings):return shapely.symmetric_difference_all([shapely.Polygon(r) for r in rings])
def primary_shape(provider):
 assert not provider.get('error') and not provider.get('exceededTransferLimit') and len(provider.get('features',[]))==1
 assert provider['spatialReference'].get('latestWkid',provider['spatialReference'].get('wkid'))==2326
 return polygon([[(x-834500,816500-y) for x,y in r] for r in provider['features'][0]['geometry']['rings']])
def primary_shared_checks(shapes,forms):
 own=polygon(forms[UID]['rings']);related=polygon(forms[RELATED]['rings'])
 expected=shapely.LineString([[1822.331,-1515.515],[1815.348,-1509.215],[1815.308,-1509.179]])
 shared=own.boundary.intersection(related.boundary)
 return shared.equals(expected) and shapes[UID].boundary.intersection(shapes[RELATED].boundary).length==9.458928413186491
def named_proof(previous,row,triangles,current_forms,providers):
 assert row['uid']==UID and previous['uid']==UID and previous['sourceSHA256']==row['sourceSHA256'] and previous['originalOwnership']['sourceGraphVerified']
 assert row['sourceSHA256']==SOURCE_SHA and row['modelId']==SOURCE_MODEL,'Named unchanged original source version required'
 tri=np.asarray(triangles,float);assert tri.shape==(row['triangles'],3,3) and np.isfinite(tri).all();assert digest(tri.astype('<f8').tobytes())==previous['worldTrianglesSHA256'],'Exact original world binding differs'
 forms={b['uid']:b for b in current_forms};assert len(forms)==len(current_forms) and UID in forms and RELATED in forms
 shapes={};attrs={}
 for uid in [UID,RELATED]:
  csuid,bid,kind=EXPECTED[uid];b=forms[uid];assert (b['buildingCSUID'],b['buildingId'],b['structureType'])==(csuid,bid,kind)
  p=providers[uid];shapes[uid]=primary_shape(p);a=p['features'][0]['attributes'];attrs[uid]=a
  assert (a['Status'],a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'],str(a['GeoRefNo']))==('Active',csuid,bid,kind,csuid[:10])
  assert isinstance(a.get('DateCreate'),(int,float)) and datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')==csuid[11:],'Primary creation lineage differs'
  assert a['BuildingNameTC']=='香港科學館' and a['BuildingNameEN'].casefold()=='hong kong science museum'
 assert forms[UID]==row['source']['building']
 assert primary_shared_checks(shapes,forms),'Exact named current and primary attached-boundary geometry differs'
 own=polygon(forms[UID]['rings']);related=polygon(forms[RELATED]['rings']);primary_shared=shapes[UID].boundary.intersection(shapes[RELATED].boundary);viewer_shared=own.boundary.intersection(related.boundary)
 assert shapes[UID].intersection(shapes[RELATED]).area==0 and own.intersection(related).area==0,'Primary/current interiors differ or overlap'
 assert primary_shared.length>9 and viewer_shared.length>9,'Specific actual attached boundary absent'
 # Exact explicit current actor only; all remaining same-name/campus actors stay foreign.
 projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));foreign=[b for b in current_forms if b['uid'] not in {UID,RELATED}];foreign_shape=shapely.union_all([polygon(b['rings']) for b in foreign]);checks={};reasons=[r for r in previous['reasons'] if r not in REASONS]
 for key,target in [('current',own),('primary',shapes[UID])]:
  extra=projection.difference(target);m={'targetCoverage':projection.intersection(target).area/target.area,'maximumOriginalExtentM':float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max()),'unrelatedSourceExcessM2':extra.intersection(foreign_shape).area,'rawExactRelatedCanopyExcessM2':extra.intersection(related).area}
  checks[key]=m
  if not(.95<=m['targetCoverage']<=1.000000001 and m['maximumOriginalExtentM']<=10 and m['unrelatedSourceExcessM2']<=1):reasons.append('complete-source-'+key+'-spatial-bound')
 raw=sorted(set(previous['reasons'])&REASONS);assert raw,'Specific raw canopy overlap required';passed=not reasons;out=deepcopy(previous)
 out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawUnrelatedOverlapReasonsRetained=raw,explicitRelatedUID=RELATED,primaryRecords=attrs,currentRelatedForm=forms[RELATED],primarySharedBoundaryGeoJSON=shapely.to_geojson(primary_shared),primarySharedBoundaryLengthM=primary_shared.length,currentSharedBoundaryGeoJSON=shapely.to_geojson(viewer_shared),currentSharedBoundaryLengthM=viewer_shared.length,independentFullSourceSpatialChecks=checks,allOtherCurrentFormsRetained=current_forms,allOtherActorsStillForeignUIDs=sorted(b['uid'] for b in foreign),canopyGovernmentVerticalMeasurementsAbsent=True,currentCanopyCollisionExemption=False,currentCanopyTerrainExemption=False,currentCanopyRemoval=False,proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Named80343/83471 only: unique Active primary Science Museum records identify one museumTower and one open-sided Science Museum structure, with different preserved BuildingIDs and exact9.459m attached boundary and disjoint own interiors on BOTH raw primary/current geometry. Complete original source is independently pinned and tested against BOTH footprints. Raw1.855m² ancillary overlap remains. No generic same-name grouping, campus polygon credit, property boundary claim, canopy height precision, actor removal, collision or full physical/runtime exemption.')
 return out
def verify_files(row,context,local):
 previous=original_verify(row,context,local);receipt=read(DOC/'result.json');assert receipt['jobId']==JOB
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 def module(name,file):
  s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 decoder=module('science_named_original_decoder','xl-second-pass.py');decoder.LOCAL=local;tri=decoder.glb_triangles(row);final=module('science_named_current_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);providers={}
 for uid in [UID,RELATED]:
  stem=uid.split('/')[1].replace(':','-');p=DOC/(stem+'-building.json');q=read(DOC/(stem+'-building.request.json'));assert q['sha256']==digest(p.read_bytes()) and q['method']=='GET' and q['url']=='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query' and q['parameters']['returnGeometry']=='true' and q['parameters']['outFields']=='*' and q['parameters']['where']=="BuildingCSUID='"+EXPECTED[uid][0]+"'";providers[uid]=read(p)
 for _,_,url in forms:assert digest((ROOT/'3d-viewer'/url).read_bytes())==context['neighbourTileHashes'][url]
 return named_proof(previous,row,tri,[b for b,_,_ in forms],providers)

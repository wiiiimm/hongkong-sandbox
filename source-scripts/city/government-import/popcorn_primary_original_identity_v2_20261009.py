"""Named source-bound primary identity alternative; no physical acceptance.

The artificial whole-cell failures remain explicit. Unique current authoritative
lineage and complete original geometry must independently pass existing bounds.
"""
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from exact_original_georef_cell_identity_20261009 import verify_files as verify_cell
UIDS={'landsd/'+str(i)+':0' for i in [295421,295425,309558,53924]}
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-six-held-primary-lineage-20261009'
JOB='ad02a882fd9a11b085d097d3d5d86b6e132832cf9d227306fe90226bda8a3539'
POLICY='four-popcorn-originals-exact-primary-stable-identity-and-complete-geometry-v2'
CELL_REASONS={'current-target-does-not-cover-whole-georef-cell','original-source-does-not-cover-whole-georef-cell'}
def primary_proof(previous,row,provider,triangles,other_forms):
 tri=np.asarray(triangles,dtype='<f8');assert tri.shape==(row['triangles'],3,3) and np.isfinite(tri).all(),'Incomplete original world triangles'
 assert digest(tri.tobytes())==previous['worldTrianglesSHA256'],'Source-bound decoded world triangles changed'
 result=deepcopy(previous);reasons=[r for r in previous['reasons'] if r not in CELL_REASONS];rawcell=sorted(set(previous['reasons'])&CELL_REASONS)
 assert row['uid'] in UIDS and rawcell,'Named failed whole-cell source required'
 assert previous['uid']==row['uid'] and previous['sourceSHA256']==row['sourceSHA256'] and previous['originalOwnership']['sourceGraphVerified']
 form=row['source']['building'];assert form['uid']==row['uid'] and form['structureType']=='Tower';csuid=form['buildingCSUID'];assert row['modelId'][1:11]==csuid[:10] and csuid[10]=='T'
 features=provider.get('features',[]);primary=None;spatial=None
 if provider.get('error') or provider.get('exceededTransferLimit') or len(features)!=1:reasons.append('unique-primary-provider-record-required')
 else:
  feature=features[0];a=feature['attributes'];primary=a
  if (a.get('Status'),a.get('BuildingCSUID'),a.get('BuildingID'),a.get('BuildingBlockType'),a.get('GeoRefNo'))!=('Active',csuid,form['buildingId'],'Tower',csuid[:10]):reasons.append('primary-stable-csuid-building-id-type-georef-differs')
  date=a.get('DateCreate')
  if not isinstance(date,(int,float)) or datetime.fromtimestamp(date/1000,timezone.utc).strftime('%Y%m%d')!=csuid[11:]:reasons.append('primary-source-creation-lineage-differs')
  g=feature.get('geometry');sr=(g or {}).get('spatialReference',provider.get('spatialReference',{}))
  if not g or sr.get('latestWkid',sr.get('wkid'))!=2326:reasons.append('primary-original-hk80-footprint-required')
  else:
   rings=[[(v[0]-834500,816500-v[1]) for v in ring] for ring in g['rings']];target=shapely.Polygon(rings[0],rings[1:]);tri=np.asarray(triangles,float)
   assert tri.shape==(row['triangles'],3,3) and np.isfinite(tri).all(),'Incomplete original world triangles'
   if not target.is_valid or target.area<=0:reasons.append('primary-original-footprint-invalid')
   else:
    projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));foreign=shapely.union_all([shapely.Polygon(b['rings'][0],b['rings'][1:]) for b in other_forms if b['uid']!=row['uid']]);excess=projection.difference(target)
    spatial=dict(targetCoveredBySourceProjection=projection.intersection(target).area/target.area,sourceExcessMaximumDistanceFromTargetM=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).max()),sourceExcessCoveredByUnrelatedFormsM2=excess.intersection(foreign).area,originalWorldTrianglesSHA256=digest(tri.astype('<f8').tobytes()),primaryTargetAreaM2=target.area)
    for k,lo,hi in [('targetCoveredBySourceProjection',.95,1.000000001),('sourceExcessMaximumDistanceFromTargetM',0,10),('sourceExcessCoveredByUnrelatedFormsM2',0,1)]:
     if not lo<=spatial[k]<=hi:reasons.append('fresh-primary-full-source-spatial-bound:'+k)
 passed=not reasons
 result.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawWholeCellReasonsRetained=rawcell,primaryProviderRecord=primary,independentPrimaryFullSourceSpatialChecks=spatial,primaryProviderObjectID=(primary or {}).get('OBJECTID'),currentViewerObjectID=form['objectId'],wholeCoordinateCellUsedForSpatialCredit=False,proof=dict(exactObjectId=passed,exactBuildingCSUID=passed,uniqueViewerMatch=passed,identityAccepted=passed),physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Unique Active exact stable BuildingCSUID/BuildingID/type/GeoRef/date primary record and unchanged original root/bytes/native lineage; full original geometry independently meets existing95%/10m/1m² bounds against BOTH viewer and provider footprints. Raw whole-cell failures remain; no cell or permit spatial credit, object-ID rewrite, unrelated-actor exemption or physical acceptance.')
 return result

def verify_files(row,context,local):
 previous=verify_cell(row,context,local);receipt=read(DOC/'result.json');assert receipt['jobId']==JOB
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 stem=row['uid'].split('/')[1].replace(':','-');p=DOC/(stem+'-provider.json');raw=p.read_bytes();request=read(DOC/(stem+'-provider.request.json'))
 assert request['sha256']==digest(raw) and request['method']=='GET' and request['url']=='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
 assert request['parameters']['where']=="BuildingCSUID='"+row['source']['building']['buildingCSUID']+"'" and request['parameters']['outSR']=='2326' and request['parameters']['returnGeometry']=='true'
 def module(name,file):
  s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 decoder=module('primary_unchanged_original_decoder','xl-second-pass.py');decoder.LOCAL=local;tri=decoder.glb_triangles(row);final=module('primary_current_complete_forms','xl-final-script-pass.py');lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 for _,_,url in forms:assert digest((ROOT/'3d-viewer'/url).read_bytes())==context['neighbourTileHashes'][url]
 return primary_proof(previous,row,json.loads(raw),tri,[b for b,_,_ in forms])

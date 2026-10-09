"""One exact original tower's ten connected street-front boundary faces.

Only the explicit extent role is interpreted. Full source coverage, all foreign
actors, root/cell/ownership, physical/support/runtime/browser gates remain.
"""
from copy import deepcopy
from datetime import datetime,timezone
import importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from source_closed_components import components
from exact_original_georef_cell_identity_20261009 import verify_files as original_verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
UID='landsd/118230:0';MODEL='B378291822401063C0'
SOURCE_SHA='0e9740f9b9b3061aa4f4bbe26b397db58f870476aa0716745339e505a79c51ff'
WORLD_SHA='b276304c2b94878d7c47665b7536a1dca385cf0bd52dd8264dff92d7dc9c5863'
ROAD_SHA='5a6db5d8bec3208e42dd1f75908804c757b79a570ee1ae63609c00ac63491658'
FACE_IDS=[16743,16747,16748,16749,16751,16752,16990,16991,16992,16993]
DOC=ROOT/'docs/astra-city/government-import/government-xl-two-harbourfront-primary-owner-20261009'
JOB='b0b8ef5f228a8ba56ee09e0110ccfd9b5dafd400235928bda75369ed9ed702bc'
POLICY='one-exact-original-two-harbourfront-connected-road-margin-boundary-v1'
REASONS={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}

def polygon(rings):
 result=shapely.GeometryCollection()
 for ring in rings:result=result.symmetric_difference(shapely.Polygon(ring))
 assert result.is_valid
 return result

def primary(provider):
 assert not provider.get('error') and not provider.get('exceededTransferLimit') and len(provider.get('features',[]))==1
 assert provider['spatialReference'].get('latestWkid',provider['spatialReference'].get('wkid'))==2326
 f=provider['features'][0];a=f['attributes'];assert (a['Status'],a['BuildingCSUID'],a['BuildingID'],a['BuildingBlockType'],str(a['GeoRefNo']))==('Active','3782918224T20050430',1108242698,'Tower','3782918224')
 assert datetime.fromtimestamp(a['DateCreate']/1000,timezone.utc).strftime('%Y%m%d')=='20050430'
 return polygon([[(x-834500,816500-y) for x,y in ring] for ring in f['geometry']['rings']]),a

def named_proof(previous,row,triangles,current_forms,provider,evidence):
 assert row['uid']==previous['uid']==UID and row['modelId']==MODEL and previous['sourceSHA256']==row['sourceSHA256']==SOURCE_SHA
 assert previous['originalOwnership']['sourceGraphVerified']
 tri=np.asarray(triangles,float);assert tri.shape==(19438,3,3) and row['triangles']==19438 and np.isfinite(tri).all()
 assert digest(tri.astype('<f8').tobytes())==previous['worldTrianglesSHA256']==evidence['worldTrianglesSHA256']==WORLD_SHA,'Complete original world geometry differs'
 assert evidence['uid']==UID and evidence['modelId']==MODEL and evidence['sourceSHA256']==SOURCE_SHA and evidence['allFarFaceIds']==FACE_IDS
 forms={b['uid']:b for b in current_forms};assert len(forms)==len(current_forms) and UID in forms and forms[UID]==row['source']['building']==evidence['currentTargetForm']
 assert (forms[UID]['buildingCSUID'],forms[UID]['buildingId'],forms[UID]['structureType'])==('3782918224T20050430',1108242698,'Tower')
 main=[c for c in components(tri)['components'] if set(FACE_IDS)<=set(c['faceIndices'])];assert len(main)==1 and main[0]['faceIndices']==evidence['completeConnectedComponentFaceIds'] and main[0]['triangles']==3643,'Complete original main attachment differs'
 roads=evidence['roadMarginRows'];assert digest(json.dumps(roads,sort_keys=True,separators=(',',':'),allow_nan=False).encode())==ROAD_SHA,'Independent road-margin geometry differs'
 assert roads and all(r['layer']=='9_CartoTransLine_1K' and r['properties']=={'_symbol':10} and r['quantizationStepM']==0.1492910708734178 for r in roads)
 assert evidence['roadMarginStyle'] and all(s['source-layer']=='9_CartoTransLine_1K' and s['filter']==['==','_symbol',10] and '/RM, E' in s['id'] for s in evidence['roadMarginStyle'])
 road=shapely.union_all([shapely.geometry.shape(r['geometry']) for r in roads]);far=tri[FACE_IDS];d=float(shapely.distance(shapely.points(far[:,:,[0,2]].reshape(-1,2)),road).max());assert d==0.2368824057038735
 assert float(far[:,:,1].min())==4.802999973297119 and float(far[:,:,1].max())==6.064000129699707,'Original low boundary height differs'
 official,attrs=primary(provider);own=polygon(forms[UID]['rings']);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));foreign=[b for b in current_forms if b['uid']!=UID];other=shapely.union_all([polygon(b['rings']) for b in foreign]);checks={};reasons=[r for r in previous['reasons'] if r not in REASONS]
 for name,target in [('current',own),('primary',official)]:
  distances=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3);ids=np.flatnonzero(distances.max(axis=1)>10).tolist();assert ids==FACE_IDS,'Extra or missing distant original faces'
  remain=np.ones(len(tri),bool);remain[FACE_IDS]=False
  m={'fullOriginalTargetCoverage':float(target.intersection(projection).area/target.area),'fullOriginalRawMaximumExtentM':float(distances.max()),'allOtherOriginalFacesMaximumExtentM':float(distances[remain].max()),'fullOriginalForeignExcessM2':float(projection.difference(target).intersection(other).area),'explicitBoundaryFaceIds':ids,'explicitBoundaryFacesOmittedFromProjection':False}
  checks[name]=m
  if not(.95<=m['fullOriginalTargetCoverage']<=1.000000001 and m['allOtherOriginalFacesMaximumExtentM']<=10 and m['fullOriginalForeignExcessM2']<=1):reasons.append('complete-source-'+name+'-spatial-bound')
 raw=sorted(set(previous['reasons'])&REASONS);assert raw,'Specific original extent failure absent';passed=not reasons;out=deepcopy(previous)
 out.update(policy=POLICY,passed=passed,reasons=sorted(set(reasons)),rawExtentReasonsRetained=raw,rawOriginalExtentRetained=True,sourceSpecificBoundaryFaceIds=FACE_IDS,independentRoadMarginMaximumDistanceM=d,primaryRecord=attrs,independentFullSourceSpatialChecks=checks,allOtherCurrentFormsRetained=current_forms,allOtherActorsStillForeignUIDs=sorted(b['uid'] for b in foreign),proof={k:passed for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,currentActorRemoval=False,physicalSupportExemption=False,qualification='Exact original118230 only: ten connected source-authored street-front boundary faces follow independently mapped RM,E. No property/cadastral/vertical survey or support claim. Raw11.9967m and all ten faces retained; full original projection, all other faces/current actors, source root/cell and physical/runtime gates remain strict.')
 return out

def verify_files(row,context,local):
 previous=original_verify(row,context,local);receipt=read(DOC/'result.json');assert receipt['jobId']==JOB
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==SOURCE_SHA;tri=decode_original_world_triangles(raw)
 spec=importlib.util.spec_from_file_location('harbourfront_named_current_forms',HERE/'xl-final-script-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=m.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
 for _,_,url in forms:assert digest((ROOT/'3d-viewer'/url).read_bytes())==context['neighbourTileHashes'][url]
 p=DOC/'current-unique-primary-record.json';request=read(DOC/'current-unique-primary-record.request.json');assert request['sha256']==digest(p.read_bytes()) and request['url']=='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query' and request['parameters']=={'f':'json','where':"BuildingCSUID='3782918224T20050430'",'outFields':'*','returnGeometry':'true','outSR':2326}
 return named_proof(previous,row,tri,[b for b,_,_ in forms],read(p),read(DOC/'attached-original-road-margin-diagnostic.json.gz'))

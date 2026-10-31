"""Measure complete four-original project coverage; preserve every approval gate."""
import argparse,json,sys,uuid,urllib.request,urllib.parse,re
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fleur-four-original-compound-context-v1-20261028';OLD='government-xl-fleur-four-original-components-20261007';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UIDS={'landsd/'+str(n)+':0'for n in[137130,23296,269972,270880]};POD='landsd/23296:0';PDF='https://cms.nwd.com.hk/download/2003/31_6599_B10003/FLEUR%20PAVILIA%20-%20Sales%20Brochure%20-%2020260730.pdf'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and{'building:'+u for u in UIDS}<=set(lease['resources'])and not DOC.exists();_,pins=authenticate(BASE/OLD);path=BASE/OLD/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];selection=read(path)['rows'];assert{r['uid']for r in selection}==UIDS;refs=[Path(__file__),BASE/OLD/'result.json',path];projected={};sources=[]
 for row in selection:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());polys=shapely.polygons(tri[:,:,[0,2]]);projected[row['uid']]=shapely.union_all(polys[shapely.area(polys)>0]);sources.append(dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),originalWorldSHA256=digest(tri.astype('<f8').tobytes()),projectionM2=projected[row['uid']].area))
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');forms={}
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in UIDS:assert b['uid']not in forms;forms[b['uid']]=b;refs.append(p)
 assert set(forms)==UIDS and len({forms[u]['parent']for u in UIDS})==1;shapes={}
 for uid,b in forms.items():
  shape=shapely.GeometryCollection()
  for ring in b['rings']:shape=shape.symmetric_difference(shapely.Polygon(ring))
  assert shape.is_valid;shapes[uid]=shape
 compound=shapely.union_all(list(projected.values()));target=shapely.union_all(list(shapes.values()));pod_missing=shapes[POD].difference(projected[POD]);coverage=[dict(uid=u,individualMissingM2=shapes[u].difference(projected[u]).area,compoundMissingM2=shapes[u].difference(compound).area)for u in sorted(UIDS)];primary=[]
 def fetch(url,name,limit):
  path=LOCAL/'primary'/name
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=120)as response:
    raw=response.read(limit+1);assert len(raw)<=limit;final=response.url;headers={k:v for k,v in response.headers.items()if k.lower()in['content-type','content-length','etag','last-modified']}
   path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);refs.append(path);primary.append(dict(url=url,finalURL=final,path=str(path.relative_to(ROOT)),sha256=digest(raw),headers=headers));return path
  except Exception as error:primary.append(dict(url=url,errorType=type(error).__name__));return None
 pdf=fetch(PDF,'fleur-pavilia-sales-brochure-20260730.pdf',64*1024**2);page_index=[]
 if pdf:
  import pymupdf
  with pymupdf.open(pdf)as document:
   terms={'layout-plan':r'layout\s+plan','basement':r'basement','ground-floor':r'ground\s+floor','podium':r'podium','elevation':r'elevation'}
   for i,page in enumerate(document):
    text=page.get_text();matched=[k for k,v in terms.items()if re.search(v,text,re.I)]
    if matched:page_index.append(dict(pageIndex=i,pageNumber=i+1,terms=matched))
   page_count=len(document)
 else:page_count=None
 endpoint='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query';params=dict(f='json',where="GeoRefNo='3903616785' AND Status='Active'",outFields='OBJECTID,BuildingID,BuildingCSUID,GeoRefNo,BuildingNameEN,BuildingBlockType,BaseHeight,TopHeight,Storeys,StoreysInBasement,Status',returnGeometry='false');metadata=fetch(endpoint+'?'+urllib.parse.urlencode(params),'podium-current-official-attributes.json',2*1024**2);official=read(metadata)if metadata else None
 result=dict(uids=sorted(UIDS),sources=sources,currentForms=[dict(uid=u,name=forms[u].get('name'),buildingCSUID=forms[u]['buildingCSUID'],parent=forms[u]['parent'])for u in sorted(UIDS)],coverageByRecord=coverage,podiumAloneMissingM2=pod_missing.area,podiumMissingAfterFourOriginalsM2=shapes[POD].difference(compound).area,oldPodiumMissingCoveredByOtherOriginalsM2=pod_missing.intersection(compound).area,compoundSourceOutsideProjectM2=compound.difference(target).area,projectMissingFromCompoundM2=target.difference(compound).area,primaryCaptures=primary,brochurePages=page_count,brochureRelevantPages=page_index,officialAttributes=official,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,qualification='All four original files and unmodified current target polygons, no new or omitted source faces. Compound projection may explain source-file allocation but never automatically proves role, identity, property boundaries, current terrain or support. PDF/official attributes are primary context only; no approval transfer, geometry/terrain edit or installation.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('fleur_complete_compound_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-original-fleur-compound-projection-primary-context',refs,result);print({k:result[k]for k in['podiumAloneMissingM2','podiumMissingAfterFourOriginalsM2','oldPodiumMissingCoveredByOtherOriginalsM2','compoundSourceOutsideProjectM2','brochurePages']},flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('four-original-fleur-context-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()

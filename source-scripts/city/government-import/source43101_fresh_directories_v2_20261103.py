"""Bounded fresh official directory lookup for unresolved two-root source43101.

Complete ETag-bound ZIP directories only; no model payload, geometry edit,
substitute, approval, or permanent absence classification.
"""
import argparse,concurrent.futures,json,struct,sys,uuid
from pathlib import Path
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v2_20261103 import execute_reserved
from bounded_zip_directory_v1_20261103 import fetch as bounded_directory
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
sys.path.insert(0,str(HERE.parent/'citywide-source'));from discover import ac,models
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-source43101-fresh-directories-v2-20261103'
CAPTURE='government-xl-source43101-current-selection-v1-20261029'
UIDS={'landsd/43101:0':'4565726830T20050430'}
SHEETS=['8-SW-11C']
INDEXES={'package':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query','individualised':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1671676915450_88604/FeatureServer/0/query'}
FORMATS=['Format_glTF','Format_FBX']

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();out=BASE/BATCH;local=HERE/'local'/BATCH;lp=local/'reservation.json'
 assert not out.exists()
 if not a.owned:
  assert not local.exists();claim=reservations.claim('source43101-fresh-source-lookup-'+str(uuid.uuid4()),['building:landsd/43101:0',*['building:'+u for u in sorted(UIDS)],'immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,'--owned'])
 lease=read(lp);assert reservations.owns(lease)
 _,pins=authenticate(BASE/CAPTURE);sp=BASE/CAPTURE/'selection.json.gz';assert digest(sp.read_bytes())==pins[str(sp.relative_to(ROOT))];selection=read(sp);assert len(selection['rows'])==1 and selection['rows'][0]['uid']=='landsd/43101:0'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());row=selection['rows'][0];tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];forms={f['uid']:f for f in read(tile)['buildings']if f['uid']in UIDS};assert {u:f['buildingCSUID']for u,f in forms.items()}==UIDS
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 refs=[Path(__file__),HERE/'bounded_zip_directory_v1_20261103.py',asset,BASE/CAPTURE/'result.json',sp,manifest,tile,HERE.parent/'landsd-territory/source.py',HERE.parent/'citywide-source/discover.py',HERE.parent/'landmark-acquisition/acquire.py'];out.mkdir();save(out/'current-forms.json',forms)
 prefixes={u:s[:10]for u,s in UIDS.items()};index_before={};tasks=[];errors=[]
 def query(family,phase):
  raw,rec=request(INDEXES[family],dict(f='json',where='SHEETNO IN ('+','.join("'"+s+"'"for s in SHEETS)+')',outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100'))
  p=out/(family+'-index-'+phase+'.json');p.write_bytes(raw);save(p.with_suffix('.request.json'),rec);d=json.loads(raw);assert not d.get('error')and not d.get('exceededTransferLimit')and len(d['features'])==1 and {f['attributes']['SHEETNO']for f in d['features']}==set(SHEETS)
  coverage=unary_union([Polygon(r)for f in d['features']for r in f['geometry']['rings']]);assert coverage.is_valid
  for prefix in prefixes.values():
   x,y=800000+int(prefix[:5]),800000+int(prefix[5:]);assert coverage.covers(box(x,y,x+1,y+1)),'Nominated sheets do not cover the exact government GeoRef cell'
  return sorted(d['features'],key=lambda f:f['attributes']['SHEETNO'])
 for family in INDEXES:
  try:
   features=query(family,'before');index_before[family]=features
   for feature in features:
    attrs=feature['attributes'];assert 'REVISIONDATE'in attrs
    for fmt in FORMATS:
     url=attrs.get(fmt);assert isinstance(url,str)and url.startswith('https://download.map.gov.hk/')
     tasks.append((family,attrs,fmt,url))
  except Exception as e:errors.append(dict(stage='index-before',family=family,errorClass=type(e).__name__,detail=str(e)[:160]))
 assert len(tasks)<=4
 def scan(task):
  family,attrs,fmt,url=task;folder=out/'directories'/family/attrs['SHEETNO']/fmt;folder.mkdir(parents=True);net=ac.Network(folder/'transfer.json',cap=8_000_000)
  infos,check,directory,archive=bounded_directory(net,url);etag=archive['etag'];size=archive['archiveBytes']
  assert check['directorySHA256']==digest(directory);(folder/'zip-directory.bin').write_bytes(directory)
  names=[e.filename for e in infos];native=models(infos)if fmt=='Format_glTF'else[]
  matches={u:[n for n in names if p in n]for u,p in prefixes.items()}
  r=dict(family=family,sheet=attrs['SHEETNO'],format=fmt,revision=attrs['REVISIONDATE'],etag=etag,archiveBytes=size,completeMembers=names,exactGeoRefMembers=matches,exactGeoRefNativeModels={u:[m for m in native if m['geoRefNo']==p]for u,p in prefixes.items()},sourceURL=url,sourceModelPayloadRequests=0,**check);save(folder/'directory.json.gz',r);return r
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  futures={pool.submit(scan,t):t for t in tasks}
  for f in concurrent.futures.as_completed(futures):
   family,attrs,fmt,_=futures[f]
   try:
    r=f.result();rows.append(r);print(dict(family=family,sheet=r['sheet'],format=fmt,matches={u:len(v)for u,v in r['exactGeoRefMembers'].items()}),flush=True)
   except Exception as e:errors.append(dict(stage='directory',family=family,sheet=attrs['SHEETNO'],format=fmt,errorClass=type(e).__name__,detail=str(e)[:160]))
 for family,before in index_before.items():
  try:assert query(family,'after')==before,'Official index changed during lookup'
  except Exception as e:errors.append(dict(stage='index-after',family=family,errorClass=type(e).__name__,detail=str(e)[:160]))
 assert reservations.owns(lease)and digest(manifest.read_bytes())==mh and digest(tile.read_bytes())==row['source']['tileSHA256']
 complete=len(tasks)==len(rows)==4 and not errors
 result=dict(uids=sorted(UIDS),ownerUid='landsd/43101:0',currentManifestSHA256=mh,historicalSelectionManifestSHA256=selection['manifestSHA256'],historicalSelectionGrantsNoCurrentAcceptance=True,currentFormCSUIDs=UIDS,exactGeoRefPrefixes=prefixes,sheets=SHEETS,formats=FORMATS,indexFamilies=list(INDEXES),completeBoundedFreshSearch=complete,rows=rows,errors=errors,sourceModelPayloadRequests=0,sourceGeometryChanges=0,installationApproved=False,publication=False,permanentRejection=False,qualification='Fresh official indexes plus complete ETag-bound GLTF/FBX central directories, with the exact GeoRef cell inside the queried sheet geometry. Exact prefix matches are acquisition candidates only; a miss applies solely to these revisions and sheets. No substitute, geometry edit, source acceptance or permanent absence decision.')
 save(out/'summary.json',result);refs.extend(p for p in out.rglob('*')if p.is_file());module('source43101_fresh_directory_v2_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-fresh-official-companion-source-directories',refs,result);print(dict(complete=complete,errors=len(errors),candidateDirectories=sum(any(r['exactGeoRefMembers'][u]for u in UIDS)for r in rows)),flush=True)
if __name__=='__main__':main()

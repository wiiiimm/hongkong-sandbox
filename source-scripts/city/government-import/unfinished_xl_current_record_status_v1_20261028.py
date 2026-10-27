"""Read-only current government record audit for every unfinished XL source key."""
from pathlib import Path
from collections import Counter
import re,urllib.request,urllib.parse,json
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unfinished-current-record-status-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;INVENTORY='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028';ENDPOINT='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists()and not LOCAL.exists();_,pins=authenticate(BASE/INVENTORY);p=BASE/INVENTORY/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=read(p)['rows'];assert len(rows)==126 and len({r['sourceKey']for r in rows})==126;refs=[Path(__file__),BASE/INVENTORY/'result.json',p];keys={}
 for r in rows:
  mid=r['sourceKey'].split('/')[1];m=re.match(r'^[A-Za-z](\d{10})',mid);assert m,mid;keys[r['sourceKey']]=m.group(1)
 georefs=sorted(set(keys.values()));captures=[];features=[];errors=[]
 for i in range(0,len(georefs),30):
  batch=georefs[i:i+30];params=dict(f='json',where='GeoRefNo IN ('+','.join("'"+g+"'"for g in batch)+')',outFields='OBJECTID,BuildingID,BuildingCSUID,GeoRefNo,BuildingNameEN,BuildingBlockType,BaseHeight,TopHeight,Storeys,StoreysInBasement,Status',returnGeometry='false');url=ENDPOINT+'?'+urllib.parse.urlencode(params)
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90)as response:raw=response.read(8*1024**2+1);assert len(raw)<=8*1024**2;final=response.url
   data=json.loads(raw);assert not data.get('error')and not data.get('exceededTransferLimit');assert all(str(f['attributes']['GeoRefNo'])in batch for f in data['features']);path=LOCAL/('response-'+str(i//30)+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);refs.append(path);features.extend(f['attributes']for f in data['features']);captures.append(dict(requestedGeoRefs=batch,url=url,finalURL=final,response=dict(path=str(path.relative_to(ROOT)),sha256=digest(raw)),records=len(data['features'])))
  except Exception as error:errors.append(dict(requestedGeoRefs=batch,errorType=type(error).__name__,httpStatus=getattr(error,'code',None)))
 checked={g for c in captures for g in c['requestedGeoRefs']};resultrows=[]
 for row in rows:
  geo=keys[row['sourceKey']];records=[f for f in features if str(f['GeoRefNo'])==geo];exact=[f for f in records if row.get('buildingCSUID')and f['BuildingCSUID']==row['buildingCSUID']];state='request-incomplete'if geo not in checked else 'exact-record-returned'if exact else 'georef-returned-without-exact-csuid'if records else 'no-record-returned';resultrows.append(dict(uid=row['uid'],sourceKey=row['sourceKey'],indexedSourceSHA256=row['indexedSourceSHA256'],indexedBuildingCSUID=row.get('buildingCSUID'),geoRefNo=geo,status=state,exactCSUIDRecordStatuses=sorted({str(f.get('Status'))for f in exact}),currentRecords=records,installationApproved=False,permanentRejection=False))
 result=dict(uids=sorted(r['uid']for r in rows if r['uid']),sourceKeys=[r['sourceKey']for r in rows],scope=126,uniqueGeoRefs=len(georefs),captures=captures,errors=errors,rows=resultrows,statusCounts=dict(Counter(r['status']for r in resultrows)),sourceGeometryChanges=0,installationApproved=False,qualification='Current primary government record attributes only; no geometry requested or modified. Exact CSUID versus GeoRef-only results remain separate, current OBJECTID changes are not fabricated viewer UID changes. Missing/changed/inactive records are evidence for investigation, not corruption, permanent rejection, source identity/placement acceptance or installation credit. All126fixed source keys and both unmatched viewer UIDs retained.')
 save(DOC/'summary.json',result);module('unfinished_xl_live_record_status_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-unfinished-xl-current-government-record-status-evidence',refs,result);print(dict(scope=126,statusCounts=result['statusCounts'],errors=len(errors)),flush=True)
if __name__=='__main__':main()

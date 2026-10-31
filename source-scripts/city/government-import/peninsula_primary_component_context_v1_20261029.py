"""Read primary current component records and the overlapping OSM form; no acceptance."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from datetime import datetime,timezone
import json
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-peninsula-primary-component-context-v1-20261029'
BASE=ROOT/'docs/astra-city/government-import';RUNTIME='government-xl-peninsula-pair-current-v1-20261029-runtime'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];_,pins=authenticate(BASE/RUNTIME)
    path=BASE/RUNTIME/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];selection=read(path);refs.extend([path,BASE/RUNTIME/'result.json'])
    uids=['landsd/270876:0','landsd/266543:0'];rows=[next(r for r in selection['rows']if r['uid']==u)for u in uids]
    csuids=[r['source']['building']['buildingCSUID']for r in rows];out.mkdir();records=[]
    root='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
    for layer in [0,1]:
        parameters=dict(f='json',where='BuildingCSUID IN ('+','.join("'"+s+"'"for s in csuids)+')',outFields='*',returnGeometry='true',outSR='2326')
        url=root+'/'+str(layer)+'/query';request=out/('primary-layer-'+str(layer)+'.request.json');resultpath=out/('primary-layer-'+str(layer)+'.json')
        try:
            with urlopen(Request(url+'?'+urlencode(parameters),headers={'User-Agent':'HongKongSandbox-source-review/1.0'}),timeout=25)as response:raw=response.read()
            resultpath.write_bytes(raw);data=json.loads(raw);assert 'error'not in data,data.get('error');assert not data.get('exceededTransferLimit')
            record=dict(layer=layer,features=data.get('features',[]),passed=True)
        except Exception as error:record=dict(layer=layer,passed=False,errorType=type(error).__name__,reason=str(error))
        save(request,dict(method='GET',url=url,parameters=parameters,retrievedUTC=datetime.now(timezone.utc).isoformat(),responseSHA256=digest(resultpath.read_bytes())if resultpath.exists()else None));refs.append(request)
        if resultpath.exists():refs.append(resultpath)
        records.append(record);print(dict(layer=layer,passed=record['passed'],features=len(record.get('features',[]))),flush=True)
    url='https://api.openstreetmap.org/api/0.6/way/709674357';path=out/'overlapping-osm-way.xml'
    try:
        with urlopen(Request(url,headers={'User-Agent':'HongKongSandbox-source-review/1.0'}),timeout=25)as response:path.write_bytes(response.read())
        import xml.etree.ElementTree as ET
        way=ET.fromstring(path.read_bytes()).find('way');assert way is not None
        osm=dict(passed=True,id=way.get('id'),version=way.get('version'),tags={t.get('k'):t.get('v')for t in way.findall('tag')});refs.append(path)
    except Exception as error:osm=dict(passed=False,errorType=type(error).__name__,reason=str(error))
    save(out/'osm-request.json',dict(url=url,method='GET',retrievedUTC=datetime.now(timezone.utc).isoformat(),responseSHA256=digest(path.read_bytes())if path.exists()else None));refs.append(out/'osm-request.json')
    result=dict(uids=uids,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},buildingCSUIDs=csuids,currentPrimaryRecords=records,overlappingOSMForm=osm,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Read-only primary-source records for exact recorded CSUIDs, both provider layers and existing foreign OSM way. Raw types/geometry/versions retained. No inferred type alias, source-role or spatial acceptance; external contextual research does not prove exact mesh identity or allow suppression.')
    save(out/'summary.json',result);module('peninsula_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-primary-exact-CSUID-two-layer-and-overlapping-OSM-context',refs,result)

if __name__=='__main__':main()

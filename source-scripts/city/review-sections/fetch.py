#!/usr/bin/env python3
"""Retain the official HAD district response without changing its geometry."""
import argparse,datetime,gzip,hashlib,json,pathlib,subprocess,urllib.parse
HERE=pathlib.Path(__file__).resolve().parent
BASE='https://portal.csdi.gov.hk/server/rest/services/common/had_rcd_1634523272907_75218/MapServer'
RES='https://data.gov.hk/en-data/dataset/hk-had-json1-hong-kong-administrative-boundaries/resource/855f034a-c330-435c-a911-1d63538a6d55'
QUERIES={'service.json':BASE+'?f=pjson','layer.json':BASE+'/0?f=pjson','districts.json':BASE+'/0/query?'+urllib.parse.urlencode({'f':'json','where':'1=1','outFields':'*','outSR':2326,'returnGeometry':'true'}),'ids.json':BASE+'/0/query?'+urllib.parse.urlencode({'f':'json','where':'1=1','returnIdsOnly':'true'})}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--refresh',action='store_true');a=ap.parse_args();src=HERE/'sources';src.mkdir(exist_ok=True)
 records=[]
 for name,url in QUERIES.items():
  path=src/name
  if a.refresh or not path.exists():
   raw=subprocess.check_output(['curl','-fLsS','--max-time','90',url]);value=json.loads(raw)
   if 'error' in value:raise ValueError(value['error'])
   path.write_bytes(raw)
  raw=path.read_bytes();records.append({'path':str(path.relative_to(HERE)),'url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 features=json.loads((src/'districts.json').read_text())['features'];ids=json.loads((src/'ids.json').read_text())['objectIds']
 assert len(features)==len(ids)==18 and {f['attributes']['OBJECTID'] for f in features}==set(ids)
 metadata={'datasetId':'had_rcd_1634523272907_75218','title':'District Boundary','provider':'Home Affairs Department','landingPage':RES,'retrievedDate':'2026-09-07','crs':'EPSG:2326','sourceRecordCount':18,'licence':'Hong Kong Government open-data terms; district data via DATA.GOV.HK/CSDI','temporalNote':'Current response retrieved on the stated date. Source BEGIN_LIFESPAN is 2016-01-01; the service does not expose a later revision date. Retrieval date is not a claimed survey revision.','files':records}
 (HERE/'source-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n');print('Verified all 18 advertised district IDs; original response hashes retained.')
if __name__=='__main__':main()

"""Bounded fresh official identity records for two unchanged source118003 originals."""
import sys,gzip
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fu-tor-loy-primary-records-v1-20261023'
CAPTURE='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime'
LOOKUP='government-xl-fu-tor-loy-five-originals-current-v1-20261023-scope'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__),HERE.parent/'landsd-territory/source.py'];pins={}
 for name in [CAPTURE,LOOKUP]:
  _,p=authenticate(BASE/name);pins.update(p);refs.append(BASE/name/'result.json')
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 row=next(r for r in take(BASE/CAPTURE/'selection.json.gz')['rows']if r['uid']=='landsd/228219:0')
 forms={r['uid']:r for r in take(BASE/LOOKUP/'form-obligations.json.gz')}
 wanted=['landsd/228219:0','landsd/231442:0','landsd/232818:0','landsd/233770:0','landsd/233775:0']
 assert all(uid in forms for uid in wanted)
 csuids=[forms[uid]['buildingCSUID']for uid in wanted];assert len(set(csuids))==len(csuids)and all(s.isalnum()for s in csuids)
 where='BuildingCSUID IN ('+','.join("'"+s+"'"for s in csuids)+')';doc.mkdir()
 def query(name,table,where,geom):
  params=dict(f='json',where=where,outFields='*',returnGeometry='true'if geom else'false',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
  raw,receipt=request(URL+'/'+str(table)+'/query',params,json_expected=False)
  decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
  (doc/(name+'.json')).write_bytes(decoded);receipt.update(decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded);save(doc/(name+'-request.json'),receipt)
  if raw!=decoded:(doc/(name+'-original.gz')).write_bytes(raw)
  result=read(doc/(name+'.json'));assert not result.get('error')and not result.get('exceededTransferLimit')
  return result['features']
 features=query('footprints',0,where,True);relations=query('relations',1002,where,False)
 ids=sorted({int(f['attributes']['BuildingStructureID'])for f in relations})
 structures=query('structures',1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')',False)if ids else[]
 report=dict(uids=['landsd/228219:0'],requestedUIDs=wanted,requestedCSUIDs=csuids,footprints=len(features),relations=len(relations),structureIDs=ids,structures=len(structures),formScopeManifestSHA256=pins['3d-viewer/city/data/manifest.json'],identityAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Fresh official primary/structure metadata for exact current target and overlapping/protected forms. No inferred shared identity, support role or physical approval.')
 save(doc/'summary.json',report)
 module('source118003_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-nam-cheong-official-identity-records',refs,report)
 print(dict(footprints=len(features),relations=len(relations),structureIDs=ids),flush=True)
if __name__=='__main__':main()

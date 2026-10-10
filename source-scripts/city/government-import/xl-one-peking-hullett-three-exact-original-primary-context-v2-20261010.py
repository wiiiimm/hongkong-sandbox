"""Exact primary query derived from all three pinned original source identifiers.
Supersedes only the v1 illustrative extra Tower GeoRef query; original visuals stay.
"""
import importlib.util,json,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request
BATCH='government-xl-one-peking-hullett-three-exact-original-primary-context-v2-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CONTEXT=DOC.parent/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010'
VISUAL=DOC.parent/'government-xl-one-peking-hullett-original-primary-and-complete-visuals-v1-20261010'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query'
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);context=read(CONTEXT/'diagnostic.json.gz');expected=[]
 for r in context['sources']:
  if 'metadata' in r:
   b=r['metadata']['source']['building'];mid=r['metadata']['modelId'];csuid=b['buildingCSUID'];bid=b['buildingId'];typ=b['structureType']
  else:
   e=r['entry'];mid=e['modelId'];csuid=e['buildingCSUID'];b=next(x['building'] for x in context['completeCurrentForms'] if x['building']['uid']==r['uid']);bid=b['buildingId'];typ=b['structureType']
  assert mid[1:11]==csuid[:10];assert (mid[11:13],csuid[10],typ) in [('01','T','Tower'),('02','P','Podium')]
  expected.append(dict(uid=r['uid'],modelId=mid,geoRef=mid[1:11],csuid=csuid,buildingID=bid,type=typ,source=r['source'],completeFaces=r['completeFaces'],worldTrianglesSHA256=r['worldTrianglesSHA256']))
 csuids=sorted(r['csuid'] for r in expected);raw,rec=request(URL,dict(f='json',where='BuildingCSUID IN ('+','.join("'"+v+"'" for v in csuids)+')',outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID'))
 (DOC/'exact-three-source-primary.json').write_bytes(raw);save(DOC/'exact-three-source-primary.request.json',rec)
 data=json.loads(raw);assert len(data['features'])==3 and not data.get('exceededTransferLimit');assert len({f['attributes']['BuildingCSUID'] for f in data['features']})==3
 for r in expected:
  f=next(f for f in data['features'] if f['attributes']['BuildingCSUID']==r['csuid']);a=f['attributes'];assert a['Status']=='Active' and a['GeoRefNo']==r['geoRef'] and a['BuildingID']==r['buildingID'] and a['BuildingBlockType']==r['type'];r['freshPrimary']=f
 save(DOC/'diagnostic.json.gz',dict(rows=expected,completePrimarySources=3,primaryNamesAreNotSharedOwnership=True,priorVisualPrimaryTowerQueryQualified=False,correctedPriorExtraGeoRef='3552117445',actualTowerGeoRef='3553717452',sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installation=False,qualification='Exact UID/source model GeoRef/CSUID/type/BuildingID match to unique active current primary records. V1 full original visuals remain valid; its illustrative extra Tower GeoRef query was not the Tower source identity and gives no credit. This independent exact-derived capture supersedes that query only.'))
 refs=[Path(__file__),CONTEXT/'result.json',CONTEXT/'diagnostic.json.gz',VISUAL/'result.json']+[p for p in DOC.rglob('*') if p.is_file()]
 spec=importlib.util.spec_from_file_location('peking_primary_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'three-complete-original-source-derived-unique-active-primary-identity-context-v2',sorted(set(refs)),dict(uids=[r['uid'] for r in expected],sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,publication=False,completeUniqueActivePrimarySources=3))
 print(dict(csuid=csuids,completeUniqueActivePrimarySources=3),flush=True)
if __name__=='__main__':main()

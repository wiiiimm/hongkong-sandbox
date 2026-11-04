"""Fetch exact current government footprint/structure records; no identity approval."""
import argparse,sys,uuid,gzip
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BASE=ROOT/'docs/astra-city/government-import'
CAPTURE='government-xl-elegant-garden-sixteen-original-updated-runtime-v1-20261028'
BASIC='government-xl-elegant-garden-rex-surveyed-podium-support-v1-20261028'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-') and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 resourcepath=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(resourcepath)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('elegant-primary-records-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),resourcepath,HERE.parent/'landsd-territory/source.py'];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(CAPTURE,'selection.json.gz');forms=[r['source']['building']for r in selection['rows']]
 forms.append(take(BASIC,'support-input.json')['building']);uids=[b['uid']for b in forms];csuids=[b['buildingCSUID']for b in forms]
 assert len(set(csuids))==len(csuids)==17 and all(s.isalnum()for s in csuids)
 out.mkdir()
 def query(name,table,where,geometry=False):
  params=dict(f='json',where=where,outFields='*',returnGeometry='true'if geometry else'false',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
  raw,receipt=request(URL+'/'+str(table)+'/query',params,json_expected=False)
  decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
  (out/(name+'.json')).write_bytes(decoded);save(out/(name+'-request.json'),dict(receipt,decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded))
  if raw!=decoded:(out/(name+'-original.gz')).write_bytes(raw)
  data=read(out/(name+'.json'));assert not data.get('error')and not data.get('exceededTransferLimit')
  return data['features']
 where='BuildingCSUID IN ('+','.join("'"+s+"'"for s in csuids)+')'
 footprints=query('footprints',0,where,True);relations=query('relations',1002,where)
 ids=sorted({int(f['attributes']['BuildingStructureID'])for f in relations})
 structures=query('structures',1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')')if ids else[]
 bycsuid={}
 for f in footprints:bycsuid.setdefault(f['attributes']['BuildingCSUID'],[]).append(f['attributes'])
 rows=[]
 for b in forms:
  matches=bycsuid.get(b['buildingCSUID'],[])
  rows.append(dict(uid=b['uid'],csuid=b['buildingCSUID'],currentObjectId=b['objectId'],officialRecords=matches,
   structureIds=sorted({int(r['attributes']['BuildingStructureID'])for r in relations if r['attributes']['BuildingCSUID']==b['buildingCSUID']}),
   uniqueOfficialRecord=len(matches)==1,identityAccepted=False))
 result=dict(uids=uids,rows=rows,requestedCSUIDs=csuids,footprintRecords=len(footprints),relationRecords=len(relations),structureRecords=len(structures),
  missingCSUIDs=sorted(set(csuids)-set(bycsuid)),unexpectedCSUIDs=sorted(set(bycsuid)-set(csuids)),
  currentManifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,
  qualification='Fresh official footprint/structure/relation API responses for exactly sixteen original targets and the current surveyed BASIC Rex podium. No inferred common permit, legal ownership, identity exception, support role or model approval. Missing/multiple/changed records remain explicit.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('elegant_primary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'fresh-exact-elegant-government-footprint-structure-records',refs,result)
 print(dict(footprints=len(footprints),relations=len(relations),structures=len(structures),missing=result['missingCSUIDs']),flush=True)
if __name__=='__main__':main()

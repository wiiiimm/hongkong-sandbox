"""Fetch complete official membership for explicitly nominated occupation permits."""
import argparse,sys,uuid,gzip,re
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request
BASE=ROOT/'docs/astra-city/government-import'
CAPTURE='government-xl-elegant-garden-seventeen-original-current-selection-v1-20261028'
PRIMARY='government-xl-elegant-garden-current-primary-records-v1-20261028'
URL='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--permit',required=True,action='append');p.add_argument('--owned',action='store_true');a=p.parse_args()
 assert a.batch.startswith('government-xl-')and '/'not in a.batch
 assert len(set(a.permit))==len(a.permit)<=4 and all(re.fullmatch(r'[A-Za-z0-9()/ -]{1,50}',s)for s in a.permit)
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 rp=BASE/'government-xl-elegant-garden-sixteen-original-updated-terrain-plan-v1-20261028.json';resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('elegant-complete-permits-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp,HERE.parent/'landsd-territory/source.py'];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(CAPTURE,'selection.json.gz')['rows'];forms={r['source']['building']['buildingCSUID']:r['source']['building']for r in selected};old=take(PRIMARY,'summary.json');assert len(forms)==17
 out.mkdir()
 def query(name,table,where):
  params=dict(f='json',where=where,outFields='*',returnGeometry='false',resultRecordCount='1000',orderByFields='OBJECTID')
  raw,receipt=request(URL+'/'+str(table)+'/query',params,json_expected=False);decoded=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
  (out/(name+'.json')).write_bytes(decoded);save(out/(name+'-request.json'),dict(receipt,decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded))
  if raw!=decoded:(out/(name+'-original.gz')).write_bytes(raw)
  data=read(out/(name+'.json'));assert not data.get('error')and not data.get('exceededTransferLimit');return data['features']
 structures=query('complete-permit-structures',1003,'OPNo IN ('+','.join("'"+s+"'"for s in a.permit)+')')
 ids=sorted({int(f['attributes']['BuildingStructureID'])for f in structures})
 assert ids and len(ids)==len(structures)
 relations=query('complete-permit-relations',1002,'BuildingStructureID IN ('+','.join(map(str,ids))+')')
 rows=[]
 for permit in a.permit:
  member_ids={int(f['attributes']['BuildingStructureID'])for f in structures if f['attributes']['OPNo']==permit}
  csuids=sorted({f['attributes']['BuildingCSUID']for f in relations if int(f['attributes']['BuildingStructureID'])in member_ids})
  known=sorted(forms[s]['uid']for s in csuids if s in forms)
  rows.append(dict(permit=permit,completeStructureIDs=sorted(member_ids),completeCSUIDs=csuids,selectedSourceUIDs=known,
   membersWithoutSelectedOriginals=sorted(set(csuids)-set(forms)),allMembersHaveSelectedOriginals=bool(member_ids and csuids)and set(csuids)<=set(forms),identityAccepted=False))
 result=dict(uids=[f['uid']for f in forms.values()],requestedPermits=a.permit,rows=rows,sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,
  qualification='Fresh complete official occupation-permit structure census and every linked CSUID, bounded by explicit server transfer-limit checks. Membership is metadata evidence only, not a legal-ownership conclusion, identity/coverage exception, physical support or installation approval. Any unselected member remains explicit.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('complete_permit_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-official-elegant-occupation-permit-membership',refs,result)
 print(rows,flush=True)
if __name__=='__main__':main()

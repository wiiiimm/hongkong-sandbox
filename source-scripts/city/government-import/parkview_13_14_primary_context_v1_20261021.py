"""Read exact government CSUID/occupation-permit records for the Parkview Blocks13/14."""
import sys,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE as API,request
BATCH='government-xl-parkview-13-14-primary-context-v1-20261021';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAP=DOC.parent/'government-xl-parkview-14-companion-projection-v2-20261021'
def main():
 assert not DOC.exists();receipt,pins=authenticate(CAP);selection=CAP/'projection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
 proof=read(selection);assert proof['companion']['uid']=='landsd/255260:0'
 selected=[dict(uid='landsd/253980:0',sourceSHA256=proof['sourceSHA256'],source=dict(building=dict(buildingCSUID='3849513117T20050430'))),dict(uid='landsd/255260:0',sourceSHA256=proof['companionSourceSHA256'],source=dict(building=dict(buildingCSUID=proof['companion']['candidate']['buildingCSUID'])))]
 rows=[];refs=[Path(__file__),CAP/'result.json',selection,HERE.parent/'landsd-territory/source.py'];DOC.mkdir()
 for row in selected:
  uid=row['uid'];csuid=row['source']['building']['buildingCSUID'];data={}
  for kind,layer in [('provider',0),('opRelations',1002),('opStructures',1003)]:
   where="BuildingCSUID='"+csuid+"'"
   if kind=='opStructures':
    ids=sorted({f['attributes']['BuildingStructureID']for f in data['opRelations']['features']})
    if not ids:data[kind]={'features':[],'notRequestedReason':'No source occupation-permit relation'};continue
    where='BuildingStructureID IN('+','.join(str(i)for i in ids)+')'
   raw,req=request(API+'/'+str(layer)+'/query',dict(f='json',where=where,outFields='*',returnGeometry='true'if kind=='provider'else'false',resultRecordCount='1000'))
   response=json.loads(raw);assert 'error'not in response and not response.get('exceededTransferLimit')
   path=DOC/(uid.split('/')[1].replace(':','-')+'-'+kind+'.json');path.write_bytes(raw);save(DOC/(path.name+'.request.json'),req);refs.append(path);data[kind]=response
  assert len(data['provider']['features'])==1
  a=data['provider']['features'][0]['attributes'];assert a['BuildingCSUID']==csuid and a['Status']=='Active'
  rows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],**data))
 save(DOC/'context.json.gz',dict(rows=rows,identityAccepted=False))
 summary=dict(uids=[r['uid']for r in rows],rows=[dict(uid=r['uid'],provider=r['provider']['features'][0]['attributes'],occupationPermits=sorted({f['attributes'].get('OPNo')for f in r['opStructures']['features']if f['attributes'].get('OPNo')}))for r in rows],identityAccepted=False,installationApproved=False)
 module('thei_primary_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-primary-source-pair-context',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()

"""Fresh provider occupation-structure relationships for exact XL component scope.
Links are authoritative relationship evidence, not automatic geometry acceptance.
"""
import json,collections,sys
from run import ROOT,HERE,read,save
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import BASE,request
INPUT=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009';OUT=DOC/'op-relationships'
def query(table,where,label):
 features=[];offset=0
 while True:
  params={'f':'json','where':where,'outFields':'*','returnGeometry':'false','resultRecordCount':'1000','resultOffset':str(offset),'orderByFields':'OBJECTID'};raw,receipt=request(BASE+'/'+str(table)+'/query',params);data=json.loads(raw);assert 'features' in data,data
  OUT.mkdir(parents=True,exist_ok=True);(OUT/(label+'-'+str(offset)+'.json')).write_bytes(raw);save(OUT/(label+'-'+str(offset)+'.request.json'),receipt);features+=data['features']
  if not data.get('exceededTransferLimit'):break
  assert data['features'];offset+=len(data['features'])
 return [f['attributes'] for f in features]
def main():
 live=read(INPUT/'live-georef-research.json.gz')['rows'];csuids=sorted({c['attributes']['BuildingCSUID'] for r in live for c in r['officialCandidates'] if c['sourceCurrentExactCSUIDMatches']});first=[]
 for i in range(0,len(csuids),30):first+=query(1002,'BuildingCSUID IN ('+','.join("'"+x+"'" for x in csuids[i:i+30])+')','source-csuid-'+str(i))
 ids=sorted({r['BuildingStructureID'] for r in first});allrel=[];structures=[]
 for i in range(0,len(ids),40):
  where='BuildingStructureID IN ('+','.join(map(str,ids[i:i+40]))+')';allrel+=query(1002,where,'all-structure-'+str(i));structures+=query(1003,where,'structure-details-'+str(i))
 forms={};by_uid={}
 for t in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
  for b in read(ROOT/'3d-viewer'/t['url'])['buildings']:
   by_uid[b['uid']]=b
   if b.get('buildingCSUID'):forms.setdefault(b['buildingCSUID'],[]).append(b)
 out=[]
 for r in live:
  exact=[c['attributes']['BuildingCSUID'] for c in r['officialCandidates'] if c['sourceCurrentExactCSUIDMatches']];ownids={x['BuildingStructureID'] for x in first if x['BuildingCSUID'] in exact};related=sorted({x['BuildingCSUID'] for x in allrel if x['BuildingStructureID'] in ownids});group=[b for cs in related for b in forms.get(cs,[])];target=by_uid.get(r['uid']);osm=set(target.get('osmRefs',[])) if target else set();direct={b['uid'] for b in by_uid.values() if target and (b['uid']==r['uid'] or osm & set(b.get('osmRefs') or []))};add=[b['uid'] for b in group if b['uid'] not in direct];item={k:r[k] for k in ('uid','sourceKey','sourceSHA256','modelId')};item.update(structureIds=sorted(ownids),relatedCSUIDs=related,currentGroupForms=group,additionalBeyondDirectOSMUids=add,opStructureDetails=[x for x in structures if x['BuildingStructureID'] in ownids],candidateForFullOriginalDiagnostic=bool(add),identityAccepted=False,installationApproved=False);out.append(item)
 save(DOC/'official-op-relationship-research.json.gz',{'rows':out,'sourceRelations':first,'allStructureRelations':allrel,'structures':structures,'qualification':'Explicit current provider BuildingCSUID↔BuildingStructureID (occupation-structure) relationships. A component group is research scope, not approval to union adjacent bodies/suppress unrelated forms or alter originals. Exact source ownership, complete geometry and physical checks remain.'})
 print(json.dumps({'exactSourceCSUIDs':len(csuids),'sourceRelations':len(first),'structureIds':len(ids),'allRelations':len(allrel),'newGroupLeads':[{'uid':r['uid'],'add':r['additionalBeyondDirectOSMUids'],'ids':r['structureIds']} for r in out if r['candidateForFullOriginalDiagnostic']]}),flush=True)
if __name__=='__main__':main()

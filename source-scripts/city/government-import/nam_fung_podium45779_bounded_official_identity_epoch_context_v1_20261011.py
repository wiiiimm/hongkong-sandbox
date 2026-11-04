"""DRAFT two bounded official outline queries/two readers + exact cached source input provenance."""
from pathlib import Path
import sys,json
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import request,BASE
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-nam-fung-podium45779-current-unchanged-owned-identity-v1-20261011';DOC=B/'government-xl-nam-fung-podium45779-bounded-official-identity-epoch-context-v1-20261011'
CACHE='dc13be536a3928765dfc6044e89f7239af45b2fb07e82b08c1fe1a573dd0f9e5';CSUID='3777116537P20060312';UIDS=['landsd/45779:0','landsd/79099:0'];LIMIT=8*1024*1024
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(UIDS,)).fetchall()
def native():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT i.cache_key,i.sheet,i.source_sha,i.input_json,r.result_sha FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key) JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND i.cache_key=%s',(NATIVE_RUN,CACHE)).fetchall()
def main():
 assert not DOC.exists();r=read(OLD/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 before=state();source=native();assert len(source)==1 and source[0][1]=='11-SE-6A';save(DOC/'cached-native-source-input.json',dict(nativeRun=NATIVE_RUN,rows=source,qualification='Actual fixed cached original source input/provenance; not a new source revision or model position.'))
 queries={};errors=[]
 for label,where in [('exact-csuid',"BuildingCSUID='"+CSUID+"'"),('historical-object','OBJECTID=45779')]:
  try:
   reads=[]
   for reader in [1,2]:
    raw,rec=request(BASE+'/0/query',dict(f='json',where=where,outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='100'));assert len(raw)<=LIMIT;data=json.loads(raw);assert isinstance(data.get('features'),list)and not data.get('exceededTransferLimit');reads.append(data);p=DOC/(label+'-reader'+str(reader)+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);save(DOC/(label+'-reader'+str(reader)+'.request.json'),rec)
   assert reads[0]==reads[1],'Official identity/geometry changed between actual readers';queries[label]=reads[0]
  except Exception as ex:errors.append(dict(query=label,errorType=type(ex).__name__,message=str(ex),identityOrAbsenceNotEstablished=True))
 assert native()==source and state()==before;current=read(OLD/'selection.json.gz')['rows'][0]['source']['building'];active=[f for f in queries.get('exact-csuid',{}).get('features',[])if f['attributes'].get('BuildingCSUID')==CSUID]
 save(DOC/'context.json',dict(sourceOnly=True,currentAcceptance=False,sourceGeometryChanges=0,queriedCSUID=CSUID,queriedHistoricalObject=45779,actualOutlineURL=BASE+'/0/query',officialActiveCSUIDRecords=active,historicalObjectRecords=queries.get('historical-object',{}).get('features',[]),uniqueActiveCSUID=len(active)==1,activeObjectIDs=[f['attributes'].get('OBJECTID')for f in active],savedCurrentObjectID=current['objectId'],savedCurrentCSUID=current['buildingCSUID'],queriesComplete=len(queries)==2 and not errors,errors=errors,protectedReviewRowsBeforeAfter=before,evidenceRefs=[ref(Path(__file__)),ref(OLD/'result.json'),ref(OLD/'selection.json.gz'),ref(HERE.parent/'landsd-territory/source.py')],qualification='Bounded authoritative current2D identity/geometry and actual cached3D source-input provenance only. CSUID date characters are not assumed3D acquisition/survey/model revision; source version/field interpretation remains literal. Object renumbering/nullheight/update evidence does not alone resolve original full projection identity. No sourcefit/pose/scale/architectural role/height/contact/acceptance or global absence claim.'))
 print(json.dumps(dict(queriesComplete=len(queries)==2 and not errors,activeCSUIDRecords=len(active),activeObjectIDs=[f['attributes'].get('OBJECTID')for f in active],errors=errors)),flush=True)
if __name__=='__main__':main()

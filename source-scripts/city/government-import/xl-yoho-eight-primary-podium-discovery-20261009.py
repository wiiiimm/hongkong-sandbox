"""Fresh explicit Yoho tower/podium primary relationships and unchanged source lookup."""
import sys,json,gzip
from run import ROOT,HERE,read,save,digest,connect
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request,BASE
BATCH='government-xl-yoho-eight-primary-podium-discovery-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CSUIDS=['2179133649T20050430','2187833636P20050609']
def query(table,where,name,geometry=False):
 params={'f':'json','where':where,'outFields':'*','returnGeometry':'true' if geometry else 'false','outSR':'2326','resultRecordCount':'1000','orderByFields':'OBJECTID'}
 raw,receipt=request(BASE+'/'+str(table)+'/query',params,json_expected=False);decoded=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw;p=DOC/(name+'.json');assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(decoded)
 if raw!=decoded:(DOC/(name+'.provider-original.gz')).write_bytes(raw)
 receipt.update(decodedSHA256=digest(decoded),gzipDecoded=raw!=decoded);save(DOC/(name+'.request.json'),receipt);obj=json.loads(decoded);assert 'features' in obj and not obj.get('exceededTransferLimit');return obj
def main():
 assert not DOC.exists();primary=query(0,'BuildingCSUID IN ('+','.join("'"+v+"'" for v in CSUIDS)+')','exact-current-primary',True);assert {f['attributes']['BuildingCSUID'] for f in primary['features']}==set(CSUIDS) and len(primary['features'])==2
 rel=query(1002,'BuildingCSUID IN ('+','.join("'"+v+"'" for v in CSUIDS)+')','exact-current-structure-relations');ids=sorted({f['attributes']['BuildingStructureID'] for f in rel['features']});structures=query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structure-details') if ids else {'features':[]}
 permits=sorted({f['attributes']['OPNo'] for f in structures['features'] if f['attributes'].get('OPNo')});permit_structures=query(1003,'OPNo IN ('+','.join("'"+p.replace("'","''")+"'" for p in permits)+')','exact-current-permit-structure-context') if permits else {'features':[]}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');models=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key),LATERAL jsonb_array_elements(r.result->'models') m WHERE m->>'modelId' LIKE 'B2187833636%%' OR m->>'modelId'='B217913364901063C0'").fetchall()
 save(DOC/'original-source-lookup.json.gz',{'rows':[{'sourceKey':k+'/'+m['modelId'],'model':m,'sheet':s,'resultSHA256':h} for k,m,s,h in models],'primaryRecords':primary['features'],'exactRelations':rel['features'],'exactStructures':structures['features'],'samePermitContext':permit_structures['features'],'identityAccepted':False,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Exact current primary Tower and Podium identities with provider relationships and original-cache lookup. Same permit context is research only; no actor grouping, geometry ownership or support credit.'})
 print(json.dumps({'primary':len(primary['features']),'structureIds':ids,'permits':permits,'originalModels':[(m['modelId'],m['asset']['sha256'],s) for k,m,s,h in models]}),flush=True)
if __name__=='__main__':main()

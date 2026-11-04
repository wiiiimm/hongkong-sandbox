"""Find exact upper-source identities for the genuine intersecting podium actors."""
import sys,json,uuid,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
BATCH='government-xl-miami-intersecting-upper-source-discovery-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
WANTED={'landsd/37001:0','landsd/176571:0','landsd/179052:0','landsd/201643:0','landsd/203830:0'}
CAUSE=ROOT/'docs/astra-city/government-import/government-xl-miami-neighbour-source-overlap-20261009/whole-source-neighbour-cause-and-elevated-census.json.gz'

def query(name,layer,params):
 raw,rec=request(BASE+'/'+str(layer)+'/query',params);path=DOC/(name+'.json');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);save(DOC/(name+'.request.json'),rec);body=json.loads(raw);assert not body.get('error') and not body.get('exceededTransferLimit');return body

def main():
 assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
 forms={r['uid']:r['currentForm'] for r in read(CAUSE)['rows'] if r['uid'] in WANTED};assert set(forms)==WANTED
 claim=reservations.claim('miami-upper-discovery-'+str(uuid.uuid4()),['building:'+u for u in sorted(WANTED)],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];rows=[]
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY')
   for uid,b in sorted(forms.items()):
    csuid=b['buildingCSUID'];name=uid.split('/')[1].replace(':','-');params={'f':'json','where':"BuildingCSUID='"+csuid+"'",'outFields':'*','returnGeometry':'true','resultRecordCount':'1000'};provider=query(name+'-fresh-provider',0,params);relation=query(name+'-fresh-op-relations',1002,{**params,'returnGeometry':'false'});ids=sorted({f['attributes']['BuildingStructureID'] for f in relation['features']});structures=query(name+'-fresh-op-structures',1003,{'f':'json','where':'BuildingStructureID IN('+','.join(map(str,ids))+')','outFields':'*','returnGeometry':'false','resultRecordCount':'1000'}) if ids else {'features':[]}
    indexed=c.execute('SELECT DISTINCT cache_key,sheet,model_id FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+csuid[:10]+'%')).fetchall();matches=[]
    for key,sheet,model in indexed:
     result_sha,data=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();m=next(m for m in data['models'] if m['modelId']==model);same=[x for x in m['matching']['viewerMatches'] if x.get('buildingCSUID')==csuid and x.get('uid')==uid]
     matches.append({'cacheKey':key,'resultSha':result_sha,'sheet':sheet,'model':m,'exactCSUIDViewerMatches':same,'sameExactSourceIdentity':len(same)==1})
    row={'uid':uid,'currentForm':b,'freshProviderCount':len(provider['features']),'freshProviderAttributes':[f['attributes'] for f in provider['features']],'providerOPRelations':relation,'providerOPStructures':structures,'cachedExactGeoRefSources':matches,'geometryChanges':0,'installationApproved':False};save(DOC/(name+'-source-discovery.json.gz'),row);rows.append(row);assert reservations.heartbeat(lease)['ok'];print({'uid':uid,'name':b.get('name',''),'providerCount':len(provider['features']),'opStructures':[f['attributes'] for f in structures['features']],'indexedSources':[{'modelId':m['model']['modelId'],'exact':m['sameExactSourceIdentity']} for m in matches]},flush=True)
  save(DOC/'complete-upper-source-discovery.json.gz',{'rows':rows,'geometryChanges':0,'installationApproved':False})
  spec=importlib.util.spec_from_file_location('miami_upper_discovery_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'exact-intersecting-miami-and-marina-upper-source-discovery-v1',[Path(__file__),CAUSE],{'uids':sorted(WANTED),'upperCurrentForms':len(rows),'cachedExactSourceMatches':sum(m['sameExactSourceIdentity'] for r in rows for m in r['cachedExactGeoRefSources']),'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'sourceOnlyDiagnostic':True,'identityAccepted':False,'remainingReason':'complete-unchanged-upper-source-acquisition-and-full-family-support-pending','nextStep':'Acquire only uniquely matching complete original upper sources, retain separate permit ownership and all foreign actors, then independently replay whole physical/source/runtime/current neighbour gates. A missing cached match is not proof that government source is unavailable.'})
 finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()

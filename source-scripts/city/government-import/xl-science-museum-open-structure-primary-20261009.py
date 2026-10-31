"""Fresh exact source/provider lineage for Science Museum open-sided neighbour."""
import sys,json,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
BATCH='government-xl-science-museum-open-structure-primary-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PACKET=DOC.parent/'xl-terrain-recovery-20261009-science-open-structure-context/diagnostic.json.gz'
PLAN='https://www.districtcouncils.gov.hk/ytm/doc/2020_2023/en/dc_meetings_doc/22064/YTMDC_2022_5_Annex_TC.pdf'
def query(name,layer,params):
 raw,receipt=request(BASE+'/'+str(layer)+'/query',params);(DOC/(name+'.json')).write_bytes(raw);save(DOC/(name+'.request.json'),receipt);result=json.loads(raw);assert not result.get('error') and not result.get('exceededTransferLimit');return result
def main():
 assert not (DOC/'result.json').exists(),'Completed checkpoint immutable';DOC.mkdir(parents=True,exist_ok=True);packet=read(PACKET);b=packet['foreignCurrentForm'];rows=[]
 for uid,csuid in [('landsd/80343:0','3634918016T20050430'),(b['uid'],b['buildingCSUID'])]:
  name=uid.split('/')[1].replace(':','-');p=query(name+'-building',0,{'f':'json','where':"BuildingCSUID='"+csuid+"'",'outFields':'*','returnGeometry':'true','resultRecordCount':'1000'});assert len(p['features'])==1
  rel=query(name+'-op-relations',1002,{'f':'json','where':"BuildingCSUID='"+csuid+"'",'outFields':'*','returnGeometry':'false','resultRecordCount':'1000'});ids=sorted({f['attributes']['BuildingStructureID'] for f in rel['features']});op=query(name+'-op-structures',1003,{'f':'json','where':'BuildingStructureID IN('+','.join(map(str,ids))+')','outFields':'*','returnGeometry':'false','resultRecordCount':'1000'}) if ids else {'features':[]};sources=[]
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY')
   for key,sheet,mid in c.execute('SELECT DISTINCT cache_key,sheet,model_id FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+csuid[:10]+'%')).fetchall():
    sha,data=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();m=next(m for m in data['models'] if m['modelId']==mid);matches=[v for v in m['matching']['viewerMatches'] if v['uid']==uid and v['buildingCSUID']==csuid];sources.append({'cacheKey':key,'resultSha':sha,'sheet':sheet,'model':m,'exactCurrentSourceMatch':len(matches)==1})
  row={'uid':uid,'buildingCSUID':csuid,'currentProvider':p,'occupationPermitRelations':rel,'occupationPermitStructures':op,'indexedSources':sources,'identityAccepted':False,'physicalAccepted':False};rows.append(row);print({'uid':uid,'provider':p['features'][0]['attributes'],'opStructures':[f['attributes'] for f in op['features']],'models':[{'sheet':r['sheet'],'modelId':r['model']['modelId'],'exact':r['exactCurrentSourceMatch']} for r in sources]},flush=True)
 try:
  raw,receipt=request(PLAN,json_expected=False);assert raw.startswith(b'%PDF');(DOC/'architectural-services-museum-expansion-existing-plans.pdf').write_bytes(raw);save(DOC/'architectural-services-museum-expansion-existing-plans.pdf.request.json',receipt);plan={'path':str((DOC/'architectural-services-museum-expansion-existing-plans.pdf').relative_to(ROOT)),'sha256':digest(raw),'url':PLAN,'qualification':'2022 design proposal includes existing museum and existing courtyard footbridge; exact offending current actor registration remains required.'}
 except Exception as e:plan={'url':PLAN,'acquisitionError':str(e),'identityAccepted':False}
 save(DOC/'fresh-source-and-primary-context.json.gz',{'rows':rows,'plan':plan,'packetPath':str(PACKET.relative_to(ROOT)),'packetSHA256':digest(PACKET.read_bytes()),'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False});spec=importlib.util.spec_from_file_location('science_primary_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'exact-science-museum-open-structure-current-provider-and-primary-v1',[Path(__file__),PACKET],{'uids':[r['uid'] for r in rows],'identityAccepted':False,'physicalAccepted':False,'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'exact-open-sided-original-source-and-current-primary-plan-registration-pending','nextStep':'Acquire exact uniquely matching open-sided original if found; compare complete original bodies/interfaces and independently register existing primary plan, preserving all 63 overlapping faces and raw1.855m2 guard failure.'})
if __name__=='__main__':main()

"""Recover the exact government hospital source collection; no acceptance.

Separate original tower parts may explain apparent podium roof gaps. They are
not grouped, installed, shifted or simplified by this source-only acquisition.
"""
import importlib.util,json,uuid,zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
MODELS={'landsd/193881:0':'B156162982801063C0','landsd/336667:0':'B156072976701063C0','landsd/336668:0':'B155952981701063C0','landsd/336669:0':'B156332976101063C0','landsd/336670:0':'B155832977501063C0','landsd/336671:0':'B156452980301063C0'}
BATCH='government-xl-tuen-mun-main-block-source-collection-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 # An interrupted acquisition can leave checksum-verified range cache files.
 # Reuse those files; never overwrite a completed/fenced diagnostic.
 assert not DOC.exists()
 claim=reservations.claim('hospital-original-collection-'+str(uuid.uuid4()),['building:'+u for u in MODELS],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY')
   rows=c.execute("SELECT r.cache_key,r.result_sha,i.sheet,m FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members n USING(cache_key),LATERAL jsonb_array_elements(r.result->'models') m WHERE n.run_id=%s AND m->>'modelId'=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,list(MODELS.values()))).fetchall()
   assert len(rows)==len(MODELS) and {r[3]['modelId'] for r in rows}==set(MODELS.values()) and len({r[2] for r in rows})==1
   sheet=rows[0][2];prior=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
  cache={p.name.removesuffix('.glb.gz'):p for p in (HERE/'local').rglob('*.glb.gz') if p.parent.name=='assets'}
  source_rows=[]
  for key,sha,sheet,m in rows:
   uid=next(u for u,v in MODELS.items() if v==m['modelId'])
   source_rows.append(dict(uid=uid,modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m)))
  helper=module('hospital_original_reuse','xl-second-pass.py');helper.LOCAL=LOCAL
  retained=[(p.parent/'download.json',read(p.parent/'download.json')) for p in (HERE/'local').rglob(sheet+'.zip') if (p.parent/'download.json').is_file()]
  recovered=helper.source_sheet(sheet,source_rows,prior,cache,retained)
  save(DOC/'selection.json.gz',dict(rows=source_rows,nativeRun=NATIVE_RUN,sourceDirectory=prior,completeOriginalAcquisition=recovered,identityAccepted=False,physicalAccepted=False,installationApproved=False))
  print(json.dumps({'models':len(source_rows),'originalFaces':sum(r['native']['model']['triangles'] for r in source_rows),'exactSourceAssets':recovered['assets'],'aiGeometryModelling':False}),flush=True)
 finally:assert reservations.release(lease)['ok']
 fence=module('hospital_source_collection_fence','xl-popcorn-source-investigations-checkpoints-20261009.py')
 fence.freeze(BATCH,'exact-unchanged-government-hospital-tower-source-collection-v1',[Path(__file__),HERE/'xl-second-pass.py']+[p for p in LOCAL.rglob('*') if p.is_file()],dict(uids=list(MODELS),sourceDownloadOrPackingOnly=True,identityAccepted=False,physicalAccepted=False,requiresAIModelGeometry=False,requiresHumanDecision=False,nextStep='Measure complete unchanged original collection against exact podium/each-own primary, current actors and original exact interfaces. A cached source-match-held Tower remains unaccepted; no common-site grouping waiver.'))
if __name__=='__main__':main()

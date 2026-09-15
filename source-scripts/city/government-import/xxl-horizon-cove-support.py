"""Recover Horizon Cove tower by exact UID from the pinned government source; never AI."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import ROOT,HERE,read,save,connect,digest,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/fourth-pass/horizon-cove';LOCAL=HERE/'local/government-xxl-second-20260911/fourth-pass-horizon-cove';UID='landsd/282761:0'

def main():
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');tile=next(t['url'] for t in manifest['tiles'] if any(b['uid']==UID for b in read(ROOT/'3d-viewer'/t['url'])['buildings']));raw=(ROOT/'3d-viewer'/tile).read_bytes();building=next(b for b in json.loads(raw)['buildings'] if b['uid']==UID);source={'building':building,'tile':tile,'tileSHA256':digest(raw)}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  rows=c.execute("""SELECT i.sheet,r.cache_key,r.result_sha,x FROM astra_modelling.native_stage_members m JOIN astra_modelling.native_stage_results r USING(cache_key) JOIN astra_modelling.native_stage_inputs i USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x WHERE m.run_id=%s AND EXISTS(SELECT 1 FROM jsonb_array_elements(x->'matching'->'viewerMatches') v WHERE v->>'uid'=%s) ORDER BY r.created_at DESC""",(NATIVE_RUN,UID)).fetchall()
 native=[{'sheet':sheet,'cacheKey':key,'resultSha':sha,'model':model} for sheet,key,sha,model in rows];assert len(native)==1
 inputs={'nativeRun':NATIVE_RUN,'rows':[UID],'requestedUids':[UID],'sources':{UID:source},'native':native};save(LOCAL/'tower-inputs.json.gz',inputs)
 result=shape_prepare.prepare(LOCAL/'tower-inputs.json.gz',LOCAL/'tower-source',allow_source=True,workers=1,env_file=ROOT/'.env.modelling');assert len(result['rows'])==1 and not result['errors']
 runtime={**result['rows'][0],'source':source,'native':native[0]};runtime['candidate']['entry'].update(placementReviewed=False,publicationApproved=False);save(LOCAL/'tower-runtime.json',runtime)
 entry=runtime['candidate']['entry'];save(DOC/'support-source-recovery.json',{'uid':UID,'sheet':native[0]['sheet'],'cacheKey':native[0]['cacheKey'],'resultSha':native[0]['resultSha'],'modelId':entry['modelId'],'sourceSHA256':entry['sha256'],'bytes':entry['bytes'],'method':next(iter(result['methods'])),'sourceFallbackEnabled':result['sourceFallbackEnabled'],'aiCalls':0,'geometryChanges':0,'publication':False})
 print(json.dumps(read(DOC/'support-source-recovery.json')))
if __name__=='__main__':main()

"""Restore exact native meshes for overlap hints; never infer assembly membership."""
from pathlib import Path
import sys,json
from run import ROOT,HERE,read,save,connect,digest,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
DOC=ROOT/'docs/astra-city/government-import/government-200-20260911/resolution';LOCAL=HERE/'local/government-198-resolution-20260911/support'
r=read(DOC.parent/'pending-context/results.json.gz');ids={n['uid'] for row in r['rows'] for n in row['overlappingFootprintHints']};sources={}
for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
    raw=(ROOT/'3d-viewer'/tile['url']).read_bytes()
    for b in json.loads(raw)['buildings']:
        if b['uid'] in ids:sources[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(raw)}
with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    found=c.execute('''SELECT i.sheet,r.cache_key,r.result_sha,x FROM astra_modelling.native_stage_members s
        JOIN astra_modelling.native_stage_results r USING(cache_key)
        JOIN astra_modelling.native_stage_inputs i USING(cache_key)
        CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
        WHERE s.run_id=%s AND EXISTS(SELECT 1 FROM jsonb_array_elements(x->'matching'->'viewerMatches') v WHERE v->>'uid'=ANY(%s))''',(NATIVE_RUN,sorted(ids))).fetchall()
e={'nativeRun':NATIVE_RUN,'rows':sorted(sources),'sources':sources,'native':[{'sheet':sheet,'cacheKey':key,'resultSha':sha,'model':m} for sheet,key,sha,m in found]}
save(LOCAL/'inputs.json.gz',e)
print(json.dumps({'supportHints':len(ids),'currentSources':len(sources),'nativeOutcomes':len(found)}),flush=True)
result=shape_prepare.prepare(LOCAL/'inputs.json.gz',LOCAL,allow_source=True,workers=4,env_file=ROOT/'.env.modelling')
save(DOC/'support-source-lookup.json',{'hintUids':sorted(ids),'currentSourceUids':sorted(sources),'nativeOutcomes':[{'sheet':s,'cacheKey':k,'resultSha':h,'modelId':m['modelId'],'state':m['state'],'matchedUids':[v['uid'] for v in m.get('matching',{}).get('viewerMatches',[]) if v['uid'] in ids]} for s,k,h,m in found],'recovered':[r['uid'] for r in result['rows']],'errors':result['errors'],'methods':result['methods'],'aiCalls':0,'publication':False,'qualification':'Exact source availability only. Footprint overlap does not approve assembly membership or ground support.'})

"""Recover exact government support models for the Telford estate assembly; never AI."""
from pathlib import Path
import json,sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import ROOT,HERE,read,save,connect,digest,NATIVE_RUN
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare

DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/third-pass/telford'
LOCAL=HERE/'local/government-xxl-second-20260911/telford-supports'


def main():
    checks=read(DOC/'neighbour-checks.json')
    wanted={r['uid'] for r in checks['rows'] if r['reasons']}|{'landsd/263578:0'}
    neighbour=read(DOC/'neighbour-inputs.json.gz')
    sources={r['building']['uid']:{'building':r['building'],'tile':next(t for t in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles'] if t['id']==r['building']['tile'])['url']} for r in neighbour['rows'] if r['building']['uid'] in wanted}
    for source in sources.values():
        raw=(ROOT/'3d-viewer'/source['tile']).read_bytes();source['tileSHA256']=digest(raw)
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        rows=c.execute("""SELECT i.sheet,r.cache_key,r.result_sha,x FROM astra_modelling.native_stage_members m
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            JOIN astra_modelling.native_stage_inputs i USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') x
            WHERE m.run_id=%s AND EXISTS(SELECT 1 FROM jsonb_array_elements(x->'matching'->'viewerMatches') v WHERE v->>'uid'=ANY(%s))""",(NATIVE_RUN,sorted(wanted))).fetchall()
    native=[{'sheet':sheet,'cacheKey':key,'resultSha':sha,'model':model} for sheet,key,sha,model in rows]
    matched={v['uid'] for item in native for v in item['model'].get('matching',{}).get('viewerMatches',[]) if v['uid'] in wanted}
    inputs={'nativeRun':NATIVE_RUN,'rows':sorted(wanted),'requestedUids':sorted(wanted),'sources':sources,'native':native}
    save(LOCAL/'inputs.json.gz',inputs)
    result=shape_prepare.prepare(LOCAL/'inputs.json.gz',LOCAL,allow_source=True,workers=4,env_file=ROOT/'.env.modelling')
    report={'requested':len(wanted),'exactSourceMatches':len(matched),'recovered':len(result['rows']),'missingUids':sorted(wanted-matched),'errors':result['errors'],'methods':result['methods'],'aiCalls':0,'geometryChanges':0,'publication':False}
    assert report['exactSourceMatches']==report['recovered']==60 and len(report['missingUids'])==1
    save(DOC/'support-source-recovery.json',report)
    print(json.dumps(report))


if __name__=='__main__':main()

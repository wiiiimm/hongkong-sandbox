"""Diagnose 196 frozen XL source-fit holds; never approve or publish a model."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN
from source_sections import horizontal_section

BATCH='government-xl-source-sections-196-20261006'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
CHECKPOINT=ROOT/'docs/astra-city/government-import/government-xl-sustained-231-checkpoint-20261006/result.json'


def inputs():
    checkpoint=read(CHECKPOINT)
    assert checkpoint['jobId']=='e286ee62bea12ba508365c4c0f4b2a6d4993af16473d6ebb6a594dd0a6c6d107'
    held={r['uid']:r for r in checkpoint['rows'] if r['blockerGroup']=='source-footprint-fit'}
    assert len(held)==196
    sources={};contexts={};refs=[CHECKPOINT]
    for count in [100,131]:
        base=ROOT/f'docs/astra-city/government-import/government-xl-sustained-{count}-inputs-20261006'
        for name,target in [('check-selection.json.gz',sources),('context.json.gz',contexts)]:
            path=base/name;refs.append(path)
            target.update({r['uid']:r for r in read(path)['rows'] if r['uid'] in held})
    assert sources.keys()==contexts.keys()==held.keys()
    return checkpoint,held,sources,contexts,refs


def verify_native(con,sources):
    current=dict(con.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',
                            (NATIVE_RUN,list({r['native']['cacheKey'] for r in sources.values()}))))
    assert all(current.get(r['native']['cacheKey'])==r['native']['resultSha'] for r in sources.values())


def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    checkpoint,held,sources,contexts,paths=inputs()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes())
    paths += [Path(__file__),HERE/'source_sections.py',HERE/'test_source_sections.py',manifest]
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in paths]
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute("SELECT result FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(checkpoint['jobId'],)).fetchone()[0]==checkpoint
        verify_native(con,sources)
    spec=importlib.util.spec_from_file_location('section_context',HERE/'xl-final-script-pass.py')
    context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);context.s.LOCAL=LOCAL
    output=[]
    for uid,row in sources.items():
        assert reservations.owns(lease)
        previous=contexts[uid];assert previous['sourceSHA256']==row['sourceSHA256']
        source=ROOT/row['candidate']['path'];assert digest(source.read_bytes())==row['sourceSHA256']
        for tile,sha in previous['neighbourTileHashes'].items():
            assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha,'Source/context changed'
        dest=LOCAL/'assets'/source.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        tri=context.s.glb_triangles(row)
        geometry_sha=digest(tri.astype('<f8').tobytes())
        b=row['source']['building'];base=b.get('baseHeightHKPD');top=b.get('topHeightHKPD')
        if isinstance(base,(int,float)) and isinstance(top,(int,float)) and top>base:
            height=(base+top)/2;section,metrics=horizontal_section(tri,height)
            polygon=context.form_polygon(b);inside=section.intersection(polygon).area
            metrics.update(targetFootprintAreaM2=float(polygon.area),
                sectionInsideTargetFraction=float(inside/section.area) if section.area else None,
                targetCoveredBySectionFraction=float(inside/polygon.area),
                centroidDistanceM=float(section.centroid.distance(polygon.centroid)) if section.area else None)
            fit=bool(section.area and inside/section.area>=.98 and inside/polygon.area>=.95
                     and section.centroid.distance(polygon.centroid)<=1)
            category=('closed-recorded-midheight-fits' if fit and metrics['completeClosedLinework']
                      else 'recorded-midheight-envelope-fits-open-or-ambiguous' if fit
                      else 'recorded-midheight-mismatch-or-empty')
        else:
            metrics={'recordedBaseHeightHKPD':base,'recordedTopHeightHKPD':top,
                     'heightHKPD':None,'qualification':'Missing/invalid source recorded height; no inferred substitute or section.'}
            category='missing-recorded-height-for-section'
        assert digest(tri.astype('<f8').tobytes())==geometry_sha
        # Same numerical comparisons as existing fit criteria, applied only as
        # a diagnostic. The full silhouette gate is retained and remains held.
        result={'uid':uid,'name':row['name'],'sourceSHA256':row['sourceSHA256'],
            'nativeCacheKey':row['native']['cacheKey'],'nativeResultSHA256':row['native']['resultSha'],
            'worldTrianglesSHA256':geometry_sha,'sourceFormSHA256':digest(json.dumps(b,sort_keys=True,separators=(',',':')).encode()),
            'sectionHeightBasis':'midpoint of the exact source form recorded base/top HKPD; not selected for fit',
            'section':metrics,'diagnosticGroup':category,'previousFullProjection':previous['identity'],
            'fullProjectionGateChanged':False,'humanStatus':'held-unknown','requiresAI':False,
            'requiresHumanDecision':False,'publication':False,'modelGeometryChanges':0,
            'nextStep':'Investigate exact source component membership and full 3D geometry outside the declared section; section fit alone never resolves identity, support, terrain or neighbours.'}
        output.append(result);path=DOC/(uid.split('/')[1].replace(':','-')+'.json.gz');save(path,result)
        refs.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())})
        print(json.dumps({'checked':len(output),'total':len(sources),'uid':uid,'group':category}),flush=True)
    payload={'evidenceRefs':refs,'runnerSHA256':digest(Path(__file__).read_bytes()),
             'algorithmSHA256':digest((HERE/'source_sections.py').read_bytes()),'sourceCheckpoint':checkpoint['jobId']}
    stage='original-source-recorded-height-section-diagnostic-v1';jobid=jobs.enqueue(BATCH,stage,payload)
    job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**payload,'batch':BATCH,'jobId':jobid,'rows':output,'sourcesChecked':len(output),
        'diagnosticGroups':dict(Counter(r['diagnosticGroup'] for r in output)),
        'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'activeWorkers':0,'queuedFollowups':0,'widerXLInstalled':50,'widerXLHeld':302,
        'qualification':'Fresh exact geometry evidence to route full-component investigation; no section or diagnostic envelope grants installation or automatic identity credit.'}
    assert digest(manifest.read_bytes())==manifest_sha
    for ref in refs:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        assert reservations._current(con,lease);verify_native(con,sources)
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jobid,'resultVerified':True})
    print(json.dumps({'jobId':jobid,'groups':result['diagnosticGroups'],'newlyInstalled':0,'neonVerified':True}),flush=True)


def start():
    assert not (DOC/'result.json').exists(),'Use a fresh stage; completed evidence is immutable'
    if (LOCAL/'reservation.json').exists():
        assert not reservations.owns(read(LOCAL/'reservation.json')),'Previous worker still owns sources'
    _,held,_,_,_=inputs()
    claim=reservations.claim('codex-xl-section-'+str(uuid.uuid4()),['building:'+uid for uid in held],batch=BATCH)
    assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)


if __name__=='__main__':(owned if sys.argv[1:]==['owned'] else start)()

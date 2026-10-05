"""Measure all connected original faces in 19 held source projections; no approval."""
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from exact_mesh_components import face_components
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row,NATIVE_RUN

BATCH='government-xl-extended-component-fit-20261005'
BASE=ROOT/'docs/astra-city/government-import/government-xl-extended-23-inputs-20261005'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH


def selected():
    contexts={r['uid']:r for r in read(BASE/'context.json.gz')['rows']}
    rows=read(BASE/'check-selection.json.gz')['rows']
    rows=[r for r in rows if read(ROOT/'docs/astra-city/government-import'/
          ('government-xl-extended-'+r['uid'].split('/')[1].split(':')[0]+'-20261005')/'result.json')['reasons']==['source-identity-fit']]
    assert len(rows)==19
    return rows,contexts


def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    rows,contexts=selected()
    spec=importlib.util.spec_from_file_location('fit_source_context',HERE/'xl-final-script-pass.py')
    context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context)
    context.s.LOCAL=LOCAL
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
          for p in [BASE/'context.json.gz',BASE/'check-selection.json.gz']]
    output=[]
    for row in rows:
        assert reservations.owns(lease)
        frozen=contexts[row['uid']]
        for tile,sha in frozen['neighbourTileHashes'].items():
            assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
        source=ROOT/row['candidate']['path']
        assert digest(source.read_bytes())==row['sourceSHA256']
        dest=LOCAL/'assets'/source.name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        triangles=context.s.glb_triangles(row)
        groups=face_components(triangles)
        polygon=context.form_polygon(row['source']['building'])
        parts=[]
        for ids in groups:
            faces=triangles[ids];vertices=np.unique(faces.reshape(-1,3),axis=0)
            projected=context.projection(faces)
            area=float(projected.area)
            inside=float(projected.intersection(polygon).area)
            outside=projected.difference(polygon)
            distances=shapely.distance(shapely.points(vertices[:,[0,2]]),polygon)
            parts.append({'firstFace':int(ids.min()),'triangles':len(ids),'uniqueVertices':len(vertices),
                'worldBounds':[faces.min(axis=(0,1)).tolist(),faces.max(axis=(0,1)).tolist()],
                'projectedAreaM2':area,'projectedInsideTargetM2':inside,'projectedExcessAreaM2':float(outside.area),
                'projectedInsideTargetFraction':inside/area if area else None,
                'maximumVertexDistanceFromTargetM':float(distances.max()),
                'verticesOutsideTarget':int(np.count_nonzero(distances>0)),
                'faceIndicesSHA256':digest(ids.astype('<i8').tobytes())})
        assert sum(p['triangles'] for p in parts)==row['triangles']
        result={'uid':row['uid'],'name':row['name'],'sourceSHA256':row['sourceSHA256'],
            'nativeCacheKey':row['native']['cacheKey'],'nativeResultSHA256':row['native']['resultSha'],
            'exactIdentifiers':frozen['identity']['exactObjectAndCSUID'],
            'previousIdentity':frozen['identity'],'connectedComponents':len(parts),'triangles':row['triangles'],
            'components':parts,'humanStatus':'held-unknown','reasons':['source-identity-fit'],
            'requiresAI':False,'requiresHumanDecision':False,
            'nextStep':'Resolve full original component/footprint coverage against exact source records; no snapping, clipping, identity waiver or inferred architecture.'}
        output.append(result)
        path=DOC/(row['uid'].split('/')[1].split(':')[0]+'.json.gz');save(path,result)
        refs.append({'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())})
        print(json.dumps({'uid':row['uid'],'components':len(parts),'triangles':row['triangles'],
                          'outsideComponents':sum(p['projectedExcessAreaM2']>0 for p in parts)}),flush=True)
    payload={'evidenceRefs':refs,'runnerSHA256':digest(Path(__file__).read_bytes()),
             'componentAlgorithmSHA256':digest((HERE/'exact_mesh_components.py').read_bytes())}
    stage='exact-connected-source-fit-diagnostic-v1';id=jobs.enqueue(BATCH,stage,payload)
    job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==id
    result={**payload,'batch':BATCH,'jobId':id,'rows':output,'primarySources':19,
        'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'activeWorkers':0,'queuedFollowups':0,
        'qualification':'All unchanged world triangles assigned exactly once by identical vertices; horizontal projected area excludes zero-area vertical faces, but vertex distance includes them. Connected components are numeric diagnostics, not semantic buildings, source acceptance or a remodel.'}
    with connect() as con:
        con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        assert reservations._current(con,lease)
        for row in rows:
            actual=con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',
                               (NATIVE_RUN,row['native']['cacheKey'])).fetchone()
            assert actual and actual['result_sha']==row['native']['resultSha']
        assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),id,job['owner'],job['token'])).rowcount==1
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(id,)).fetchone()[0]==result
    save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':id,'resultVerified':True})
    print(json.dumps({'models':19,'newlyInstalled':0,'jobId':id,'neonVerified':True}),flush=True)


def start():
    assert not DOC.exists(),'Completed evidence is immutable'
    rows,_=selected()
    claim=reservations.claim('codex-xl-component-fit-'+str(uuid.uuid4()),
                             ['building:'+r['uid'] for r in rows],batch=BATCH);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run',
                    '--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)


if __name__=='__main__': (owned if sys.argv[1:] == ['owned'] else start)()

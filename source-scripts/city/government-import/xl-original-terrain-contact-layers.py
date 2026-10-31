"""Inspect unchanged government terrain layers at exact recorded contact failures.

Diagnostic only: no surface selection, model edits, review changes or acceptance.
"""
import argparse, importlib.util, json, subprocess, sys, uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest, reservations, jobs, connect, Jsonb, dict_row

def ref(p):
    return {'path': str(p.relative_to(ROOT)), 'sha256': digest(p.read_bytes())}

def owned(a, doc, local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    previous=ROOT/a.previous;prior=read(previous/'result.json');sync=read(previous/'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId']==prior['jobId']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
    diagnostic=read(ROOT/a.diagnostic)
    assert diagnostic['diagnosticOnly'] and not diagnostic['publication']
    assert diagnostic['runnerSHA256']==digest((HERE/'xl-cached-runtime-contact-diagnostic.mjs').read_bytes())
    geometry=diagnostic['geometry'];assert ref(ROOT/geometry['path'])==geometry
    for path,sha in diagnostic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    assert len(diagnostic['rows'])==1
    row=diagnostic['rows'][0];assert row['uid']==prior['uid'] and row['sourceSHA256']==prior['sourceSHA256'] and row['failed']
    terrain=read(previous/'terrain.json');pieces=[]
    spec=importlib.util.spec_from_file_location('original_terrain_layers',HERE/'xl-second-pass.py')
    decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=local
    for r in terrain['sourceFiles']:
        assert ref(ROOT/r['path'])==r
        if r['path'].endswith('.gltf'):pieces.append(decoder.terrain_triangles(ROOT/r['path']))
    assert pieces,'Original terrain geometry required'
    triangles=np.concatenate(pieces);polygons=shapely.polygons(triangles[:,:,[0,2]])
    keep=shapely.area(polygons)>1e-10;triangles=triangles[keep];polygons=polygons[keep];tree=shapely.STRtree(polygons)
    rows=[]
    for sample in row['failed']:
        x,y,z=sample['point'];heights=[]
        for i in tree.query(shapely.Point(x,z).buffer(1e-7)):
            p,q,r=triangles[i];u,v=np.linalg.solve(np.array([[p[0]-r[0],q[0]-r[0]],[p[2]-r[2],q[2]-r[2]]]),np.array([x-r[0],z-r[2]]))
            if min(u,v,1-u-v)<-1e-7:continue
            heights.append(float(u*p[1]+v*q[1]+(1-u-v)*r[1]))
        rows.append({'point':sample['point'],'runtimeGround':sample['ground'],'originalGovernmentTerrainHeights':sorted(set(heights)),
                     'originalFacesBelowExistingClearance':[h for h in heights if y-h>=-.5]})
    save(doc/'layer-checks.json.gz',{'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'rows':rows,'originalTerrainFaces':len(triangles),
         'pointsWithOriginalLowerSurface':sum(bool(r['originalFacesBelowExistingClearance']) for r in rows),'sourceFiles':terrain['sourceFiles'],
         'previousResult':ref(previous/'result.json'),'contactDiagnostic':ref(ROOT/a.diagnostic),'geometry':geometry,'diagnosticOnly':True,'publication':False})
    refs=[ref(doc/'layer-checks.json.gz'),ref(Path(__file__)),ref(HERE/'xl-second-pass.py')]
    payload={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'evidenceRefs':refs}
    stage='exact-original-terrain-contact-layers-diagnostic-v1';jid=jobs.enqueue(a.batch,stage,payload)
    job=jobs.claim(a.batch,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
    result={**payload,'batch':a.batch,'jobId':jid,'failedPoints':len(rows),'pointsWithOriginalLowerSurface':sum(bool(r['originalFacesBelowExistingClearance']) for r in rows),
            'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'diagnosticOnly':True}
    with connect() as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
        assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
    save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps(result),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['previous','diagnostic','batch']:p.add_argument('--'+k,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args();assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    if a.owned:return owned(a,doc,local)
    assert not doc.exists(),'Fresh diagnostic only';uid=read(ROOT/a.previous/'result.json')['uid']
    claim=reservations.claim('codex-xl-original-terrain-layers-'+str(uuid.uuid4()),['building:'+uid],batch=a.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()

"""Private existing source-floor kernel trials for Peng Chau's largest nine.

Exact cached original geometry stays immutable. No approval, viewer changes or
uploads; full identity/current-neighbour/browser/publication checks remain.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid
import numpy as np
import shapely
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from retained_native_floor_domains_v1_20261102 import inset
from run import connect,reservations,jobs,dict_row

BATCH='government-islands-peng-two-largest-exact-floor-probe-20261107-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PARENT='government-islands-peng-chau-largest-first-20261107-v1-direct-001'


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    source=ROOT/'docs/astra-city/government-import'/PARENT/'selection.json.gz';selected=read(source);rows=selected['rows'][:2];selected['manifestSHA256']=sha(ROOT/'3d-viewer/city/data/manifest.json')
    assert len(rows)==2 and selected['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    if not a.owned:
        assert not DOC.exists()and not LOCAL.exists()
        claim=reservations.claim('codex-peng-largest-floor-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows]+['terrain:city/data/terrain.json'],batch=BATCH,ttl=3600);assert claim['ok'],'Existing owner; no takeover'
        receipt=json.loads(json.dumps(claim['reservation'],default=str));save(LOCAL/'reservation.json',receipt)
        save(DOC/'selection.json.gz',{**selected,'rows':rows})
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',LOCAL/'reservation.json','--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
        return
    receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
    pins={rel(source):sha(source),rel(Path(__file__)):sha(Path(__file__)),rel(HERE/'islands_source_floor_geometry.mjs'):sha(HERE/'islands_source_floor_geometry.mjs')}
    for path in ['retained_native_floor_domains_v1_20261102.py','source_floor_return_with_existing_seabed_v1_20261102.py','bounded_original_upward_floor_return_v3_20261102.py','exact_packed_world_geometry_v2_20261103.py']:
        pins[rel(HERE/path)]=sha(HERE/path)
    subprocess.run(['node',HERE/'islands_source_floor_geometry.mjs','--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(HERE/'accepted'/PARENT),'--out',rel(DOC/'capture-metrics.json'),'--geometry-out',rel(LOCAL/'geometry.json.gz')],cwd=ROOT,check=True)
    captured=read(LOCAL/'geometry.json.gz');geometry={r['uid']:r for r in captured['rows']};assert set(geometry)=={r['uid']for r in rows}
    pins.update(captured['inputHashes']);pins[rel(LOCAL/'geometry.json.gz')]=sha(LOCAL/'geometry.json.gz')
    previous={r['uid']:r for r in read(ROOT/'docs/astra-city/government-import'/PARENT/'metrics.json')['rows']}
    for row in read(DOC/'capture-metrics.json')['rows']:
        # Expanded observation bounds must leave existing source metrics exact.
        assert not row.get('error')
        for key in ['minSurfaceGap','minLowGap','maxLowGap','maxSamplerDelta','missingTerrain','sourceSHA256']:
            assert row[key]==previous[row['uid']][key],(row['uid'],key)
    old=module('peng_floor_source_audit',HERE/'resolve-pass.py');outcomes=[]
    for selected_row in rows:
        uid=selected_row['uid'];entry=selected_row['candidate']['entry'];asset=ROOT/selected_row['candidate']['path'];assert sha(asset)==entry['sha256'];pins[rel(asset)]=entry['sha256']
        tri=decode_original_world_triangles(asset.read_bytes());g=geometry[uid];assert len(tri)==entry['triangles']and g['sourceSHA256']==entry['sha256']
        ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);literal=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert tri.shape==literal.shape
        points=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1);polys=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polys)>1e-12
        heights=old.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),ground[valid],shapely.STRtree(polys[valid])).reshape(-1,4)
        gaps=points[:,:,1]-heights;normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=normals[:,1]>.25*np.linalg.norm(normals,axis=1)
        previous_grade=ROOT/'docs/astra-city/government-import/government-islands-peng-two-largest-grade-probe-20261107-v1/results.json.gz'
        grade=read(previous_grade);sync=read(previous_grade.parent/'neon-sync.json')
        with connect()as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert sync['exactResultMatch'] and db.execute("SELECT result->'evidence' FROM astra_modelling.jobs WHERE id=%s AND status='complete'",(sync['jobId'],)).fetchone()[0]=={'path':rel(previous_grade),'sha256':sha(previous_grade)}
        pins[rel(previous_grade)]=sha(previous_grade)
        prior_capture=read(HERE/'local'/previous_grade.parent.name/'geometry.json.gz');old_geometry=next(r for r in prior_capture['rows']if r['uid']==uid)
        assert old_geometry==g,'Exact source/ground capture changed; repeat the finite source proof first'
        cases=[r for r in grade['rows']if r['uid']==uid and r['terrain']=='current'];assert len(cases)==2 and {r['mode']for r in cases}=={'original','literal'}
        ids=np.asarray(sorted(set().union(*(set(r['ordinaryNonWallFailures'])for r in cases))),dtype=int)
        assert all(abs(normals[i,1])>.25*np.linalg.norm(normals[i])for i in ids),'Only exact failed non-wall original surfaces define the private return'
        result={'uid':uid,'sourceSHA256':entry['sha256'],'sourceTriangles':len(tri),'sourceRendererMaximumCoordinateDifferenceM':float(np.max(np.abs(tri-literal))),'nominatedExactNegativeNonWallSourceFaceIndices':ids.tolist(),'sourceGeometryChanges':0,'publication':False,'requiresAI':False,'requiresUserDecision':False}
        try:
            assert len(ids),'No exact negative non-wall surfaces nominated'
            after,proof=inset(ground,tri[ids]);lo,hi=np.asarray(entry['worldBounds']);outer=shapely.from_wkt(proof['outerWKT']);assert shapely.box(lo[0]-5,lo[2]-5,hi[0]+5,hi[2]+5).covers(outer)
            # Preserve full production POSITION/index/low-rim sampling unchanged.
            samples,bottom=old.sample_points(g);audit=old.audit_native(samples,bottom,after)
            candidate=LOCAL/(uid.split('/')[1]+'.json.gz');save(candidate,{'position':after.reshape(-1).tolist(),'index':list(range(len(after)*3)),'proof':proof,'sourceFaceIndices':ids.tolist(),'sourceSHA256':entry['sha256']})
            result.update(state='private-self-contact-pass'if audit['passed']else'private-self-contact-failed',selfContactAudit=audit,candidate={'path':rel(candidate),'sha256':sha(candidate)},terrainTriangles=len(after),changedTerrainFaces=len(proof['changedTerrainFaceIndices']),fullNeighbourChecks=False,physicalAcceptance=False)
        except (AssertionError,ValueError)as error:
            result.update(state='private-constructor-or-source-precheck-failed',reason=str(error),physicalAcceptance=False)
        outcomes.append(result);save(DOC/'partial.json',{'rows':outcomes,'publication':False});print({'uid':uid,'state':result['state'],'floorFaces':len(ids)},flush=True)
    for path,h in pins.items():assert sha(ROOT/path)==h,path
    report={'models':len(rows),'rows':outcomes,'inputHashes':pins,'sourceGeometryChanges':0,'modelReviewWrites':0,'uploads':False,'publication':False,'qualification':'Existing 1m core/3m return/0.05m source-plane kernel with exact failed non-wall facets, including downward authored surfaces. Private self-contact test only; original winding/bytes unchanged. No source identity, full affected-neighbour, runtime/browser or publication approval.'};output=DOC/'results.json.gz';save(output,report);payload={'path':rel(output),'sha256':sha(output)};jobid=jobs.enqueue(BATCH,'islands-source-floor-private-diagnostic-v1',payload);job=jobs.claim(BATCH,receipt['owner'],['islands-source-floor-private-diagnostic-v1'],lease_seconds=600,job_ids=[jobid]);assert job and job['id']==jobid
    result={**report,'jobId':jobid,'evidence':payload}
    with connect()as db:
        db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));group=reservations._current(db,receipt);assert group and {'building:'+r['uid']for r in rows}<=set(group['resources'])
        for path,h in pins.items():assert sha(ROOT/path)==h,path
        assert jobs.finish(job,result=result,connection=db)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
    save(DOC/'neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(rows),'modelReviewWrites':0});print({'complete':True,'models':len(rows),'jobId':jobid},flush=True)


if __name__=='__main__':main()

"""Exact finite-facet/grade diagnostics for the two largest Peng originals.

Existing coverage, finite-column, cap-path and upper-ground kernels only. No
source edits, threshold changes, role approval, terrain publication or uploads.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid
import numpy as np
from islands_direct_stage import ROOT,HERE,read,save,sha,rel
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from exact_original_projection_coverage_20261009 import exact_coverage
from exact_original_triangle_pair_column_gap_20261010 import verify as pair_gap
from original_bound_facet_wall_context_20261010 import down,canonical
from original_strict_clear_cap_wall_paths_20261009 import verify as cap_paths
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from retained_native_floor_domains_v1_20261102 import inset
from run import connect,reservations,jobs,dict_row

BATCH='government-islands-peng-two-largest-grade-probe-20261107-v1'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PARENT='government-islands-peng-chau-largest-first-20261107-v1-direct-001'


def analyze(task):
    uid,mode,terrain_kind,tri,ground=task
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);wall=(length>0)&(np.abs(normals[:,1])<=.25*length)
    xz=ground[:,:,[0,2]];lo=xz.min(axis=1);hi=xz.max(axis=1);contexts=[];finite=[];uncovered=[];nonwall=[]
    for i,face in enumerate(tri):
        bounds=face[:,[0,2]];ids=np.flatnonzero(np.all(hi>=bounds.min(axis=0),axis=1)&np.all(lo<=bounds.max(axis=0),axis=1))
        coverage=exact_coverage(face,ground);bound=None;pairs=[]
        if len(ids):
            bound=F(float(face[:,1].min()))-F(float(ground[ids,:,1].max()))
            if bound<F(-1,2)and not wall[i]:
                values=[]
                for j in ids:
                    proof=pair_gap(face,ground[int(j)]);pairs.append({'groundFace':int(j),'proof':proof})
                    if proof['exactMinimumFiniteColumnGapM']is not None:values.append(F(proof['exactMinimumFiniteColumnGapM']))
                bound=min(values)if values else None
        if not coverage['exactProjectionCovered']or bound is None:uncovered.append(i)
        if bound is not None and bound<F(-1,2)and not wall[i]:nonwall.append(i)
        exposure=F(float(face[:,1].max()))-F(float(ground[ids,:,1].max()))if len(ids)else None
        contexts.append({'sourceFace':i,'groundProjectionCovered':coverage['exactProjectionCovered'],'minimum':{'minimumGapM':down(bound),'qualification':'Conservative exact finite lower bound'}if bound is not None else None,'maximumObservedGapM':down(exposure)if exposure is not None else None})
        finite.append({'sourceFace':i,'projectionCoverage':coverage,'allAABBCandidateGroundFaces':list(map(int,ids)),'exactCertifiedLowerClearanceM':str(bound)if bound is not None else None,'pairedFiniteProofs':pairs})
        if(i+1)%200==0:print({'uid':uid,'mode':mode,'terrain':terrain_kind,'faces':i+1,'total':len(tri)},flush=True)
    binding={'completeOriginalWorldTrianglesSHA256':hashlib.sha256(tri.astype('<f8').tobytes()).hexdigest(),'completeCurrentFacetContextsSHA256':canonical(contexts),'exactOriginalContactListSHA256':canonical([])}
    paths=None;interfaces=[]
    if not uncovered and not nonwall:
        paths=cap_paths(tri,contexts,[],expected_binding=binding,current_binding=binding)
        interfaces=exact_upper_ground_interfaces(tri,paths['affectedOriginalWallFaces'],ground)
    result={'uid':uid,'mode':mode,'terrain':terrain_kind,'faces':len(tri),'uncoveredFaces':uncovered,'ordinaryNonWallFailures':nonwall,'allAffectedHaveCapPaths':paths['allAffectedHavePaths']if paths else False,'rawExposureFailures':paths['rawExposureFailures']if paths else None,'gradeContactFaces':sorted({r['sourceFace']for r in interfaces}),'affectedWallFaces':paths['affectedOriginalWallFaces']if paths else None,'sourceGeometryChanges':0,'roleAccepted':False,'physicalAcceptance':False,'publication':False}
    output=DOC/(uid.split('/')[1]+'-'+mode+'-'+terrain_kind+'.json.gz');save(output,{'summary':result,'binding':binding,'completeDrawnGroundSHA256':hashlib.sha256(ground.astype('<f8').tobytes()).hexdigest(),'contexts':contexts,'finiteProofs':finite,'capPaths':paths,'actualUpperGroundInterfaces':interfaces});return {**result,'evidence':{'path':rel(output),'sha256':sha(output)}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--owned',action='store_true');a=p.parse_args()
    oldpath=ROOT/'docs/astra-city/government-import'/PARENT/'selection.json.gz';old=read(oldpath)
    if not a.owned:
        assert not DOC.exists()and not LOCAL.exists();rows=old['rows'][:2];assert [r['uid']for r in rows]==['landsd/190234:0','landsd/192052:0']
        manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=sha(manifest)
        for row in rows:
            path=ROOT/'3d-viewer'/row['source']['tile'];actual=next(r for r in read(path)['buildings']if r['uid']==row['uid']);assert actual==row['source']['building'];row['source']['tileSHA256']=sha(path)
        claim=reservations.claim('codex-peng-exact-grade-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows]+['terrain:city/data/terrain.json'],batch=BATCH,ttl=3600);assert claim['ok'],'Existing owner; no takeover'
        receipt=json.loads(json.dumps(claim['reservation'],default=str));save(LOCAL/'reservation.json',receipt);save(DOC/'selection.json.gz',{**old,'rows':rows,'manifestSHA256':mh})
        subprocess.run([sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',LOCAL/'reservation.json','--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
    receipt=read(LOCAL/'reservation.json');assert reservations.owns(receipt)
    selected=read(DOC/'selection.json.gz');assert selected['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    subprocess.run(['node',HERE/'islands_source_floor_geometry.mjs','--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(HERE/'accepted'/PARENT),'--out',rel(DOC/'capture-metrics.json'),'--geometry-out',rel(LOCAL/'geometry.json.gz')],cwd=ROOT,check=True)
    captured=read(LOCAL/'geometry.json.gz');by_uid={r['uid']:r for r in captured['rows']};assert len(by_uid)==2
    pins={**captured['inputHashes'],rel(Path(__file__)):sha(Path(__file__)),rel(HERE/'islands_source_floor_geometry.mjs'):sha(HERE/'islands_source_floor_geometry.mjs'),rel(LOCAL/'geometry.json.gz'):sha(LOCAL/'geometry.json.gz')}
    for name in ['exact_original_projection_coverage_20261009.py','exact_original_triangle_pair_column_gap_20261010.py','original_strict_clear_cap_wall_paths_20261009.py','exact_original_upper_ground_interfaces_20261009.py','retained_native_floor_domains_v1_20261102.py']:pins[rel(HERE/name)]=sha(HERE/name)
    tasks=[]
    for row in selected['rows']:
        uid=row['uid'];asset=ROOT/row['candidate']['path'];assert sha(asset)==row['candidate']['entry']['sha256'];pins[rel(asset)]=sha(asset);original=decode_original_world_triangles(asset.read_bytes());g=by_uid[uid];literal=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
        assert original.shape==literal.shape and len(original)==row['candidate']['entry']['triangles']
        terrains=[('current',ground)]
        old_probe=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-largest-nine-floor-probe-20261107-v1/results.json.gz';prior=next(r for r in read(old_probe)['rows']if r['uid']==uid)
        if prior.get('candidate'):
            # Replay the same existing kernel against fresh exact current ground.
            ids=prior['nominatedOriginalUpwardFloorFaceIndices'];after,proof=inset(ground,original[ids]);candidate=LOCAL/(uid.split('/')[1]+'-replayed-floor.json.gz');save(candidate,{'position':after.reshape(-1).tolist(),'proof':proof,'sourceFaceIndices':ids,'sourceSHA256':row['candidate']['entry']['sha256']});pins[rel(candidate)]=sha(candidate);terrains.append(('private-source-floor',after))
        pins[rel(old_probe)]=sha(old_probe)
        for terrain_kind,terrain in terrains:
            for mode,tri in [('original',original),('literal',literal)]:tasks.append((uid,mode,terrain_kind,tri,terrain))
    results=[]
    with ProcessPoolExecutor(max_workers=2)as pool:
        for result in pool.map(analyze,tasks):results.append(result);save(DOC/'partial.json',{'rows':results,'publication':False});print(result,flush=True)
    for path,h in pins.items():assert sha(ROOT/path)==h,path
    report={'models':2,'cases':len(results),'rows':results,'inputHashes':pins,'sourceGeometryChanges':0,'modelReviewWrites':0,'uploads':False,'publication':False,'qualification':'Exact original/literal finite coverage, non-wall clearance, clear-cap paths and actual upper-ground interfaces only. No source role/identity, full affected-neighbour, four-stream, support, runtime/browser or publication approval.'};output=DOC/'results.json.gz';save(output,report);payload={'path':rel(output),'sha256':sha(output)};jobid=jobs.enqueue(BATCH,'islands-exact-source-grade-diagnostic-v1',payload);job=jobs.claim(BATCH,receipt['owner'],['islands-exact-source-grade-diagnostic-v1'],lease_seconds=600,job_ids=[jobid]);assert job and job['id']==jobid;result={**report,'jobId':jobid,'evidence':payload}
    with connect()as db:
        db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(db,receipt)
        for path,h in pins.items():assert sha(ROOT/path)==h,path
        assert jobs.finish(job,result=result,connection=db)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==('complete',result)
    save(DOC/'neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':2,'cases':len(results),'modelReviewWrites':0})


if __name__=='__main__':main()

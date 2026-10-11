"""Scan remaining exact originals for complete current direct shared-OSM footprint groups.

Diagnostics only: no model edits, acceptance, permanent rejection or publication.
The full original projection is measured, never triangle count or a roof proxy.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row,NATIVE_RUN
from original_source_ownership import graph_reasons,document
from government_georef_cell_identity import geographic_cell


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    frozen=read(doc/'inputs.json');count=read(ROOT/frozen['count']['path']);prior=read(ROOT/frozen['dispositions']['path'])
    for item in [frozen['count'],frozen['dispositions'],frozen['runner']]:assert ref(ROOT/item['path'])==item
    remaining={r['sourceKey']:r for r in count['rows'] if not r['installedVerified'] and r.get('uid') not in args.exclude_uid and (not args.only_uid or r.get('uid') in args.only_uid)}
    old={r['sourceKey']:r for r in prior['rows']};assert remaining.keys()<=old.keys()
    previous_groups={}
    for item in frozen['previousGroupMeasurements']:
        assert ref(ROOT/item['path'])==item
        previous_groups.update({r['sourceKey']:r for r in read(ROOT/item['path'])['rows']})
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        native_rows=con.execute("SELECT cache_key,result_sha,m FROM astra_modelling.native_stage_results, LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",(sorted({r['sourceKey'].split('/')[0] for r in remaining.values()}),sorted({old[k]['modelId'] for k in remaining}))).fetchall()
        native_models={}
        native={}
        for key,result_sha,model in native_rows:
            source_key=key+'/'+model['modelId']
            assert source_key not in native_models
            native_models[source_key]=model;native[key]=result_sha
        assert remaining.keys()<=native_models.keys()
    cache={}
    for path in sorted((HERE/'local').rglob('*.glb.gz')):
        if path.stem.endswith('.glb'):cache.setdefault(path.name[:-7],path)
    decoder=module('group_original_decoder','xl-second-pass.py');decoder.LOCAL=local
    final=module('group_current_forms','xl-final-script-pass.py');outcomes=[];tile_hashes={}
    stage='remaining-original-direct-shared-osm-group-diagnostic-v1'
    payload={'input':ref(doc/'inputs.json'),'sourceKeys':sorted(remaining)}
    jid=jobs.enqueue(args.batch,stage,payload);job=jobs.claim(args.batch,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
    try:
        for source_key,current in sorted(remaining.items()):
            earlier=old[source_key];uid=current['uid'];sha=current['indexedSourceSHA256'];key=source_key.split('/')[0]
            assert native[key]==earlier['nativeResultSHA256']==current.get('nativeResultSHA256',earlier['nativeResultSHA256'])
            assert earlier['sourceSHA256']==sha
            model=native_models[source_key];assert model['asset']['sha256']==sha
            result={'uid':uid,'sourceKey':source_key,'sourceSHA256':sha,'modelId':earlier['modelId'],'nativeResultSHA256':native[key],
                'identityAccepted':False,'installationApproved':False,'modelGeometryChanges':0,'candidate':False}
            path=cache.get(sha)
            if path is None:
                result.update(state='source-cache-missing',reasons=['exact-original-cache-unavailable'])
            else:
                raw=path.read_bytes();assert digest(raw)==sha;result['original']=ref(path)
                result['graphReasons']=graph_reasons(document(raw),earlier['modelId'],model['triangles'])
                if uid is None:
                    result.update(state='no-current-source-form',reasons=['exact-official-and-viewer-route-unresolved'])
                else:
                    lo,hi=model['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);targets=[b for b,_,_ in forms if b['uid']==uid]
                    for _,_,tile in forms:tile_hashes[tile]=digest((ROOT/'3d-viewer'/tile).read_bytes())
                    if len(targets)!=1:
                        result.update(state='no-unique-current-target-in-original-bounds',reasons=['current-target-geometry-route-unresolved'])
                    else:
                        target=targets[0];parent=target.get('parent');refs_osm=set(target.get('osmRefs') or []);group=[b for b,_,_ in forms if b['uid']==uid or refs_osm & set(b.get('osmRefs') or [])]
                        result['groupUids']=sorted(b['uid'] for b in group);result['groupForms']=group
                        previous=previous_groups.get(source_key)
                        if previous and previous.get('sourceSHA256')==sha and sorted(previous.get('groupForms',[]),key=lambda b:b['uid'])==sorted(group,key=lambda b:b['uid']):
                            result.update(state='unchanged-group-already-checked',reasons=previous.get('reasons',[]),previousState=previous['state'],previousMeasurements=previous.get('measures'),unchangedMeasurementReused=True)
                        elif len(group)==1:
                            result.update(state='no-additional-direct-shared-osm-footprint',reasons=['complete-component-group-does-not-expand-target'])
                        else:
                            asset=local/'assets'/(sha+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,asset)
                            row={'sourceSHA256':sha,'modelId':earlier['modelId'],'triangles':model['triangles'],'native':{'model':model}}
                            tri=decoder.glb_triangles(row);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
                            shape=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:]) for b in group]);others=shapely.union_all([p for b,p,_ in forms if b['uid'] not in set(result['groupUids'])])
                            measures={'targetCoveredBySourceProjection':float(shape.intersection(projection).area/shape.area),
                                'sourceExcessMaximumDistanceFromTargetM':float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),shape).max()),
                                'sourceExcessCoveredByUnrelatedFormsM2':float(projection.difference(shape).intersection(others).area)}
                            reasons=list(result['graphReasons'])
                            for k,lower,upper in [('targetCoveredBySourceProjection',.95,1.000000001),('sourceExcessMaximumDistanceFromTargetM',0,10),('sourceExcessCoveredByUnrelatedFormsM2',0,1)]:
                                if not lower<=measures[k]<=upper:reasons.append('complete-group-spatial-bound:'+k)
                            try:
                                cell=geographic_cell(earlier['modelId'],target['buildingCSUID'],target['structureType'])
                                if not Polygon(target['rings'][0],target['rings'][1:]).covers(cell):reasons.append('current-original-target-whole-georef-cell')
                                if not projection.covers(cell):reasons.append('original-projection-whole-georef-cell')
                            except (ValueError,KeyError):reasons.append('source-georef-type')
                            result.update(state='candidate-for-official-complete-group-verification' if not reasons else 'complete-group-still-fails',reasons=sorted(set(reasons)),measures=measures,candidate=not reasons,
                                worldTrianglesSHA256=digest(tri.astype('<f8').tobytes()))
            outcomes.append(result)
            save(doc/'progress.json',{'checked':len(outcomes),'total':len(remaining),'candidates':[r['uid'] for r in outcomes if r['candidate']],'lastUid':uid,'jobId':jid,'publication':False})
            save(local/'partial-outcomes.json.gz',{'rows':outcomes})
            assert reservations.owns(lease)
            with connect() as con:
                assert con.execute("UPDATE astra_modelling.jobs SET lease_until=clock_timestamp()+interval '1 hour',updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(jid,job['owner'],job['token'])).rowcount==1
            print(json.dumps({'checked':len(outcomes),'total':len(remaining),'uid':uid,'state':result['state'],'candidate':result['candidate']}),flush=True)
        for tile,sha in tile_hashes.items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
        save(doc/'outcomes.json.gz',{'rows':outcomes,'sourceTileHashes':tile_hashes})
        refs=[ref(doc/'inputs.json'),ref(doc/'outcomes.json.gz'),ref(Path(__file__)),*frozen['previousGroupMeasurements']]
        refs += [{'path':'3d-viewer/'+p,'sha256':sha} for p,sha in tile_hashes.items()]
        refs += [r['original'] for r in outcomes if r.get('original')]
        from collections import Counter
        result={**payload,'jobId':jid,'batch':args.batch,'checked':len(outcomes),'counts':dict(Counter(r['state'] for r in outcomes)),
            'candidateUids':[r['uid'] for r in outcomes if r['candidate']],'evidenceRefs':refs,
            'inputManifestSHA256':count['manifestSHA256'],'completionManifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),
            'newlyInstalled':0,'publication':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'identityAccepted':False,
            'qualification':'Diagnostic direct shared-OSM footprint scan, retaining separate OSM parents and every current form. All original bytes/root graph/poses and complete measured projections are retained. Candidates require authoritative full component ownership and dedicated current identity/physical/runtime/browser/publication checks. Failures neither establish corruption nor permanent impossibility; Unchanged exact groups reuse prior measurements without rerunning them; newly expanded direct shared-OSM groups need fresh official ownership and all physical acceptance gates. No component suppression approval.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for item in refs:assert ref(ROOT/item['path'])==item
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'counts':result['counts'],'candidateUids':result['candidateUids'],'neonVerified':True}),flush=True)
    except Exception as error:
        jobs.finish(job,error=str(error));raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--count',required=True);p.add_argument('--batch',required=True);p.add_argument('--exclude-uid',action='append',default=[]);p.add_argument('--only-uid',action='append',default=[]);p.add_argument('--owned',action='store_true');args=p.parse_args()
    assert args.batch.startswith('government-xl-') and Path(args.batch).name==args.batch
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    if args.owned:return owned(args,doc,local)
    assert not doc.exists() and not local.exists(),'Fresh complete-group scan only'
    count=read(ROOT/args.count);assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==count['manifestSHA256']
    remaining=[r for r in count['rows'] if not r['installedVerified'] and r.get('uid') not in args.exclude_uid and (not args.only_uid or r.get('uid') in args.only_uid)]
    claim=reservations.claim('codex-xl-full-group-scan-'+str(uuid.uuid4()),['native-model:'+r['sourceKey'] for r in remaining],batch=args.batch,ttl=3600);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    save(doc/'inputs.json',{'count':ref(ROOT/args.count),'dispositions':ref(ROOT/'docs/astra-city/government-import/government-xl-held-second-pass-dispositions-20261008/dispositions.json.gz'),'runner':ref(Path(__file__)),'previousGroupMeasurements':[ref(ROOT/'docs/astra-city/government-import'/name/'outcomes.json.gz') for name in ['government-xl-322-complete-footprint-group-scan-v2-20261008','government-xl-two-lantau-complete-footprint-group-scan-20261008']],'excludeUids':args.exclude_uid,'newlyInstalled':0,'publication':False})
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()

"""Recover an explicit official successor without replacing pinned native results."""
import importlib.util
import argparse
import json
import subprocess
import sys
import uuid
import zipfile
from collections import defaultdict
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN, jobs, Jsonb, dict_row

sys.path.insert(0, str(HERE.parent/'citywide-native'))
from download import acquire
from convert import _convert_one, official_shape
sys.path.insert(0, str(HERE.parent/'enhancement-screening'))
from shape_prepare import entry
sys.path.insert(0, str(HERE.parent/'landsd-territory'))
from retain import iter_features
from pyproj import Transformer


def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--uid',required=True);parser.add_argument('--model-id',required=True)
    parser.add_argument('--directory',required=True);parser.add_argument('--batch',required=True)
    args=parser.parse_args()
    UID,MODEL,BATCH=args.uid,args.model_id,args.batch
    assert Path(BATCH).name==BATCH and BATCH.startswith('government-xl-')
    DIRECTORY=(ROOT/args.directory).resolve();assert DIRECTORY.is_relative_to(HERE/'local')
    DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
    assert not DOC.exists(), 'Use an immutable diagnostic result'
    claim = reservations.claim('codex-pier-successor-'+str(uuid.uuid4()), ['building:'+UID], batch=BATCH)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL/'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        macro = ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz'
        old = next(r for r in read(macro)['rows'] if r['uid']==UID)
        assert MODEL[:-1]==old['modelId'][:-1] and MODEL!=old['modelId']
        geo_ref=MODEL[1:11]
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s', (NATIVE_RUN,old['native']['cacheKey'])).fetchone()==(old['native']['resultSha'],)
        current = read(DIRECTORY/'result.json')
        models = [m for m in current['models'] if m['modelId']==MODEL]
        assert len(models)==1 and models[0]['geoRefNo']==geo_ref and current['sheet']==old['native']['sheet']
        assert not any(m['modelId']==old['modelId'] for m in current['models'])
        selected = {**current, 'models':models}
        download = acquire(selected, DIRECTORY/'zip-directory.bin', LOCAL/'original')
        assert reservations.owns(lease)
        official_source = HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz'
        projection = Transformer.from_crs(4326,2326,always_xy=True)
        features = []
        for f in iter_features(official_source):
            if str(f['properties'].get('GeoRefNo'))!=geo_ref:continue
            geom=f['geometry'];assert geom['type'] in ('Polygon','MultiPolygon')
            polygons=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
            rings=[[list(projection.transform(*point)) for point in ring] for poly in polygons for ring in poly]
            features.append({'attributes':f['properties'],'geometry':{'rings':rings}})
        official_path = LOCAL/'official.json.gz'
        save(official_path,{'sourceSHA256':digest(official_source.read_bytes()),'features':features})
        official = read(official_path)
        manifest_path = ROOT/'3d-viewer/city/data/manifest.json'
        manifest = read(manifest_path)
        matches = []
        for tile in manifest['tiles']:
            path = ROOT/'3d-viewer'/tile['url']
            for building in read(path)['buildings']:
                if building['uid']==UID:matches.append((building,tile['url'],path))
        assert len(matches)==1
        building, tile, tile_path = matches[0]
        by_ref = defaultdict(list)
        for feature in official['features']:
            if str(feature['attributes'].get('GeoRefNo'))!=geo_ref:continue
            feature = {**feature, 'viewerUids':[]}
            if feature['attributes'].get('BuildingCSUID')==building['buildingCSUID']:
                feature['viewerUids']=[{k:building[k] for k in ('uid','rings','base','height')}]
            by_ref[geo_ref].append((feature,official_shape(feature)))
        assert by_ref[geo_ref]
        packed = LOCAL/'packed'; packed.mkdir(exist_ok=True)
        source_entry = next(m['name'] for m in models[0]['members'] if m['name'].endswith('.gltf'))
        with zipfile.ZipFile(LOCAL/'original'/(current['sheet']+'.zip')) as archive:
            converted = _convert_one(archive,archive.getinfo(source_entry),LOCAL/'decoded',packed,by_ref,{'modelId':MODEL,'sourceEntry':source_entry})
        native = {'sheet':current['sheet'],'model':converted}
        source_sha = converted['asset']['sha256']
        path = packed/converted['asset']['asset']
        assert digest(path.read_bytes())==source_sha
        assert converted['matching']['viewerMatches'] and converted['matching']['viewerMatches'][0]['uid']==UID
        candidate = entry(native,building)
        source = {'building':building,'tile':tile,'tileSHA256':digest(tile_path.read_bytes())}
        row = {**old,'modelId':MODEL,'triangles':converted['triangles'],'sourceSHA256':source_sha,'native':native,'source':source,
               'candidate':{'entry':candidate,'path':str(path.relative_to(ROOT))},
               'successorOf':{'modelId':old['modelId'],'sourceSHA256':old['sourceSHA256'],'nativeRun':NATIVE_RUN,'cacheKey':old['native']['cacheKey']}}
        spec = importlib.util.spec_from_file_location('pier_identity',HERE/'xl-final-script-pass.py')
        context = importlib.util.module_from_spec(spec);spec.loader.exec_module(context);context.s.LOCAL=packed
        triangles = context.s.glb_triangles(row);lo,hi=triangles.min(axis=(0,1)),triangles.max(axis=(0,1))
        forms=context.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
        evidence={'uid':UID,'sourceSHA256':source_sha,'identity':context.identity_context(row,triangles,forms),
                  'neighbourTileHashes':{t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms}}
        from terrain_source_preflight import preflight,SourceSheetIndex
        preflight_result=preflight(row,evidence,SourceSheetIndex(read(HERE.parent/'landmark-acquisition/index.json')))
        manifest_sha=digest(manifest_path.read_bytes())
        save(DOC/'check-selection.json.gz',{'batch':BATCH,'rows':[row],'manifestSHA256':manifest_sha,'diagnosticOnly':True,'installationApproved':False})
        save(DOC/'context.json.gz',{'rows':[evidence]})
        save(DOC/'preflight.json',preflight_result)
        refs=[ref(p) for p in [macro,DIRECTORY/'result.json',DIRECTORY/'zip-directory.bin',official_source,official_path,manifest_path,tile_path,
              LOCAL/'original/download.json',path,DOC/'check-selection.json.gz',DOC/'context.json.gz',DOC/'preflight.json',Path(__file__),HERE.parent/'citywide-native/convert.py',HERE.parent/'citywide-native/download.py']]
        stage='official-successor-readonly-diagnostic-v1';payload={'uid':UID,'evidenceRefs':refs}
        jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'modelId':MODEL,'sourceSHA256':source_sha,'successorOf':row['successorOf'],
                'identity':preflight_result['identity'],'triangles':converted['triangles'],'runtimeFormatChecks':converted['runtimeFormatChecks'],
                'newlyInstalled':0,'publication':False,'diagnosticOnly':True,'modelGeometryChanges':0,'scriptExternalAICalls':0,
                'activeWorkers':0,'queuedFollowups':0,'sourceRevisionChanged':True,
                'qualification':'Official successor members packed unchanged. Original native result and prior reviews preserved. Identity diagnostic only; full physical/browser checks and successor-bound acceptance required.'}
        with connect() as con:
            con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
            for r in refs:assert ref(ROOT/r['path'])==r
            assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'uid':UID,'modelId':MODEL,'triangles':converted['triangles'],'identityPassed':preflight_result['identity']['passed'],'jobId':jid}),flush=True)
    finally:reservations.release(lease)


if __name__=='__main__':main()

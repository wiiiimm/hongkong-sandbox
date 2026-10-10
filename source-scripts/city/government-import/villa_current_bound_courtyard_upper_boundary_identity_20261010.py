"""Full current/source/provider replay for the named identity-only Villa rule."""
import gzip
import importlib.util
import json
import numpy as np
import shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from routed_original_cell_identity import verify as routed_verify
from exact_original_georef_cell_identity_20261009 import apply_exact_cell
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin
from villa_current_native_inventory_20261010 import native_rows,missing_profiles,verify_native_rows
from villa_original_courtyard_upper_boundary_identity_20261010 import named_proof,UID,FOREIGN,SOURCE_SHA,WORLD_SHA

DOC=ROOT/'docs/astra-city/government-import/government-xl-villa-current-bound-courtyard-edge-inputs-v1-20261010'
BASE='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer'


def module(name,filename):
    s=importlib.util.spec_from_file_location(name,HERE/filename)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def verify_receipt(receipt,read_bytes=lambda p:p.read_bytes()):
    assert receipt['batch']==DOC.name and receipt['identityAccepted'] is False and receipt['newlyInstalled']==0
    assert len(receipt['evidenceRefs'])==len({r['path'] for r in receipt['evidenceRefs']})
    for ref in receipt['evidenceRefs']:
        p=(ROOT/ref['path']).resolve()
        assert p.is_relative_to(ROOT.resolve()) and digest(read_bytes(p))==ref['sha256'],'Frozen evidence reference changed: '+ref['path']
    return True


def primary_records(load=read,read_bytes=lambda p:p.read_bytes()):
    p=DOC/'exact-current-primary.json';request=load(DOC/'exact-current-primary.request.json');raw=read_bytes(p)
    params=dict(f='json',where="BuildingCSUID IN ('2162333401P20050627','2162233384T20211022')",
        outFields='*',returnGeometry='true',outSR='2326',resultRecordCount='1000',orderByFields='OBJECTID')
    assert request['method']=='GET' and request['url']==BASE+'/0/query' and request['parameters']==params
    assert request['decodedSHA256']==digest(raw)
    if request['gzipDecoded']:
        original=read_bytes(DOC/'exact-current-primary.provider-original.gz')
        assert digest(original)==request['sha256'] and gzip.decompress(original)==raw
    else:assert digest(raw)==request['sha256']
    obj=json.loads(raw)
    assert not obj.get('error') and not obj.get('exceededTransferLimit')
    assert obj['spatialReference'].get('latestWkid',obj['spatialReference'].get('wkid'))==2326
    return obj['features']


def current_binding(row,context,tri,capture,load_forms,read_bytes=lambda p:p.read_bytes()):
    before=read_bytes(ROOT/'3d-viewer/city/data/manifest.json')
    assert digest(before)==capture['manifestSHA256'],'Current manifest differs'
    lo,hi=tri.min((0,1)),tri.max((0,1))
    loaded=load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded]
    hashes={t:digest(read_bytes(ROOT/'3d-viewer'/t)) for _,_,t in loaded}
    assert hashes==context['neighbourTileHashes']==capture['tileHashes'] and forms==capture['forms'],'Complete actual nearby form/tile inventory differs'
    assert next(b for b in forms if b['uid']==UID)==row['source']['building']
    sources=[];route_hashes={}
    for record in json.loads(before)['tiles']:
        raw=read_bytes(ROOT/'3d-viewer'/record['url'])
        matches=[b for b in json.loads(raw)['buildings'] if str(b.get('buildingCSUID') or '')[:10]==row['modelId'][1:11]]
        if matches:
            route_hashes[record['url']]=digest(raw)
            sources.extend(dict(building=b,tile=record['url'],tileSHA256=digest(raw)) for b in matches)
    assert route_hashes==capture['exactRouteTileHashes'],'Complete current territory-wide GeoRef route differs'
    return forms,sources


def replay_raw(row,context,tri,raw,forms,sources):
    final=module('villa_identity_complete_record_current','xl-final-script-pass.py')
    final.projection=lambda faces:shapely.union_all(shapely.polygons(np.asarray(faces)[:,:,[0,2]]))
    loaded=[(b,final.form_polygon(b),next(t for t in context['neighbourTileHashes'] if t.endswith('/'+b['tile']+'.json'))) for b in forms]
    current_identity=final.identity_context(row,tri,loaded)
    assert current_identity==context['identity'],'Full actual current projection context differs'
    previous=routed_verify(raw,row,context,tri,current_identity=current_identity,sources=sources)
    pin=dict(uid=UID,sourceSHA256=SOURCE_SHA,decodedWorldTrianglesSHA256=WORLD_SHA)
    previous=apply_exact_cell(previous,tri,expected_binding=pin,current_binding=pin)
    previous.update(exactRouteTileHashes=read(DOC/'current-inputs.json.gz')['exactRouteTileHashes'],
        exactRouteManifestSHA256=read(DOC/'current-inputs.json.gz')['manifestSHA256'])
    assert previous==read(DOC/'raw-identity.json'),'The complete raw full-cell proof changed'
    return previous


def verify_files(row,context,local):
    receipt=read(DOC/'result.json');verify_receipt(receipt)
    capture=read(DOC/'current-inputs.json.gz');lookup=read(DOC/'source-lookup.json.gz')
    verify_native_rows(lookup['rows'])
    assert lookup['nativeRunID']==NATIVE_RUN and not lookup['foreignProfiles']
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
        actual=native_rows(c);verify_native_rows(actual);assert actual==lookup['rows']
        assert missing_profiles(c)==lookup['foreignProfiles']
        assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    assert actual[0]['sourceKey']==row['native']['cacheKey']+'/'+row['modelId']
    assert actual[0]['model']==row['native']['model'] and actual[0]['resultSHA256']==row['native']['resultSha']
    own=(ROOT/row['candidate']['path']).read_bytes();assert digest(own)==SOURCE_SHA
    assert read(DOC/'complete-original-stream-pins.json.gz')==stream_pin(own,row['modelId'],16669),'Complete source root/BIN/attribute streams differ'
    tri=decode_original_world_triangles(own);assert digest(tri.astype('<f8').tobytes())==WORLD_SHA
    final=module('villa_current_all_foreign_actors','xl-final-script-pass.py')
    forms,sources=current_binding(row,context,tri,capture,final.load_forms)
    missing=lookup['missingForeign']
    assert missing['currentSource']['building']==next(b for b in forms if b['uid']==FOREIGN)
    previous=replay_raw(row,context,tri,own,forms,sources)
    proof=named_proof(previous,row,tri,forms,primary_records(),missing)
    proof.update(currentBinding=dict(manifestSHA256=capture['manifestSHA256'],
        completeCurrentTileHashes=capture['tileHashes'],
        completeCurrentFormsSHA256=digest(json.dumps(forms,sort_keys=True,separators=(',',':')).encode()),
        sourceEvidenceJobId=receipt['jobId'],allEvidenceRefsVerified=True,allOriginalStreamsVerified=True,
        completeCurrentNativeMembershipVerified=True,foreignNativeAbsenceVerifiedForCurrentRun=True,
        rawFullCellRecomputed=True,consistentCompleteRecordProjection=True),
        foreignRemainsActualEstimatedBasicActor=True,physicalAccepted=False,installationApproved=False)
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==capture['manifestSHA256']
    assert all(digest((ROOT/'3d-viewer'/t).read_bytes())==h for t,h in capture['tileHashes'].items())
    return proof

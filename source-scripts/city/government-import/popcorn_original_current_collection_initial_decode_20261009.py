"""Current replay of the reviewed exact PopCorn two-source stair identity.

Identity only. Every original surface and every other current actor is retained;
physical/support/runtime checks in the caller are never supplied by this proof.
"""
import importlib.util
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from popcorn_original_ancillary_identity_20261009 import verify_collection,PINS,POLICY

UIDS=set(PINS)
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-complete-original-current-pair-20261009/selection.json.gz'
PREFIX=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-complete-face-ground-20261009'


def verify_files(row,context,local):
    proof=verify_collection()
    assert row['uid'] in UIDS and context['uid']==row['uid']
    mid,sha,worldsha=PINS[row['uid']]
    assert row['modelId']==mid and row['sourceSHA256']==context['sourceSHA256']==sha
    source=next(r for r in read(INPUT)['rows'] if r['uid']==row['uid'])
    assert row['source']==source['source'] and row['native']==source['native']
    assert row['candidate']['entry']==source['candidate']['entry']
    raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==sha
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        actual=con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual[0]==row['native']['resultSha']
        assert [m for m in actual[1]['models'] if m['modelId']==mid]==[row['native']['model']]
    from xl_source_stream_binding_20261009 import source_stream_binding
    binding=source_stream_binding(raw)
    prefix=read(PREFIX/(row['uid'].split('/')[1].replace(':','-')+'-complete-face-prefix.json.gz'))['binding']
    for key in ['sourceSHA256','rootMatrix','positionTriangleStreamSHA256','normalTriangleStreamSHA256','colourTriangleStreamSHA256']:
        assert binding[key]==prefix[key], 'Changed original source stream/root'
    spec=importlib.util.spec_from_file_location('popcorn_current_full_original_decode',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=local
    decoded=decoder.glb_triangles({**row,'triangles':row['native']['model']['triangles']})
    assert digest(decoded.astype('<f8').tobytes())==worldsha==prefix['decodedWorldTrianglesSHA256']
    assert context['neighbourTileHashes'] and all(digest((ROOT/'3d-viewer'/u).read_bytes())==h for u,h in context['neighbourTileHashes'].items())
    return {'policy':POLICY,'uid':row['uid'],'sourceSHA256':sha,'passed':True,'reasons':[],
            'proof':{'exactObjectId':True,'exactBuildingCSUID':True,'uniqueViewerMatch':True,'identityAccepted':True},
            'completeIndependentCollection':proof,'wholeOriginalSourceBinding':binding,
            'wholeOriginalWorldTrianglesSHA256':worldsha,'currentManifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),
            'installationApproved':False,'sourceGeometryChanges':0}

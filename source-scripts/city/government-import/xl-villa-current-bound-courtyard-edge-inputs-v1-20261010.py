"""Fresh complete current/provider/native capture for the reviewed named proposal."""
from copy import deepcopy
import importlib.util
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from villa_original_courtyard_upper_boundary_identity_20261010 import UID, FOREIGN, SOURCE_SHA, WORLD_SHA
from villa_current_native_inventory_20261010 import native_rows, missing_profiles, verify_native_rows
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from tung_sing_current_bound_identity_20261010 import stream_pin

BATCH = 'government-xl-villa-current-bound-courtyard-edge-inputs-v1-20261010'
DOC = ROOT/'docs/astra-city/government-import'/BATCH
OLD = DOC.parent/'government-xl-villa-premiere-complete-record-projection-identity-20261010'
ACQUISITION = DOC.parent/'government-xl-villa-premiere-two-original-recovery-20261010'


def module(name, filename):
    s=importlib.util.spec_from_file_location(name,HERE/filename)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def main():
    assert not DOC.exists()
    claim=reservations.claim('villa-current-bound-inputs-'+str(uuid.uuid4()),
        ['building:'+UID,'building:'+FOREIGN],batch=BATCH,ttl=3600)
    assert claim['ok'],claim
    try:
        DOC.mkdir(parents=True)
        before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
        assert before==(OLD/'captured-manifest.json').read_bytes(), 'Fresh raw identity must match the actual current global manifest'
        row=deepcopy(read(OLD/'selection.json.gz')['rows'][0])
        context=deepcopy(read(OLD/'context.json.gz')['rows'][0])
        source=ROOT/row['candidate']['path'];raw=source.read_bytes()
        assert digest(raw)==SOURCE_SHA
        tri=decode_original_world_triangles(raw)
        assert digest(tri.astype('<f8').tobytes())==WORLD_SHA
        final=module('villa_capture_current_forms','xl-final-script-pass.py')
        lo,hi=tri.min((0,1)),tri.max((0,1))
        loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
        forms=[b for b,_,_ in loaded]
        hashes={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in loaded}
        assert hashes==context['neighbourTileHashes']
        assert next(b for b in forms if b['uid']==UID)==row['source']['building']
        missing=deepcopy(read(ACQUISITION/'selection.json.gz')['missing'][0])
        assert next(b for b in forms if b['uid']==FOREIGN)==missing['currentSource']['building']
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            rows=native_rows(c);verify_native_rows(rows)
            profiles=missing_profiles(c);assert not profiles
        assert rows[0]['model']==row['native']['model'] and rows[0]['resultSHA256']==row['native']['resultSha']
        assert rows[0]['sourceKey']==row['native']['cacheKey']+'/'+row['modelId']
        primary=module('villa_fresh_primary_capture','xl-man-fuk-man-oi-primary-relations-20261010.py');primary.DOC=DOC
        features=primary.query(0,"BuildingCSUID IN ('2162333401P20050627','2162233384T20211022')",'exact-current-primary',True)
        assert len(features)==2 and {f['attributes']['BuildingCSUID'] for f in features}=={'2162333401P20050627','2162233384T20211022'}
        save(DOC/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(before)))
        save(DOC/'context.json.gz',dict(rows=[context]))
        save(DOC/'current-inputs.json.gz',dict(manifestSHA256=digest(before),tileHashes=hashes,forms=forms,
            exactRouteTileHashes=read(OLD/'identity.json')['exactRouteTileHashes']))
        save(DOC/'source-lookup.json.gz',dict(rows=rows,foreignProfiles=profiles,missingForeign=missing,
            originalPaths={UID:row['candidate']['path']},nativeRunID=NATIVE_RUN_VALUE()))
        save(DOC/'complete-original-stream-pins.json.gz',stream_pin(raw,row['modelId'],16669))
        save(DOC/'raw-identity.json',read(OLD/'identity.json'))
        save(DOC/'projection-census.json',read(OLD/'complete-record-projection-census.json'))
        (DOC/'captured-manifest.json').write_bytes(before)
        assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before
        assert all(digest((ROOT/'3d-viewer'/t).read_bytes())==h for t,h in hashes.items())
        refs=[Path(__file__),source,HERE/'villa_current_native_inventory_20261010.py',
            HERE/'villa_original_courtyard_upper_boundary_identity_20261010.py',
            HERE/'test_villa_original_courtyard_upper_boundary_identity_20261010.py',
            HERE/'tung_sing_current_bound_identity_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',
            HERE/'xl-final-script-pass.py',HERE/'xl-man-fuk-man-oi-primary-relations-20261010.py',
            OLD/'result.json',OLD/'identity.json',OLD/'complete-record-projection-census.json',
            ACQUISITION/'result.json',ACQUISITION/'selection.json.gz']
        refs += [ROOT/'3d-viewer'/t for t in hashes]
        result=module('villa_current_capture_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH,'complete-current-native-provider-courtyard-boundary-inputs-v1',refs,
            dict(uids=[UID,FOREIGN],manifestSHA256=digest(before),identityAccepted=False,physicalAccepted=False,
                completeCurrentForms=len(forms),completeOriginalFaces=16669,foreignNativeAvailable=False,
                qualification='Fresh immutable complete input capture only. Exact single current original source membership/bytes, original root/BIN/attributes/world, all actual nearby forms and unique active primary records are pinned. Unknown canopy surveyed heights and absent native original remain explicit; all physical actors/gates independent.'))
        print(json.dumps(dict(jobId=result['jobId'],manifestSHA256=digest(before),forms=len(forms))),flush=True)
    finally:
        assert reservations.release(claim['reservation'])['ok']


def NATIVE_RUN_VALUE():
    from run import NATIVE_RUN
    return NATIVE_RUN


if __name__=='__main__':main()

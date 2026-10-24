"""Recover an indexed unmapped original by source key, without inventing a viewer UID."""
import argparse,traceback,uuid,zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model-id',required=True);a=p.parse_args();assert a.model_id in ['B349971856402063C0','B352981210001063C0']
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-unmapped-'+a.model_id[1:11]+'-original-acquire-v1-20261023';out=base/batch;local=HERE/'local'/batch;assert not out.exists()and not local.exists();lookup='government-xl-four-primary-exceptions-native-context-v1-20261023';_,pins=authenticate(base/lookup);path=base/lookup/(a.model_id+'.json.gz');assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];context=read(path);assert context['uid']is None and context['nativeModel']['modelId']==a.model_id;model=context['nativeModel'];expected=context['originalIndexedSHA256'];assert model['asset']['sha256']==expected
    refs=[Path(__file__),base/lookup/'result.json',path];report=dict(uids=[],sourceKeys=[context['sourceKey']],modelId=a.model_id,viewerUid=None,expectedSourceSHA256=expected,sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,permanentRejection=False)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');sha=db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(context['nativeCacheKey'],)).fetchone()[0];assert sha==context['nativeResultSHA256'];sheet=db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(context['nativeCacheKey'],)).fetchone()[0];directoryrow=db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone();assert directoryrow is not None;prior=directoryrow[0]
    claim=reservations.claim('unmapped-original-'+str(uuid.uuid4()),['native-model:'+context['nativeCacheKey']+':'+a.model_id],batch=batch,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
    try:
        save(out/'original-directory-binding.json',dict(nativeCacheKey=context['nativeCacheKey'],nativeResultSHA256=sha,sheet=sheet,source=prior));helper=module('unmapped_original_recovery',HERE/'xl-second-pass.py');directory,_=helper.recovery.scan(dict(SHEETNO=sheet,Format_glTF=prior['sourceURL'],REVISIONDATE=prior['revision']),local/'directory');assert directory['etag']==prior['etag']and directory['directorySHA256']==prior['directorySHA256'],'Pinned original directory changed'
        directory['models']=[m for m in directory['models']if m['modelId']==a.model_id];assert len(directory['models'])==1;helper.acquire(directory,local/'directory/zip-directory.bin',local/'original',include_terrain=False);packed=local/'packed';packed.mkdir()
        with zipfile.ZipFile(local/'original'/(sheet+'.zip'))as archive:converted=helper._convert_one(archive,archive.getinfo(model['sourceEntry']),local/'decoded',packed,{},dict(modelId=a.model_id))
        assert converted['triangles']==model['triangles'];raw=helper.recovery.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),expected);assert digest(raw)==expected and len(raw)==model['asset']['bytes'];dest=local/'assets'/(expected+'.glb.gz');dest.parent.mkdir();dest.write_bytes(raw)
        from exact_packed_world_geometry_20261009 import decode_original_world_triangles
        t=decode_original_world_triangles(raw);assert len(t)==model['triangles'];report.update(status='exact-unmapped-original-recovered',sourceRecovered=True,sourceSHA256=expected,asset=dict(path=str(dest.relative_to(ROOT)),sha256=expected),completeSourceFaces=len(t),originalWorldSHA256=digest(t.tobytes()),worldBounds=dict(min=t.min((0,1)).tolist(),max=t.max((0,1)).tolist()),qualification='Exact indexed compressed original recovered with the existing range/CRC/deterministic converter. No viewer UID assigned or original vertices/placement changed. Current-target correspondence, source graph, support, terrain and browser/publication checks remain unapproved.')
        refs.extend(HERE/n for n in ['xl-second-pass.py','exact_packed_world_geometry_20261009.py'])
    except Exception as error:
        report.update(status='original-source-recovery-investigation',sourceRecovered=False,reason=str(error),errorType=type(error).__name__);save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc()))
    finally:assert reservations.release(lease)['ok']
    save(out/'summary.json',report);refs.extend(p for p in local.rglob('*')if p.is_file());module('unmapped_original_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'unmapped-indexed-original-government-source-recovery',refs,report);print({k:report.get(k)for k in ['modelId','status','sourceRecovered','completeSourceFaces','reason']},flush=True)

if __name__=='__main__':main()

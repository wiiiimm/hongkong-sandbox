"""Recover one exact cached government original; no modelling or acceptance."""
import traceback,uuid,zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-nam-cheong-fu-yun-acquire-v1-20261023'
LOOKUP='government-xl-nam-cheong-fu-yun-lookup-v1-20261023'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
 _,pins=authenticate(BASE/LOOKUP);p=BASE/LOOKUP/'lookup.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 lookup=read(p);assert len(lookup['matchedOriginalModels'])==1
 model=lookup['matchedOriginalModels'][0];assert model['modelId']=='B340312091301063C0'and model['triangles']==6035
 expected=model['asset']['sha256'];assert expected=='159453e8bc40543eb211dd9e0e2081e9796651051f430c935359e29b03ea31eb'
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  sha=db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(lookup['nativeCacheKey'],)).fetchone()[0]
  assert sha==lookup['nativeResultSHA256']
  sheet=db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(lookup['nativeCacheKey'],)).fetchone()[0]
  prior=db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
 claim=reservations.claim('source118003-adjacent-original-'+str(uuid.uuid4()),['native-model:'+lookup['nativeCacheKey']+':'+model['modelId']],batch=BATCH,ttl=1800);assert claim['ok'],claim
 lease=claim['reservation'];refs=[Path(__file__),BASE/LOOKUP/'result.json',p]
 report=dict(uids=['landsd/268867:0'],relatedUID='landsd/270874:0',modelId=model['modelId'],expectedSourceSHA256=expected,sourceGeometryChanges=0,identityAccepted=False,installationApproved=False,permanentRejection=False)
 try:
  save(doc/'original-directory-binding.json',dict(nativeCacheKey=lookup['nativeCacheKey'],nativeResultSHA256=sha,source=prior))
  helper=module('source118003_source_recovery',HERE/'xl-second-pass.py')
  directory,_=helper.recovery.scan(dict(SHEETNO=sheet,Format_glTF=prior['sourceURL'],REVISIONDATE=prior['revision']),local/'directory')
  assert directory['etag']==prior['etag']and directory['directorySHA256']==prior['directorySHA256'],'Pinned original directory changed'
  directory['models']=[m for m in directory['models']if m['modelId']==model['modelId']];assert len(directory['models'])==1
  helper.acquire(directory,local/'directory/zip-directory.bin',local/'original',include_terrain=False)
  packed=local/'packed';packed.mkdir()
  with zipfile.ZipFile(local/'original'/(sheet+'.zip'))as archive:
   converted=helper._convert_one(archive,archive.getinfo(model['sourceEntry']),local/'decoded',packed,{},dict(modelId=model['modelId']))
  assert converted['triangles']==model['triangles']
  raw=helper.recovery.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),expected)
  assert digest(raw)==expected and len(raw)==model['asset']['bytes']
  destination=local/'assets'/(expected+'.glb.gz');destination.parent.mkdir();destination.write_bytes(raw)
  from exact_packed_world_geometry_20261009 import decode_original_world_triangles
  tri=decode_original_world_triangles(raw);assert len(tri)==6035
  report.update(status='exact-original-recovered',sourceRecovered=True,sourceSHA256=expected,asset=dict(path=str(destination.relative_to(ROOT)),sha256=expected),completeSourceFaces=len(tri),originalWorldSHA256=digest(tri.tobytes()),worldBounds=dict(min=tri.min(axis=(0,1)).tolist(),max=tri.max(axis=(0,1)).tolist()),qualification='Exact expected compressed original asset recovered from government members using existing deterministic converter and checksum. Source-only evidence; identity/contact/terrain/current-scene/runtime/publication remain unapproved.')
  refs.extend([HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE.parent/'citywide-native/download.py',HERE.parent/'citywide-native/convert.py',HERE.parent/'enhancement-screening/shape_prepare.py'])
 except Exception as e:
  report.update(status='source-recovery-investigation',sourceRecovered=False,reason=str(e),errorType=type(e).__name__)
  save(doc/'failure.json',dict(error=repr(e),traceback=traceback.format_exc()))
 finally:
  assert reservations.release(lease)['ok']
 save(doc/'summary.json',report)
 refs.extend(p for p in local.rglob('*')if p.is_file())
 module('source118003_annex_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-adjacent-original-recovery',refs,report)
 print(dict(status=report['status'],sourceRecovered=report['sourceRecovered'],faces=report.get('completeSourceFaces')),flush=True)
if __name__=='__main__':main()

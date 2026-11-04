"""Use existing verified source recovery for a newly nominated original.

Source-download fallback is explicit. Exact indexed GLB/gzip bytes are mandatory;
no model geometry, pose, viewer data, acceptance or production queue is changed.
"""
import argparse,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--target',required=True);p.add_argument('--uid',required=True);p.add_argument('--nomination',required=True);p.add_argument('--lease',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
 lease=read(Path(a.lease));assert reservations.owns(lease);out=BASE/a.batch;local=HERE/'local'/a.batch;assert not out.exists();_,pins=authenticate(BASE/a.nomination);path=BASE/a.nomination/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];nomination=read(path)
 target=next(r for r in nomination['rows']if r['uid']==a.target)
 assert {'building:'+u for u in [a.uid,a.target]}<=set(lease['resources'])
 row=next(r for r in target['nearbyOriginalCandidates']if r['uid']==a.uid);key,model_id=row['sourceKey'].split('/',1)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert record and record[0]==row['nativeResultSHA256'];model=next(m for m in record[1]['models']if m['modelId']==model_id)
 entry=model['candidate'];assert entry['uid']==a.uid and entry['sha256']==row['indexedSourceSHA256'] and model['worldBounds']==row['worldBounds']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(row['nativeResultSHA256'],)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';forms=[]
 for tile in read(manifest)['tiles']:
  tilepath=ROOT/'3d-viewer'/tile['url']
  for b in read(tilepath)['buildings']:
   if b['uid']==a.uid:forms.append(dict(building=b,tile=tile['url'],tileSHA256=digest(tilepath.read_bytes())))
 assert len(forms)==1;form=forms[0];b=form['building']
 assert b['objectId']==entry['objectId']and b['buildingCSUID']==entry['buildingCSUID']
 assert b.get('baseHeightHKPD')==entry['recordedBaseHeight']and b.get('topHeightHKPD')==entry['recordedTopHeight']
 inp=local/'recovery-inputs.json.gz';save(inp,dict(nativeRun=NATIVE_RUN,rows=[a.uid],sources={a.uid:form},native=[dict(sheet=row['sheet'],cacheKey=key,resultSha=row['nativeResultSHA256'],model=model)]))
 prepared=shape_prepare.prepare(inp,local/'recovered',allow_source=True,workers=1,env_file=ROOT/'.env.modelling',reservation_receipt=lease);assert reservations.owns(lease)
 asset=local/'recovered/assets'/(entry['sha256']+'.glb.gz');success=asset.exists()and a.uid not in prepared['errors']
 refs=[Path(__file__),BASE/a.nomination/'result.json',path,inp,local/'recovered/geometry-inputs.json',Path(shape_prepare.__file__),ROOT/'3d-viewer'/form['tile']]
 if success:assert digest(asset.read_bytes())==entry['sha256']and asset.stat().st_size==entry['bytes'];refs.append(asset)
 result=dict(uids=[a.uid],uid=a.uid,sourceKey=row['sourceKey'],sourceSHA256=entry['sha256'],sourceAsset=dict(path=str(asset.relative_to(ROOT)),sha256=entry['sha256'])if success else None,candidate=entry,sourceWorldBounds=model['worldBounds'],triangles=model['triangles'],nativeResultSHA256=row['nativeResultSHA256'],recovered=success,errors=prepared['errors'],methods=prepared['methods'],sourceFallbackEnabled=True,sourceGeometryChanges=0,installationApproved=False,qualification='Existing acquire/convert/canonical-byte recovery only; output must equal the pinned original asset SHA and byte count. No simplification, redesign, geometry/pose edits or source/placement/runtime acceptance.')
 save(out/'summary.json',result);module('nominated_source_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-nominated-government-original-source-recovery',refs,result)
 print(dict(recovered=success,errors=prepared['errors']),flush=True)
if __name__=='__main__':main()

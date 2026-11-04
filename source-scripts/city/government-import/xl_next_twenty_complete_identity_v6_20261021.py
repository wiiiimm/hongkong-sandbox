"""Recover one exact retained asset and finish the frozen twenty-source identity batch."""
from pathlib import Path,PurePosixPath
import os,sys,tarfile
from dotenv import dotenv_values
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
sys.path.insert(0,str(HERE.parent/'landmark-resume'))
from r2_snapshot import R2Store,verify_object,key_for
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-twenty-original-identity-v6-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SOURCE=BASE/'government-xl-next-twenty-original-identity-v3-20261021'
def main():
 assert not DOC.exists();prior=read(SOURCE/'result.json');refs=[Path(__file__),SOURCE/'result.json']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for e in prior['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 selection=read(SOURCE/'selection.json.gz');summary=read(SOURCE/'summary.json')['rows'];missing=[r for r in selection['rows']if not r.get('candidate')];assert len(missing)==1
 row=missing[0];assert row['uid']=='landsd/213352:0'
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');sha,result=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone();assert sha==row['native']['resultSha']
 artifacts=[a for a in result['artifacts']if a['kind']=='original-and-prepared-sheet'];assert len(artifacts)==1;artifact=artifacts[0];assert artifact['key']==key_for(artifact['sha256'])
 import gzip,json
 source=HERE.parent/'central-completion/staged/11-SW-9A'/row['native']['model']['sourceEntry'];original=json.loads(source.read_text());inputs=[source]+[source.parent/b['uri'] for b in original['buffers']];hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs}
 packer=module('exact_pier_recovery_packer',HERE.parent/'central-completion/pack_models.py');raw,stats=packer.pack(source);compressed=gzip.compress(raw,mtime=0);compressed=compressed[:9]+bytes([255])+compressed[10:];expected=row['sourceSHA256'];assert digest(compressed)==expected,'Local deterministic packing differs from indexed original bytes';assert stats['triangles']==row['triangles']
 asset=LOCAL/'assets'/(expected+'.glb.gz');asset.parent.mkdir(parents=True);asset.write_bytes(compressed);row['candidate']=dict(path=str(asset.relative_to(ROOT)));refs.extend([asset,*inputs,HERE.parent/'central-completion/pack_models.py'])
 save(DOC/'asset-recovery.json',dict(uid=row['uid'],nativeResultSHA256=sha,assetSHA256=expected,bytes=len(compressed),sourceHashes=hashes,method='Existing deterministic packer applied to retained original glTF/buffer; portable gzip OS header 255; exact compressed hash equals immutable indexed original asset.',geometryChanges=0))
 final=module('next_twenty_recovered_identity',HERE/'xl-final-script-pass.py');tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in near};context=dict(sourceSHA256=expected,identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);key=row['uid'].split('/')[1];save(DOC/key/'context.json',context);proof=verify_files(row,context,LOCAL/key);save(DOC/key/'identity.json',proof)
 completion=dict(uid=row['uid'],name=row['source']['building'].get('name'),status='identity-passed'if proof['passed']else'identity-review-required',reasons=proof['reasons'],triangles=len(tri));summary=[completion if r['uid']==row['uid']else r for r in summary]
 for e in prior['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 save(DOC/'selection.json.gz',selection);save(DOC/'summary.json',dict(rows=summary,installationApproved=False,geometryChanges=0));save(DOC/'inherited-identity.json',dict(priorReceipt=prior['jobId'],unchangedUids=[r['uid']for r in summary if r['uid']!=row['uid']],qualification='Nineteen exact unchanged prior identity results retained; missing asset recovered and checked separately. No approvals transferred across changed sources.'))
 refs.extend(ROOT/'3d-viewer'/t for t in tiles);refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py',HERE.parent/'landmark-resume/r2_snapshot.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 module('next_twenty_recovery_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-twenty-original-source-identity',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in selection['rows']],rows=summary,installationApproved=False,newlyInstalled=0));print(completion,flush=True)
if __name__=='__main__':main()

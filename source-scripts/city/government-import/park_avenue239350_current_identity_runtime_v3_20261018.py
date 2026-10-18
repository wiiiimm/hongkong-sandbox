"""Current six-original identity and runtime qualification under existing leases."""
from pathlib import Path
import subprocess,sys,uuid,json
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-current-identity-runtime-v3-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/239350:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);prior=BASE/'government-xl-olympian-two-park-avenue-restored-v1-20261018/result.json';r=read(prior);pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),prior]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 historical='3d-viewer/city/data/manifest.json';expected=pins.pop(historical);revision=subprocess.check_output(['git','rev-parse','02746bdb2'],cwd=ROOT,text=True).strip();raw=subprocess.check_output(['git','show',revision+':'+historical],cwd=ROOT);assert digest(raw)==expected
 archived=LOCAL/'historical-manifest.json';archived.parent.mkdir(parents=True,exist_ok=True);archived.write_bytes(raw);refs.append(archived);save(DOC/'historical-binding.json',dict(path=historical,sha256=expected,commit=revision,archive=str(archived.relative_to(ROOT)),currentSceneRecheckedSeparately=True))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);tile='city/data/tiles/0_-2.json';tilepath=ROOT/'3d-viewer'/tile;tilehash=digest(tilepath.read_bytes());forms={b['uid']:b for b in read(tilepath)['buildings']};manifest=ROOT/'3d-viewer/city/data/manifest.json';manifesthash=digest(manifest.read_bytes());refs.extend([tilepath,manifest])
 rows=[]
 restored=[r for r in read(BASE/'government-xl-olympian-two-park-avenue-restored-v1-20261018/restored.json')['rows']if r['uid']in UIDS]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for s in restored:
   stage=c.execute('SELECT result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(s['cacheKey'],)).fetchone()[0];matches=[m for m in stage['models']if m['modelId']==s['modelId']];assert len(matches)==1;model=matches[0];assert model['asset']['sha256']==s['sourceSHA256']and model.get('candidate')==s['candidate']
   assert s['candidate'] is None
   form=forms[s['uid']];official=model['matching']['officialCandidates'];assert len(official)==1 and official[0]['objectId']==form['objectId'] and official[0]['buildingCSUID']==form['buildingCSUID']
   provisional={**model['asset'],'uid':s['uid'],'modelId':s['modelId'],'objectId':form['objectId'],'buildingCSUID':form['buildingCSUID'],'label':form.get('name') or 'Park Avenue podium','triangles':s['triangles'],'worldBounds':s['worldBounds'],'recordedBaseHeight':official[0]['sourceBaseHeight'],'recordedTopHeight':official[0]['sourceTopHeight'],'placementReviewed':False,'publicationApproved':False,'identityReviewApproved':False}
   rows.append(dict(uid=s['uid'],modelId=s['modelId'],triangles=s['triangles'],sourceSHA256=s['sourceSHA256'],native=dict(model=model,cacheKey=s['cacheKey'],sheet=s['sheet']),candidate=dict(path=s['assetPath'],entry={**provisional,'rootTranslation':[-834500,0,816500],'sourceTile':s['sheet']})))
 assert set(x['uid']for x in rows)==set(UIDS);final=module('olympian_identity_context',HERE/'xl-final-script-pass.py');results=[];stage=LOCAL/'runtime';entries=[];sourceforms={}
 for row in rows:
  uid=row['uid'];row['source']=dict(building=forms[uid],tile=tile,tileSHA256=tilehash);row.update(modelId=row['native']['model']['modelId'],triangles=row['native']['model']['triangles']);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);identity=final.identity_context(row,tri,near);context=dict(sourceSHA256=row['sourceSHA256'],identity=identity,neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in near});proof=verify_files(row,context,LOCAL/uid.split('/')[1]);save(DOC/(uid.split('/')[1]+'-identity.json'),dict(context=context,proof=proof));results.append(dict(uid=uid,passed=proof['passed'],reasons=proof['reasons']));print(results[-1],flush=True)
  refs.extend(ROOT/'3d-viewer'/t for t in context['neighbourTileHashes']);entry={**row['candidate']['entry'],'sourceTile':row['native']['sheet'],'publicationApproved':False,'placementReviewed':False,'proceduralWindows':False};asset=stage/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw);assert digest(asset.read_bytes())==entry['sha256'];entries.append(entry);sourceforms[uid]=row['source'];assert reservations.owns(lease)
 save(DOC/'selection.json.gz',dict(manifestSHA256=manifesthash,rows=rows));template=read(HERE/'accepted/government-xxl-20260911/catalogue.json');template.update(models=entries,counts=dict(packedModels=len(entries)));save(stage/'catalogue.json',template);save(stage/'catalogue-index.json',dict(models=len(entries),catalogues=['catalogue.json']));save(stage/'source-forms.json',sourceforms)
 tool=HERE.parent/'building-batch/validate_candidates.mjs';subprocess.run(['node',str(tool),'--candidates',str(stage),'--source-forms',str((stage/'source-forms.json').relative_to(ROOT)),'--out',str(DOC/'validation.json')],cwd=ROOT,check=True);validation=read(DOC/'validation.json')
 for p,h in validation.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 assert digest(tilepath.read_bytes())==tilehash and digest(manifest.read_bytes())==manifesthash;save(DOC/'summary.json',dict(identity=results,validation=validation,fullAcceptance=False))
 refs.extend(HERE/n for n in ['xl-final-script-pass.py','exact_original_georef_cell_identity_20261009.py','government_georef_cell_identity.py','original_source_ownership.py','georef_projection_coverage.py','xl-second-pass.py','exact_packed_world_geometry_20261009.py']);refs.append(tool);refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');assert reservations.owns(lease)
 out=module('olympian_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue239350-original-exact-identity-and-runtime-v1',list(set(refs)),dict(uids=UIDS,identity=results,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

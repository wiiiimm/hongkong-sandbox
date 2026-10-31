"""Recover exact original Tower1 and check their unchanged podium interfaces."""
from pathlib import Path
import copy,sys,uuid,zipfile,subprocess,importlib.util
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from government_georef_cell_identity import geographic_cell
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import canonical_bytes,scan,acquire,_convert_one
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-primrose-remaining-original-components-v2-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
OLD=BASE/'government-xl-primrose-podium-original-closure-20261007';NEW=['landsd/74568:0']
def main():
 assert not DOC.exists()and not LOCAL.exists();old=read(OLD/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(old['jobId'],)).fetchone()==('complete',old)
 for q in old['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 rows={r['uid']:copy.deepcopy(r)for r in read(OLD/'selection.json.gz')['rows']};tile=ROOT/'3d-viewer/city/data/tiles/-2_-5.json';forms={b['uid']:b for b in read(tile)['buildings']};manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes())
 claim=reservations.claim('primrose-original-components-'+str(uuid.uuid4()),['building:'+u for u in sorted(set(rows)|set(NEW))],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];refs=[ROOT/q['path']for q in old['evidenceRefs']]+[OLD/'result.json',tile,manifest,Path(__file__)];recoveries=[]
 try:
  DOC.mkdir();LOCAL.mkdir()
  for uid in NEW:
   form=forms[uid];matches=[]
   with connect()as db:
    db.execute('SET TRANSACTION READ ONLY');profiles=db.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+form['buildingCSUID'][:10]+'%')).fetchall()
    for key,sheet in profiles:
     value=db.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone();assert value;sha,data=value
     for model in data['models']:
      exact=[v for v in model.get('matching',{}).get('officialCandidates',[])if v['objectId']==form['objectId']and v['buildingCSUID']==form['buildingCSUID']]
      if not exact:continue
      try:geographic_cell(model['modelId'],form['buildingCSUID'],form['structureType'])
      except (ValueError,KeyError):continue
      assert len(exact)==1;matches.append((key,sha,sheet,model,exact[0]))
   assert len(matches)==1,(uid,'missing or ambiguous exact source',len(matches));key,result_sha,sheet,model,official=matches[0]
   entry={**model['asset'],'uid':uid,'objectId':form['objectId'],'buildingCSUID':form['buildingCSUID'],'label':form.get('name')or model['modelId'],'modelId':model['modelId'],'triangles':model['triangles'],'worldBounds':model['worldBounds'],'sourceTile':sheet,'rootTranslation':[-834500,0,816500],'priority':'unreviewed','recordedBaseHeight':form['baseHeightHKPD'],'recordedTopHeight':form['topHeightHKPD'],'overlapOfSmallerFootprint':official['overlapOfSmallerFootprint'],'footprintCentroidDistanceMetres':official['footprintCentroidDistanceMetres'],'sourceIdentityReviewed':False,'placementReviewed':False,'publicationApproved':False}
   rows[uid]=dict(uid=uid,sourceSHA256=model['asset']['sha256'],modelId=model['modelId'],triangles=model['triangles'],name=form.get('name'),native=dict(cacheKey=key,resultSha=result_sha,sheet=sheet,model=model),candidate=dict(entry=entry),sourceLookupBasis='exact-full-object-csuid-type-georef-pinned-native-run')
  missing={r['sourceSHA256']for r in rows.values()};cache={}
  for folder in [HERE/'local',ROOT/'3d-viewer/city/data/official-models']:
   for p in folder.rglob('*.glb.gz'):
    sha=p.name.removesuffix('.glb.gz')
    if sha in missing and digest(p.read_bytes())==sha:cache[sha]=p;missing.remove(sha)
    if not missing:break
   if not missing:break
  for uid,row in rows.items():
   sha=row['sourceSHA256'];transferred=0
   if sha in cache:raw=cache[sha].read_bytes();method='verified-local-original';refs.append(cache[sha])
   else:
    sheet=row['native']['sheet'];folder=LOCAL/'sheets'/sheet
    with connect()as db:
     db.execute('SET TRANSACTION READ ONLY');pinned=db.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
    directory,_=scan(dict(SHEETNO=sheet,Format_glTF=pinned['sourceURL'],REVISIONDATE=pinned['revision']),folder/'directory');directory['models']=[m for m in directory['models']if m['modelId']==row['modelId']];assert len(directory['models'])==1
    receipt=acquire(directory,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True)
    with zipfile.ZipFile(folder/'original'/(sheet+'.zip'))as archive:
     m=row['native']['model'];converted=_convert_one(archive,archive.getinfo(m['sourceEntry']),folder/'decoded',packed,{},dict(modelId=row['modelId']));raw=canonical_bytes((packed/converted['asset']['asset']).read_bytes(),sha)
    transferred=receipt['newThisInvocationBytes'];method='exact-original-government-recovery'
   assert digest(raw)==sha and len(raw)==row['native']['model']['asset']['bytes'];dest=LOCAL/'assets'/(sha+'.glb.gz');dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw);refs.append(dest);row['candidate']['path']=str(dest.relative_to(ROOT));row['candidate']['entry']['asset']='assets/'+dest.name;row['candidate']['entry']['rootTranslation']=[-834500,0,816500]
   if 'source'in row:assert row['source']['building']==forms[uid]
   row['source']=dict(building=forms[uid],tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()));recoveries.append(dict(uid=uid,sourceSHA256=sha,method=method,transferredBytes=transferred));print(recoveries[-1],flush=True);assert reservations.heartbeat(lease)['ok']
  ordered=[rows[u]for u in sorted(rows)];save(DOC/'selection.json.gz',dict(rows=ordered,manifestSHA256=manifest_sha));save(DOC/'recovery.json',dict(rows=recoveries,sourceGeometryChanges=0));save(DOC/'support-inputs.json',dict(sources=ordered,pairs=[dict(uid=u,supportUid='landsd/74573:0')for u in NEW]))
  tool=HERE/'original-support-closure-interfaces.mjs'
  with (DOC/'support.log').open('w')as log:p=subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  save(DOC/'command.json',dict(exitCode=p.returncode));assert p.returncode==0
  support=read(DOC/'support-checks.json.gz');refs +=[ROOT/p for p in support['inputHashes']]
  for p,h in support['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  assert digest(manifest.read_bytes())==manifest_sha
  spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'exact-original-remaining-compound-components-v1',refs,dict(uids=list(rows),newlyRecoveredOriginals=NEW,interfaces=[dict(uid=r['uid'],passed=r['interface']['passed'],samples=r['interface']['samples'],unresolved=len(r['interface']['unresolved']))for r in support['rows']],fullAcceptance=False,qualification='Exact original components recovered; support interface diagnostics only. Fresh identity, physical, runtime and publication acceptance remain required.'))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

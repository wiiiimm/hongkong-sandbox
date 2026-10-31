"""Exact full original Miami podium pair recovery and current outline diagnostic.

Provider OP-related sources are retained independently. No live file changes,
neighbour suppression, geometry edits or identity/physical acceptance.
"""
import importlib.util,json,uuid,zipfile,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
BATCH='government-xl-miami-op-complete-pair-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/232089:0','landsd/259038:0']
def module(name,filename):
 s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(additional_forms=None):
 assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes())
 prior=next(r for r in read(ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009/full-original-op-group-measures.json.gz')['rows'] if r['uid']==UIDS[0]);wanted={b['id']+':0':b for b in prior['groupForms']+(additional_forms or [])};current={};allforms=[]
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];forms=read(p)['buildings'];allforms+=forms
  for b in forms:
   if b['uid'] in UIDS:
    assert b==wanted[b['uid']],b['uid']
    current[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(p.read_bytes())}
 assert set(current)==set(UIDS)
 claim=reservations.claim('xl-miami-full-op-pair-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  helper=module('miami_source_recovery','xl-next-support-recovery-20261005.py');rows=[]
  for uid in UIDS:
   b=current[uid]['building'];matches=[]
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY')
    profiles=c.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+b['buildingCSUID'][:10]+'%')).fetchall()
    for key,sheet in profiles:
     resultsha,data=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone()
     for mod in data['models']:
      if mod['modelId'][1:11]==b['buildingCSUID'][:10] and any(v['buildingCSUID']==b['buildingCSUID'] for v in mod.get('matching',{}).get('officialCandidates',[])):matches.append({'cacheKey':key,'resultSha':resultsha,'sheet':sheet,'model':mod})
   assert len(matches)==1,(uid,len(matches));native=matches[0];entry,basis=helper.diagnostic_entry(native,b);sha=native['model']['asset']['sha256'];row={'uid':uid,'source':current[uid],'native':native,'modelId':native['model']['modelId'],'sourceSHA256':sha,'candidate':{'entry':entry},'sourceLookupBasis':basis}
   cached=next((p for p in (HERE/'local').rglob(sha+'.glb.gz') if digest(p.read_bytes())==sha),None)
   if cached:raw=cached.read_bytes();recovery={'method':'verified-local-original','transferredBytes':0}
   else:
    sheet=native['sheet'];folder=LOCAL/'sheets'/sheet
    with connect() as c:
     c.execute('SET TRANSACTION READ ONLY');pinned=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
    directory,_=helper.scan({'SHEETNO':sheet,'Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},folder/'directory',refresh=True)
    save(DOC/(uid.split('/')[1].replace(':','-')+'-fresh-container-lineage.json'),{'oldPinnedContainer':pinned,'freshCurrentContainer':{k:v for k,v in directory.items() if k!='models'},'containerChanged':directory['etag']!=pinned['etag'] or directory['directorySHA256']!=pinned['directorySHA256'],'qualification':'Container changes recorded, never inherited as model approval. Following canonical byte check must establish exact unchanged asset SHA independently; a changed source asset requires a new version pin.'})
    directory['models']=[m for m in directory['models'] if m['modelId']==row['modelId']];assert len(directory['models'])==1
    receipt=helper.acquire(directory,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True)
    with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
     converted=helper._convert_one(z,z.getinfo(native['model']['sourceEntry']),folder/'decoded',packed,{}, {'modelId':row['modelId']});raw=helper.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),sha)
    recovery={'method':'exact-original-government-recovery','transferredBytes':receipt['newThisInvocationBytes']}
   assert digest(raw)==sha and len(raw)==native['model']['asset']['bytes'];p=LOCAL/'assets'/(sha+'.glb.gz');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['candidate']['path']=str(p.relative_to(ROOT));row['candidate']['entry']['asset']='assets/'+p.name;rows.append(row);save(DOC/(uid.split('/')[1].replace(':','-')+'-recovery.json'),recovery)
  assert digest(manifest.read_bytes())==mh;save(DOC/'selection.json.gz',{'rows':rows,'manifestSHA256':mh,'nativeRun':NATIVE_RUN,'currentTargetFormsRebound':True,'officialOPStructureIds':prior['structureIds'],'opStructureDetails':prior['opStructureDetails']})
  decoder=module('miami_original_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL;triangles=[]
  for r in rows:
   r['triangles']=r['native']['model']['triangles'];t=decoder.glb_triangles(r);triangles.append(t);save(DOC/(r['uid'].split('/')[1].replace(':','-')+'-original-decoding.json'),{'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'originalTriangles':len(t),'worldTriangleSHA256':digest(t.astype('<f8').tobytes()),'worldBounds':[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()]})
  tri=np.concatenate(triangles);fp=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));poly=lambda b:shapely.Polygon(b['rings'][0],b['rings'][1:]);target=shapely.union_all([poly(current[u]['building']) for u in UIDS]);excess=fp.difference(target)
  foreign=[b for b in allforms if b['uid'] not in UIDS and shapely.box(*poly(b).bounds).intersects(fp.envelope)];other=shapely.union_all([poly(b) for b in foreign]);distance=max(float(target.distance(shapely.Point(v))) for v in tri[:,:,[0,2]].reshape(-1,2))
  metrics={'uids':UIDS,'completeOriginalTriangles':len(tri),'targetCoveredByFullOriginalPair':target.intersection(fp).area/target.area,'maximumSourceExcessDistanceM':distance,'sourceExcessCoveredByUnrelatedFormsM2':excess.intersection(other).area,'targetAreaM2':target.area,'missingTargetAreaM2':target.difference(fp).area,'sourceExcessAreaM2':excess.area,'allForeignFormsRetained':[b['uid'] for b in foreign],'unrelatedPositiveOverlap':[{'uid':b['uid'],'name':b.get('name',''),'areaM2':excess.intersection(poly(b)).area} for b in foreign if excess.intersection(poly(b)).area>0],'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'geometryChanges':0,'qualification':'Complete exact provider OP-related original pair; current target/foreign forms all retained. Existing thresholds unchanged; no acceptance from projected union alone.'}
  save(DOC/'complete-original-pair-current-measures.json',metrics);save(DOC/'missing-target-and-source-excess.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'role':'missing-current-target'},'geometry':shapely.geometry.mapping(target.difference(fp))},{'type':'Feature','properties':{'role':'full-original-source-excess'},'geometry':shapely.geometry.mapping(excess)}]});print(metrics,flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

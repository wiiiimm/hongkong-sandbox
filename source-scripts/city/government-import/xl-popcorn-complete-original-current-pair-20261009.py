"""Recover complete original native collection under exact current forms; no live changes."""
import json,importlib.util,subprocess,sys,uuid,zipfile,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
BATCH='government-xl-popcorn-complete-original-current-pair-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;UIDS=['landsd/295538:0','landsd/295539:0']
def module(name,filename):
 sp=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 if (DOC/'selection.json.gz').exists():return measure()
 assert not DOC.exists() and not LOCAL.exists()
 manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());collection=read(ROOT/'docs/astra-city/government-import/government-xl-popcorn-station-collection-20261009/complete-original-popcorn-station-measures.json.gz');wanted={b['uid']:b for b in collection['groupForms']};current={}
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];found=[b for b in read(p)['buildings'] if b['uid'] in UIDS]
  for b in found:
   assert b==wanted[b['uid']];current[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(p.read_bytes())}
 assert set(current)==set(UIDS)
 claim=reservations.claim('xl-popcorn-native-pair-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  helper=module('popcorn_original_recovery','xl-next-support-recovery-20261005.py');rows=[]
  for uid in UIDS:
   b=current[uid]['building']
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');matches=[]
    profiles=c.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+b['buildingCSUID'][:10]+'%')).fetchall()
    for key,sheet in profiles:
     sha,data=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone()
     for model in data['models']:
      if model['modelId'][1:11]==b['buildingCSUID'][:10] and any(v['buildingCSUID']==b['buildingCSUID'] for v in model.get('matching',{}).get('officialCandidates',[])):matches.append({'cacheKey':key,'resultSha':sha,'sheet':sheet,'model':model})
   assert len(matches)==1,(uid,len(matches));native=matches[0];entry,basis=helper.diagnostic_entry(native,b);row={'uid':uid,'source':current[uid],'native':native,'modelId':native['model']['modelId'],'sourceSHA256':native['model']['asset']['sha256'],'candidate':{'entry':entry},'sourceLookupBasis':basis};sha=row['sourceSHA256'];cached=None
   for folder in [HERE/'local',ROOT/'3d-viewer/city/data/official-models']:
    for path in folder.rglob(sha+'.glb.gz'):
     if digest(path.read_bytes())==sha:cached=path;break
    if cached:break
   if cached:raw=cached.read_bytes();recovery={'method':'verified-local-original','transferredBytes':0}
   else:
    sheet=native['sheet'];folder=LOCAL/'sheets'/sheet
    with connect() as c:
     c.execute('SET TRANSACTION READ ONLY');pinned=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
    directory,_=helper.scan({'SHEETNO':sheet,'Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},folder/'directory');directory['models']=[m for m in directory['models'] if m['modelId']==row['modelId']];assert len(directory['models'])==1
    receipt=helper.acquire(directory,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True)
    with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as archive:
     converted=helper._convert_one(archive,archive.getinfo(native['model']['sourceEntry']),folder/'decoded',packed,{}, {'modelId':row['modelId']});raw=helper.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),sha)
    recovery={'method':'exact-original-government-recovery','transferredBytes':receipt['newThisInvocationBytes']}
   assert digest(raw)==sha and len(raw)==native['model']['asset']['bytes'];destination=LOCAL/'assets'/(sha+'.glb.gz');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw);row['candidate']['path']=str(destination.relative_to(ROOT));row['candidate']['entry']['asset']='assets/'+destination.name;rows.append(row);save(DOC/(uid.split('/')[1].replace(':','-')+'-recovery.json'),recovery)
  assert digest(manifest.read_bytes())==mh;save(DOC/'selection.json.gz',{'rows':rows,'manifestSHA256':mh,'nativeRun':NATIVE_RUN,'currentTargetFormsRebound':True});measure()
 finally:assert reservations.release(lease)['ok']

def measure():
 rows=read(DOC/'selection.json.gz')['rows']
 for row in rows:row['triangles']=row['native']['model']['triangles']
 decoder=module('popcorn_native_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL;proof=[]
 for row in rows:
  tri=decoder.glb_triangles(row);fp=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));batch='government-xl-source-authored-openings-20261009' if row['uid']==UIDS[0] else 'government-xl-popcorn-station-collection-20261009';fbx=np.load(HERE/'local'/batch/'raw-fbx'/row['modelId']/'full-world-triangles.npz')['triangles'];orig=np.stack([fbx[:,:,0]-834500,fbx[:,:,2],816500-fbx[:,:,1]],axis=2);op=shapely.union_all(shapely.polygons(orig[:,:,[0,2]]));proof.append({'uid':row['uid'],'originalFBXTriangles':len(orig),'originalNativeGLTFTriangles':len(tri),'sameProjectedGeometrySymmetricDifferenceM2':op.symmetric_difference(fp).area,'boundaryHausdorffM':op.boundary.hausdorff_distance(fp.boundary),'nativeWorldBounds':row['native']['model']['worldBounds'],'nativeSourceSHA256':row['sourceSHA256'],'exactDecodedWorldTrianglesSHA256':digest(tri.astype('<f8').tobytes()),'originalFBXWorldTrianglesSHA256':digest(orig.astype('<f8').tobytes()),'newFormatApprovalInherited':False})
 save(DOC/'independent-native-fbx-collection-check.json',{'rows':proof,'installationApproved':False,'identityAccepted':False,'geometryChanges':0});print({'pair':UIDS,'formats':proof,'manifestSHA256':read(DOC/'selection.json.gz')['manifestSHA256']},flush=True)
if __name__=='__main__':main()

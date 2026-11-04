"""Recover distinct adjacent podium unchanged and compare its actual original surfaces.

No grouping, foreign suppression, source transformation or collision acceptance.
"""
import importlib.util,uuid,zipfile,json,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_original_component_contacts_20261009 import exact_component_contacts
BATCH='government-xl-miami-foreign-original-interface-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
 family=DOC.parent/'government-xl-miami-op-complete-family-20261009';foreign=read(DOC.parent/'government-xl-miami-op-complete-pair-20261009/current-foreign-overlap-form.json')
 claim=reservations.claim('miami-distinct-original-'+str(uuid.uuid4()),['building:'+foreign['uid']],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');profiles=c.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id=%s',(NATIVE_RUN,'B150352589702062G0')).fetchall();assert len(profiles)==1;key,sheet=profiles[0];sha,data=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();mods=[m for m in data['models'] if m['modelId']=='B150352589702062G0'];assert len(mods)==1
   pinned=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
  native={'cacheKey':key,'resultSha':sha,'sheet':sheet,'model':mods[0]};helper=module('miami_foreign_recovery','xl-next-support-recovery-20261005.py');entry,basis=helper.diagnostic_entry(native,foreign);folder=LOCAL/'sheet';directory,_=helper.scan({'SHEETNO':sheet,'Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},folder/'directory',refresh=True);directory['models']=[m for m in directory['models'] if m['modelId']==mods[0]['modelId']];assert len(directory['models'])==1;receipt=helper.acquire(directory,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True)
  with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
   converted=helper._convert_one(z,z.getinfo(mods[0]['sourceEntry']),folder/'decoded',packed,{}, {'modelId':mods[0]['modelId']});raw=helper.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),mods[0]['asset']['sha256'])
  assert digest(raw)==mods[0]['asset']['sha256'];path=LOCAL/'assets'/(digest(raw)+'.glb.gz');path.parent.mkdir(exist_ok=True);path.write_bytes(raw);r={'uid':foreign['uid'],'source':{'building':foreign},'native':native,'modelId':mods[0]['modelId'],'sourceSHA256':digest(raw),'candidate':{'entry':entry,'path':str(path.relative_to(ROOT))},'triangles':mods[0]['triangles']};save(DOC/'exact-distinct-source-selection.json.gz',{'row':r,'sourceLookupBasis':basis,'freshContainer':{k:v for k,v in directory.items() if k!='models'},'acquisition':receipt,'canonicalAssetSHA256':digest(raw)})
  decoder=module('miami_foreign_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;foreigntri=decoder.glb_triangles(r);fsel=read(family/'selection.json.gz');club=next(x for x in fsel['rows'] if x['uid']=='landsd/259038:0');club['triangles']=club['native']['model']['triangles'];decoder.LOCAL=HERE/'local'/family.name;clubtri=decoder.glb_triangles(club);target=shapely.union_all([shapely.Polygon(x['source']['building']['rings'][0],x['source']['building']['rings'][1:]) for x in fsel['rows']]);fp=shapely.union_all(shapely.polygons(foreigntri[:,:,[0,2]]));clubfp=shapely.union_all(shapely.polygons(clubtri[:,:,[0,2]]));excess=clubfp.difference(target)
  offending=read(family/'foreign-podium-every-original-overlap-face.json.gz')['allOffendingOriginalFaces'];ids=[x['faceId'] for x in offending];exact=exact_component_contacts(clubtri,ids,foreigntri,list(range(len(foreigntri))))
  save(DOC/'exact-original-distinct-interface.json.gz',{'foreignUID':foreign['uid'],'foreignSourceSHA256':digest(raw),'foreignTriangles':len(foreigntri),'foreignWorldTriangleSHA256':digest(foreigntri.astype('<f8').tobytes()),'clubSourceSHA256':club['sourceSHA256'],'clubWorldTriangleSHA256':digest(clubtri.astype('<f8').tobytes()),'offendingClubFaceIds':ids,'actualForeignOriginalProjectionExcessOverlapM2':excess.intersection(fp).area,'wholeOriginalClubForeignProjectedOverlapM2':clubfp.intersection(fp).area,'exactSurfaceIntersection':exact,'identityAccepted':False,'physicalAccepted':False,'geometryChanges':0,'qualification':'Independent distinct neighbour source surfaces; projected overlap and exact intersection witnesses never authorize changing current foreign actor or identity grouping.'});print({'actualForeignOriginalProjectionExcessOverlapM2':excess.intersection(fp).area,'wholeOriginalClubForeignProjectedOverlapM2':clubfp.intersection(fp).area,'exactSurfaceContactCount':len(exact['contacts']),'intersectionSummary':{k:v for k,v in exact.items() if k!='contacts'}},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

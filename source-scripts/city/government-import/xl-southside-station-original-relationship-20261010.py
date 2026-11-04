"""New exact source/primary/MTR-station relationship lead; no blanket estate credit."""
import sys,gzip,json,importlib.util,urllib.request,datetime,uuid
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from yoho_eight_related_original_podium_identity_20261009 import ring_poly
sys.path.insert(0,str(HERE.parent/'landsd-territory'));from source import request,BASE
BATCH='government-xl-southside-station-original-relationship-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
UIDS=['landsd/315025:0','landsd/300867:0'];CSUIDS=['3533312006P20240709','3536012138T20160607'];MODELS=['B353331200602063C0','B353601213801063C1']
PATHS=[HERE/'local/government-xl-southside-station-original-recovery-20261010/assets/85be44e7ab9410c850d3b7d59d05df2cd45fc1072ec2f984ddbb7b43c4d9ff7c.glb.gz',HERE/'local/government-xl-southside-station-original-recovery-20261010/assets/2293ba8925406abcdbd848486a772dfa8baa01caf0cfe96e749d5a3cd51210f1.glb.gz']
def query(table,where,name,geometry=False):
 params={'f':'json','where':where,'outFields':'*','returnGeometry':'true' if geometry else 'false','outSR':'2326','resultRecordCount':'1000','orderByFields':'OBJECTID'};raw,rec=request(BASE+'/'+str(table)+'/query',params,json_expected=False);dec=gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw;(DOC/(name+'.json')).write_bytes(dec)
 if raw!=dec:(DOC/(name+'.provider-original.gz')).write_bytes(raw)
 rec.update(decodedSHA256=digest(dec),gzipDecoded=raw!=dec);save(DOC/(name+'.request.json'),rec);obj=json.loads(dec);assert not obj.get('error') and not obj.get('exceededTransferLimit');return obj['features']
def main():
 assert not DOC.exists();claim=reservations.claim('southside-source-relation-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  DOC.mkdir(parents=True);manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());primary=query(0,'BuildingCSUID IN ('+','.join("'"+u+"'" for u in CSUIDS)+')','exact-current-primary',True);relations=query(1002,'BuildingCSUID IN ('+','.join("'"+u+"'" for u in CSUIDS)+')','exact-current-structure-relations');ids=sorted({r['attributes']['BuildingStructureID'] for r in relations});structures=query(1003,'BuildingStructureID IN ('+','.join(map(str,ids))+')','exact-current-structures') if ids else []
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');rows=c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE m->>'modelId' IN ('B353331200602063C0','B353601213801063C1')").fetchall()
  assert len(rows)==2;native=[next({'sourceKey':k+'/'+m['modelId'],'model':m,'sheet':s,'resultSHA256':h} for k,m,s,h in rows if m['modelId']==model) for model in MODELS];tri=[]
  for model,p in zip(native,PATHS):raw=p.read_bytes();assert digest(raw)==model['model']['asset']['sha256'];tri.append(decode_original_world_triangles(raw))
  contacts=exact_component_contacts(tri[0],list(range(len(tri[0]))),tri[1],list(range(len(tri[1]))),maximum_pairs=1000000);save(DOC/'complete-original-contacts.json.gz',contacts)
  s=importlib.util.spec_from_file_location('tung_sing_current_foreign_forms',HERE/'xl-final-script-pass.py');final=importlib.util.module_from_spec(s);s.loader.exec_module(final);alltri=np.concatenate(tri);lo,hi=alltri.min(axis=(0,1)),alltri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);own=next(b for b,_,_ in forms if b['uid']==UIDS[0]);other=next(b for b,_,_ in forms if b['uid']==UIDS[1]);target=ring_poly(own['rings']);foreign=ring_poly(other['rings']);projection=shapely.union_all(shapely.polygons(tri[0][:,:,[0,2]]));overlap=projection.difference(target).intersection(foreign);ids=[]
  for i,t in enumerate(tri[0]):
   if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area>0:ids.append(i)
  evidence=[]
  urls=[('mtr-shopping-malls.html','https://www.mtr.com.hk/en/corporate/properties/mtrshopping_centres.html'),('southside-owner-transport.html','https://www.thesouthside.com.hk/en/transportation'),('station-original-plan.pdf','https://www.mtr.com.hk/archive/ch/services/layouts/wch.pdf')]
  for name,url in urls:
   req=urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-source-provenance/1.0'})
   with urllib.request.urlopen(req,timeout=60) as response:data=response.read();headers=dict(response.headers);resolved=response.url
   assert data.startswith(b'%PDF-') if name.endswith('.pdf') else len(data)>1000;(DOC/name).write_bytes(data);rec={'url':url,'resolvedURL':resolved,'retrievedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(data),'sha256':digest(data),'responseHeaders':headers};save(DOC/(name+'.request.json'),rec);evidence.append(rec)
  hashes={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in PATHS};hashes['3d-viewer/city/data/manifest.json']=msha;hashes.update({'3d-viewer/'+u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in forms});assert digest(manifest.read_bytes())==msha
  save(DOC/'diagnostic.json.gz',{'uids':UIDS,'native':native,'primary':primary,'exactRelations':relations,'exactStructures':structures,'completeCurrentForms':[b for b,_,_ in forms],'wholeOriginalWorldSHA256s':[digest(t.astype('<f8').tobytes()) for t in tri],'completeSourceFaceCounts':[len(t) for t in tri],'towerExcessIntoNamedPodiumM2':overlap.area,'allOverlapOriginalFaceIds':ids,'allOverlapOriginalFaces':tri[0][ids].tolist(),'positiveOriginalContactCount':sum(q['dimension']>0 for q in contacts['contacts']),'exactOriginalContactsPath':str((DOC/'complete-original-contacts.json.gz').relative_to(ROOT)),'primaryURLs':evidence,'inputHashes':hashes,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'qualification':'Specific exact source/primary/owner-plan relationship research. Distinct current parent IDs, ownership and every other current actor retained. No invented OP relation, same-estate blanket waiver, actor suppression or contact/support/physical credit.'})
  print({'uids':UIDS,'completeSourceFaces':[len(t) for t in tri],'positiveOriginalContacts':sum(q['dimension']>0 for q in contacts['contacts']),'originalOverlapFaces':len(ids),'overlapM2':overlap.area,'structureRelations':len(relations),'accepted':False},flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()

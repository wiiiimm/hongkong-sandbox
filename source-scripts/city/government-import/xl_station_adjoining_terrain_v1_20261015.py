"""Recover adjoining original terrain selected by sheet-index intersection."""
import importlib.util,uuid,zipfile
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-station-adjoining-terrain-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
MODEL='B360171738601063C0';INDEX=HERE.parent/'landmark-acquisition/index.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not LOCAL.exists()
 source=next(r for r in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if r['modelId']==MODEL);asset=ROOT/source['asset']['path'];assert ref(asset)==source['asset'];tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));region=box(lo[0]+834500-2,816500-hi[2]-2,hi[0]+834500+2,816500-lo[2]+2)
 index=read(INDEX);assert index['spatialReference']['wkid']==2326 and index['completePagination'];sheets=[f['attributes']for f in index['features']if Polygon(f['geometry']['rings'][0]).intersects(region)];names=sorted(f['SHEETNO']for f in sheets);assert len(names)==4
 prior=read(BASE/'government-xl-unmapped-native-terrain-v1-20261015/result.json');existing={r['sheet']:r for r in prior['rows']};missing=[f for f in sheets if f['SHEETNO']not in existing]
 claim=reservations.claim('station-adjoining-'+str(uuid.uuid4()),['native-model:'+source['sourceKey']]+['immutable-source-sheet:'+f['SHEETNO']for f in missing],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);save(DOC/'selection.json',{'sourceKey':source['sourceKey'],'index':ref(INDEX),'source':source['asset'],'boundsHK1980':list(region.bounds),'selectedSheets':sheets,'missingSheets':[f['SHEETNO']for f in missing]})
  stage='original-station-four-sheet-terrain-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,{'sourceKey':source['sourceKey'],'sheets':names});job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=3600);assert job and job['id']==jid
  spec=importlib.util.spec_from_file_location('station_adjoining_context',HERE/'xl-final-script-pass.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.s.LOCAL=LOCAL
  refs=[ref(Path(__file__)),ref(INDEX),ref(asset),ref(BASE/'government-xl-unmapped-native-terrain-v1-20261015/result.json')];terrainPaths=[ROOT/p for sheet,r in existing.items()if sheet in names for p in r['terrainPaths']];acquisitions=[]
  for attrs in missing:
   sheet=attrs['SHEETNO'];folder=LOCAL/sheet;directory,_=f.s.recovery.scan(attrs,folder/'directory');directory['models']=[];record=f.s.acquire(directory,folder/'directory/zip-directory.bin',folder/'original',include_terrain=True);acquisitions.append(record)
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip'))as z:
    for name in z.namelist():
     if name.startswith('TERRAIN')and name.endswith(('.gltf','.bin')):
      p=folder/'terrain'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));refs.append(ref(p))
      if name.endswith('.gltf'):terrainPaths.append(p)
   refs.extend(ref(folder/p)for p in ['directory/result.json','directory/zip-directory.bin','original/download.json']);assert reservations.heartbeat(lease)['ok'];print('Acquired',sheet,flush=True)
  terrain=np.concatenate([f.s.terrain_triangles(p)for p in terrainPaths]);binding=next(r for r in read(BASE/'government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json')['rows']if r['modelId']==MODEL);form=binding['bindings'][0]['viewerForm'];foundation=f.foundation_context(tri,terrain,f.form_polygon(form));save(DOC/'diagnostic.json',{'modelId':MODEL,'sourceSHA256':source['sourceSHA256'],'sheets':names,'terrainPaths':[str(p.relative_to(ROOT))for p in terrainPaths],'nativeTerrainFaces':len(terrain),'foundationDiagnostic':foundation,'installationApproved':False});refs.extend(ref(p)for p in DOC.iterdir()if p.is_file());refs.extend(ref(p)for p in (LOCAL/'terrain-repairs').rglob('*')if p.is_file())
  for q in refs:assert ref(ROOT/q['path'])==q
  result={'jobId':jid,'sourceKey':source['sourceKey'],'sourceSHA256':source['sourceSHA256'],'sheets':names,'acquisitions':acquisitions,'foundationDiagnostic':foundation,'evidenceRefs':refs,'newlyInstalled':0,'sourceGeometryChanges':0,'publicationApproved':False,'qualification':'Four-sheet original terrain diagnostic, all source faces tested at vertices and centroid. No continuous acceptance or live terrain replacement.'}
  with connect()as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease);assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);print('COMPLETE',jid,foundation,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

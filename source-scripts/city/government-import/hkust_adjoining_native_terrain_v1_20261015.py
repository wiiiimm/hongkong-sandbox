"""Acquire exact government sheet terrain and diagnose both unchanged HKUST originals."""
from pathlib import Path
import zipfile,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-hkust-adjoining-native-terrain-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PACKET=BASE/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014';CACHE=HERE/'local/government-xl-eight-further-original-closures-20261008/sheets/12-NW-6A/directory'
def main():
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim('hkust-native-'+str(uuid.uuid4()),['original-terrain-acquisition:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);f=module('hkust_existing_native_pipeline',HERE/'xl-final-script-pass.py');f.s.LOCAL=LOCAL
  from shapely.geometry import Polygon,box
  olddoc=BASE/'government-xl-hkust-native-terrain-foundation-v1-20261015';oldresult=read(olddoc/'result.json');pins={x['path']:x['sha256'] for x in oldresult['evidenceRefs']};oldground=olddoc/'native-ground.json.gz';assert digest(oldground.read_bytes())==pins[str(oldground.relative_to(ROOT))];old=read(oldground);baseground=np.array(old['completeOriginalTerrainTriangles'])
  source=read(BASE/'government-xl-hkust-pair-current-ground-v1-20261015/source-input.json.gz');v=np.array(source['sourceWorlds'][0]['position']).reshape(-1,3);lo,hi=v.min(0),v.max(0);region=box(lo[0]+834500-2,816500-hi[2]-2,hi[0]+834500+2,816500-lo[2]+2)
  indexpath=HERE.parent/'landmark-acquisition/index.json';index=read(indexpath);assert index['spatialReference']['wkid']==2326 and index['completePagination'];attrs=[x['attributes'] for x in index['features'] if Polygon(x['geometry']['rings'][0]).intersects(region)];assert any(x['SHEETNO']=='12-NW-6A' for x in attrs);missing=[x for x in attrs if x['SHEETNO']!='12-NW-6A'];assert missing
  save(DOC/'sheet-selection.json',{'indexSHA256':digest(indexpath.read_bytes()),'boundsHK1980':list(region.bounds),'selectedSheets':[x['SHEETNO'] for x in attrs]});paths=[Path(__file__),oldground,olddoc/'result.json',indexpath,BASE/'government-xl-hkust-pair-current-ground-v1-20261015/source-input.json.gz'];terrain=[]
  for attr in missing:
   sheet=attr['SHEETNO'];folder=LOCAL/sheet;directory,_=f.s.recovery.scan(attr,folder/'directory');directory['models']=[];acquired=f.s.acquire(directory,folder/'directory/zip-directory.bin',folder/'original',include_terrain=True);save(DOC/(sheet+'-acquisition.json'),acquired)
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
    for name in z.namelist():
     if name.startswith('TERRAIN') and name.endswith(('.gltf','.bin')):
      p=folder/'terrain'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));paths.append(p)
      if name.endswith('.gltf'):terrain.append(p)
   paths.extend(folder/x for x in ['directory/result.json','directory/zip-directory.bin','original/download.json']);assert reservations.heartbeat(lease,ttl=3600)['ok'];print('Acquired',sheet,flush=True)
  ground=np.concatenate([baseground]+[f.s.terrain_triangles(p) for p in terrain]);assert np.isfinite(ground).all();save(DOC/'native-ground.json.gz',{'completeOriginalTerrainTriangles':ground.tolist(),'terrainPaths':old['terrainPaths']+[str(p.relative_to(ROOT)) for p in terrain],'terrainGeometryChanges':0})
  prior=read(BASE/'government-xl-hkust-uncovered-target-partition-v1-20261015/result.json');pins={r['path']:r['sha256'] for r in prior['evidenceRefs']};reportp=PACKET/'two-original-scope-interface-output-v1/result.json';assert digest(reportp.read_bytes())==pins[str(reportp.relative_to(ROOT))];report=read(reportp);forms={x['uid']:x for x in report['currentAllSixFormsVerbatim']};rows=[];paths += [reportp,BASE/'government-xl-hkust-uncovered-target-partition-v1-20261015/result.json']
  for ref in report['arrayRefs']:
   p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];a=read(p);s=a['sourceTuple'];asset=ROOT/s['originalAssetPath'];assert digest(asset.read_bytes())==s['sourceSHA256'];tri=np.asarray(a['completeOrderedOriginalTriangles']);assert len(tri)==s['originalFaces'];foot=f.form_polygon(forms[s['uid']]);foundation=f.foundation_context(tri,ground,foot);rows.append({'uid':s['uid'],'sourceSHA256':s['sourceSHA256'],'originalFaces':len(tri),'nativeTerrainFaces':len(ground),'foundation':foundation});paths += [p,asset];assert reservations.heartbeat(lease,ttl=3600)['ok'];print(s['uid'],foundation,flush=True)
  save(DOC/'foundation.json',{'rows':rows,'qualification':'Existing source-native foundation diagnostic only, no live terrain, complete-continuous/four-world or neighbour acceptance.'});paths.extend(p for p in (LOCAL/'terrain-repairs').rglob('*') if p.is_file())
  module('hkust_native_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'hkust-original-native-terrain-foundation-v1',paths,{'uids':report['uids'],'rows':rows,'sourceGeometryChanges':0,'nextStep':'If native ground resolves burial, prepare a source-preserving private patch with full affected-parent scope; otherwise attribute concrete remaining source/native failures. Identity gap and support review remain independent.'})
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

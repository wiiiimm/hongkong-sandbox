"""Stream the verified LandsD source through the existing Astra component converter.
Writes staging tiles only; does not replace live city data or merge OSM forms.
"""
from __future__ import annotations
import collections,hashlib,importlib.util,json,pathlib,tempfile,time
from pyproj import Transformer
from retain import iter_features
from source import HERE,ROOT,DOCS,read_json,save_json,atomic,encode,digest,utc

OUT=ROOT/'3d-viewer/city/data/landsd-territory';TILE_SIZE=2000

def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
shared=load_module('astra_landsd_converter',ROOT/'source-scripts/city/mui-wo-buildings/build.py')
dem_module=load_module('astra_dem_sampler',ROOT/'source-scripts/city/mui-wo-buildings/fine_terrain_audit.py')
project=Transformer.from_crs(4326,2326,always_xy=True)

def native_feature(feature):
 """Only coordinate/format adaptation; shared stage_feature owns all geometry policy."""
 geometry=feature['geometry'];polygons=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates'];rings=[]
 for polygon in polygons:
  for ring in polygon:
   east,north=project.transform(*zip(*[point[:2] for point in ring]));rings.append(list(map(list,zip(east,north))))
 return {'attributes':dict(feature['properties']),'geometry':{'rings':rings}}

class CurrentTerrain:
 def __init__(self):
  self.sources=[];self.grids=[]
  for name in ['terrain.json','terrain-mui-wo.json']:
   path=ROOT/'3d-viewer/city/data'/name;data=read_json(path);sampler=dem_module.DemSampler(data,path);g=sampler.g
   bounds=[g['bE']-834500,816500-g['bN'],g['bE']+(data['w']-1)*g['aE']-834500,816500-(g['bN']+(data['h']-1)*g['aN'])]
   self.grids.append((bounds,sampler,abs(g['aE'])));self.sources.append({'file':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'resolution':abs(g['aE'])})
 def sample(self,p):
  points=[(x,z) for ring in [p.exterior,*p.interiors] for x,z in ring.coords];points.append((p.centroid.x,p.centroid.y));values=[];resolutions=set()
  for x,z in points:
   match=next(((sampler,resolution) for (x0,z0,x1,z1),sampler,resolution in reversed(self.grids) if x0<=x<=x1 and z0<=z<=z1),None)
   if match is None:raise ValueError('Official footprint point outside current terrain '+str([x,z]))
   sampler,resolution=match;values.append(sampler.ground(x,z));resolutions.add(resolution)
  return {'min':round(min(values),3),'max':round(max(values),3),'centre':round(values[-1],3),'method':'Sampled footprint vertices and centroid on current rendered terrain; not exhaustive triangle extrema','resolutions':sorted(resolutions),'sampleCount':len(points)}

class TileSpool:
 def __init__(self,folder):self.folder=folder;self.handles=collections.OrderedDict();self.keys=set()
 def append(self,key,record):
  if key not in self.handles:
   if len(self.handles)>=32:self.handles.popitem(last=False)[1].close()
   self.handles[key]=(self.folder/(key+'.jsonl')).open('ab')
  self.handles.move_to_end(key);self.handles[key].write(encode(record)+b'\n');self.keys.add(key)
 def close(self):
  for file in self.handles.values():file.close()
  self.handles.clear()

def compact(record):
 record=dict(record);terrain=record.pop('terrain');record.pop('sourceAttributes');record.pop('source',None)
 record['sourceDataset']='landsd-territory';record['terrainAudit']={key:terrain[key] for key in ['roofWhollyBelowTerrain','roofPartlyBelowTerrain','baseWhollyAboveTerrain']}
 record['terrainAudit'].update(sampled=True,resolutions=terrain['resolutions'])
 return record,terrain


def main():
 started=utc();clock=time.monotonic();source=read_json(HERE/'manifest.json');path=ROOT/source['snapshot']['file']
 if digest(path.read_bytes())!=source['snapshot']['compressedSHA256']:raise ValueError('Unverified source archive')
 terrain=CurrentTerrain();counts=collections.Counter();source_ids=set();all_uids=set();conflicts=[];repairs=[];tiles=[];counts_by_type=collections.Counter()
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'tiles').mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='tile-spool-',dir=HERE) as folder:
  spool=TileSpool(pathlib.Path(folder))
  try:
   for feature in iter_features(path):
    oid=feature['properties']['OBJECTID'];components=list(shared.stage_feature(native_feature(feature),terrain.sample,tile_size=TILE_SIZE))
    if not components:raise ValueError('No valid polygon component for source OBJECTID '+str(oid))
    source_ids.add(oid);counts['sourceRecords']+=1
    for original in components:
     b,t=compact(original)
     if b['uid'] in all_uids:raise ValueError('Duplicate component '+b['uid'])
     all_uids.add(b['uid']);spool.append(b['tile'],b);counts['components']+=1;counts['height:'+b['heightSource']]+=1;counts['base:'+b['baseSource']]+=1;counts_by_type[b['structureType']]+=1;counts['vertices']+=sum(map(len,b['rings']));counts['holes']+=len(b['rings'])-1
     for key in ['roofWhollyBelowTerrain','roofPartlyBelowTerrain','baseWhollyAboveTerrain']:
      counts[key]+=t[key]
     if b['geometryRepaired']:repairs.append({'uid':b['uid'],'OBJECTID':oid})
     if t['roofPartlyBelowTerrain'] or t['baseWhollyAboveTerrain']:
      conflicts.append({'uid':b['uid'],'structureType':b['structureType'],'heightSource':b['heightSource'],'base':b['base'],'top':b['renderTopHeight'],'terrain':t})
    if counts['sourceRecords']%25000==0:
     progress={'sourceRecords':counts['sourceRecords'],'components':counts['components'],'elapsedSeconds':round(time.monotonic()-clock,1)};save_json(DOCS/'staging-progress.json',progress);print(json.dumps(progress),flush=True)
  finally:spool.close()
  advertised=set(read_json(HERE/'query-object-ids.json')['objectIds'])
  if source_ids!=advertised:raise ValueError('Staged source IDs differ from verified official membership')
  for key in sorted(spool.keys):
   with (pathlib.Path(folder)/(key+'.jsonl')).open() as file:buildings=[json.loads(line) for line in file]
   x,z=map(int,key.split('_'));bounds=[x*TILE_SIZE,z*TILE_SIZE,(x+1)*TILE_SIZE,(z+1)*TILE_SIZE]
   for b in buildings:
    for ring in b['rings']:
     for px,pz in ring:bounds=[min(bounds[0],px),min(bounds[1],pz),max(bounds[2],px),max(bounds[3],pz)]
   payload={'id':key,'bounds':bounds,'buildings':buildings,'sourceDataset':'landsd-territory'};content=encode(payload);target=OUT/'tiles'/(key+'.json');atomic(target,content)
   tiles.append({'id':key,'bounds':bounds,'centre':[(x+.5)*TILE_SIZE,(z+.5)*TILE_SIZE],'url':'city/data/landsd-territory/tiles/'+key+'.json','bytes':len(content),'sha256':digest(content),'counts':{'buildings':len(buildings),'heights':dict(collections.Counter(b['heightSource'] for b in buildings))}})
 supplemental={'provider':'Lands Department, Hong Kong SAR Government','datasetId':source['datasetId'],'datasetVersion':source['datasetVersion'],'sourceUrl':source['serviceURL'],'metadataUrl':source['metadataURL'],'specificationUrl':source['specificationURL'],'licenceUrl':'https://portal.csdi.gov.hk/csdi-webpage/doc/TNC','rawSource':source['snapshot'],'provenance':'Reused existing original public source bytes; no other-model implementation or rendered output copied.'}
 result={'schemaVersion':1,'stagingOnly':True,'origin':[834500,816500],'crs':'EPSG:2326','verticalDatum':'HKPD','tileSize':TILE_SIZE,'startedAtUTC':started,'completedAtUTC':utc(),'elapsedSeconds':round(time.monotonic()-clock,1),'sourceDataset':'landsd-territory','sources':[supplemental],'terrainSources':terrain.sources,'counts':dict(counts),'structureTypes':dict(counts_by_type),'tiles':tiles,'geometryPolicy':'Original official GeoJSON polygons transformed with existing PROJ, then existing Astra stage_feature validity repair/containment and millimetre packing with finer precision where needed to preserve topology. Full original source retained. No simplification or omission by structure type, area, names or missing heights. Components remain whole at tile boundaries.','heightPolicy':'Shared Astra source-height policy: approximate recorded BaseHeight/TopHeight stay absolute HKPD. Missing values alone use labelled defaults and current rendered terrain estimates; no lifting of recorded buildings.','terrainPolicy':'Cheap vertex-and-centroid samples use the existing terrain interpolation: 70 m across Hong Kong and current 5 m Mui Wo patch where present. Conflict flags are sample-based diagnostics, not exhaustive roof/terrain intersection proof.','sourceRecordsRepresented':len(source_ids),'allAdvertisedIdsRepresented':True,'geometryRepairedComponents':len(repairs),'outputBytes':sum(t['bytes'] for t in tiles),'noOSMMerge':True}
 save_json(OUT/'manifest.json',result);save_json(DOCS/'staging-verification.json',result);save_json(DOCS/'geometry-repairs.json',repairs);save_json(DOCS/'terrain-conflicts.json',{'note':result['terrainPolicy'],'counts':{k:counts[k] for k in ['roofWhollyBelowTerrain','roofPartlyBelowTerrain','baseWhollyAboveTerrain']},'buildings':conflicts})
 print(json.dumps({'complete':True,'counts':dict(counts),'tiles':len(tiles),'bytes':result['outputBytes'],'elapsedSeconds':result['elapsedSeconds']}),flush=True)

if __name__=='__main__':main()

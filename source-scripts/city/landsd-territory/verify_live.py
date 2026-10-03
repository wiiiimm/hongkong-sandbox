"""Read-only live-tile audit against frozen official source, staging and OSM baseline.
Writes only docs/astra-city/landsd-territory/live-verification.json.
Run after the root's publish completes. No geometry is modified or repaired here.
"""
from __future__ import annotations
import argparse,collections,hashlib,importlib.util,json,math,subprocess,tarfile,time,urllib.parse,urllib.request
from shapely.geometry import Polygon
from shapely.strtree import STRtree
from retain import iter_features
from source import HERE,ROOT,DOCS,BASE,DATASET,read_json,save_json,digest,encode,utc
OUT=ROOT/'3d-viewer/city/data'
EXPECTED_IDS=342223
EXPECTED_COMPONENTS=342225

def rings_hash(rings):return digest(encode(rings))
def finite(v):return isinstance(v,(int,float)) and math.isfinite(v)
def close(a,b):return abs(a-b)<.00001

def baseline_features(commit):
 process=subprocess.Popen(['git','archive',commit,'3d-viewer/city/data/tiles'],cwd=ROOT,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=process.stdout,mode='r|') as archive:
  for member in archive:
   if member.isfile() and member.name.endswith('.json'):
    yield from json.load(archive.extractfile(member))['buildings']
 if process.wait()!=0:raise RuntimeError('Could not read frozen OSM baseline')

def check_urls(records,manifest):
 source=manifest['supplementalSources'][0]
 assert source['datasetId']==DATASET and source['sourceUrl']==BASE+'/0'
 selected=sorted({min(records),max(records),174478,335513})
 parameters={'f':'json','objectIds':','.join(map(str,selected)),'outFields':'OBJECTID,BuildingCSUID,BaseHeight,TopHeight,BuildingBlockType','returnGeometry':'false'}
 url=BASE+'/0/query?'+urllib.parse.urlencode(parameters)
 results=[]
 req=urllib.request.Request(url,headers={'User-Agent':'HongKongSandbox-Astra/read-only live integration audit'})
 with urllib.request.urlopen(req,timeout=30) as response:
  raw=response.read();data=json.loads(raw);status=response.status
 assert not data.get('error');features={f['attributes']['OBJECTID']:f['attributes'] for f in data['features']};assert set(features)==set(selected)
 for oid,a in features.items():
  b=records[oid][0];assert a['BuildingCSUID']==b['buildingCSUID'];assert a['BaseHeight']==b['baseHeightHKPD'];assert a['TopHeight']==b['topHeightHKPD'];assert a['BuildingBlockType']==b['structureType']
 results.append({'url':url,'status':status,'objectIds':selected,'sourceAttributesMatch':True,'sha256':digest(raw)})
 with urllib.request.urlopen(source['licenceUrl'],timeout=30) as response:
  raw=response.read();assert response.status==200;results.append({'url':source['licenceUrl'],'status':response.status,'sha256':digest(raw)})
 return results

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--skip-network',action='store_true');args=parser.parse_args();started=utc();clock=time.monotonic()
 manifest_path=OUT/'manifest.json';manifest_raw=manifest_path.read_bytes();manifest=json.loads(manifest_raw);integration=read_json(DOCS/'integration.json');staging=read_json(OUT/'landsd-territory/manifest.json');source=read_json(HERE/'manifest.json')
 assert manifest['officialCoverage']['area']=='Hong Kong territory','Wait for complete root publication'
 assert manifest['officialCoverage']['sourceRecords']==EXPECTED_IDS and manifest['officialCoverage']['renderedComponents']==EXPECTED_COMPONENTS
 model_source=read_json(ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample/model-geometries.json')['byBuildingUid'];models_seen=set()
 native={b['uid']:b for b in read_json(OUT/'mui-wo-buildings.json')['buildings']}
 fine={b['uid']:b for b in read_json(ROOT/'docs/astra-city/mui-wo-buildings/fine-terrain-audit.json')['buildings']}
 converter_path=ROOT/'source-scripts/city/mui-wo-buildings/build.py';spec=importlib.util.spec_from_file_location('live_check_height_policy',converter_path);converter=importlib.util.module_from_spec(spec);spec.loader.exec_module(converter)
 records=collections.defaultdict(list);live={};official_polys=[];official_uids=[];retained_osm={};totals=collections.Counter();heights=collections.Counter();types=collections.Counter();sources=collections.Counter();tile_ids=set();url_ids=set();tile_hashes={};model_bound_warnings=[];rounded_centre_boundaries=[]
 for metadata in manifest['tiles']:
  key=metadata['id'];assert key not in tile_ids and metadata['url'] not in url_ids;tile_ids.add(key);url_ids.add(metadata['url'])
  path=ROOT/'3d-viewer'/metadata['url'];raw=path.read_bytes();assert len(raw)==metadata['bytes'],key;tile=json.loads(raw);assert tile['id']==key;assert tile['bounds']==metadata['bounds'];tile_hashes[key]=digest(raw)
  x0,z0,x1,z1=metadata['bounds'];tile_counts=collections.Counter(b['heightSource'] for b in tile['buildings']);assert dict(tile_counts)==metadata['counts']['heights']
  for name in ['buildings','roads','parks']:assert len(tile[name])==metadata['counts'][name];totals[name]+=len(tile[name])
  for b in tile['buildings']:
   uid=b['uid'];assert uid not in live,uid;assert b['tile']==key,(uid,key);assert all(finite(n) for n in [b['base'],b['height'],*b['centre']]);assert b['height']>0
   assert all(ring and ring[0]==ring[-1] for ring in b['rings']);assert all(finite(x) and finite(z) and x0-.000001<=x<=x1+.000001 and z0-.000001<=z<=z1+.000001 for ring in b['rings'] for x,z in ring)
   p=Polygon(b['rings'][0],b['rings'][1:]);assert p.is_valid and not p.is_empty and p.area>0,uid
   expected_tile=f'{math.floor(p.centroid.x/manifest["tileSize"])}_{math.floor(p.centroid.y/manifest["tileSize"])}';assert expected_tile==key,(uid,expected_tile,key)
   rounded_tile=f'{math.floor(b["centre"][0]/manifest["tileSize"])}_{math.floor(b["centre"][1]/manifest["tileSize"])}'
   if rounded_tile!=key:rounded_centre_boundaries.append({'uid':uid,'tile':key,'roundedCentre':b['centre'],'actualCentroid':[p.centroid.x,p.centroid.y]})
   compact={k:b.get(k) for k in ['id','uid','tile','objectId','buildingCSUID','structureType','sourceDataset','baseHeightHKPD','topHeightHKPD','base','height','heightSource','baseSource','minimum','heightRule','osmRef','osmRefs','parent']};compact['geometryHash']=rings_hash(b['rings']);live[uid]=compact;heights[b['heightSource']]+=1
   if b['id'].startswith('landsd/'):
    assert b['id']==f'landsd/{b["objectId"]}';assert b['minimum']==0;assert b['heightRule'] in manifest['heightRules'] and manifest['heightRules'][b['heightRule']]
    assert b['sourceDataset'] in ['landsd-territory','landsd-mui-wo'];sources[b['sourceDataset']]+=1;records[b['objectId']].append(compact);types[b['structureType']]+=1;official_polys.append(p);official_uids.append(uid)
    if b['sourceDataset']=='landsd-mui-wo':
     assert uid in native and uid in fine;expected=converter.render_elevations(native[uid]['sourceAttributes'],fine[uid]['fineTerrain']);assert b['base']==expected['base'] and close(b['height'],expected['height']);assert compact['geometryHash']==rings_hash(native[uid]['rings'])
    if 'modelGeometry' in b:
     assert uid in model_source and b['modelGeometry']==model_source[uid];models_seen.add(uid);model=b['modelGeometry'];assert model['buildingCSUID']==b['buildingCSUID'];assert model['source'] in model['sourceHashes']
     position=model['position'];assert len(position)==len(model['normal']) and len(position)%9==0;assert all(finite(n) for n in position);assert all(finite(n) for n in model['normal'])
     if any(not (x0<=position[i]<=x1 and z0<=position[i+2]<=z1) for i in range(0,len(position),3)):model_bound_warnings.append(uid)
   else:retained_osm[uid]=p
 assert dict(heights)==manifest['counts']['heights'];assert all(totals[k]==manifest['counts'][k] for k in totals)
 assert len(records)==EXPECTED_IDS and len(official_polys)==EXPECTED_COMPONENTS;assert models_seen==set(model_source) and len(models_seen)==275
 print(json.dumps({'phase':'live tiles','sourceIds':len(records),'officialComponents':len(official_polys),'allForms':len(live),'models':len(models_seen)}),flush=True)
 checkpoint_path=DOCS/'live-verification.json';previous=read_json(checkpoint_path).get('sourceStageCheckpoint',{}) if checkpoint_path.exists() else {}
 geometry_digest=hashlib.sha256()
 for uid in sorted(live):geometry_digest.update(encode({k:v for k,v in live[uid].items() if k not in ['heightRule','osmRef','osmRefs','parent']}))
 geometry_signature=geometry_digest.hexdigest();stage_fingerprint=digest((OUT/'landsd-territory/manifest.json').read_bytes());source_fingerprint=source['snapshot']['compressedSHA256']
 can_reuse=previous.get('geometrySignature')==geometry_signature and previous.get('stageManifestSHA256')==stage_fingerprint and previous.get('sourceSHA256')==source_fingerprint
 stage_uids=set();stage_geometry_identical=0;preferred_geometry=0
 if can_reuse:
  stage_geometry_identical=previous['unchangedTerritoryGeometryAndRenderElevations'];preferred_geometry=previous['preferredMuiWoRecords'];source_types=collections.Counter(previous['sourceTypes']);source_nulls=collections.Counter(previous['sourceNullFields'])
 else:
  for tile in staging['tiles']:
   for b in read_json(ROOT/'3d-viewer'/tile['url'])['buildings']:
    uid=b['uid'];assert uid in live and uid not in stage_uids;stage_uids.add(uid);current=live[uid]
    for name in ['objectId','buildingCSUID','structureType','baseHeightHKPD','topHeightHKPD']:assert current[name]==b[name],(uid,name)
    if current['sourceDataset']=='landsd-mui-wo':preferred_geometry+=1
    else:
     assert current['geometryHash']==rings_hash(b['rings']);assert current['base']==b['base'] and close(current['height'],b['height']);assert current['heightSource']==b['heightSource'];stage_geometry_identical+=1
  assert stage_uids==set(official_uids)
  checked=set();source_types=collections.Counter();source_nulls=collections.Counter()
  for feature in iter_features(HERE/'landsd-hong-kong-source.geojson.gz'):
   a=feature['properties'];oid=a['OBJECTID'];assert oid in records and oid not in checked;checked.add(oid);source_types[a['BuildingBlockType']]+=1
   for name in ['BaseHeight','TopHeight']:source_nulls[name]+=a[name] is None
   for b in records[oid]:
    assert b['buildingCSUID']==a['BuildingCSUID'];assert b['structureType']==a['BuildingBlockType'];assert b['baseHeightHKPD']==a['BaseHeight'];assert b['topHeightHKPD']==a['TopHeight']
    if a['BaseHeight'] is not None and a['TopHeight'] is not None and a['TopHeight']>a['BaseHeight']:
     assert b['heightSource']=='landsd' and b['base']==a['BaseHeight'] and close(b['height'],a['TopHeight']-a['BaseHeight'])
    else:assert b['heightSource']=='estimated',b['uid']
  assert checked==set(records)==set(read_json(HERE/'query-object-ids.json')['objectIds']);assert len(checked)==read_json(HERE/'query-count.json')['count']
  assert dict(source_types)==source['validation']['buildingTypes'];assert dict(source_nulls)=={k:source['validation']['nullFields'][k] for k in source_nulls}
  assert manifest['supplementalSources'][0]['sha256']==source['snapshot']['compressedSHA256'];assert digest((HERE/'landsd-hong-kong-source.geojson.gz').read_bytes())==source['snapshot']['compressedSHA256']
 print(json.dumps({'phase':'source and stage','sourceTypes':dict(source_types),'nullFields':dict(source_nulls)}),flush=True)
 checkpoint={'geometrySignature':geometry_signature,'stageManifestSHA256':stage_fingerprint,'sourceSHA256':source_fingerprint,'unchangedTerritoryGeometryAndRenderElevations':stage_geometry_identical,'preferredMuiWoRecords':preferred_geometry,'sourceTypes':dict(source_types),'sourceNullFields':dict(source_nulls),'sourceComparisonComplete':True}
 save_json(checkpoint_path,{'result':'checking-overlaps','sourceStageCheckpoint':checkpoint,'startedAtUTC':started,'note':'Source/stage checks complete; final overlap, metadata and source URL checks pending.'})
 # Recompute the published threshold for every original OSM form, independently
 # of the integration script's removed list. Retain edge evidence rather than alter it.
 tree=STRtree(official_polys);removed=set();retained=set();edge_rows=[];baseline_ids=set();all_pairs=0;overlay_repairs=[];strong_refs=collections.defaultdict(set)
 for ordinal,b in enumerate(baseline_features(integration['osmBaselineCommit'])):
  uid=b['uid'];assert uid not in baseline_ids;baseline_ids.add(uid);p=Polygon(b['rings'][0],b['rings'][1:]);overlaps=[]
  if not p.is_valid:p=p.buffer(0);overlay_repairs.append(uid)
  assert not p.is_empty,uid
  for index in tree.query(p):
   q=official_polys[index];area=p.intersection(q).area
   if area>.01:
    of,lf=area/p.area,area/q.area;overlaps.append((int(index),area,of,lf))
    if of>=.5 or lf>=.5:strong_refs[official_uids[index]].update(oid for oid in [b['id'],b.get('parent')] if oid)
  replace=any(osm_fraction>=.15 or official_fraction>=.5 for _,_,osm_fraction,official_fraction in overlaps)
  if replace:removed.add(uid);assert uid not in live,uid
  else:
   retained.add(uid);assert uid in retained_osm,uid
   if overlaps:
    all_pairs+=len(overlaps);edge_rows.append({'osmUid':uid,'officialMatches':[{'uid':official_uids[i],'areaSquareMetres':round(area,3),'osmFraction':round(of,6),'officialFraction':round(lf,6)} for i,area,of,lf in overlaps]})
  if ordinal and ordinal%40000==0:print(json.dumps({'phase':'independent OSM overlap audit','checked':ordinal}),flush=True)
 assert removed==set(integration['replacedOSMUids']);assert retained==set(retained_osm);assert len(baseline_ids)==117062;assert len(edge_rows)==integration['retainedEdgeOverlapOSMForms']
 for uid,refs in strong_refs.items():assert set(live[uid].get('osmRefs') or [])==refs,(uid,'Strong OSM aliases incomplete')
 assert len(removed)==manifest['officialCoverage']['replacedOSMForms'];assert len(retained)==manifest['officialCoverage']['retainedOSMForms']
 # All internal metadata codes resolve without per-feature URL duplication.
 source_probes=[] if args.skip_network else check_urls(records,manifest)
 assert digest(manifest_path.read_bytes())==digest(manifest_raw),'Live manifest changed during verification; rerun against a stable publication'
 result={'result':'passed','sourceStageCheckpoint':checkpoint,'reusedSourceStageCheckpoint':can_reuse,'startedAtUTC':started,'completedAtUTC':utc(),'elapsedSeconds':round(time.monotonic()-clock,3),'liveManifestSHA256':digest(manifest_raw),'liveTileHashes':tile_hashes,'counts':{'sourceIDs':len(records),'officialComponents':len(official_polys),'retainedOSMForms':len(retained),'replacedOSMForms':len(removed),'cityForms':len(live),'tiles':len(tile_ids),'detailedModels':len(models_seen),'sourceTypes':dict(source_types),'componentTypes':dict(types),'sourceNullFields':dict(source_nulls),'sourceDatasets':dict(sources),'heightSources':dict(heights)},'roundedCentreBoundaryCases':rounded_centre_boundaries,'stageComparison':{'allUIDsMatch':True,'unchangedTerritoryGeometryAndRenderElevations':stage_geometry_identical,'preferredMuiWoNativeGeometryAndFineAuditElevations':preferred_geometry,'originalSourceElevationsAndTypesPreserved':True},'duplicates':{'policy':integration['overlapPolicy'],'allBaselineFormsIndependentlyRetested':len(baseline_ids),'remainingThresholdViolations':0,'overlayOnlyRepairsOfInvalidBaseline':overlay_repairs,'allStrongOverlapAliasesPreserved':True,'officialFormsWithStrongOverlapAliases':len(strong_refs),'retainedEdgeOverlapOSMForms':len(edge_rows),'retainedEdgeOverlapPairs':all_pairs,'edgeOverlaps':edge_rows},'modelChecks':{'allExpectedModelsIdentical':True,'sourceCSUIDAndReferencedAssetHashKeysResolve':True,'modelVerticesOutsideFootprintTileBounds':model_bound_warnings},'sourceResolution':{'allHeightRuleCodesResolve':True,'allObjectIdsResolveInCompleteOfficialQuery':True,'sourceProbes':source_probes,'networkSkipped':args.skip_network},'checks':['every live tile byte size, feature/height count and whole-footprint bound matches metadata','unique UID and one centroid-based owner tile per component','exactly all 342223 official IDs and 342225 components; all structure types and null elevations retained','recorded BaseHeight/TopHeight/CSUID/type identical to retained official source','non-Mui Wo geometry and render elevations equal frozen staging; preferred Mui Wo uses native outlines and explicit fine-audit estimates','all 275 detailed models and source-code/hash references retained unchanged','all 117062 original OSM forms independently checked against published overlap threshold; no residual threshold duplicates','height rule/source codes resolve and bounded primary endpoint checks match source attributes','live manifest unchanged throughout this audit'],'notes':['No geometry, heights, source records or OSM overlaps were modified by this verifier. Invalid baseline OSM polygons are repaired only in memory for the documented intersection comparison; their IDs are reported.','Official completeness is completeness of this retained source version, not a claim that every current real-world structure is represented.','Terrain conflict flags outside the separate fine audit remain vertex/centroid samples, not exhaustive intersections.']}
 save_json(DOCS/'live-verification.json',result);print(json.dumps({k:v for k,v in result['counts'].items() if not isinstance(v,dict)},indent=2));print('LIVE DATA VERIFICATION PASSED',flush=True)

if __name__=='__main__':main()

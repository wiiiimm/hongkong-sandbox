"""Stage only missing exact-identity models, reusing the existing importer and packer."""
import collections,gzip,hashlib,importlib.util,json,pathlib,sys
from audit import HERE,ROOT,OLD,DOC,dump,sha
sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
from fetch import fetch_tiles
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import stage,model_geometry
from shapely.geometry import MultiPoint,Polygon

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
pack=module('shared_pack',HERE.parent/'central-completion/pack_models.py').pack

def main():
 audit=json.loads((DOC/'audit.json').read_text());selected={b['uid']:b for b in json.loads(gzip.decompress((OLD/'building-selection.json.gz').read_bytes()))['buildings']};groups=collections.defaultdict(list)
 for r in audit['rows']:
  if not r['existingDetailed']:
   for c in r['candidateModels']:groups[c['sheet']].append((r,c))
 results=[];assets=[];matches=[];failures=[]
 for sheet,rows in sorted(groups.items()):
  if (OLD/'staged'/sheet/'manifest.json').exists():folder=OLD/'staged'/sheet;manifest=json.loads((folder/'manifest.json').read_text())
  else:
   prefixes=sorted({str(pathlib.PurePosixPath(c['entry']).parent)+'/' for _,c in rows})+['TERRAIN']
   fetch_tiles(HERE,[sheet],prefixes)
   source=HERE/'sources'/sheet;download=json.loads((source/'download.json').read_text());assert sha((source/(sheet+'.zip')).read_bytes())==download['sha256'];folder=HERE/'staged'/sheet;manifest=stage(source/(sheet+'.zip'),download,OLD/'official-selection.json.gz',folder)
  for r,c in rows:
   spec=next(s for s in manifest['models'] if s['id']==c['modelId']);csuids=spec['officialBuildingCSUIDs'];reason=None
   if csuids!=[r['buildingCSUID']]:reason='exact-georef-candidate-fails-conservative-footprint-match' if not csuids else 'ambiguous-or-different-official-match'
   if sum(b['buildingCSUID']==r['buildingCSUID'] for b in selected.values())!=1:reason='ambiguous-selected-component'
   record={'uid':r['uid'],'modelId':c['modelId'],'sheet':sheet,'worldBounds':spec['worldBounds'],'officialMatches':spec['officialMatches'],'reason':reason or 'safe-staged-addition','placementReviewed':False}
   results.append(record)
   if reason:
    path=folder/spec['sourceEntry'];data=json.loads(path.read_text());positions,_=model_geometry(data,lambda uri:(path.parent/uri).read_bytes());hull=MultiPoint(positions[:,[0,2]]).convex_hull;b=selected[r['uid']];footprint=Polygon(b['rings'][0],b['rings'][1:])
    failures.append({'uid':r['uid'],'modelId':spec['id'],'overlapOfSmallerFootprint':hull.intersection(footprint).area/min(hull.area,footprint.area),'footprintCentroidDistanceMetres':hull.centroid.distance(footprint.centroid),'thresholds':{'minimumOverlap':.5,'maximumCentroidDistanceMetres':10},'action':'retain existing footprint until explicit source revision/identity review; do not weaken matching thresholds'})
    continue
   b=selected[r['uid']];path=folder/spec['sourceEntry']
   for rel,digest in spec['sourceHashes'].items():assert sha((folder/rel).read_bytes())==digest
   glb,stats=pack(path);compressed=gzip.compress(glb,mtime=0);dest=HERE/'compact/models'/(spec['id']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(compressed);assert stats['triangles']==spec['triangles']
   matches.append({'uid':b['uid'],'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'modelId':spec['id'],'sourceTile':sheet,'sourceTileRevision':manifest['tileRevision'],'worldBounds':spec['worldBounds'],'triangles':stats['triangles'],'recordedBaseHeight':b['baseHeightHKPD'],'recordedTopHeight':b['topHeightHKPD'],'structureType':b['structureType'],'label':b.get('name') or spec['id'],'priority':'unreviewed','placementReviewed':False,'asset':str(dest.relative_to(HERE/'compact')),'encoding':'gzip','bytes':len(compressed),'glbBytes':len(glb),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':sha(compressed)})
   assets.append({'uid':b['uid'],'sourceEntry':str(path.relative_to(ROOT)),'sourceHashes':spec['sourceHashes'],'sourceCacheSha256':manifest['sourceCacheSha256'],'sourceDownload':manifest['sourceDownload'],'sourceMatches':spec['officialMatches'],'compressedSha256':sha(compressed),'glbSha256':sha(glb),**stats})
 counts={'catalogueModels':len(matches),'packedModels':len(matches),'compressedBytes':sum(r['bytes'] for r in matches),'glbBytes':sum(r['glbBytes'] for r in matches),'decodedGeometryBytes':sum(r['decodedGeometryBytes'] for r in matches),'packedTriangles':sum(r['triangles'] for r in matches)}
 dump(HERE/'compact/catalogue.json',{'schemaVersion':1,'kind':'staged-official-model-catalogue','area':'Tai O boundary completion','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'coordinatePolicy':'Original glTF nodes, source geometry and material metadata; exact-bit attribute indexing by existing shared packer. Apply city translation once. No source height adjustment.','loadingPolicy':'Staging only. Keep existing fallback until verified individual asset loads; preserve shared loader LOD/budgets.','counts':counts,'models':matches})
 dump(DOC/'staged-additions.json',{'counts':counts,'candidateResults':results,'assets':assets,'limits':['Not live: root must review terrain/collision/browser placement before publishing.','Do not suppress unmatched structures or change source height fields.','No prior detailed model is changed; these are only previously fallback UIDs.']})
 dump(DOC/'match-failures.json',failures)
 result_by_uid={r['uid']:r for r in results}
 for r in audit['rows']:
  if r['uid'] in result_by_uid:r['reason']=result_by_uid[r['uid']]['reason'];r['candidateResult']=result_by_uid[r['uid']]
 audit['counts'].update(safeStagedAdditions=len(matches),detailedIfIntegrated=532+len(matches),remainingFallbackAfterIntegration=498-len(matches));dump(DOC/'audit.json',audit);print(json.dumps(audit['counts'],indent=2));print(json.dumps(counts,indent=2))
if __name__=='__main__':main()

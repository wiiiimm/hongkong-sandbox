"""Extend the proved Mui Wo importer; no second renderer or source-height edits."""
import collections,gzip,hashlib,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REVIEW=ROOT/'docs/astra-city/mui-wo-buildings/review';DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension'
sys.path.insert(0,str(REVIEW));from prepare_model_sample import stage
from bake_model_geometry import bake
from resample_model_terrain import resample
from fetch import TILES

def dump(path,data,pretty=False):
 path.parent.mkdir(parents=True,exist_ok=True);raw=json.dumps(data,ensure_ascii=False,indent=2 if pretty else None,separators=None if pretty else (',',':'),allow_nan=False).encode();path.write_bytes(gzip.compress(raw+b'\n',mtime=0) if path.suffix=='.gz' else raw+b'\n');return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 official=ROOT/'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz'
 by_csuid=collections.defaultdict(list)
 for b in json.loads((ROOT/'3d-viewer/city/data/mui-wo-buildings.json').read_text())['buildings']:by_csuid[b['buildingCSUID']].append(b['uid'])
 all_specs=[];manifests=[];summaries=[]
 existing=REVIEW/'model-sample';manifest=json.loads((existing/'manifest.json').read_text());manifests.append((existing,manifest))
 for tile in TILES:
  source=HERE/'sources'/tile;assets=HERE/'staged'/tile;download=json.loads((source/'download.json').read_text())
  assert hashlib.sha256((source/(tile+'.zip')).read_bytes()).hexdigest()==download['sha256'],tile
  manifest=stage(source/(tile+'.zip'),download,official,assets);manifests.append((assets,manifest))
  _,summary=resample(assets,assets);summaries.append(summary)
  print(tile,manifest['counts'],flush=True)
 grouped=collections.defaultdict(list);unmatched=[]
 for assets,manifest in manifests:
  for spec in manifest['models']:
   csuids=spec['officialBuildingCSUIDs']
   reason=None
   if not csuids:reason='No exact GeoRefNo plus footprint/centroid match in the retained Mui Wo envelope'
   elif len(csuids)!=1 or len(by_csuid[csuids[0]])!=1:reason='Ambiguous official source component match'
   if reason:unmatched.append({'tile':manifest['tile'],'modelId':spec['id'],'reason':reason,'geoRefNo':spec['geoRefNo'],'worldBounds':spec['worldBounds']});continue
   uid=by_csuid[csuids[0]][0];grouped[uid].append((assets,manifest,spec))
 geometries={};duplicate=[];ambiguous=[]
 for uid,entries in grouped.items():
  # Same individual model can cross sheet boundaries. Keep the latest published
  # revision of that same ID; never collapse distinct models into one footprint.
  if len({e[2]['id'] for e in entries})!=1:
   ambiguous.append({'uid':uid,'models':[{'tile':m['tile'],'id':s['id']} for _,m,s in entries]});continue
  entries.sort(key=lambda e:(e[1]['tileRevision'],e[1]['tile']),reverse=True)
  assets,m,spec=entries[0];record=bake(spec,assets)
  record.update(buildingCSUID=spec['officialBuildingCSUIDs'][0],sourceTile=m['tile'],sourceTileRevision=m['tileRevision'],sourceArchiveSha256=m['sourceArchiveSha256'])
  geometries[uid]=record
  if len(entries)>1:duplicate.append({'uid':uid,'modelId':spec['id'],'selectedTile':m['tile'],'tiles':[e[1]['tile'] for e in entries]})
 original=json.loads((existing/'model-geometries.json').read_text())['byBuildingUid']
 # Never remove a previously verified match because an adjacent sheet is ambiguous.
 for uid in set(original)-set(geometries):geometries[uid]=original[uid]
 counts={'tiles':len(manifests),'sourceModelEntries':sum(len(m['models']) for _,m in manifests),'sourceModelIds':len({s['id'] for _,m in manifests for s in m['models']}),'matchedBuildingGeometries':len(geometries),'previousDetailedModels':len(original),'newDetailedModels':len(set(geometries)-set(original)),'triangles':sum(r['triangles'] for r in geometries.values()),'vertices':sum(r['vertices'] for r in geometries.values()),'unmatchedEntries':len(unmatched),'ambiguousUidGroups':len(ambiguous),'duplicateMatchedUidGroups':len(duplicate)}
 payload={'schemaVersion':1,'kind':'official-building-model-geometries','datasetId':manifest['datasetId'],'crs':'EPSG:2326','origin':[834500,816500],'verticalDatum':'Hong Kong Principal Datum','coordinatePolicy':'Exact original glTF node transforms; city translation [-834500,0,816500]. Source positions/normals/colours retained. No height adjustment or simplification.','matchPolicy':manifest['matchPolicy'],'scope':'Only verified single-component BuildingCSUID matches in the retained user-supplied Mui Wo bbox are replaced. Unmatched/outside/ambiguous models are accounted for but not added as duplicate buildings.','sourceManifests':[{'file':str((a/'manifest.json').relative_to(ROOT)),'sha256':hashlib.sha256((a/'manifest.json').read_bytes()).hexdigest(),'tile':m['tile'],'revision':m['tileRevision'],'counts':m['counts']} for a,m in manifests],'counts':counts,'byBuildingUid':geometries}
 path=HERE/'model-geometries.json.gz';digest=dump(path,payload)
 report={'counts':counts,'file':str(path.relative_to(ROOT)),'sha256':digest,'bytes':path.stat().st_size,'uncompressedBytes':len(gzip.decompress(path.read_bytes())),'tiles':payload['sourceManifests'],'unmatched':unmatched,'ambiguous':ambiguous,'duplicates':duplicate,'terrainGrids':summaries}
 dump(DOC/'build.json',report,True);print(json.dumps({k:v for k,v in report.items() if k not in ('unmatched','duplicates','tiles','terrainGrids','ambiguous')},indent=2))
if __name__=='__main__':main()

"""Stage new Mui Wo source terrain using the established glTF and 5m mosaic pipeline."""
import hashlib,importlib.util,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-completion'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import stage
from resample_model_terrain import resample

def main():
 config=json.loads((HERE/'terrain-config.json').read_text());reports=[]
 for row in config['tiles']:
  tile=row['sheet'];source=HERE/'sources'/tile;assets=HERE/'staged'/tile;download=json.loads((source/'download.json').read_text());archive=source/(tile+'.zip')
  assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256']
  assert download['entries'] and all(e['name'].startswith('TERRAIN') for e in download['entries'])
  if not (assets/'manifest.json').exists():manifest=stage(archive,download,ROOT/'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz',assets)
  else:manifest=json.loads((assets/'manifest.json').read_text())
  assert not manifest['models'],'Terrain-only investigation must not reimport existing buildings'
  if not (assets/'terrain-source-5m.json').exists():_,summary=resample(assets,assets)
  else:summary=json.loads((assets/'model-terrain-resample.json').read_text())
  reports.append({'sheet':tile,'sourceRevision':download['revisionDate'],'terrain':summary,'sourceArchiveBytes':download['sourceArchiveBytes'],'transferredBytes':download['transferredBytes']});print(tile,summary['sourceTriangles'],summary['coveredGridNodes'],flush=True)
 # Crop derived grids to the existing patch only; complete original grids remain intact.
 patch=json.loads((ROOT/'3d-viewer/city/data/terrain-mui-wo.json').read_text());g=patch['meta']['georef'];cropped=[]
 for source in sorted((HERE/'staged').glob('*/terrain-source-5m.json')):
  d=json.loads(source.read_text());dg=d['meta']['georef'];dc=round((dg['bE']-g['bE'])/5);dr=round((g['bN']-dg['bN'])/5)
  c0=max(0,-dc);r0=max(0,-dr);c1=min(d['w'],patch['w']-dc);r1=min(d['h'],patch['h']-dr)
  if c1-c0<2 or r1-r0<2:continue
  originalWidth=d['w'];d['elev']=[v for r in range(r0,r1) for v in d['elev'][r*originalWidth+c0:r*originalWidth+c1]];d['valid']=[v is not None for v in d['elev']];d['w']=c1-c0;d['h']=r1-r0;dg['bE']+=c0*5;dg['bN']-=r0*5
  d['bounds']=[dg['bE']-834500,816500-dg['bN'],dg['bE']+(d['w']-1)*5-834500,816500-dg['bN']+(d['h']-1)*5]
  d['counts']={**d.get('counts',{}),'coveredGridNodes':sum(d['valid']),'gridNodes':d['w']*d['h']}
  d['derivedCrop']={'originalGrid':str(source.relative_to(ROOT)),'originalGridSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'indicesExclusive':[c0,r0,c1,r1],'purpose':'Retain only existing Mui Wo patch extent for integration; original complete source grid remains unchanged.'}
  target=HERE/'clipped-grids'/(source.parent.name+'.json');target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(d,separators=(',',':'))+'\n');cropped.append(target)
 detail=[ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample/terrain-source-5m.json',*sorted((ROOT/'source-scripts/city/mui-wo-models/staged').glob('*/terrain-source-5m.json')),*cropped]
 path=ROOT/'source-scripts/city/terrain-detail/build.py';spec=importlib.util.spec_from_file_location('shared_terrain_patch',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 module.build_patch(output=HERE/'staged-terrain-mui-wo.json',detail_paths=detail,evidence=DOC)
 (DOC/'terrain-staging.json').write_text(json.dumps({'newTerrainSheets':len(reports),'existingTerrainSheets':7,'newBuildingModels':0,'reports':reports,'published':False},indent=2)+'\n')
if __name__=='__main__':main()

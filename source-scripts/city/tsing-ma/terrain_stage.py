"""Reuse source glTF→5m grid→existing patch builder for verified bridge ground."""
import math,hashlib,importlib.util,json,pathlib,sys
from pyproj import Transformer
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/tsing-ma'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import stage
from resample_model_terrain import resample

def main(*,here=HERE,doc=DOC,bounds=(824200,823000,826900,824000),region='tsing-ma',area='Tsing Ma Bridge foundations'):
 HERE=pathlib.Path(here);DOC=pathlib.Path(doc)
 reports=[];grids=[]
 for source in sorted((HERE/'terrain/sources').iterdir()):
  assets=HERE/'terrain/staged'/source.name;download=json.loads((source/'download.json').read_text());archive=source/(source.name+'.zip')
  assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256']
  if not (assets/'manifest.json').exists():stage(archive,download,ROOT/'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz',assets)
  if not (assets/'terrain-source-5m.json').exists():resample(assets,assets)
  grids.append(assets/'terrain-source-5m.json');report=json.loads((assets/'model-terrain-resample.json').read_text());reports.append({'sheet':source.name,'sourceRevision':download['revisionDate'],**report});print(source.name,report['sourceTriangles'],flush=True)
 t=Transformer.from_crs(2326,4326,always_xy=True);points=[t.transform(E,N) for E,N in [(bounds[0],bounds[1]),(bounds[2],bounds[3])]];bbox=[points[0][0],points[0][1],points[1][0],points[1][1]]
 # The shared mosaic requires each grid to lie inside the target patch; crop derived grids only.
 coarse=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());cg=coarse['meta']['georef'];project=Transformer.from_crs(4326,2326,always_xy=True);corners=[project.transform(x,y) for x in bbox[::2] for y in bbox[1::2]]
 c0=math.floor((min(x for x,y in corners)-cg['bE'])/70)-2;c1=math.ceil((max(x for x,y in corners)-cg['bE'])/70)+2;r0=math.floor((cg['bN']-max(y for x,y in corners))/70)-2;r1=math.ceil((cg['bN']-min(y for x,y in corners))/70)+2
 E=cg['bE']+c0*70;N=cg['bN']-r0*70;W=(c1-c0)*14+1;H=(r1-r0)*14+1;cropped=[]
 for path in grids:
  d=json.loads(path.read_text());g=d['meta']['georef'];dc=round((g['bE']-E)/5);dr=round((N-g['bN'])/5);cc0=max(0,-dc);rr0=max(0,-dr);cc1=min(d['w'],W-dc);rr1=min(d['h'],H-dr)
  if cc1-cc0<2 or rr1-rr0<2:continue
  width=d['w'];d['elev']=[v for r in range(rr0,rr1) for v in d['elev'][r*width+cc0:r*width+cc1]];d['valid']=[v is not None for v in d['elev']];d['w']=cc1-cc0;d['h']=rr1-rr0;g['bE']+=cc0*5;g['bN']-=rr0*5;g.update(W=d['w'],H=d['h']);d['bounds']=[g['bE']-834500,816500-g['bN'],g['bE']+(d['w']-1)*5-834500,816500-g['bN']+(d['h']-1)*5];d['derivedCrop']={'source':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'indicesExclusive':[cc0,rr0,cc1,rr1]}
  dest=HERE/'terrain/clipped-grids'/(path.parent.name+'.json');dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(d,separators=(',',':'))+'\n');cropped.append(dest)
 grids=cropped
 spec=importlib.util.spec_from_file_location('shared_patch',ROOT/'source-scripts/city/terrain-detail/build.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.build_patch(bbox=bbox,output=HERE/f'terrain-{region}.json',detail_paths=grids,evidence=DOC,area=area,rendered_transition=True)
 (DOC/'terrain-staging.json').write_text(json.dumps({'sourceSheets':len(reports),'reports':reports,'published':False},indent=2)+'\n')
if __name__=='__main__':main()

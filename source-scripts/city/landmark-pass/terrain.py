"""Stage a Ngong Ping 5 m terrain patch using the existing native-TIN/DTM pipeline."""
import importlib.util,json,pathlib,sys
from pyproj import Transformer
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from resample_model_terrain import resample

def main():
 plan=json.loads((HERE/'acquisition-plan.json').read_text())
 paths=[]
 for tile in plan['sheets']:
  assets=HERE/'staged'/tile
  resample(assets,assets);paths.append(assets/'terrain-source-5m.json')
 xs=[];zs=[]
 for p in paths:
  d=json.loads(p.read_text());x0,z0,x1,z1=d['bounds'];xs.extend([x0+834500,x1+834500]);zs.extend([816500-z0,816500-z1])
 trans=Transformer.from_crs(2326,4326,always_xy=True);west,south=trans.transform(min(xs)-30,min(zs)-30);east,north=trans.transform(max(xs)+30,max(zs)+30)
 spec=importlib.util.spec_from_file_location('shared_landmark_terrain',HERE.parent/'terrain-detail/build.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 out=HERE/'terrain-ngong-ping.json';evidence=ROOT/'docs/astra-city/landmark-pass';evidence.mkdir(parents=True,exist_ok=True)
 m.build_patch(bbox=[west,south,east,north],output=out,detail_paths=paths,evidence=evidence,area='Ngong Ping landmarks',rendered_transition=True)
if __name__=='__main__':main()

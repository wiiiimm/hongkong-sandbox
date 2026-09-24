"""Audit staged Mui Wo changes through the existing arrival validator and search."""
import hashlib,json,os,pathlib,shutil,subprocess,sys
from shapely.geometry import Point
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-completion'
sys.path.insert(0,str(HERE.parent))
from repair_arrivals import CityArrivalValidator,retained_paths,find_repair
class StagedValidator(CityArrivalValidator):
 def __init__(self):
  self.process=subprocess.Popen([os.environ.get('CITY_NODE') or shutil.which('node'),'--import',str(HERE/'arrival-preload.mjs'),str(HERE.parent/'arrival-validator.mjs')],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
def main():
 manifest=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text());source=json.loads((DOC/'routes-staged.json').read_text());stops={p['id']:p for p in source['stops']}
 with StagedValidator() as validator:
  state=validator.request('places');walking=[(id,p) for id,p in state['places'].items() if not p.get('aerialOnly')];checks=validator.audit([p['spawn'] for _,p in walking]);failures=[{'id':id,'spawn':p['spawn'],'check':c} for (id,p),c in zip(walking,checks) if not c['valid']]
  records,origins,sources,paths,pathids,tree=retained_paths(manifest);destinations=[];repairs=[]
  for failure in failures:
   repair=find_repair(validator,Point(failure['spawn']),paths,pathids,tree);repair.update(id=failure['id'],previousSpawn=failure['spawn'],failure=failure['check']);repairs.append(repair)
  replacements={r['id']:r['spawn'] for r in repairs};after=validator.audit([replacements.get(id,p['spawn']) for id,p in walking]);assert all(c['valid'] for c in after)
  config=[('wangtong','Wang Tong','橫塘','Public paths beside the village and Wang Tong River.'),('paknganheung','Pak Ngan Heung','白銀鄉','Village paths below Silvermine Waterfall and the surrounding hills.'),('taiteitong','Tai Tei Tong','大地塘','Public village approaches beside the River Silver valley.'),('lukteitong','Luk Tei Tong','鹿地塘','Village lanes and the southern Mui Wo valley.'),('muiwoferrypier','Mui Wo ferry waterfront','梅窩碼頭海旁','The public waterfront approach beside Mui Wo ferry pier.')]
  for id,title,zh,description in config:
   assert id not in state['places'];stop=stops['ferry-promenade' if id=='muiwoferrypier' else id];centre=Point(stop['nodePosition']);repair=find_repair(validator,centre,paths,pathids,tree);oid=repair['arrivalSource'].removeprefix('https://www.openstreetmap.org/');e=records[oid]
   if 'lat' in stop:lat,lon=stop['lat'],stop['lon'];sourceurl='https://www.openstreetmap.org/node/'+str(stop['sourcePlaceNode'])
   else:
    from pyproj import Transformer
    lon,lat=Transformer.from_crs(2326,4326,always_xy=True).transform(centre.x+834500,816500-centre.y);sourceurl='https://www.openstreetmap.org/node/'+str(stop['sourceNode'])
   entry={'id':id,'region':'lantau','sectionId':'10.6','title':title,'zh':zh,'description':description,'lat':lat,'lon':lon,'source':sourceurl,'spawn':repair['spawn'],'terrainY':repair['terrainY'],'arrivalSource':repair['arrivalSource'],'arrivalVerified':True,'offset':[650,480,700]}
   destinations.append({'place':entry,'arrival':repair,'sourceFile':origins[oid],'sourceTags':e.get('tags',{})})
  report={'schemaVersion':1,'staged':True,'passed':all(c['valid'] for c in after),'existing':{'destinations':len(state['places']),'walking':len(walking),'aerial':len(state['places'])-len(walking),'failures':failures},'arrivals':[{'id':id,'spawn':p['spawn'],'check':c} for (id,p),c in zip(walking,checks)],'repairs':repairs,'existingAfter':{'walking':len(after),'passed':sum(c['valid'] for c in after)},'new':destinations,'method':'Unchanged arrival-validator.mjs and repair_arrivals.find_repair, with staged terrain/hydro and only source-null base estimates substituted in memory. All current source tiles and collision modules reused. New arrivals include 2 m public-path checks at 1.2 m building clearance.','terrainSha256':hashlib.sha256((HERE/'staged-terrain-mui-wo.json').read_bytes()).hexdigest()}
  (DOC/'arrivals-staged.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(HERE/'places-staged.json').write_text(json.dumps({'schemaVersion':1,'region':'mui-wo','places':[d['place'] for d in destinations]},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'existing':report['existing'],'repairs':repairs,'new':[{'id':d['place']['id'],'spawn':d['place']['spawn'],'source':d['place']['arrivalSource'],'distanceM':d['arrival']['movementMetres']} for d in destinations]},indent=2))
if __name__=='__main__':main()

"""Run the validated original-source terrain workflow for selected XL candidates."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from shapely.geometry import Polygon,box
sys.path.insert(0,str(Path(__file__).resolve().parent))
spec=importlib.util.spec_from_file_location('west',Path(__file__).with_name('xl-stage-west9zone.py'));w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
s=w.s;ROOT,HERE=s.ROOT,s.HERE;read,save,h,rel=s.read,s.save,s.h,s.rel
CONFIG={
 'harbourfront': 'landsd/31275:0',
 'v-city': 'landsd/230643:0',
 'chung-kin': 'landsd/147024:0',
 'spectra-3': 'landsd/265311:0',
 'tower-147505': 'landsd/147505:0',
 'chung-mei': 'landsd/160193:0',
 'goldmark': 'landsd/177244:0',
}
def configure(key):
 uid=CONFIG[key];w.UID=uid;w.DOC=s.DOC/'third-pass'/('terrain-'+key);w.LOCAL=s.LOCAL/('third-pass-terrain-'+key);return uid,w.DOC,w.LOCAL
def start(key):
 uid,doc,local=configure(key);selected=read(s.DOC/'runtime-selection.json.gz');row=next(r for r in selected['rows'] if r['uid']==uid);parent=read(ROOT/'3d-viewer/city/data/terrain.json');cells=s.resolution.rectangle_for(row['candidate']['entry']['worldBounds'],parent)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');replacement=None
 if key=='chung-mei':
  overlapping=[entry for entry in manifest['terrainPatches'] if s.resolution.terrain.overlap(cells,read(ROOT/'3d-viewer'/entry['url'])['coarseCells'])]
  assert [entry['url'] for entry in overlapping]==['city/data/government-native-147024-0.json']
  entry=overlapping[0];old=read(ROOT/'3d-viewer'/entry['url']);assert old['meta']['targetUids']==['landsd/147024:0']
  a,b,c,d=old['coarseCells'];cells=[min(cells[0],a),min(cells[1],b),max(cells[2],c),max(cells[3],d)]
  replacement={'url':entry['url'],'sha256':h(ROOT/'3d-viewer'/entry['url']),'retainedUids':['landsd/147024:0']}
 bounds=s.resolution.extent(cells,parent);region=box(*bounds)
 live={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']};neighbours=[];hashes={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
  for building in json.loads(raw)['buildings']:
   if Polygon(building['rings'][0],building['rings'][1:]).intersects(region):neighbours.append({'building':building,'patchIndexes':[0],'existingNative':building['uid'] in live or bool(building.get('modelGeometry'))});touched=True
  if touched:hashes[rel(path)]=s.digest(raw)
 current=h(ROOT/'3d-viewer/city/data/manifest.json');save(doc/'selection.json.gz',{**selected,'manifestSHA256':current,'rows':[row]});save(doc/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'candidateIds':[uid],'patches':[]});save(doc/'patch-plan.json',{'cells':cells,'bounds':bounds,'manifestSHA256':current,'uid':uid,'replaces':replacement})
 resources=set(['building:'+uid])|{('building:' if item['building']['uid'].startswith('landsd/') else 'source-form:')+item['building']['uid'] for item in neighbours};claim=s.reservations.claim('codex-xl-terrain-'+key+'-'+str(uuid.uuid4()),sorted(resources),batch='government-xl-terrain-'+key+'-20260914');assert claim['ok'];save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,key,'owned'],cwd=ROOT,check=True)
def owned(key):
 configure(key);w.owned()
if __name__=='__main__':
 key=sys.argv[1];assert key in CONFIG;owned(key) if len(sys.argv)>2 else start(key)

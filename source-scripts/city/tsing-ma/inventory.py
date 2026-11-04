"""Inspect retained original infrastructure without adding/repositioning models."""
import json,pathlib,sys,zipfile,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
rows=[]
for folder in sorted((HERE/'sources').iterdir()):
 archive=folder/(folder.name+'.zip');download=json.loads((folder/'download.json').read_text())
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   if not name.endswith('.gltf'):continue
   raw=z.read(name);d=json.loads(raw);p=pathlib.PurePosixPath(name).parent;positions,triangles=model_geometry(d,lambda uri:z.read(str(p/uri)))
   bounds=[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()]
   rows.append({'id':p.name,'sheet':folder.name,'entry':name,'triangles':triangles,'bounds':bounds,'sha256':hashlib.sha256(raw).hexdigest(),'source':download['source'],'sourceRevision':download['revisionDate']})
report={'kind':'all-retained-infrastructure-in-bounded-index','models':rows,'counts':{'entries':len(rows),'uniqueModelIds':len(set(r['id'] for r in rows))}}
(ROOT/'docs/astra-city/tsing-ma/model-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
for r in rows:print(r['sheet'],r['id'],r['triangles'],r['bounds'])

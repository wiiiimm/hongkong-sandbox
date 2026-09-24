"""Read-only geometric identity evidence for four alias-resolved native towers."""
import json,pathlib,sqlite3,sys,hashlib,numpy as np
from shapely.geometry import Polygon,MultiPoint
from shapely import union_all,make_valid
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-four-native';BATCH=ROOT/'source-scripts/city/landmark-acquisition/batches/identity-four-native-20260909'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
c=sqlite3.connect('file:'+str(ROOT/'source-scripts/city/building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON')
def shape(b):
 r=json.loads(b['rings_json']);return make_valid(Polygon(r[0],r[1:]))
def metrics(a,b):
 area=a.intersection(b).area;return {'footprintCoverage':area/b.area,'sourceProjectionInside':area/a.area if a.area else 0,'centroidDistance':a.centroid.distance(b.centroid)}
rows=[]
for uid in json.loads((HERE/'targets.json').read_text())['targets']:
 b=dict(c.execute('select * from buildings where uid=? and active=1',(uid,)).fetchone());options=[]
 for mp in (BATCH/'staged').glob('*/manifest.json'):
  for s in json.loads(mp.read_text())['models']:
   if s['id'][1:11]==b['csuid'][:10]:options.append((mp,s))
 assert len(options)==1,(uid,len(options));mp,s=options[0]
 for rel,digest in s['sourceHashes'].items():assert hashlib.sha256((mp.parent/rel).read_bytes()).hexdigest()==digest
 p=np.array(bake(s,mp.parent)['position']).reshape(-1,3);tri=p.reshape(-1,3,3);foot=shape(b);levels={}
 for level in [float(p[:,1].min())-.01,b['source_base']+.5,(b['source_base']+b['source_top'])/2]:
  faces=[Polygon(t[:,[0,2]]) for t in tri if t[:,1].max()>=level];proj=union_all([f for f in faces if f.area>1e-8]);levels[str(level)]=metrics(proj,foot)
 related=[{'uid':r['uid'],'csuid':r['csuid'],'name':r['name']} for r in c.execute('select uid,csuid,name from buildings where active=1 and csuid like ?',(b['csuid'][:10]+'%',))]
 rows.append({'uid':uid,'name':b['name'],'csuid':b['csuid'],'sourceBaseTop':[b['source_base'],b['source_top']],'nativeBounds':s['worldBounds'],'modelId':s['id'],'sourceManifest':str(mp.relative_to(ROOT)),'sourceHashes':s['sourceHashes'],'originalOfficialMatches':s['officialMatches'],'sameGeoRefRecords':related,'sourceProjectionByMinimumHeight':levels,'geometryChanged':False,'identityAutomaticallyApproved':False})
c.close();(DOC/'identity-geometry.json').write_text(json.dumps({'rows':rows,'qualification':'Projection evidence alone is not component, terrain or installation acceptance.'},indent=2)+'\n')
for row in rows:print(row['uid'],row['sourceProjectionByMinimumHeight'])

"""Read-only native support and terrain context for HKS-207."""
import json,pathlib,sqlite3,sys,numpy as np
from shapely.geometry import Polygon
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry
sys.path.insert(0,str(H.parent/'landmark-pass'));from audit_existing import triangle_evidence
read=lambda p:json.loads(p.read_bytes())
c=sqlite3.connect('file:'+str(H.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
bs={r['uid']:dict(r) for r in c.execute('select * from buildings where active=1 and x between 900 and 1400 and z between -950 and -500')}
cat={r['uid']:r for r in read(H/'compact/catalogue.json')['models']};manifest=read(H/'staged/11-SW-4D/manifest.json');specs={r['id']:r for r in manifest['models']}
def native(uid):
 p=H/'staged/11-SW-4D'/specs[cat[uid]['modelId']]['sourceEntry'];return p,model_geometry(read(p),lambda u:(p.parent/u).read_bytes())[0]
def poly(b):
 rs=json.loads(b['rings_json']);return Polygon(rs[0],rs[1:])
terrain=read(R/'3d-viewer/city/data/terrain-central.json');g=terrain['meta']['georef'];w=terrain['w'];h=terrain['h'];e=np.array([v if v is not None else max(1.2,terrain['elev'][i]) if terrain['elev'][i]>0 else -4 for i,v in enumerate(terrain['renderedElev'])]).reshape(h,w)
def ground(x,z):
 c=np.clip((x+834500-g['bE'])/g['aE'],0,w-1);r=np.clip((816500-z-g['bN'])/g['aN'],0,h-1);i=np.minimum(w-2,np.floor(c)).astype(int);j=np.minimum(h-2,np.floor(r)).astype(int);u=c-i;v=r-j;a=e[j,i];b=e[j,i+1];d=e[j+1,i];ee=e[j+1,i+1];return np.where(u+v<=1,a+(b-a)*u+(d-a)*v,ee+(d-ee)*(1-u)+(b-ee)*(1-v))
rows=[]
for uid in ['landsd/209787:0','landsd/77406:0','landsd/72491:0','landsd/123119:0']:
 b=bs[uid];p,v=native(uid);v=np.unique(v,axis=0);gv=ground(v[:,0],v[:,2]);delta=v[:,1]-gv;bottom=v[:,1].min();nearbottom=v[:,1]<=bottom+.5;foot=poly(b)
 row={'uid':uid,'name':b['name'],'sourceBaseTop':[b['source_base'],b['source_top']],'nativeBaseTop':[float(bottom),float(v[:,1].max())],'nativeVertexTerrain':{'uniqueVertices':len(v),'belowTerrainBy05m':int((delta<-.5).sum()),'belowTerrainBy2m':int((delta<-2).sum()),'nearBottomVertices':int(nearbottom.sum()),'nearBottomGroundRange':list(map(float,[gv[nearbottom].min(),gv[nearbottom].max()])),'nearBottomClearanceQuantiles':np.quantile(delta[nearbottom],[0,.25,.5,.75,1]).tolist(),'terrainResolutionMetres':5},'nearbyParts':[]}
 for nid,n in bs.items():
  if uid!=nid and foot.distance(poly(n))<1:row['nearbyParts'].append({'uid':nid,'name':n['name'],'structureType':n['structure_type'],'sourceBaseTop':[n['source_base'],n['source_top']],'targetFootprintCoverage':poly(n).intersection(foot).area/foot.area})
 # Main podium true source triangle support for the raised restaurant block.
 if uid=='landsd/77406:0':
  pp,pv=native('landsd/72491:0');ev=triangle_evidence(pp,pv,foot,b['source_base'],b['base'],b['height']);diff=[min(abs(y-bottom) for y in ray['surfaceHeightsHKPD']) for ray in ev['rays'] if ray['surfaceHeightsHKPD']];row['podiumSupport']={'uid':'landsd/72491:0','samples':len(ev['rays']),'samplesWithActualTriangle':len(diff),'samplesWithin05m':int(sum(d<=.5 for d in diff)),'samplesWithin1m':int(sum(d<=1 for d in diff)),'surfaceDifferenceRange':[min(diff),max(diff)] if diff else None,'evidence':ev};row['interpretation']='Restaurant survey base8.3m matches separate podium top8.3m. Bare-terrain gap is expected; use source podium support. Do not lower the upper component.'
 elif uid=='landsd/209787:0':row['interpretation']='Studio native base4.228m aligns surveyed ground base4.1m. Compare low ground sample only at actual bottom vertices; global bbox samples may lie outside supported footprint or on steps.'
 else:row['interpretation']='Source includes below-grade lower geometry down to2.341m beneath groundaround4m. Count local intersections and inspect visible walls/roof; global model bottom below ground is not sufficient proof of incorrect model placement.'
 rows.append(row)
report={'issue':'HKS-207','renderedTerrain':'city/data/terrain-central.json','terrainResolutionMetres':5,'rows':rows,'limits':['Read-only support audit; no source vertices, transforms, terrain or footprint metadata changed.','Ground samples use same triangle diagonal and fallback heights as final terrain sampler.','Native model bottom may include substructure or lower circulation areas; visual review decides exposed foundation quality.']};(H/'support-context.json').write_text(json.dumps(report,indent=2)+'\n')
for r in rows:print(json.dumps({k:v for k,v in r.items() if k not in ('nearbyParts','podiumSupport')},indent=2))
if 'podiumSupport'in rows[1]:print(json.dumps({k:v for k,v in rows[1]['podiumSupport'].items() if k!='evidence'},indent=2))

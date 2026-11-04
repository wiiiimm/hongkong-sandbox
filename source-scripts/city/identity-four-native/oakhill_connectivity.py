"""Evidence for the two projecting Oakhill lower corners; no geometry modification."""
import pathlib,json,sys,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-four-native';sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
read=lambda p:json.loads(p.read_bytes());row=next(r for r in read(DOC/'identity-geometry.json')['rows']if r['uid']=='landsd/323059:0');mp=ROOT/row['sourceManifest'];spec=next(m for m in read(mp)['models']if m['id']==row['modelId']);b=bake(spec,mp.parent);v=np.array(b['position']).reshape(-1,3);keys=[tuple(round(float(x),3)for x in p)for p in v];parent={k:k for k in keys}
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
def join(a,b):parent[find(a)]=find(b)
for i in range(0,len(keys),3):join(keys[i],keys[i+1]);join(keys[i],keys[i+2])
r=next(r for r in read(DOC/'support.json')['rows']if r['uid']=='landsd/323059:0');rim={tuple(round(x,3)for x in p['position']):p for p in r['rim']};anchor={find(k)for k,p in rim.items()if p['distance']<=.5};exceptions=[]
for k,p in rim.items():
 if p['distance']<=.5:continue
 component=find(k);members=[q for q in parent if find(q)==component];contacts=[q for q,v in rim.items()if v['distance']<=.5 and find(q)==component];exceptions.append({'position':list(k),'supportDistance':p['distance'],'connectedVertices':len(members),'connectedLowerRimContacts':len(contacts),'supportedNativeComponent':component in anchor})
assert all(p['supportedNativeComponent']for p in exceptions);(DOC/'oakhill-connectivity.json').write_text(json.dumps({'issue':'HKS-214','uid':r['uid'],'exceptions':exceptions,'method':'Native triangle graph welded at1mm source vertex coordinates; connectivity to directly surveyed-podium-contacting lower-rim vertices. This proves source-connected projecting corners, not structural engineering capacity.','sourceGeometryChanged':False},indent=2)+'\n');print(exceptions)

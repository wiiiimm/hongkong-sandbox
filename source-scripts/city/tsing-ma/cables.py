"""Separate, explicitly illustrative main-span cables between source saddle tops.
This is not part of LandsD's original mesh and is not a surveyed cable profile.
"""
import json,math,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/tsing-ma'
FACT='https://www.hyd.gov.hk/en/information_corner/hyd_factsheets/doc/e_Tsing_Ma_Bridge.pdf'
PAPER='https://link.springer.com/article/10.1007/s13349-024-00842-5'
def tube(path,diameter,sides=6):
 p=np.array(path,float);tangents=np.empty_like(p);tangents[1:-1]=p[2:]-p[:-2];tangents[0]=p[1]-p[0];tangents[-1]=p[-1]-p[-2];tangents/=np.linalg.norm(tangents,axis=1)[:,None]
 axes=np.cross(tangents,np.array([0,1,0]));lengths=np.linalg.norm(axes,axis=1);axes[lengths<1e-8]=[1,0,0];axes/=np.linalg.norm(axes,axis=1)[:,None];second=np.cross(tangents,axes)
 rings=np.array([p+(axes*np.cos(a)+second*np.sin(a))*diameter/2 for a in np.linspace(0,2*np.pi,sides,endpoint=False)]).transpose(1,0,2);normals=(rings-p[:,None,:])/(diameter/2);positions=[];ns=[]
 for i in range(len(p)-1):
  for k in range(sides):
   kk=(k+1)%sides
   for a,b in [(i,k),(i+1,kk),(i+1,k),(i,k),(i,kk),(i+1,kk)]:positions.extend(rings[a,b]);ns.extend(normals[a,b])
 return positions,ns

def build():
 data=json.loads((HERE/'bridges-tsing-ma.json').read_text());byid={m['id'].split('/')[-1]:m for m in data['models']};deck=np.concatenate([np.array(m['modelGeometry']['position']).reshape(-1,3,3) for m in data['models'] if '/I' in m['id']]);cross=np.cross(deck[:,1]-deck[:,0],deck[:,2]-deck[:,0]);deck=deck[cross[:,1]>.01]
 anchors={}
 for mid in ['B250112338101063C0','B250222334201063C0','B263302377501063C0','B263422373701063C0']:
  m=byid[mid];p=np.unique(np.array(m['modelGeometry']['position']).reshape(-1,3),axis=0);top=p[p[:,1]>p[:,1].max()-.03];anchor=top.mean(axis=0)
  anchors[mid]={'modelId':m['id'],'point':anchor.tolist(),'method':'Mean of unique source vertices within3cm of the saddle-cover maximum. Exact mesh samples; inferred cable centreline attachment, not a surveyed cable anchor.','sourceHashes':m['modelGeometry']['sourceHashes']}
 def deck_height(x,z):
  t=deck[(deck[:,:,0].min(axis=1)<=x)&(deck[:,:,0].max(axis=1)>=x)&(deck[:,:,2].min(axis=1)<=z)&(deck[:,:,2].max(axis=1)>=z)];ys=[]
  for tri in t:
   a,b,c=tri[:,[0,2]];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-10:continue
   u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(z-c[1]))/den;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(z-c[1]))/den;w=1-u-v
   if min(u,v,w)>=-1e-8:ys.append(float(u*tri[0,1]+v*tri[1,1]+w*tri[2,1]))
  return max(ys) if ys else None
 parts=[];skipped=[];spans=[]
 for side,(west,east) in enumerate([('B250112338101063C0','B263302377501063C0'),('B250222334201063C0','B263422373701063C0')]):
  a=np.array(anchors[west]['point']);b=np.array(anchors[east]['point']);length=float(np.linalg.norm((b-a)[[0,2]]));sag=length*.091
  def point(t):
   p=a*(1-t)+b*t;p[1]-=4*sag*t*(1-t);return p
  path=[point(t).tolist() for t in np.linspace(0,1,193)];parts.append({'id':'main-cable-'+str(side),'role':'main-cable','path':path,'diameter':1.1,'diameterSource':FACT,'estimatedGeometry':True,'anchorModels':[west,east]});spans.append({'side':side,'horizontalSpanMetres':length,'sagMetres':sag,'minHeightHKPD':min(p[1] for p in path)})
  for d in np.arange(18,length-9,18):
   p=point(d/length);y=deck_height(p[0],p[2])
   if y is None or y>=p[1]:skipped.append({'side':side,'distance':float(d),'reason':'No upward source deck face below inferred cable'});continue
   parts.append({'id':f'hanger-{side}-{int(d)}','role':'hanger','path':[[float(p[0]),y,float(p[2])],p.tolist()],'diameter':.16,'estimatedGeometry':True,'spacingBasis':'Illustrative18m spacing, half the generally36m source-described deck erection sections; not verified hanger spacing.','baseBasis':'Interpolated upward original deck triangle at the same horizontal point.'})
 positions=[];normal=[]
 for p in parts:
  pp,nn=tube(p['path'],p['diameter']);positions.extend(pp);normal.extend(nn)
 pos=np.array(positions).reshape(-1,3);g={'position':positions,'normal':normal,'colour':[.55,.57,.58]*len(pos),'worldBounds':[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()],'vertices':len(pos),'triangles':len(pos)//3}
 out={'schemaVersion':1,'kind':'illustrative-bridge-cables','region':'tsing-ma','id':'estimated-tsing-ma-main-span-cables','estimatedGeometry':True,'walkable':False,'sourceUrl':FACT,'sources':[{'url':FACT,'facts':['main cables1.1m diameter','main span1377m','generally36m erection deck segments']},{'url':PAPER,'facts':['main-cable sag ratio0.091 used in the published monitoring model'],'use':'Only a static visual approximation; not the measured present cable curve or current deflection.'}],'anchors':anchors,'profile':'Straight horizontal interpolation between inferred source-saddle anchors; parabolic vertical profile with sag0.091×horizontal span.','parts':parts,'modelGeometry':g,'limits':['All cable/hanger geometry is illustrative and separate from the six original source meshes.','No wind, load, temperature or structural analysis is simulated.','Backstay anchorage geometry and exact hanger layout are not verified and are omitted from this bounded addition.','The source deck and tower vertices remain unchanged.'],'counts':{'originalSourceModels':0,'mainCables':2,'illustrativeHangers':sum(p['role']=='hanger' for p in parts),'illustrativeTriangles':g['triangles']},'spans':spans,'skippedHangers':skipped}
 (HERE/'cables-tsing-ma.json').write_text(json.dumps(out,separators=(',',':'))+'\n');(DOC/'cable-approximation.json').write_text(json.dumps({k:v for k,v in out.items() if k not in ['parts','modelGeometry']},indent=2)+'\n');print(json.dumps(out['counts']),spans,'skipped',len(skipped));return out
if __name__=='__main__':build()

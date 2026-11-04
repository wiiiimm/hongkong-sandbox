"""Separate illustrative Ting Kau fan stays, anchored to the unchanged source bridge.
Reuses only the generic tube tessellator, never Tsing Ma suspension-profile maths.
"""
import importlib.util,json,pathlib,numpy as np
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/ting-kau'
FACT='https://www.hyd.gov.hk/en/information_corner/hyd_factsheets/doc/e_Ting_Kau_Bridge.pdf'
def cross2(a,b):return a[0]*b[1]-a[1]*b[0]
def build():
 spec=importlib.util.spec_from_file_location('shared_tube',HERE.parent/'tsing-ma/cables.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 original=json.loads((HERE/'bridges-ting-kau.json').read_text())['models'][0];p=np.array(original['modelGeometry']['position']).reshape(-1,3);tri=p.reshape(-1,3,3);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);up=tri[(normal[:,1]>.01)&(tri[:,:,1].max(axis=1)<110)&(tri[:,:,1].min(axis=1)>45)]
 anchors=[]
 for match in original['buildingMatches']:
  b=match['identityWorldBounds'];centre=(np.array(b[0])+np.array(b[1]))/2;near=p[np.linalg.norm(p[:,[0,2]]-centre[[0,2]],axis=1)<15];top=np.unique(near[near[:,1]>near[:,1].max()-.02],axis=0);a=top.mean(axis=0);anchors.append({'uid':match['uid'],'point':a.tolist(),'method':'Mean of unique highest source infrastructure vertices near the exact matched tower; cable attachment itself is inferred.'})
 anchors.sort(key=lambda a:a['point'][2]);a=np.array(anchors[0]['point']);b=np.array(anchors[-1]['point']);u=(b-a)[[0,2]];u/=np.linalg.norm(u);v=np.array([-u[1],u[0]]);s0=np.array(a[[0,2]]);ss=[float((np.array(q['point'])[[0,2]]-s0)@u) for q in anchors];long=(p[:,[0,2]]-s0)@u
 limits=[float(long.min()+5),(ss[0]+ss[1])/2,(ss[1]+ss[2])/2,float(long.max()-5)]
 def deck_y(q):
  rows=up[(up[:,:,0].min(axis=1)<=q[0])&(up[:,:,0].max(axis=1)>=q[0])&(up[:,:,2].min(axis=1)<=q[1])&(up[:,:,2].max(axis=1)>=q[1])];ys=[]
  for t in rows:
   a,b,c=t[:,[0,2]];den=cross2(b-a,c-a)
   if abs(den)<1e-8:continue
   r=cross2(q-a,c-a)/den;s=cross2(b-a,q-a)/den
   if min(r,s,1-r-s)>=-1e-8:ys.append(float((1-r-s)*t[0,1]+r*t[1,1]+s*t[2,1]))
  return max(ys) if ys else None
 parts=[];skipped=[]
 for k,tower in enumerate(anchors):
  centre=np.array(tower['point']);station=ss[k]
  for side in (-1,1):
   end=limits[k] if side<0 else limits[k+1];dist=abs(end-station)
   for i,d in enumerate(np.arange(13.5,dist-1,13.5)):
    # Four source-described cable planes. Plane positions/upper anchor distribution are illustrative.
    for plane,cross in enumerate((-22,-5,5,22)):
     q=s0+u*(station+side*d)+v*cross;y=deck_y(q)
     if y is None:skipped.append({'tower':k,'side':side,'distance':float(d),'plane':plane});continue
     start=centre.copy();start[[0,2]]+=v*np.sign(cross)*1.0;start[1]-=2+18*(1-d/dist)
     parts.append({'id':f'fan-{k}-{side}-{i}-{plane}','role':'fan-stay','path':[start.tolist(),[float(q[0]),y,float(q[1])]],'diameter':.22,'estimatedGeometry':True,'basis':'Four fan planes and 13.5 m deck anchorage spacing from HyD; exact plane offsets, cable diameters and attachment distribution are estimated. Lower height is an original upward source deck triangle.'})
 # HyD documents eight long stays from the central tower towards the two outer towers.
 for outer in (0,2):
  for side in (-1,1):
   for pair in (0,1):
    q=np.array(anchors[outer]['point'])[[0,2]]+u*(8 if outer==0 else -8)+v*(side*(5+pair*.45));y=deck_y(q)
    if y is None:continue
    start=np.array(anchors[1]['point']);start[[0,2]]+=v*(side*(1+pair*.45));start[1]-=1.5+pair*.5
    parts.append({'id':f'longitudinal-{outer}-{side}-{pair}','role':'longitudinal-stay','path':[start.tolist(),[float(q[0]),y,float(q[1])]],'diameter':.26,'estimatedGeometry':True,'basis':'Eight longitudinal stabilising stays documented by HyD. Exact paired attachment offsets and diameter are illustrative; source tower and deck heights stay unchanged.'})
 positions=[];normals=[]
 for part in parts:
  pp,nn=m.tube(part['path'],part['diameter'],sides=6);positions.extend(pp);normals.extend(nn)
 points=np.array(positions).reshape(-1,3);geometry={'position':positions,'normal':normals,'colour':[.57,.59,.61]*len(points),'worldBounds':[points.min(axis=0).tolist(),points.max(axis=0).tolist()],'vertices':len(points),'triangles':len(points)//3}
 out={'schemaVersion':1,'kind':'illustrative-bridge-cables','region':'ting-kau','id':'estimated-ting-kau-fan-stays','estimatedGeometry':True,'walkable':False,'sourceUrl':FACT,'sources':[{'url':FACT,'facts':['three single-legged towers and four fan planes','deck anchor centres 13.5 m','eight longitudinal stabilising stays'],'use':'Structural arrangement only; no claim of surveyed individual cable attachment coordinates.'}],'anchors':anchors,'profile':'Straight inclined fan stays from three source towers to source deck faces; a cable-stayed arrangement, not a suspension catenary.','parts':parts,'modelGeometry':geometry,'counts':{'originalSourceModels':0,'illustrativeFanStays':sum(p['role']=='fan-stay' for p in parts),'illustrativeLongitudinalStays':sum(p['role']=='longitudinal-stay' for p in parts),'illustrativeTriangles':geometry['triangles']},'limits':['All cable geometry is explicitly illustrative and separate from the original deck/tower mesh.','The official published cable inventory is not claimed to be fully reconstructed; these fan anchors are generated for a source-informed visual arrangement.','Transverse stabilisation cables, exact anchor hardware, dampers and dynamic cable sag are not reconstructed.','Source geometry, source HKPD elevations and public-access restrictions are unchanged.'],'skippedUnsupportedAnchors':skipped}
 (HERE/'cables-ting-kau.json').write_text(json.dumps(out,separators=(',',':'))+'\n');(DOC/'cable-approximation.json').write_text(json.dumps({k:v for k,v in out.items() if k not in ['parts','modelGeometry']},indent=2)+'\n');print(out['counts'],'skipped',len(skipped));return out
if __name__=='__main__':build()

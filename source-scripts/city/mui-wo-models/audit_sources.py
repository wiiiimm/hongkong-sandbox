"""Independent same-position TIN joins and source-model versus outline evidence."""
import collections,gzip,json,pathlib,sys
import numpy as np
from shapely.geometry import Point
from shapely.ops import nearest_points
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];REVIEW=ROOT/'docs/astra-city/mui-wo-buildings/review';DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension'
sys.path.insert(0,str(REVIEW));from resample_model_terrain import terrain_index

def source_height(item,x,z,tolerance=0):
 usable,tree=item;values=[];point=Point(x,z)
 candidates=tree.query(point,predicate='dwithin',distance=tolerance) if tolerance else tree.query(point,predicate='covered_by')
 for i in candidates:
  sample=nearest_points(point,tree.geometries[i])[1] if tolerance else point
  tri=usable[i];u,v=np.linalg.solve((tri[1:,:][:,[0,2]]-tri[0,[0,2]]).T,np.array([sample.x,sample.y])-tri[0,[0,2]])
  values.append(float(tri[0,1]+u*(tri[1,1]-tri[0,1])+v*(tri[2,1]-tri[0,1])))
 return max(values) if values else None

def audit_sources(source_dir=HERE,doc=DOC,existing_assets=None):
 assets=[*(existing_assets if existing_assets is not None else [REVIEW/'model-sample']),*sorted((source_dir/'staged').iterdir())];sources={};bounds={};revisions={}
 for folder in assets:
  m,s,t,valid,usable,tree=terrain_index(folder);sources[m['tile']]=(usable,tree);bounds[m['tile']]=[[round(p[0]),p[1],round(p[2])] for p in s['worldBounds']];revisions[m['tile']]=m['tileRevision']
 seams=[]
 for a,ba in bounds.items():
  for b,bb in bounds.items():
   if a>=b:continue
   points=[]
   if abs(ba[1][0]-bb[0][0])<.001 or abs(bb[1][0]-ba[0][0])<.001:
    x=(ba[1][0]+bb[0][0])/2 if abs(ba[1][0]-bb[0][0])<.001 else (bb[1][0]+ba[0][0])/2
    lo=max(ba[0][2],bb[0][2]);hi=min(ba[1][2],bb[1][2]);points=[(x,float(z)) for z in np.arange(lo+2.5,hi,5)] if hi>lo else []
   if abs(ba[1][2]-bb[0][2])<.001 or abs(bb[1][2]-ba[0][2])<.001:
    z=(ba[1][2]+bb[0][2])/2 if abs(ba[1][2]-bb[0][2])<.001 else (bb[1][2]+ba[0][2])/2
    lo=max(ba[0][0],bb[0][0]);hi=min(ba[1][0],bb[1][0]);points=[(float(x),z) for x in np.arange(lo+2.5,hi,5)] if hi>lo else points
   if not points:continue
   rows=[]
   for x,z in points:
    ah=source_height(sources[a],x,z,.01);bh=source_height(sources[b],x,z,.01)
    if ah is not None and bh is not None:rows.append({'point':[x,z],'heights':[ah,bh],'difference':abs(ah-bh)})
   diffs=[r['difference'] for r in rows]
   seams.append({'tiles':[a,b],'revisions':[revisions[a],revisions[b]],'sampled':len(points),'paired':len(rows),'maxMetres':max(diffs) if diffs else None,'medianMetres':float(np.median(diffs)) if diffs else None,'over1m':sum(d>1 for d in diffs),'largest':sorted(rows,key=lambda r:r['difference'],reverse=True)[:10]})
 geometries=json.loads(gzip.decompress((source_dir/'model-geometries.json.gz').read_bytes()))['byBuildingUid'];models=[]
 for uid,m in geometries.items():
  box=np.array(m['worldBounds']);x,y,z=box.mean(axis=0);tile=m.get('sourceTile','10-SW-12C');ground=source_height(sources[tile],x,z);attrs=m['officialMatches'][0]
  models.append({'uid':uid,'modelId':m['modelId'],'tile':tile,'centre':[x,z],'modelBottom':box[0,1],'modelTop':box[1,1],'sourceTINGround':ground,'roofBelowOwnSourceTIN':ground is not None and box[1,1]<ground-.1,'outlineBase':attrs['sourceBaseHeight'],'outlineTop':attrs['sourceTopHeight'],'modelMinusOutlineTop':None if attrs['sourceTopHeight'] is None else box[1,1]-attrs['sourceTopHeight']})
 counts={'models':len(models),'noOwnTINAtCentre':sum(m['sourceTINGround'] is None for m in models),'roofBelowOwnSourceTIN':sum(m['roofBelowOwnSourceTIN'] for m in models),'modelTopDiffersFromOutlineOver2m':sum(m['modelMinusOutlineTop'] is not None and abs(m['modelMinusOutlineTop'])>2 for m in models)}
 report={'counts':counts,'seams':seams,'models':models,'policy':'Nominal integer-metre sheet-edge comparisons using exact source triangle barycentric heights. The nearest source point within 1 cm is accepted because tile boundary coordinates differ by up to 5 mm after source Float32 transforms. Original terrain/model heights stay unchanged; differing source revisions are retained, not aligned by invented offsets.'}
 (doc/'source-audit.json').write_text(json.dumps(report,indent=2,default=lambda v:v.item())+'\n');print(json.dumps({'counts':counts,'seams':[{k:v for k,v in s.items() if k!='largest'} for s in seams]},indent=2,default=lambda v:v.item()))
 return report
def main():audit_sources()
if __name__=='__main__':main()

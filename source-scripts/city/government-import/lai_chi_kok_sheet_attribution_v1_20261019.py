"""Attribute whole-source burial to exact adjoining sheets; no acceptance."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-lai-chi-kok-sheet-attribution-v1-20261019';DOC=BASE/BATCH
CURRENT=BASE/'government-xl-lai-chi-kok-current-scope-v1-20261019'
SRC=BASE/'government-xl-next-five-adjoining-ground-v1-20261018';UID='landsd/281463:0'
def main():
 assert not DOC.exists();r=read(CURRENT/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),CURRENT/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 selection=BASE/'government-xl-next-five-current-terrain-v1-20261018/selection.json.gz';row=next(x for x in read(selection)['rows']if x['uid']==UID)
 asset=ROOT/row['candidate']['path'];groundpath=HERE/'local'/SRC.name/'281463:0-ground.json.gz';acq=SRC/'acquisitions.json';prior=SRC/'281463:0.json'
 for p in [selection,asset,groundpath,acq,prior]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p;refs.append(p)
 triangles=decode_original_world_triangles(asset.read_bytes());assert len(triangles)==37577 and digest(asset.read_bytes())==row['sourceSHA256']
 ground=read(groundpath);native=np.asarray(ground['completeAdjoiningTerrain']);acquisitions={x['sheet']:x for x in read(acq)}
 points=np.concatenate([triangles,triangles.mean(1)[:,None,:]],axis=1);cross=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);area=np.linalg.norm(cross,axis=1)/2;upward=cross[:,1]>.25*np.linalg.norm(cross,axis=1)
 helper=module('lai_sheet_foundation',HERE/'xl-final-script-pass.py');heights=[];rows=[];offset=0
 for sheet in ground['sheets']:
  count=acquisitions[sheet]['triangles'];t=native[offset:offset+count];assert len(t)==count;offset+=count
  lo=triangles.min((0,1));hi=triangles.max((0,1));t=t[(t[:,:,0].max(1)>=lo[0]-1)&(t[:,:,0].min(1)<=hi[0]+1)&(t[:,:,2].max(1)>=lo[2]-1)&(t[:,:,2].min(1)<=hi[2]+1)]
  p=shapely.polygons(t[:,:,[0,2]]);valid=shapely.area(p)>1e-10;t=t[valid];p=p[valid]
  h=helper.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),t,shapely.STRtree(p)).reshape(-1,4);heights.append(h)
  complete=np.isfinite(h).all(1);buried=complete&((points[:,:,1]-h)<-.5).all(1)
  rows.append(dict(sheet=sheet,originalTerrainFaces=count,sourceFacesWithCompleteTerrain=int(complete.sum()),fullyBuriedFaces=int(buried.sum()),fullyBuriedUpwardFaces=int((buried&upward).sum()),fullyBuriedAreaM2=float(area[buried].sum()),buriedFaceIds=np.flatnonzero(buried).tolist()))
  print({k:v for k,v in rows[-1].items()if k!='buriedFaceIds'},flush=True)
 assert offset==len(native)
 heights=np.asarray(heights);finite=np.isfinite(heights);maximum=np.max(np.where(finite,heights,-np.inf),axis=0);assert np.isfinite(maximum).all()
 gaps=points[:,:,1]-maximum;buried=(gaps<-.5).all(1);expected=read(prior)['foundation'];assert int(buried.sum())==expected['fullyBuriedTriangles']==2591 and int((buried&upward).sum())==expected['fullyBuriedUpwardTriangles']==1598
 multiple=(finite.sum(0)>1);spread=maximum-np.min(np.where(finite,heights,np.inf),axis=0)
 selected=np.flatnonzero(buried);records=[]
 for i in selected:
  records.append(dict(faceId=int(i),vertices=triangles[i].tolist(),upward=bool(upward[i]),areaM2=float(area[i]),maxTerrainGaps=gaps[i].tolist(),winningSheetsPerSample=[[ground['sheets'][j]for j in range(len(heights))if finite[j,i,k]and abs(heights[j,i,k]-maximum[i,k])<1e-9]for k in range(4)],terrainHeightsBySheet={sheet:[float(v)if np.isfinite(v)else None for v in heights[j,i]]for j,sheet in enumerate(ground['sheets'])}))
 summary=dict(uid=UID,sourceSHA256=row['sourceSHA256'],sourceFaces=len(triangles),sheets=ground['sheets'],fullyBuriedFaces=int(buried.sum()),fullyBuriedUpwardFaces=int((buried&upward).sum()),samplesCoveredByMultipleSheets=int(multiple.sum()),maximumDifferenceBetweenSheetsM=float(spread[multiple].max())if multiple.any()else 0,sourceGeometryChanges=0,installationApproved=False,qualification='Exact original-sheet attribution only; source component roles, candidate placement and all retained-neighbour checks remain required.')
 save(DOC/'summary.json',dict(summary=summary,bySheet=rows));save(DOC/'buried-faces.json.gz',dict(summary=summary,faces=records))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 fig,ax=plt.subplots(figsize=(10,13));ax.add_collection(PolyCollection(triangles[:,:,[0,2]],facecolors='#dddddd',edgecolors='none'));ax.add_collection(PolyCollection(triangles[buried&~upward][:,:,[0,2]],facecolors='#e29d45',edgecolors='none'));ax.add_collection(PolyCollection(triangles[buried&upward][:,:,[0,2]],facecolors='#d84343',edgecolors='none'));ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Lai Chi Kok original source: buried upward faces red; other buried orange');ax.set_xlabel('World X metres');ax.set_ylabel('World Z metres');fig.savefig(DOC/'buried-faces.png',dpi=150);plt.close(fig)
 for p in [selection,asset,groundpath,acq,prior]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('lai_sheet_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'lai-chi-kok-original-sheet-burial-attribution',refs,dict(uids=[UID],summary=summary,installationApproved=False))
 print(summary,flush=True)
if __name__=='__main__':main()

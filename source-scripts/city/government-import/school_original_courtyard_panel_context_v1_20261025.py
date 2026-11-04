"""Exact source-role measurements and diagrams; no identity or physical approval."""
from pathlib import Path
from fractions import Fraction
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-school-original-courtyard-panel-context-v1-20261025'
RT='government-xl-quality-music-school-ramp-return-runtime-v5-20261025';LOW='government-xl-school-244581-ramp-return-complete-ground-v5-20261025';CAPS='government-xl-school-244581-ramp-return-cap-paths-v5-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(n,path):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(RT,BASE/RT/'selection.json.gz');g=next(r for r in take(RT,HERE/'local'/RT/'runtime-geometry.json.gz')['rows']if r['uid']=='landsd/244581:0');tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert g['sourceSHA256']=='26427158252a7943232c9c281d20dbbf24326c9aba26be028da4cb19d75e5393';target=shapely.union_all([shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:])for r in selection['rows']]);dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3);extent_ids=np.flatnonzero(dist.max(1)>10).tolist();assert len(extent_ids)==64
 ext=tri[extent_ids];assert ext[:,:,1].min()==88.1860122680664 and ext[:,:,1].max()==88.86001586914062
 caps=take(CAPS,BASE/CAPS/'summary.json');details=[];panel_ids=list(range(10594,10602))
 for mode in ['original','literal','left','balanced']:
  cap=next(r for r in caps['rows']if r['mode']==mode)['completeGroundClearancePartition'];failed=[r['sourceFace']for r in cap['paths']if not r['hasExactSharedEdgeClearCapPath']];assert failed==panel_ids
  low=take(LOW,BASE/LOW/(mode+'.json.gz'));assert low['sourceWorldSHA256']==next(r for r in caps['rows']if r['mode']==mode)['sourceWorldSHA256'];byid={r['sourceFace']:r for r in low['rows']};rows=[]
  for i in panel_ids:
   r=byid[i];assert r['absoluteNormalYRatio']<.25 and r['highestVertexAboveEveryOverlappingGroundFace']
   crossings=[]
   for pair in r['negativeGroundPairProofs']:
    gaps=[Fraction(v['exactGapM'])for v in pair['proof']['allExactBasicFeasibleColumnVertices']]
    if gaps and min(gaps)<0<max(gaps):crossings.append(pair['groundFace'])
   assert crossings
   rows.append(dict(sourceFace=i,highestVertexAboveEveryGroundFace=True,exactFiniteSameFaceGradeCrossings=crossings,rawMinimumGapM=r['minimumFiniteGapM']))
  details.append(dict(mode=mode,ordinaryCapPaths=144,originalOpenPanelFaces=rows))
 out.mkdir();fig=plt.figure(figsize=(16,10));ax=fig.add_subplot(221);ax.add_collection(PolyCollection(tri[:,:,[0,2]],facecolor='#d4d8d8',edgecolors='none'));ax.add_collection(PolyCollection(ext[:,:,[0,2]],facecolor='#d03938',edgecolors='#d03938'))
 for p in shapely.get_parts(target):
  x,z=p.exterior.xy;ax.plot(x,z,color='black',lw=1)
 ax.autoscale_view();ax.set_aspect('equal');ax.set_title('All original main source; black=current3footprints; red=64extent flags')
 for slot,faces,title in [(222,ext,'64 low source features; whole original triangles'),(223,tri[panel_ids],'Eight uncapped original vertical faces'),(224,tri[panel_ids],'Same eight faces, reverse view')]:
  ax=fig.add_subplot(slot,projection='3d');center=faces.mean((0,1));v=faces[:,:,[0,2,1]]-center[[0,2,1]];ax.add_collection3d(Poly3DCollection(v,facecolor='#c96546',edgecolor='#333333',linewidth=.25,alpha=.85));ax.auto_scale_xyz(v[:,:,0].ravel(),v[:,:,1].ravel(),v[:,:,2].ravel());ax.set_box_aspect(np.maximum(np.ptp(v.reshape(-1,3),axis=0),.1));ax.view_init(elev=32,azim=35 if slot!=224 else 215);ax.set_title(title)
 fig.tight_layout();fig.savefig(out/'exact-source-role-context.png',dpi=160);plt.close(fig)
 result=dict(uids=['landsd/244581:0'],sourceSHA256=g['sourceSHA256'],extentFaceIds=extent_ids,extentFeaturesYRangeM=[float(ext[:,:,1].min()),float(ext[:,:,1].max())],rawMaximumExtentM=float(dist.max()),fourWorldOpenPanelContexts=details,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,qualification='Closed exact-source diagnostic. 64rawextentfaces are low source features, not high building wings. Eight uncapped vertical faces lack the cap path but each has an exact finite ground crossing and a highest vertex above every overlapping ground facet in all4worlds. No source role, engineering, ground-root,10m-policy or publication approval is inferred; primary campus evidence and ROOT review remain separate.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'selected_original_four_world_low_face_context_v1_20261024.py']);module('school_courtyard_panel_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-school-low-feature-and-open-panel-role-context',refs,result)
if __name__=='__main__':main()

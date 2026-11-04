"""Measure original-TIN projection gaps against complete source/ground negatives.

Diagnostic geometry only: no terrain edits, coverage waiver or approval.
"""
import argparse
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','attributes','clearance','terrain-check','uid']:p.add_argument('--'+k,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();pins={};refs=[Path(__file__)]
 def take(n,path):
  if n not in pins:pins[n]=authenticate(base/n)[1];refs.append(base/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=take(a.runtime,base/a.runtime/'selection.json.gz');row=next(r for r in selected['rows']if r['uid']==a.uid)
 g=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid)
 attrs=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attr=next(r for r in attrs['rows']if r['uid']==a.uid)
 checked=next(r for r in take(a.terrain_check,base/a.terrain_check/'summary.json')['rows']if r['uid']==a.uid)
 asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==g['sourceSHA256']==attr['sourceSHA256']==checked['sourceSHA256'];refs.append(asset)
 decoder=module('original_tin_gap_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=local;terrain=[]
 for name in checked['sourceTerrainPaths']:
  path=ROOT/name;meta=take(a.terrain_check,path)
  for buffer in meta.get('buffers',[]):
   member=path.parent/buffer['uri'];assert digest(member.read_bytes())==pins[a.terrain_check][str(member.relative_to(ROOT))];refs.append(member)
  terrain.extend(decoder.terrain_triangles(path))
 terrain=np.asarray(terrain,dtype='<f8');assert len(terrain)>0
 polygons=shapely.polygons(terrain[:,:,[0,2]]);valid=shapely.area(polygons)>0;union=shapely.union_all(polygons[valid]);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 worlds={'original':decode_original_world_triangles(raw),**{m:np.asarray(attr[k],dtype='<f8').reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
 ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);results=[];plots=[]
 for mode,tri in worlds.items():
  proof=take(a.clearance,base/a.clearance/(mode+'.json.gz'));assert proof['sourceWorldSHA256']==digest(tri.tobytes())and proof['groundSHA256']==digest(ground.tobytes())and proof['completeSourceFaces']==len(tri)
  negative={r['sourceFace']:r for r in proof['rows']};hulls=[shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in tri];projection=shapely.union_all(hulls);missing=projection.difference(union);faces=[]
  for i,hull in enumerate(hulls):
   gap=hull.difference(union)
   if gap.is_empty:continue
   faces.append(dict(sourceFace=i,missingProjectionType=gap.geom_type,missingProjectionAreaM2=float(gap.area),currentGroundNegative=i in negative,missingBounds=list(gap.bounds),rawCurrentMinimumGapM=negative[i]['minimumFiniteGapM']if i in negative else None))
  negatives=[r for r in faces if r['currentGroundNegative']]
  result=dict(mode=mode,completeSourceFaces=len(tri),allCurrentNegativeFaces=sorted(negative),sourceProjectionAreaM2=float(projection.area),missingProjectionAreaM2=float(missing.area),missingProjectionBounds=list(missing.bounds)if not missing.is_empty else None,missingGeometryType=missing.geom_type,sourceFacesOutsideOriginalTIN=len(faces),negativeFacesOutsideOriginalTIN=len(negatives),negativeFaceIdsOutsideOriginalTIN=[r['sourceFace']for r in negatives],negativeFaceAreaOutsideOriginalTINM2=sum(r['missingProjectionAreaM2']for r in negatives),rows=faces)
  save(out/(mode+'-missing-projection.json.gz'),dict(**result,missingProjectionWKT=missing.wkt));results.append({k:v for k,v in result.items()if k!='rows'});plots.append((mode,projection,missing,tri,negative))
 fig,axes=plt.subplots(1,2,figsize=(12,6),layout='constrained')
 mode,projection,missing,tri,negative=plots[0]
 def drawpoly(ax,geometry,color,alpha):
  if hasattr(geometry,'geoms'):
   for g in geometry.geoms:drawpoly(ax,g,color,alpha)
  elif geometry.geom_type=='Polygon':
   x,y=geometry.exterior.xy;ax.fill(x,y,color=color,alpha=alpha)
  elif geometry.geom_type in ['LineString','LinearRing']:
   x,y=geometry.xy;ax.plot(x,y,color=color,alpha=alpha)
 drawpoly(axes[0],projection,'steelblue',.5);drawpoly(axes[0],missing,'crimson',.9)
 drawpoly(axes[1],projection,'lightgrey',.5)
 for i in negative:drawpoly(axes[1],shapely.MultiPoint(tri[i][:,[0,2]]).convex_hull,'darkorange',.9)
 drawpoly(axes[1],missing,'crimson',.9)
 for ax in axes:ax.set_aspect('equal');ax.set(xlabel='Local easting (m)',ylabel='Local z (m)');ax.grid(alpha=.2)
 axes[0].set_title('Whole original projection (blue), outside original TIN (red)');axes[1].set_title('Current negative faces (orange), missing TIN (red)')
 figure=out/'original-tin-gap-and-current-negative-faces.png';fig.savefig(figure,dpi=160);plt.close(fig);refs.append(figure)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 summary=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],currentManifestSHA256=selected['manifestSHA256'],originalTerrainFaces=len(terrain),rows=results,projectionDiagnosticOnly=True,exactFiniteMissingRegionClearanceProven=False,sourceGeometryChanges=0,terrainEdits=False,installationApproved=False,physicalAcceptance=False,publication=False,qualification='Shapely projected gaps for all complete source streams, classified against exactly rebound complete actual-ground negative faces. Every source face and raw negative remains. This diagnoses whether a hybrid local terrain proposal merits exact finite checking; it grants no missing-coverage or clearance exemption.')
 save(out/'summary.json',summary);refs.extend([HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py']);refs.extend(q for q in local.rglob('*')if q.is_file())
 module('original_tin_missing_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-tin-projection-gap-and-current-negative-region-diagnostic',refs,summary)


if __name__=='__main__':main()

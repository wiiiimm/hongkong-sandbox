"""Bind the actual F/E joint locus and primary records; source geometry stays untouched."""
from pathlib import Path
from fractions import Fraction
import numpy as np,shapely
from shapely.geometry import Polygon,Point
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-fe-joint-locus-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime='government-xl-beverly-fe-after-k-runtime-v1-20261025';selection=take(runtime,'selection.json.gz');by={r['uid']:r for r in selection['rows']};uids=['landsd/256334:0','landsd/256142:0'];assert set(by)==set(uids)
 roles='government-xl-beverly-fe-after-k-pair-roles-v1-20261025';summary=take(roles,'summary.json');assert summary['uids']==uids and all(r['contactCount']==34and r['roles']['transverse-surface-crossing']==15for r in summary['rows'])
 raw=take(roles,'original.json.gz');triangles=[];polys=[];sources={}
 for uid in uids:
  r=by[uid];asset=ROOT/r['candidate']['path'];sources[uid]=digest(asset.read_bytes());assert sources[uid]==r['sourceSHA256']==summary['sourceSHA256ByUid'][uid];refs.append(asset);triangles.append(decode_original_world_triangles(asset.read_bytes()));f=r['source']['building'];polys.append(Polygon(f['rings'][0],f['rings'][1:]))
 facts=[]
 for role in sorted({c['contactRole']for c in raw}):
  contacts=[c for c in raw if c['contactRole']==role];points=[tuple(Fraction(v)for v in q)for c in contacts for q in c['exactPoints']];lo=[min(q[i]for q in points)for i in range(3)];hi=[max(q[i]for q in points)for i in range(3)];facts.append(dict(role=role,contacts=len(contacts),exactBounds=[[str(v)for v in lo],[str(v)for v in hi]],bounds=[[float(v)for v in lo],[float(v)for v in hi]],horizontalSpanM=[float(hi[i]-lo[i])for i in [0,2]],maximumDistanceToRecordedBoundaryM=[max(Point(float(q[0]),float(q[2])).distance(p.boundary)for q in points)for p in polys]))
 projected=[]
 for t in triangles:
  v=t[:,:,[0,2]];twice=(v[:,1,0]-v[:,0,0])*(v[:,2,1]-v[:,0,1])-(v[:,1,1]-v[:,0,1])*(v[:,2,0]-v[:,0,0]);projected.append(shapely.union_all(shapely.polygons(v[twice!=0])))
 primary='government-xl-beverly-fe-after-k-primary-records-v1-20261025';relations=take(primary,'relations.json')['features'];structures=take(primary,'structures.json')['features'];structure_by={r['attributes']['BuildingStructureID']:r['attributes']for r in structures};records=[]
 for uid in uids:
  csuid=by[uid]['source']['building']['buildingCSUID'];matches=[r['attributes']for r in relations if r['attributes']['BuildingCSUID']==csuid];assert len(matches)==1;structure=structure_by[matches[0]['BuildingStructureID']];records.append(dict(uid=uid,buildingCSUID=csuid,relation=matches[0],structure=structure))
 assert len({r['structure']['OPNo']for r in records})==1 and all(r['structure']['Storeys']==30for r in records)
 out.mkdir();fig,axes=plt.subplots(1,2,figsize=(14,7));colours=['tab:blue','tab:orange']
 for ax in axes:
  for uid,p,colour in zip(uids,polys,colours):x,z=p.exterior.xy;ax.plot(x,z,color=colour,label=by[uid]['source']['building']['name'])
  for c in raw:
   pts=np.asarray([[float(Fraction(v))for v in q]for q in c['exactPoints']]);ax.plot(pts[:,0],pts[:,2],color='red'if c['contactRole']=='transverse-surface-crossing'else'purple',linewidth=1,marker='.',markersize=2)
  ax.set_aspect('equal');ax.set_xlabel('Viewer east (m)');ax.set_ylabel('Viewer Z (m)');ax.ticklabel_format(useOffset=False);ax.grid(alpha=.2)
 cross=next(r for r in facts if r['role']=='transverse-surface-crossing');lo,hi=np.asarray(cross['bounds']);axes[0].set_title('Complete recorded footprints and original contacts');axes[0].legend();axes[1].set_xlim(lo[0]-.3,hi[0]+.3);axes[1].set_ylim(lo[2]-.3,hi[2]+.3);axes[1].set_title('Original transverse contact strip (red)');fig.tight_layout();fig.savefig(out/'joint-plan-and-locus.png',dpi=160);plt.close(fig)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 result=dict(uids=uids,sourceSHA256ByUid=sources,contactRoles=facts,recordedFootprintOverlapM2=polys[0].intersection(polys[1]).area,recordedFootprintDistanceM=polys[0].distance(polys[1]),sourceProjectedUnionOverlapM2=projected[0].intersection(projected[1]).area,projectionAreaIsDiagnosticDoublePrecision=True,primaryRecords=records,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Full source geometry and all34 original contacts retained. Exact rational contact bounds and geometric crossing classifications do not prove architectural intent or absence of interpenetration. Primary records independently identify both30-storey towers under one occupancy permit. Small façade-joint locus and footprint/source-projection facts are context for a bounded visual/source-role review, not automatic acceptance.')
 save(out/'summary.json',result);module('beverly_fe_joint_locus_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-joint-locus-and-primary-record-context',refs,result)
if __name__=='__main__':main()

"""Inspect exact original inward walls and empty source projections, without repair.
New diagnostic only: raw coverage retained and no courtyard identity credit granted.
"""
import importlib.util
import numpy as np,shapely
from shapely.geometry import Polygon,LineString,mapping
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from government_georef_cell_identity import geographic_cell
OLD=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009';DOC=ROOT/'docs/astra-city/government-import/government-xl-source-authored-openings-20261009';LOCAL=HERE/'local/government-xl-spatial-surface-roles-20261009'
s=importlib.util.spec_from_file_location('openings_source_decode',HERE/'xl-second-pass.py');dec=importlib.util.module_from_spec(s);s.loader.exec_module(dec)
rows=[]
for uid in ['157125-0','295538-0']:
 r=read(OLD/(uid+'.json.gz'));v=r['variants']['direct-shared-OSM'];tri=dec.context.triangles(LOCAL/'unpacked'/r['modelId']/'model.gltf');assert digest(tri.astype('<f8').tobytes())==r['worldTrianglesSHA256'];projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));target=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:]) for b in v['groupForms']]);holes=[Polygon(ring) for p in ([projection] if projection.geom_type=='Polygon' else projection.geoms) if p.geom_type=='Polygon' for ring in p.interiors];holes=sorted(holes,key=lambda p:-p.area);b=next(b for b in v['groupForms'] if b['uid']==r['uid']);cell=geographic_cell(r['modelId'],b['buildingCSUID'],b['structureType']);proofs=[]
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(normals,axis=1);vertical=(norm>1e-10)&(np.abs(normals[:,1])<=1e-6*norm)
 for hole in holes:
  if hole.area<.01:continue
  ring=hole.exterior;edges=[];faces=[]
  for i,t in enumerate(tri[vertical]):
   p=shapely.convex_hull(shapely.multipoints(t[:,[0,2]]));line=ring.intersection(p)
   if line.length>1e-6:edges += [g for g in ([line] if line.geom_type in ['LineString','LinearRing'] else line.geoms if hasattr(line,'geoms') else []) if g.geom_type in ['LineString','LinearRing']];faces.append(t)
  faces=np.array(faces);edgeunion=shapely.union_all(edges);wallCoverage=float(edgeunion.length/ring.length) if ring.length else 0;stats={'areaM2':float(hole.area),'perimeterM':float(ring.length),'insideFullTarget':bool(target.covers(hole)),'distanceToTargetBoundaryM':float(hole.distance(target.boundary)),'innerVerticalFaceCount':len(faces),'exactInnerWallPerimeterCoverage':wallCoverage,'innerWallYRange':[float(faces[:,:,1].min()),float(faces[:,:,1].max())] if len(faces) else None,'unmatchedRimLengthM':float(ring.difference(edgeunion).length),'containsSourceWholeCell':bool(hole.covers(cell)),'intersectsSourceWholeCell':bool(hole.intersects(cell)),'geometry':mapping(hole),'qualification':'Inner walls geometrically bound the empty projection; semantic courtyard/open sky versus absent floor/roof needs primary design evidence. No inferred model completeness or physical acceptance.'};proofs.append(stats)
 # Diagnostic denominator only, not edited footprint or accepted coverage.
 inside=[p for p in holes if target.covers(p)];excluded=shapely.union_all(inside);built=target.difference(excluded);rawCoverage=float(target.intersection(projection).area/target.area);diagnostic=float(built.intersection(projection).area/built.area)
 fig,axs=plt.subplots(1,2,figsize=(12,6));ax=axs[0]
 for p in ([projection] if projection.geom_type=='Polygon' else projection.geoms):
  if p.geom_type!='Polygon':continue
  x,z=p.exterior.xy;ax.fill(x,z,color='#2a9d8f',alpha=.5)
  for ring in p.interiors:x,z=ring.xy;ax.fill(x,z,color='white')
 for p in v['groupForms']:
  for ring in p['rings']:x,z=np.array(ring).T;ax.plot(x,z,color='black',linewidth=.8)
 for hole in holes:
  if hole.area<.01:continue
  x,z=hole.exterior.xy;ax.fill(x,z,color='#e63946',alpha=.7)
 x,z=cell.exterior.xy;ax.plot(x,z,color='purple',linewidth=1);ax.set_aspect('equal');ax.invert_yaxis();ax.set_title(r['name'] or r['modelId']);points=tri.reshape(-1,3);axs[1].scatter(points[:,0]-.4*points[:,2],points[:,1]+.3*points[:,2],c=points[:,1],s=.03,cmap='viridis');axs[1].set_aspect('equal');axs[1].set_title('Every unchanged original vertex');fig.tight_layout();(DOC/uid).mkdir(parents=True,exist_ok=True);fig.savefig(DOC/uid/'full-original-openings.png',dpi=180);plt.close(fig)
 item={'uid':r['uid'],'name':r['name'],'modelId':r['modelId'],'sourceKey':r['sourceKey'],'sourceSHA256':r['sourceSHA256'],'worldTrianglesSHA256':r['worldTrianglesSHA256'],'originalPath':r['originalPath'],'sourceSurfaceRoleInput':{'path':str((OLD/(uid+'.json.gz')).relative_to(ROOT)),'sha256':digest((OLD/(uid+'.json.gz')).read_bytes())},'groupForms':v['groupForms'],'originalBounds':[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],'rawTargetCoverage':rawCoverage,'wholeOriginalTargetCell':bool(target.covers(cell)),'wholeOriginalSourceProjectionCell':bool(projection.covers(cell)),'sourceProjectionOpeningCount':len(holes),'sourceAuthoredOpeningDiagnostics':proofs,'notAcceptedOpeningAdjustedCoverage':diagnostic,'notAcceptedOpeningsAreaM2':float(excluded.area),'identityAccepted':False,'installationApproved':False,'geometryChanges':0,'qualification':'All original triangles, source poses, current forms and strict raw metrics retained. Adjusted denominator is explicit diagnostic, not courtyard credit, source edit or coverage waiver. Positive alternative requires documented visible-surface roles and complete original ownership plus fresh full gates.'};save(DOC/uid/'opening-diagnostics.json.gz',item);rows.append(item);print({k:item[k] for k in ['uid','rawTargetCoverage','notAcceptedOpeningAdjustedCoverage','wholeOriginalTargetCell','wholeOriginalSourceProjectionCell']}|{'largestOpenings':[{k:p[k] for k in ['areaM2','innerVerticalFaceCount','exactInnerWallPerimeterCoverage','innerWallYRange','containsSourceWholeCell']} for p in proofs[:5]]},flush=True)
save(DOC/'original-opening-diagnostics.json.gz',{'rows':rows})

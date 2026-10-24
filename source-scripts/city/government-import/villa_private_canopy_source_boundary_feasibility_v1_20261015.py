"""Private source-backed fallback footprint correction feasibility; never edits originals/live data."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon,mapping
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-private-canopy-source-boundary-feasibility-v1-20261015';DOC=B/NAME
OLD=B/'government-xl-villa-premiere-complete-record-projection-identity-20261010';UID='landsd/325786:0'
def main():
 assert not DOC.exists();row=read(OLD/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==16669
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);tilepath=ROOT/'3d-viewer/city/data/tiles/-7_-9.json';tile=read(tilepath);forms={x['uid']:x for x in tile['buildings']};canopy=forms[UID];assert canopy['buildingCSUID']=='2162233384T20211022';assert forms[row['uid']]['buildingCSUID']==row['source']['building']['buildingCSUID']
 # Retain actual current source identity and every full original face in the union.
 roof=Polygon(canopy['rings'][0],canopy['rings'][1:]);assert roof.is_valid
 source=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));cut=roof.intersection(source);candidate=roof.difference(source)
 assert candidate.is_valid and not candidate.is_empty;assert candidate.difference(roof).area==0
 retained_fraction=candidate.area/roof.area;residual=candidate.intersection(source).area
 parts=list(candidate.geoms) if candidate.geom_type=='MultiPolygon' else [candidate];assert all(p.geom_type=='Polygon' for p in parts)
 plan={'uid':UID,'sourceBuildingUID':row['uid'],'sourceSHA256':row['sourceSHA256'],'manifestSHA256':digest(manifestpath.read_bytes()),'tileSHA256':digest(tilepath.read_bytes()),'completeOriginalFaces':len(tri),'currentForm':canopy,'sourceForm':forms[row['uid']],'privateCandidateRings':[[list(p.exterior.coords),*[list(r.coords) for r in p.interiors]] for p in parts],'originalFootprintAreaM2':roof.area,'removedSourceOccupiedProjectionAreaM2':cut.area,'retainedFootprintAreaM2':candidate.area,'retainedFraction':retained_fraction,'candidateParts':len(parts),'residualProjectedIntersectionAreaM2':residual,'policy':'Private compute-only feasibility: subtract the complete immutable podium projection from the estimated procedural canopy footprint; preserve canopy actor, heights and every government source triangle. No buffer or height guess. Not yet rendered or collision accepted.','sourceBuildingGeometryChanged':False,'liveGeometryChanged':False,'proposedProceduralGeometryChange':True,'installationApproved':False}
 DOC.mkdir();save(DOC/'proposal.json',plan);save(DOC/'footprints.geojson',{'type':'FeatureCollection','features':[{'type':'Feature','properties':{'role':role},'geometry':mapping(g)} for role,g in [('current-canopy',roof),('source-occupied-cut',cut),('private-candidate',candidate)]]})
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(9,7))
 for g,color,label in [(roof,'#aaaaaa','Current estimated canopy'),(candidate,'#4488aa','Retained canopy'),(cut,'#dd6655','Source-occupied projection')]:
  polys=list(g.geoms) if hasattr(g,'geoms') else [g]
  for i,p in enumerate(polys):
   if p.geom_type!='Polygon':continue
   xy=np.array(p.exterior.coords);ax.fill(xy[:,0],xy[:,1],color=color,alpha=.7,label=label if i==0 else None)
 ax.set_aspect('equal');ax.legend();ax.set_title('Private Villa canopy correction feasibility\nOriginal government podium remains unchanged');fig.savefig(DOC/'private-footprint.png',dpi=150);plt.close(fig)
 paths=[Path(__file__),OLD/'selection.json.gz',asset,manifestpath,tilepath,HERE/'exact_packed_world_geometry_20261009.py']
 module('villa_private_boundary_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'private-source-backed-procedural-canopy-boundary-feasibility-v1',paths,{'uids':[row['uid'],UID],**{k:v for k,v in plan.items() if k not in ['currentForm','sourceForm','privateCandidateRings','policy']},'nextStep':'Render the exact private candidate using production canopy construction, check actual Float32 wall/roof intersections, all retained canopy components and full five-source placement/neighbour/runtime gates before any live change.'});print({k:plan[k] for k in ['retainedFraction','candidateParts','removedSourceOccupiedProjectionAreaM2','residualProjectedIntersectionAreaM2']},flush=True)
if __name__=='__main__':main()

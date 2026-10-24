"""Complete original commercial projection gap, visibly retained without threshold changes."""
from pathlib import Path
import json,numpy as np,shapely
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-commercial-complete-coverage-context-20261010'
RAW=DOC.parent/'government-xl-tung-sing-commercial-current-identity-diagnostic-20261010';PAIR=DOC.parent/'government-xl-tung-sing-interior-current-identity-inputs-v2-20261010/selection.json.gz'
def outline(ax,p,**kwargs):
 for q in shapely.get_parts(p):
  if q.geom_type=='Polygon':
   xy=np.array(q.exterior.coords);ax.plot(xy[:,0],xy[:,1],**kwargs)
   for r in q.interiors:
    xy=np.array(r.coords);ax.plot(xy[:,0],xy[:,1],**kwargs)
def main():
 assert not DOC.exists();own=read(RAW/'selection.json.gz')['rows'][0];pod=next(r for r in read(PAIR)['rows'] if r['uid']=='landsd/126434:0');rows=[own,pod];a=[decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows];p=[shapely.union_all(shapely.polygons(t[:,:,[0,2]])) for t in a];q=shapely.Polygon(own['source']['building']['rings'][0]);missing=q.difference(p[0]);parts=[]
 for part in shapely.get_parts(missing):
  if part.geom_type!='Polygon':continue
  touch=part.boundary.intersection(q.boundary);vertices=np.array(part.exterior.coords);parts.append({'areaM2':float(part.area),'bounds':list(part.bounds),'fullExactReportedGeoJSON':json.loads(shapely.to_geojson(part)),'touchesTargetOuterBoundary':bool(not touch.is_empty),'outerBoundaryContactLengthM':float(touch.length),'maximumVertexDistanceToWholeOwnProjectionM':float(shapely.distance(shapely.points(vertices),p[0]).max()),'originalPodiumCoversMissingPart':bool(p[1].covers(part)),'originalPodiumUncoveredMissingAreaM2':float(part.difference(p[1]).area)})
 DOC.mkdir(parents=True);fig,ax=plt.subplots(figsize=(12,10),dpi=200);outline(ax,p[1],color='#40906b',linewidth=.7);outline(ax,p[0],color='#3568b7',linewidth=1.0);outline(ax,q,color='black',linewidth=1.2)
 for g in shapely.get_parts(missing):
  if g.geom_type=='Polygon':xy=np.array(g.exterior.coords);ax.fill(xy[:,0],xy[:,1],color='#e54955',alpha=.8)
 x0,z0,x1,z1=q.bounds;ax.set_xlim(x0-8,x1+8);ax.set_ylim(z1+8,z0-8);ax.set_aspect('equal');ax.set_xlabel('Exact source/current viewer X (m)');ax.set_ylabel('Exact source/current viewer Z (m; north upward)');ax.set_title('Lei Tung Commercial Centre Phase2 — complete original projection\nBlack: current target; blue: original Tower; green: full original Podium; red: all uncovered target areas');fig.tight_layout();fig.savefig(DOC/'complete-original-coverage-overlay-2400x2000.png');plt.close(fig)
 inputs=[Path(__file__),RAW/'selection.json.gz',PAIR,*[ROOT/r['candidate']['path'] for r in rows],HERE/'exact_packed_world_geometry_20261009.py'];save(DOC/'diagnostic.json.gz',{'uid':own['uid'],'completeOriginalFaces':len(a[0]),'wholeTargetAreaM2':q.area,'wholeOwnOriginalCoverage':p[0].intersection(q).area/q.area,'wholeTwoOriginalCoverage':shapely.union_all(p).intersection(q).area/q.area,'completeMissingTargetAreaM2':missing.area,'allMissingTargetPolygons':parts,'originalPodiumMissingCoverageAreaM2':missing.difference(p[1]).area,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs},'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'qualification':'All missing target polygons remain exact diagnostics; courtyard/exterior/support/ownership roles are not inferred. A complete source-family identity route requires independent named primary/component role evidence and all physical gates.'});print({'missingPieces':len(parts),'area':missing.area,'boundaryPieces':sum(r['touchesTargetOuterBoundary'] for r in parts),'maxVertexGap':max(r['maximumVertexDistanceToWholeOwnProjectionM'] for r in parts),'fullOriginalPodiumMissingArea':missing.difference(p[1]).area},flush=True)
if __name__=='__main__':main()

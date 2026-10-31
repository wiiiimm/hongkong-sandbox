"""Whole untouched source projections against three actually regressed basic actors."""
import json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-three-basic-source-intersections-20261010'
PHYS=DOC.parent/'government-xl-tung-sing-two-flat-original-physical-v4-20261010'
def polygon(rings):
 p=shapely.Polygon()
 for ring in rings:p=p.symmetric_difference(shapely.Polygon(ring))
 assert p.is_valid and p.area>0
 return p
def main():
 assert not DOC.exists();selected=read(PHYS/'selection.json.gz')['rows'];neighbours=read(PHYS/'neighbour-inputs.json.gz');checks=read(PHYS/'neighbour-checks.json')['rows'];sources=[];paths=[]
 for row in selected:
  p=ROOT/row['candidate']['path'];raw=p.read_bytes();assert digest(raw)==row['sourceSHA256'];a=decode_original_world_triangles(raw);assert len(a)==row['triangles'];sources.append((row,a,shapely.union_all(shapely.polygons(a[:,:,[0,2]]))));paths.append(p)
 rows=[]
 for uid in ['landsd/124952:0','landsd/254604:0','landsd/341948:0']:
  own=next(r for r in neighbours['rows'] if r['building']['uid']==uid);building=own['building'];q=polygon(building['rings']);out=[]
  for source,a,p in sources:
   ids=[i for i,face in enumerate(a) if shapely.Polygon(face[:,[0,2]]).intersects(q)]
   out.append({'uid':source['uid'],'sourceSHA256':source['sourceSHA256'],'completeWorldSHA256':digest(a.astype('<f8').tobytes()),'completeSourceFaces':len(a),'wholeProjectionIntersects':bool(p.intersects(q)),'wholeProjectionIntersectionAreaM2':float(p.intersection(q).area),'wholeProjectionDistanceM':float(p.distance(q)),'allIntersectingOriginalFaceIds':ids,'allIntersectingOriginalTriangles':a[ids].tolist()})
  rows.append({'uid':uid,'completeCurrentBuilding':building,'rawCurrentPhysicalCheck':next(c for c in checks if c['uid']==uid),'wholeOriginalSources':out,'sourceModelOmissions':0,'physicalAccepted':False,'qualification':'Whole-source disjointness is a candidate cause only; no terrain-retention, actor-exemption or source-relationship acceptance.'})
 inputs=[Path(__file__),PHYS/'selection.json.gz',PHYS/'neighbour-inputs.json.gz',PHYS/'neighbour-checks.json',HERE/'exact_packed_world_geometry_20261009.py',*paths]
 save(DOC/'diagnostic.json.gz',{'rows':rows,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs},'sourceGeometryChanges':0,'physicalAccepted':False,'currentHistoricalManifestSHA256':read(PHYS/'selection.json.gz')['manifestSHA256']})
 print(json.dumps([{'uid':r['uid'],'sources':[{k:v for k,v in s.items() if k not in ['allIntersectingOriginalTriangles','allIntersectingOriginalFaceIds']} for s in r['wholeOriginalSources']]} for r in rows]),flush=True)
if __name__=='__main__':main()

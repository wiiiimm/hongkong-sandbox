"""Measure source/form relationships for the ten recorded Primrose warnings."""
from pathlib import Path
import importlib.util
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-primrose-podium-current-physical-20261007';BATCH='government-xl-primrose-neighbour-source-scope-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 source=read(OLD/'selection.json.gz')['rows'][0];asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;projection=shapely.union_all(polys[valid]);tree=shapely.STRtree(polys)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');patch=read(OLD/'terrain-candidates.json')[0];domain=box(*patch['bounds']);forms={};tilepaths=[]
 for tile in manifest['tiles']:
  if box(*tile['bounds']).intersects(domain):
   p=ROOT/'3d-viewer'/tile['url'];tilepaths.append(p)
   for b in read(p)['buildings']:
    if b.get('rings'):
     poly=shapely.make_valid(Polygon(b['rings'][0],b['rings'][1:]))
     if poly.intersects(domain):forms[b['uid']]=(b,poly,str(p.relative_to(ROOT)))
 historical={r['building']['uid']:r['building']for r in read(OLD/'neighbour-inputs.json.gz')['rows']};bad=[r for r in read(OLD/'neighbour-checks.json')['rows']if r['reasons']];rows=[]
 for r in bad:
  b,poly,tile=forms[r['uid']];hits=tree.query(poly,predicate='intersects');hits=hits[valid[hits]];overlap=float(projection.intersection(poly).area);distance=float(projection.distance(poly));pieces=tri[hits];source_y=[float(pieces[:,:,1].min()),float(pieces[:,:,1].max())]if len(hits)else None
  rows.append(dict(uid=b['uid'],currentForm=b,currentEqualsHistorical=b==historical[b['uid']],tile=tile,structureType=b.get('structureType'),sourceProjectionIntersectionM2=overlap,sourceProjectionCoverage=overlap/poly.area if poly.area else None,sourceProjectionDistanceM=distance,intersectingSourceFaceCount=len(hits),intersectingSourceYRange=source_y,recordedBase=b['base'],historicalReasons=r['reasons'],provisionalRoute='compound-support-review'if overlap>0 else'preserve-current-ground-outside-original-source',halfSeparationProposalM=distance/2 if distance else None))
 DOC.mkdir();save(DOC/'scope.json',dict(rows=rows,wholeParentBounds=patch['bounds'],sourceSHA256=source['sourceSHA256'],completeOriginalSourceTriangles=len(tri),sourceGeometryChanges=0,allAffectedFormsUnchanged=all(r['currentEqualsHistorical']for r in rows),qualification='Projection relationships nominate repair routes only. Half-distance is a proposal, not exact clearance or collar proof. Full actual source/BASIC/native actor bounds and complete current terrain regressions remain required.',publication=False,installationApproved=False))
 refs=[ROOT/q['path']for q in receipt['evidenceRefs']]+[OLD/'result.json',asset,ROOT/'3d-viewer/city/data/manifest.json',Path(__file__),HERE/'exact_packed_world_geometry_20261009.py']+tilepaths
 spec=importlib.util.spec_from_file_location('checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'current-neighbour-original-source-projection-routing-v1',refs,dict(uids=[source['uid']]+[r['uid']for r in rows],fullAcceptance=False,sourceGeometryChanges=0,qualification='Measured current original-source neighbour scope; repair route nomination only.'))
 print([(r['uid'],round(r['sourceProjectionCoverage'],4),round(r['sourceProjectionDistanceM'],4),r['currentEqualsHistorical'])for r in rows],flush=True)
if __name__=='__main__':main()

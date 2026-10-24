"""Measure exact original projection/current footprint differences; diagnostic only."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-lai-chi-kok-component-boundary-audit-v1-20261019'
BASE=ROOT/'docs/astra-city/government-import'
SRC=BASE/'government-xl-lai-chi-kok-original-component-checks-v1-20261019'
DOC=BASE/BATCH

def main():
 assert not DOC.exists(), 'Existing evidence must not be overwritten'
 receipt=read(SRC/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[__file__,SRC/'result.json',SRC/'selection.json.gz'];pins={}
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];pins[p]=e['sha256'];refs.append(p)
 results=[]
 for row in read(SRC/'selection.json.gz')['rows']:
  path=ROOT/row['candidate']['path'];tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles']
  b=row['source']['building'];foot=Polygon(b['rings'][0],b['rings'][1:]);assert foot.is_valid
  faces=[Polygon(t[:,[0,2]]) for t in tri];projection=unary_union([p for p in faces if p.area>0]);assert projection.is_valid
  missing=foot.difference(projection);extra=projection.difference(foot)
  parts=list(missing.geoms) if missing.geom_type=='MultiPolygon' else [missing]
  out=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],triangles=len(tri),footprintArea=foot.area,sourceProjectionArea=projection.area,missingFootprintArea=missing.area,extraSourceArea=extra.area,targetCoverage=foot.intersection(projection).area/foot.area,boundaryHausdorffMetres=foot.boundary.hausdorff_distance(projection.boundary),missingParts=[dict(area=p.area,bounds=list(p.bounds)) for p in parts if not p.is_empty],identityAccepted=False,installationApproved=False)
  save(DOC/(row['uid'].split('/')[1]+'-difference.json'),dict(summary=out,missing=missing.__geo_interface__,extra=extra.__geo_interface__))
  results.append(out);refs.append(path);print(out,flush=True)
 for p,h in pins.items():assert digest(p.read_bytes())==h,p
 summary=dict(uids=[r["uid"] for r in results],rows=results,installationApproved=False,interpretation='Quantitative diagnostic only; no identity, support or publication approval.')
 save(DOC/'summary.json',summary)
 module('boundary_audit_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-component-footprint-difference-diagnostic',list(dict.fromkeys(map(Path,refs))),summary)
if __name__=='__main__':main()

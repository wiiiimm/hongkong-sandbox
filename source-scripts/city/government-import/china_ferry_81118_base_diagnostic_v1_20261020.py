"""Whole-footprint terrain bounds for an existing unsurveyed BASIC fallback; no edits."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import get_coordinates
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-81118-base-diagnostic-v1-20261020';DOC=BASE/BATCH
CAP=BASE/'government-xl-china-ferry-five-private-terrain-v1-20261020';NEI=BASE/'government-xl-china-ferry-current-neighbours-v1-20261020';UID='landsd/81118:0'
assert not DOC.exists();pins={};refs=[Path(__file__)]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [CAP,NEI]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
b=next(x['building']for x in read(NEI/'neighbour-inputs.json.gz')['rows']if x['building']['uid']==UID)
assert b['baseSource']=='terrain-estimated' and b['heightSource']=='estimated' and b.get('baseHeightHKPD')is None and b.get('topHeightHKPD')is None and not b.get('modelGeometry')
poly=Polygon(b['rings'][0],b['rings'][1:]);row=next(x for x in read(HERE/'local'/CAP.name/'runtime-geometry.json.gz')['rows']if x['uid']=='landsd/285642:0');ground=np.asarray(row['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
parts=[];vals=[];faces=[]
for i,t in enumerate(ground):
 p=Polygon(t[:,[0,2]])
 if p.area<1e-12 or not p.intersects(poly):continue
 piece=p.intersection(poly)
 if piece.area<1e-12:continue
 coefficients=np.linalg.solve(np.column_stack([t[:,0],t[:,2],np.ones(3)]),t[:,1]);xy=get_coordinates(piece);ys=np.column_stack([xy,np.ones(len(xy))])@coefficients
 parts.append(piece);vals.extend(ys.tolist());faces.append(dict(face=i,area=piece.area,min=float(min(ys)),max=float(max(ys))))
missing=poly.difference(unary_union(parts)).area;assert vals and missing<1e-7
lo=min(vals);hi=max(vals)
result=dict(uids=[UID],previousBase=b['base'],conservativeAllSurfaceMin=lo,conservativeAllSurfaceMax=hi,missingArea=missing,groundRange=hi-lo,possibleEstimatedBase=lo,maximumBurialAtSuggestedBase=hi-lo,unchangedHeight=b['height'],sourceFieldsRemainNull=True,geometryChanges=0,installationApproved=False,baseUpdateApproved=False,policy='Bounds include every nonvertical drawn surface intersecting the full footprint. This is a conservative envelope, not an assertion of surveyed placement or ancillary identity. Preserve BASIC fallback; do not suppress it as a tower component.')
save(DOC/'terrain-envelope.json',dict(**result,faces=faces,building=b,drawnGroundSHA256=digest(ground.tobytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
refs.append(ROOT/'source-scripts/city/island-detail-integration/publish.py')
module('china_ferry_base_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-estimated-basic-full-footprint-terrain-envelope',list(dict.fromkeys(refs)),result)
print(result,flush=True)

"""Bind same-XZ source streams to complete existing continuous terrain diagnostics."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympic-four-stream-transport-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name,local=False):
  folder=BASE/batch;_,pins=authenticate(folder);p=(HERE/'local'/batch if local else folder)/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return read(p)
 runtime='government-xl-olympic-station-band-runtime-v1-20261022';row=take(runtime,'selection.json.gz')['rows'][0];g=take(runtime,'runtime-geometry.json.gz',True)['rows'][0];context=take('government-xl-olympic-station-band-continuous-v1-20261022','81242:0.json.gz');attrs=take('government-xl-olympic-station-original-attributes-v1-20261022','attributes.json.gz')['rows'][0];paths=take('government-xl-olympic-station-original-wall-paths-v2-20261022','paths.json.gz');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==g['sourceSHA256'];refs.append(asset);ix=np.asarray(attrs['completeOriginalIndex']).reshape(-1,3);streams=dict(original=decode_original_world_triangles(asset.read_bytes()))
 for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[mode]=np.asarray(attrs[key]).reshape(-1,3)[ix]
 literal=streams['literal'];assert digest(literal.tobytes())==context['sourceBinding']['decodedWorldTrianglesSHA256'];assert context['wholeSourceUncoveredFaces']==0;affected=set(context['affectedWallFaces']);rows=[]
 for mode,tri in streams.items():
  assert np.array_equal(tri[:,:,[0,2]],literal[:,:,[0,2]]),'Changed source projection needs fresh full coverage/clearance check';differences=np.abs(tri[:,:,1]-literal[:,:,1]);delta=differences.max(1);assert np.all(tri[:,:,1]>.5*literal[:,:,1])and np.all(tri[:,:,1]<2*literal[:,:,1]) # Sterbenz: binary subtraction is exact here.
  lower=np.asarray([c['minimum']['minimumGapM']for c in context['faces']])-delta;ordinary=[i for i in range(len(tri))if i not in affected];assert lower[ordinary].min()>=-.5;normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(tri)),where=length>0);assert all(length[i]>0 and abs(ratio[i])<=.25 for i in affected);edgechecks=0
  for p in paths['faces']:
   route=p['wallToRoofPath'];assert route[-1]in paths['roofFaces']and ratio[route[-1]]>.25 and lower[route[-1]]>=-.5
   for a,b in zip(route,route[1:]):
    edges=lambda f:{tuple(sorted([tuple(x),tuple(y)]))for x,y in zip(f,np.roll(f,-1,axis=0))};assert edges(tri[a])&edges(tri[b]);edgechecks+=1
  maxdelta=float(delta.max());rows.append(dict(mode=mode,sourceWorldSHA256=digest(tri.tobytes()),sourceFaces=len(tri),identicalXZProjection=True,maximumExactYDeviationM=maxdelta,maximumExactYDeviationFraction=str(F.from_float(maxdelta)),ordinaryContinuousClearanceLowerBoundM=float(lower[ordinary].min()),affectedWallFaces=sorted(affected),exactSharedPathEdgesChecked=edgechecks,wholeCoverageTransportedFromSameProjection=True,ordinaryGapBoundsTransferredByConvexBarycentricCorrespondence=True,installationApproved=False));print(rows[-1],flush=True)
 result=dict(uids=['landsd/81242:0'],sourceSHA256=g['sourceSHA256'],rows=rows,sourceGeometryChanges=0,newlyInstalled=0,installationApproved=False,qualification='All source faces, unchanged XZ projection, exact per-face binary Y displacement; every ordinary source point retains literal continuous clearance minus its convex-interpolation Y bound. Exact shared original edge paths separately replayed in each representation. One affected original wall retains its scoped role/contact review obligations. No universal GPU/camera or architecture acceptance; original raw contact flags and foreign/browser/publication checks remain.');save(doc/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('aquarium_four_stream_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-four-stream-source-projection-clearance-transport',refs,result)
if __name__=='__main__':main()

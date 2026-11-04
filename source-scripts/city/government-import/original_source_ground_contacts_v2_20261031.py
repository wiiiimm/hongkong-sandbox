"""Exact four-world contact with every saved drawn-ground facet.

Includes vertical and collapsed-XZ terrain facets; no height-field proxy or edit.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser()
 for key in ['batch','uid','runtime','attributes','lease']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch;out=BASE/a.batch;assert not out.exists();lease=read(Path(a.lease));assert reservations.owns(lease)and 'building:'+a.uid in lease['resources'];_,pins=authenticate(BASE/a.runtime);refs=[Path(__file__),BASE/a.runtime/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 row=next(r for r in take(BASE/a.runtime/'selection.json.gz')['rows']if r['uid']==a.uid);g=next(r for r in take(HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==g['sourceSHA256'];refs.append(asset)
 attrdoc=BASE/a.attributes
 _,apins=authenticate(attrdoc);refs.append(attrdoc/'result.json');ap=attrdoc/'attributes.json.gz';assert digest(ap.read_bytes())==apins[str(ap.relative_to(ROOT))];refs.append(ap);attributes=read(ap);assert attributes['startEndAllInputsVerified'];attr=next(r for r in attributes['rows']if r['uid']==a.uid);assert attr['sourceSHA256']==row['sourceSHA256']
 ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);worlds=dict(original=decode_original_world_triangles(asset.read_bytes()),literal=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]);rows=[]
 ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 assert np.array_equal(worlds['literal'],np.asarray(attr['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[ix])
 for mode,field in [('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[ix]
 cache={}
 for mode,tri in worlds.items():
  assert reservations.owns(lease);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));candidates=np.flatnonzero(np.all(ground.max(1)>=lo,axis=1)&np.all(ground.min(1)<=hi,axis=1));worldsha=digest(tri.astype('<f8').tobytes())
  assert len(tri)==row['triangles']
  if worldsha in cache:
   prior,measured=cache[worldsha];assert np.array_equal(tri,prior);proof=deepcopy(measured)
  else:
   proof=exact_finite_contacts(tri,list(range(len(tri))),ground,list(range(len(ground))));cache[worldsha]=(tri.copy(),deepcopy(proof))
  assert proof['allPairsExamined'] and proof['sourceFacesOmitted']==0
  positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
  result=dict(mode=mode,sourceFaces=len(tri),completeDrawnGroundFaces=len(ground),groundFacesIntersectingSourceBounds=len(candidates),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),completeGroundSHA256=digest(ground.tobytes()),finiteContacts=len(proof['contacts']),positiveFiniteSurfaceContacts=len(positive),sourceFacesOmitted=0,groundFacesOmitted=0)
  save(out/(mode+'.json.gz'),dict(**result,proof=proof));rows.append(result);print(result,flush=True)
 assert len(rows)==4 and {r['mode'] for r in rows}=={'original','literal','leftF32','balancedF32'}
 result=dict(uids=[a.uid],uid=a.uid,sourceSHA256=row['sourceSHA256'],rows=rows,sourceGeometryChanges=0,physicalSupportAccepted=False,installationApproved=False,qualification='Every original indexed source facet and every saved actual drawn-ground facet supplied to exact finite-contact test, including vertical terrain. All four represented source streams are explicitly bound. Only byte-identical complete arrays reuse contact measurements. No height-based exclusion, generated support, changed source/terrain, current-scene approval or root acceptance.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py']);module('original_source_ground_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-source-drawn-ground-finite-contacts',refs,result)
if __name__=='__main__':main()

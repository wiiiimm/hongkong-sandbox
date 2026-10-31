"""Complete exact original contact test for one existing selection/new recovery.

No source edit, inferred support, new join, tolerance change or acceptance.
"""
import argparse
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
 for key in ['batch','uid','selection','recovery','lease']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch;out=BASE/a.batch;assert not out.exists();lease=read(Path(a.lease));assert reservations.owns(lease);refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 first=next(r for r in take(a.selection,'selection.json.gz')['rows']if r['uid']==a.uid);second=take(a.recovery,'summary.json');assert second['recovered']and second['uid']!=a.uid
 assert {'building:'+u for u in [a.uid,second['uid']]}<=set(lease['resources'])
 assets=[ROOT/first['candidate']['path'],ROOT/second['sourceAsset']['path']];sources={a.uid:first['sourceSHA256'],second['uid']:second['sourceSHA256']};triangles=[]
 for uid,path,entry in zip(sources,assets,[first['candidate']['entry'],second['candidate']]):
  assert path.resolve().is_relative_to(ROOT.resolve())and digest(path.read_bytes())==sources[uid];refs.append(path);tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==entry['triangles'];bounds=np.array([tri.min(axis=(0,1)),tri.max(axis=(0,1))]);assert np.max(np.abs(bounds-np.asarray(entry['worldBounds'])))<1e-6;triangles.append(tri)
 proof=exact_finite_contacts(triangles[0],list(range(len(triangles[0]))),triangles[1],list(range(len(triangles[1]))));positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
 result=dict(uids=list(sources),sourceSHA256ByUid=sources,sourceWorldSHA256ByUid={u:digest(t.astype('<f8').tobytes())for u,t in zip(sources,triangles)},mode='original',completeFaceCounts={u:len(t)for u,t in zip(sources,triangles)},exactOriginalContactPairs=len(proof['contacts']),positiveFiniteSurfaceContacts=len(positive),sourceFacesOmitted=0,sourceGeometryChanges=0,physicalSupportAccepted=False,installationApproved=False,qualification='Every original indexed facet from both exact source packages supplied to the finite contact kernel at fixed source placement. Original contacts are diagnostic terminals only. No root, connected-component, four-world runtime, current-ground or installation approval.')
 save(out/'original.json.gz',dict(**result,proof=proof));save(out/'summary.json',result);assert reservations.owns(lease);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py']);module('nominated_original_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-new-nominated-original-pair-finite-contacts',refs,result);print({k:result[k]for k in ['completeFaceCounts','exactOriginalContactPairs','positiveFiniteSurfaceContacts']},flush=True)
if __name__=='__main__':main()

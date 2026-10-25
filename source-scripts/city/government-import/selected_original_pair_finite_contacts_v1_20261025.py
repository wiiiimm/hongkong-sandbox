"""Measure full exact contacts for an explicit pair of unchanged original candidates."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','attributes','left','right']:p.add_argument('--'+k,required=True)
 a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch and a.left!=a.right
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,'selection.json.gz');by={r['uid']:r for r in selection['rows']};attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']};worlds={};sources={}
 for uid in [a.left,a.right]:
  row=by[uid];attr=attrs[uid];asset=ROOT/row['candidate']['path'];sources[uid]=digest(asset.read_bytes());assert sources[uid]==row['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
  worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())};index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
  for name,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][name]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
  assert all(len(t)==row['triangles']for t in worlds[uid].values())
 rows=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  t=worlds[a.left][mode];u=worlds[a.right][mode];proof=exact_finite_contacts(t,range(len(t)),u,range(len(u)));assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0
  save(out/(mode+'.json.gz'),proof);summary=dict(mode=mode,sourceFaces=[len(t),len(u)],sourceWorldSHA256ByUid={a.left:digest(t.tobytes()),a.right:digest(u.tobytes())},finiteContactPairs=len(proof['contacts']),positiveSurfaceContactPairs=sum(c['dimension']>0 for c in proof['contacts']),areaContactPairs=sum(c['dimension']==2 for c in proof['contacts']),allPairsExamined=True,sourceFacesOmitted=0);rows.append(summary);print(summary,flush=True)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 result=dict(uids=[a.left,a.right],sourceSHA256ByUid=sources,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Every original indexed source face in four coordinate representations participates in the exact inclusive-AABB finite-pair scan. All raw contacts retained; no source editing, support/identity/collision approval or installation credit. Candidate-pair interpretation remains separate from current BASIC and installed-native context.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py']);module('selected_original_pair_finite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-explicit-original-candidate-pair-finite-contacts',refs,result)
if __name__=='__main__':main()

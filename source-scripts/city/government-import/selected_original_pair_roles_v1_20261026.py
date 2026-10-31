"""Classify exact candidate-pair contacts using each complete represented world."""
import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','contacts','attributes']:p.add_argument('--'+k,required=True)
 a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  path=base/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(a.contacts,'summary.json');uids=summary['uids'];assert len(uids)==2;selected={r['uid']:r for r in take(a.runtime,'selection.json.gz')['rows']};triangles={};hashes={};attrs=take(a.attributes,'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']}
 for uid in uids:
  r=selected[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==summary['sourceSHA256ByUid'][uid];refs.append(asset);attr=attrs[uid];assert attr['sourceSHA256']==r['sourceSHA256'];index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);triangles[uid]={'original':decode_original_world_triangles(asset.read_bytes())};triangles[uid].update({n:np.asarray(attr[f],dtype='<f8').reshape(-1,3)[index]for n,f in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
 assert len(summary['rows'])==4 and {m['mode']for m in summary['rows']}=={'original','literal','leftF32','balancedF32'}and all(m['sourceWorldSHA256ByUid']=={uid:digest(triangles[uid][m['mode']].astype('<f8').tobytes())for uid in uids}for m in summary['rows'])
 results=[]
 for mode in summary['rows']:
  proof=take(a.contacts,mode['mode']+'.json.gz');assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0 and len(proof['contacts'])==mode['finiteContactPairs'];classified=[]
  for c in proof['contacts']:
   points=[tuple(Fraction(z)for z in q)for q in c['exactPoints']];left=rational_face(triangles[uids[0]][mode['mode']][c['sourceFaceA']]);right=rational_face(triangles[uids[1]][mode['mode']][c['sourceFaceB']]);role=contact_role(left,right,points,c['dimension'],[c['sourcePrimitiveDimensionA'],c['sourcePrimitiveDimensionB']]);classified.append(dict(c,contactRole=role))
  save(out/(mode['mode']+'.json.gz'),classified);row=dict(mode=mode['mode'],contactCount=len(classified),roles=dict(Counter(c['contactRole']for c in classified)));results.append(row);print(row,flush=True)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[a.runtime][str(manifest.relative_to(ROOT))];refs.append(manifest)
 result=dict(uids=uids,sourceSHA256ByUid=summary['sourceSHA256ByUid'],rows=results,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact rational triangle/primitive classifications only. Each representation is independently reconstructed from authenticated complete position/index arrays and matched to its saved complete contact-stream hash. Raw contacts remain unchanged. Geometric role does not establish architectural intent, support or collision acceptance.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_contact_role_context_v1_20261023.py']);module('represented_original_pair_roles_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-contact-roles-for-independently-bound-four-world-original-pair',refs,result)
if __name__=='__main__':main()

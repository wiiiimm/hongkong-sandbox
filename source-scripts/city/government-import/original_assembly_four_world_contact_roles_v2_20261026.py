"""Classify nested complete assembly-pair diagnostics; no acceptance."""
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
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','runtime','attributes','contacts']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists();refs=[Path(__file__)];pins={}
 def take(name,path):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(a.runtime,base/a.runtime/'selection.json.gz');attrs=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']};summary=take(a.contacts,base/a.contacts/'summary.json');worlds={}
 for r in selection['rows']:
  uid=r['uid'];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==summary['sourceSHA256ByUid'][uid]==attrs[uid]['sourceSHA256'];refs.append(asset);attr=attrs[uid];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
  worlds[uid]=dict(original=decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(attr[field]).reshape(-1,3)[ix]for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
 assert set(worlds)==set(summary['uids']) and summary['pairCount']==len(summary['rows'])==len(worlds)*(len(worlds)-1)//2
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==summary['currentManifestSHA256'];refs.append(manifest)
 expanded=[]
 seen=set()
 for pair in summary['rows']:
  u,v=pair['left'],pair['right'];key=frozenset([u,v]);assert u!=v and key not in seen and key<=set(worlds);seen.add(key)
  assert {m['mode']for m in pair['modes']}=={'original','literal','leftF32','balancedF32'} and len(pair['modes'])==4
  for m in pair['modes']:
   mode=m['mode'];assert m['sourceFaces']==[len(worlds[u][mode]),len(worlds[v][mode])]
   assert m['sourceWorldSHA256ByUid']=={u:digest(worlds[u][mode].tobytes()),v:digest(worlds[v][mode].tobytes())}
   separated=m['method']=='strict-complete-bounds-separation';assert separated or m['method']=='complete-exact-finite-triangle-contacts'
   expanded.append(dict(uid=u,peerUid=v,mode=mode,strictBoundsSeparated=separated,axisGapsM=m.get('strictSeparatingAxisGapsM'),rawPath=str((base/a.contacts/(u.split('/')[1]+'--'+v.split('/')[1]+'--'+mode+'.json.gz')).relative_to(ROOT))))
 assert len(expanded)==len(worlds)*(len(worlds)-1)//2*4;results=[]
 for row in expanded:
  u,v,mode=row['uid'],row['peerUid'],row['mode'];left,right=worlds[u][mode],worlds[v][mode]
  if row['strictBoundsSeparated']:
   gaps=np.maximum(left.min((0,1))-right.max((0,1)),right.min((0,1))-left.max((0,1)));assert np.any(gaps>0)and gaps.tolist()==row['axisGapsM'];results.append(dict(uid=u,peerUid=v,mode=mode,strictBoundsSeparated=True,contactCount=0,roles={}));continue
  raw=take(a.contacts,ROOT/row['rawPath']);assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0;classified=[]
  for c in raw['contacts']:
   points=[tuple(Fraction(z)for z in p)for p in c['exactPoints']];fa=rational_face(left[c['sourceFaceA']]);fb=rational_face(right[c['sourceFaceB']]);role=contact_role(fa,fb,points,c['dimension'],[c['sourcePrimitiveDimensionA'],c['sourcePrimitiveDimensionB']]);classified.append(dict(c,contactRole=role))
  save(out/(u.split('/')[1]+'--'+v.split('/')[1]+'--'+mode+'.json.gz'),classified);results.append(dict(uid=u,peerUid=v,mode=mode,strictBoundsSeparated=False,contactCount=len(classified),roles=dict(Counter(c['contactRole']for c in classified))))
 assert digest(manifest.read_bytes())==selection['manifestSHA256']
 result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],rows=results,allRawContactsClassified=True,architectureReview=False,physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Every saved original surface/degenerate contact in every coordinate stream classified with the existing exact rational role helper. Strictly disjoint pairs rechecked. No collision, related ownership, load dependency, source-role or installation approval follows from geometric contact alone.')
 save(out/'summary.json',result);refs.extend([HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_contact_role_context_v1_20261023.py']);module('assembly_world_roles_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-original-assembly-four-world-contact-role-diagnostics',refs,result)
 print([dict(uid=r['uid'],peerUid=r['peerUid'],mode=r['mode'],roles=r['roles'])for r in results],flush=True)
if __name__=='__main__':main()

"""Finite facet paths for unresolved BASIC-support probes; no approval."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_four_world_contact_paths_v1_20261023 import paths
from pool_incident_wall_contacts_v1_20261017 import closest
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from source_closed_components import components


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','checks','uid','support']:p.add_argument('--'+key,required=True)
 a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.checks])
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();_,pins=authenticate(base/a.checks);refs=[Path(__file__),base/a.checks/'result.json']
 def take(name):
  path=base/a.checks/name;assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
 inputs=[r for r in take('mode-inputs.json.gz')['rows']if r['uid']==a.uid];assert len(inputs)==1 and inputs[0]['supportUid']==a.support
 source=inputs[0];checks=[r for r in take('mode-checks.json.gz')['rows']if r['uid']==a.uid];assert len(checks)==4 and {r['mode']for r in checks}=={m['mode']for m in source['modes']}
 support=source['supportGeometry'];podium=np.asarray(support['position'],dtype='<f8').reshape(-1,3)[np.asarray(support['index']).reshape(-1,3)]
 rows=[]
 for mode in source['modes']:
  g=mode['geometry'];t=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];check=next(r for r in checks if r['mode']==mode['mode']);assert check['sourceSHA256']==source['sourceSHA256']and check['uid']==a.uid and check['supportUid']==a.support
  lo,hi=t.min(1),t.max(1);targets=[]
  for witness in check['proof']['unresolved']:
   point=np.asarray(witness['position']);broad=np.flatnonzero(np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
   ids=[int(i)for i in broad if np.linalg.norm(np.cross(t[i,1]-t[i,0],t[i,2]-t[i,0]))>0 and np.linalg.norm(closest(point,t[i])-point)<=.001];assert ids
   targets.append(dict(witness=witness,incidentFaces=ids))
  topology=components(t);incident={i for r in targets for i in r['incidentFaces']};reached=sorted({i for c in topology['components']if incident.intersection(c['faceIndices'])for i in c['faceIndices']})
  proof=exact_finite_contacts(t,reached,podium,list(range(len(podium))))if reached else dict(contacts=[])
  rawproof=proof;roof=float(podium[:,:,1].max())
  def roof_contact(c):
   v=t[c['sourceFaceA']];w=podium[c['sourceFaceB']];n=np.cross(v[1]-v[0],v[2]-v[0])
   return c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 and n[1]==0 and v[:,1].min()<roof<v[:,1].max()and np.all(w[:,1]==roof)and c['bounds'][0][1]==c['bounds'][1][1]==roof
  proof=dict(contacts=[c for c in rawproof['contacts']if roof_contact(c)],contactsFilteredToMaximumRoof=True,rawFiniteContacts=len(rawproof['contacts']))
  verified=paths(t,dict(targets=targets,proof=proof))
  rises=[r['verifiedPath']['maximumPathHeightM']-r['witness']['position'][1]for r in verified if r['verifiedPath']is not None]
  result=dict(mode=mode['mode'],targets=len(targets),verifiedPaths=sum(r['verifiedPath']is not None for r in verified),remaining=sum(r['verifiedPath']is None for r in verified),maximumPathRiseM=max(rises,default=0),sourceFaces=len(t),supportFaces=len(podium),sourceWorldSHA256=digest(t.tobytes()),supportWorldSHA256=digest(podium.tobytes()),strictInterfacePassed=check['proof']['passed'],roofContactsOnly=True)
  save(out/(mode['mode']+'.json.gz'),dict(**result,rows=verified,exactContacts=proof,rawExactContacts=rawproof));rows.append(result);print(result,flush=True)
 result=dict(uids=[a.uid],supportUid=a.support,rows=rows,allUnresolvedHaveFinitePaths=all(r['remaining']==0 for r in rows),sourceGeometryChanges=0,physicalSupportAccepted=False,installationApproved=False,publication=False,qualification='Existing exact finite facet/shared-edge path algorithm applied ONLY to actual exposed vertical source-wall/flat maximum BASIC-roof contacts in four source worlds. All raw finite contacts are retained separately; no roof predicate is weakened. Existing1mm witness/path residual checks unchanged. Raw strict negatives remain. No geometry, tolerance, source identity, native contact, architectural support or publication approval.')
 save(out/'summary.json',result)
 refs.extend(HERE/n for n in ['original_four_world_contact_paths_v1_20261023.py','pool_incident_wall_contacts_v1_20261017.py','exact_original_finite_triangle_contacts_20261010.py','source_closed_components.py'])
 module('basic_finite_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'four-world-original-to-current-basic-finite-contact-path-diagnostics',refs,result)
if __name__=='__main__':main()

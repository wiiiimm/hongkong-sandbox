"""Find shared-original-edge routes to an authenticated installed support.

Diagnostic only: original endpoint-height failures remain unapproved.
"""
from pathlib import Path
import argparse
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_attachment_minimax_v2_20261024 import attachment_paths
from pool_incident_wall_contacts_v1_20261017 import closest

BASE=ROOT/'docs/astra-city/government-import'


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','runtime','attributes','strict-support','uid','support']:p.add_argument('--'+key,required=True)
 a=p.parse_args();BATCH=a.batch;RUNTIME=a.runtime;ATTRS=a.attributes
 assert all(n.startswith('government-xl-')and'/'not in n for n in [BATCH,RUNTIME,ATTRS,a.strict_support])
 assert a.uid!=a.support
 out=BASE/BATCH;assert not out.exists();out.mkdir();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=take(RUNTIME,'selection.json.gz');attributes=take(ATTRS,'attributes.json.gz');assert attributes['startEndAllInputsVerified'];worlds={};sources={}
 r=next(r for r in selection['rows']if r['uid']==a.uid);attr=next(r for r in attributes['rows']if r['uid']==a.uid)
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
 sources[a.uid]=r['sourceSHA256'];ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 worlds[a.uid]=dict(original=decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k],dtype='<f8').reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
 strict=take(a.strict_support,'summary.json')
 assert strict['supportedUid']==a.uid and strict['installedSupportUid']==a.support
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==strict['currentManifestSHA256'];refs.append(manifest)
 current=[]
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for entry in read(path)['models']:
   if entry['uid']==a.support:current.append((entry,path))
 assert len(current)==1
 entry,catalogue=current[0];nativeasset=catalogue.parent/entry['asset']
 assert entry==strict['installedNativeEntry'] and digest(nativeasset.read_bytes())==entry['sha256']
 refs.extend([catalogue,nativeasset]);sources[a.support]=entry['sha256'];worlds[a.support]={}
 assert sources==strict['sourceSHA256ByUid']
 for mode in worlds[a.uid]:
  inp=take(a.strict_support,mode+'/input.json.gz')
  child=inp['rows'][0];assert child['uid']==a.uid
  child_tri=np.asarray(child['position'],dtype='<f8').reshape(-1,3)[np.asarray(child['index']).reshape(-1,3)]
  assert np.array_equal(child_tri,worlds[a.uid][mode])
  podium=np.asarray(inp['podium'],dtype='<f8');assert podium.shape==(entry['triangles'],3,3)
  bound=next(row for row in strict['rows']if row['mode']==mode)
  assert digest(podium.tobytes())==bound['sourceWorldSHA256ByUid'][a.support]
  worlds[a.support][mode]=podium
 summary=[]
 for mode,tri in worlds[a.uid].items():
  strict_batch=a.strict_support
  strict=take(strict_batch,'summary.json');assert strict['supportedUid']==a.uid and strict['installedSupportUid']==a.support and strict['sourceSHA256ByUid']==sources
  old=next(r for r in strict['rows']if r['mode']==mode)
  assert old['sourceWorldSHA256ByUid'][a.uid]==digest(tri.tobytes()) and old['sourceWorldSHA256ByUid'][a.support]==digest(worlds[a.support][mode].tobytes())
  input_data=take(strict_batch,mode+'/input.json.gz');inputpath=BASE/strict_batch/mode/'input.json.gz'
  assert np.array_equal(np.asarray(input_data['rows'][0]['position'],dtype='<f8').reshape(-1,3)[np.asarray(input_data['rows'][0]['index']).reshape(-1,3)],tri)
  assert np.array_equal(np.asarray(input_data['podium']),worlds[a.support][mode])
  rootpath=out/(mode+'-strict-roots.json.gz');tool=HERE/'original_strict_support_roots_v1_20261024.mjs'
  subprocess.run(['node',str(tool),str(inputpath),str(rootpath)],cwd=ROOT,check=True)
  rootproof=read(rootpath);assert rootproof['inputSHA256']==digest(inputpath.read_bytes()) and rootproof['strict']==old['support']['strictLowRim']
  anchors=[];lo=tri.min(1);hi=tri.max(1);renderable=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)>0
  for root in rootproof['roots']:
   if not root['strictAccepted']:continue
   point=np.asarray(root['position']);candidate=np.flatnonzero(renderable & np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
   incident=[int(i)for i in candidate if np.linalg.norm(closest(point,tri[i])-point)<=.001];assert incident
   anchors.append(dict(**root,incidentFaces=incident))
  assert len(anchors)==old['support']['strictContacts']
  targets=[]
  for witness in old['support']['unresolved']:
   point=np.asarray(witness['position']);candidate=np.flatnonzero(renderable & np.all(lo<=point+.001,axis=1)&np.all(hi>=point-.001,axis=1))
   incident=[int(i)for i in candidate if np.linalg.norm(closest(point,tri[i])-point)<=.001];assert incident
   targets.append(dict(witness=witness,incidentFaces=incident))
  rows=attachment_paths(tri,dict(targets=targets,proof=dict(contacts=[])),[],strict_anchors=anchors)
  contact_tool=HERE/'support-contact.mjs';assert digest(contact_tool.read_bytes())==pins[strict_batch][str(contact_tool.relative_to(ROOT))]
  refs.extend([inputpath,tool,contact_tool])
  report=dict(mode=mode,sourceWorldSHA256=digest(tri.tobytes()),supportWorldSHA256=digest(worlds[a.support][mode].tobytes()),noIntercomponentJoins=True,rows=rows,canonicalStrictAnchorCount=len(anchors),canonicalStrictRoots=anchors,originalEndpointHeightGatePreserved=True,supportApproved=False)
  save(out/(mode+'.json.gz'),report)
  r=dict(mode=mode,targets=len(rows),finiteAttachmentPaths=sum(r['hasUnrestrictedFiniteAttachment']for r in rows),disconnected=sum(not r['hasUnrestrictedFiniteAttachment']for r in rows),aboveExistingEndpointCeiling=sum(r.get('riseAboveEndpointsM',0)>0 for r in rows),riseAboveEndpointRangeM=[min((r['riseAboveEndpointsM']for r in rows if r['hasUnrestrictedFiniteAttachment']),default=None),max((r['riseAboveEndpointsM']for r in rows if r['hasUnrestrictedFiniteAttachment']),default=None)],supportApproved=False)
  summary.append(r);print(r,flush=True)
 result=dict(uids=list(sources),sourceSHA256ByUid=sources,rows=summary,currentManifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,supportApproved=False,physicalAcceptance=False,qualification='Every remaining direct support warning receives a shared-original-edge attachment diagnostic in each freshly rebound coordinate stream. Canonical strict accepted rim anchors are independently reproduced against exact source/podium arrays with the unchanged[-.1,1]m interval. No intercomponent join or pseudo intersection is used. Every raw direct-interface failure remains recorded; current actual-ground, identity, role, neighbours, browser and publication checks remain independent. Paths above their endpoints explicitly fail the unchanged production support ceiling. This supplies component-role evidence, not support/architecture/installation approval; absent paths are not automatically source corruption.')
 save(out/'summary.json',result);refs.extend([HERE/'original_face_attachment_minimax_v2_20261024.py',HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'exact_packed_world_geometry_20261009.py'])
 module('canonical_strict_root_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-native-minimum-height-original-attachment-diagnostic',refs,result)

if __name__=='__main__':main()

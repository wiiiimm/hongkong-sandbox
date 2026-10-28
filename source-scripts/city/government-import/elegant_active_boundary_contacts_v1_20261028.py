"""Complete finite physical contacts for active original-group boundary actors."""
import argparse,sys,uuid,subprocess
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from exact_footing_prism_contacts_v1_20261028 import surface_contacts
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
RUNTIME=PREFIX+'sixteen-original-updated-runtime-v1-20261028';ATTRS=PREFIX+'sixteen-original-final-attributes-v1-20261028'
PAIRS=[('landsd/236170:0','landsd/236367:0'),('landsd/236170:0','landsd/173767:0'),('landsd/173764:0','landsd/224121:0')]
BASICS=[('landsd/236170:0','landsd/99061:0','main-canopy-final-sixteen-posts-v1-20261028'),('landsd/173532:0','landsd/213586:0','unnamed-basic-podium-footing-v1-20261028')]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out,local=BASE/a.batch,HERE/'local'/a.batch;assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);lp=local/'reservation.json'
 if not a.owned:
  assert not local.exists();claim=reservations.claim('active-original-boundary-contacts-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(RUNTIME,'selection.json.gz');sources={r['uid']:r for r in selection['rows']}
 attributes=take(ATTRS,'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attrs={r['uid']:r for r in attributes['rows']}
 boundary=take(PREFIX+'two-permit-boundary-allocation-v1-20261028','summary.json')
 assert {a['uid']for g in boundary['rows']for a in g['actors']}=={'landsd/99061:0','landsd/236367:0','landsd/173767:0','landsd/213586:0','landsd/215726:0','landsd/224121:0'}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 worlds={}
 for uid in sorted({u for pair in PAIRS for u in pair}|{r[0]for r in BASICS}):
  r=sources[uid];attr=attrs[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attr['sourceSHA256'];refs.append(asset)
  index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
  worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(attr[field]).reshape(-1,3)[index]
  assert all(len(t)==r['triangles']for t in worlds[uid].values())
 basic_inputs=[];live_hashes={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())}
 for original,uid,proposal_name in BASICS:
  b=take(PREFIX+proposal_name,'input.json')['building'];proposal=take(PREFIX+proposal_name,'proposal.json');tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');raw=next(r for r in read(tile)['buildings']if r['uid']==uid);assert raw==b and raw.get('foundationBase')is None;refs.append(tile);live_hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes())
  basic_inputs.append(dict(building=raw,foundationBase=proposal['foundationBase']))
 input_path=out/'basic-part-input.json';save(input_path,dict(rows=basic_inputs,inputHashes=live_hashes))
 tool=HERE/'basic_boundary_part_prisms_v1_20261028.mjs';refs.append(tool)
 subprocess.run(['node',str(tool),str(input_path.relative_to(ROOT)),str((out/'basic-parts.json').relative_to(ROOT))],cwd=ROOT,check=True)
 basics=read(out/'basic-parts.json');assert all(r[s]['fullProductionPositionParity']for r in basics['rows']for s in ['before','after'])
 rows=[]
 for left,right in PAIRS:
  for mode in ['original','literal','leftF32','balancedF32']:
   first,second=worlds[left][mode],worlds[right][mode];proof=exact_component_contacts_with_primitives(first,range(len(first)),second,range(len(second)));assert proof['allPairsExamined']
   name=left.split('/')[1]+'--'+right.split('/')[1]+'--'+mode+'.json.gz';save(out/name,proof)
   row=dict(sourceUid=left,otherUid=right,role='active-original-pair',mode=mode,completeSourceFaces=len(first),completeOtherFaces=len(second),sourceWorldSHA256=digest(first.astype('<f8').tobytes()),otherWorldSHA256=digest(second.astype('<f8').tobytes()),trianglePairsTested=proof['trianglePairsTested'],contacts=len(proof['contacts']),contactDimensions=dict(Counter(str(c['dimension'])for c in proof['contacts'])),proof=name)
   rows.append(row);print(row,flush=True)
 for original,uid,_ in BASICS:
  basic=next(r for r in basics['rows']if r['uid']==uid)
  for mode,tri in worlds[original].items():
   for state in ['before','after']:
    for part_index,part in enumerate(basic[state]['parts']):
     proof=surface_contacts(tri,np.asarray(part['caps']),part['bottom'],part['top']);assert proof['allForeignFacesExamined']and proof['sourceFacesOmitted']==0
     name=original.split('/')[1]+'--'+uid.split('/')[1]+'--'+mode+'--'+state+'--'+str(part_index)+'.json.gz';save(out/name,proof)
     row=dict(sourceUid=original,otherUid=uid,role='retained-basic-part-volume',mode=mode,state=state,partIndex=part_index,partKind=part['kind'],bottom=part['bottom'],top=part['top'],completeSourceFaces=len(tri),surfaceInClosedVolumeContacts=len(proof['contacts']),sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),proof=name,reverseSolidContainmentProved=False)
     rows.append(row);print({k:v for k,v in row.items()if k not in ['sourceWorldSHA256','proof']},flush=True)
 for path,sha in basics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 result=dict(uids=sorted(worlds),status='complete-active-boundary-interface-contacts',rows=rows,activeOriginalPairs=PAIRS,retainedBasicInterfaces=[[r[0],r[1]]for r in BASICS],inactiveOptionalOriginal='landsd/228592:0',inactiveOptionalQualification='Native Rex podium228592is private/uninstalled and is not part of the16actor fixture; retain its existing surveyed BASIC support. Its optional native projection contributions remain recorded in the permit allocation but are not actual activated-surface interfaces.',sourceGeometryChanges=0,physicalAccepted=False,identityAccepted=False,installationApproved=False,publication=False,qualification='Every primitive of each active original pair and every complete source surface against exact production-parity BASIC closed-part prisms, in all4coordinate streams. Before/after BASIC foundations are separate. Contact presence requires architectural/collision interpretation; absence is not reverse closed-solid containment. No overlap threshold, source face, source pose or production guard changed.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','exact_footing_prism_contacts_v1_20261028.py'])
 module('active_boundary_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-active-original-boundary-contacts-and-retained-basic-volumes',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()

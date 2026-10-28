"""Exhaustive original/original and mixed BASIC activation contacts; no acceptance."""
import argparse,sys,uuid,subprocess,itertools
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
MODES=['original','literal','leftF32','balancedF32']
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists()
 rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('activation-interference-matrix-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');sources={r['uid']:r for r in selection['rows']};assert len(sources)==16
 attrs={r['uid']:r for r in take(PREFIX+'sixteen-original-final-attributes-v1-20261028','attributes.json.gz')['rows']}
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 worlds={};basic_inputs={};hashes={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())}
 for uid,r in sources.items():
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==attrs[uid]['sourceSHA256'];refs.append(asset)
  index=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3);worlds[uid]={'original':decode_original_world_triangles(asset.read_bytes())}
  for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[uid][mode]=np.asarray(attrs[uid][field]).reshape(-1,3)[index]
  b=r['source']['building'];tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');raw=next(x for x in read(tile)['buildings']if x['uid']==uid);assert raw==b;refs.append(tile);hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());basic_inputs[uid]=dict(building=raw,foundationBase=raw.get('foundationBase',raw['base']))
 for name in ['main-canopy-final-sixteen-posts-v1-20261028','unnamed-basic-podium-footing-v1-20261028','grand-scholar-final-sixteen-posts-v1-20261028']:
  b=take(PREFIX+name,'input.json')['building'];proposal=take(PREFIX+name,'proposal.json');tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');raw=next(x for x in read(tile)['buildings']if x['uid']==b['uid']);assert raw==b;refs.append(tile);hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());basic_inputs[b['uid']]=dict(building=raw,foundationBase=proposal['foundationBase'])
 save(out/'basic-input.json',dict(rows=list(basic_inputs.values()),inputHashes=hashes));tool=HERE/'basic_boundary_part_prisms_v1_20261028.mjs';refs.append(tool)
 subprocess.run(['node',str(tool),str((out/'basic-input.json').relative_to(ROOT)),str((out/'basic-parts.json').relative_to(ROOT))],cwd=ROOT,check=True)
 basics={r['uid']:r for r in read(out/'basic-parts.json')['rows']};assert len(basics)==19
 rows=[]
 for left,right in itertools.combinations(sorted(sources),2):
  for mode in MODES:
   ta,tb=worlds[left][mode],worlds[right][mode];lo_a,hi_a=ta.min((0,1)),ta.max((0,1));lo_b,hi_b=tb.min((0,1)),tb.max((0,1));disjoint=bool(np.any(hi_a<lo_b)|np.any(hi_b<lo_a))
   row=dict(kind='original-original',sourceUid=left,otherUid=right,mode=mode,wholeBoundsSeparated=disjoint,sourceBounds=[lo_a.tolist(),hi_a.tolist()],otherBounds=[lo_b.tolist(),hi_b.tolist()],completeSourceFaces=len(ta),completeOtherFaces=len(tb))
   if not disjoint:
    proof=exact_component_contacts_with_primitives(ta,range(len(ta)),tb,range(len(tb)));assert proof['allPairsExamined'];name='native-'+left.split('/')[1]+'-'+right.split('/')[1]+'-'+mode+'.json.gz';save(out/name,proof);row.update(contacts=len(proof['contacts']),dimensions=dict(Counter(str(c['dimension'])for c in proof['contacts'])),proof=name)
   else:row['contacts']=0
   rows.append(row)
  print('native pair',left,right,[r['contacts']for r in rows[-4:]],flush=True)
 for uid in sorted(sources):
  for basic_uid,basic in basics.items():
   if uid==basic_uid:continue
   states=['after']if basic['before']['productionPositionSHA256']==basic['after']['productionPositionSHA256']else['before','after']
   for mode in MODES:
    tri=worlds[uid][mode]
    for state in states:
     contacts=0;proofs=[]
     for i,part in enumerate(basic[state]['parts']):
      proof=surface_contacts(tri,np.asarray(part['caps']),part['bottom'],part['top']);assert proof['allForeignFacesExamined']and proof['sourceFacesOmitted']==0
      contacts+=len(proof['contacts'])
      if proof['contacts']:
       name='mixed-'+uid.split('/')[1]+'-'+basic_uid.split('/')[1]+'-'+mode+'-'+state+'-'+str(i)+'.json.gz';save(out/name,proof);proofs.append(dict(partIndex=i,kind=part['kind'],proof=name,contacts=len(proof['contacts'])))
     rows.append(dict(kind='original-basic',sourceUid=uid,otherUid=basic_uid,mode=mode,state=state,unchangedStatesAliased=states==['after'],contacts=contacts,parts=len(basic[state]['parts']),completeSourceFaces=len(tri),contactProofs=proofs,allSourceFacesAndPartsExamined=True,reverseSolidContainmentProved=False))
   print('mixed pair',uid,basic_uid,'contacts',sum(r['contacts']for r in rows[-4*len(states):]),flush=True)
 assert sum(r['kind']=='original-original'for r in rows)==480
 for path,sha in read(out/'basic-parts.json')['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 save(out/'rows.json.gz',rows)
 positive_native=sorted({(r['sourceUid'],r['otherUid'])for r in rows if r['kind']=='original-original'and r['contacts']})
 positive_mixed=sorted({(r['sourceUid'],r['otherUid'])for r in rows if r['kind']=='original-basic'and r['contacts']})
 result=dict(uids=sorted(sources),completeOriginalPairs=120,coordinateStreams=4,completeBasicActors=19,completeMixedPairs=288,positiveOriginalPairs=positive_native,positiveMixedPairs=positive_mixed,rows=len(rows),sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,publication=False,qualification='Every original pair in all four coordinate streams; strict whole-bounds separation or exact primitive contacts. Every foreign target BASIC and all three retained BASIC foundation actors use complete production-parity closed part prisms. Same before/after geometry aliases explicitly. Contacts nominate activation dependencies/interface reviews; neither containment clearance nor role acceptance follows automatically.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_primitive_contacts_v1.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','exact_footing_prism_contacts_v1_20261028.py'])
 module('activation_matrix_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-sixteen-original-native-and-mixed-basic-activation-contact-matrix',list(dict.fromkeys(refs)),read(out/'summary.json'))
if __name__=='__main__':main()

"""Complete original source footing queries, not current-scene support approval."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-five-recovered-cases-original-rim-contacts-v2-20261028';PRIOR='government-xl-nine-original-recovery-contact-followthrough-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';JS=HERE/'original_neighbour_rim_contacts_v1_20261028.mjs'
def cases():
 authenticate(BASE/PRIOR);d=read(BASE/PRIOR/'summary.json');assert len(d['completed'])==5 and not d['unresolved'];rows=[]
 for item in d['completed']:
  receipt=ROOT/item['receipt'];r,pins=authenticate(receipt.parent);path=receipt.parent/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];row=read(path);assert row['allNominatedOriginalsTested']and not row['missingCachedSources'];rows.append((receipt,row,r))
 return rows

def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();rows=cases();refs=[Path(__file__),JS,BASE/PRIOR/'result.json',HERE/'exact_packed_world_geometry_20261009.py'];inputs=[];scopes=[]
 def decode(receipt,sha,expected):
  matches=[ROOT/r['path']for r in receipt['evidenceRefs']if r['sha256']==sha and r['path'].endswith('.glb.gz')];assert matches;path=next(p for p in matches if p.exists());assert digest(path.read_bytes())==sha;tri=decode_original_world_triangles(path.read_bytes());assert np.isfinite(tri).all()and len(tri)==expected;refs.append(path);return tri
 for path,row,receipt in rows:
  uid=row['targetUid'];assert 'building:'+uid in lease['resources'];refs.append(path);source=decode(receipt,row['sourceSHA256'],row['rows'][0]['sourceFaces']);supports=[];scope=[];offset=0
  for item in row['rows']:
   peer=item['peer'];assert 'building:'+peer['uid']in lease['resources'];tri=decode(receipt,peer['indexedSourceSHA256'],item['peerFaces']);supports.append(tri);scope.append(dict(uid=peer['uid'],sourceKey=peer['sourceKey'],sourceSHA256=peer['indexedSourceSHA256'],originalWorldSHA256=digest(tri.astype('<f8').tobytes()),faceRange=[offset,offset+len(tri)]));offset+=len(tri)
  support=np.concatenate(supports);geometry=lambda t:dict(position=t.reshape(-1).tolist(),index=list(range(t.size//3)));inputs.append(dict(uid=uid,mode='original',source=geometry(source),support=geometry(support),sourceMinimumY=float(source[:,:,1].min()),sourceWorldSHA256=digest(source.astype('<f8').tobytes()),supportWorldSHA256=digest(support.astype('<f8').tobytes())));scopes.append(dict(uid=uid,sourceFaces=len(source),supportFaces=len(support),originalSupportMembers=scope))
 save(DOC/'input.json.gz',dict(rows=inputs));proc=subprocess.run(['node',str(JS),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'contacts.json.gz').relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True);save(DOC/'command.json',dict(exitCode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr));assert proc.returncode==0;report=read(DOC/'contacts.json.gz');assert len(report['rows'])==5
 for path,sha in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 summary=[{k:v for k,v in r.items()if k not in ['rawInterface','mapped']}for r in report['rows']];result=dict(uids=[r['uid']for r in inputs],mode='original',rows=summary,completeOriginalSourceScopes=scopes,sourceGeometryChanges=0,terrainIncluded=False,currentSceneSupportAccepted=False,physicalAccepted=False,qualification='Existing canonical low-rim/interface kernel and finite original-face queries applied to every target original and every nominated original neighbour. Supports concatenate complete facet sets for queries only: no new facets, welding, GLB edit, root assignment or rendering change. No terrain/current-region, four-world, identity, semantic support or installation acceptance; zero contacts alone is not a terrain-root rejection.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('five_case_original_rim_query_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-recovered-cases-canonical-original-rim-queries',refs,result);print(summary,flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();resources=set()
 for _,row,_ in cases():resources.update('building:'+u for u in[row['targetUid'],*[r['peer']['uid']for r in row['rows']]])
 c=reservations.claim('five-case-original-rim-query-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()

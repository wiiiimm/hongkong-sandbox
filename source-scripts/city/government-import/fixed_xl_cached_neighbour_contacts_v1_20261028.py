"""Complete finite contacts for cached originals nominated by the territorial scan.

Missing cache assets stay explicit; no acquisition, physical approval or scene edit.
"""
import argparse,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';INVENTORY='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028'
def main():
 p=argparse.ArgumentParser()
 for k in ['batch','uid','lease']:p.add_argument('--'+k,required=True)
 a=p.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch;out=BASE/a.batch;assert not out.exists();lease=read(Path(a.lease));assert reservations.owns(lease)
 _,pins=authenticate(BASE/INVENTORY);path=BASE/INVENTORY/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];row=next(r for r in read(path)['rows']if r['uid']==a.uid);peers=row['nearbyOriginalCandidates'];assert {'building:'+u for u in [a.uid,*[r['uid']for r in peers if r['uid']]]}<=set(lease['resources']);refs=[Path(__file__),BASE/INVENTORY/'result.json',path];decoded={};missing=[]
 for r in [row,*peers]:
  key,mid=r['sourceKey'].split('/',1)
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert record[0]==r['nativeResultSHA256'];m=next(m for m in record[1]['models']if m['modelId']==mid);assert(m.get('candidate')or m['asset'])['sha256']==r['indexedSourceSHA256']
  found=subprocess.run(['rg','--files','--hidden','--no-ignore','-g',r['indexedSourceSHA256']+'.glb.gz',str(HERE/'local'),str(ROOT/'3d-viewer/city/data/official-models')],capture_output=True,text=True);assert found.returncode in[0,1];candidates=[Path(s)for s in found.stdout.splitlines()];asset=next((p for p in candidates if digest(p.read_bytes())==r['indexedSourceSHA256']),None)
  if asset is None:missing.append(dict(sourceKey=r['sourceKey'],uid=r['uid'],sha256=r['indexedSourceSHA256']));continue
  tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==m['triangles'];assert np.max(np.abs(np.array([tri.min(axis=(0,1)),tri.max(axis=(0,1))])-np.asarray(m['worldBounds'])))<1e-6;decoded[r['sourceKey']]=tri;refs.append(asset)
 assert row['sourceKey']in decoded;source=decoded[row['sourceKey']];results=[]
 for peer in peers:
  if peer['sourceKey']not in decoded:continue
  other=decoded[peer['sourceKey']];proof=exact_finite_contacts(source,list(range(len(source))),other,list(range(len(other))));positive=[c for c in proof['contacts']if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
  index=len(results);save(out/('peer-'+str(index)+'.json.gz'),dict(peer=peer,proof=proof));results.append(dict(peer=peer,sourceFaces=len(source),peerFaces=len(other),finiteContacts=len(proof['contacts']),positiveSurfaceContacts=len(positive),sourceContactFaces=sorted({c['faceA']for c in proof['contacts']})if proof['contacts']and'faceA'in proof['contacts'][0]else None))
 result=dict(uids=sorted({u for u in[a.uid,*[r['uid']for r in peers]]if u}),targetUid=a.uid,targetSourceKey=row['sourceKey'],sourceSHA256=row['indexedSourceSHA256'],rows=results,missingCachedSources=missing,allNominatedOriginalsTested=not missing,sourceGeometryChanges=0,sourceFacesOmitted=0,physicalSupportAccepted=False,qualification='Every facet of each cached exact original supplied at fixed source placement. No support path, ground root, identity, runtime, terrain, burial or installation acceptance. Missing assets and unknown-bound units remain unresolved.')
 save(out/'summary.json',result);assert reservations.owns(lease);module('cached_nominated_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-cached-nominated-original-finite-contacts',refs,result);print(dict(target=a.uid,tested=len(results),missing=len(missing),contacts=[r['finiteContacts']for r in results]),flush=True)
if __name__=='__main__':main()

"""Bind existing ground+podium support checks; no threshold or geometry change."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-combined-ground-interfaces-v1-20261017';DOC=BASE/BATCH;WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-companion-original-patch-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [WORLD,GROUND]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 paths=[WORLD/'world-triangles.json.gz',GROUND/'drawn-patch.json.gz']
 for p in paths:assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p)
 claim=reservations.claim('opus-combined-interface-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();tool=HERE/'opus_combined_ground_interfaces_v1_20261017.mjs';out=DOC/'interfaces.json.gz'
  subprocess.run(['node',str(tool),*[str(p.relative_to(ROOT)) for p in paths],str(out.relative_to(ROOT))],cwd=ROOT,check=True,timeout=600)
  data=read(out);refs += [tool,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs']
  for p,h in {**data['inputHashes'],**data['closure']['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  summary=[dict(mode=r['mode'],uid=r['uid'],samples=r['proof']['samples'],strict=r['proof']['strictContacts'],walls=r['proof']['wallIntersections'],unresolved=len(r['proof']['unresolved']),missing=sum(x.get('gap') is None for x in r['proof']['unresolved'])) for r in data['rows']];save(DOC/'summary.json',dict(rows=summary,fullAcceptance=False))
  result=module('opus_combined_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-ground-plus-podium-canonical-support-v1',refs,dict(uids=['landsd/322573:0','landsd/319559:0','landsd/248432:0'],rows=summary,fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

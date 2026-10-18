"""All-mode lower contact and finite-original-face path diagnostics."""
from pathlib import Path
from fractions import Fraction as F
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-lower-contacts-v1-20261018';DOC=BASE/BATCH
CAP=BASE/'government-xl-park-avenue239350-six-four-world-v1-20261018';CHECK=BASE/'government-xl-park-avenue239350-six-foundations-contacts-v1-20261018'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,CHECK]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 worlds=read(CAP/'world-triangles.json.gz');paths=[]
 inputs=dict(worlds=worlds,paths=paths,targetUIDs=['landsd/80093:0','landsd/81847:0','landsd/82015:0'],supportUIDs=['landsd/239350:0','landsd/240161:0','landsd/227455:0']);save(DOC/'inputs.json.gz',inputs);tool=HERE/'olympian_two_park_four_world_contacts_v1_20261018.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True)
 rows=read(DOC/'contacts.json.gz')['rows'];checks=[]
 for r in rows:
  for d in r['details']:
   if d['contacts']:continue
   assert d['path']and d['path']['endpointPassed'];w=d['path']['original']['witness'];assert len(w['faces'])==1
   face=worlds[r['mode']][r['uid']][w['faces'][0]];distances=[squared_distance(p,face)for p in [d['position'],w['contact']['point']]];passed=all(x<=F(.001)**2 for x in distances);assert passed
   checks.append(dict(uid=r['uid'],mode=r['mode'],position=d['position'],originalFace=w['faces'][0],endpointSquaredDistances=[str(x)for x in distances],passed=passed))
 assert len(checks)==0 and len(rows)==12 and all(d['contacts'] for r in rows for d in r['details'])
 summary=dict(uids=inputs['targetUIDs'],coordinateChecks=len(rows),lowerContactChecks=sum(bool(d['contacts'])for r in rows for d in r['details']),finiteFacePathChecks=len(checks),allDiagnosticContactsResolved=True,fullAcceptance=False,newlyInstalled=0,qualification='Existing gap and 1 mm finite-face membership limits. Both path endpoints lie on the same finite convex original face within tolerance. Source-specific architectural interpretation and final terrain/browser/publication remain required; no generic support override.')
 save(DOC/'path-checks.json',dict(rows=checks));save(DOC/'summary.json',summary)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend([tool,HERE/'support-interface.mjs',HERE/'support-contact.mjs',HERE/'exact_point_triangle_distance_20261018.py']);out=module('park_contacts_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-finite-lower-source-contacts-four-worlds-v1',list(set(refs)),summary);print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()

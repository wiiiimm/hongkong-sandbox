"""Exact original lower-face interface review and provider closure; no publication."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-park-avenue239350-interface-review-v1-20261018';DOC=BASE/BATCH
PREFIX='government-xl-park-avenue239350-'
def folder(n):return BASE/(PREFIX+n+'-20261018')
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 names=['lower-contacts-v1','interface-views-v1','six-nearest-interfaces-v1','six-foundations-contacts-v1','base-neighbour-identity-runtime-v1']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for name in names:
   path=folder(name)/'result.json';r=read(path);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(path)
   for e in r['evidenceRefs']:
    assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 contact=folder('lower-contacts-v1');summary=read(contact/'summary.json');rows=read(contact/'contacts.json.gz')['rows'];assert len(rows)==12 and summary['lowerContactChecks']==236 and summary['finiteFacePathChecks']==0
 for row in rows:
  assert row['proof']['wallIntersections']==0
  for d in row['details']:
   assert d['reason']=='support-above-rim' and d['path'] is None
   assert any(hit['supportUid']=='landsd/227455:0' for hit in d['contacts'])
 foundations=read(folder('six-foundations-contacts-v1')/'summary.json');assert foundations['allModesPassed'] and len(foundations['rows'])==24
 nearest=read(folder('six-nearest-interfaces-v1')/'nearest-surfaces.json.gz')['rows'];assert len(nearest)==12 and all(r['failedSamples']==r['exactSurfaceContacts'] and r['maximumDistanceM']<.000001 for r in nearest)
 bindings=[]
 for uid in summary['uids']:
  proof=read(folder('base-neighbour-identity-runtime-v1')/(uid.split('/')[1]+'-identity.json'))['proof'];assert proof['passed'];bindings.append({k:proof[k] for k in ['uid','sourceSHA256','sourceFormSHA256','worldTrianglesSHA256']})
 review=dict(uids=summary['uids'],bindings=bindings,sourceSpecificInterfaceInterpretationAccepted=True,rawCanonicalFailuresRetained=True,reviewBasis=['ROOT inspected all three original plan/oblique lower-assembly views. Flagged lower perimeter points align with the original stepped and raised podium features. Finite lower original surfaces contact the towers below the highest surface selected by the generic check.', 'All 59 flagged points have finite lower-face contacts on unchanged source227455 in each of four coordinate modes (236 checks), using unchanged contact limits. Every flagged point is within 0.000001m of an original support triangle. No graph paths or inferred structural members are used.', 'All 24 full-face foundation checks pass with complete terrain/support coverage and no wholly buried faces; canonical checks report no wall intersections.', 'This accepts only these exact source interfaces. It is not a generic support waiver or engineering certification. Browser, neighbour and publication acceptance remain separate.'],modelGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceInterpretationUsedAI=True,fullAcceptance=False,publicationApproved=False)
 save(DOC/'ROOT-INTERFACE-REVIEW.json',review)
 inputs=read(contact/'inputs.json.gz');save(DOC/'inputs.json.gz',dict(worlds=inputs['worlds'],targets=inputs['targetUIDs'],towerPaths=[],parkContacts=rows))
 tool=HERE/'park_avenue239350_support_dependencies_v1_20261018.mjs';subprocess.run(['node',str(tool),str(DOC)],cwd=ROOT,check=True)
 providers=read(DOC/'provider-checks.json.gz');assert len(providers['rows'])==12 and providers['dependencies']=={uid:['landsd/227455:0'] for uid in summary['uids']}
 save(DOC/'dependencies.json',dict(dependencies=providers['dependencies'],qualification='All original low-rim samples covered in all four modes by unchanged source227455; source-specific lower-face review recorded separately.'))
 refs.extend([tool,HERE/'support-contact.mjs',*[ROOT/p for p in pins]])
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 out=module('park_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-exact-original-interface-and-provider-review-v1',list(set(refs)),dict(**review,dependencies=providers['dependencies']));print(out['jobId'],flush=True)
if __name__=='__main__':main()

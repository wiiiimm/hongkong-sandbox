"""Apply the existing unchanged_support proof to a frozen current neighbour report.

No thresholds or raw reports change. The report is scoped evidence, not a
publisher, source review or approval to change a retained tower or podium.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from unchanged_support import unchanged_supports

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for k in ['batch','neighbours']:ap.add_argument('--'+k,required=True)
 a=ap.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.neighbours])
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();r,pins=authenticate(base/a.neighbours);refs=[Path(__file__),base/a.neighbours/'result.json',HERE/'unchanged_support.py']
 for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
 def take(name):
  p=base/a.neighbours/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 inputs=take('neighbour-inputs.json.gz');checks=take('neighbour-checks.json');assert set(inputs['candidateIds'])==set(r['uids'])
 assert {x['building']['uid']for x in inputs['rows']}=={x['uid']for x in checks['rows']}
 proofs=unchanged_supports(inputs,checks,inputs['candidateIds']);assert len({p['uid']for p in proofs})==len(proofs)
 rows={x['uid']:x for x in checks['rows']};forms={x['building']['uid']:x['building']for x in inputs['rows']}
 for p in proofs:
  assert rows[p['uid']]['reasons']==['increased-neighbour-ground-gap']and not rows[p['supportUid']]['reasons']
  assert p['footprintCoverage']>=.9999 and abs(p['unchangedVerticalGap'])<=.1 and p['horizontalToleranceMetres']==.002
  p['ownerForm']=forms[p['uid']];p['supportForm']=forms[p['supportUid']]
 resolved={p['uid']for p in proofs};raw=r['basicFlags'];remaining=[p for p in raw if p['uid']not in resolved]
 assert all(next(p for p in raw if p['uid']==uid)['reasons']==['increased-neighbour-ground-gap']for uid in resolved)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==checks['inputHashes'][str(manifest.relative_to(ROOT))];refs.append(manifest)
 result=dict(uids=r['uids'],proofs=proofs,rawBasicFlagsPreserved=raw,remainingBasicFlags=remaining,allBasicFlagsResolved=not remaining,retainedNativeRows=r['nativeRows'],retainedNativeResolved=r['nativeResolved'],allRetainedNativeChecksPassed=all(x['passed']for x in r['nativeRows']),sourceGeometryChanges=0,sourcePoseChanges=0,currentManifestSHA256=digest(manifest.read_bytes()),installationApproved=False,physicalAccepted=False,publication=False,qualification='Only the existing unchanged_supports rule is applied: a unique unchanged solid BASIC podium, unchanged matching roof/base within0.1m, full footprint containment within2mm and>=99.99percent exact overlap, and no terrain warning on the support. Existing raised-ground-gap flags remain verbatim; all other flags stay unresolved. Both exact current owner/support forms are bound for subsequent publication checks. No geometry or approval flag changes.')
 save(out/'summary.json',result);module('unchanged_basic_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'existing-unchanged-basic-support-rule-current-bound-resolution',refs,result)
if __name__=='__main__':main()

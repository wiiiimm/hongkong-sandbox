"""Complete current installed-support interface and foundation; no role-label holds."""
from pathlib import Path
import numpy as np,uuid
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from installed_support_acceptance import compound_foundation,resolve_contact
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-current-support-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CAP=BASE/'government-xl-langham-current-pair-v1-20261017';RT=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();receipt=read(CAP/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/79318:0','building:landsd/224399:0'],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  rows=read(CAP/'selection.json.gz')['rows'];row=next(r for r in rows if r['uid']=='landsd/79318:0');support=next(r for r in rows if r['uid']=='landsd/224399:0');save(DOC/'support-inputs.json',dict(pairs=[dict(uid=row['uid'],supportUid=support['uid'])],sources=rows))
  rt=read(RT);g=next(r for r in rt['rows']if r['uid']==row['uid']);assert g['sourceSHA256']==row['sourceSHA256'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert len(t)==18086;b=row['source']['building']
  foundation,proof=compound_foundation(DOC,LOCAL,row,t,ground,Polygon(b['rings'][0],b['rings'][1:]),DOC)
  save(DOC/'foundation.json',foundation);raw=['ground-contact-unresolved','sampled-ground-gap-below-model-bottom'];remaining=resolve_contact(raw,proof['interface'],proof['foundation'])
  if not proof['foundation']['strictFoundationAccepted']:remaining.append('whole-source-foundation')
  save(DOC/'resolution.json',dict(rawContactReasons=raw,remainingReasons=remaining,wholeSourceFaces=len(t),uninterpretedComponentLabelsAreIndependentHolds=False,fullAcceptance=False,installationApproved=False))
  refs=[Path(__file__),CAP/'result.json',CAP/'selection.json.gz',RT,HERE/'installed_support_acceptance.py',HERE/'xl-final-script-pass.py']
  for p,h in {**rt['inputHashes'],**proof['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  assert reservations.owns(lease)
  out=module('langham_current_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-complete-langham-installed-support-physical-v1',refs,dict(uids=[row['uid']],supportUid=support['uid'],interface=proof['interface'],strictFoundationAccepted=proof['foundation']['strictFoundationAccepted'],remainingReasons=remaining,fullAcceptance=False,nextStep='Proceed to complete current identity/neighbour/runtime checks if physical checks pass; otherwise investigate exact current contact/foundation failures, not unqualified component labels.'))
  print(dict(jobId=out['jobId'],interface=proof['interface'],remaining=remaining),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

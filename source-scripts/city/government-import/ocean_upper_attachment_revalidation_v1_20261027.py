"""Rebind exact source-only attachment paths to fresh complete support witnesses."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-after-waterfront-ocean-'

def validate_binding(old,new,attachment,contacts):
 assert old['supportedUid']==new['supportedUid']==attachment['targetUid']
 assert old['supportUid']==new['supportUid']and old['supportUid']!=old['supportedUid']
 assert old['sourceSHA256ByUid']==new['sourceSHA256ByUid']==attachment['sourceSHA256ByUid']==contacts['sourceSHA256ByUid']
 modes={'original','literal','leftF32','balancedF32'}
 for data in [old,new,attachment,contacts]:assert len(data['rows'])==4 and {r['mode']for r in data['rows']}==modes
 for before in old['rows']:
  after=next(r for r in new['rows']if r['mode']==before['mode']);paths=next(r for r in attachment['rows']if r['mode']==before['mode']);pair=next(r for r in contacts['rows']if r['mode']==before['mode'])
  # Compare every witness position/classification/root field, never counts alone.
  assert before['support']==after['support']
  assert before['sourceWorldSHA256ByUid']==after['sourceWorldSHA256ByUid']==pair['sourceWorldSHA256ByUid']
  count=len(after['support']['unresolved'])
  assert paths['disconnected']==0 and paths['witnesses']==paths['finiteAttachmentPaths']==paths['pathsWithinEndpointHeight']==count
 return True

def main():
 base=ROOT/'docs/astra-city/government-import';batch=P+'four-corrected-upper-attachment-revalidation-v1-20261027';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(name):
  pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json');path=base/name/'summary.json';assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 old=take(P+'pair-support-v1-20261027');new=take(P+'four-corrected-upper-support-v1-20261027');attachment=take(P+'pair-rim-attachment-v1-20261027');contacts=take(P+'pair-contacts-v1-20261027');assert validate_binding(old,new,attachment,contacts)
 assert new['supportedUid']=='landsd/156599:0'and new['supportUid']=='landsd/234188:0'
 assert not new['allFourModesPassed']and not attachment['companionRootsApproved']and not attachment['physicalAcceptance']
 for bound in pins.values():
  for path,sha in bound.items():assert digest((ROOT/path).read_bytes())==sha
 result=dict(uids=new['uids'],targetUid=new['supportedUid'],supportUid=new['supportUid'],sourceSHA256ByUid=new['sourceSHA256ByUid'],sourceOnlyAttachmentEvidenceRevalidated=True,completeFreshSupportWitnessesExactlyEqual=True,completeSourceWorldHashesExactlyEqual=True,rows=attachment['rows'],rawStrictSupportPassed=False,physicalAcceptance=False,companionRootsApproved=False,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='All four fresh complete strict-support proof dictionaries, including every unresolved witness position, classification and root, equal the authenticated prior proofs exactly. Both complete indexed source-world hashes equal every saved contact-stream binding. Prior 608 positive finite source attachment paths per world therefore apply to these exact current witnesses with their unchanged endpoint-height ceiling and 1mm incidence rules. This revalidates source topology only; no old terrain acceptance, root approval, architectural role, physical or browser decision transfers.')
 save(out/'summary.json',result);module('ocean_upper_attachment_revalidation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-source-attachment-revalidation-on-complete-fresh-support-witnesses',list(dict.fromkeys(refs)),result)
 print(dict(sourceAttachmentRevalidated=True,physicalAcceptance=False),flush=True)
if __name__=='__main__':main()

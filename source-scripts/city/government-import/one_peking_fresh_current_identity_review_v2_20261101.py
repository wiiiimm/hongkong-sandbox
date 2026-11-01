"""Run the bounded current identity adapter only; no model/physical acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from one_peking_fresh_current_identity_v2_20261101 import verify_files
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-one-peking-after-twin-';BATCH=P+'fresh-current-named-identity-v2-20261101'
def main():
 out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();b=P+'runtime-v1-20261101';r,p=authenticate(BASE/b);sp=BASE/b/'selection.json.gz';assert digest(sp.read_bytes())==p[str(sp.relative_to(ROOT))];selection=read(sp);refs=[Path(__file__),BASE/b/'result.json',sp];results=[]
 for row in selection['rows']:
  cp=BASE/(P+'identity-v1-20261101')/row['uid'].split('/')[1]/'context.json';proof=verify_files(row,read(cp),local/row['uid'].split('/')[1]);assert proof['passed'];save(out/(row['uid'].split('/')[1]+'-identity.json'),proof);results.append(proof);refs.extend(ROOT/r['path']for r in proof['currentBinding']['evidenceRefs'])
 result=dict(uids=[r['uid']for r in selection['rows']],currentManifestSHA256=selection['manifestSHA256'],identityAccepted=True,rawCachedIdentityFlagsPreserved=True,rawSourceNegativeReasonsPreserved=True,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in selection['rows']},physicalAcceptance=False,collisionExemption=False,installationApproved=False,publication=False,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Fresh exact-source/current-native/provider identity only. Two named current foreign basic-proxy reasons replaced by complete already-installed foreign source silhouette under unchanged1m2limit across32coordinate/target combinations. No physical/contact/support/browser/publication exemption.')
 save(out/'summary.json',result);refs.extend([HERE/'one_peking_fresh_current_identity_v2_20261101.py',HERE/'one_peking_fresh_finite_silhouette_identity_v1_20261101.py']);module('one_peking_named_fresh_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-current-source-and-installed-foreign-identity-only-positive-bound-adapter',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()

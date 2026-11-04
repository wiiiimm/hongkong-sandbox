"""Freeze exact190 source ledger; no new identity/physical/publication credit."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read
BATCH='government-xl-identity-190-actionable-ledger-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
    x=read(DOC/'ledger.json.gz');s=importlib.util.spec_from_file_location('identity190_ledger_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    paths=[Path(__file__),HERE/'xl-identity-190-actionable-ledger-20261010.py']
    m.freeze(BATCH,'fixed190-exact-source-actionable-evidence-ledger-v1',paths,{'uids':sorted({r['uid'] for r in x['rows'] if r['uid']}),'sourceKeys':[r['sourceKey'] for r in x['rows']],'counts':x['counts'],'rows':x['rows'],'shortlist':x['shortlist'],'ledgerManifestSHA256':x['manifestSHA256'],'identityAccepted':False,'physicalAccepted':False,'newAcceptance':False,'queueCreated':False,'sourceIdentityReviewUsedAI':True,'remainingReason':'172deeper-component-investigations-plus-explicit-physical-and-provider-lineage-held-cases','qualification':x['qualification']})
    Path('/tmp/xl-identity-190-ledger-closed-scope-20261010.json').write_text(json.dumps([str(DOC.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT)),str((HERE/'xl-identity-190-actionable-ledger-20261010.py').relative_to(ROOT))],indent=2)+'\n')
if __name__=='__main__':main()

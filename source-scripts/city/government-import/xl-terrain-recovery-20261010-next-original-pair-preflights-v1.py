"""Bind exact distinct original source pair candidates, no identity/support credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';INPUTS=[BASE/'government-xl-terrain-recovery-next-four-original-source-recovery-v1-20261010/selection.json.gz',BASE/'government-xl-terrain-recovery-next-three-original-podium-recovery-v1-20261010/selection.json.gz'];PAIRS={'park-haven':[320705,246467],'unnamed-268032':[268032,101781],'beverly-hill-f':[256334,233218]}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 sha=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes());r={q['uid']:q for p in INPUTS for q in read(p)['rows']};assert all(read(p)['manifestSHA256']==sha for p in INPUTS)
 for label,ids in PAIRS.items():
  b='government-xl-terrain-recovery-'+label+'-original-pair-preflight-v1-20261010';d=BASE/b;assert not d.exists();uids=['landsd/'+str(i)+':0'for i in ids];rows=[r[u]for u in sorted(uids)]
  for row in rows:assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256']
  out=dict(rows=rows,missing=[],manifestSHA256=sha,batch=b,sourceGeometryChanges=0,publication=False,installationApproved=False,exactOriginalSourceMembershipOnly=True,identityAccepted=False,structuralSupportAccepted=False,qualification='Exact individually recovered native original candidates only. Current same-parent/basic heights select an investigation; not a common-ownership, identity or support exemption. Independent complete original/current gates mandatory.',evidenceRefs=[ref(p)for p in [Path(__file__),*INPUTS,ROOT/'3d-viewer/city/data/manifest.json',*[ROOT/q['candidate']['path']for q in rows]]]);save(d/'check-selection.json.gz',out);save(d/'selection.json.gz',out);print(b,flush=True)
if __name__=='__main__':main()

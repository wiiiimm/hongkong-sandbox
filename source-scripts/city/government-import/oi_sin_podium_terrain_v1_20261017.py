"""Prepare fresh single-podium inputs and run existing original terrain pipeline."""
import subprocess,sys
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-current-pair-v1-20261017';INPUT=BASE/'government-xl-oi-sin-podium-terrain-inputs-v1-20261017';BATCH='government-xl-oi-sin-podium-terrain-v1-20261017';UID='landsd/91128:0'
def main():
 assert not INPUT.exists()and not(BASE/BATCH).exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  assert c.execute('SELECT review_state FROM astra_modelling.model_reviews WHERE uid=%s ORDER BY updated_at DESC LIMIT 1',(UID,)).fetchone()is None,'Existing podium review must be explicitly reconciled'
 pins={q['path']:q['sha256']for q in r['evidenceRefs']}
 for name in ['selection.json.gz','context.json.gz','identity-proofs.json']:
  p=PRIOR/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 selection=read(PRIOR/'selection.json.gz');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256'];row=next(x for x in selection['rows']if x['uid']==UID);assert next(x for x in read(PRIOR/'identity-proofs.json')['rows']if x['uid']==UID)['passed'];row['currentReview']=None
 context=next(x for x in read(PRIOR/'context.json.gz')['rows']if x['uid']==UID)
 save(INPUT/'check-selection.json.gz',dict(selection,rows=[row]));save(INPUT/'context.json.gz',dict(rows=[context]));save(INPUT/'input-provenance.json',dict(priorJobId=r['jobId'],priorReceiptSHA256=digest((PRIOR/'result.json').read_bytes()),scriptSHA256=digest(Path(__file__).read_bytes()),publication=False))
 subprocess.run([sys.executable,str(HERE/'xl-cell-indexed-terrain-continuation.py'),'--uid',UID,'--batch',BATCH,'--base',str(INPUT.relative_to(ROOT))],cwd=ROOT,check=True)
if __name__=='__main__':main()

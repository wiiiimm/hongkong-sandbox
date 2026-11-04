"""Check whether existing basic companions can remain supported by unchanged original."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-basic-support-v1-20261021';DOC=BASE/BATCH;CAP=BASE/'government-xl-manhattan-assembly-capture-v1-20261021'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json']
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 capture=read(CAP/'attributes.json.gz');p=next(x for x in capture['rows'] if x['uid']=='landsd/276331:0');sel=read(CAP/'selection.json.gz')['rows'];buildings=[x['source']['building'] for x in sel if x['uid']!=p['uid']];assert len(buildings)==7
 save(DOC/'input.json.gz',dict(buildings=buildings,podium=dict(position=p['completeLiteralWorldPosition'],index=p['completeOriginalIndex']),evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in refs]))
 tool=HERE/'manhattan_basic_support_v1_20261021.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);out=read(DOC/'support.json.gz')
 for p,h in out['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=dict(uids=[b['uid'] for b in buildings],rows=[dict(uid=x['uid'],passed=x['proof']['passed'],samples=x['proof']['samples'],strictContacts=x['proof']['strictContacts'],unresolved=len(x['proof']['unresolved'])) for x in out['rows']],installationApproved=False)
 save(DOC/'summary.json',summary);module('manhattan_basic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'existing-basic-original-podium-support-diagnostic',list(dict.fromkeys(refs+[tool])),summary)
if __name__=='__main__':main()

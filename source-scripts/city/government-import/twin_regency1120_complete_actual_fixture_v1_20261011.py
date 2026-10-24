"""Actual completed whole-pair tuple; no synthetic source body substitution."""
from run import ROOT,read,digest
import twin155_complete_boundary_actual_fixture_v1_20261011 as prior
import twin_regency1120_complete_original_role_composition_v1_20261011 as k
BASE=ROOT/'docs/astra-city/government-import'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def actual_fixture():
 docs,parts,refs,receipts=prior.actual_fixture();worlds=next(iter(parts.values()))['worlds']
 for name,batch in [('boundary155','xl-terrain-recovery-20261011-twin155-named-complete-boundary-visual-proposals-v1'),('placement138','xl-terrain-recovery-20261011-twin138-named-original-source-placement-proposals-v1')]:
  folder=BASE/batch;r=read(folder/'result.json');receipts[name]=r;refs.append(ref(folder/'result.json'));p=folder/'diagnostic.json.gz';assert ref(p)in r['evidenceRefs'];docs[name]=read(p);refs.append(ref(p))
  for q in r['evidenceRefs']:assert ref(ROOT/q['path'])==q;refs.append(q)
 args=dict(worlds=worlds,graph=docs['graph'],finite=docs['finite'],paths=docs['paths'],boundary155=docs['boundary155'],placement138=docs['placement138'])
 args['expected_binding']=k.binding(**args)
 return args,docs,list({(r['path'],r['sha256']):r for r in refs}.values()),receipts

"""Freeze three Block17 source-only receipts; preserve held review state exactly."""
import ast,importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
B=ROOT/'docs/astra-city/government-import';UID='landsd/256116:0'
S=importlib.util.spec_from_file_location('block17_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');F=importlib.util.module_from_spec(S);S.loader.exec_module(F)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def imports(p,seen):
 if p in seen or not p.is_file():return
 seen.add(p)
 if p.suffix!='.py':return
 for n in ast.walk(ast.parse(p.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[a.name for a in n.names]if isinstance(n,ast.Import)else[]
  for name in names:imports(HERE/(name.split('.')[0]+'.py'),seen)
def state():
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');return c.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=%s',(UID,)).fetchall()
def main():
 before=state();jobs=[]
 names=[('complete-original-support-graph-v1','parkview_block17_complete_original_support_graph_20261011.py'),('bounded-eligible-native-route-v1','parkview_block17_bounded_eligible_native_bfs_20261011.py'),('original-lower-opening-association-v3','parkview_block17_original_lower_opening_association_v3_20261011.py')]
 for short,producer in names:
  batch='government-xl-parkview-block17-'+short+'-20261011';doc=B/batch;assert not(doc/'result.json').exists();d=read(doc/'diagnostic.json.gz');paths=set();imports(Path(__file__),paths);imports(HERE/producer,paths)
  for r in d['evidenceRefs']:
   p=ROOT/r['path'];assert ref(p)==r;paths.add(p)
  paths.add(doc/'diagnostic.json.gz')
  notes='Bounded original source-only evidence. No installation/current acceptance, source or terrain changes, whole-native reapproval, architectural function, closed-solid, point-only bridge or visual-body root credit. '
  if short=='complete-original-support-graph-v1':notes+='All15,614 original faces accounted:93 genuine nonzero shared-edge bodies cover15,612 facets; original24/25 are exactly nonrendering and remain unchanged without support credit. Complete14,473 cross-body AABB pairs yield4,967 contacts:3,119 segments,32 areas and1,816 points. Exactly92 bodies/15,602 nonzero facets have positive-dimensional conditional paths from body0 at original cap54418; ten-face body62 has zero exact primitive contacts. The carrier grade-to-cap route is independently required; raw neighbour256120 regression and both ground warnings remain untouched.'
  elif short=='bounded-eligible-native-route-v1':notes+='Frozen currentcb795 carrier ground25,167 facets SHA bba71625b8cff1e25e3d220ccaeab0d902bfdcce3c73eac6d76f1053b4255140. Original native wall51646 has two exact positive upper-ground interfaces and an actual exposed original vertex303153239713/73954197504m above every finite ground facet at its XZ. Original path51646→49682→54417→54418 uses three complete strictly exposed shared edges and wholly covered strictly clear intermediate facets; cap54418 strict whole finite lower bound113831/32768m is reused from root-frozen original proof.15 examined facets/14 edges within192-face budget. Wall remains partly buried: actual original lower vertex gap−57736278035/18488549376m is retained; no whole-wall-clearance/whole-native-body credit. Known facet54320 coverage gap and partly buried52248–52249 edge excluded. No fresh current acceptance capture; future whole-source/F32/identity/foreign/retained/runtime/browser/publisher guards remain mandatory.'
  else:notes+='Exact source/body/host-bound v3 guard passes for complete original ten-face body62, original faces13229–13238, with all four directed lower-opening edges at own exact minimumY370.8290100097656m. Entire edges associate with nonzero reached original host union within unchanged±.1m band (gap557/32768m≈.017m). No exact contact is introduced; function and visual role approval remain separate. Original nonrendering faces24/25 are retained but excluded from host band credit. Existing root-reviewed11 adversarial kernel tests apply; this source-only proof does not replace actual F32/current checks.'
  (doc/'REVIEW.md').write_text('# Parkview Block17 '+short+'\n\n'+notes+'\n')
  save(doc/'review.json',dict(uids=[UID],finding=notes,sourceOnly=True,currentAcceptance=False,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,historicalReasonsUnchanged=['ground-contact-unresolved','sampled-ground-gap-below-model-bottom','terrain-regresses-neighbour:landsd/256120:0'],remaining=['independent-numerical-and-source-role-review','whole-current-source-finite-original-and-actual-F32','exact-current-identity-and-full-foreign-scope','all-retained-native-and-runtime-loader-gates','staged-browser-and-guarded-publisher'],evidenceRefs=[ref(p)for p in sorted(paths)]))
  paths.update([doc/'REVIEW.md',doc/'review.json'])
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY')
   for p in list(paths):
    if p.name=='result.json':
     receipt=read(p)
     if 'jobId'in receipt:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  r=F.freeze(batch,short,sorted(paths),dict(uids=[UID],sourceOnly=True,currentAcceptance=False,scriptFullAcceptancePassed=False,currentHeldReasonsPreserved=True,nativeReacceptance=False,sourceGeometryChanges=0,terrainChanges=0,outcome=short+'-source-only-complete',noArchitecturalFunctionClaim=True));jobs.append(dict(batch=batch,jobId=r['jobId']))
 assert state()==before,'Held Block17 review state changed during source-only freeze'
 print(json.dumps(dict(jobs=jobs,heldReviewStateUnchanged=True)),flush=True)
if __name__=='__main__':main()

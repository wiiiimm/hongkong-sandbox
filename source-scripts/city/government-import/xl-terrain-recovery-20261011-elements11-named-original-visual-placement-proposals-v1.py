"""Freeze reviewed original source-placement roles, no current acceptance."""
from pathlib import Path
import importlib.util,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements11-named-original-visual-placement-proposals-v1';DOC=BASE/BATCH
INPUTS=(
 'elements-complete-owned-original-contact-graph-v1',
 'elements132-four-stream-qualified-host-association-v1',
 'elements-owned-four-stream-complete-finite-v1',
 'elements-sun-star-two-current-render-attribute-capture-v1',
 'elements-bounded-owned-four-stream-path-replay-v1',
 'elements15-intrinsic-sheet-backing-and-roof-correspondence-v1',
 'elements4-named-complete-perimeter-visual-sheet-proposals-v1',
 'elements11-whole-original-building-placement-context-v2')
HELPERS=(
 'elements11_named_original_visual_placement_proposal_v1_20261011.py',
 'test_elements11_named_original_visual_placement_proposal_v1_20261011.py',
 'elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'exact_packed_world_geometry_20261009.py',
 'exact_original_shared_edge_component_census_v2_20261011.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]+[ref(HERE/n)for n in HELPERS]
 for stem in INPUTS:
  folder=BASE/('xl-terrain-recovery-20261011-'+stem);r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(ref(folder/'result.json'))
  for q in r['evidenceRefs']:
   p=ROOT/q['path'];assert p.is_file()and ref(p)==q;refs.append(q)
 refs=list({(q['path'],q['sha256']):q for q in refs}.values())
 log=Path('/tmp/elements11-named-original-visual-placement-v1-tests-20261011.log').read_bytes();assert b'Ran 15 tests'in log and b'\nOK\n'in log
 k=load(HELPERS[0].removesuffix('.py'),HERE/HELPERS[0]);fixture=load(HELPERS[1].removesuffix('.py'),HERE/HELPERS[1]);docs,packages=fixture.actual_fixture()
 paths=read(BASE/('xl-terrain-recovery-20261011-'+INPUTS[4])/'diagnostic.json.gz')
 for row in docs['bands']['rows']:
  assert row['boundedHostPathReceipt']==ref(BASE/('xl-terrain-recovery-20261011-'+INPUTS[4])/'result.json')
  p=next(p for p in paths['rows']if p['mode']==row['mode']);assert len(row['qualifiedHostOriginalBodies'])==866 and set(row['qualifiedHostOriginalBodies'])==set(p['qualifiedDiagnosticOwnedBodies'])and p['noWholeNativeBodySeed']is True
 claim=reservations.claim('elements11-placement-roles-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  proposals=[]
  for part in sorted(packages):
   proposals.append(k.verify(**packages[part]));assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)
  assert len(proposals)==11 and sum(len(p['completeOriginalFaces'])for p in proposals)==2389
  assert all(ref(ROOT/q['path'])==q for q in refs)
  DOC.mkdir(parents=True);(DOC/'actual-adverse-tests-v1.log').write_bytes(log)
  save(DOC/'diagnostic.json.gz',dict(uids=list(k.SOURCE_SHA),all11NamedOriginalVisualPlacementProposals=proposals,completeOriginalPartCount=11,completeOriginalFaces=2389,qualifiedContextOnlyFrom866NonvisualPaths=True,allOriginalMountingFanAndBackingNegativesPreserved=True,sourceOnly=True,noFreshCurrentReacceptance=True,authoredRoleAccepted=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs))
  freezer=load('elements11_source_placement_freeze',HERE/HELPERS[-1]);freezer.freeze(BATCH,'elements11-reviewed-exact-original-visual-placement-proposals-no-current-acceptance-v1',[ROOT/q['path']for q in refs]+list(DOC.iterdir()),dict(uids=list(k.SOURCE_SHA),sourceOnly=True,completeNamedProposalParts=11,completeOriginalFaces=2389,currentAcceptance=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

"""Completed-source proposal composition; no fresh current or role acceptance.

The exact complete source fixture replays untouched assets/indices/four worlds.
Completed numerical contexts and nonvisual hosts are independently file/Neon
validated before the named policy is loaded. This layer grants no root/bridge.
"""
from pathlib import Path
import importlib.util,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements24-named-original-visual-proposals-v1';DOC=BASE/BATCH
INPUTS=(
 'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1',
 'xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1',
 'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1',
 'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1',
 'xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1',
 'xl-terrain-recovery-20261011-elements31-complete-lateral-patches-and39-disposition-v1')
HELPERS=(
 'elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'test_elements24_named_original_mounted_visual_surface_proposal_v1_20261011.py',
 'test_elements24_named_original_mounted_visual_surface_proposal_v2_20261011.py',
 'exact_original_shared_edge_component_census_v2_20261011.py',
 'exact_packed_world_geometry_20261009.py',
 'xl-popcorn-source-investigations-checkpoints-20261009.py')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]+[ref(HERE/n)for n in HELPERS];receipts={}
 for batch in INPUTS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[batch]=r;refs.append(ref(folder/'result.json'))
  for binding in r['evidenceRefs']:
   p=ROOT/binding['path'];assert p.is_file()and ref(p)==binding;refs.append(binding)
 refs=list({(r['path'],r['sha256']):r for r in refs}.values())
 testlogs={n:Path('/tmp/elements24-named-original-visual-proposal-'+n+'-tests-20261011.log').read_bytes()for n in ['v1','v2']}
 assert b'Ran 16 tests'in testlogs['v1']and b'\nOK\n'in testlogs['v1']
 assert b'Ran 23 tests'in testlogs['v2']and b'\nOK\n'in testlogs['v2']
 k=load(HELPERS[0].removesuffix('.py'),HERE/HELPERS[0]);fixture=load(HELPERS[1].removesuffix('.py'),HERE/HELPERS[1]);docs,packages=fixture.actual_fixture()
 # Host lists are derived from the completed four-stream nonvisual forest,
 # not from mounted proposals or the availability of a native catalogue entry.
 paths=read(BASE/INPUTS[4]/'diagnostic.json.gz')
 for row in docs['bands']['rows']:
  assert row['boundedHostPathReceipt']==ref(BASE/INPUTS[4]/'result.json')
  qualified=set(row['qualifiedHostOriginalBodies']);assert len(qualified)==866
  pathrow=next(p for p in paths['rows']if p['mode']==row['mode'])
  assert qualified==set(pathrow['qualifiedDiagnosticOwnedBodies'])and pathrow['noWholeNativeBodySeed']is True
  assert all(i<998 for i in qualified)
  expected={f for i in qualified for f in docs['graph']['components'][i]['globalOriginalFaces']}
  for p in packages.values():
   actual=set(p['qualified_hosts'][row['mode']]);offset=0 if p['uid']=='landsd/204145:0'else 12129
   assert actual=={f for f in expected if (f<12129)==(offset==0)}
 claim=reservations.claim('elements24-named-visual-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  results=[]
  for part in sorted(packages):
   results.append(k.verify(**packages[part]));assert reservations.heartbeat(lease)['ok']and reservations.owns(lease)
  assert len(results)==24 and sum(len(r['completeOriginalFaces'])for r in results)==82
  assert all(ref(ROOT/r['path'])==r for r in refs)
  DOC.mkdir(parents=True)
  for version,data in testlogs.items():
   p=DOC/('actual-adverse-tests-'+version+'.log');p.write_bytes(data);assert p.read_bytes()==data
  output=dict(uids=list(k.SOURCE_SHA),all24ExactNamedSourceVisualProposals=results,completeSourcePartCount=24,completeOriginalFaces=82,allActualSourceAndFourStreamNumericContextsPinned=True,qualifiedHostsOnlyFrom866NonvisualPaths=True,unprovedFreeEdgesAndInteriorBandsRemainVerbatim=True,all15RemainingBodiesStillUnqualified=[69,70,75,76,78,705,744,839,890,893,897,902,904,918,921],sourceOnly=True,noFreshCurrentReacceptance=True,authoredRoleAccepted=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',output)
  freezer=load('elements24_proposal_freeze',HERE/HELPERS[-1]);freezer.freeze(BATCH,'elements24-exact-named-complete-original-visual-mount-proposals-no-current-acceptance-v1',[ROOT/r['path']for r in refs]+list(DOC.iterdir()),dict(uids=list(k.SOURCE_SHA),sourceOnly=True,completeNamedProposalParts=24,completeOriginalFaces=82,remainingUnqualifiedParts=15,currentAcceptance=False,structuralRootOrBridgeCredit=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()

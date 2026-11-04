"""DRAFT source-bound typed visual context; never full-body current acceptance."""
import argparse,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import west_wing26195_visual_mounting_interface_context_draft_v1_20261012 as M
import west_wing26195_typed_original_visual_surface_roles_draft_v1_20261012 as H
BATCH='government-xl-west-wing26195-current-typed-original-visual-surface-roles-v1-20261012';DOC=M.D.S.G.P.BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=M.D.S.G.P.BASE/'government-xl-west-wing26195-typed-original-visual-surface-role-proposal-v1-20261012';FREEZER=HERE/'west_wing26195_freeze_current_typed_visual_surface_roles_draft_v1_20261012.py';TEST=HERE/'test_west_wing26195_typed_original_visual_surface_roles_draft_v1_20261012.py';HELPER=Path(H.__file__);ref=M.ref

def validation():
 v=read(PROPOSAL/'no-worker-validation.json');assert v['exactTests']==17 and v['testExitCode']==0 and v['noDBQueries']and v['noReservations']and v['noNumericalRecomputation'];assert v['codeRefs']==[ref(p)for p in [HELPER,TEST,Path(__file__),FREEZER]];assert ref(ROOT/v['testLog']['path'])==v['testLog'];s=(ROOT/v['testLog']['path']).read_text();assert 'Ran 17 tests'in s and s.rstrip().endswith('OK');return [ref(PROPOSAL/'no-worker-validation.json')]+v['codeRefs']+[v['testLog'],ref(PROPOSAL/'METHOD.md')]
def inputs():
 _,scope,worlds,finite,_=M.inputs();receipt=read(M.DOC/'result.json');assert receipt['jobId']=='6e368cf0ad826dac3d7c21a89593183403470fb9cf32ba7c07b50cd7506b92aa'and ref(M.DOC/'result.json')['sha256']=='705fbcc211ccf1b0a1bf30378932eb60807ee1de83221a049438ef593da35155'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
 mount=read(M.DOC/'diagnostic.json.gz');visual=read(M.VISUAL/'context.json');graph=read(M.D.DOC/'diagnostic.json.gz');assert mount['allFourStreamBindings']==finite['allFourStreamBindings'];assert len(scope['canonicalReservationResources'])==15
 for name,w in worlds.items():assert digest(w.tobytes())==mount['allFourStreamBindings'][name]['wholeWorldSHA256']
 assert digest((ROOT/visual['source']['path']).read_bytes())==H.SOURCE and M.D.S.G.P.F.UID==H.UID
 return receipt,scope,mount,visual,finite,graph

def calculate(mount,visual,finite,graph):return H.verify(mount,visual,finite['originalBodyCensus'],graph,dict(uid=H.UID,sourceSHA256=H.SOURCE),expected_binding=H.input_binding(mount,visual,finite['originalBodyCensus'],graph))

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--owned',action='store_true');args=parser.parse_args();valid=validation();receipt,scope,mount,visual,finite,graph=inputs();assert not(DOC/'diagnostic.json.gz').exists()
 if not args.owned:
  c=reservations.claim('westwing-typed-visual-context-'+str(uuid.uuid4()),scope['canonicalReservationResources'],batch=BATCH,ttl=1800);assert c['ok'],c;save(LOCAL/'reservation.json',json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);walker=M.D.S.G.P.F.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','westwingtypedvisualclosure');paths=set();walker.local_imports(Path(__file__),paths);walker.local_imports(FREEZER,paths);codes=[ref(p)for p in sorted(paths)]+valid
 def fence():
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==scope['currentManifest']
  for path,h in scope['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h
  for e in codes:assert ref(ROOT/e['path'])==e
  before=read(M.D.S.G.P.F.CAP/'protected-state-before.json');assert json.loads(json.dumps(M.D.S.G.P.F.state(before['uids']),default=str))==before['rows']
 fence();roles=calculate(mount,visual,finite,graph);fence();assert reservations.heartbeat(lease)['ok'];save(DOC/'diagnostic.json.gz',dict(sourceOnly=True,physicalAccepted=False,installationApproved=False,legacyDeliveryAnd15ReviewsUnchanged=True,noGroundContactCorridorOrBandArithmeticRerun=True,currentManifest=scope['currentManifest'],allFourStreamBindings=finite['allFourStreamBindings'],typedSourceVisualRoleContext=roles,evidenceRefs=codes+[ref(M.DOC/'result.json'),ref(M.DOC/'diagnostic.json.gz'),ref(M.VISUAL/'context.json'),ref(M.VISUAL/'actual-export-readback-and-observations.json'),ref(M.D.DOC/'diagnostic.json.gz'),ref(M.D.S.G.P.F.DOC/'diagnostic.json.gz')]+[{k:e[k]for k in ['path','sha256']}for e in visual['outputs']]));print(json.dumps(dict(sourceVisualBodies=[108,113],independentHostBody0Qualified=False,remainingBodyRoles=116,physicalAccepted=False)),flush=True);subprocess.run([sys.executable,str(FREEZER),'--lease-file',str(LOCAL/'reservation.json')],cwd=ROOT,check=True)
if __name__=='__main__':main()

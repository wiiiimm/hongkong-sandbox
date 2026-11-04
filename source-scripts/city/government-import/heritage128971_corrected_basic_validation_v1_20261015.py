"""Private original-work follow-up; real before-state retained for changed BASIC base."""
from pathlib import Path
from fractions import Fraction
import copy,json,subprocess,uuid
import numpy as np
import heritage165054_parent_basic_production_capture_v1_20261014 as capture
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from upton_parent_tin_regression_bookkeeping_v1_20261012 import triangles,finite_record,sha
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=capture.ROOT;HERE=capture.HERE;BASE=capture.BASE
BATCH='government-xl-heritage128971-corrected-basic-validation-v1-20261015';DOC=BASE/BATCH
PROPOSAL=BASE/'government-xl-heritage128971-estimated-base-proposal-v1-20261015/proposal.json'
UID='landsd/128971:0';read=capture.read;save=capture.save;ref=capture.ref;check=capture.check
RUNTIME=HERE/'heritage128971_corrected_basic_capture_v1_20261015.mjs'
def main():
 from run import reservations
 assert not DOC.exists()
 p=read(PROPOSAL)
 for q in p['evidenceRefs']:check(q)
 old=read(capture.DOC/'complete23-current-basic-constructor-streams.json.gz');prior=next(r for r in old['rows']if r['uid']==UID)
 assert prior['building']==p['sourceBuildingBefore'];assert p['privateProposalOnly']and not p['published']
 building=copy.deepcopy(prior['building']);building['base']=p['base']
 assert {k for k in building if building[k]!=prior['building'][k]}=={'base'}
 actors=[r['uid']for r in old['rows']]
 resources=reservations.normalise([r for r in capture.resources(actors)if not r.startswith('immutable-source-proof:')]+['immutable-source-proof:'+BATCH])
 refs=p['evidenceRefs']+[ref(PROPOSAL),ref(Path(__file__)),ref(RUNTIME)]+[ref(capture.DOC/n)for n in ['complete23-current-basic-constructor-streams.json.gz','complete-before-ground.json.gz','complete-candidate-ground.json.gz','neighbour-inputs.json.gz','neighbour-checks.json']]
 c=reservations.claim('heritage-shelter-'+str(uuid.uuid4()),resources,ttl=3600,batch=BATCH);assert c['ok'],c
 lease=c['reservation'];pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
 def fence():
  pulse(force=True)
  for q in refs:check(q);pulse()
 def call(args):
  fence();r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/('command-'+str(len(list(DOC.glob('command-*.json'))))+'.json'),dict(command=args,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stderr;fence()
 try:
  fence();DOC.mkdir();save(DOC/'input.json.gz',dict(building=building,evidenceRefs=refs))
  call(['node',str(RUNTIME),str(DOC.relative_to(ROOT))])
  selection=read(capture.DOC/'neighbour-inputs.json.gz');row=next(r for r in selection['rows']if r['building']['uid']==UID);assert row['building']==prior['building'];row['building']=building
  assert UID not in selection['candidateIds'];save(DOC/'neighbour-inputs.json.gz',selection)
  call(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'])
  original=read(capture.DOC/'neighbour-checks.json');raw=read(DOC/'neighbour-checks.json');original_by={r['uid']:r for r in original['rows']};combined=[]
  for r in raw['rows']:
   before=original_by[r['uid']]
   if r['uid']!=UID:assert r==before;combined.append(r);continue
   assert not r['candidate']and not r['existingNative']and r['checks']==before['checks']
   old_min,old_max=before['beforeGap'];new_min,new_max=r['afterGap'];reasons=[]
   if new_min<min(-.5,old_min)-.25:reasons.append('increased-neighbour-burial')
   if new_max>max(1,old_max)+.25:reasons.append('increased-neighbour-ground-gap')
   old_ground_max=prior['building']['base']+(prior['building'].get('minimum')or 0)-old_min
   new_ground_max=building['base']+(building.get('minimum')or 0)-new_min
   if new_ground_max>max(building['base']+building['height']-.1,old_ground_max)+.25:reasons.append('increased-neighbour-roof-burial')
   combined.append(dict(r,beforeGap=before['beforeGap'],reasons=reasons,originalBeforeRow=before,rawChangedBaseOnBothTerrainsRow=r,baselineCorrectedForJointEstimatedBaseAndTerrainChange=True))
  save(DOC/'joint-neighbour-comparison.json',dict(rows=combined,regressions=[r for r in combined if r['reasons']],originalBeforeStatePreserved=True,rawCheckerReportRetained=True,installationApproved=False))
  new=read(DOC/'corrected-basic-streams.json.gz');assert len(new['meshes'])==len(prior['meshes'])and new['completeFaces']==prior['completeFaces']
  for a,b in zip(prior['meshes'],new['meshes']):
   assert a['index']==b['index']and a['completePositionVerticesIncludingUnused']==b['completePositionVerticesIncludingUnused']
   for mode in a['streams']:
    aa=np.asarray(a['streams'][mode]).reshape(-1,3);bb=np.asarray(b['streams'][mode]).reshape(-1,3);assert np.array_equal(aa[:,[0,2]],bb[:,[0,2]])
  grounds=[triangles(np.asarray(read(capture.DOC/n)['completeRelevantDrawnTriplets']).reshape(-1,3,3))for n in ['complete-before-ground.json.gz','complete-candidate-ground.json.gz']];selectors=[CompleteGround(g)for g in grounds];results=[];cache={}
  for mode in ['constructorFloat32World','leftFloat32World','balancedFloat32World']:
   worlds=[]
   for actor in [prior,new]:worlds.append(triangles(np.concatenate([np.asarray(m['streams'][mode]).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)]for m in actor['meshes']])))
   rows=[]
   for i,(a,b)in enumerate(zip(*worlds)):
    findings=[]
    for face,g,selector in zip([a,b],grounds,selectors):
     ids,proof=selector.select([[Fraction(float(x))for x in v]for v in face]);key=(sha(face),sha(g[ids]))
     if key not in cache:cache[key]=finite_record(face,g[ids])
     findings.append(dict(selection=proof,finite=cache[key]))
    rows.append(dict(face=i,before=findings[0],after=findings[1]));pulse()
   results.append(dict(mode=mode,completeFaces=len(rows),rows=rows,candidateUnproved=[r['face']for r in rows if not r['after']['finite']['ordinaryBoundProved']],newlyUnproved=[r['face']for r in rows if r['before']['finite']['ordinaryBoundProved']and not r['after']['finite']['ordinaryBoundProved']]))
   print(json.dumps({k:results[-1][k]for k in ['mode','completeFaces','candidateUnproved','newlyUnproved']}),flush=True)
  for s in selectors:s.verify_binding()
  fence();save(DOC/'complete-corrected-basic-finite.json.gz',dict(rows=results,evidenceRefs=refs,privateOnly=True,installationApproved=False,newlyInstalled=0))
  save(DOC/'completion.json',dict(complete=True,uid=UID,ordinaryRegressions=[r['uid']for r in combined if r['reasons']],finiteCandidateUnproved={r['mode']:r['candidateUnproved']for r in results},sourceGeometryChanges=0,privateOnly=True,publication=False,neonDiagnosticReceiptPending=True))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

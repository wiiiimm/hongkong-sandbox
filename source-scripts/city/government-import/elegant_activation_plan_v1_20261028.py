"""Prepare a private availability-only activation plan from the complete contact matrix."""
import argparse,sys,uuid,copy,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists();rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources'])
 if not a.owned:
  assert not local.exists();claim=reservations.claim('private-activation-plan-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 matrix=take(PREFIX+'activation-interference-matrix-v1-20261028','summary.json');rows=take(PREFIX+'activation-interference-matrix-v1-20261028','rows.json.gz');uids=sorted(matrix['uids']);assert len(uids)==16 and matrix['completeOriginalPairs']==120 and matrix['completeMixedPairs']==288
 # A conservative common availability switch for each connected mixed-state component.
 edges=[list(pair)for pair in matrix['positiveMixedPairs']if pair[1]in uids];pending=set(uids);components=[]
 while pending:
  found={min(pending)};old=set()
  while old!=found:
   old=set(found)
   for left,right in edges:
    if left in found or right in found:found.update([left,right])
  components.append(sorted(found));pending-=found
 assert components==[uids]
 fixture=take(PREFIX+'full-scene-preview-fixture-v2-20261028','fixture-inputs.json');config_path=ROOT/fixture['configPath'];config=read(config_path);refs.append(config_path)
 oldcat=HERE/'local'/(PREFIX+'full-scene-preview-fixture-v2-20261028')/'catalogue.json';assert digest(oldcat.read_bytes())==pins[PREFIX+'full-scene-preview-fixture-v2-20261028'][str(oldcat.relative_to(ROOT))];refs.append(oldcat);cat=copy.deepcopy(read(oldcat));assert sorted(e['uid']for e in cat['models'])==uids
 replacement=take(PREFIX+'canopy-replacement-review-v1-20261028','summary.json');assert replacement['conditionalReplacementDecisionApproved']and replacement['requiresPrivateRuntimeFallbackChecks']
 for e in cat['models']:
  assert not e.get('supportDependencies')and not e.get('activationGroup');e['activationGroup']=uids
  if e['uid']==replacement['sourceUid']:
   assert e['sha256']==replacement['sourceSHA256'];e['suppressesBuildingUids']=replacement['proposedSuppression']['suppressesBuildingUids']
  assert not e['publicationApproved']and not e['placementReviewed']
 save(out/'private-catalogue-draft.json',cat)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==fixture['currentManifestSHA256'];refs.append(manifest)
 inp=out/'planner-input.json';save(inp,dict(catalogue=cat,activationGroup=uids,inputHashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in [oldcat,manifest]}))
 tool=HERE/'elegant_activation_plan_contract_v1_20261028.mjs';refs.append(tool);subprocess.run(['node',str(tool),str(inp.relative_to(ROOT)),str((out/'planner-contract.json').relative_to(ROOT))],cwd=ROOT,check=True)
 proof=read(out/'planner-contract.json');assert proof['allPassed']and proof['caseCount']==66
 for path,sha in proof['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 result=dict(uids=uids,activationGroups=components,directedMixedStateContactEdges=edges,positiveRetainedBasicInterfaces=[p for p in matrix['positiveMixedPairs']if p[1]not in uids],plannerCases=66,desktopMobilePlannerContractPassed=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalSupportMetadataPending=True,sourceInterfaceRoleAcceptancePending=True,actualBrowserAvailabilityFailureBaseOnlyPending=True,installationApproved=False,publication=False,qualification='The complete directed mixed-state contact graph connects all16sources. A conservative common availability switch prevents these mixed states without asserting a physical support edge. Actual unchanged production planner admits all16on desktop/mobile and rejects partial groups for each missing member. This is metadata/planner evidence only, not failed-download/browser/base-only/placement acceptance. Native physical support dependencies and retained Rex BASIC support must still be bound before final integration.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('activation_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-complete-contact-derived-availability-group-and-actual-runtime-planner-contract',list(dict.fromkeys(refs)),read(out/'summary.json'))
if __name__=='__main__':main()

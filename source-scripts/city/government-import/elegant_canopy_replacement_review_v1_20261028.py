"""Record a source-bound duplicate BASIC canopy decision for private activation tests."""
import argparse,sys,uuid
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
  assert not local.exists();claim=reservations.claim('root-conditional-canopy-replacement-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 packet=take(PREFIX+'canopy-feature-packet-v1-20261028','summary.json');context=take(PREFIX+'active-boundary-context-v1-20261028','summary.json')
 assert packet['sourceUid']=='landsd/236170:0'and packet['basicUid']=='landsd/99061:0'and packet['buildingCSUID']=='3228616401T20080917'
 assert packet['officialRecord']['BaseHeight']is None and packet['officialRecord']['TopHeight']is None
 b=packet['exactCurrentForm'];tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert digest(tile.read_bytes())==packet['tileSHA256'];assert next(x for x in read(tile)['buildings']if x['uid']==b['uid'])==b;refs.append(tile)
 assert b['heightSource']=='estimated'and b['baseSource']=='terrain-estimated'and b['structureType']=='Open-sided Structure'
 inspected=[packet['image']]+[r for r in context['figures']if r['otherUid']==b['uid']and r['path'].endswith('canopy-existing-interfaces-1.png')];assert len(inspected)==2
 for r in inspected:path=ROOT/r['path'];assert digest(path.read_bytes())==r['sha256'];refs.append(path)
 selection=take(PREFIX+'sixteen-original-updated-runtime-v1-20261028','selection.json.gz');row=next(r for r in selection['rows']if r['uid']==packet['sourceUid']);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==packet['sourceSHA256']==row['sourceSHA256'];refs.append(asset)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 review=dict(uids=packet['uids'],reviewer='Codex ROOT',reviewType='conditional-estimated-BASIC-canopy-replacement-for-private-runtime-tests',sourceUid=packet['sourceUid'],sourceSHA256=packet['sourceSHA256'],sourceModelId=packet['sourceModelId'],basicUid=b['uid'],buildingCSUID=b['buildingCSUID'],exactBasicForm=b,tileSHA256=packet['tileSHA256'],currentManifestSHA256=selection['manifestSHA256'],sourceFeatureAssociationApproved=True,conditionalReplacementDecisionApproved=True,proposedSuppression=dict(ownerUid=packet['sourceUid'],suppressesBuildingUids=[b['uid']],onlyWhileExactOriginalActive=True,restoreBasicOnUnavailableOrBaseOnly=True),imagesActuallyInspected=inspected,
  basis=[
   'The active official open-sided-structure CSUID binds this BASIC footprint, with no surveyed top/base. ROOT inspected the exact original roof/current official/BASIC overlay and the original-source 3D interface view: the unchanged podium contains the detailed pavilion roof/columns/stairs at this feature, while the viewer adds an estimated lower flat canopy and two posts in the same location.',
   'The judgement uses exact source graph identity, active registered feature type and footprint, native roof components, and the 3D structural arrangement together. It is not a coverage-percentage rule. The retained source projection/footprint differences and the approximately 0.109m current/BASIC footprint discrepancy remain in the packet; no missing outline is declared covered and no cadastral ownership is inferred.',
   'Keep the complete original source unchanged. Suppress only BASIC99061 while that exact original is active, then restore its qualified fallback foundation when absent or Base-only. Do not remove the BASIC source form globally or alter the government roof/columns to fit an estimated height.',
   'This permits a private conditional activation/failure/restoration test. Actual runtime suppression, collision, fallback, whole-group placement and guarded publication acceptance remain required; this receipt alone does not install anything.'
  ],originalRoofComponentsVerbatim=packet['completeOriginalRoofComponentsAboveEstimatedRoof'],estimatedBasicRoofY=packet['estimatedBasicRoofY'],rawPacketSuppressionApproved=False,requiresPrivateRuntimeFallbackChecks=True,sourceGeometryChanges=0,sourcePoseChanges=0,evidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,publicationApproved=False,installationApproved=False,publication=False)
 save(out/'summary.json',review);assert reservations.owns(lease)
 module('canopy_replacement_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'root-source-bound-conditional-estimated-canopy-replacement-decision',list(dict.fromkeys(refs)),read(out/'summary.json'))
if __name__=='__main__':main()

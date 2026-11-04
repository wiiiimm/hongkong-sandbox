"""Bind the exact existing support providers into a private original activation fixture."""
import argparse,sys,uuid,copy,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-elegant-garden-'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert a.batch.startswith(PREFIX)and '/'not in a.batch
 out=BASE/a.batch;local=HERE/'local'/a.batch;lp=local/'reservation.json';assert not out.exists();rp=BASE/(PREFIX+'sixteen-original-updated-terrain-plan-v1-20261028.json');resources=set(read(rp)['resources']);assert 'building:landsd/228592:0'in resources
 if not a.owned:
  assert not local.exists();claim=reservations.claim('supported-atomic-original-fixture-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=1800);assert claim['ok']
  return execute_reserved(claim['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease)and resources<=set(lease['resources']);refs=[Path(__file__),rp];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 plan=take(PREFIX+'activation-plan-v1-20261028','summary.json');cat=copy.deepcopy(take(PREFIX+'activation-plan-v1-20261028','private-catalogue-draft.json'));uids=sorted(plan['uids']);models={r['uid']:r for r in cat['models']};assert sorted(models)==uids
 identity=take(PREFIX+'identity-boundary-reviews-v1-20261028','summary.json');assert identity['allSixteenSourceAssociationsQualified'];roles=take(PREFIX+'remaining-interface-reviews-v1-20261028','summary.json');assert len(roles['boundedInterfaceReviews'])==14
 graph=take(PREFIX+'current-support-provenance-v1-20261028','actor-graph.json');edges={}
 for uid in uids:
  rows=[r for r in graph['edges']if r['uid']==uid];assert len(rows)==4 and len({tuple(r['providers'])for r in rows})==1;edges[uid]=rows[0]['providers']
 rex_batch=PREFIX+'rex-surveyed-podium-support-v1-20261028';rex=take(rex_batch,'result.json');old=take(rex_batch,'support-attributes.json.gz');b=old['currentForm'];tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');actual=next(x for x in read(tile)['buildings']if x['uid']==b['uid']);assert actual==b;refs.append(tile)
 inp=out/'rex-capture-input.json';save(inp,dict(uid=b['uid'],csuid=b['buildingCSUID'],building=actual,refs=[dict(path=str(tile.relative_to(ROOT)),sha256=digest(tile.read_bytes()))]));capture=HERE/'capture_current_surveyed_support_v1.mjs';refs.extend([capture,HERE/'surveyed_fallback_support_geometry_v1.mjs']);subprocess.run(['node',str(capture),str(inp.relative_to(ROOT)),str((out/'rex-current-attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);fresh=read(out/'rex-current-attributes.json.gz');assert fresh['position']==old['position']and fresh['index']==old['index'];assert rex['supportBasicBeforeAfterClear']and all(r['canonicalContacts']==r['samples']==49 and r['stillUnresolved']==0 for r in rex['rows'])
 for path,sha in fresh['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 for uid,e in models.items():
  assert e['activationGroup']==uids and not e.get('supportDependencies');deps=[]
  for provider in edges[uid]:
   if provider=='drawn-terrain':continue
   if provider in models:deps.append(dict(uid=provider,state='candidate',csuid=models[provider]['buildingCSUID']))
   else:
    assert uid=='landsd/173764:0'and provider==b['uid']=='landsd/228592:0';deps.append(dict(uid=provider,state='surveyed-footprint-fallback',csuid=b['buildingCSUID']))
    e['retainedBasicSupportDependencies']=[dict(uid=uid,supportUid=provider,supportCSUID=b['buildingCSUID'],dependencyMode='retained-current-basic-podium',currentBasicForm=actual,currentBasicFormSHA256=digest(jobs.encode(actual).encode()),completeIndexedBasicGeometrySHA256=digest(jobs.encode(dict(position=fresh['position'],index=fresh['index'])).encode()),supportEvidence=dict(path=str((BASE/rex_batch/'contacts.json.gz').relative_to(ROOT)),sha256=digest((BASE/rex_batch/'contacts.json.gz').read_bytes())),sourceSHA256=e['sha256'],mustRemainBasicAndUnsuppressed=True,futureReplacementRequiresDependentRevalidation=True)]
  e['supportDependencies']=deps
 def visit(uid,active,done):
  if uid in done:return
  assert uid not in active;active.add(uid)
  for d in models[uid]['supportDependencies']:
   if d['state']=='candidate':visit(d['uid'],active,done)
  active.remove(uid);done.add(uid)
 for uid in uids:visit(uid,set(),set())
 retained=module('retained_support_fixture',HERE.parent/'island-detail-integration/retained_basic_support.py');checks=retained.validate_retained_basic_support(cat['models'],{b['uid']:actual});assert len(checks)==1
 oldfixture=PREFIX+'full-scene-preview-fixture-v2-20261028';fi=take(oldfixture,'fixture-inputs.json');cfgpath=ROOT/fi['configPath'];assert digest(cfgpath.read_bytes())==pins[oldfixture][str(cfgpath.relative_to(ROOT))];cfg=copy.deepcopy(read(cfgpath));refs.append(cfgpath)
 for e in cat['models']:
  path=ROOT/cfg['stage']/e['asset'];raw=path.read_bytes();assert digest(raw)==e['sha256'];dest=local/e['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);refs.extend([path,dest])
 save(local/'catalogue.json',cat);forms=ROOT/cfg['stage']/'source-forms.json';refs.append(forms);save(local/'source-forms.json',read(forms));cfg.update(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',failureTestUids=uids);save(local/'config.json',cfg)
 preflight=HERE/'private_original_catalogue_preflight_v1_20261028.mjs';refs.append(preflight);subprocess.run(['node',str(preflight),str((local/'catalogue.json').relative_to(ROOT)),'http://127.0.0.1:4177/'+cfg['catalogueURL']],cwd=ROOT,check=True)
 save(out/'fixture-inputs.json',dict(resources=sorted(resources),configPath=str((local/'config.json').relative_to(ROOT)),uids=uids,currentManifestSHA256=fi['currentManifestSHA256'],physicalSupportProviders=edges,retainedBasicSupportChecks=checks,diagnosticOnly=True,publication=False))
 refs.extend([local/'catalogue.json',local/'source-forms.json',local/'config.json']);result=dict(uids=uids,supportProviderMetadataBound=True,allFourWorldProviderSetsAgree=True,nativeSupportGraphAcyclic=True,rexFreshProductionGeometryMatchesReviewed=True,retainedBasicSupportChecks=checks,activationGroup=uids,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAccepted=False,installationApproved=False,publication=False,qualification='Exact reviewed provider graph is bound as native candidate or retained surveyed BASIC support metadata for private runtime testing. Every actual source association/interface review remains separate. Current Rex form/CSUID and complete production geometry match its reviewed49/49support in all4worlds. Existing retention validator passes. No dependency/whole-group/publication acceptance follows until real browser and final publisher checks.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 module('supported_activation_fixture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'private-original-atomic-availability-and-exact-current-support-metadata-fixture',list(dict.fromkeys(refs)),read(out/'summary.json'))
if __name__=='__main__':main()

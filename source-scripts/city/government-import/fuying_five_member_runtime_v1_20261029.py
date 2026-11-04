"""Capture actual rendered ground for the private whole-parent five-node group."""
from pathlib import Path
from copy import deepcopy
import json,shutil,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import fuying_whole_parent_five_boundary_v1_20261029 as boundary
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-member-runtime-v1-20261029';PATCH='government-xl-fuying181489-five-member-boundary-contract-v2-20261029';CAP='government-xl-fuying-peninsula-after-depot-current-v1-20261029-selection';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();_,pp=authenticate(BASE/PATCH);_,cp=authenticate(BASE/CAP);refs=[Path(__file__),HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',BASE/PATCH/'result.json',BASE/CAP/'result.json']
 def take(p,pins):assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 proof=take(BASE/PATCH/'summary.json',pp);assert proof['allTerrainValidatorsPassed']and proof['allFiveEffectiveMembersVerified'];wanted=set(proof['completeTargetObligations']);assert len(wanted)==6 and proof['uids']==['landsd/181489:0']
 patches=[take(ROOT/m['candidate']['path'],pp)for m in proof['members']]
 with boundary.private_validator():boundary.validate_effective_coordinated_members(patches)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestref=ref(manifestpath);refs.append(manifestpath);models={}
 for url in manifest['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url
  for m in read(path)['models']:
   if m['uid']in wanted:assert m['uid']not in models;models[m['uid']]=(deepcopy(m),path)
 assert set(models)==wanted-{'landsd/181489:0'}
 current=take(BASE/CAP/'selection.json.gz',cp);row=deepcopy(next(r for r in current['rows']if r['uid']=='landsd/181489:0'));rows=[row]
 for uid,(entry,catalogue)in sorted(models.items()):
  tile=entry['sourceTile'];path=ROOT/'3d-viewer'/tile;building=[b for b in read(path)['buildings']if b['uid']==uid];assert len(building)==1;asset=catalogue.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];refs.extend([catalogue,path,asset])
  rows.append(dict(uid=uid,sourceSHA256=entry['sha256'],originalGeometryOnly=True,candidate=dict(entry=entry,path=str(asset.relative_to(ROOT))),source=dict(tile=tile,tileSHA256=digest(path.read_bytes()),building=building[0])))
 DOC.mkdir();names=set()
 for row in rows:
  b=row['source'];tile=ROOT/'3d-viewer'/b['tile'];assert [f for f in read(tile)['buildings']if f['uid']==row['uid']]==[b['building']];assert digest(tile.read_bytes())==b['tileSHA256'];refs.append(tile)
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']==row['candidate']['entry']['sha256'];refs.append(asset)
  name=row['candidate']['entry']['asset'];assert name not in names;names.add(name);dest=LOCAL/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest);refs.append(dest);row['candidate']['path']=str(dest.relative_to(ROOT))
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestref['sha256']))
 old=proof['oldParent'];oldpath=ROOT/old['path'];assert ref(oldpath)==old;oldnode=read(oldpath);refs.append(oldpath);url=str(oldpath.relative_to(ROOT/'3d-viewer'));assert sum(m['url']==url for m in manifest['terrainPatches'])==1
 candidates=[]
 for i,(member,patch)in enumerate(zip(proof['members'],patches)):
  item=dict(**member['candidate'],uids=sorted(wanted),triangles=len(patch['nativeMesh']['index'])//3)
  if i==0:item['replaces']=dict(url=url,sha256=old['sha256'],retainedUids=oldnode['meta']['targetUids'])
  candidates.append(item)
 save(DOC/'terrain-candidates.json',candidates);before={ref(p)['path']:ref(p)['sha256']for p in refs};tool=HERE/'acceptance_metrics_multi_retained_v2.mjs'
 command=['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with(DOC/'worker.log').open('w')as log:process=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'command.json',dict(command=command,exitCode=process.returncode));assert process.returncode==0 and reservations.owns(lease);metrics=read(DOC/'metrics.json');assert len(metrics['rows'])==6 and {r['uid']for r in metrics['rows']}==wanted
 for path,sha in {**before,**metrics['inputHashes']}.items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 assert ref(manifestpath)==manifestref
 result=dict(uids=sorted(wanted),terrainEditOwnerUids=proof['uids'],sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},rows=metrics['rows'],allSixOriginalsCaptured=not any('error'in r for r in metrics['rows']),fiveTerrainMembers=True,wholeOldParentRemovedExactlyOnce=True,sourceGeometryChanges=0,sourcePoseChanges=0,publication=False,installationApproved=False,physicalAcceptance=False,qualification='Actual production renderer draw, highest-surface sampler and original asset decoder capture only. Full6source four-world foundations, affected whole-domain BASIC/native regressions, continuous-source floors, identity/physical/browser and dedicated publisher integration remain pending. No old acceptance transfer.')
 save(DOC/'summary.json',result);refs.extend([tool,LOCAL/'runtime-geometry.json.gz']);module('fuying_five_runtime_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-five-effective-terrain-nodes-six-original-source-runtime-capture',refs,result);print(dict(captured=6,errors=sum('error'in r for r in metrics['rows'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();proof=read(BASE/PATCH/'summary.json');keys=['building:'+u for u in proof['completeTargetObligations']]+['terrain:city/data/terrain.json','terrain:city/data/government-native-fu-wong-original-v1-20261023.json'];claim=reservations.claim('fuying-five-runtime-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

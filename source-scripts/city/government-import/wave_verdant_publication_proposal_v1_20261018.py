"""Concrete original assembly publisher dry run; deliberately unapproved/unpublished."""
from pathlib import Path
import shutil,sys
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave301562-reviewed-underside-v1-20261018';BATCH='government-xl-wave-verdant-publication-proposal-v1-20261018';DOC=BASE/BATCH;STAGE=HERE/'local'/BATCH;OLD=HERE/'local/government-xl-wave-verdant-private-browser-v5-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()and not STAGE.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 cat=read(OLD/'catalogue.json');manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);sources={}
 for name,file,key in [('government-xl-wave-all-original-support-distance-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-podium-support-v1-20261017','support-inputs.json','sources'),('government-xl-wave-verdant-block2-original-recovery-v1-20261017','selection.json.gz','rows'),('government-xl-wave-verdant-194544-original-recovery-v1-20261017','selection.json.gz','rows')]:
  p=BASE/name/file;refs.append(p);sources.update({x['uid']:x for x in read(p)[key]})
 for m in cat['models']:
  row=sources[m['uid']];m['originalSourceKey']=row['native']['cacheKey']+'/'+row['native']['model']['modelId'];assert m['publicationApproved']is False and m['placementReviewed']is False
  dest=STAGE/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(OLD/m['asset'],dest);assert digest(dest.read_bytes())==m['sha256']
 save(STAGE/'catalogue.json',cat);save(STAGE/'catalogue-index.json',dict(models=len(cat['models']),catalogues=['catalogue.json']));shutil.copyfile(OLD/'source-forms.json',STAGE/'source-forms.json')
 candidate=read(BASE/'government-xl-wave-verdant-current-terrain-rebind-v5-20261018/terrain-candidates.json')[0];terrainpath=ROOT/candidate['path'];assert digest(terrainpath.read_bytes())==candidate['sha256'];terrain=read(terrainpath);terrainentry=dict(source=candidate['path'],sha256=candidate['sha256'],destination='city/data/government-wave-verdant-original-v1-20261018.json',resolution=terrain['cell'],area='Wave and Verdant original source terrain')
 estimates=[];foundations=[];updates=read(BASE/'government-xl-wave-multicore-private-basic-estimates-v4-20261017/geometry.json.gz')['rows']
 for x in updates:
  before=x['sourceBefore'];after=x['privateAfter'];found=[]
  for t in manifest['tiles']:
   if not(t['bounds'][0]<=before['centre'][0]<=t['bounds'][2] and t['bounds'][1]<=before['centre'][1]<=t['bounds'][3]):continue
   p=ROOT/'3d-viewer'/t['url'];found.extend((t,p,b)for b in read(p)['buildings']if b['uid']==x['uid'])
  assert len(found)==1;tile,path,current=found[0];assert current==before;refs.append(path)
  if 'foundationBase'in after and after.get('foundationBase')!=before.get('foundationBase'):
   assert x['uid']=='landsd/268957:0';partsfile=BASE/'government-xl-wave-multicore-private-basic-estimates-v4-20261017/268957:0-parts.json';parts=read(partsfile)['parts'];posts=[p for p in parts if p['kind']!='roof'];roofs=[p for p in parts if p['kind']=='roof'];assert posts and roofs and all(p['fullTerrainCoverage']and p['baseReachesAllGround']and p['roofOrTopClear']for p in posts)and all(p['fullTerrainCoverage']and p['roofOrTopClear']for p in roofs)
   proof=STAGE/'illustrative-foundation-proof.json';proposal=STAGE/'illustrative-foundation-proposal.json';save(proof,dict(uid=x['uid'],fullPostFootprintsMeetGround=True,wholeRoofClear=True,rawParts=parts,sourceEvidence=ref(partsfile),fullAcceptance=False));save(proposal,dict(uid=x['uid'],foundationBase=after['foundationBase'],originalBase=before['base']));foundations.append(dict(uid=x['uid'],tile=tile['url'],tileSHA256=digest(path.read_bytes()),before=before,foundationBase=after['foundationBase'],evidence=ref(proof),proposal=ref(proposal)));refs.append(partsfile)
  else:
   assert {k for k in set(before)|set(after)if before.get(k)!=after.get(k)}=={'base'};estimates.append(dict(uid=x['uid'],objectId=before['objectId'],buildingCSUID=before['buildingCSUID'],baseSource=before['baseSource'],previousBase=before['base'],base=after['base'],height=before['height']))
 assert len(estimates)==2 and len(foundations)==1
 save(STAGE/'estimated-bases.json',dict(parentSha256=digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()),refinementSha256=candidate['sha256'],buildings=estimates))
 url='city/data/official-models/government-wave-verdant-original-v1-20261018/catalogue.json';plan=dict(areas=[dict(area='Nine unchanged Wave and Verdant originals',catalogue=str((STAGE/'catalogue.json').relative_to(ROOT)),destination=url,estimates=[str((STAGE/'estimated-bases.json').relative_to(ROOT))])],topLevelTerrainPatches=[terrainentry],illustrativeFoundations=foundations);save(STAGE/'plan.json',plan)
 pub=module('wave_assembly_dry_publisher',HERE.parent/'island-detail-integration/publish.py');pub.DOC=DOC/'publisher-dry-run';sys.argv=['publish.py',str((STAGE/'plan.json').relative_to(ROOT))];pub.main();dry=read(pub.DOC/'publication-plan.json');assert not dry['published'];assert len(dry['estimatedBases'])==2 and len(dry['illustrativeFoundations'])==1;assert read(manifestpath)==manifest
 save(DOC/'summary.json',dict(publisherDryRunPassed=True,models=9,estimatedBases=2,illustrativeFoundations=1,plannedEdits=dry['after'],currentManifest=ref(manifestpath),publicationApproved=False,fullAcceptance=False,qualification='Concrete dry run only. Catalogue approval flags remain false; source/whole-assembly qualification and live rollback/ledger verification are required before apply.'))
 refs.extend([HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/illustrative_foundations.py',manifestpath,*[ROOT/p for p in pins],*[p for p in STAGE.rglob('*')if p.is_file()]])
 out=module('wave_proposal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'nine-original-concrete-publisher-proposal-v1',list(set(refs)),dict(uids=[m['uid']for m in cat['models']],publisherDryRunPassed=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()

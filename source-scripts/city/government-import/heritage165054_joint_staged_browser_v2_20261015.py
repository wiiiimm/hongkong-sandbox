"""Leased staged browser checks for immutable Museum, terrain and BASIC estimate."""
from pathlib import Path
import json,os,subprocess,sys,uuid,hashlib
from urllib.request import urlopen
import heritage165054_joint_private_stage_v1_20261015 as stage
from run import reservations,connect
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
ROOT=stage.ROOT;HERE=stage.HERE;BASE=stage.BASE;read=stage.read;save=stage.save;ref=stage.ref;check=stage.check
BATCH='government-xl-heritage165054-joint-staged-browser-v2-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';BROWSER=HERE/'heritage165054_joint_original_browser_v1_20261015.mjs'
JOB='908612b5fc795b9e9751dcd383345ffb91e0b78d6f3abf964babe1ab8d9646fa'
def load():
 r=read(stage.DOC/'result.json');v=read(stage.DOC/'ROOT-VERIFIED.json');assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased']
 refs=distinct_refs(r['evidenceRefs']+[ref(stage.DOC/'result.json'),ref(stage.DOC/'ROOT-VERIFIED.json'),ref(Path(__file__)),ref(BROWSER),ref(ROOT/'3d-viewer/city/app.js')])
 for q in refs:check(q)
 return r,refs

def owned():
 from publication_lock import locked_publication
 with locked_publication(ROOT):
  lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();r,refs=load()
  def fence():
   assert reservations.owns(lease)
   for q in refs:check(q)
  fence()
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',r)
  for name in ['city/app.js','city/data/manifest.json']:
   with urlopen('http://127.0.0.1:4176/'+name,timeout=20)as response:assert response.status==200 and hashlib.sha256(response.read()).hexdigest()==ref(ROOT/'3d-viewer'/name)['sha256']
  DOC.mkdir();config=read(stage.STAGE/'browser-config.json');config['doc']=str(DOC.relative_to(ROOT))+'/';config['captureDirectionByModel']={stage.UID:[.2,.55,-.8]}
  pub=stage.original.prior.module(HERE.parent/'island-detail-integration/publish.py','heritage_browser_encode');tile=ROOT/'3d-viewer/city/data/tiles/1_-6.json';data=read(tile);estimate=read(stage.STAGE/'estimated-bases.json')['buildings'][0];b=next(b for b in data['buildings']if b['uid']==estimate['uid']);assert b['base']==estimate['previousBase']and b['height']==estimate['height']and b['baseHeightHKPD']is None and b['topHeightHKPD']is None;b['base']=estimate['base']
  raw=pub.encoded(data);expected=read(stage.DOC/'publisher-dry-run/publication-plan.json')['after'][str(tile.relative_to(ROOT))];assert hashlib.sha256(raw).hexdigest()==expected
  tile_out=LOCAL/'estimated-tile-1_-6.json';tile_out.write_bytes(raw);config['estimatedTileOverrides']=[dict(url='city/data/tiles/1_-6.json',source=str(tile_out.relative_to(ROOT)),sha256=expected,bytes=len(raw))];save(LOCAL/'browser-config.json',config)
  refs=distinct_refs(refs+[ref(tile_out),ref(LOCAL/'browser-config.json'),ref(tile)]);fence()
  command=['node',str(BROWSER),'staged',str((LOCAL/'browser-config.json').relative_to(ROOT))];p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,env={**os.environ,'CHROME_PATH':os.environ.get('CHROME_PATH','/opt/google/chrome/chrome')});save(DOC/'command.json',dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));fence();assert p.returncode==0,p.stderr
  report=stage.original.prior.module(HERE/'integrate.py','heritage_browser_contract').browser_verified(DOC/'staged-browser.json',{stage.UID});views=[v for v in report['views']if 'time'in v];assert len(views)==4
  for v in views:
   assert v['fullyFramed']and v['selectionClosed']and v['solidAppearance']and v['originalTriangles']==15140 and v['sourceSHA256']==stage.original.SOURCE and v['fallbackFaces']==0
   assert v['retained']['landsd/128971:0']['base']==estimate['base']and all(not x for x in v['wireframeFlags'])and all(x==1 for x in v['materialOpacities'])
  save(DOC/'staged-acceptance.json',dict(passed=True,stage=ref(stage.DOC/'result.json'),browser=ref(DOC/'staged-browser.json'),exactPublisherTileBytes=ref(tile_out),views=[ref(DOC/v['file'])for v in views],sourceGeometryChanges=0,publication=False,newlyInstalled=0,ROOTActuallyInspectedExportedImages=False,liveBrowserStillRequired=True))
  refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence();stage.original.prior.module(stage.original.prior.old.FREEZER,'heritage_browser_freezer').freeze(BATCH,'solid-joint-staged-desktop-mobile-picking-collision-retry-no-install',[check(q)for q in refs],dict(uids=[stage.UID],sourceOnly=True,physicalAccepted=False,newlyInstalled=0))

def main():
 if '--owned'in sys.argv:return owned()
 assert sys.argv[1:]==['--staged-only']and not DOC.exists()and not LOCAL.exists();load();forms=read(stage.shelter.capture.DOC/'input.json.gz')['currentForms'];keys=reservations.normalise([r for r in stage.shelter.capture.resources([f['building']['uid']for f in forms])if not r.startswith('immutable-source-proof:')]+['immutable-source-proof:'+BATCH]);c=reservations.claim('heritage-staged-browser-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert c['ok'];lease=c['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

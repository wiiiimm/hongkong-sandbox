"""Bind and review three unchanged La Marina originals; no installation approval."""
import argparse,sys,uuid,subprocess
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-la-marina-three-original-assembly-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';PRIOR='government-xl-six-two-case-recovery-311761-0-contacts-v1-20261028';UIDS={'landsd/311761:0','landsd/311762:0','landsd/315025:0'}
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and{'building:'+u for u in UIDS}<=set(lease['resources'])and not DOC.exists();receipt,pins=authenticate(BASE/PRIOR);path=BASE/PRIOR/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];old=read(path);inventory=BASE/'government-xl-unfinished-territorial-neighbour-inventory-v1-20261028';_,ip=authenticate(inventory);inv=inventory/'summary.json';assert digest(inv.read_bytes())==ip[str(inv.relative_to(ROOT))];target=next(r for r in read(inv)['rows']if r['uid']==old['targetUid']);sources={target['uid']:target};sources.update({r['uid']:r for r in target['nearbyOriginalCandidates']if r['uid']in UIDS});assert set(sources)==UIDS
 manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);forms={};refs=[Path(__file__),BASE/PRIOR/'result.json',path,inventory/'result.json',inv,manifest]
 for tile in m['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid']in UIDS:assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes()));refs.append(p)
 assert set(forms)==UIDS;rows=[]
 for uid,r in sorted(sources.items()):
  key,mid=r['sourceKey'].split('/',1)
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==r['nativeResultSHA256'];model=next(x for x in native['models']if x['modelId']==mid)
  entry=deepcopy(model['candidate']);assert entry['uid']==uid and entry['sha256']==r['indexedSourceSHA256'];b=forms[uid]['building'];assert entry['objectId']==b['objectId']and entry['buildingCSUID']==b['buildingCSUID'];assert not any(entry.get(k)for k in ['identityReviewApproved','placementReviewed','publicationApproved'])
  matches=[ROOT/x['path']for x in receipt['evidenceRefs']if x['sha256']==entry['sha256']and x['path'].endswith('.glb.gz')];asset=next(p for p in matches if p.exists());assert digest(asset.read_bytes())==entry['sha256'];refs.append(asset)
  entry.update(proceduralWindows=False,rootTranslation=[-834500,0,816500],sourceTile=r['sheet'],sourceBaseHeight=b['baseHeightHKPD'],sourceTopHeight=b['topHeightHKPD']);rows.append(dict(uid=uid,modelId=mid,triangles=model['triangles'],sourceSHA256=entry['sha256'],originalGeometryOnly=True,source=forms[uid],native=dict(cacheKey=key,resultSha=sha,model=model),candidate=dict(path=str(asset.relative_to(ROOT)),entry=entry)))
 for url in m['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;assert not UIDS&{e['uid']for e in read(p)['models']};refs.append(p)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest(manifest.read_bytes())));module('la_marina_assembly_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-original-assembly-selection-no-approval',refs,dict(uids=sorted(UIDS),sourceGeometryChanges=0,identityAccepted=False,installationApproved=False))
 for script,suffix in [('selected_original_identity_v3_20261023.py','identity'),('selected_original_current_capture_v3.py','runtime')]:
  command=[sys.executable,str(HERE/script),'--batch',BATCH+'-'+suffix,'--capture',BATCH]
  if suffix=='runtime':
   for uid in sorted(UIDS):command+=['--uid',uid]
  with (LOCAL/(suffix+'.log')).open('w')as stream:proc=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
  assert proc.returncode==0,(suffix,'preserved-failure-no-approval');assert reservations.owns(lease)
 print('Three-original identity and actual current-runtime diagnostics complete; no installation credit',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('la-marina-three-original-assembly-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()

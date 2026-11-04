"""Bounded grouped recovery of six required original neighbours, no modelling.

Reuse existing sheet acquisition and exact canonical-byte converter. No approvals.
"""
import argparse,json,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-six-neighbours-two-cases-recovery-v1-20261028';LOCAL=HERE/'local'/BATCH;DOC=BASE/BATCH;LEASE=LOCAL/'reservation.json';INVENTORY='government-xl-unfinished-territorial-neighbour-inventory-v1-20261028';PRIOR='government-xl-cross-sheet-cached-contacts-controller-v1-20261028';TARGETS={'landsd/'+str(n)+':0'for n in[311761,264206]}
def plan():
 authenticate(BASE/INVENTORY);authenticate(BASE/PRIOR);inventory=read(BASE/INVENTORY/'summary.json');prior=read(BASE/PRIOR/'summary.json');rows={r['uid']:r for r in inventory['rows']if r['uid']};selected={};refs=[BASE/INVENTORY/'result.json',BASE/PRIOR/'result.json']
 for item in prior['completed']:
  if item['uid']not in TARGETS:continue
  receipt=ROOT/item['receipt'];authenticate(receipt.parent);refs.append(receipt)
  for missing in read(receipt.parent/'summary.json')['missingCachedSources']:
   row=next(r for r in rows[item['uid']]['nearbyOriginalCandidates']if r['sourceKey']==missing['sourceKey']);assert row['uid']and row['indexedSourceSHA256']==missing['sha256'];selected[row['sourceKey']]=row
 assert len(selected)==6
 return list(selected.values()),refs

def owned():
 lease=read(LEASE);assert reservations.owns(lease);items,refs=plan();assert {'building:'+r['uid']for r in items}<=set(lease['resources']);assert not DOC.exists()and shutil.disk_usage(ROOT).free>=3*1024**3;manifest=read(ROOT/'3d-viewer/city/data/manifest.json');wanted={r['uid']for r in items};forms={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];data=read(path)
  for b in data['buildings']:
   if b['uid']in wanted:assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes()))
 native=[];skipped=[];packed=0;decoded=0
 for row in items:
  uid=row['uid'];key,mid=row['sourceKey'].split('/',1)
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert record and record[0]==row['nativeResultSHA256'];model=next(m for m in record[1]['models']if m['modelId']==mid)
  entry=model['candidate'];assert entry['uid']==uid and entry['sha256']==row['indexedSourceSHA256'];form=forms.get(uid);b=form['building']if form else{};matches=[v for v in model.get('matching',{}).get('viewerMatches',[])if v['uid']==uid]
  if len(matches)!=1 or not form or any(b.get(k)!=entry.get(v)for k,v in[('objectId','objectId'),('buildingCSUID','buildingCSUID'),('baseHeightHKPD','recordedBaseHeight'),('topHeightHKPD','recordedTopHeight')]):skipped.append(dict(uid=uid,sourceKey=row['sourceKey'],reason='current-form-or-source-match-differs-no-guessed-input'));continue
  if entry['bytes']>1024**2 or entry['glbBytes']>20*1024**2:skipped.append(dict(uid=uid,sourceKey=row['sourceKey'],reason='outside-bounded-asset-size'));continue
  packed+=entry['bytes'];decoded+=entry['glbBytes'];native.append(dict(sheet=row['sheet'],cacheKey=key,resultSha=row['nativeResultSHA256'],model=model));refs.append(ROOT/'3d-viewer'/form['tile'])
 assert packed<=20*1024**2 and decoded<=128*1024**2
 selected_uids=[n['model']['candidate']['uid']for n in native];inp=LOCAL/'recovery-inputs.json.gz';save(inp,dict(nativeRun=NATIVE_RUN,rows=selected_uids,sources={u:forms[u]for u in selected_uids},native=native));refs.extend([Path(__file__),inp,Path(shape_prepare.__file__)])
 prepared=shape_prepare.prepare(inp,LOCAL/'recovered',allow_source=True,workers=1,env_file=ROOT/'.env.modelling',reservation_receipt=lease)if native else dict(errors={},methods={});recovered=[]
 for n in native:
  e=n['model']['candidate'];asset=LOCAL/'recovered/assets'/(e['sha256']+'.glb.gz')
  if not asset.exists()or e['uid']in prepared['errors']:continue
  assert digest(asset.read_bytes())==e['sha256']and asset.stat().st_size==e['bytes'];refs.append(asset);recovered.append(dict(uid=e['uid'],sourceKey=n['cacheKey']+'/'+n['model']['modelId'],sourceSHA256=e['sha256'],triangles=n['model']['triangles'],sourceAsset=dict(path=str(asset.relative_to(ROOT)),sha256=e['sha256']),candidate=e))
 for name in['geometry-inputs.json','source-metadata.json']:
  path=LOCAL/'recovered'/name
  if path.exists():refs.append(path)
 for path in(LOCAL/'recovered/sheets').glob('*/recovery.json'):refs.append(path)
 result=dict(uids=sorted(wanted),requested=6,recovered=recovered,recoveredCount=len(recovered),skipped=skipped,errors=prepared['errors'],methods=prepared['methods'],packedSourceBytes=packed,originalGLBBytes=decoded,sheets=len({r['sheet']for r in native}),workers=1,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Bounded acquisition/conversion only; each packed original must equal the pinned native-stage SHA and bytes. Shared per-sheet acquisition, single compute worker. Current viewer identity metadata checked only to recover correct source inputs, not accepted for installation. No geometry simplification/edit, model-review approval, production queue, terrain or catalogue write.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('grouped_exact_original_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-six-originals-grouped-source-recovery',refs,result);print(dict(requested=6,recovered=len(recovered),skipped=len(skipped),errors=prepared['errors']),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();items,_=plan();c=reservations.claim('bounded-six-original-source-recovery-'+str(uuid.uuid4()),sorted({'building:'+r['uid']for r in items}),batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()

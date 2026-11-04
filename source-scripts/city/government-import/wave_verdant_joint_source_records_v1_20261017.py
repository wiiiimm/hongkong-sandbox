"""Bind all proposed original assets to exact current official source records; no placement waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
from wave_verdant_assembly_four_worlds_v1_20261017 import UIDS
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave-verdant-joint-source-records-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json',HERE/'wave_verdant_assembly_four_worlds_v1_20261017.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 sources={r['uid']:r for r in read(BASE/'government-xl-wave-all-original-support-distance-v1-20261017/support-inputs.json')['sources']};sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-podium-support-v1-20261017/support-inputs.json')['sources']});sources.update({r['uid']:r for r in read(BASE/'government-xl-wave-verdant-block2-original-recovery-v1-20261017/selection.json.gz')['rows']});rows=[];cached={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for uid in UIDS:
   r=sources[uid];n=r['native'];key=n['cacheKey']
   if key not in cached:cached[key]=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone()
   sha,data=cached[key];assert sha==n['resultSha'];models=[m for m in data['models']if m['modelId']==n['model']['modelId']];assert models==[n['model']];m=models[0];b=r['source']['building'];tile=ROOT/'3d-viewer'/r['source']['tile'];assert b in read(tile)['buildings'];asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']==m['asset']['sha256']and len(raw)==m['asset']['bytes'];assert m['modelId'][1:11]==b['buildingCSUID'][:10]
   official=[v for v in m['matching']['officialMatches']if v['objectId']==b['objectId']and v['buildingCSUID']==b['buildingCSUID']];viewer=[v for v in m['matching']['viewerMatches']if v['uid']==uid and v['objectId']==b['objectId']and v['buildingCSUID']==b['buildingCSUID']];assert len(official)==len(viewer)==1
   for v in official+viewer:assert v['overlapOfSmallerFootprint']>=.5 and v['footprintCentroidDistanceMetres']<=10
   rows.append(dict(uid=uid,modelId=m['modelId'],sourceSHA256=r['sourceSHA256'],buildingCSUID=b['buildingCSUID'],objectId=b['objectId'],cacheKey=key,resultSha=sha,officialMatch=official[0],viewerMatch=viewer[0],assetBytes=len(raw),triangles=m['triangles'],exactCurrentSourceRecordMatch=True));refs.extend([asset,tile])
 save(DOC/'source-records.json',dict(rows=rows,nativeRun=NATIVE_RUN,fullAcceptance=False,publicationApproved=False,qualification='Exact current CSUID/objectId/viewer part, byte-identical original asset and pinned native-stage record under existing matching gates. Establishes source-record correspondence only; source-specific component interpretation, all placement/support/collision/runtime/browser acceptance remain separate. No proposed landmark aliases approved.'))
 out=module('joint_source_records_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-exact-current-source-record-bindings-v1',list(set(refs)),dict(uids=UIDS,exactSourceRecordMatches=len(rows),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],exactSourceRecordMatches=len(rows)),flush=True)
if __name__=='__main__':main()

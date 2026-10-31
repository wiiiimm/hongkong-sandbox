"""Recover two exact original Tai Fu and Tai Wing neighbours, never remodel or publish."""
import sys,json,uuid,tarfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tai-kwei-neighbour-originals-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/201002:0','landsd/209728:0'];CACHE=HERE/'local/tai-kwei-neighbours-source-lookup-20261017/sheet.json.gz'
def main():
 assert not DOC.exists();cached=read(CACHE);key=cached['cacheKey']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone()==(cached['resultSHA256'],cached['result'])
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest.read_bytes());tile='city/data/tiles/0_-2.json';path=ROOT/'3d-viewer'/tile;forms={b['uid']:b for b in read(path)['buildings']};sources={u:dict(building=forms[u],tile=tile,tileSHA256=digest(path.read_bytes()))for u in UIDS};native=[]
  for u in UIDS:
   matches=[m for m in cached['result']['models']if any(v['uid']==u for v in m.get('matching',{}).get('viewerMatches',[]))];assert len(matches)==1;m=matches[0];assert m['candidate']['buildingCSUID']==forms[u]['buildingCSUID'];native.append(dict(cacheKey=key,resultSha=cached['resultSHA256'],sheet='11-NW-19A',model=m))
  save(LOCAL/'recovery-inputs.json.gz',dict(nativeRun=NATIVE_RUN,rows=UIDS,sources=sources,native=native));recovered=LOCAL/'recovered';assets=recovered/'assets';assets.mkdir(parents=True);needed={o['model']['asset']['sha256']:o for o in native};refs=[Path(__file__),CACHE,manifest,path,LOCAL/'recovery-inputs.json.gz'];cache_hits=[]
  for artifact in cached['result']['artifacts']:
   if artifact.get('kind')!='original-and-prepared-sheet':continue
   for bundle in (HERE/'local').rglob(artifact['sha256']+'.tar.gz'):
    if bundle.stat().st_size!=artifact['bytes']or digest(bundle.read_bytes())!=artifact['sha256']:continue
    with tarfile.open(bundle,'r:gz')as tar:
     for member in tar:
      h=Path(member.name).name.removesuffix('.glb.gz')
      if h not in needed:continue
      assert member.isfile()and member.size==needed[h]['model']['asset']['bytes'];raw=shape_prepare.canonical_bytes(tar.extractfile(member).read(),h);(assets/(h+'.glb.gz')).write_bytes(raw);cache_hits.append(h)
    refs.append(bundle)
    if all((assets/(h+'.glb.gz')).exists()for h in needed):break
  result=shape_prepare.prepare(LOCAL/'recovery-inputs.json.gz',recovered,allow_source=True,workers=1,env_file=ROOT/'.env.modelling',reservation_receipt=lease);assert not result['errors'],result['errors'];rows=[]
  for u,o in zip(UIDS,native):
   p=assets/(o['model']['asset']['sha256']+'.glb.gz');assert digest(p.read_bytes())==o['model']['asset']['sha256'];refs.append(p);entry=shape_prepare.entry(o,forms[u]);rows.append(dict(uid=u,name=forms[u].get('name'),modelId=o['model']['modelId'],sourceSHA256=entry['sha256'],triangles=o['model']['triangles'],native=o,source=sources[u],candidate=dict(entry=entry,path=str(p.relative_to(ROOT))),currentReview=None))
  assert reservations.owns(lease)and digest(manifest.read_bytes())==manifest_sha and digest(path.read_bytes())==sources[UIDS[0]]['tileSHA256'];save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifest_sha));save(DOC/'recovery.json',dict(result=result,localBundleRecoveredHashes=cache_hits,modelGeometryChanges=0))
  refs.extend(p for p in recovered.rglob('*.json')if p.is_file());refs.append(Path(shape_prepare.__file__))
  out=module('tai_kwei_neighbour_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-two-exact-neighbour-source-acquisition-v1',refs,dict(uids=UIDS,recovered=len(rows),triangles={r['uid']:r['triangles']for r in rows},fullAcceptance=False,nextStep='Compare complete Tai Kwei source against both exact neighbouring originals; identity and collision review remain pending, no installation credit.'))
  print(dict(jobId=out['jobId'],recovered=len(rows),methods=result['methods']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

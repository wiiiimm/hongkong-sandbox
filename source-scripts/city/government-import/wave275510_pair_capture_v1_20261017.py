"""Current unchanged Wave tower/podium capture without proposing terrain edits."""
import subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from require_remaining_xl import require_remaining
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-wave275510-pair-capture-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
COUNT=BASE/'government-xl-namcheong244683-original-installed-v1-20261017/full-xl-current-count.json'
SOURCES={'landsd/275510:0':'152e3667ea93adab7659b3bcb714ae96f3c67dbf7db213f572ef3383245f32c6','landsd/301560:0':'34d84bcd05b196cd38f559bcef2b9a6b1df68017b2999a1487333908fc8dad04'}
def main():
 assert not DOC.exists()and not LOCAL.exists();require_remaining(COUNT,'landsd/275510:0',SOURCES['landsd/275510:0']);claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in SOURCES],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  inputs=[BASE/'government-xl-wave275510-current-capture-v1-20261017/selection.json.gz',BASE/'government-xl-four-qualified-original-podiums-physical-20261007-301560-0/selection.json.gz'];rows=[read(p)['rows'][0]for p in inputs];assert {r['uid']:r['sourceSHA256']for r in rows}==SOURCES
  manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);pins={};refs=[Path(__file__),COUNT,*inputs]
  def pin(p):pins[str(p.relative_to(ROOT))]=digest(p.read_bytes());refs.append(p)
  pin(manifest);forms={}
  for t in m['tiles']:
   p=ROOT/'3d-viewer'/t['url']
   for b in read(p)['buildings']:
    if b['uid']in SOURCES:assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=t['url'],tileSHA256=digest(p.read_bytes()));pin(p)
  assert set(forms)==set(SOURCES)
  for url in m['officialModelCatalogues']:
   p=ROOT/'3d-viewer'/url;assert not(set(SOURCES)&{x['uid']for x in read(p)['models']});pin(p)
  for r in rows:
   assert r['source']['building']['buildingCSUID']==forms[r['uid']]['building']['buildingCSUID'];r['source']=forms[r['uid']];entry=r['candidate']['entry'];entry.update(sourceTile=r['native']['sheet'],rootTranslation=[-834500,0,816500]);p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==SOURCES[r['uid']];pin(p);dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());r['candidate']['path']=str(dest.relative_to(ROOT));refs.append(dest)
  DOC.mkdir();save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=digest(manifest.read_bytes())));save(LOCAL/'catalogue.json',dict(models=[r['candidate']['entry']for r in rows]));save(DOC/'terrain-candidates.json',[])
  subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True,timeout=600)
  g=read(LOCAL/'runtime-geometry.json.gz');assert {r['uid']for r in g['rows']}==set(SOURCES)
  for p,h in g['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;pin(ROOT/p)
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  metrics=read(DOC/'metrics.json')['rows'];assert all(not r.get('error')for r in metrics);save(DOC/'summary.json',dict(rows=[{k:r.get(k)for k in ['uid','minSurfaceGap','minLowGap','maxLowGap','missingTerrain','identity']}for r in metrics],noTerrainProposal=True,fullAcceptance=False))
  assert reservations.owns(lease);out=module('wave_pair_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'wave-original-tower-podium-current-no-terrain-capture-v1',refs+[LOCAL/'runtime-geometry.json.gz',HERE/'acceptance-metrics-multi-retained.mjs'],dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,noTerrainProposal=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

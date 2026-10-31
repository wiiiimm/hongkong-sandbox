"""Capture complete actual affected original/basic sources and before/after drawn terrain."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tai-kwei-runtime-capture-v1-20261017';DOC=BASE/BATCH
PHYS=BASE/'government-xl-tai-kwei-candidate-physical-v2-20261017';SCOPE=BASE/'government-xl-tai-kwei-current-native-scope-v1-20261017';TERR=BASE/'government-xl-tai-kwei-private-terrain-v1-20261017'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYS,SCOPE,TERR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 scope=read(SCOPE/'scope.json');candidate=read(TERR/'terrain-candidates.json')[0];construction=read(TERR/'construction.json');assert candidate['bounds']==scope['changedParentExtent'];manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);row=read(PHYS/'selection.json.gz')['rows'][0];assert digest(manifest.read_bytes())==read(PHYS/'selection.json.gz')['manifestSHA256']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
  models={};roots={};assets={}
  for url in m['officialModelCatalogues']:
   p=ROOT/'3d-viewer'/url;cat=read(p)
   for e in cat['models']:models[e['uid']]=e;roots[e['uid']]=cat['rootTranslation'];assets[e['uid']]=p.parent/e['asset']
  nominated=scope['touchingNativeUids'];assert nominated==['landsd/147024:0','landsd/148321:0','landsd/160193:0'];forms={}
  for t in m['tiles']:
   p=ROOT/'3d-viewer'/t['url']
   for b in read(p)['buildings']:
    if b['uid']in nominated:forms[b['uid']]=b;refs.append(p)
  rows=[dict(uid=row['uid'],entry={**row['candidate']['entry'],'rootTranslation':[-834500,0,816500]},building=row['source']['building'],path=row['candidate']['path'])]+[dict(uid=u,entry={**models[u],'rootTranslation':roots[u]},building=forms[u],path=str(assets[u].relative_to(ROOT)))for u in nominated]
  extra=[]
  for b in read(SCOPE/'complete-bounds.json.gz')['rows']:
   if b['uid']in nominated:
    for lo,hi in b['completeFourWorldBounds']:extra.append([lo[0],lo[2],hi[0],hi[2]])
  save(DOC/'input.json.gz',dict(currentManifestSHA256=digest(manifest.read_bytes()),domain=candidate['bounds'],cells=construction['coarseCells'],candidate=candidate,extraBounds=extra))
  save(DOC/'attributes-input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in m['officialModelCatalogues']],evidenceRefs=[ref(PHYS/'selection.json.gz'),ref(SCOPE/'scope.json')],rows=rows))
  for tool,args in [('tai_kwei_runtime_ground_capture_v1_20261017.mjs',[str(DOC.relative_to(ROOT))]),('tai_kwei_runtime_attributes_v1_20261017.mjs',[str((DOC/'attributes-input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))])]:
   with(DOC/(tool+'.log')).open('w')as log:subprocess.run(['node','--max-old-space-size=8192',str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
   assert reservations.heartbeat(lease)['ok'];refs.append(HERE/tool)
  report=read(DOC/'capture-report.json.gz');attrs=read(DOC/'attributes.json.gz');assert report['strictExteriorUnchanged']and report['startEndAllInputsVerified']and attrs['startEndAllInputsVerified']
  for p,h in {**report['inputHashes'],**attrs['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  out=module('tai_kwei_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-complete-runtime-ground-basic-native-capture-v1',list(set(refs)),dict(uids=[r['uid']for r in rows],basicActors=report['basicActors'],strictExteriorUnchanged=True,fullAcceptance=False,nextStep='Verify complete finite terrain clearance in all captured worlds and before/after affected neighbour regressions; then staged desktop/mobile browser checks.'));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

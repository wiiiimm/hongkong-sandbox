"""Check the existing Ocean Pride tower against its now-native podium, unchanged."""
from pathlib import Path
import subprocess,uuid
from run import ROOT,HERE,read,save,digest,reservations,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-ocean-pride-current-support-v1-20261015';DOC=BASE/BATCH
CENSUS=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015';UIDS=['landsd/162512:0','landsd/175935:0']
def main():
 assert not DOC.exists();packet=read(CENSUS/'input.json.gz');paths=[Path(__file__),CENSUS/'input.json.gz',CENSUS/'result.json'];receipt=read(CENSUS/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in packet['currentNativeViewerTileHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==packet['currentManifest']['sha256'];paths.append(ROOT/'3d-viewer/city/data/manifest.json')
 entries={}
 for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;c=read(p)
  for e in c['models']:
   if e['uid']in UIDS:
    assert e['uid']not in entries;entries[e['uid']]={**e,'rootTranslation':c['rootTranslation']};paths.append(p)
 sources=[]
 for uid in UIDS:
  r=next(r for r in packet['rows']if r['uid']==uid);assert r['rawCurrentEntry']==entries[uid]
  src=r['source'];assert digest((ROOT/src['path']).read_bytes())==src['sha256']==entries[uid]['sha256'];paths.append(ROOT/src['path'])
  sources.append(dict(uid=uid,sourceSHA256=src['sha256'],source={'building':r['currentBuilding']},candidate={'path':src['path'],'entry':entries[uid]}))
 claim=reservations.claim('ocean-pride-current-support-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'support-inputs.json',dict(pairs=[dict(uid=UIDS[0],supportUid=UIDS[1])],sources=sources))
  tool=HERE/'original-support-closure-interfaces.mjs';paths.append(tool)
  with(DOC/'worker.log').open('w')as log:result=subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
  assert result.returncode==0
  checked=read(DOC/'support-checks.json.gz');assert len(checked['rows'])==1
  for p,h in checked['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;paths.append(ROOT/p)
  row=checked['rows'][0];f=row['interface'];summary={k:f[k]for k in ['passed','samples','strictContacts','wallIntersections']};summary['unresolved']=len(f['unresolved']);save(DOC/'summary.json',summary)
  module('ocean_pride_pair_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-ocean-pride-pair-interface-v1',paths,dict(uids=UIDS,summary=summary,installationApproved=False,fullAcceptance=False,nextStep='Compare current strict interface to the retained basic-podium review; preserve existing publication flag and all raw failures.'))
  print(summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()

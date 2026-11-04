"""Full current neighbour regressions for the original assembly terrain candidate."""
import json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-orchards-assembly-terrain-candidate-v1-20261017';BATCH='government-xl-orchards-assembly-neighbours-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);receipt=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);manifestsha=digest(manifestpath.read_bytes());scope=read(PRIOR/'scope.json');patches=read(PRIOR/'terrain-candidates.json');final=module('orchards_neighbour_forms',HERE/'xl-final-script-pass.py');forms=final.load_forms(scope['parentExtent']);byuid={b['uid']:(b,t)for b,_,t in forms};assert set(scope['touchingNativeUids'])<=set(byuid)
 live={e['uid']for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']};selection=read(PRIOR/'selection.json.gz');rows=[r for r in selection['rows']if r['uid']!='landsd/254621:0'];assert len(rows)==3 and not ({r['uid']for r in rows}&live)
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=b,patchIndexes=[0],existingNative=b['uid']in live or bool(b.get('modelGeometry')))for b,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes())for b,_,t in forms},candidateIds=[r['uid']for r in rows],patches=patches))
 for name in ['check-neighbours.mjs','check-native-neighbours.mjs']:
  subprocess.run(['node',str(HERE/name),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True);assert reservations.owns(lease);refs.append(HERE/name)
 standard=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json');assert set(scope['touchingNativeUids'])<=set(native['blocked']);assert set(scope['touchingNativeUids'])<={r['uid']for r in native['rows']}
 for report in [standard,native]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 summary=dict(forms=len(forms),basicFlags=[dict(uid=r['uid'],reasons=r['reasons'])for r in standard['rows']if r['reasons']and not r['existingNative']],nativeRows=native['rows'],nativeResolved=native['resolved'],fullAcceptance=False)
 save(DOC/'summary.json',summary);assert digest(manifestpath.read_bytes())==manifestsha and reservations.owns(lease)
 out=module('orchards_neighbour_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-expanded-domain-basic-native-before-after-v1',list(set(refs)),dict(uids=[r['uid']for r in rows]+scope['touchingNativeUids'],summary=summary,fullAcceptance=False));print(dict(jobId=out['jobId'],forms=len(forms),basicFlags=summary['basicFlags'],nativeResolved=native['resolved']),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope=read(PRIOR/'scope.json');resources=[('building:'if u.startswith('landsd/')else'source-form:')+u for u in sorted(set(scope['basicAndNativeForms']+scope['touchingNativeUids']))]+['terrain-surface:city/data/government-native-254621-0.json']
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

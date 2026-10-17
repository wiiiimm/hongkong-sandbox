"""Read-only actual current geometry probe for three original HKDI actors.

The already-installed original22089 is included ONLY for source/support math.
This diagnostic does not propose terrain, approve identity, or re-publish it.
All old6/50 sampled source support failures remain untouched.
"""
import importlib.util,json,os,shutil,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-hkdi-original-support-20261006'
BATCH='government-xl-terrain-recovery-hkdi-complete-original-current-probe-v1-20261010';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/22089:0','landsd/88343:0','landsd/89613:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);manifest=ROOT/'3d-viewer/city/data/manifest.json';before=ref(manifest);current=read(manifest);old=read(OLD/'selection.json.gz');forms={}
 for tile in current['tiles']:
  p=ROOT/'3d-viewer'/tile['url']
  for b in read(p)['buildings']:
   if b['uid'] in UIDS:assert b['uid'] not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(p.read_bytes()))
 assert set(forms)==set(UIDS);rows=[];refs=[ref(Path(__file__)),ref(OLD/'selection.json.gz'),ref(OLD/'result.json'),ref(OLD/'support-checks.json.gz'),before];matches=[]
 for url in current['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid'] in UIDS:matches.append((p,e))
 assert len(matches)==1 and matches[0][1]['uid']==UIDS[0];cat,e=matches[0];nativeasset=cat.parent/e['asset'];refs.extend([ref(cat),ref(nativeasset)]);assert digest(nativeasset.read_bytes())==e['sha256']
 for r in old['rows']:
  assert r['uid'] in forms;raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256']==r['candidate']['entry']['sha256'];assert r['source']['building']['objectId']==forms[r['uid']]['building']['objectId'] and r['source']['building']['buildingCSUID']==forms[r['uid']]['building']['buildingCSUID']
  if r['uid']==UIDS[0]:assert r['sourceSHA256']==e['sha256'] and r['modelId']==e['modelId']
  asset=LOCAL/r['candidate']['entry']['asset'];asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw);rows.append(dict(r,source=forms[r['uid']],candidate=dict(r['candidate'],path=str(asset.relative_to(ROOT)))));refs.extend([ref(asset),ref(ROOT/'3d-viewer'/forms[r['uid']]['tile'])])
 rows.sort(key=lambda r:UIDS.index(r['uid']));save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=before['sha256'],diagnosticOnly=True,alreadyInstalledActorIncludedOnlyForOriginalSupportGeometry=UIDS[0],sourceGeometryChanges=0,publication=False,newlyInstalled=0));save(LOCAL/'catalogue.json',dict(models=[r['candidate']['entry'] for r in rows]));save(DOC/'terrain-candidates.json',[])
 subprocess.run(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 assert ref(manifest)==before and reservations.owns(lease);metrics=read(DOC/'metrics.json');assert [r['uid'] for r in metrics['rows']]==UIDS and not any(r.get('error') for r in metrics['rows']);geometry=read(LOCAL/'runtime-geometry.json.gz');assert [r['uid'] for r in geometry['rows']]==UIDS
 for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ref(ROOT/path))
 s=importlib.util.spec_from_file_location('hkdi_probe_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(s);s.loader.exec_module(f);refs.extend([ref(DOC/'selection.json.gz'),ref(DOC/'metrics.json'),ref(LOCAL/'runtime-geometry.json.gz')]);f.freeze(BATCH,'read-only-current-three-original-runtime-source-geometry-v1',[ROOT/x['path'] for x in {r['path']:r for r in refs}.values()],dict(uids=UIDS,sourceGeometryChanges=0,alreadyInstalledOriginalSupportActor=UIDS[0],noTerrainProposal=True,diagnosticOnly=True,currentIdentityAcceptance=False,fullAcceptance=False,publication=False,newlyInstalled=0,metrics=[dict(uid=r['uid'],minSurfaceGap=r['minSurfaceGap'],minLowGap=r['minLowGap'],maxLowGap=r['maxLowGap'],maxSamplerDelta=r['maxSamplerDelta'],missingTerrain=r['missingTerrain']) for r in metrics['rows']]));print(dict(probeFenced=True,publication=False),flush=True)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists();claim=reservations.claim('hkdi-source-only-probe-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=1800);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','1800','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

"""UNEXECUTED read-only draft: both exact installed market/terrain targets.

No proposal construction or native reapproval. Full original POSITION, actual
literal and two explicit F32 worlds plus currently drawn ground are captured.
Raw entries, suppressions and failed Sparkle v1 evidence remain unchanged.
"""
from pathlib import Path
import importlib.util,json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-sparkle-retained-market-two-current-render-ground-capture-v2'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-sparkle-tower-podium-pair-authentic-current-v1-20261011'
ERRATUM=BASE/'government-xl-sparkle-pair-authentic-current-v1-attempted-terrain-erratum-20261011/erratum.json'
UIDS=['landsd/113733:0','landsd/138091:0'];COUNTS=[15641,25224]
SOURCES=['e2d625839e898da7633663718adfc098ce07c4c44c57d31ec3fa95c1a1549bc2','4d738150459dcbf4092a02867219cc14cf83f3e9645cbbc33a255d88b65d9a78']
CSUIDS=['3381721476T20050430','3385221611T20050430']
SUPPRESSIONS=[['landsd/28244:0','landsd/107780:0','landsd/271008:0','landsd/271555:0'],['landsd/20045:0']]
MANIFEST='947f0a3b3a1d7167a9f98074af35d4030ff0245e121ee682eed4f9ab9baedfa6'
PATCH=ROOT/'3d-viewer/city/data/government-native-138091-0.json'
PATCH_SHA='adba04439687b055cd499f334d57b6c2edf92e769180f87a4f09ec83a97421d0'
CAPTURE=HERE/(BATCH+'.mjs')
FAILURE=BASE/'government-xl-sparkle-retained-market-capture-v1-scope-callback-failure-20261011'
FORM_UIDS=UIDS+[u for group in SUPPRESSIONS for u in group]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(r):
 p=ROOT/r['path'];assert p.is_file() and ref(p)==r;return p
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists()
 receipt=read(PHYSICAL/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 assert receipt['jobId']=='c834befb9fc03942b42683e9aeaa8d233663609ca12e1cc0a22b9524d0fcceb7'
 for pin in receipt['evidenceRefs']:verify(pin)
 assert not(PHYSICAL/'terrain-candidates.json').exists()
 assert not(PHYSICAL/'metrics.json').exists()and not(PHYSICAL/'foundation.json').exists()
 assert digest(ERRATUM.read_bytes())=='0e0d8d1b24ae156ab512aa37d8c77ce4d1ae90ca1f100cdac3f20be9e52d0742'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 current=read(manifest);assert ref(PATCH)['sha256']==PATCH_SHA
 old=read(PATCH);assert old['meta']['targetUids']==UIDS and old['coarseCells']==[481,376,486,380]
 assert sum(p['url']=='city/data/government-native-138091-0.json'for p in current['terrainPatches'])==1
 parent=ROOT/'3d-viewer'/old['meta']['parentTerrain'];assert ref(parent)['sha256']==old['meta']['parentSha256']
 refs=[*[ref(p)for p in sorted(FAILURE.iterdir())if p.is_file()],ref(Path(__file__)),ref(CAPTURE),ref(PHYSICAL/'result.json'),ref(PHYSICAL/'guard-failure.json'),ref(ERRATUM),start,ref(PATCH),ref(parent)]
 for source in old['meta']['source']['nativeSources']:
  for pin in source['sourceFiles']:verify(pin);refs.append(pin)
 audit=Path(old['nativeMesh']['sourceOverlap']['evidencePath']);assert ref(audit)['sha256']==old['nativeMesh']['sourceOverlap']['evidenceSHA256'];refs.append(ref(audit))
 cats=[ref(ROOT/'3d-viewer'/url)for url in current['officialModelCatalogues']]
 tiles=[ref(ROOT/'3d-viewer'/tile['url'])for tile in current['tiles']]
 entries={};forms={};all_uids=[]
 for pin in cats:
  catalogue=read(verify(pin))
  for entry in catalogue['models']:
   all_uids.append(entry['uid'])
   if entry['uid']in UIDS:
    assert entry['uid']not in entries;entries[entry['uid']]=(entry,pin)
 assert len(all_uids)==len(set(all_uids))==6648 and set(entries)==set(UIDS)
 for pin in tiles:
  for building in read(verify(pin))['buildings']:
   if building['uid']in FORM_UIDS:
    assert building['uid']not in forms
    forms[building['uid']]=dict(building=building,tile=pin['path'].removeprefix('3d-viewer/'),tileSHA256=pin['sha256'])
 assert set(forms)==set(FORM_UIDS);rows=[]
 for uid,count,source,csuid,suppressed in zip(UIDS,COUNTS,SOURCES,CSUIDS,SUPPRESSIONS):
  entry,catpin=entries[uid];assert entry['sha256']==source and entry['triangles']==count
  assert entry['buildingCSUID']==forms[uid]['building']['buildingCSUID']==csuid
  assert entry['rootTranslation']==[-834500,0,816500] and entry['publicationApproved']is True
  assert entry['supportDependencies']==[] and entry['suppressesBuildingUids']==suppressed
  assert entry['proceduralWindows']is False
  asset=(ROOT/catpin['path']).parent/entry['asset'];assetpin=ref(asset);assert assetpin['sha256']==source
  proof=packed_world_bounds(asset.read_bytes());assert proof['sourceSHA256']==source and proof['completeOriginalTriangles']==count
  refs.append(assetpin);rows.append(dict(uid=uid,rawEntry=entry,sourceAsset=assetpin,catalogue=catpin,sourceForm=forms[uid],completeOriginalPOSITIONProof=proof))
 refs.extend(ref(HERE/n)for n in ['exact_packed_world_bounds_v3_20261010.py','actual_float32_model_matrix_bounds_20261011.mjs','literal_production_module_dependency_closure_20261010.mjs','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 DOC.mkdir(parents=True);(DOC/'historical-current-manifest.json').write_bytes(manifest.read_bytes());refs.append(ref(DOC/'historical-current-manifest.json'))
 save(DOC/'native-render-inputs.json.gz',dict(rows=rows,currentManifest=start,currentCatalogueRefs=cats,currentTileRefs=tiles,completeCurrentFootprintForms=forms,evidenceRefs=refs,retainedTerrain=ref(PATCH),noTerrainProposalCreated=True))
 subprocess.run(['node',str(CAPTURE),str((DOC/'native-render-inputs.json.gz').relative_to(ROOT)),str((DOC/'native-render-ground.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
 output=read(DOC/'native-render-ground.json.gz');assert[r['uid']for r in output['rows']]==UIDS
 for r,inp,count in zip(output['rows'],rows,COUNTS):
  assert r['rawCurrentNativeEntry']==inp['rawEntry']and r['sourceSHA256']==inp['sourceAsset']['sha256']
  assert len(r['completeOriginalIndex'])//3==count and r['completeOriginalPOSITIONProof']==inp['completeOriginalPOSITIONProof']
 assert reservations.owns(lease)and ref(manifest)==start
 for pin in refs+cats+tiles:verify(pin)
 for p,h in output['inputHashes'].items():verify(dict(path=p,sha256=h));refs.append(dict(path=p,sha256=h))
 refs.extend(cats+tiles+[ref(DOC/'native-render-inputs.json.gz'),ref(DOC/'native-render-ground.json.gz')])
 spec=importlib.util.spec_from_file_location('sparkle_retained_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'fresh-two-retained-market-current-original-literal-two-explicit-float32-drawn-ground-v2',[ROOT/r['path']for r in {r['path']:r for r in refs}.values()],dict(uids=UIDS,completeNativeOriginalFaces=sum(COUNTS),completePOSITIONIncludingUnused=True,currentManifest=start,retainedTerrain=ref(PATCH),allCurrentCatalogueAndTileHashesPinned=True,rawNativeEntriesAndSuppressionSemanticsUnchanged=True,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,terrainChanges=0,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists()
 keys=['building:'+u for u in FORM_UIDS+['landsd/242198:0','landsd/228000:0']]+['terrain-patch:'+u for u in UIDS]
 claim=reservations.claim('sparkle-retained-market-render-ground-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600);assert claim['ok']
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()

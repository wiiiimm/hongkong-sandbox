"""Read-only fresh King-additive regional equality, not physical acceptance.

All old 6642 catalogue entries/assets and whole actual regional module/form/
terrain byte inputs remain exact. Complete owned and retained original POSITION,
literal and both captured F32 position sets define the protected region. Only
King is added; its untouched original POSITION and four rendered worlds must
be strictly disjoint. No source numerical proofs are rerun or relabelled.
"""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements-king-additive-current-regional-proof-v2';DOC=BASE/BATCH
CURRENT='de8db939e48be0ed3661a9f3bf59454d92ff27f4a1024f34a401b17612e03e54';BASELINE='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011'
CAPTURE=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
NATIVE=BASE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1'
INV=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v10'
KING=BASE/'government-xl-king-cheung-95691-current-actual-ground-capture-v1-20261011'
KING_INSTALLED=BASE/'government-xl-king-cheung-95691-unchanged-installed-v1-20261011'
OLD=HERE/'local'/KING_INSTALLED.name/'manifest-before-installation.json'
UIDS=['landsd/204145:0','landsd/204143:0'];NATIVES=['landsd/273061:0','landsd/204144:0'];KING_UID='landsd/95691:0'
POSITION_KEYS=['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def fenced(folder,names=()):
 r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for n in names:assert ref(folder/n)in r['evidenceRefs']
 return r

def bounds(points):
 p=np.asarray(points,float).reshape(-1,3);assert len(p)and np.isfinite(p).all();return np.array([p.min(0),p.max(0)])
def disjoint(a,b):return any(a[1,k]<b[0,k]or b[1,k]<a[0,k]for k in [0,2])
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==CURRENT and ref(OLD)['sha256']==BASELINE
 old=read(OLD);current=read(manifest);assert current['officialModelCatalogues'][:-1]==old['officialModelCatalogues']
 added=current['officialModelCatalogues'][-1];assert added=='city/data/official-models/government-xl-king-cheung-95691-unchanged-private-stage-v1-20261011/catalogue.json'
 clone=json.loads(json.dumps(current));clone['officialModelCatalogues']=old['officialModelCatalogues'];assert clone==old
 refs=[ref(Path(__file__)),start,ref(OLD)]
 for folder,names in [(PHYSICAL,()),(CAPTURE,('actual-render-attributes.json.gz',)),(NATIVE,('native-render-ground.json.gz',)),(INV,('inventory.json.gz',)),(KING,('complete-four-stream-ground-inputs.json.gz',)),(KING_INSTALLED,())]:
  r=fenced(folder,names);refs.append(ref(folder/'result.json'));refs.extend(ref(folder/n)for n in names)
 # Literal full regional form/tile, loader modules, original terrain and native
 # asset fences from the original physical/capture jobs all remain unchanged.
 # Sole historical manifest is byte-checked against actual archived d152.
 preserved=[]
 for folder in [PHYSICAL,CAPTURE,NATIVE]:
  for pin in read(folder/'result.json')['evidenceRefs']:
   if pin['path']=='3d-viewer/city/data/manifest.json':assert pin['sha256']==BASELINE;continue
   assert ref(ROOT/pin['path'])==pin;preserved.append(pin);refs.append(pin)
 inv=read(INV/'inventory.json.gz');assert inv['currentManifest']['sha256']==BASELINE and inv['completeNativeActors']==6642 and inv['allOriginalPOSITIONVerticesIncluded']is True
 entries={};catrefs=[]
 for url in current['officialModelCatalogues']:
  cp=ROOT/'3d-viewer'/url;catrefs.append(ref(cp))
  for entry in read(cp)['models']:assert entry['uid']not in entries;entries[entry['uid']]=(cp,entry)
 baseline={r['uid']:r for r in inv['rows']};assert len(entries)==6643 and set(entries)==set(baseline)|{KING_UID}and not set(UIDS)&set(entries)
 for uid,item in baseline.items():
  cp,e=entries[uid];assert ref(cp)==item['catalogue']and e==item['rawCurrentEntry']and e['sha256']==item['sourceSHA256'];assert ref(ROOT/item['source']['path'])==item['source'];refs.extend([item['catalogue'],item['source']])
 rows=read(PHYSICAL/'selection.json.gz')['rows'];actual=read(CAPTURE/'actual-render-attributes.json.gz')['rows'];native=read(NATIVE/'native-render-ground.json.gz')['rows']
 assert [r['uid']for r in rows]==[r['uid']for r in actual]==UIDS and [r['uid']for r in native]==NATIVES
 allbounds=[];bound_rows=[]
 for row,a in zip(rows,actual):
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']==a['sourceSHA256'];p=packed_world_bounds(raw);b=[np.asarray(p['originalWholeSourceBounds']),*[bounds(a[k])for k in POSITION_KEYS]];allbounds.extend(b);bound_rows.append(dict(uid=row['uid'],completeOriginalPOSITIONProof=p,completeLiteralBothF32Bounds=[v.tolist()for v in b[1:]],source=ref(asset)));refs.append(ref(asset))
 owned_region=np.array([np.min(np.asarray(allbounds)[:,0,:],axis=0),np.max(np.asarray(allbounds)[:,1,:],axis=0)])
 for a in native:
  item=baseline[a['uid']];assert a['rawCurrentNativeEntry']==item['rawCurrentEntry']and a['sourceSHA256']==item['sourceSHA256'];p=item['completeOriginalPOSITIONProof'];assert p==a['completeOriginalPOSITIONProof'];b=[np.asarray(p['originalWholeSourceBounds']),*[bounds(a[k])for k in POSITION_KEYS]];allbounds.extend(b);bound_rows.append(dict(uid=a['uid'],completeOriginalPOSITIONProof=p,completeLiteralBothF32Bounds=[v.tolist()for v in b[1:]],source=item['source']))
 # Protect complete regional current form footprints as well, not only models.
 foreign=read(PHYSICAL/'neighbour-inputs.json.gz')['rows'];form_bounds=[]
 for row in foreign:
  points=[v for ring in row['building']['rings']for v in ring];p=np.asarray(points,float);assert p.ndim==2 and p.shape[1]==2 and np.isfinite(p).all();b=np.array([[p[:,0].min(),0,p[:,1].min()],[p[:,0].max(),0,p[:,1].max()]]);allbounds.append(b);form_bounds.append(dict(uid=row['building']['uid'],wholeCurrentFootprintBounds=b.tolist()))
 region=np.array([np.min(np.asarray(allbounds)[:,0,:],axis=0),np.max(np.asarray(allbounds)[:,1,:],axis=0)])
 cp,e=entries[KING_UID];asset=cp.parent/e['asset'];raw=asset.read_bytes();assert digest(raw)==e['sha256'];king=read(KING/'complete-four-stream-ground-inputs.json.gz');assert king['uid']==KING_UID and king['sourceSHA256']==e['sha256']and king['completeOriginalFaces']==18742
 kp=packed_world_bounds(raw);added_bounds=[np.asarray(kp['originalWholeSourceBounds'])]
 assert set(king['completeWorldStreams'])=={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
 for mode,s in king['completeWorldStreams'].items():
  w=np.asarray(s['completeWorldTriangles'],float);assert w.shape==(18742,3,3)and digest(w.astype('<f8').tobytes())==s['completeWorldTriangleSHA256'];added_bounds.append(bounds(w))
 assert np.array_equal(decode_original_world_triangles(raw),np.asarray(king['completeWorldStreams']['providerOriginal']['completeWorldTriangles']))
 assert all(disjoint(region,b)for b in added_bounds),'King is not strictly outside the full protected original/literal/F32 region'
 complete_protected_touches=sorted(uid for uid,r in baseline.items()if not disjoint(region,np.asarray(r['completeOriginalPOSITIONProof']['originalWholeSourceBounds'])))
 touched=sorted(uid for uid,r in baseline.items()if not disjoint(owned_region,np.asarray(r['completeOriginalPOSITIONProof']['originalWholeSourceBounds'])))
 # All prior protected-region actors are unchanged preservation only. The
 # physical touch guard applies to the owned complete source/literal/F32 box,
 # not reacceptance of the much larger retained legacy native environment.
 assert touched==sorted(NATIVES),touched
 preflight=read(PHYSICAL/'current-source-terrain-preflight.json');assert preflight['terrainProposalChanged']is False
 for pin in [preflight['rootTerrain'],*[r['asset']for r in preflight['completeCurrentTerrainRouting']]]:assert ref(ROOT/pin['path'])==pin;refs.append(pin)
 failure=DOC/'prior-v1-failure.log';failure.parent.mkdir(parents=True,exist_ok=True);failure.write_bytes(Path('/tmp/elements-king-additive-regional-v1-20261011.log').read_bytes());assert 'AssertionError:'in failure.read_text();refs.extend([ref(failure),ref(HERE/'xl-terrain-recovery-20261011-elements-king-additive-current-regional-proof-v1.py')])
 refs.extend(catrefs);refs.extend([ref(asset),ref(KING/'complete-four-stream-ground-inputs.json.gz'),ref(PHYSICAL/'neighbour-inputs.json.gz'),ref(PHYSICAL/'current-source-terrain-preflight.json'),ref(HERE/'exact_packed_world_bounds_v3_20261010.py')]);assert all(ref(ROOT/p['path'])==p for p in refs)and ref(manifest)==start
 output=dict(uids=UIDS,currentManifest=start,baselineManifest=ref(OLD),exactHistoricalManifestAliases=[dict(original=dict(path='3d-viewer/city/data/manifest.json',sha256=BASELINE),archive=ref(OLD))],soleAddedUID=KING_UID,soleAddedCatalogue=added,completeCurrentNativeActors=6643,completeProtectedOriginalLiteralBothF32Bounds=region.tolist(),completeOwnedOriginalLiteralBothF32PhysicalTouchBounds=owned_region.tolist(),completeProtectedPriorSourceTouchUIDsPreservedUnchanged=complete_protected_touches,completeProtectedModelBounds=bound_rows,completeProtectedCurrentFormBounds=form_bounds,addedCompleteOriginalPOSITIONProof=kp,addedCompleteOriginalLiteralBothF32Bounds=[b.tolist()for b in added_bounds],all6642PriorRawEntriesAndAssetsUnchanged=True,allPriorCatalogueBytesUnchanged=True,allPreviousTerrainBytesUnchanged=True,allCurrentRegionalFormsUnchanged=True,allProductionModuleBytesUnchanged=True,completeOwnedAndRetainedOriginalLiteralBothF32RegionCovered=True,addedCompleteOriginalPOSITIONLiteralBothF32BoundsStrictlyDisjoint=True,currentWholeSourceTouchUIDs=touched,unchangedCompleteRegionalForeignUIDs=sorted(r['building']['uid']for r in foreign),completeRetainedNativeEntries=preflight['completeRetainedNativeEntries'],explicitPreservedCurrentInputRefs=list({p['path']:p for p in preserved}.values()),noNewNumericReacceptance=True,nativeReacceptance=False,publication=False,installationApproved=False,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',output);spec=importlib.util.spec_from_file_location('freeze_elements_regional',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'fresh-king-additive-complete-source-literal-F32-regional-equality-v2',[ROOT/p['path']for p in {r['path']:r for r in refs}.values()]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,currentManifest=start,completeCurrentNativeActors=6643,sourceGeometryChanges=0,terrainChanges=0,sourceOnlyRegionalProof=True,installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()

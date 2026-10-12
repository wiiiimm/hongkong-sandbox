"""Draft only: unchanged complete source/native interfaces, no terrain or acceptance."""
import argparse,json,subprocess,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
from polyu_sports305582_saved_contact_classification_helper_v1_20261012 import classify
B=ROOT/'docs/astra-city/government-import';P=B/'government-xl-citywalk134332-surviving-native-interface-proposal-v1-20261013';D=B/'government-xl-citywalk134332-surviving-native-interface-context-v1-20261013'
UID='landsd/134332:0';ACTORS=['landsd/175935:0','landsd/273839:0','landsd/305615:0'];SOURCE='b2d26e9f7a3b033877cd8c2aa6e6c363fec2cdcc2c09af8b06a1e3f583ad17df';JS=HERE/'citywalk134332_actual_surviving_native_attributes_draft_v1_20261013.mjs'
SEL=B/'government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue/selection.json.gz';COMP=B/'government-xl-remaining-20260923/sol-continuation-20261003/components/134332-0.json.gz';CAT=HERE/'accepted/government-xl-citywalk-source-20261004/catalogue.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def current_actor_partition(entries):
 assert len(entries)==len({e['uid']for e in entries})
 lookup={e['uid']:e for e in entries};assert UID not in lookup
 assert all(u in lookup for u in ACTORS)
 suppressed={u:[e['uid']for e in entries if u in e.get('suppressesBuildingUids',[])]for u in [UID,*ACTORS]}
 assert all(not suppressed[u]for u in [UID,*ACTORS]),'Named actor suppressed by current installed geometry; changed scope requires review'
 return lookup,suppressed

def main():
 p=argparse.ArgumentParser();p.add_argument('--expected-manifest',required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args();pins=read(P/'executable-pins.json')['refs']
 def fence():
  for e in pins:assert ref(ROOT/e['path'])==e
 fence();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==a.expected_manifest;m=read(manifest);catalogues=[ref(ROOT/'3d-viewer'/url)for url in m['officialModelCatalogues']];entries=[];catalogue_by_uid={}
 for c in catalogues:
  for e in read(ROOT/c['path'])['models']:entries.append(e);catalogue_by_uid[e['uid']]=c
 assert len(entries)==6650;lookup,suppressed=current_actor_partition(entries);row=read(SEL)['rows'][0];selection_entry=row['candidate']['entry'];catalogue=read(CAT);assert len(catalogue['models'])==1;entry=catalogue['models'][0];metadata_differences={k for k in set(entry)|set(selection_entry)if entry.get(k)!=selection_entry.get(k)};assert metadata_differences=={'identityReviewApproved','placementReviewed','placementReview','publicationApproved','sourceIdentityReviewed','priority','suppressesBuildingUids','proceduralWindows'};assert all(entry.get(k)==selection_entry.get(k)for k in set(entry)|set(selection_entry)if k not in metadata_differences);assert entry['uid']==UID and entry['sha256']==SOURCE and entry['triangles']==41277 and entry['modelId']=='B297602566802063C0'and entry['buildingCSUID']=='2976025668P20070723';assert read(CAT)['models']==[entry];source=Path(row['candidate']['path']);source=source if source.is_absolute()else ROOT/source;assert source.is_relative_to(ROOT)and ref(source)['sha256']==SOURCE
 components=read(COMP)['components'];labels={int(f):i for i,c in enumerate(components)for f in c['sourceFaceIndices']};assert len(components)==193 and sorted(labels)==list(range(41277));assert sum(len(c['sourceFaceIndices'])for c in components)==41277
 forms={};tilepins=[]
 for tile in m['tiles']:
  tp=ROOT/'3d-viewer'/tile['url'];hits=[f for f in read(tp)['buildings']if f['uid']in [UID,*ACTORS]]
  if hits:tilepins.append(ref(tp))
  for f in hits:
   assert f['uid']not in forms or forms[f['uid']]==f;forms[f['uid']]=f
 assert set(forms)=={UID,*ACTORS};assert forms[UID]['buildingCSUID']==entry['buildingCSUID']
 rows=[];assets=[ref(source)]
 for u in ACTORS:
  e=lookup[u];asset=(ROOT/catalogue_by_uid[u]['path']).parent/e['asset'];assert ref(asset)['sha256']==e['sha256'];assert forms[u]['buildingCSUID']==e['buildingCSUID'];assets.append(ref(asset));rows.append(dict(uid=u,entry=e,building=forms[u],path=ref(asset)['path'],role='actual-surviving-native-context'))
 refs=pins+catalogues+tilepins+assets+[ref(manifest),ref(SEL),ref(COMP),ref(CAT)]
 inp=dict(rows=[dict(uid=UID,entry=entry,building=forms[UID],path=ref(source)['path'],role='uninstalled-original-source-context')],nativeContextRows=rows,basicContextRows=[],completeCurrentForms=list(forms.values()),expectedNativeCount=6650,currentManifest=ref(manifest),currentCatalogueRefs=catalogues,sourceCatalogue=ref(CAT),historicalSelectionEntry=selection_entry,historicalCatalogueEntryReviewFlagsAreNotCurrentApproval=True,historicalMetadataDifferences=sorted(metadata_differences),evidenceRefs=refs)
 if a.preflight_only:print(json.dumps(dict(preflightPassed=True,noWorker=True,sourceFaces=41277,sourceBodies=193,nativeActors=ACTORS,suppressed=suppressed)));return
 assert not D.exists();D.mkdir();save(D/'current-interface-input.json.gz',inp);subprocess.run(['node',str(JS),ref(D/'current-interface-input.json.gz')['path'],str((D/'actual-attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);actual=read(D/'actual-attributes.json.gz')
 def worlds(r,path):
  idx=np.asarray(r['completeOriginalIndex'],int).reshape(-1,3);return {'providerOriginal':decode_original_world_triangles(path.read_bytes()),'actualLiteral':np.asarray(r['completeLiteralWorldPosition']).reshape(-1,3)[idx],'explicitLeftF32':np.asarray(r['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3)[idx],'explicitBalancedF32':np.asarray(r['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)[idx]}
 own=worlds(actual['rows'][0],source);assert digest(own['providerOriginal'].astype('<f8').tobytes())=='e4f766dcd25463e7bbef605068852b893059df268eff9cc3b5f73d2b1b3cdb21';assert all(t.shape==(41277,3,3)and np.isfinite(t).all()for t in own.values());bindings=[];proofs={}
 for n in actual['nativeContextRows']:
  path=ROOT/next(r['path']for r in rows if r['uid']==n['uid']);nw=worlds(n,path)
  for am,t in own.items():
   for bm,w in nw.items():
    key=digest(t.astype('<f8').tobytes()+w.astype('<f8').tobytes());bindings.append(dict(actor=n['uid'],sourceWorld=am,actorWorld=bm,sourceFaces=len(t),actorFaces=len(w),sourceWorldSHA256=digest(t.astype('<f8').tobytes()),actorWorldSHA256=digest(w.astype('<f8').tobytes()),proofKey=key))
    if key in proofs:continue
    records=[];tested=0
    for start in range(0,len(t),512):
     chunk=D/'chunks'/f"{key}-{start:05d}.json.gz";ids=list(range(start,min(start+512,len(t))));raw=exact_finite_contacts(t,ids,w,list(range(len(w))),maximum_pairs=1000000-tested);tested+=raw['trianglePairsTested'];assert tested<=1000000
     for c in raw['contacts']:
      aa,bb=rational_face(t[c['sourceFaceA']]),rational_face(w[c['sourceFaceB']]);na=cross(sub(aa[1],aa[0]),sub(aa[2],aa[0]));nb=cross(sub(bb[1],bb[0]),sub(bb[2],bb[0]));cop=bool(any(na)and any(nb)and not any(cross(na,nb))and dot(na,sub(bb[0],aa[0]))==0);cc=dict(**c,nonzeroExactCoplanarPlanes=cop);records.append(dict(**cc,originalBodyProvenance=labels[c['sourceFaceA']],classification=classify(cc,t[c['sourceFaceA']],w[c['sourceFaceB']])))
     save(chunk,dict(sourceFaceIDs=ids,exactRawContactProof=raw,wholeSourceWorldSHA256=bindings[-1]['sourceWorldSHA256'],wholeActorWorldSHA256=bindings[-1]['actorWorldSHA256']));fence()
     for e in refs:assert ref(ROOT/e['path'])==e
     for path,h in actual['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
     print(json.dumps(dict(actor=n['uid'],sourceWorld=am,actorWorld=bm,completedSourceFaces=min(start+512,len(t)),testedPairs=tested)),flush=True)
    proofs[key]=dict(completeWholeSourceFaceIDs=list(range(len(t))),completeActorFaceIDs=list(range(len(w))),exactPairsTested=tested,contacts=records,allCompleteFiniteFacesAccounted=True,ordinaryClearanceNotRecomputed=True)
 fence()
 for e in refs:assert ref(ROOT/e['path'])==e
 for path,h in actual['inputHashes'].items():assert ref(ROOT/path)['sha256']==h
 save(D/'diagnostic.json.gz',dict(sourceOnly=True,currentAcceptance=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,currentManifest=ref(manifest),currentNativeCount=6650,uid=UID,sourceSHA256=SOURCE,completeSourceFaces=41277,completeOriginalBodies=193,originalBodyLabelsAreProviderOriginalProvenance=True,suppressionInventory=suppressed,bindings=bindings,proofs=proofs,ordinaryThresholdM=-.5,ordinaryProofHistoricalOnly=True,properSurfaceCrossingNotSolidOrIntendedJoint=True,allBodyRootSupportRolesStillIndependent=True,evidenceRefs=refs+[ref(D/'current-interface-input.json.gz'),ref(D/'actual-attributes.json.gz')]))
if __name__=='__main__':main()

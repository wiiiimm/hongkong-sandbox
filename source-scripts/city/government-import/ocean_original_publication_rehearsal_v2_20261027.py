"""Dry-run exact original catalogue/terrain routes; no visual approval or --apply."""
from pathlib import Path
import copy,shutil,sys
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_coordinated_retained_contract_v1_20261027 import verify_metadata,verify_retained_entries,verify_terrain,verify_native_interfaces
BATCH='government-xl-ocean-original-publication-rehearsal-v2-20261027';PHYSICAL='government-xl-ocean-four-original-physical-review-v2-20261027';PATCH='government-xl-after-waterfront-ocean-four-nested-pair-surface-v1-20261027';P='government-xl-after-waterfront-ocean-four-corrected-'
def main():
 base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;stage=HERE/'local'/BATCH;assert not doc.exists()and not stage.exists();pins={};refs=[Path(__file__),HERE/'original_coordinated_retained_contract_v1_20261027.py']
 def take(name,file='summary.json'):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 physical=take(PHYSICAL,'ROOT-PHYSICAL-REVIEW.json');sources=physical['sourceSHA256ByUid'];assert physical['sourceSpecificPhysicalInterpretationAccepted']and not physical['visualAcceptance']and not physical['installationApproved']
 selection=take(P+'runtime-v1-20261027','selection.json.gz');original={r['uid']:r['candidate']['entry']for r in selection['rows']}
 private=HERE/'local/government-xl-ocean-coordinated-full-browser-v2-20261027';cat=read(private/'catalogue.json');refs.append(private/'catalogue.json')
 assert verify_metadata(cat['models'],sources,physical['supportByUid'],original,physical['groundOwnerUids'])
 assert all(m.get('publicationApproved')is False and m.get('placementReviewed')is False for m in cat['models'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==physical['currentManifestSHA256'];refs.append(manifest);current={}
 for url in read(manifest)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;refs.append(path)
  for m in read(path)['models']:assert m['uid']not in current;current[m['uid']]=m
 assert verify_retained_entries(current,physical['retainedNativeEntries'],sources,6985)
 assert verify_native_interfaces(physical,take(P+'model-scope-v1-20261027'),take(P+'native-contacts-v1-20261027'),current,sources)
 patch=take(PATCH);replacement=patch['replacedNativeTerrain'][0];old=ROOT/'3d-viewer'/replacement['url'];terrain=ROOT/patch['candidate']['path'];assert digest(old.read_bytes())==replacement['sha256']and digest(terrain.read_bytes())==patch['candidate']['sha256'];refs.extend([old,terrain])
 retention=verify_terrain(read(old),read(terrain),physical['groundOwnerUids'],sources,patch,digest(old.read_bytes()),digest(terrain.read_bytes()))
 for model in cat['models']:
  asset=private/model['asset'];assert digest(asset.read_bytes())==model['sha256'];refs.append(asset);dest=stage/model['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(asset,dest)
 save(stage/'catalogue.json',cat)
 destination='city/data/official-models/'+BATCH+'/catalogue.json';plan=dict(areas=[dict(area='Private original-source publication rehearsal',catalogue=str((stage/'catalogue.json').relative_to(ROOT)),destination=destination)],topLevelTerrainPatches=[dict(source=str(terrain.relative_to(ROOT)),destination='city/data/'+BATCH+'-terrain.json',sha256=digest(terrain.read_bytes()),resolution=read(terrain)['cell'],area='Private original-source publication rehearsal',replaces=replacement)])
 save(stage/'plan.json',plan);doc.mkdir();save(doc/'preconditions.json',dict(sourceSHA256ByUid=sources,physicalReviewAccepted=True,visualApprovalPending=True,installationApproved=False,publication=False,retention=retention,warning='Rehearsal only. Unapproved catalogue flags preserved. This plan is not a qualified installation plan.'))
 from original_nested_coordinated_publisher_v1_20261027 import publisher
 pub,validated_retention=publisher('ocean_unapproved_nested_publication_dry_run',old,terrain,physical['groundOwnerUids'],sources,patch);assert validated_retention==retention;pub.DOC=doc/'publisher-dry-run';oldargv=sys.argv[:]
 try:sys.argv=['publish.py',str((stage/'plan.json').relative_to(ROOT))];pub.main()
 finally:sys.argv=oldargv
 report=read(pub.DOC/'publication-plan.json');assert report['published']is False and digest(manifest.read_bytes())==physical['currentManifestSHA256'];assert not(ROOT/'3d-viewer'/destination).exists()
 refs.extend([HERE.parent/'island-detail-integration/publish.py',HERE/'original_nested_coordinated_publisher_v1_20261027.py',HERE/'nested_terrain_patch_validation_v1_20261027.py',HERE/'nested_native_terrain_validation_v1_20261027.py',HERE/'nested_coordinated_native_boundary_v1_20261027.py',HERE/'nested_coordinated_parent_contract_v1_20261027.py',*[p for p in stage.rglob('*')if p.is_file()]])
 module('ocean_publication_rehearsal_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unapproved-original-coordinated-retained-publication-rehearsal-v1',refs,dict(uids=sorted(sources),dryRunPassed=True,retainedEntriesUnchanged=True,newOriginalActors=len(sources),visualAcceptance=False,installationApproved=False,publication=False))
if __name__=='__main__':main()

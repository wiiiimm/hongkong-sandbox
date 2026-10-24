"""Pin the unique actual installed related original; identity-only, no physics credit."""
from pathlib import Path
import importlib.util,json
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from man_fuk_named_original_envelope_identity_v3_20261010 import UID,RELATED,RELATED_SHA,RELATED_WORLD_SHA
DOC=ROOT/'docs/astra-city/government-import/government-xl-man-fuk-current-installed-related-original-binding-v2-20261010'
CAP=DOC.parent/'government-xl-man-fuk-current-bound-envelope-inputs-v3-20261010'
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';raw=manifest.read_bytes();m=json.loads(raw);assert digest(raw)==read(CAP/'current-inputs.json.gz')['manifestSHA256'];allentries=[];catalogues=[]
 for url in m['officialModelCatalogues']:
  cat=ROOT/'3d-viewer'/url;catalogues.append(cat)
  for entry in read(cat)['models']:
   if entry['uid']==RELATED:allentries.append((cat,entry))
 assert len(allentries)==1;cat,entry=allentries[0];asset=cat.parent/entry['asset'];assert asset.is_file() and digest(asset.read_bytes())==entry['sha256']==RELATED_SHA
 world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(2160,3,3) and digest(world.astype('<f8').tobytes())==RELATED_WORLD_SHA
 assert entry['modelId']=='B364721945401063C0' and entry['buildingCSUID']=='3647219454T20050430' and entry['triangles']==2160 and entry['rootTranslation']==[-834500,0,816500] and entry['proceduralWindows'] is False and entry['publicationApproved'] is True
 save(DOC/'binding.json',{'manifestSHA256':digest(raw),'catalogueURL':str(cat.relative_to(ROOT/'3d-viewer')),'catalogueSHA256':digest(cat.read_bytes()),'entry':entry,'actualInstalledAssetPath':str(asset.relative_to(ROOT)),'actualInstalledAssetSHA256':digest(asset.read_bytes()),'completeOriginalWorldSHA256':digest(world.astype('<f8').tobytes()),'allCatalogueURLs':m['officialModelCatalogues'],'allCatalogueSHA256s':{str(c.relative_to(ROOT)):digest(c.read_bytes()) for c in catalogues},'physicalAccepted':False,'installationCredit':0})
 assert manifest.read_bytes()==raw
 (DOC/'README.md').write_text('Unique actual installed Man Oi catalogue entry and literal government compressed bytes/root/world are pinned independently. All2160faces remain; source equals independently acquired original. Catalogue uniqueness is checked across the entire current inventory. This binds identity context only; collision, complete runtime mesh/support/current drawn ground remain independent physical checks.\n')
 spec=importlib.util.spec_from_file_location('man_fuk_installed_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
 f.freeze(DOC.name,'unique-current-installed-related-original-binding-v1',[Path(__file__),manifest,*catalogues,asset,CAP/'result.json',CAP/'current-inputs.json.gz',HERE/'man_fuk_named_original_envelope_identity_v3_20261010.py',HERE/'exact_packed_world_geometry_20261009.py'],{'uids':[UID,RELATED],'manifestSHA256':digest(raw),'identityAccepted':False,'physicalAccepted':False,'remainingReason':'current-bound-named-envelope-replay-and-independent-physical-checks'})
if __name__=='__main__':main()

"""Read-only historical manifest relocation and exact current identity-form binding."""
from pathlib import Path
import subprocess,hashlib,json
import heritage165054_joint_private_stage_v1_20261015 as stage
ROOT=stage.ROOT;BASE=stage.BASE;read=stage.read;ref=stage.ref;check=stage.check;save=stage.save
DOC=BASE/'government-xl-heritage165054-identity-current-reconciliation-v1-20261015'
OLD='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
def main():
 assert not DOC.exists()
 receipt=BASE/'government-xl-heritage165054-current-typed-identity-receipt-v3-20261014/result.json';r=read(receipt)
 stale=[q for q in r['evidenceRefs']if hashlib.sha256((ROOT/q['path']).read_bytes()).hexdigest()!=q['sha256']]
 assert stale==[dict(path='3d-viewer/city/data/manifest.json',sha256=OLD)]
 raw=subprocess.check_output(['git','show','71daf44c89cc37782fff65aa2c598c4bd1bd2497:3d-viewer/city/data/manifest.json'],cwd=ROOT);assert hashlib.sha256(raw).hexdigest()==OLD
 old=json.loads(raw);current=read(ROOT/'3d-viewer/city/data/manifest.json');assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==stage.original.CURRENT
 changed=sorted(k for k in old.keys()|current.keys()if old.get(k)!=current.get(k));assert changed==['officialModelCatalogues','terrainPatches']
 identity=read(stage.IDENTITY);forms=identity['allCurrentFormsRetained'];assert len(forms)==len({f['uid']for f in forms})
 found={};tile_refs=[]
 for tile in current['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];rows=read(path)['buildings'];matches=[b for b in rows if b['uid']in {f['uid']for f in forms}]
  if matches:
   tile_refs.append(ref(path))
   for b in matches:assert b['uid']not in found;found[b['uid']]=b
 assert len(found)==len(forms)and all(found[f['uid']]==f for f in forms)
 added=[x for x in current['officialModelCatalogues']if x not in old['officialModelCatalogues']];assert len(added)==2 and all(x in current['officialModelCatalogues']for x in old['officialModelCatalogues'])
 added_models=[]
 for url in added:
  cat=read(ROOT/'3d-viewer'/url);added_models.extend(dict(uid=m['uid'],sha256=m['sha256'])for m in cat['models'])
 assert {m['uid']for m in added_models}=={'landsd/338946:0','landsd/12728:0','landsd/193086:0'}
 DOC.mkdir();(DOC/'historical-manifest.json').write_bytes(raw)
 save(DOC/'reconciliation.json',dict(historicalReceipt=ref(receipt),historicalManifestReference=stale[0],exactHistoricalManifestBytes=ref(DOC/'historical-manifest.json'),currentManifest=ref(ROOT/'3d-viewer/city/data/manifest.json'),changedManifestKeys=changed,allOther401HistoricalEvidenceRefsStillExact=True,retainedCurrentForms=len(forms),allRetainedFormsDeepEqual=True,sourceIdentity=ref(stage.IDENTITY),currentTileRefs=tile_refs,addedOriginalModels=added_models,unchangedOtherHistoricalRefs=[q for q in r['evidenceRefs']if q not in stale],terrainAcceptanceTransferred=False,currentPhysicalEvidenceRequired=ref(stage.shelter.DOC/'ROOT-VERIFIED.json'),caller=ref(Path(__file__)),installationApproved=False))
 print(json.dumps(dict(reconciled=True,retainedForms=len(forms),addedOriginalModels=len(added_models))))
if __name__=='__main__':main()

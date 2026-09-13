"""Prove this channel pass preserves every existing city source/model tile."""
import hashlib,json,subprocess
from hydro_build import HERE,ROOT,DOC
OUT=ROOT/'3d-viewer/city/data';BASELINE='7757ee6'
def main():
 manifest=json.loads((OUT/'manifest.json').read_text());prior=json.loads(subprocess.check_output(['git','show',BASELINE+':3d-viewer/city/data/manifest.json'],cwd=ROOT));assert manifest['tiles']==prior['tiles'];assert manifest['counts']==prior['counts'];assert manifest.get('sources')==prior.get('sources')
 changed=subprocess.check_output(['git','diff','--name-only',BASELINE,'--','3d-viewer/city/data/tiles'],cwd=ROOT,text=True).splitlines();assert not changed,changed
 added=subprocess.check_output(['git','ls-files','--others','--exclude-standard','3d-viewer/city/data/tiles'],cwd=ROOT,text=True).splitlines();assert not added,added
 count=0;ids=[];models={};official=[]
 for t in manifest['tiles']:
  for b in json.loads((ROOT/'3d-viewer'/t['url']).read_text())['buildings']:
   count+=1;ids.append(b['uid'])
   if b['uid'].startswith('landsd/'):official.append(b['id'])
   if b.get('modelGeometry'):models[b['uid']]=hashlib.sha256(json.dumps(b['modelGeometry'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert count==346115 and len(models)==1859
 report={'baseline':BASELINE,'allTileFilesByteEquivalentToBaseline':True,'tileCatalogueUnchanged':True,'sourceCatalogueUnchanged':True,'forms':count,'officialForms':len(official),'uniqueOfficialSourceIds':len(set(official)),'detailedModels':len(models),'uniqueFormIds':len(set(ids)),'allFormIdsSha256':hashlib.sha256('\n'.join(sorted(ids)).encode()).hexdigest(),'detailedGeometryByUidSha256':hashlib.sha256(json.dumps(models,sort_keys=True).encode()).hexdigest(),'tileDataChanges':changed,'newTileFiles':added,'terrainSourcePreservation':'hydro-validation.json separately verifies unchanged coarse terrain fields and whole Tai O fine patch; only source-backed optional hydro geometry is added.','authorisedArrivalChange':'Only taiopromenade moves8.302m along retained publicpath to clear the newly mapped shore.'}
 (DOC/'hydro-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()

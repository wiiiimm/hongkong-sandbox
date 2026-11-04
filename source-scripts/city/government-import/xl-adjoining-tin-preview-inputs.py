"""Pin ten unchanged production meshes for newly verified adjoining terrain."""
from pathlib import Path
import subprocess,sys
from run import ROOT,read,save,digest
DIR=ROOT/'source-scripts/city/government-import';BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-adjoining-current-tin-preview-20261007'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 doc=BASE/(BATCH+'-inputs');assert not doc.exists()
 audit=BASE/'government-xl-adjoining-current-terrain-directory-audit-20261007/result.json';wanted=set(read(audit)['uids']);assert len(wanted)==10
 original=BASE/'government-xl-original-dtm-contact-preview-20261007/result.json';fresh=BASE/'government-xl-refreshed-current-tin-preview-20261007-inputs/result.json'
 source=read(original);pool={r['uid']:r for r in source['rows']};pool.update({r['uid']:r for r in read(fresh)['rows']})
 rows=[];selections=[];contexts=[];refs=[ref(audit),ref(original),ref(fresh),ref(Path(__file__))]
 for uid in sorted(wanted):
  r=pool[uid];geo=ROOT/r['geometry']['path'];assert ref(geo)==r['geometry'];data=read(geo)
  for path,sha in data['inputHashes'].items():
   if digest((ROOT/path).read_bytes())!=sha:assert path=='3d-viewer/city/data/manifest.json' or path.startswith(('3d-viewer/city/data/terrain','3d-viewer/city/data/government-native-'))
  row=next(v for v in read(BASE/r['priorBatch']/'selection.json.gz')['rows'] if v['uid']==uid)
  assert row['sourceSHA256']==r['sourceSHA256']==digest((ROOT/row['candidate']['path']).read_bytes())
  assert row['source']['tileSHA256']==digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())
  selections.append(row);contexts.append({'uid':uid,'sourceSHA256':row['sourceSHA256'],'neighbourTileHashes':{row['source']['tile']:row['source']['tileSHA256']}})
  rows.append({**r,'historicalPriorBatch':r['priorBatch'],'priorBatch':doc.name})
 frozen={'rows':selections,'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'diagnosticOnly':True,'publication':False}
 save(doc/'selection.json.gz',frozen);save(doc/'check-selection.json.gz',frozen);save(doc/'context.json.gz',{'rows':contexts})
 receipt={'source':source['source'],'rows':rows,'exactProductionGeometryInputsVerified':True,'historicalGeometryReused':True,'evidenceRefs':refs,'diagnosticOnly':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0};save(doc/'result.json',receipt)
 subprocess.run([sys.executable,str(DIR/'xl-adjoining-current-tin-preview.py'),'--batch',BATCH,'--receipt',str((doc/'result.json').relative_to(ROOT))],cwd=ROOT,check=True)
if __name__=='__main__':main()

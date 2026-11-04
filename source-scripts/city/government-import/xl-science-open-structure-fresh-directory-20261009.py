"""Fresh bounded primary source-directory query; not a territory absence claim."""
import sys,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,connect
sys.path.insert(0,str(HERE.parent/'citywide-source'))
from discover import scan
BATCH='government-xl-science-open-structure-fresh-directory-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
SHEETS=['11-NW-25C','11-NW-25A','11-NW-25B','11-NW-25D']
def main():
 assert not (DOC/'result.json').exists(),'Completed captured source-version evidence immutable'
 if '--scan' in sys.argv:
  assert not DOC.exists(),'Fresh source query scope required';DOC.mkdir(parents=True);rows=[]
  for sheet in SHEETS:
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');p=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()
   if not p:rows.append({'sheet':sheet,'notChecked':'no-pinned-directory-row'});continue
   old=p[0];new,_=scan({'SHEETNO':sheet,'Format_glTF':old['sourceURL'],'REVISIONDATE':old['revision']},LOCAL/sheet,refresh=True);matches=[m for m in new['models'] if m['modelId'].startswith('B3631518015')]
   rows.append({'sheet':sheet,'sourceURL':new['sourceURL'],'etag':new['etag'],'revision':new['revision'],'directorySHA256':new['directorySHA256'],'completeEntries':new['completeEntries'],'completeModelCount':len(new['models']),'matches':matches,'directory':str((LOCAL/sheet/'zip-directory.bin').relative_to(ROOT))})
  save(DOC/'fresh-four-sheet-source-search.json',{'uid':'landsd/83471:0','buildingCSUID':'3631518015T20071227','rows':rows,'searchCoverage':'Only exact footprint sheet11-NW-25C and3adjacent25quadrants. Fresh original directory bytes/HEADETag; absence notterritory-wideabsence.','nativeModelAcquired':False,'identityAccepted':False,'publication':False})
 result=read(DOC/'fresh-four-sheet-source-search.json');assert [r['sheet'] for r in result['rows']]==SHEETS
 paths=[Path(__file__),HERE.parent/'citywide-source/discover.py',HERE.parent/'landmark-acquisition/acquire.py',DOC.parent/'government-xl-science-museum-open-structure-primary-20261009/result.json',DOC.parent/'xl-terrain-recovery-20261009-science-open-structure-context/diagnostic.json.gz']
 for r in result['rows']:
  assert not r.get('notChecked');directory=read(LOCAL/r['sheet']/'result.json');assert directory['etag']==r['etag'] and directory['directorySHA256']==r['directorySHA256'];assert len(directory['models'])==r['completeModelCount'];assert not r['matches'];paths.extend(p for p in (LOCAL/r['sheet']).rglob('*') if p.is_file())
 spec=importlib.util.spec_from_file_location('science_directory_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'fresh-complete-four-local-government-source-directories-exact-open-sided-prefix-v1',paths,{'uids':['landsd/80343:0','landsd/83471:0'],'freshCompleteSourceSheets':4,'completeListedModels':sum(r['completeModelCount'] for r in result['rows']),'exactOpenSidedSourceMatches':0,'territoryAbsenceEstablished':False,'sourceCorruptionEstablished':False,'identityAccepted':False,'scriptFullAcceptancePassed':False,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'original-museum-overlap-with-active-current-open-sided-structure-needs-exact-primary-function-ownership-and-3D-interface','nextStep':'Independently register existing primary museum plan and measure all63original faces against full current renderer canopy geometry; retain raw1.855m2 excess and all actor geometry. Current4GLTF0 source sheets do not supply exact ancillary original; do not call it impossible or corrupt.'})
if __name__=='__main__':main()

"""Fresh primary/current/source provenance for reviewed named mall-station identity."""
import importlib.util,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from tung_sing_current_bound_identity_20261010 import stream_pin
from test_southside_named_original_station_envelope_identity_20261010 import EVIDENCE,D,REL
DOC=ROOT/'docs/astra-city/government-import/government-xl-southside-current-bound-source-inputs-20261010'
RAW=DOC.parent/'government-xl-southside-fresh-current-full-cell-preflight-v2-20261010'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();DOC.mkdir(parents=True);selection=read(RAW/'selection.json.gz');row=selection['rows'][0];capture=read(RAW/'all-current-forms.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']
 query=module('southside_fresh_primary_request','xl-southside-station-original-relationship-20261010.py');query.DOC=DOC;where="BuildingCSUID IN ('3533312006P20240709','3536012138T20160607')";primary=query.query(0,where,'exact-current-primary',True);relations=query.query(1002,where,'exact-current-structure-relations');structures=query.query(1003,'BuildingStructureID IN (6095667)','exact-current-structures')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');native=[{'sourceKey':k+'/'+m['modelId'],'model':m,'sheet':s,'resultSHA256':h} for k,m,s,h in c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE m->>'modelId' IN ('B353331200602063C0','B353601213801063C1')").fetchall()]
 native.sort(key=lambda n:n['model']['modelId']!='B353331200602063C0');assert native==D['native']
 source={**EVIDENCE,'rows':native,'primaryRecords':primary,'exactRelations':relations,'exactStructures':structures};save(DOC/'original-source-lookup.json.gz',source)
 related=next(ROOT/k for k,v in D['inputHashes'].items() if k.endswith('.glb.gz') and v==native[1]['model']['asset']['sha256']);save(DOC/'current-inputs.json.gz',{'manifestSHA256':selection['manifestSHA256'],'forms':capture['forms'],'tileHashes':capture['tileHashes'],'relatedOriginalPath':str(related.relative_to(ROOT))});save(DOC/'complete-original-stream-pins.json.gz',{'mall':stream_pin((ROOT/row['candidate']['path']).read_bytes(),row['modelId'],11699),'station':stream_pin(related.read_bytes(),'B353601213801063C1',1191)})
 for name in ['mtr-shopping-malls.html','southside-owner-transport.html','station-original-plan.pdf']:
  shutil.copyfile(REL/name,DOC/name);shutil.copyfile(REL/(name+'.request.json'),DOC/(name+'.request.json'))
 save(DOC/'selection.json.gz',selection);save(DOC/'context.json.gz',read(RAW/'context.json.gz'))
 assert digest(manifest.read_bytes())==selection['manifestSHA256'];(DOC/'README.md').write_text('Fresh complete current forms/tiles/manifest, authoritative primary stable identifiers and sole mall OP record, exact original source/native versions and complete source root/BIN/all-bufferViews/world streams. MTR and owner explicitly document direct mall-station connection; this establishes no shared OP/legal ownership/all-face L1/support claim. All157 source components and34 excess faces remain. The named kernel34 adverse actual-source tests pass; production current adapter and physical gates remain separate. No source building/model/terrain edits or installation approval.\n')
 paths=[Path(__file__),manifest,related,ROOT/row['candidate']['path'],HERE/'southside_named_original_station_envelope_identity_20261010.py',HERE/'test_southside_named_original_station_envelope_identity_20261010.py',HERE/'xl-southside-fresh-current-full-cell-preflight-v2-20261010.py',HERE/'xl-southside-current-full-cell-preflight-20261010.py',HERE/'xl-southside-station-original-relationship-20261010.py',HERE/'tung_sing_current_bound_identity_20261010.py']+[q for q in RAW.rglob('*') if q.is_file()]+[ROOT/'3d-viewer'/u for u in capture['tileHashes']]
 module('southside_current_source_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'fresh-complete-current-primary-native-mtr-station-inputs-v1',paths,{'uids':D['uids'],'identityAccepted':False,'physicalAccepted':False,'completeOriginalSourceFaces':[11699,1191],'completeOriginalMallComponents':157,'allRawOverlapFacesRetained':34,'sourceIdentityReviewUsedAI':True,'remainingReason':'current-bound-adapter-replay-then-independent-full-physical'})
if __name__=='__main__':main()

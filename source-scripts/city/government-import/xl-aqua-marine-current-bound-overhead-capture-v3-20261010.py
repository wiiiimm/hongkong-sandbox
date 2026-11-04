"""Freeze full current/provider/root/source inputs for the named overhead identity."""
import importlib.util,shutil,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from tung_sing_current_bound_identity_20261010 import stream_pin
from aqua_named_original_overhead_identity_20261010 import UID,FOREIGN,SOURCE_SHA,FOREIGN_SHA
BATCH='government-xl-aqua-marine-current-bound-overhead-inputs-v3-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
RAW=DOC.parent/'government-xl-aqua-marine-current-full-cell-preflight-v3-20261010';PRIMARY=DOC.parent/'government-xl-aqua-marine-fresh-overhead-source-context-v3-20261010';SELECT=DOC.parent/'government-xl-aqua-marine-original-recovery-20261010/selection.json.gz'
def native_rows(c):return [{'sourceKey':k+'/'+m['modelId'],'model':m,'sheet':s,'resultSHA256':h} for k,m,s,h in c.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key),LATERAL jsonb_array_elements(r.result->'models')m WHERE m->>'modelId' IN ('B333392151502063C0','B333622156101063C0') ORDER BY m->>'modelId'").fetchall()]
def main():
 assert not DOC.exists();selection=read(RAW/'selection.json.gz');row=selection['rows'][0];capture=read(RAW/'all-current-forms.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];assert read(PRIMARY/'diagnostic.json.gz')['inputHashes']['3d-viewer/city/data/manifest.json']==selection['manifestSHA256']
 DOC.mkdir(parents=True)
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');native=native_rows(c)
 assert len(native)==2
 sel=read(SELECT);paths={r['uid']:ROOT/r['candidate']['path'] for r in sel['rows']};assert digest(paths[UID].read_bytes())==SOURCE_SHA and digest(paths[FOREIGN].read_bytes())==FOREIGN_SHA
 save(DOC/'source-lookup.json.gz',{'rows':native,'originalPaths':{u:str(p.relative_to(ROOT)) for u,p in paths.items()}});save(DOC/'complete-original-stream-pins.json.gz',{'own':stream_pin(paths[UID].read_bytes(),'B333392151502063C0',22735),'foreign':stream_pin(paths[FOREIGN].read_bytes(),'B333622156101063C0',116)});save(DOC/'current-inputs.json.gz',{'manifestSHA256':selection['manifestSHA256'],'forms':capture['forms'],'tileHashes':capture['tileHashes']});save(DOC/'selection.json.gz',selection);save(DOC/'context.json.gz',read(RAW/'context.json.gz'))
 for p in PRIMARY.glob('exact-current-*'):
  if p.is_file():shutil.copyfile(p,DOC/p.name)
 for name in ['government-xl-aqua-marine-original-overhead-envelope-20261010','government-xl-aqua-marine-overhead-original-visual-contact-20261010']:
  save(DOC/(name+'.refs.json'),{'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in (DOC.parent/name).rglob('*') if p.is_file()}})
 (DOC/'README.md').write_text('Full current complete actor/tile/manifest and raw full-cell inputs, unique Active primary stableCSUID/BuildingID/type/GeoRef/date/height, unchanged exact native versions and complete source scene/root/BIN/allbufferViews/world streams for the named Aqua Marine overhead plate. The complete656face component and all22 overlap faces lie strictly above the separate116faceoriginal/current/primary body;337 nondegenerate source-internal positive contacts corroborate the original source envelope. Every authored degenerate triangle remains separately retained/uncredited. Siteplan is contextonly; no common ownership, physical support, surveyed-height, actor removal/collision/terrain exemption.21actualkerneltestsPASS. Current adapter replay, allphysical/browser/publicationgates remain separate.\n')
 paths_for_receipt=[Path(__file__),manifest,SELECT,*paths.values(),HERE/'aqua_named_original_overhead_identity_20261010.py',HERE/'test_aqua_named_original_overhead_identity_20261010.py',HERE/'xl-aqua-marine-current-full-cell-preflight-v3-20261010.py',HERE/'tung_sing_current_bound_identity_20261010.py']+[p for p in RAW.rglob('*') if p.is_file()]+[ROOT/'3d-viewer'/u for u in capture['tileHashes']]
 for n in ['government-xl-aqua-marine-original-overhead-envelope-20261010','government-xl-aqua-marine-overhead-original-visual-contact-20261010','government-xl-aqua-marine-fresh-overhead-source-context-v3-20261010','government-xl-aqua-marine-original-recovery-20261010']:paths_for_receipt.extend(p for p in (DOC.parent/n).rglob('*') if p.is_file())
 assert digest(manifest.read_bytes())==selection['manifestSHA256'];s=importlib.util.spec_from_file_location('aqua_overhead_input_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);receipt=m.freeze(BATCH,'complete-named-original-overhead-current-provider-source-inputs-v1',paths_for_receipt,{'uids':[UID,FOREIGN],'identityAccepted':False,'physicalAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalFaces':[22735,116],'completeOverheadFaces':656,'completeProjectedOverlapFaces':22,'remainingReason':'reviewed-named-kernel-current-bound-replay-then-independent-fullphysical','sourceIdentityReviewUsedAI':True});print({'jobId':receipt['jobId']},flush=True)
if __name__=='__main__':main()
